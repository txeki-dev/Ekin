"""
Conversión a HTML de Qt del Markdown / texto plano que envían los agentes por MCP.

La app pinta descripciones y entradas del diario como HTML (`setHtml`, `QLabel` rich text), así
que el Markdown guardado tal cual perdía los saltos de línea y salía en un único párrafo.
"""
import re

from PySide6.QtGui import Qt, QTextDocument

import database

_MIGRATION_FLAG = "md_content_migrated"
_BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL)
_AUTHOR_PREFIX_RE = re.compile(r"^\[([^\]\n]+)\]:")
_FEATURES = QTextDocument.MarkdownFeature(
    QTextDocument.MarkdownFeature.MarkdownDialectGitHub.value
    | QTextDocument.MarkdownFeature.MarkdownNoHTML.value  # el HTML embebido sale como texto
)


def markdown_to_qt_html(text):
    """Fragmento HTML de Qt para `text`. Lo que ya es HTML (empieza por una etiqueta) se devuelve
    tal cual; el resto se interpreta como Markdown de GitHub sin HTML embebido. Basta
    `mightBeRichText` no: da por HTML cualquier texto con una etiqueta en la primera línea, que
    así se saltaba el filtro y perdía el Markdown (#112)."""
    if not text or not text.strip() or (text.lstrip().startswith("<") and Qt.mightBeRichText(text)):
        return text or ""
    doc = QTextDocument()
    doc.setMarkdown(text, _FEATURES)
    return _BODY_RE.search(doc.toHtml()).group(1).strip()


def author_entry_html(author, text):
    """Entrada del diario «[autor]: texto» con el texto en Markdown. Los corchetes se escapan:
    sin eso CommonMark lee «[autor]: …» como una definición de enlace y la entrada desaparece."""
    return markdown_to_qt_html(f"\\[{author}\\]: {text}")


def migrate_plain_text_content(db_path=None):
    """Migración única: pasa a HTML las descripciones y entradas del diario guardadas como
    Markdown / texto plano con saltos de línea (antes de #99). Las descripciones suben `version`
    para que la sync .ekboard las exporte; las entradas de tableros sincronizados no se tocan
    (la sync fusiona el diario por contenido exacto y las duplicaría). Devuelve cuántas cambió."""
    if database.get_setting(_MIGRATION_FLAG, db_path=db_path) == "1":
        return 0
    changed = 0
    with database.get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, description AS text FROM tasks WHERE description LIKE '%' || char(10) || '%'"
        ).fetchall()
        for row in rows:
            if not Qt.mightBeRichText(row["text"]):
                conn.execute(
                    "UPDATE tasks SET description = ?, version = version + 1 WHERE id = ?",
                    (markdown_to_qt_html(row["text"]), row["id"]),
                )
                changed += 1

        rows = conn.execute(
            """SELECT l.id, l.content AS text FROM task_logs l
               JOIN tasks t ON t.id = l.task_id
               JOIN columns c ON c.id = t.column_id
               JOIN boards b ON b.id = c.board_id
               WHERE b.sync_path IS NULL AND l.content LIKE '%' || char(10) || '%'"""
        ).fetchall()
        for row in rows:
            if not Qt.mightBeRichText(row["text"]):
                text = _AUTHOR_PREFIX_RE.sub(r"\\[\1\\]:", row["text"])
                conn.execute("UPDATE task_logs SET content = ? WHERE id = ?", (markdown_to_qt_html(text), row["id"]))
                changed += 1
    database.set_setting(_MIGRATION_FLAG, "1", db_path=db_path)
    return changed
