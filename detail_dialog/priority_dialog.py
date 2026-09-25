from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QColorDialog, QMessageBox, QInputDialog
)
from PySide6.QtGui import QColor

import database
import styles
from strings import t


def ensure_priority_category(db_path=None):
    """Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si no existe."""
    cats = database.get_tag_categories(db_path)
    for cat in cats:
        if cat["name"].strip().lower() in ("priority", "prioridad"):
            return cat["id"]
    cat_id = database.create_tag_category(t("task_detail.priority_category_name"), db_path)
    defaults = [
        (t("task_detail.priority_low"), styles.COLORS["accent_2"]),
        (t("task_detail.priority_medium"), styles.COLORS["text_muted"]),
        (t("task_detail.priority_high"), styles.COLORS["accent_pressed"]),
    ]
    for name, color in defaults:
        database.create_tag_value(cat_id, name, color, db_path)
    return cat_id


class PriorityManagerDialog(QDialog):
    """Modal propio e independiente para gestionar los niveles y colores de Prioridad.

    Permite añadir, renombrar, cambiar color y eliminar niveles de prioridad de forma
    aislada, sin que se mezclen ni interfieran con el catálogo general de etiquetas.
    """
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.cat_id = ensure_priority_category(db_path)
        self.setWindowTitle(t("priority_manager.window_title"))
        self.resize(460, 420)
        self.setMinimumSize(400, 360)

        self.new_value_color = styles.COLORS["accent"]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        header = QLabel(t("priority_manager.header"))
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.values_layout = QVBoxLayout(self.container)
        self.values_layout.setContentsMargins(6, 6, 6, 6)
        self.values_layout.setSpacing(6)
        self.values_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area, 1)

        # Fila de alta de nuevo nivel
        add_row = QHBoxLayout()
        add_row.setSpacing(6)
        self.new_value_input = QLineEdit()
        self.new_value_input.setPlaceholderText(t("priority_manager.new_value_placeholder"))
        self.new_value_input.returnPressed.connect(self.add_priority_value)
        self.new_color_btn = QPushButton()
        self.new_color_btn.setFixedSize(30, 26)
        self.new_color_btn.setCursor(Qt.PointingHandCursor)
        self.new_color_btn.clicked.connect(self.pick_new_color)
        self._refresh_new_color_btn()

        self.add_btn = QPushButton(t("priority_manager.add_value_btn"))
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_priority_value)

        add_row.addWidget(self.new_color_btn)
        add_row.addWidget(self.new_value_input, 1)
        add_row.addWidget(self.add_btn)
        layout.addLayout(add_row)

        # Botón inferior para cerrar
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        close_btn = QPushButton(t("priority_manager.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        bottom_row.addWidget(close_btn)
        layout.addLayout(bottom_row)

        self.reload_values()

    def _refresh_new_color_btn(self):
        self.new_color_btn.setStyleSheet(styles.color_swatch_css(self.new_value_color))

    def pick_new_color(self):
        color = QColorDialog.getColor(QColor(self.new_value_color), self, t("tag_manager.color_dialog_title"))
        if color.isValid():
            self.new_value_color = color.name()
            self._refresh_new_color_btn()

    def reload_values(self):
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        values = database.get_tag_values(self.cat_id, self.db_path)
        if not values:
            hint = QLabel(t("tag_manager.no_values_hint"))
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; padding: 8px;")
            self.values_layout.addWidget(hint)
            return

        for value in values:
            self.values_layout.addWidget(self._build_row(value))

    def _build_row(self, value):
        row = QFrame()
        row.setObjectName("TagValueRow")
        h = QHBoxLayout(row)
        h.setContentsMargins(8, 4, 8, 4)
        h.setSpacing(8)

        swatch = QPushButton()
        swatch.setFixedSize(20, 20)
        swatch.setCursor(Qt.PointingHandCursor)
        swatch.setToolTip(t("tag_manager.swatch_tooltip"))
        swatch.setStyleSheet(styles.color_swatch_css(value['color']))
        swatch.clicked.connect(lambda _=False, v=dict(value): self.change_value_color(v))
        h.addWidget(swatch)

        name = QLabel(value["value"])
        name.setStyleSheet("background: transparent; border: none; font-weight: 500;")
        h.addWidget(name)
        h.addStretch()

        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(26, 24)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip(t("tag_manager.rename_value_tooltip"))
        edit_btn.clicked.connect(lambda _=False, v=dict(value): self.rename_value(v))
        h.addWidget(edit_btn)

        del_btn = QPushButton("×")
        del_btn.setObjectName("DangerButton")
        del_btn.setFixedSize(26, 24)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip(t("tag_manager.delete_value_tooltip"))
        del_btn.clicked.connect(lambda _=False, v=dict(value): self.delete_value(v))
        h.addWidget(del_btn)

        return row

    def add_priority_value(self):
        text = self.new_value_input.text().strip()
        if not text:
            return
        if database.value_exists_in_category(self.cat_id, text, db_path=self.db_path):
            QMessageBox.warning(self, t("tag_manager.warn_title"), t("tag_manager.duplicate_value_body"))
            return
        database.create_tag_value(self.cat_id, text, self.new_value_color, self.db_path)
        self.new_value_input.clear()
        self.reload_values()

    def change_value_color(self, value):
        color = QColorDialog.getColor(QColor(value["color"]), self, t("tag_manager.color_dialog_title"))
        if color.isValid():
            database.update_tag_value(value["id"], value["value"], color.name(), self.db_path)
            self.reload_values()

    def rename_value(self, value):
        name, ok = QInputDialog.getText(
            self, t("tag_manager.rename_value_tooltip"), t("tag_manager.new_name_prompt"), text=value["value"]
        )
        name = name.strip()
        if not (ok and name) or name == value["value"]:
            return
        if database.value_exists_in_category(self.cat_id, name, exclude_value_id=value["id"], db_path=self.db_path):
            QMessageBox.warning(self, t("tag_manager.warn_title"), t("tag_manager.duplicate_value_body"))
            return
        database.update_tag_value(value["id"], name, value["color"], self.db_path)
        self.reload_values()

    def delete_value(self, value):
        confirm = QMessageBox.question(
            self, t("tag_manager.delete_value_tooltip"),
            t("tag_manager.delete_value_body", value=value['value']),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_tag_value(value["id"], self.db_path)
            self.reload_values()
