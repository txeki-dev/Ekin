"""#99: el Markdown que envían los agentes por MCP se guarda como HTML de Qt para que la app lo
pinte con formato (antes los saltos de línea se perdían y todo salía en un único párrafo)."""
import database
import markdown_html
from html_utils import clean_html_description
from PySide6.QtGui import QTextBlockFormat, QTextDocument

MD = "### Criterios\n\nTexto con **negrita** y `code`.\n\n- [ ] pendiente\n- [x] hecho\n\n1. uno\n2. dos"


def _blocks(fragment):
    doc = QTextDocument()
    doc.setHtml(fragment)
    block, out = doc.begin(), []
    while block.isValid():
        out.append((block.text(), block.blockFormat().headingLevel(), block.blockFormat().marker()))
        block = block.next()
    return out


def test_markdown_becomes_qt_html_with_headings_lists_and_checkboxes():
    fragment = markdown_html.markdown_to_qt_html(MD)
    blocks = _blocks(fragment)
    assert ("Criterios", 3, QTextBlockFormat.MarkerType.NoMarker) in blocks
    assert ("pendiente", 0, QTextBlockFormat.MarkerType.Unchecked) in blocks
    assert ("hecho", 0, QTextBlockFormat.MarkerType.Checked) in blocks
    assert "<ol" in fragment and "font-weight:700" in fragment
    assert "<body" not in fragment and "<style" not in fragment


def test_html_input_is_kept_and_empty_stays_empty():
    html_in = "<p><b>Problema</b>: x</p><ul><li>a</li></ul>"
    assert markdown_html.markdown_to_qt_html(html_in) == html_in
    assert markdown_html.markdown_to_qt_html("") == ""
    assert markdown_html.markdown_to_qt_html(None) == ""


def test_embedded_html_in_markdown_is_shown_as_text():
    fragment = markdown_html.markdown_to_qt_html("### T\n\nHola <script>alert(1)</script> <img src=x>")
    assert "<script" not in fragment and "<img" not in fragment
    assert "&lt;script&gt;" in fragment


def test_author_entry_keeps_the_author_prefix():
    fragment = markdown_html.author_entry_html("Claude Code", "DONE:\n- a\n- b")
    text = clean_html_description(fragment)
    assert text.startswith("[Claude Code]: DONE:")
    assert "• a" in text and "• b" in text


def test_clean_html_description_reads_checkboxes_for_agents():
    text = clean_html_description(markdown_html.markdown_to_qt_html(MD))
    assert "• [ ] pendiente" in text and "• [x] hecho" in text
    assert "Criterios" in text and "<" not in text


def _board_with_task(db_path, description):
    board_id = database.create_board("B", db_path=db_path)
    col = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col, "T", description=description, db_path=db_path)
    return board_id, task_id


def test_migration_converts_plain_text_once(db_path):
    _, task_id = _board_with_task(db_path, "Linea 1\n- a\n- b")
    _, html_task = _board_with_task(db_path, "<p>ya es HTML</p>\n")
    _, single = _board_with_task(db_path, "una sola línea")
    log_id = database.add_task_log(task_id, "[Claude Code]: DONE:\n- uno &amp; dos", db_path=db_path)
    version = database.get_task(task_id, db_path)["version"]

    assert markdown_html.migrate_plain_text_content(db_path) == 2

    task = database.get_task(task_id, db_path)
    assert "<li" in task["description"] and task["version"] == version + 1
    assert database.get_task(html_task, db_path)["description"] == "<p>ya es HTML</p>\n"
    assert database.get_task(single, db_path)["description"] == "una sola línea"
    log = next(entry for entry in database.get_task_logs(task_id, db_path=db_path) if entry["id"] == log_id)
    assert clean_html_description(log["content"]).startswith("[Claude Code]: DONE:")
    assert "• uno & dos" in clean_html_description(log["content"])

    database.update_task(task_id, "T", "otra\nvez", db_path=db_path)
    assert markdown_html.migrate_plain_text_content(db_path) == 0


def test_migration_skips_journal_of_synced_boards(db_path):
    board_id, task_id = _board_with_task(db_path, "")
    database.add_task_log(task_id, "[Agente]: a\nb", db_path=db_path)
    database.set_board_sync_path(board_id, "C:/compartido/b.ekboard", db_path=db_path)

    assert markdown_html.migrate_plain_text_content(db_path) == 0
