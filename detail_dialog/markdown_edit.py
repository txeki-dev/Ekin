from PySide6.QtCore import Qt, QBuffer, QIODevice, QUrl, QPointF, QSize
from PySide6.QtWidgets import (
    QTextEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout,
    QInputDialog, QDialog, QLabel, QComboBox, QPlainTextEdit,
    QColorDialog, QMenu, QLineEdit
)
from PySide6.QtGui import (
    QFont, QTextCharFormat, QTextListFormat, QTextCursor, QImage,
    QTextTableFormat, QColor, QDesktopServices,
    QPixmap, QPainter, QPen, QIcon
)
import html
import re
import styles
from strings import t
from widgets import FlowLayout
from .image_preview_dialog import show_image_preview


def format_code_block_html(code: str, language: str = "python") -> str:
    """Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual
    con fondo oscuro y tipografía monospace, compatible con el motor HTML de Qt."""
    code_clean = code.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    lang_name = (language or "").strip()
    lexer = None
    if lang_name and lang_name.lower() not in ("text", "plain", "texto plano", "ninguno"):
        try:
            import pygments
            from pygments.lexers import get_lexer_by_name
            lexer = get_lexer_by_name(lang_name.lower())
        except Exception:
            lexer = None

    if lexer is not None:
        try:
            import pygments
            from pygments.formatters import HtmlFormatter
            formatter = HtmlFormatter(nowrap=True, noclasses=True, style="monokai")
            highlighted = pygments.highlight(code_clean, lexer, formatter).strip()
        except Exception:
            highlighted = html.escape(code_clean)
    else:
        highlighted = html.escape(code_clean)

    bg = "#1e1e2e"
    border = "#3b4252"
    lang_display = html.escape(lang_name.upper()) if (lang_name and lang_name.lower() not in ("text", "plain", "texto plano", "ninguno")) else "CÓDIGO"
    header_html = (
        f'<table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 4px;">'
        f'<tr>'
        f'<td align="left" style="color: #94a3b8; font-size: 10px; font-weight: bold; font-family: sans-serif; text-transform: uppercase;">{lang_display}</td>'
        f'<td align="right"><a href="action:delete_code_block" style="color: #ef4444; font-size: 11px; font-weight: bold; text-decoration: none;" title="{t("markdown_edit.delete_code_tooltip")}">✕ {t("markdown_edit.delete_code_btn")}</a></td>'
        f'</tr></table>'
    )

    return (
        f'<table width="100%" cellpadding="8" cellspacing="0" '
        f'style="background-color: {bg}; border: 1px solid {border}; border-radius: 4px; margin: 6px 0px;">'
        f'<tr><td>{header_html}'
        f'<pre style="margin: 0; font-family: Consolas, \'Courier New\', monospace; font-size: 11px; line-height: 1.4; color: #f8f8f2; white-space: pre-wrap;">'
        f'{highlighted}</pre></td></tr></table>'
    )


def _color_icon(color_hex, size=12):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(color_hex))
    painter.setPen(QColor(styles.COLORS["border"]))
    painter.drawRoundedRect(0, 0, size - 1, size - 1, 2, 2)
    painter.end()
    return pix


def _align_icon(kind, color, size=14):
    """Dibuja un icono vectorial nítido para alineación de texto (left, center, right, justify)."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color), 1.6)
    pen.setCapStyle(Qt.RoundCap)
    p.setPen(pen)

    y_coords = [2.5, 6.0, 9.5, 13.0]
    s = float(size)
    for i, y in enumerate(y_coords):
        if kind == "left":
            x2 = s - 2.0 if i % 2 == 0 else s - 5.5
            p.drawLine(QPointF(2.0, y), QPointF(x2, y))
        elif kind == "center":
            if i % 2 == 0:
                p.drawLine(QPointF(2.0, y), QPointF(s - 2.0, y))
            else:
                p.drawLine(QPointF(4.0, y), QPointF(s - 4.0, y))
        elif kind == "right":
            x1 = 2.0 if i % 2 == 0 else 5.5
            p.drawLine(QPointF(x1, y), QPointF(s - 2.0, y))
        elif kind == "justify":
            p.drawLine(QPointF(2.0, y), QPointF(s - 2.0, y))
    p.end()
    return QIcon(pix)


class CodeBlockDialog(QDialog):
    """Diálogo modal para insertar un bloque de código formateado."""
    LANGUAGES = [
        ("Python", "python"),
        ("JavaScript", "javascript"),
        ("TypeScript", "typescript"),
        ("HTML", "html"),
        ("CSS", "css"),
        ("SQL", "sql"),
        ("Bash / Shell", "bash"),
        ("JSON", "json"),
        ("C / C++", "cpp"),
        ("C#", "csharp"),
        ("Rust", "rust"),
        ("Go", "go"),
        ("Java", "java"),
        ("PHP", "php"),
        ("YAML", "yaml"),
        ("Markdown", "markdown"),
        ("Texto plano", "text"),
    ]

    def __init__(self, initial_code="", initial_lang="python", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("markdown_edit.code_dialog_title"))
        self.setMinimumSize(480, 360)
        self.resize(520, 400)
        if isinstance(initial_code, bool) or initial_code is None:
            initial_code = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(t("markdown_edit.code_lang_label")))
        self.lang_combo = QComboBox()
        for label, val in self.LANGUAGES:
            self.lang_combo.addItem(label, val)

        idx = -1
        for i, (_, val) in enumerate(self.LANGUAGES):
            if val.lower() == (initial_lang or "").lower():
                idx = i
                break
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_layout.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_layout)

        layout.addWidget(QLabel(t("markdown_edit.code_text_label")))
        self.code_edit = QPlainTextEdit()
        font = self.font()
        font.setFamily("Consolas")
        self.code_edit.setFont(font)
        self.code_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px;")
        self.code_edit.setPlainText(str(initial_code))
        self.code_edit.setPlaceholderText("def main():\n    print('Hello World')")
        layout.addWidget(self.code_edit, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.insert_btn = QPushButton(t("markdown_edit.code_insert_btn"))
        self.insert_btn.setObjectName("PrimaryButton")
        self.insert_btn.setCursor(Qt.PointingHandCursor)
        self.insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.insert_btn)

        cancel_btn = QPushButton(t("markdown_edit.code_cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_data(self):
        return self.code_edit.toPlainText(), self.lang_combo.currentData()


class LinkDialog(QDialog):
    """Diálogo modal para insertar un enlace (URL)."""
    def __init__(self, initial_url="", initial_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("markdown_edit.link_dialog_title"))
        self.setMinimumWidth(380)
        if isinstance(initial_url, bool) or initial_url is None:
            initial_url = ""
        if isinstance(initial_text, bool) or initial_text is None:
            initial_text = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel(t("markdown_edit.link_url_label")))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://ejemplo.com")
        self.url_input.setText(initial_url)
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel(t("markdown_edit.link_text_label")))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ej. Mi enlace")
        self.text_input.setText(initial_text)
        layout.addWidget(self.text_input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.insert_btn = QPushButton(t("markdown_edit.link_insert_btn"))
        self.insert_btn.setObjectName("PrimaryButton")
        self.insert_btn.setCursor(Qt.PointingHandCursor)
        self.insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.insert_btn)

        cancel_btn = QPushButton(t("markdown_edit.link_cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_data(self):
        url = self.url_input.text().strip()
        label = self.text_input.text().strip()
        if url and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
            url = f"https://{url}"
        return url, label or url


class MarkdownTextEdit(QTextEdit):
    """QTextEdit con atajos tipo Markdown para crear listas al vuelo.

    - `* `, `- `, `+ ` al inicio de una línea -> lista con viñetas (bullet).
    - `1. `, `1) ` al inicio de una línea -> lista numerada.
    - Enter sobre una viñeta vacía -> sale de la lista (comportamiento habitual).
    """

    # Marcadores que disparan cada tipo de lista al pulsar espacio
    _BULLET_MARKERS = ("*", "-", "+")
    _ORDERED_RE = re.compile(r"\d+[.)]")
    # Ancho máximo (px) de la copia de mayor resolución guardada para la vista ampliada
    # (detail_dialog/image_preview_dialog.py) -- ver _insert_image.
    _PREVIEW_MAX_WIDTH = 1920

    def __init__(self, parent=None):
        super().__init__(parent)
        # Si se define, devuelve el ancho máximo (px) para imágenes pegadas. Sirve para
        # que las imágenes del chat quepan en el histórico (más estrecho que el editor).
        self.image_width_provider = None
        # Necesario para que mouseMoveEvent reciba eventos sin botón pulsado (cursor de
        # mano al pasar sobre una imagen pegada).
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self._press_pos = None

    def mousePressEvent(self, event):
        self._press_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Un clic (no un arrastre de selección) sobre una imagen pegada la abre en
        grande; sobre '✕ Borrar' elimina el bloque de código; sobre un enlace web lo abre en el navegador."""
        pos = event.position().toPoint()
        if event.button() == Qt.LeftButton and self._press_pos is not None:
            moved = (pos - self._press_pos).manhattanLength()
            if moved < 4:
                anchor = self.anchorAt(pos)
                if anchor == "action:delete_code_block" or anchor.startswith("action:delete_code_block"):
                    self._delete_code_block_at(self._press_pos, anchor)
                    return
                elif anchor.startswith("data:image/"):
                    show_image_preview(anchor, self)
                    return
                elif anchor.startswith(("http://", "https://", "mailto:", "file:", "ftp://")):
                    QDesktopServices.openUrl(QUrl(anchor))
                    return
        super().mouseReleaseEvent(event)

    def _delete_code_block_at(self, pos, anchor="action:delete_code_block"):
        """Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra el cursor."""
        cursor = self.cursorForPosition(pos)
        table = cursor.currentTable()
        if not table:
            doc = self.document()
            block = doc.begin()
            found_pos = -1
            min_dist = float("inf")
            click_pos = cursor.position()
            while block.isValid():
                it = block.begin()
                while not it.atEnd():
                    frag = it.fragment()
                    if frag.isValid() and frag.charFormat().anchorHref().startswith("action:delete_code_block"):
                        dist = abs(frag.position() - click_pos)
                        if dist < min_dist:
                            min_dist = dist
                            found_pos = frag.position()
                    it += 1
                block = block.next()
            if found_pos >= 0:
                c = QTextCursor(doc)
                c.setPosition(found_pos)
                table = c.currentTable()

        if table:
            from PySide6.QtGui import QTextTable
            parent_frame = table.parentFrame()
            outer_table = parent_frame if isinstance(parent_frame, QTextTable) else table
            first_pos = outer_table.firstCursorPosition().position()
            last_pos = outer_table.lastCursorPosition().position()
            del_cursor = self.textCursor()
            del_cursor.beginEditBlock()
            del_cursor.setPosition(max(0, first_pos - 1))
            del_cursor.setPosition(min(self.document().characterCount() - 1, last_pos + 1), QTextCursor.KeepAnchor)
            del_cursor.removeSelectedText()
            del_cursor.endEditBlock()
            self.setTextCursor(del_cursor)

    def align_left(self):
        """Alinea el bloque de texto actual o selección a la izquierda."""
        self.setAlignment(Qt.AlignLeft)
        self.setFocus()

    def align_center(self):
        """Centra el bloque de texto actual o selección."""
        self.setAlignment(Qt.AlignHCenter)
        self.setFocus()

    def align_right(self):
        """Alinea el bloque de texto actual o selección a la derecha."""
        self.setAlignment(Qt.AlignRight)
        self.setFocus()

    def align_justify(self):
        """Justifica el bloque de texto actual o selección."""
        self.setAlignment(Qt.AlignJustify)
        self.setFocus()

    def to_uppercase(self):
        """Convierte el texto seleccionado (o la palabra bajo el cursor) a MAYÚSCULAS."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            selected = cursor.selectedText()
            fmt = cursor.charFormat()
            new_text = selected.upper()
            start_pos = cursor.selectionStart()
            cursor.beginEditBlock()
            cursor.insertText(new_text, fmt)
            cursor.endEditBlock()
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(new_text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.setFocus()

    def to_lowercase(self):
        """Convierte el texto seleccionado (o la palabra bajo el cursor) a minúsculas."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            selected = cursor.selectedText()
            fmt = cursor.charFormat()
            new_text = selected.lower()
            start_pos = cursor.selectionStart()
            cursor.beginEditBlock()
            cursor.insertText(new_text, fmt)
            cursor.endEditBlock()
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(new_text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.setFocus()

    def toggle_case(self):
        """Alterna el caso de la selección o palabra: MAYÚSCULAS <-> minúsculas (Shift+F3)."""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        if cursor.hasSelection():
            selected = cursor.selectedText()
            fmt = cursor.charFormat()
            if selected.isupper():
                new_text = selected.lower()
            else:
                new_text = selected.upper()
            start_pos = cursor.selectionStart()
            cursor.beginEditBlock()
            cursor.insertText(new_text, fmt)
            cursor.endEditBlock()
            cursor.setPosition(start_pos)
            cursor.setPosition(start_pos + len(new_text), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.setFocus()

    def contextMenuEvent(self, event):
        """Menú contextual estándar ampliado con opciones de mayúsculas/minúsculas y borrar código."""
        menu = self.createStandardContextMenu()
        styles.style_menu(menu)
        cursor = self.cursorForPosition(event.pos())
        table = cursor.currentTable()
        if table:
            menu.addSeparator()
            act_del = menu.addAction(f"🗑️ {t('markdown_edit.delete_code_btn_menu')}")
            act_del.triggered.connect(lambda: self._delete_code_block_at(event.pos()))

        text_cur = self.textCursor()
        if text_cur.hasSelection():
            menu.addSeparator()
            act_upper = menu.addAction(t("markdown_edit.context_upper"))
            act_upper.triggered.connect(self.to_uppercase)
            act_lower = menu.addAction(t("markdown_edit.context_lower"))
            act_lower.triggered.connect(self.to_lowercase)

        menu.exec(event.globalPos())

    def mouseMoveEvent(self, event):
        anchor = self.anchorAt(event.position().toPoint())
        self.viewport().setCursor(
            Qt.CursorShape.PointingHandCursor if anchor
            else Qt.CursorShape.IBeamCursor
        )
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        ctrl = bool(event.modifiers() & Qt.ControlModifier)
        shift = bool(event.modifiers() & Qt.ShiftModifier)

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
        if ctrl and shift and event.key() == Qt.Key_X:
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(not self.currentCharFormat().fontStrikeOut())
            self.mergeCurrentCharFormat(fmt)
            event.accept()
            return

        # --- Alineaciones de texto: Ctrl+L (izq), Ctrl+E (centro), Ctrl+R (der), Ctrl+J (justificado) ---
        if ctrl and not shift and event.key() == Qt.Key_L:
            self.align_left()
            event.accept()
            return
        if ctrl and not shift and event.key() == Qt.Key_E:
            self.align_center()
            event.accept()
            return
        if ctrl and not shift and event.key() == Qt.Key_R:
            self.align_right()
            event.accept()
            return
        if ctrl and not shift and event.key() == Qt.Key_J:
            self.align_justify()
            event.accept()
            return

        # --- MAYÚSCULAS / minúsculas: Ctrl+Shift+U, Ctrl+Shift+L, Shift+F3 ---
        if ctrl and shift and event.key() == Qt.Key_U:
            self.to_uppercase()
            event.accept()
            return
        if ctrl and shift and event.key() == Qt.Key_L:
            self.to_lowercase()
            event.accept()
            return
        if shift and not ctrl and event.key() == Qt.Key_F3:
            self.toggle_case()
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

        # --- Línea separadora al escribir el tercer guion en una línea vacía ---
        if event.text() in ("-", "_", "*") and not cursor.hasSelection():
            text_before = cursor.block().text()[:cursor.positionInBlock()]
            if text_before == event.text() * 2 and not cursor.block().text()[cursor.positionInBlock():].strip():
                cursor.beginEditBlock()
                cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertHtml("<hr>")
                cursor.endEditBlock()
                self.setTextCursor(cursor)
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

        # --- Enter sobre "---" / "___" / "***" / "—-" -> línea separadora ---
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not cursor.hasSelection():
            raw_line = cursor.block().text().strip()
            if raw_line in ("---", "___", "***", "—-", "–––"):
                cursor.beginEditBlock()
                cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                cursor.insertHtml("<hr>")
                cursor.endEditBlock()
                self.setTextCursor(cursor)
                event.accept()
                return
            # Enter sobre "```" o "```python" abre el diálogo de código
            if raw_line.startswith("```"):
                lang = raw_line[3:].strip()
                cursor.beginEditBlock()
                cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()
                cursor.endEditBlock()
                self.setTextCursor(cursor)
                self.open_code_dialog(initial_lang=lang)
                event.accept()
                return

        # --- Enter sobre una viñeta vacía: salir de la lista ---
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not cursor.hasSelection():
            block = cursor.block()
            if block.textList() is not None and not block.text().strip():
                self._exit_list()
                event.accept()
                return

        # --- "-->" al escribir: se convierte en una flecha "→" ---
        if event.text() == ">" and not cursor.hasSelection():
            text_before = cursor.block().text()[:cursor.positionInBlock()]
            if text_before.endswith("--"):
                cursor.beginEditBlock()
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, 2)
                cursor.removeSelectedText()
                cursor.insertText("→")
                cursor.endEditBlock()
                self.setTextCursor(cursor)
                event.accept()
                return

        # --- Borrar tabla/bloque de código con Backspace si celda está vacía o al inicio ---
        if event.key() == Qt.Key_Backspace and not cursor.hasSelection():
            table = cursor.currentTable()
            if table:
                cell = table.cellAt(cursor)
                if cell.isValid():
                    first_pos_in_cell = cell.firstCursorPosition().position()
                    if cursor.position() == first_pos_in_cell or not cell.firstCursorPosition().block().text().strip():
                        parent_frame = table.parentFrame()
                        from PySide6.QtGui import QTextTable
                        outer_table = parent_frame if isinstance(parent_frame, QTextTable) else table
                        first_pos = outer_table.firstCursorPosition().position()
                        last_pos = outer_table.lastCursorPosition().position()
                        del_cursor = self.textCursor()
                        del_cursor.beginEditBlock()
                        del_cursor.setPosition(max(0, first_pos - 1))
                        del_cursor.setPosition(min(self.document().characterCount() - 1, last_pos + 1), QTextCursor.KeepAnchor)
                        del_cursor.removeSelectedText()
                        del_cursor.endEditBlock()
                        self.setTextCursor(del_cursor)
                        event.accept()
                        return

        super().keyPressEvent(event)

    def insertFromMimeData(self, source):
        """Al pegar: las imágenes se insertan como imagen; las tablas como tablas reales;
        los enlaces se preservan como hipervínculos clicables; el resto sin formato."""
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage) and not image.isNull():
                self._insert_image(image)
                return
        if source.hasHtml():
            html_content = source.html()
            if "<img" in html_content.lower() or "<table" in html_content.lower():
                from .html_utils import fit_html_images
                target_w = self.image_width_provider() if self.image_width_provider else max(100, self.viewport().width() - 24)
                fitted = fit_html_images(html_content, target_w)
                self.textCursor().insertHtml(fitted)
                return
        if source.hasText():
            raw_text = source.text()
            grid = self._grid_from_plain_text(raw_text)
            if grid is not None:
                self.insert_table(len(grid), max(len(row) for row in grid), cell_texts=grid)
                return
            # Si el texto pegado es una sola URL web
            url_match = re.match(r'^https?://\S+$', raw_text.strip(), re.IGNORECASE)
            if url_match:
                url = raw_text.strip()
                cursor = self.textCursor()
                if cursor.hasSelection():
                    selected = cursor.selectedText()
                    cursor.insertHtml(f'<a href="{url}">{html.escape(selected)}</a>')
                else:
                    cursor.insertHtml(f'<a href="{url}">{html.escape(url)}</a>')
                return
            # Si el texto contiene enlaces web en medio del texto
            from .html_utils import linkify_urls
            if re.search(r'https?://[^\s<>"\'`]+', raw_text):
                escaped = html.escape(raw_text).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br/>")
                linkified = linkify_urls(escaped)
                self.textCursor().insertHtml(linkified)
                return
            self.insertPlainText(raw_text)
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
        """Inserta una tabla `rows`x`cols` en la posición del cursor con diseño estilo Microsoft Word:
        bordes estilizados, cabecera resaltada, celdas con padding generoso y texto centrado."""
        from .html_utils import apply_word_style_to_qt_table
        fmt = QTextTableFormat()
        table = self.textCursor().insertTable(rows, cols, fmt)
        apply_word_style_to_qt_table(
            table,
            rows,
            cols,
            cell_texts=cell_texts,
            border_color=styles.COLORS["border"],
            bg_header=styles.COLORS["bg_card"],
        )

    @staticmethod
    def _image_to_data_uri(image):
        """Codifica un QImage como data URI PNG en base64."""
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        b64 = bytes(buffer.data().toBase64()).decode("ascii")
        buffer.close()
        return f"data:image/png;base64,{b64}"

    def _insert_image(self, image):
        """Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se
        guardan DOS copias: una ajustada al ancho útil (el del histórico del chat si se ha
        configurado un `image_width_provider`, más estrecho que el editor) para mostrarla
        inline, y otra de mayor resolución (hasta _PREVIEW_MAX_WIDTH) para la vista
        ampliada -- así ImagePreviewDialog escala hacia ABAJO desde una fuente con detalle
        real al pulsar la imagen, en vez de estirar (y emborronar) la miniatura ya reducida."""
        preview_image = image
        if preview_image.width() > self._PREVIEW_MAX_WIDTH:
            preview_image = preview_image.scaledToWidth(self._PREVIEW_MAX_WIDTH, Qt.SmoothTransformation)
        preview_uri = self._image_to_data_uri(preview_image)

        if self.image_width_provider:
            avail = max(100, self.image_width_provider())
        else:
            avail = max(100, self.viewport().width() - 24)
        if image.width() > avail:
            image = image.scaledToWidth(avail, Qt.SmoothTransformation)
        inline_uri = self._image_to_data_uri(image)

        # <a href> con la copia de alta resolución, <img src> con la miniatura inline: no
        # cambia el aspecto (Qt no añade subrayado/borde a una imagen-enlace) pero la hace
        # clicable vía anchorAt() en los QTextEdit editables y linkActivated en el QLabel
        # del diario ya enviado -- y ahora abre con detalle real en vez de emborronarse.
        self.textCursor().insertHtml(f'<a href="{preview_uri}"><img src="{inline_uri}" /></a>')

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

    def insert_horizontal_rule(self):
        """Inserta una línea separadora horizontal en la posición del cursor."""
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.insertHtml("<hr>")
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.setFocus()

    def open_code_dialog(self, initial_code=None, initial_lang="python"):
        """Abre el diálogo para insertar un bloque de código formateado."""
        if isinstance(initial_code, bool) or initial_code is None:
            initial_code = ""
        cursor = self.textCursor()
        if not initial_code and cursor.hasSelection():
            initial_code = cursor.selectedText()
        dlg = CodeBlockDialog(initial_code, initial_lang, parent=self.window())
        if dlg.exec() == QDialog.Accepted:
            code, lang = dlg.get_data()
            if code.strip():
                self.insert_code_block(code, lang)
        self.setFocus()

    def insert_code_block(self, code, language="python"):
        """Inserta un bloque de código formateado con resaltado de sintaxis."""
        block_html = format_code_block_html(code, language)
        cursor = self.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        cursor.insertHtml(block_html)
        cursor.endEditBlock()
        self.setTextCursor(cursor)
        self.setFocus()

    def open_link_dialog(self, *args):
        """Abre el diálogo para insertar o editar un enlace web."""
        cursor = self.textCursor()
        initial_text = cursor.selectedText() if cursor.hasSelection() else ""
        initial_url = ""
        anchor = cursor.charFormat().anchorHref()
        if anchor:
            initial_url = anchor
        elif initial_text.startswith(("http://", "https://")):
            initial_url = initial_text

        dlg = LinkDialog(initial_url, initial_text, parent=self.window())
        if dlg.exec() == QDialog.Accepted:
            url, label = dlg.get_data()
            if url:
                cursor.beginEditBlock()
                cursor.insertHtml(f'<a href="{url}">{html.escape(label)}</a>')
                cursor.endEditBlock()
                self.setTextCursor(cursor)
        self.setFocus()


class RichTextToolbar(QWidget):
    """Barra de formato (negrita, cursiva, tachado, color, alineaciones, mayúsculas/minúsculas,
    viñetas, línea separadora, tablas, código, enlaces)."""
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self._current_text_color = styles.COLORS["text_main"]

        layout = FlowLayout(self, margin=0, spacing=2)

        self.bold_btn = QPushButton("B")
        self.bold_btn.setObjectName("FormatButton")
        self.bold_btn.setToolTip(t("markdown_edit.bold_tooltip"))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setCursor(Qt.PointingHandCursor)
        self.bold_btn.setFixedSize(26, 24)
        bold_font = self.bold_btn.font()
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
        self.italic_btn.setFixedSize(26, 24)
        italic_font = self.italic_btn.font()
        italic_font.setItalic(True)
        self.italic_btn.setFont(italic_font)
        self.italic_btn.clicked.connect(self.toggle_italic)
        layout.addWidget(self.italic_btn)

        self.strike_btn = QPushButton("S")
        self.strike_btn.setObjectName("FormatButton")
        self.strike_btn.setToolTip(t("markdown_edit.strike_tooltip"))
        self.strike_btn.setCheckable(True)
        self.strike_btn.setCursor(Qt.PointingHandCursor)
        self.strike_btn.setFixedSize(26, 24)
        strike_font = self.strike_btn.font()
        strike_font.setStrikeOut(True)
        self.strike_btn.setFont(strike_font)
        self.strike_btn.clicked.connect(self.toggle_strikethrough)
        layout.addWidget(self.strike_btn)

        self.color_btn = QPushButton("A")
        self.color_btn.setObjectName("FormatButton")
        self.color_btn.setToolTip(t("markdown_edit.color_tooltip"))
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.setFixedSize(26, 24)
        color_font = self.color_btn.font()
        color_font.setBold(True)
        self.color_btn.setFont(color_font)
        self.color_btn.clicked.connect(self.show_color_menu)
        self._update_color_btn_indicator()
        layout.addWidget(self.color_btn)

        # Botones de alineación de texto
        icon_c = styles.COLORS["text_main"]
        self.align_left_btn = QPushButton()
        self.align_left_btn.setObjectName("FormatButton")
        self.align_left_btn.setToolTip(t("markdown_edit.align_left_tooltip"))
        self.align_left_btn.setCheckable(True)
        self.align_left_btn.setCursor(Qt.PointingHandCursor)
        self.align_left_btn.setFixedSize(26, 24)
        self.align_left_btn.setIcon(_align_icon("left", icon_c))
        self.align_left_btn.setIconSize(QSize(14, 14))
        self.align_left_btn.clicked.connect(self.text_edit.align_left)
        layout.addWidget(self.align_left_btn)

        self.align_center_btn = QPushButton()
        self.align_center_btn.setObjectName("FormatButton")
        self.align_center_btn.setToolTip(t("markdown_edit.align_center_tooltip"))
        self.align_center_btn.setCheckable(True)
        self.align_center_btn.setCursor(Qt.PointingHandCursor)
        self.align_center_btn.setFixedSize(26, 24)
        self.align_center_btn.setIcon(_align_icon("center", icon_c))
        self.align_center_btn.setIconSize(QSize(14, 14))
        self.align_center_btn.clicked.connect(self.text_edit.align_center)
        layout.addWidget(self.align_center_btn)

        self.align_right_btn = QPushButton()
        self.align_right_btn.setObjectName("FormatButton")
        self.align_right_btn.setToolTip(t("markdown_edit.align_right_tooltip"))
        self.align_right_btn.setCheckable(True)
        self.align_right_btn.setCursor(Qt.PointingHandCursor)
        self.align_right_btn.setFixedSize(26, 24)
        self.align_right_btn.setIcon(_align_icon("right", icon_c))
        self.align_right_btn.setIconSize(QSize(14, 14))
        self.align_right_btn.clicked.connect(self.text_edit.align_right)
        layout.addWidget(self.align_right_btn)

        self.align_justify_btn = QPushButton()
        self.align_justify_btn.setObjectName("FormatButton")
        self.align_justify_btn.setToolTip(t("markdown_edit.align_justify_tooltip"))
        self.align_justify_btn.setCheckable(True)
        self.align_justify_btn.setCursor(Qt.PointingHandCursor)
        self.align_justify_btn.setFixedSize(26, 24)
        self.align_justify_btn.setIcon(_align_icon("justify", icon_c))
        self.align_justify_btn.setIconSize(QSize(14, 14))
        self.align_justify_btn.clicked.connect(self.text_edit.align_justify)
        layout.addWidget(self.align_justify_btn)

        # Botones de MAYÚSCULAS / minúsculas
        self.upper_btn = QPushButton("AA")
        self.upper_btn.setObjectName("FormatButton")
        self.upper_btn.setToolTip(t("markdown_edit.upper_tooltip"))
        self.upper_btn.setCursor(Qt.PointingHandCursor)
        self.upper_btn.setFixedSize(26, 24)
        f_up = self.upper_btn.font()
        f_up.setBold(True)
        f_up.setPointSize(9)
        self.upper_btn.setFont(f_up)
        self.upper_btn.clicked.connect(self.text_edit.to_uppercase)
        layout.addWidget(self.upper_btn)

        self.lower_btn = QPushButton("aa")
        self.lower_btn.setObjectName("FormatButton")
        self.lower_btn.setToolTip(t("markdown_edit.lower_tooltip"))
        self.lower_btn.setCursor(Qt.PointingHandCursor)
        self.lower_btn.setFixedSize(26, 24)
        f_low = self.lower_btn.font()
        f_low.setBold(True)
        f_low.setPointSize(9)
        self.lower_btn.setFont(f_low)
        self.lower_btn.clicked.connect(self.text_edit.to_lowercase)
        layout.addWidget(self.lower_btn)

        self.bullet_btn = QPushButton("•")
        self.bullet_btn.setObjectName("FormatButton")
        self.bullet_btn.setToolTip(t("markdown_edit.bullet_tooltip"))
        self.bullet_btn.setCursor(Qt.PointingHandCursor)
        self.bullet_btn.setFixedSize(26, 24)
        self.bullet_btn.clicked.connect(self.toggle_bullets)
        layout.addWidget(self.bullet_btn)

        self.hr_btn = QPushButton("―")
        self.hr_btn.setObjectName("FormatButton")
        self.hr_btn.setToolTip(t("markdown_edit.hr_tooltip"))
        self.hr_btn.setCursor(Qt.PointingHandCursor)
        self.hr_btn.setFixedSize(26, 24)
        self.hr_btn.clicked.connect(lambda: self.text_edit.insert_horizontal_rule())
        layout.addWidget(self.hr_btn)

        self.table_btn = QPushButton("▦")
        self.table_btn.setObjectName("FormatButton")
        self.table_btn.setToolTip(t("markdown_edit.table_tooltip"))
        self.table_btn.setCursor(Qt.PointingHandCursor)
        self.table_btn.setFixedSize(26, 24)
        self.table_btn.clicked.connect(self.insert_table_dialog)
        layout.addWidget(self.table_btn)

        self.code_btn = QPushButton("</>")
        self.code_btn.setObjectName("FormatButton")
        self.code_btn.setToolTip(t("markdown_edit.code_tooltip"))
        self.code_btn.setCursor(Qt.PointingHandCursor)
        self.code_btn.setFixedSize(26, 24)
        code_font = self.code_btn.font()
        code_font.setFamily("Consolas")
        code_font.setBold(True)
        self.code_btn.setFont(code_font)
        self.code_btn.clicked.connect(lambda: self.text_edit.open_code_dialog())
        layout.addWidget(self.code_btn)

        self.link_btn = QPushButton("🔗")
        self.link_btn.setObjectName("FormatButton")
        self.link_btn.setToolTip(t("markdown_edit.link_tooltip"))
        self.link_btn.setCursor(Qt.PointingHandCursor)
        self.link_btn.setFixedSize(26, 24)
        self.link_btn.clicked.connect(lambda: self.text_edit.open_link_dialog())
        layout.addWidget(self.link_btn)

        self.arrow_btn = QPushButton("→")
        self.arrow_btn.setObjectName("FormatButton")
        self.arrow_btn.setToolTip(t("markdown_edit.arrow_tooltip"))
        self.arrow_btn.setCursor(Qt.PointingHandCursor)
        self.arrow_btn.setFixedSize(26, 24)
        self.arrow_btn.clicked.connect(self.insert_arrow)
        layout.addWidget(self.arrow_btn)

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

    def insert_arrow(self):
        cursor = self.text_edit.textCursor()
        cursor.insertText("→")
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

    def show_color_menu(self):
        """Despliega un menú emergente con una paleta de colores y opción personalizada."""
        menu = QMenu(self)
        styles.style_menu(menu)

        act_default = menu.addAction(t("markdown_edit.color_default"))
        act_default.setIcon(_color_icon(styles.COLORS["text_main"]))
        act_default.triggered.connect(lambda: self.apply_text_color(styles.COLORS["text_main"]))

        menu.addSeparator()

        palette = [
            ("Rojo", "#ef4444"),
            ("Naranja", "#f97316"),
            ("Amarillo", "#eab308"),
            ("Verde", "#10b981"),
            ("Cian", "#06b6d4"),
            ("Azul", "#3b82f6"),
            ("Morado", "#8b5cf6"),
            ("Rosa", "#ec4899"),
            ("Gris", "#94a3b8"),
        ]
        for name, hex_code in palette:
            act = menu.addAction(name)
            act.setIcon(_color_icon(hex_code))
            act.triggered.connect(lambda _, h=hex_code: self.apply_text_color(h))

        menu.addSeparator()
        act_more = menu.addAction(t("markdown_edit.color_more"))
        act_more.triggered.connect(self.choose_custom_color)

        menu.exec(self.color_btn.mapToGlobal(self.color_btn.rect().bottomLeft()))

    def apply_text_color(self, hex_code):
        """Aplica el color seleccionado al texto seleccionado o al texto que se escriba."""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(hex_code))
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()
        self._current_text_color = hex_code
        self._update_color_btn_indicator(hex_code)

    def choose_custom_color(self):
        initial = QColor(getattr(self, "_current_text_color", styles.COLORS["accent_blue"]))
        color = QColorDialog.getColor(initial, self, t("markdown_edit.color_dialog_title"))
        if color.isValid():
            self.apply_text_color(color.name())

    def _update_color_btn_indicator(self, color_hex=None):
        c = color_hex or getattr(self, "_current_text_color", styles.COLORS["text_main"])
        self.color_btn.setStyleSheet(f"border-bottom: 2.5px solid {c}; padding-bottom: 1px;")

    def sync_buttons(self, *args):
        fmt = self.text_edit.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())
        self.strike_btn.setChecked(fmt.fontStrikeOut())
        fg = fmt.foreground().color()
        if fg.isValid() and fg.name() != "#000000":
            self._update_color_btn_indicator(fg.name())
        else:
            self._update_color_btn_indicator(styles.COLORS["text_main"])

        align = self.text_edit.alignment()
        is_center = bool(align & Qt.AlignHCenter)
        is_right = bool(align & Qt.AlignRight)
        is_justify = bool(align & Qt.AlignJustify)
        is_left = bool(align & Qt.AlignLeft) or (not is_center and not is_right and not is_justify)

        self.align_left_btn.setChecked(is_left)
        self.align_center_btn.setChecked(is_center)
        self.align_right_btn.setChecked(is_right)
        self.align_justify_btn.setChecked(is_justify)

