"""#86: en los tableros con directorio local, Ekin muestra en Markdown los diarios de
desarrollo (diary.md, diary_archive.md) que escriben los agentes de IA.
#142: y también el resto de archivos .md / .txt del repo (raíz en pestañas, subcarpetas en «Más…»)."""
import subprocess

import database
from board_view import BoardViewWidget
from diary_viewer_dialog import DiaryViewerDialog, doc_files


def _board(db_path, local_dir=None):
    board_id = database.create_board("Repo", db_path=db_path)
    database.create_column(board_id, "Backlog", db_path=db_path)
    database.set_board_local_dir(board_id, local_dir, db_path=db_path)
    return board_id


def _write(root, rel_path, text="x"):
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_doc_files_lists_root_docs_diaries_first_and_subfolder_docs(tmp_path):
    assert doc_files(None) == ([], []) and doc_files(str(tmp_path / "no_existe")) == ([], [])
    # Los diarios suelen estar en .gitignore: no se puede listar con `git ls-files --exclude-standard`
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=False)
    _write(tmp_path, ".gitignore", "diary.md\ndiary_archive.md\n")
    for rel in ("README.md", "notes.txt", "diary_archive.md", "diary.md", "main.py",
                "docs/guide.md", ".agents/docs/plan.md",
                "venv/lib/readme.md", "node_modules/pkg/README.md", "pkg.egg-info/SOURCES.txt"):
        _write(tmp_path, rel)

    root, sub = doc_files(str(tmp_path))
    assert root == ["diary.md", "diary_archive.md", "notes.txt", "README.md"]
    assert sub == [".agents/docs/plan.md", "docs/guide.md"]


def test_viewer_renders_markdown_and_reloads(qapp, db_path, tmp_path):
    _write(tmp_path, "diary.md", "# Developer Diary\n\n- **hecho**: algo")
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)

    assert dlg.tabs.count() == 1 and dlg.tabs.tabText(0) == "diary.md"
    text = dlg.browsers[0].toPlainText()
    assert "Developer Diary" in text and "#" not in text and "**" not in text

    _write(tmp_path, "diary.md", "# Otro título")
    dlg.reload_btn.click()
    assert "Otro título" in dlg.browsers[0].toPlainText()
    dlg.close()


def test_viewer_shows_text_files_as_plain_text(qapp, db_path, tmp_path):
    _write(tmp_path, "notes.txt", "# no es un título\n**tal cual**")
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)

    assert dlg.tabs.tabText(0) == "notes.txt"
    assert dlg.browsers[0].toPlainText() == "# no es un título\n**tal cual**"
    dlg.close()


def test_more_menu_opens_subfolder_docs_as_tabs_once(qapp, db_path, tmp_path):
    _write(tmp_path, "README.md", "# Léeme")
    _write(tmp_path, "docs/guide.md", "# Guía")
    _write(tmp_path, ".agents/docs/plan.md", "# Plan")
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)

    assert not dlg.more_btn.isHidden()
    folders = {action.text(): action.menu() for action in dlg.more_btn.menu().actions()}
    assert list(folders) == [".agents", "docs"]
    guide = next(a for a in folders["docs"].actions() if a.text() == "guide.md")

    guide.trigger()
    assert dlg.tabs.count() == 2 and dlg.tabs.tabText(1) == "docs/guide.md"
    assert dlg.tabs.currentIndex() == 1 and "Guía" in dlg.browsers[1].toPlainText()

    dlg.tabs.setCurrentIndex(0)
    guide.trigger()
    assert dlg.tabs.count() == 2 and dlg.tabs.currentIndex() == 1
    dlg.close()


def test_more_button_hidden_without_subfolder_docs(qapp, db_path, tmp_path):
    _write(tmp_path, "README.md")
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)
    assert dlg.more_btn.isHidden()
    dlg.close()


def test_reload_keeps_the_scroll_and_adds_new_root_docs(qapp, db_path, tmp_path):
    _write(tmp_path, "diary.md", "\n\n".join(f"Línea {i}" for i in range(300)))
    dlg = DiaryViewerDialog(_board(db_path, str(tmp_path)), db_path=db_path)
    dlg.show()
    qapp.processEvents()
    bar = dlg.browsers[0].verticalScrollBar()
    bar.setValue(bar.maximum() // 2)
    scroll = bar.value()
    assert scroll > 0

    _write(tmp_path, "CHANGELOG.md", "# Cambios")
    dlg.reload_btn.click()
    assert bar.value() == scroll
    assert [dlg.tabs.tabText(i) for i in range(dlg.tabs.count())] == ["diary.md", "CHANGELOG.md"]
    dlg.close()


def test_diary_button_for_boards_with_any_doc(qapp, db_path, tmp_path):
    view = BoardViewWidget(db_path=db_path)
    without_dir = _board(db_path)
    with_dir = _board(db_path, str(tmp_path))

    view.load_board(without_dir)
    assert view.diary_btn.isHidden()
    _write(tmp_path, "main.py")
    view.load_board(with_dir)
    assert view.diary_btn.isHidden()  # directorio sin .md ni .txt

    _write(tmp_path, "README.md", "# R")
    view.load_board(with_dir)
    assert not view.diary_btn.isHidden()
    view.close()
