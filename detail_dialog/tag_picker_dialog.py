from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
)
import database
import styles
from .tag_pill import color_icon
from .tag_manager_dialog import TagManagerDialog


class TagPickerDialog(QDialog):
    """Selecciona una etiqueta del catálogo para una tarea.

    - Modo asignar (fixed_category=None): elige una etiqueta y uno de sus valores.
    - Modo editar (fixed_category dado): la etiqueta queda fija y se elige otro valor
      o «Ninguno» (que la oculta/retira de la tarea).
    """
    def __init__(self, db_path, parent=None, fixed_category=None, current_value_id=None, allow_none=False):
        super().__init__(parent)
        self.db_path = db_path
        self.fixed_category = fixed_category   # dict {'id', 'name'} o None
        self.current_value_id = current_value_id
        self.allow_none = allow_none
        self._result_value_id = None
        self._is_none = False

        self.setWindowTitle("Editar Etiqueta" if fixed_category else "Asignar Etiqueta")
        self.setMinimumWidth(340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        layout.addWidget(QLabel("🏷️ <b>Etiqueta</b>"))
        if fixed_category:
            cat_label = QLabel(fixed_category["name"])
            cat_label.setStyleSheet(
                f"background-color: {styles.COLORS['bg_main']}; border: 1px solid {styles.COLORS['border']};"
                " border-radius: 6px; padding: 6px; font-weight: bold;"
            )
            layout.addWidget(cat_label)
        else:
            self.category_combo = QComboBox()
            self.category_combo.currentIndexChanged.connect(lambda *_: self.reload_values())
            layout.addWidget(self.category_combo)

        layout.addWidget(QLabel("<b>Valor</b>"))
        self.value_combo = QComboBox()
        layout.addWidget(self.value_combo)

        self.hint_label = QLabel("")
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 10px;")
        layout.addWidget(self.hint_label)

        manage_btn = QPushButton("⚙  Gestionar etiquetas…")
        manage_btn.setCursor(Qt.PointingHandCursor)
        manage_btn.clicked.connect(self.open_manager)
        layout.addWidget(manage_btn)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("Aceptar")
        ok_btn.setObjectName("PrimaryButton")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.on_accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.reload_catalog()

    def reload_catalog(self):
        if not self.fixed_category:
            self.category_combo.blockSignals(True)
            self.category_combo.clear()
            for cat in database.get_tag_categories(self.db_path):
                self.category_combo.addItem(cat["name"], cat["id"])
            self.category_combo.blockSignals(False)
        self.reload_values()

    def selected_category_id(self):
        if self.fixed_category:
            return self.fixed_category["id"]
        return self.category_combo.currentData()

    def reload_values(self):
        self.value_combo.clear()
        if self.allow_none:
            self.value_combo.addItem("— Ninguno (ocultar) —", None)

        cat_id = self.selected_category_id()
        if cat_id is None:
            self.hint_label.setText("No hay etiquetas definidas. Usa «Gestionar etiquetas…» para crear una.")
            return

        values = database.get_tag_values(cat_id, self.db_path)
        if not values:
            self.hint_label.setText("Esta etiqueta no tiene valores. Añádelos en «Gestionar etiquetas…».")
        else:
            self.hint_label.setText("")

        for value in values:
            self.value_combo.addItem(color_icon(value["color"]), value["value"], value["id"])

        if self.current_value_id is not None:
            idx = self.value_combo.findData(self.current_value_id)
            if idx >= 0:
                self.value_combo.setCurrentIndex(idx)

    def open_manager(self):
        TagManagerDialog(self.db_path, self).exec()
        self.reload_catalog()

    def on_accept(self):
        cat_id = self.selected_category_id()
        if cat_id is None:
            QMessageBox.warning(self, "Atención", "Primero crea una etiqueta en «Gestionar etiquetas…».")
            return
        data = self.value_combo.currentData()
        if data is None and not self.allow_none:
            QMessageBox.warning(self, "Atención", "Selecciona un valor (o créalo en «Gestionar etiquetas…»).")
            return
        self._result_value_id = data
        self._is_none = data is None
        self.accept()

    def get_selection(self):
        """Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»."""
        return self._result_value_id, self._is_none
