"""
Utilidades compartidas para procesamiento y saneamiento de HTML en descripciones y diario/chat.
Desacopla dependencias entre MarkdownTextEdit y LogEntryWidget.
"""

import re


def fit_html_images(html: str, max_width: int = None) -> str:
    """Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca
    desborden el ancho del contenedor de chat o descripción, y asegura que las imágenes queden
    envueltas en un enlace clicable para abrir la vista previa ampliada."""
    if not html:
        return html
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
    respetando los enlaces <a> o etiquetas <img> que ya existan."""
    if not html_text:
        return html_text
    pattern = re.compile(r'(<a\s+[^>]*?>[\s\S]*?</a>|<img\s+[^>]*?>)|(https?://[^\s<>"\'`]+)')
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
