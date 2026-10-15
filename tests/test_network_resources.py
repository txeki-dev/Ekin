"""#113: el HTML de las tarjetas (de un .ekboard compartido, una importación o un agente) puede
apuntar imágenes y fondos a una ruta de red; Qt los resuelve solo con abrir la tarjeta."""
import pytest

from detail_dialog.html_utils import strip_network_resources
from detail_dialog.log_entry import LogEntryWidget
from detail_dialog.markdown_edit import MarkdownTextEdit

HOST = "example.invalid"


@pytest.mark.parametrize("html", [
    f'<img src="\\\\{HOST}\\share\\a.png">',
    f"<img src='//{HOST}/share/a.png'>",
    f'<img src=file://{HOST}/share/a.png>',
    f'<img src="&#92;&#92;{HOST}&#92;share&#92;a.png">',
    f'<table background="\\\\{HOST}\\s\\b.png"><tr><td>x</td></tr></table>',
    f'<p style="background-image: url(\'file://{HOST}/s/b.png\')">x</p>',
])
def test_network_locations_are_neutralised(html):
    assert HOST not in strip_network_resources(html)


def test_local_and_embedded_images_and_the_rest_are_kept():
    html = ('<p><b>Hola</b> <a href="https://example.com/x">enlace</a></p>'
            '<img src="data:image/png;base64,AAAA"><img src="file:///C:/Users/me/a.png">')
    assert strip_network_resources(html) == html


def test_editors_and_journal_entries_render_without_network_resources(qapp):
    html = f'<p>Nota</p><img src="\\\\{HOST}\\share\\a.png">'

    editor = MarkdownTextEdit()
    editor.setHtml(html)
    assert HOST not in editor.toHtml() and "Nota" in editor.toPlainText()

    entry = LogEntryWidget({"id": 1, "content": html, "created_at": "2026-10-15 12:00:00"},
                           delete_callback=lambda: None, save_edit_callback=lambda *_: None)
    assert HOST not in entry.content_label.text() and "Nota" in entry.content_label.text()
    entry.deleteLater()
    editor.deleteLater()


@pytest.mark.parametrize("ext", [".chm", ".scf", ".appref-ms", ".settingcontent-ms", ".library-ms", ".search-ms",
                                 ".xll", ".iso", ".img", ".vhd", ".vhdx", ".diagcab", ".ps1xml", ".psc1", ".vb",
                                 ".ws", ".msix", ".msixbundle", ".appx", ".appxbundle"])
def test_links_to_windows_types_that_run_or_mount_content_ask_first(qapp, monkeypatch, ext):
    """#116: estos tipos ejecutan código o montan contenido al abrirse y no pedían confirmación."""
    from detail_dialog import security_utils
    asked = []
    monkeypatch.setattr(security_utils.QMessageBox, "warning",
                        lambda *a, **k: asked.append(a[2]) or security_utils.QMessageBox.StandardButton.Cancel)
    assert security_utils.confirm_open_untrusted_link(None, f"C:/Users/me/Downloads/file{ext}") is False
    assert len(asked) == 1 and ext in asked[0]
