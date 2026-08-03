from PySide6.QtCore import Qt, QDate, QTime, QUrl, Signal, QBuffer, QIODevice, QSize
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QScrollArea, QWidget,
    QColorDialog, QMessageBox, QCheckBox, QDateEdit, QTimeEdit, QComboBox,
    QListWidget, QListWidgetItem, QInputDialog
)
from PySide6.QtGui import (
    QKeySequence, QColor, QShortcut, QFont, QTextCharFormat, QTextListFormat,
    QTextCursor, QPixmap, QIcon, QImage, QDesktopServices
)
from datetime import datetime
import re
import database
import styles
from widgets import make_glyph_icon


class MarkdownTextEdit(QTextEdit):
    """QTextEdit con atajos tipo Markdown para crear listas al vuelo.

    - `* `, `- `, `+ ` al inicio de una línea -> lista con viñetas (bullet).
    - `1. `, `1) ` al inicio de una línea -> lista numerada.
    - Enter sobre una viñeta vacía -> sale de la lista (comportamiento habitual).
    """

    # Marcadores que disparan cada tipo de lista al pulsar espacio
    _BULLET_MARKERS = ("*", "-", "+")
    _ORDERED_RE = re.compile(r"\d+[.)]")

    def __init__(self, parent=None):
        super().__init__(parent)
        # Si se define, devuelve el ancho máximo (px) para imágenes pegadas. Sirve para
        # que las imágenes del chat quepan en el histórico (más estrecho que el editor).
        self.image_width_provider = None

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)

        # --- Negrita: Ctrl+B o Ctrl+N (Negrita en Word en español) ---
        if ctrl and event.key() in (Qt.Key_B, Qt.Key_N):
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Normal if self.fontWeight() > QFont.Normal else QFont.Bold)
            self.mergeCurrentCharFormat(fmt)
            event.accept()
            return
        # --- Cursiva: Ctrl+K (Cursiva en Word) o Ctrl+I ---
        if ctrl and event.key() in (Qt.Key_K, Qt.Key_I):
            fmt = QTextCharFormat()
            fmt.setFontItalic(not self.fontItalic())
            self.mergeCurrentCharFormat(fmt)
            event.accept()
            return

        # --- Tab / Shift+Tab dentro de una lista: anidar / desanidar la viñeta ---
        if event.key() == Qt.Key_Tab and cursor.block().textList() is not None and not cursor.hasSelection():
            self._change_list_indent(+1)
            event.accept()
            return
        if event.key() == Qt.Key_Backtab and cursor.block().textList() is not None:
            self._change_list_indent(-1)
            event.accept()
            return

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

    def insertFromMimeData(self, source):
        """Al pegar: las imágenes se insertan como imagen; el texto, SIEMPRE sin formato.

        Así el contenido copiado de webs/Word se pega como texto plano (sin fuentes ni
        colores ajenos), pero se pueden pegar capturas/imágenes del portapapeles."""
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage) and not image.isNull():
                self._insert_image(image)
                return
        if source.hasText():
            self.insertPlainText(source.text())
            return
        super().insertFromMimeData(source)

    def _insert_image(self, image):
        """Embebe un QImage como data URI base64 (queda guardado dentro del HTML).
        Ajusta la imagen al ancho útil (el del histórico del chat si se ha configurado
        un `image_width_provider`, que es más estrecho que el editor)."""
        if self.image_width_provider:
            avail = max(120, self.image_width_provider())
        else:
            avail = max(120, self.viewport().width() - 24)
        if image.width() > avail:
            image = image.scaledToWidth(avail, Qt.SmoothTransformation)
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        b64 = bytes(buffer.data().toBase64()).decode("ascii")
        buffer.close()
        self.textCursor().insertHtml(f'<img src="data:image/png;base64,{b64}" />')

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

    @staticmethod
    def _style_for_indent(current_style, indent):
        """Elige el símbolo de viñeta según el nivel de anidamiento (las listas
        numeradas conservan su estilo)."""
        ordered = current_style in (
            QTextListFormat.ListDecimal, QTextListFormat.ListLowerAlpha,
            QTextListFormat.ListUpperAlpha, QTextListFormat.ListLowerRoman,
            QTextListFormat.ListUpperRoman,
        )
        if ordered:
            return current_style
        bullets = [QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare]
        return bullets[(max(1, indent) - 1) % len(bullets)]

    def _change_list_indent(self, delta):
        """Aumenta (Tab) o reduce (Shift+Tab) el nivel de anidamiento de la viñeta actual."""
        cursor = self.textCursor()
        current = cursor.currentList()
        if current is None:
            return
        fmt = current.format()
        new_indent = max(1, fmt.indent() + delta)
        cursor.beginEditBlock()
        new_fmt = QTextListFormat()
        new_fmt.setIndent(new_indent)
        new_fmt.setStyle(self._style_for_indent(fmt.style(), new_indent))
        cursor.createList(new_fmt)
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
        self.bold_btn.setToolTip("Negrita (Ctrl+B o Ctrl+N)")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setCursor(Qt.PointingHandCursor)
        self.bold_btn.setFixedSize(28, 26)
        bold_font = QFont()
        bold_font.setBold(True)
        self.bold_btn.setFont(bold_font)
        self.bold_btn.clicked.connect(self.toggle_bold)
        layout.addWidget(self.bold_btn)

        # Etiqueta "K" (Cursiva): una "I" en cursiva se ve como "/", que confunde.
        self.italic_btn = QPushButton("K")
        self.italic_btn.setObjectName("FormatButton")
        self.italic_btn.setToolTip("Cursiva (Ctrl+K o Ctrl+I)")
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
    """Una entrada del diario/chat, con botones (pintados) de editar y eliminar y
    edición en línea del contenido."""
    def __init__(self, log_data, delete_callback, save_edit_callback, parent=None):
        super().__init__(parent)
        self.log_data = log_data
        self.log_id = log_data["id"]
        self.delete_callback = delete_callback
        self.save_edit_callback = save_edit_callback
        self._editing = False

        self.setObjectName("LogEntryWidget")
        self.init_ui(log_data)

    def _icon_button(self, kind, color, tooltip, hover_rgba):
        btn = QPushButton()
        btn.setFixedSize(20, 20)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setIcon(make_glyph_icon(kind, color, 13))
        btn.setIconSize(QSize(13, 13))
        btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            f"QPushButton:hover {{ background-color: {hover_rgba}; border-radius: 3px; }}"
        )
        return btn

    def init_ui(self, log_data):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(4)

        # Fila superior: Fecha/Hora + botones de editar y eliminar
        top_layout = QHBoxLayout()

        raw_date = log_data["created_at"]
        try:
            # Ej: '2026-07-09 19:30:00' -> '09/07/2026 19:30'
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_date = raw_date

        timestamp_label = QLabel(formatted_date)
        timestamp_label.setObjectName("LogTimestamp")
        top_layout.addWidget(timestamp_label)
        top_layout.addStretch()

        self.edit_btn = self._icon_button(
            "pencil", "#94a3b8", "Editar comentario", "rgba(148, 163, 184, 0.20)")
        self.edit_btn.clicked.connect(self._enter_edit_mode)
        top_layout.addWidget(self.edit_btn)

        self.delete_btn = self._icon_button(
            "cross", "#ef4444", "Eliminar comentario", "rgba(239, 68, 68, 0.15)")
        self.delete_btn.clicked.connect(lambda: self.delete_callback(self.log_id, self))
        top_layout.addWidget(self.delete_btn)

        self._layout.addLayout(top_layout)

        # Contenido de la entrada
        self.content_label = QLabel(log_data["content"])
        self.content_label.setObjectName("LogContent")
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._layout.addWidget(self.content_label)

    def _enter_edit_mode(self):
        """Sustituye el contenido por un editor en línea con Guardar/Cancelar."""
        if self._editing:
            return
        self._editing = True
        self.content_label.hide()
        self.edit_btn.setEnabled(False)

        self._editor = MarkdownTextEdit()
        self._editor.setHtml(self.log_data["content"])
        self._editor.setMinimumHeight(90)
        self._layout.addWidget(RichTextToolbar(self._editor))
        self._layout.addWidget(self._editor)

        btns = QHBoxLayout()
        btns.addStretch()
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(lambda: self.save_edit_callback(self.log_id, self._editor.toHtml()))
        btns.addWidget(save_btn)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self.save_edit_callback(self.log_id, None))
        btns.addWidget(cancel_btn)
        self._layout.addLayout(btns)
        self._editor.setFocus()


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
        self.modified = False      # Indica si hubo algún cambio real (título, tags, diario, enlaces...)
        
        self.setWindowTitle("Detalles de la Tarea")
        self.resize(1120, 720)
        self.setMinimumSize(940, 580)
        
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
        self.due_enable_chk.stateChanged.connect(self._sync_due_enabled)
        due_layout.addWidget(self.due_enable_chk)

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setEnabled(False)
        due_layout.addWidget(self.due_date_edit)

        # Hora de vencimiento opcional (activa un aviso en el .ics)
        self.due_time_chk = QCheckBox("Hora")
        self.due_time_chk.setCursor(Qt.PointingHandCursor)
        self.due_time_chk.setToolTip("Añadir hora al vencimiento (crea un aviso en el calendario)")
        self.due_time_chk.stateChanged.connect(self._sync_due_enabled)
        due_layout.addWidget(self.due_time_chk)
        self.due_time_edit = QTimeEdit()
        self.due_time_edit.setDisplayFormat("HH:mm")
        self.due_time_edit.setTime(QTime(9, 0))
        self.due_time_edit.setEnabled(False)
        due_layout.addWidget(self.due_time_edit)

        # Recurrencia (repetir la tarea)
        due_layout.addWidget(QLabel("🔁"))
        self._recurrence_values = ["none", "daily", "weekly", "monthly"]
        self.recurrence_combo = QComboBox()
        for label in ("Sin repetir", "Diaria", "Semanal", "Mensual"):
            self.recurrence_combo.addItem(label)
        self.recurrence_combo.setToolTip("Repetir la tarea: al pasar la fecha, se adelanta sola")
        due_layout.addWidget(self.recurrence_combo)
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

        # 5. Enlaces / adjuntos
        links_section = QWidget()
        links_outer = QVBoxLayout(links_section)
        links_outer.setContentsMargins(0, 0, 0, 0)
        links_outer.setSpacing(4)
        links_outer.addWidget(QLabel("🔗 <b>Enlaces / adjuntos:</b>"))

        self.links_container = QWidget()
        self.links_layout = QVBoxLayout(self.links_container)
        self.links_layout.setContentsMargins(0, 0, 0, 0)
        self.links_layout.setSpacing(2)
        links_outer.addWidget(self.links_container)

        add_link_row = QHBoxLayout()
        add_link_row.setSpacing(6)
        self.link_url_input = QLineEdit()
        self.link_url_input.setPlaceholderText("URL o ruta…")
        self.link_url_input.returnPressed.connect(self.add_link)
        add_link_row.addWidget(self.link_url_input, 2)
        self.link_label_input = QLineEdit()
        self.link_label_input.setPlaceholderText("Nombre (opcional)")
        add_link_row.addWidget(self.link_label_input, 1)
        add_link_btn = QPushButton("➕")
        add_link_btn.setFixedWidth(30)
        add_link_btn.setCursor(Qt.PointingHandCursor)
        add_link_btn.setToolTip("Añadir enlace")
        add_link_btn.clicked.connect(self.add_link)
        add_link_row.addWidget(add_link_btn)
        links_outer.addLayout(add_link_row)

        left_layout.addWidget(links_section)
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
        right_layout.addWidget(self.scroll_area, 1)  # el historial domina el alto

        # Caja de entrada para nuevos logs
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.log_input = MarkdownTextEdit()
        self.log_input.setPlaceholderText("Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)")
        # Caja cómoda que crece con el texto (sin límite de caracteres; solo tope visual)
        self.log_input.setMinimumHeight(110)
        self.log_input.setMaximumHeight(260)
        # Las imágenes pegadas en el chat se ajustan al ancho del histórico (más estrecho)
        self.log_input.image_width_provider = self._chat_image_width
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

    def _sync_due_enabled(self):
        """Habilita/inhabilita fecha y hora según los checks."""
        due_on = self.due_enable_chk.isChecked()
        self.due_date_edit.setEnabled(due_on)
        self.due_time_chk.setEnabled(due_on)
        self.due_time_edit.setEnabled(due_on and self.due_time_chk.isChecked())

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

        # Cargar hora de vencimiento
        due_time = task.get("due_time")
        if due_date and due_time:
            self.due_time_chk.setChecked(True)
            self.due_time_edit.setTime(QTime.fromString(due_time, "HH:mm"))
        else:
            self.due_time_chk.setChecked(False)
        self._sync_due_enabled()

        # Cargar recurrencia
        rec = task.get("recurrence", "none") or "none"
        self.recurrence_combo.setCurrentIndex(
            self._recurrence_values.index(rec) if rec in self._recurrence_values else 0
        )

        # Cargar etiquetas
        self.current_tags = task.get("tags", [])
        self.render_tags()

        # Cargar enlaces y logs
        self.reload_links()
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

        # Obtener fecha y hora de vencimiento
        due_date = None
        due_time = None
        if self.due_enable_chk.isChecked():
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
            if self.due_time_chk.isChecked():
                due_time = self.due_time_edit.time().toString("HH:mm")

        # Guardar tarea principal (las columnas tag_text/tag_color quedan sin uso: las etiquetas
        # estructuradas viven en task_tags/tag_values)
        database.update_task(self.task_id, title, description, "", "#6b7280", due_date, self.db_path)
        database.set_task_due_time(self.task_id, due_time, self.db_path)

        # Guardar las etiquetas asignadas
        tag_value_ids = [tag["tag_value_id"] for tag in self.current_tags]
        database.set_task_tags(self.task_id, tag_value_ids, self.db_path)

        # Guardar la recurrencia
        database.set_task_recurrence(
            self.task_id, self._recurrence_values[self.recurrence_combo.currentIndex()], self.db_path
        )

        self.modified = True
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
            # Snapshot antes de borrar, para poder deshacer (Ctrl+Z)
            self.deleted_snapshot = database.snapshot_task(self.task_id, self.db_path)
            database.delete_task(self.task_id, self.db_path)
            self.task_deleted = True
            self.accept()

    # --- Enlaces / adjuntos (persistidos al instante) ---

    def reload_links(self):
        while self.links_layout.count():
            item = self.links_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        links = database.get_task_links(self.task_id, self.db_path)
        if not links:
            hint = QLabel("Sin enlaces.")
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;")
            self.links_layout.addWidget(hint)
            return
        for link in links:
            self.links_layout.addWidget(self._build_link_row(link))

    def _build_link_row(self, link):
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        open_btn = QPushButton("🔗 " + (link["label"] or link["url"]))
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setToolTip(link["url"])
        open_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #60a5fa; text-align: left; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        open_btn.clicked.connect(lambda _=False, url=link["url"]: QDesktopServices.openUrl(QUrl(url)))
        h.addWidget(open_btn, 1)
        del_btn = QPushButton()
        del_btn.setFixedSize(18, 18)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Eliminar enlace")
        del_btn.setIcon(make_glyph_icon("cross", "#ef4444", 12))
        del_btn.setIconSize(QSize(12, 12))
        del_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        del_btn.clicked.connect(lambda _=False, lid=link["id"]: self.remove_link(lid))
        h.addWidget(del_btn)
        return row

    def add_link(self):
        url = self.link_url_input.text().strip()
        if not url:
            return
        label = self.link_label_input.text().strip() or None
        database.add_task_link(self.task_id, url, label, self.db_path)
        self.link_url_input.clear()
        self.link_label_input.clear()
        self.modified = True
        self.reload_links()

    def remove_link(self, link_id):
        database.delete_task_link(link_id, self.db_path)
        self.modified = True
        self.reload_links()

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
            log_widget = LogEntryWidget(log, self.delete_log_entry, self.edit_log_entry, self)
            self.logs_layout.addWidget(log_widget)

        # Pequeño retardo para dar tiempo a Qt a renderizar antes de bajar el scroll
        self.scroll_to_bottom()

    def edit_log_entry(self, log_id, new_html):
        """Guarda la edición de un comentario (o cancela si new_html es None) y recarga."""
        if new_html is not None:
            database.update_log(log_id, new_html, self.db_path)
            self.modified = True
        self.reload_logs()

    def _chat_image_width(self):
        """Ancho máximo (px) para imágenes pegadas en el chat: el del histórico (más
        estrecho que el editor), reservando márgenes y la barra de scroll para que no
        aparezca scroll horizontal ni tape los botones de la entrada."""
        w = self.scroll_area.viewport().width()
        return max(120, w - 44)

    def add_log_entry(self):
        """Crea una nueva entrada de diario con el texto del input."""
        if not self.log_input.toPlainText().strip():
            return  # No añadir logs vacíos

        database.create_log(self.task_id, self.log_input.toHtml(), self.db_path)
        self.log_input.clear()
        self.modified = True

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
            self.modified = True
            widget.deleteLater()

    def scroll_to_bottom(self):
        """Mueve la barra de desplazamiento del diario hasta abajo."""
        # Usamos un timer de un solo disparo o directamente el valor del scrollbar
        # ya que Qt a veces tarda un instante en actualizar el scroll máximo
        scrollbar = self.scroll_area.verticalScrollBar()
        # Conectamos de forma asíncrona sutil para que se ejecute después del repaint
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: scrollbar.setValue(scrollbar.maximum()))
