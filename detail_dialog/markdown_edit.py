from PySide6.QtCore import Qt, QBuffer, QIODevice
from PySide6.QtWidgets import QTextEdit, QPushButton, QWidget, QHBoxLayout, QInputDialog
from PySide6.QtGui import (
    QFont, QTextCharFormat, QTextListFormat, QTextCursor, QImage,
    QTextTableFormat, QTextFrameFormat, QColor
)
import re
import styles
from strings import t


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
        # --- Tachado: Ctrl+Shift+X ---
        if ctrl and bool(event.modifiers() & Qt.ShiftModifier) and event.key() == Qt.Key_X:
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(not self.currentCharFormat().fontStrikeOut())
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
        """Al pegar: las imágenes se insertan como imagen; una tabla (de Excel/Sheets/Word o
        un origen HTML con `<table>`) se inserta como tabla real; el resto del texto,
        SIEMPRE sin formato.

        Así el contenido copiado de webs/Word se pega como texto plano (sin fuentes ni
        colores ajenos), pero se pueden pegar capturas/imágenes y tablas del portapapeles."""
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage) and not image.isNull():
                self._insert_image(image)
                return
        if source.hasHtml() and "<table" in source.html().lower():
            # Se conserva el HTML de la tabla tal cual: Qt reconstruye una QTextTable real
            # (con celdas combinadas, etc.) y así se preserva su aspecto de origen.
            self.textCursor().insertHtml(source.html())
            return
        if source.hasText():
            grid = self._grid_from_plain_text(source.text())
            if grid is not None:
                self.insert_table(len(grid), max(len(row) for row in grid), cell_texts=grid)
                return
            self.insertPlainText(source.text())
            return
        super().insertFromMimeData(source)

    @staticmethod
    def _grid_from_plain_text(text):
        """Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,
        p. ej. copiado de una hoja de cálculo sin HTML en el portapapeles), lo devuelve
        como una cuadrícula de filas de texto. Si no, devuelve None."""
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        while lines and lines[-1] == "":
            lines.pop()
        if len(lines) < 2 or not any("\t" in ln for ln in lines):
            return None
        return [ln.split("\t") for ln in lines]

    def insert_table(self, rows, cols, cell_texts=None):
        """Inserta una tabla `rows`x`cols` en la posición del cursor, con el estilo del
        tema activo. Si se pasa `cell_texts` (lista de filas de texto), rellena cada
        celda con su contenido; si no, la deja vacía (usado por el botón «Insertar tabla»)."""
        fmt = QTextTableFormat()
        fmt.setCellPadding(4)
        fmt.setCellSpacing(0)
        fmt.setBorder(1)
        fmt.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        fmt.setBorderBrush(QColor(styles.COLORS["border"]))
        table = self.textCursor().insertTable(rows, cols, fmt)
        if cell_texts:
            for r, row in enumerate(cell_texts):
                for c, text in enumerate(row):
                    if r < rows and c < cols:
                        table.cellAt(r, c).firstCursorPosition().insertText(text)

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
    """Barra de formato básica (negrita, cursiva, tachado, viñetas, tablas) para un QTextEdit."""
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.bold_btn = QPushButton("B")
        self.bold_btn.setObjectName("FormatButton")
        self.bold_btn.setToolTip(t("markdown_edit.bold_tooltip"))
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
        self.italic_btn.setToolTip(t("markdown_edit.italic_tooltip"))
        self.italic_btn.setCheckable(True)
        self.italic_btn.setCursor(Qt.PointingHandCursor)
        self.italic_btn.setFixedSize(28, 26)
        italic_font = QFont()
        italic_font.setItalic(True)
        self.italic_btn.setFont(italic_font)
        self.italic_btn.clicked.connect(self.toggle_italic)
        layout.addWidget(self.italic_btn)

        self.strike_btn = QPushButton("S")
        self.strike_btn.setObjectName("FormatButton")
        self.strike_btn.setToolTip(t("markdown_edit.strike_tooltip"))
        self.strike_btn.setCheckable(True)
        self.strike_btn.setCursor(Qt.PointingHandCursor)
        self.strike_btn.setFixedSize(28, 26)
        strike_font = QFont()
        strike_font.setStrikeOut(True)
        self.strike_btn.setFont(strike_font)
        self.strike_btn.clicked.connect(self.toggle_strikethrough)
        layout.addWidget(self.strike_btn)

        self.bullet_btn = QPushButton("•")
        self.bullet_btn.setObjectName("FormatButton")
        self.bullet_btn.setToolTip(t("markdown_edit.bullet_tooltip"))
        self.bullet_btn.setCursor(Qt.PointingHandCursor)
        self.bullet_btn.setFixedSize(28, 26)
        self.bullet_btn.clicked.connect(self.toggle_bullets)
        layout.addWidget(self.bullet_btn)

        self.table_btn = QPushButton("▦")
        self.table_btn.setObjectName("FormatButton")
        self.table_btn.setToolTip(t("markdown_edit.table_tooltip"))
        self.table_btn.setCursor(Qt.PointingHandCursor)
        self.table_btn.setFixedSize(28, 26)
        self.table_btn.clicked.connect(self.insert_table_dialog)
        layout.addWidget(self.table_btn)

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

    def toggle_strikethrough(self):
        fmt = QTextCharFormat()
        fmt.setFontStrikeOut(self.strike_btn.isChecked())
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_bullets(self):
        cursor = self.text_edit.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)
        cursor.createList(list_format)
        self.text_edit.setFocus()

    def insert_table_dialog(self):
        """Pide filas y columnas y crea una tabla vacía en la posición del cursor."""
        rows, ok = QInputDialog.getInt(
            self, t("markdown_edit.table_dialog_title"), t("markdown_edit.table_rows_label"), 3, 1, 20
        )
        if not ok:
            return
        cols, ok = QInputDialog.getInt(
            self, t("markdown_edit.table_dialog_title"), t("markdown_edit.table_cols_label"), 3, 1, 20
        )
        if not ok:
            return
        self.text_edit.insert_table(rows, cols)
        self.text_edit.setFocus()

    def sync_buttons(self, *args):
        fmt = self.text_edit.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.strike_btn.setChecked(fmt.fontStrikeOut())
