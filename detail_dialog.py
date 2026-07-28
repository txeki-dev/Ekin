from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QScrollArea, QWidget,
    QColorDialog, QMessageBox, QCheckBox, QDateEdit, QComboBox,
    QListWidget, QListWidgetItem, QInputDialog
)
from PySide6.QtGui import (
    QKeySequence, QColor, QShortcut, QFont, QTextCharFormat, QTextListFormat,
    QTextCursor, QPixmap, QIcon
)
from datetime import datetime
import re
import database
import styles


class MarkdownTextEdit(QTextEdit):
    """QTextEdit con atajos tipo Markdown para crear listas al vuelo.

    - `* `, `- `, `+ ` al inicio de una línea -> lista con viñetas (bullet).
    - `1. `, `1) ` al inicio de una línea -> lista numerada.
    - Enter sobre una viñeta vacía -> sale de la lista (comportamiento habitual).
    """

    # Marcadores que disparan cada tipo de lista al pulsar espacio
    _BULLET_MARKERS = ("*", "-", "+")
    _ORDERED_RE = re.compile(r"\d+[.)]")

    def keyPressEvent(self, event):
        cursor = self.textCursor()

        # --- Espacio: intentar convertir el marcador en una lista ---
        if event.key() == Qt.Key_Space and not cursor.hasSelection():
            block = cursor.block()
            # Texto de la línea desde su inicio hasta el cursor
            text_before = block.text()[:cursor.positionInBlock()]
            marker = text_before.strip()

            # Solo si aún no estamos dentro de una lista
            if block.textList() is None:
                if marker in self._BULLET_MARKERS:
                    self._convert_line_to_list(QTextListFormat.ListDisc)
                    event.accept()
                    return
                if self._ORDERED_RE.fullmatch(marker):
                    self._convert_line_to_list(QTextListFormat.ListDecimal)
                    event.accept()
                    return

        # --- Enter sobre una viñeta vacía: salir de la lista ---
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not cursor.hasSelection():
            block = cursor.block()
            if block.textList() is not None and not block.text().strip():
                self._exit_list()
                event.accept()
                return

        super().keyPressEvent(event)

    def _convert_line_to_list(self, style):
        """Elimina el marcador escrito y convierte la línea actual en una lista."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        # Seleccionar desde el inicio de la línea hasta el cursor (el marcador) y borrarlo
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        list_format = QTextListFormat()
        list_format.setStyle(style)
        cursor.createList(list_format)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def _exit_list(self):
        """Saca el bloque actual de la lista, dejando un párrafo normal."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        text_list = cursor.block().textList()
        if text_list is not None:
            # Quitar el bloque de la lista y restablecer la sangría/formato de bloque
            text_list.remove(cursor.block())
            block_format = cursor.blockFormat()
            block_format.setIndent(0)
            block_format.setObjectIndex(-1)
            cursor.setBlockFormat(block_format)
        cursor.endEditBlock()
        self.setTextCursor(cursor)


class RichTextToolbar(QWidget):
    """Barra de formato básica (negrita, cursiva, viñetas) para un QTextEdit."""
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.bold_btn = QPushButton("B")
        self.bold_btn.setObjectName("FormatButton")
        self.bold_btn.setToolTip("Negrita (Ctrl+B)")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setCursor(Qt.PointingHandCursor)
        self.bold_btn.setFixedSize(28, 26)
        bold_font = QFont()
        bold_font.setBold(True)
        self.bold_btn.setFont(bold_font)
        self.bold_btn.clicked.connect(self.toggle_bold)
        layout.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("I")
        self.italic_btn.setObjectName("FormatButton")
        self.italic_btn.setToolTip("Cursiva (Ctrl+I)")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setCursor(Qt.PointingHandCursor)
        self.italic_btn.setFixedSize(28, 26)
        italic_font = QFont()
        italic_font.setItalic(True)
        self.italic_btn.setFont(italic_font)
        self.italic_btn.clicked.connect(self.toggle_italic)
        layout.addWidget(self.italic_btn)

        self.bullet_btn = QPushButton("•")
        self.bullet_btn.setObjectName("FormatButton")
        self.bullet_btn.setToolTip("Lista con viñetas  ·  también con «* », «- » o «+ »")
        self.bullet_btn.setCursor(Qt.PointingHandCursor)
        self.bullet_btn.setFixedSize(28, 26)
        self.bullet_btn.clicked.connect(self.toggle_bullets)
        layout.addWidget(self.bullet_btn)

        layout.addStretch()

        # Mantener el estado visual de los botones sincronizado con el formato actual,
        # ya sea por movimiento del cursor o por atajos nativos (Ctrl+B / Ctrl+I).
        self.text_edit.cursorPositionChanged.connect(self.sync_buttons)
        self.text_edit.currentCharFormatChanged.connect(self.sync_buttons)

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.bold_btn.isChecked() else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_bullets(self):
        cursor = self.text_edit.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)
        cursor.createList(list_format)
        self.text_edit.setFocus()

    def sync_buttons(self, *args):
        fmt = self.text_edit.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())


class LogEntryWidget(QFrame):
    """Representa una única entrada en el diario/chat de la tarea."""
    def __init__(self, log_data, delete_callback, parent=None):
        super().__init__(parent)
        self.log_id = log_data["id"]
        self.delete_callback = delete_callback
        
        self.setObjectName("LogEntryWidget")
        self.init_ui(log_data)

    def init_ui(self, log_data):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Fila superior: Fecha/Hora y botón de eliminar
        top_layout = QHBoxLayout()
        
        # Formatear la fecha
        raw_date = log_data["created_at"]
        try:
            # SQLite por defecto guarda en UTC o local text. Formateamos para mejor lectura
            # Ejemplo: '2026-07-09 19:30:00' -> '09/07/2026 19:30'
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_date = raw_date  # Fallback
            
        timestamp_label = QLabel(formatted_date)
        timestamp_label.setObjectName("LogTimestamp")
        top_layout.addWidget(timestamp_label)
        top_layout.addStretch()

        # Botón sutil para borrar la entrada del diario
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(16, 16)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ef4444;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #dc2626;
                background-color: rgba(239, 68, 68, 0.1);
                border-radius: 2px;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_callback(self.log_id, self))
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)

        # Contenido de la entrada
        content_label = QLabel(log_data["content"])
        content_label.setObjectName("LogContent")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(content_label)


def color_icon(color, size=13):
    """Genera un pequeño icono cuadrado del color indicado (para combos y listas)."""
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class ClickableTagPill(QFrame):
    """Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor).
    El botón de borrar interno consume su propio clic y no dispara esta señal."""
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class TagManagerDialog(QDialog):
    """Gestor del catálogo de etiquetas permanentes.

    Panel izquierdo: las etiquetas (categorías). Panel derecho: los valores de la
    etiqueta seleccionada, cada uno con su color. Los cambios se guardan al instante
    y afectan al catálogo global reutilizable por todas las tareas.
    """
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle("Gestionar Etiquetas")
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
        left.addWidget(QLabel("🏷️ <b>Etiquetas</b>"))

        self.cat_list = QListWidget()
        self.cat_list.currentItemChanged.connect(lambda *_: self.reload_values())
        left.addWidget(self.cat_list)

        cat_btns = QHBoxLayout()
        cat_btns.setSpacing(4)
        add_cat_btn = QPushButton("＋ Nueva")
        add_cat_btn.setCursor(Qt.PointingHandCursor)
        add_cat_btn.clicked.connect(self.add_category)
        rename_cat_btn = QPushButton("✎")
        rename_cat_btn.setToolTip("Renombrar etiqueta")
        rename_cat_btn.setFixedWidth(34)
        rename_cat_btn.setCursor(Qt.PointingHandCursor)
        rename_cat_btn.clicked.connect(self.rename_category)
        del_cat_btn = QPushButton("🗑")
        del_cat_btn.setObjectName("DangerButton")
        del_cat_btn.setToolTip("Eliminar etiqueta")
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
        self.values_title = QLabel("<b>Valores</b>")
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
        self.new_value_input.setPlaceholderText("Nuevo valor (ej. Alta)…")
        self.new_value_input.returnPressed.connect(self.add_value)
        self.new_color_btn = QPushButton()
        self.new_color_btn.setFixedSize(30, 26)
        self.new_color_btn.setCursor(Qt.PointingHandCursor)
        self.new_color_btn.setToolTip("Color del nuevo valor")
        self.new_color_btn.clicked.connect(self.pick_new_color)
        self._refresh_new_color_btn()
        self.add_value_btn = QPushButton("Añadir valor")
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
        close_btn = QPushButton("Cerrar")
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
        name, ok = QInputDialog.getText(self, "Nueva etiqueta", "Nombre de la etiqueta (ej. Prioridad):")
        name = name.strip()
        if ok and name:
            new_id = database.create_tag_category(name, self.db_path)
            self.reload_categories(select_id=new_id)

    def rename_category(self):
        cat_id = self.current_category_id()
        if cat_id is None:
            return
        name, ok = QInputDialog.getText(
            self, "Renombrar etiqueta", "Nuevo nombre:", text=self.current_category_name()
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
            self, "Eliminar etiqueta",
            f"¿Eliminar la etiqueta «{self.current_category_name()}» y todos sus valores?\n"
            "Se quitará de todas las tareas que la usen.",
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
            self.values_title.setText("<b>Valores</b>")
            hint = QLabel("Crea o selecciona una etiqueta a la izquierda para definir sus valores.")
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; padding: 8px;")
            self.values_layout.addWidget(hint)
            return

        self.values_title.setText(f"<b>Valores de «{self.current_category_name()}»</b>")
        values = database.get_tag_values(cat_id, self.db_path)
        if not values:
            hint = QLabel("Aún no hay valores. Añade el primero abajo.")
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
        swatch.setToolTip("Cambiar color")
        swatch.setStyleSheet(
            f"background-color: {value['color']}; border: 1px solid {styles.COLORS['border']}; border-radius: 4px;"
        )
        swatch.clicked.connect(lambda _=False, v=dict(value): self.change_value_color(v))
        h.addWidget(swatch)

        name = QLabel(value["value"])
        name.setStyleSheet("background: transparent; border: none;")
        h.addWidget(name)
        h.addStretch()

        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(26, 24)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Renombrar valor")
        edit_btn.clicked.connect(lambda _=False, v=dict(value): self.rename_value(v))
        h.addWidget(edit_btn)

        del_btn = QPushButton("×")
        del_btn.setObjectName("DangerButton")
        del_btn.setFixedSize(26, 24)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Eliminar valor")
        del_btn.clicked.connect(lambda _=False, v=dict(value): self.delete_value(v))
        h.addWidget(del_btn)

        return row

    def pick_new_color(self):
        color = QColorDialog.getColor(QColor(self.new_value_color), self, "Color del valor")
        if color.isValid():
            self.new_value_color = color.name()
            self._refresh_new_color_btn()

    def _refresh_new_color_btn(self):
        self.new_color_btn.setStyleSheet(
            f"background-color: {self.new_value_color}; border: 1px solid {styles.COLORS['border']}; border-radius: 4px;"
        )

    def add_value(self):
        cat_id = self.current_category_id()
        if cat_id is None:
            return
        text = self.new_value_input.text().strip()
        if not text:
            return
        if database.value_exists_in_category(cat_id, text, db_path=self.db_path):
            QMessageBox.warning(self, "Atención", "Ya existe un valor con ese nombre en esta etiqueta.")
            return
        database.create_tag_value(cat_id, text, self.new_value_color, self.db_path)
        self.new_value_input.clear()
        self.reload_values()

    def change_value_color(self, value):
        color = QColorDialog.getColor(QColor(value["color"]), self, "Color del valor")
        if color.isValid():
            database.update_tag_value(value["id"], value["value"], color.name(), self.db_path)
            self.reload_values()

    def rename_value(self, value):
        cat_id = self.current_category_id()
        name, ok = QInputDialog.getText(self, "Renombrar valor", "Nuevo nombre:", text=value["value"])
        name = name.strip()
        if not (ok and name) or name == value["value"]:
            return
        if database.value_exists_in_category(cat_id, name, exclude_value_id=value["id"], db_path=self.db_path):
            QMessageBox.warning(self, "Atención", "Ya existe un valor con ese nombre en esta etiqueta.")
            return
        database.update_tag_value(value["id"], name, value["color"], self.db_path)
        self.reload_values()

    def delete_value(self, value):
        confirm = QMessageBox.question(
            self, "Eliminar valor",
            f"¿Eliminar el valor «{value['value']}»?\nSe quitará de las tareas que lo tengan asignado.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_tag_value(value["id"], self.db_path)
            self.reload_values()


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


class TaskDetailDialog(QDialog):
    def __init__(self, task_id, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.db_path = db_path
        self.current_tags = []      # Lista de diccionarios {'text': '...', 'color': '...'}
        self.task_deleted = False  # Indica si se borró la tarea desde este diálogo
        
        self.setWindowTitle("Detalles de la Tarea")
        self.resize(800, 550)
        self.setMinimumSize(700, 450)
        
        self.init_ui()
        self.load_task_data()

    def init_ui(self):
        # Layout principal horizontal (Izquierda: Formulario, Derecha: Diario/Log)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ==========================================
        # PANEL IZQUIERDO: DETALLES DE LA TAREA
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # 1. Título
        left_layout.addWidget(QLabel("📝 <b>Título de la Tarea</b>"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ej. Escribir informe mensual...")
        left_layout.addWidget(self.title_input)

        # 2. Descripción
        left_layout.addWidget(QLabel("📄 <b>Descripción / Notas</b>"))
        self.desc_input = MarkdownTextEdit()
        self.desc_input.setPlaceholderText("Añade detalles sobre esta tarea...")
        left_layout.addWidget(RichTextToolbar(self.desc_input))
        left_layout.addWidget(self.desc_input)

        # 3. Fecha de Vencimiento
        due_section = QWidget()
        due_layout = QHBoxLayout(due_section)
        due_layout.setContentsMargins(0, 0, 0, 0)
        due_layout.setSpacing(10)
        
        due_layout.addWidget(QLabel("📅 <b>Vencimiento:</b>"))
        
        self.due_enable_chk = QCheckBox("Habilitar")
        self.due_enable_chk.setCursor(Qt.PointingHandCursor)
        self.due_enable_chk.stateChanged.connect(lambda state: self.due_date_edit.setEnabled(self.due_enable_chk.isChecked()))
        due_layout.addWidget(self.due_enable_chk)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setEnabled(False)
        due_layout.addWidget(self.due_date_edit)
        due_layout.addStretch()
        
        left_layout.addWidget(due_section)

        # 4. Sección de Etiquetas Múltiples
        tags_section = QWidget()
        tags_layout = QVBoxLayout(tags_section)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(4)
        
        tags_layout.addWidget(QLabel("🏷️ <b>Etiquetas:</b>"))
        
        self.tags_container_widget = QWidget()
        self.tags_container_layout = QHBoxLayout(self.tags_container_widget)
        self.tags_container_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_container_layout.setSpacing(6)
        self.tags_container_layout.setAlignment(Qt.AlignLeft)
        tags_layout.addWidget(self.tags_container_widget)
        
        tag_btns_row = QHBoxLayout()
        tag_btns_row.setSpacing(6)
        self.add_tag_btn = QPushButton("➕ Asignar Etiqueta")
        self.add_tag_btn.setCursor(Qt.PointingHandCursor)
        self.add_tag_btn.clicked.connect(self.assign_tag_dialog)
        tag_btns_row.addWidget(self.add_tag_btn)

        self.manage_tags_btn = QPushButton("⚙ Gestionar")
        self.manage_tags_btn.setToolTip("Definir etiquetas permanentes y sus valores")
        self.manage_tags_btn.setCursor(Qt.PointingHandCursor)
        self.manage_tags_btn.clicked.connect(self.open_tag_manager)
        tag_btns_row.addWidget(self.manage_tags_btn)
        tag_btns_row.addStretch()
        tags_layout.addLayout(tag_btns_row)
        
        left_layout.addWidget(tags_section)

        # 5. Subtareas / Checklist
        subtasks_section = QWidget()
        subtasks_outer = QVBoxLayout(subtasks_section)
        subtasks_outer.setContentsMargins(0, 0, 0, 0)
        subtasks_outer.setSpacing(4)

        subtasks_header = QHBoxLayout()
        subtasks_header.setSpacing(6)
        subtasks_header.addWidget(QLabel("☑️ <b>Subtareas</b>"))
        subtasks_header.addStretch()
        self.subtasks_progress_label = QLabel("")
        self.subtasks_progress_label.setStyleSheet(
            f"color: {styles.COLORS['text_muted']}; font-size: 11px;"
        )
        subtasks_header.addWidget(self.subtasks_progress_label)
        subtasks_outer.addLayout(subtasks_header)

        subtasks_scroll = QScrollArea()
        subtasks_scroll.setWidgetResizable(True)
        subtasks_scroll.setFrameShape(QFrame.NoFrame)
        subtasks_scroll.setStyleSheet("background: transparent; border: none;")
        subtasks_scroll.setMaximumHeight(130)
        self.subtasks_container = QWidget()
        self.subtasks_container.setStyleSheet("background: transparent;")
        self.subtasks_layout = QVBoxLayout(self.subtasks_container)
        self.subtasks_layout.setContentsMargins(0, 0, 0, 0)
        self.subtasks_layout.setSpacing(2)
        self.subtasks_layout.setAlignment(Qt.AlignTop)
        subtasks_scroll.setWidget(self.subtasks_container)
        subtasks_outer.addWidget(subtasks_scroll)

        add_sub_row = QHBoxLayout()
        add_sub_row.setSpacing(6)
        self.new_subtask_input = QLineEdit()
        self.new_subtask_input.setPlaceholderText("Nueva subtarea…")
        self.new_subtask_input.returnPressed.connect(self.add_subtask)
        add_sub_row.addWidget(self.new_subtask_input)
        self.add_subtask_btn = QPushButton("➕ Añadir")
        self.add_subtask_btn.setCursor(Qt.PointingHandCursor)
        self.add_subtask_btn.clicked.connect(self.add_subtask)
        add_sub_row.addWidget(self.add_subtask_btn)
        subtasks_outer.addLayout(add_sub_row)

        left_layout.addWidget(subtasks_section)
        left_layout.addStretch()

        # Botones de Acción de la Tarea (Guardar, Eliminar, Cerrar)
        action_layout = QHBoxLayout()
        
        self.delete_task_btn = QPushButton("🗑️ Eliminar")
        self.delete_task_btn.setObjectName("DangerButton")
        self.delete_task_btn.setCursor(Qt.PointingHandCursor)
        self.delete_task_btn.clicked.connect(self.delete_task)
        action_layout.addWidget(self.delete_task_btn)
        
        action_layout.addStretch()

        self.save_btn = QPushButton("💾 Guardar Cambios")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_changes)
        action_layout.addWidget(self.save_btn)

        self.close_btn = QPushButton("❌ Cerrar")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)
        action_layout.addWidget(self.close_btn)

        left_layout.addLayout(action_layout)
        main_layout.addWidget(left_panel, 4)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {styles.COLORS['border']};")
        main_layout.addWidget(separator)

        # ==========================================
        # PANEL DERECHO: DIARIO / HISTORIAL (LOGS)
        # ==========================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        right_layout.addWidget(QLabel("📖 <b>Log / Diario Personal de la Tarea</b>"))

        # Área de Scroll para ver el historial
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        
        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(6, 6, 6, 6)
        self.logs_layout.setSpacing(8)
        self.logs_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.logs_container)
        right_layout.addWidget(self.scroll_area)

        # Caja de entrada para nuevos logs
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.log_input = MarkdownTextEdit()
        self.log_input.setPlaceholderText("Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)")
        self.log_input.setFixedHeight(90)
        input_layout.addWidget(RichTextToolbar(self.log_input))
        input_layout.addWidget(self.log_input)

        log_btn_layout = QHBoxLayout()
        log_btn_layout.addStretch()
        self.add_log_btn = QPushButton("✍️ Añadir al Diario")
        self.add_log_btn.setObjectName("PrimaryButton")
        self.add_log_btn.setCursor(Qt.PointingHandCursor)
        self.add_log_btn.clicked.connect(self.add_log_entry)
        log_btn_layout.addWidget(self.add_log_btn)
        
        input_layout.addLayout(log_btn_layout)
        right_layout.addWidget(input_container)

        main_layout.addWidget(right_panel, 5)

        # Atajo teclado Ctrl+Enter para añadir entrada al diario
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.add_log_entry)
        
        # También mapear Ctrl+Enter del teclado numérico
        shortcut_num = QShortcut(QKeySequence("Ctrl+Enter"), self)
        shortcut_num.activated.connect(self.add_log_entry)

    def load_task_data(self):
        """Carga los datos iniciales de la tarea y sus logs desde la base de datos."""
        task = database.get_task(self.task_id, self.db_path)
        if not task:
            QMessageBox.critical(self, "Error", "No se pudo cargar la tarea.")
            self.reject()
            return

        self.title_input.setText(task["title"])
        self.desc_input.setHtml(task["description"] or "")
        
        # Cargar fecha de vencimiento
        due_date = task.get("due_date")
        if due_date:
            self.due_enable_chk.setChecked(True)
            self.due_date_edit.setEnabled(True)
            self.due_date_edit.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
        else:
            self.due_enable_chk.setChecked(False)
            self.due_date_edit.setEnabled(False)
            self.due_date_edit.setDate(QDate.currentDate())

        # Cargar etiquetas
        self.current_tags = task.get("tags", [])
        self.render_tags()

        # Cargar subtareas (checklist)
        self.reload_subtasks()

        # Cargar los logs
        self.reload_logs()

    def render_tags(self):
        """Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el
        valor; el botón × la retira de la tarea."""
        # Limpiar
        while self.tags_container_layout.count():
            item = self.tags_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.current_tags:
            hint = QLabel("Sin etiquetas. Pulsa «Asignar Etiqueta».")
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;")
            self.tags_container_layout.addWidget(hint)
            return

        for index, tag in enumerate(self.current_tags):
            pill = ClickableTagPill()
            pill.setObjectName("TagPillFrame")
            pill.setCursor(Qt.PointingHandCursor)
            pill.setToolTip("Clic para cambiar el valor")
            pill.setStyleSheet(f"""
                #TagPillFrame {{
                    background-color: {tag['color']};
                    border-radius: 4px;
                }}
            """)
            pill.clicked.connect(lambda idx=index: self.edit_tag_at(idx))
            pill_layout = QHBoxLayout(pill)
            pill_layout.setContentsMargins(6, 2, 6, 2)
            pill_layout.setSpacing(4)

            lbl = QLabel(f"{tag['category']}: {tag['value']}".upper())
            lbl.setStyleSheet("color: #ffffff; font-size: 9px; font-weight: bold; background: transparent; border: none;")
            pill_layout.addWidget(lbl)

            del_btn = QPushButton("×")
            del_btn.setFixedSize(14, 14)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setToolTip("Quitar de la tarea")
            del_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    color: #ef4444;
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 2px;
                }
            """)
            # Usar captura de índice en lambda
            del_btn.clicked.connect(lambda checked=False, idx=index: self.delete_tag_at(idx))
            pill_layout.addWidget(del_btn)

            self.tags_container_layout.addWidget(pill)

    def _set_category_value(self, tag):
        """Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un
        único valor por etiqueta en la tarea y conservando la posición existente."""
        idx = next(
            (i for i, t in enumerate(self.current_tags)
             if t["category"].lower() == tag["category"].lower()),
            None
        )
        if idx is None:
            self.current_tags.append(tag)
        else:
            self.current_tags[idx] = tag
            # Eliminar cualquier duplicado posterior de la misma etiqueta
            self.current_tags = [
                t for i, t in enumerate(self.current_tags)
                if i == idx or t["category"].lower() != tag["category"].lower()
            ]
        self.render_tags()

    def delete_tag_at(self, index):
        """Retira una etiqueta de la tarea (localmente) y re-renderiza."""
        if 0 <= index < len(self.current_tags):
            self.current_tags.pop(index)
            self.render_tags()

    def edit_tag_at(self, index):
        """Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno» (retirarla)."""
        if not (0 <= index < len(self.current_tags)):
            return
        tag = self.current_tags[index]
        dialog = TagPickerDialog(
            self.db_path, self,
            fixed_category={"id": tag["category_id"], "name": tag["category"]},
            current_value_id=tag["tag_value_id"],
            allow_none=True
        )
        if dialog.exec() != QDialog.Accepted:
            return

        value_id, is_none = dialog.get_selection()
        if is_none or value_id is None:
            self.current_tags.pop(index)
            self.render_tags()
            return

        new_tag = database.get_tag_value(value_id, self.db_path)
        if new_tag:
            self.current_tags[index] = new_tag
            self.render_tags()

    def assign_tag_dialog(self):
        """Asigna una etiqueta permanente (categoría) con uno de sus valores a la tarea."""
        dialog = TagPickerDialog(self.db_path, self)
        if dialog.exec() != QDialog.Accepted:
            return

        value_id, _ = dialog.get_selection()
        if value_id is None:
            return

        tag = database.get_tag_value(value_id, self.db_path)
        if tag:
            self._set_category_value(tag)

    def open_tag_manager(self):
        """Abre el gestor del catálogo de etiquetas y re-sincroniza las etiquetas asignadas."""
        TagManagerDialog(self.db_path, self).exec()
        self.refresh_current_tags_from_db()

    def refresh_current_tags_from_db(self):
        """Refresca los datos (valor/color) de las etiquetas asignadas y descarta las que
        hayan sido eliminadas del catálogo desde el gestor."""
        refreshed = []
        for tag in self.current_tags:
            latest = database.get_tag_value(tag["tag_value_id"], self.db_path)
            if latest:
                refreshed.append(latest)
        self.current_tags = refreshed
        self.render_tags()

    def save_changes(self):
        """Guarda el título, descripción, etiquetas y fecha de vencimiento."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Atención", "El título de la tarea no puede estar vacío.")
            return

        description = self.desc_input.toHtml()

        # Obtener fecha de vencimiento
        due_date = None
        if self.due_enable_chk.isChecked():
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd")

        # Guardar tarea principal (las columnas tag_text/tag_color quedan sin uso: las etiquetas
        # estructuradas viven en task_tags/tag_values)
        database.update_task(self.task_id, title, description, "", "#6b7280", due_date, self.db_path)

        # Guardar las etiquetas asignadas
        tag_value_ids = [tag["tag_value_id"] for tag in self.current_tags]
        database.set_task_tags(self.task_id, tag_value_ids, self.db_path)

        self.accept()

    def delete_task(self):
        """Borra definitivamente la tarea actual de la base de datos."""
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Estás seguro de que deseas eliminar esta tarea de forma permanente? No se podrá recuperar.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_task(self.task_id, self.db_path)
            self.task_deleted = True
            self.accept()

    # --- Subtareas / checklist (se persisten al instante, como los logs) ---

    def reload_subtasks(self):
        """Limpia y vuelve a pintar el checklist de la tarea desde la base de datos."""
        while self.subtasks_layout.count():
            item = self.subtasks_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        subtasks = database.get_subtasks(self.task_id, self.db_path)
        if not subtasks:
            hint = QLabel("Sin subtareas todavía.")
            hint.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;"
            )
            self.subtasks_layout.addWidget(hint)
        else:
            for sub in subtasks:
                self.subtasks_layout.addWidget(self._build_subtask_row(sub))
        self._update_subtask_progress(subtasks)

    def _build_subtask_row(self, sub):
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        chk = QCheckBox()
        chk.setChecked(bool(sub["done"]))
        chk.setCursor(Qt.PointingHandCursor)
        # `clicked` (no `toggled`) para que el setChecked programático del reload no reentre.
        chk.clicked.connect(lambda checked, sid=sub["id"]: self.toggle_subtask(sid, checked))
        row_layout.addWidget(chk)

        title_edit = QLineEdit(sub["title"])
        title_edit.setFrame(False)
        if sub["done"]:
            title_edit.setStyleSheet("background: transparent; border: none; color: #64748b;")
        else:
            title_edit.setStyleSheet("background: transparent; border: none;")
        title_edit.editingFinished.connect(
            lambda sid=sub["id"], le=title_edit: self.rename_subtask(sid, le.text())
        )
        row_layout.addWidget(title_edit, 1)

        del_btn = QPushButton("×")
        del_btn.setFixedSize(18, 18)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Eliminar subtarea")
        del_btn.clicked.connect(lambda _=False, sid=sub["id"]: self.remove_subtask(sid))
        row_layout.addWidget(del_btn)
        return row

    def add_subtask(self):
        text = self.new_subtask_input.text().strip()
        if not text:
            return
        database.create_subtask(self.task_id, text, self.db_path)
        self.new_subtask_input.clear()
        self.reload_subtasks()

    def toggle_subtask(self, subtask_id, checked):
        database.set_subtask_done(subtask_id, checked, self.db_path)
        self.reload_subtasks()  # refresca tachado + progreso

    def rename_subtask(self, subtask_id, text):
        text = text.strip()
        if not text:
            self.reload_subtasks()  # título vacío: restaura el anterior
            return
        database.update_subtask_title(subtask_id, text, self.db_path)

    def remove_subtask(self, subtask_id):
        database.delete_subtask(subtask_id, self.db_path)
        self.reload_subtasks()

    def _update_subtask_progress(self, subtasks=None):
        if subtasks is None:
            subtasks = database.get_subtasks(self.task_id, self.db_path)
        total = len(subtasks)
        done = sum(1 for s in subtasks if s["done"])
        if total == 0:
            self.subtasks_progress_label.setText("")
        else:
            pct = int(done / total * 100)
            self.subtasks_progress_label.setText(f"{done}/{total} · {pct}%")

    def reload_logs(self):
        """Limpia y vuelve a cargar todos los logs/entradas del diario."""
        # Limpiar contenedor de logs
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Consultar y agregar los logs
        logs = database.get_logs(self.task_id, self.db_path)
        for log in logs:
            log_widget = LogEntryWidget(log, self.delete_log_entry, self)
            self.logs_layout.addWidget(log_widget)
        
        # Pequeño retardo para dar tiempo a Qt a renderizar antes de bajar el scroll
        self.scroll_to_bottom()

    def add_log_entry(self):
        """Crea una nueva entrada de diario con el texto del input."""
        if not self.log_input.toPlainText().strip():
            return  # No añadir logs vacíos

        database.create_log(self.task_id, self.log_input.toHtml(), self.db_path)
        self.log_input.clear()
        
        # En vez de recargar todo, recargamos para asegurar sincronización limpia
        self.reload_logs()

    def delete_log_entry(self, log_id, widget):
        """Elimina una entrada de diario tras confirmación."""
        confirm = QMessageBox.question(
            self,
            "Eliminar Entrada",
            "¿Estás seguro de que deseas borrar esta entrada del diario?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_log(log_id, self.db_path)
            widget.deleteLater()

    def scroll_to_bottom(self):
        """Mueve la barra de desplazamiento del diario hasta abajo."""
        # Usamos un timer de un solo disparo o directamente el valor del scrollbar
        # ya que Qt a veces tarda un instante en actualizar el scroll máximo
        scrollbar = self.scroll_area.verticalScrollBar()
        # Conectamos de forma asíncrona sutil para que se ejecute después del repaint
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: scrollbar.setValue(scrollbar.maximum()))
