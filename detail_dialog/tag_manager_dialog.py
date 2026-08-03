from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget,
    QColorDialog, QMessageBox, QListWidget, QListWidgetItem, QInputDialog
)
from PySide6.QtGui import QColor
import database
import styles
from strings import t


class TagManagerDialog(QDialog):
    """Gestor del catálogo de etiquetas permanentes.

    Panel izquierdo: las etiquetas (categorías). Panel derecho: los valores de la
    etiqueta seleccionada, cada uno con su color. Los cambios se guardan al instante
    y afectan al catálogo global reutilizable por todas las tareas.
    """
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle(t("tag_manager.window_title"))
        self.resize(600, 440)
        self.setMinimumSize(520, 380)

        self.new_value_color = "#3b82f6"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(15, 15, 15, 15)
        outer.setSpacing(12)

        content = QHBoxLayout()
        content.setSpacing(14)

        # --- Panel izquierdo: etiquetas (categorías) ---
        left = QVBoxLayout()
        left.setSpacing(6)
        left.addWidget(QLabel(t("tag_manager.header")))

        self.cat_list = QListWidget()
        self.cat_list.currentItemChanged.connect(lambda *_: self.reload_values())
        left.addWidget(self.cat_list)

        cat_btns = QHBoxLayout()
        cat_btns.setSpacing(4)
        add_cat_btn = QPushButton(t("tag_manager.add_category_btn"))
        add_cat_btn.setCursor(Qt.PointingHandCursor)
        add_cat_btn.clicked.connect(self.add_category)
        rename_cat_btn = QPushButton("✎")
        rename_cat_btn.setToolTip(t("tag_manager.category_action_label"))
        rename_cat_btn.setFixedWidth(34)
        rename_cat_btn.setCursor(Qt.PointingHandCursor)
        rename_cat_btn.clicked.connect(self.rename_category)
        del_cat_btn = QPushButton("🗑")
        del_cat_btn.setObjectName("DangerButton")
        del_cat_btn.setToolTip(t("tag_manager.delete_category_tooltip"))
        del_cat_btn.setFixedWidth(34)
        del_cat_btn.setCursor(Qt.PointingHandCursor)
        del_cat_btn.clicked.connect(self.delete_category)
        cat_btns.addWidget(add_cat_btn)
        cat_btns.addWidget(rename_cat_btn)
        cat_btns.addWidget(del_cat_btn)
        cat_btns.addStretch()
        left.addLayout(cat_btns)
        content.addLayout(left, 2)

        # --- Panel derecho: valores de la etiqueta seleccionada ---
        right = QVBoxLayout()
        right.setSpacing(6)
        self.values_title = QLabel(t("tag_manager.values_title_default"))
        right.addWidget(self.values_title)

        self.values_scroll = QScrollArea()
        self.values_scroll.setObjectName("ChatScrollArea")
        self.values_scroll.setWidgetResizable(True)
        self.values_container = QWidget()
        self.values_layout = QVBoxLayout(self.values_container)
        self.values_layout.setContentsMargins(6, 6, 6, 6)
        self.values_layout.setSpacing(6)
        self.values_layout.setAlignment(Qt.AlignTop)
        self.values_scroll.setWidget(self.values_container)
        right.addWidget(self.values_scroll)

        add_row = QHBoxLayout()
        add_row.setSpacing(6)
        self.new_value_input = QLineEdit()
        self.new_value_input.setPlaceholderText(t("tag_manager.new_value_placeholder"))
        self.new_value_input.returnPressed.connect(self.add_value)
        self.new_color_btn = QPushButton()
        self.new_color_btn.setFixedSize(30, 26)
        self.new_color_btn.setCursor(Qt.PointingHandCursor)
        self.new_color_btn.setToolTip(t("tag_manager.new_value_color_tooltip"))
        self.new_color_btn.clicked.connect(self.pick_new_color)
        self._refresh_new_color_btn()
        self.add_value_btn = QPushButton(t("tag_manager.add_value_btn"))
        self.add_value_btn.setObjectName("PrimaryButton")
        self.add_value_btn.setCursor(Qt.PointingHandCursor)
        self.add_value_btn.clicked.connect(self.add_value)
        add_row.addWidget(self.new_value_input)
        add_row.addWidget(self.new_color_btn)
        add_row.addWidget(self.add_value_btn)
        right.addLayout(add_row)
        content.addLayout(right, 3)

        outer.addLayout(content)

        bottom = QHBoxLayout()
        bottom.addStretch()
        close_btn = QPushButton(t("tag_manager.close_btn"))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)
        outer.addLayout(bottom)

        self.reload_categories()

    # --- Categorías (etiquetas permanentes) ---

    def reload_categories(self, select_id=None):
        previous = select_id if select_id is not None else self.current_category_id()
        self.cat_list.blockSignals(True)
        self.cat_list.clear()
        for cat in database.get_tag_categories(self.db_path):
            item = QListWidgetItem(cat["name"])
            item.setData(Qt.UserRole, cat["id"])
            self.cat_list.addItem(item)
            if cat["id"] == previous:
                self.cat_list.setCurrentItem(item)
        if self.cat_list.currentItem() is None and self.cat_list.count() > 0:
            self.cat_list.setCurrentRow(0)
        self.cat_list.blockSignals(False)
        self.reload_values()

    def current_category_id(self):
        item = self.cat_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def current_category_name(self):
        item = self.cat_list.currentItem()
        return item.text() if item else None

    def add_category(self):
        name, ok = QInputDialog.getText(
            self, t("tag_manager.add_category_dialog_title"), t("tag_manager.add_category_prompt")
        )
        name = name.strip()
        if ok and name:
            new_id = database.create_tag_category(name, self.db_path)
            self.reload_categories(select_id=new_id)

    def rename_category(self):
        cat_id = self.current_category_id()
        if cat_id is None:
            return
        name, ok = QInputDialog.getText(
            self, t("tag_manager.category_action_label"), t("tag_manager.new_name_prompt"),
            text=self.current_category_name()
        )
        name = name.strip()
        if ok and name:
            database.rename_tag_category(cat_id, name, self.db_path)
            self.reload_categories(select_id=cat_id)

    def delete_category(self):
        cat_id = self.current_category_id()
        if cat_id is None:
            return
        confirm = QMessageBox.question(
            self, t("tag_manager.delete_category_tooltip"),
            t("tag_manager.delete_category_body", category=self.current_category_name()),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_tag_category(cat_id, self.db_path)
            self.reload_categories()

    # --- Valores de la etiqueta seleccionada ---

    def reload_values(self):
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        cat_id = self.current_category_id()
        has_category = cat_id is not None
        self.new_value_input.setEnabled(has_category)
        self.new_color_btn.setEnabled(has_category)
        self.add_value_btn.setEnabled(has_category)

        if not has_category:
            self.values_title.setText(t("tag_manager.values_title_default"))
            hint = QLabel(t("tag_manager.no_category_hint"))
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; padding: 8px;")
            self.values_layout.addWidget(hint)
            return

        self.values_title.setText(t("tag_manager.values_title_for_category", category=self.current_category_name()))
        values = database.get_tag_values(cat_id, self.db_path)
        if not values:
            hint = QLabel(t("tag_manager.no_values_hint"))
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; padding: 8px;")
            self.values_layout.addWidget(hint)
            return

        for value in values:
            self.values_layout.addWidget(self._build_value_row(value))

    def _build_value_row(self, value):
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
        name.setStyleSheet("background: transparent; border: none;")
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

    def pick_new_color(self):
        color = QColorDialog.getColor(QColor(self.new_value_color), self, t("tag_manager.color_dialog_title"))
        if color.isValid():
            self.new_value_color = color.name()
            self._refresh_new_color_btn()

    def _refresh_new_color_btn(self):
        self.new_color_btn.setStyleSheet(styles.color_swatch_css(self.new_value_color))

    def add_value(self):
        cat_id = self.current_category_id()
        if cat_id is None:
            return
        text = self.new_value_input.text().strip()
        if not text:
            return
        if database.value_exists_in_category(cat_id, text, db_path=self.db_path):
            QMessageBox.warning(self, t("tag_manager.warn_title"), t("tag_manager.duplicate_value_body"))
            return
        database.create_tag_value(cat_id, text, self.new_value_color, self.db_path)
        self.new_value_input.clear()
        self.reload_values()

    def change_value_color(self, value):
        color = QColorDialog.getColor(QColor(value["color"]), self, t("tag_manager.color_dialog_title"))
        if color.isValid():
            database.update_tag_value(value["id"], value["value"], color.name(), self.db_path)
            self.reload_values()

    def rename_value(self, value):
        cat_id = self.current_category_id()
        name, ok = QInputDialog.getText(
            self, t("tag_manager.rename_value_tooltip"), t("tag_manager.new_name_prompt"), text=value["value"]
        )
        name = name.strip()
        if not (ok and name) or name == value["value"]:
            return
        if database.value_exists_in_category(cat_id, name, exclude_value_id=value["id"], db_path=self.db_path):
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
