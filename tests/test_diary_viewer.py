"""#86: en los tableros con directorio local, Ekin muestra en Markdown los diarios de
desarrollo (diary.md, diary_archive.md) que escriben los agentes de IA."""
import database
from board_view import BoardViewWidget
from diary_viewer_dialog import DiaryViewerDialog, diary_files


def _board(db_path, local_dir=None):
    board_id = database.create_board("Repo", db_path=db_path)
    database.create_column(board_id, "Backlog", db_path=db_path)
    database.set_board_local_dir(board_id, local_dir, db_path=db_path)
    return board_id


def test_diary_files_lists_only_existing_diaries(tmp_path):
    assert diary_files(None) == [] and diary_files(str(tmp_path)) == []
    (tmp_path / "diary_archive.md").write_text("# Archivo", encoding="utf-8")
    assert diary_files(str(tmp_path)) == [str(tmp_path / "diary_archive.md")]
    (tmp_path / "diary.md").write_text("# Diario", encoding="utf-8")
    assert [p.rsplit("\\", 1)[-1].rsplit("/", 1)[-1] for p in diary_files(str(tmp_path))] == ["diary.md", "diary_archive.md"]


def test_viewer_renders_markdown_and_reloads(qapp, db_path, tmp_path):
    (tmp_path / "diary.md").write_text("# Developer Diary\n\n- **hecho**: algo", encoding="utf-8")
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)

    assert dlg.tabs.count() == 1 and dlg.tabs.tabText(0) == "diary.md"
    text = dlg.browsers[0].toPlainText()
    assert "Developer Diary" in text and "#" not in text and "**" not in text

    (tmp_path / "diary.md").write_text("# Otro título", encoding="utf-8")
    dlg.reload_btn.click()
    assert "Otro título" in dlg.browsers[0].toPlainText()
    dlg.close()


def test_diary_button_only_for_boards_with_diaries(qapp, db_path, tmp_path):
    view = BoardViewWidget(db_path=db_path)
    without_dir = _board(db_path)
    with_dir = _board(db_path, str(tmp_path))

    view.load_board(without_dir)
    assert view.diary_btn.isHidden()
    view.load_board(with_dir)
    assert view.diary_btn.isHidden()  # directorio sin diarios

    (tmp_path / "diary.md").write_text("# D", encoding="utf-8")
    view.load_board(with_dir)
    assert not view.diary_btn.isHidden()
    view.close()
