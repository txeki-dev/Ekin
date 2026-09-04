"""
Utilidades compartidas para procesamiento y saneamiento de HTML en descripciones y diario/chat.
Desacopla dependencias entre MarkdownTextEdit y LogEntryWidget.
"""

import re


def sanitize_chat_html(html: str) -> str:
    """Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no
    se muestren como texto plano en el chat o en las descripciones."""
    if not html:
        return html
    # Eliminar cualquier <!DOCTYPE ...> que incluya o no la URL de W3C
    cleaned = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
    # Limpiar cualquier fragmento de DTD residual o previamente corrupto por el parser
    cleaned = re.sub(r'(?:<a\s+[^>]*?>)?http://www\.w3\.org/TR/REC-html40/strict\.dtd(?:</a>)?["\'>]*', '', cleaned, flags=re.IGNORECASE)
    return cleaned


def fit_html_images(html: str, max_width: int = None) -> str:
    """Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca
    desborden el ancho del contenedor de chat o descripción, y asegura que las imágenes queden
    envueltas en un enlace clicable para abrir la vista previa ampliada."""
    if not html:
        return html
    html = sanitize_chat_html(html)
    if max_width is None:
        max_width = 280
    max_w_int = int(max_width)

    # Ajustar etiquetas <img>
    if "<img" in html.lower():
        def _repl_img(match):
            attrs = match.group(1)
            w_match = re.search(r'\bwidth\s*=\s*["\']?(\d+)["\']?', attrs, re.IGNORECASE)
            if w_match:
                orig_w = int(w_match.group(1))
                target_w = min(orig_w, max_w_int)
            else:
                target_w = max_w_int
            attrs_clean = re.sub(r'\bwidth\s*=\s*["\']?[^"\'>\s]+["\']?', '', attrs, flags=re.IGNORECASE).strip()
            return f'<img width="{target_w}" {attrs_clean}>'

        html = re.sub(r'<img\s+([^>]*?)>', _repl_img, html, flags=re.IGNORECASE)

        # Envolver cualquier <img ...> que no esté dentro de un <a href="..."> con su propio src
        def _wrap_img(match):
            full_match = match.group(0)
            if full_match.lower().startswith("<a"):
                return full_match
            img_tag = match.group(2) if match.group(2) else match.group(0)
            src_m = re.search(r'src=["\']([^"\']+)["\']', img_tag, re.IGNORECASE)
            if src_m:
                return f'<a href="{src_m.group(1)}">{img_tag}</a>'
            return img_tag

        html = re.sub(r'(<a\s+[^>]*?>[\s\S]*?</a>)|(<img\s+[^>]*?>)', _wrap_img, html, flags=re.IGNORECASE)

    # Ajustar etiquetas <table> para evitar tablas con ancho rígido superior
    if "<table" in html.lower():
        def _repl_tbl(match):
            attrs = match.group(1)
            w_match = re.search(r'\bwidth\s*=\s*["\']?(\d+)(px|%)?["\']?', attrs, re.IGNORECASE)
            if w_match:
                unit = w_match.group(2)
                if unit == "%":
                    return match.group(0)
                orig_w = int(w_match.group(1))
                target_w = min(orig_w, max_w_int)
            else:
                target_w = max_w_int
            attrs_clean = re.sub(r'\bwidth\s*=\s*["\']?[^"\'>\s]+["\']?', '', attrs, flags=re.IGNORECASE).strip()
            return f'<table width="{target_w}" {attrs_clean}>'

        html = re.sub(r'<table\s+([^>]*?)>', _repl_tbl, html, flags=re.IGNORECASE)

    return html


def linkify_urls(html_text: str) -> str:
    """Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,
    respetando los enlaces <a>, etiquetas <img> y cualquier otra etiqueta HTML existente."""
    if not html_text:
        return html_text
    html_text = sanitize_chat_html(html_text)
    # Protege cualquier etiqueta HTML (<...>) o enlace existente (<a ...>...</a>) para
    # que ninguna URL dentro de atributos HTML (src, href, etc.) se convierta en link duplicado.
    pattern = re.compile(r'(<a\s+[^>]*?>[\s\S]*?</a>|<[^>]+>)|(https?://[^\s<>"\'`]+)', re.IGNORECASE)

    def _repl(m):
        if m.group(1):
            return m.group(1)
        url = m.group(2)
        trailing = ""
        while url and url[-1] in ".,;:!?)":
            trailing = url[-1] + trailing
            url = url[:-1]
        return f'<a href="{url}">{url}</a>{trailing}'

    return pattern.sub(_repl, html_text)


def apply_word_style_to_qt_table(table, rows: int, cols: int, cell_texts=None, border_color=None, bg_header=None):
    """Aplica formato estilo Microsoft Word a un QTextTable de Qt:
    padding equilibrado, centrado vertical y horizontal, y cabecera diferenciada."""
    from PySide6.QtGui import QTextFrameFormat, QTextCharFormat, QColor, QFont
    from PySide6.QtCore import Qt

    border_color = border_color or "#e2e8f0"
    bg_header = bg_header or "#f8fafc"

    fmt = table.format()
    fmt.setCellPadding(6)
    fmt.setCellSpacing(0)
    fmt.setBorder(1)
    fmt.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
    fmt.setBorderBrush(QColor(border_color))
    fmt.setAlignment(Qt.AlignCenter)
    if rows > 1:
        fmt.setHeaderRowCount(1)
    table.setFormat(fmt)

    for r in range(rows):
        for c in range(cols):
            cell = table.cellAt(r, c)
            cell_fmt = cell.format().toTableCellFormat()
            cell_fmt.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignMiddle)
            cell_fmt.setTopPadding(6)
            cell_fmt.setBottomPadding(6)
            cell_fmt.setLeftPadding(8)
            cell_fmt.setRightPadding(8)
            if r == 0:
                cell_fmt.setBackground(QColor(bg_header))
            cell.setFormat(cell_fmt)

            cur = cell.firstCursorPosition()
            b_fmt = cur.blockFormat()
            b_fmt.setAlignment(Qt.AlignCenter)
            cur.setBlockFormat(b_fmt)

            if r == 0:
                c_fmt = cur.charFormat()
                c_fmt.setFontWeight(QFont.Bold)
                cur.setCharFormat(c_fmt)

            if cell_texts and r < len(cell_texts) and c < len(cell_texts[r]):
                cur.insertText(cell_texts[r][c])

