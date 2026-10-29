"""#85: un tablero puede asociarse a un directorio local (repo): el agente de IA conoce su CWD
por MCP y la mención «@» ofrece los archivos del repo. Es un dato de esta máquina: nunca se
sincroniza, exporta ni copia."""
import json
import os
import subprocess

import pytest
from PySide6.QtCore import QEvent, QModelIndex, Qt

import board_sync
import database
import exporter
import prompt_packs
import sidebar
import templates
from detail_dialog import TaskDetailDialog
from detail_dialog.repo_files import list_repo_files
from mcp_server import McpProtocolHandler


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "venv" / "lib").mkdir(parents=True)
    (root / "src" / "app.py").write_text("print()")
    (root / "README.md").write_text("# r")
    (root / "debug.log").write_text("x")
    (root / "venv" / "lib" / "dep.py").write_text("x")
    (root / ".gitignore").write_text("*.log\nvenv/\n")
    return root


def _board_with_task(db_path, local_dir=None):
    board_id = database.create_board("Repo", db_path=db_path)
    col = database.create_column(board_id, "Backlog", db_path=db_path)
    task_id = database.create_task(col, "T", db_path=db_path)
    database.set_board_local_dir(board_id, local_dir, db_path=db_path)
    return board_id, task_id


def test_local_dir_is_persisted_and_cleared(db_path, tmp_path):
    board_id, _ = _board_with_task(db_path, str(tmp_path))
    board = database.get_board(board_id, db_path=db_path)
    assert board["local_dir"] == str(tmp_path)
    assert database.get_board_by_uuid(board["board_uuid"], db_path=db_path)["local_dir"] == str(tmp_path)
    assert next(b for b in database.get_boards(db_path) if b["id"] == board_id)["local_dir"] == str(tmp_path)

    database.set_board_local_dir(board_id, "", db_path=db_path)
    assert database.get_board(board_id, db_path=db_path)["local_dir"] is None


def test_local_dir_never_leaves_the_machine(db_path, tmp_path):
    secret = str(tmp_path / "C-Users-private-repo")
    board_id, _ = _board_with_task(db_path, secret)

    assert secret not in json.dumps(board_sync.export_board_to_sync_dict(board_id, db_path))
    assert secret not in exporter.boards_to_json(db_path, board_id=board_id)
    tmpl = templates.export_board_to_template(board_id, "t", "T", "d", db_path=db_path)
    assert secret not in json.dumps(tmpl.to_dict(), default=str)
    copy_id = database.copy_board(board_id, "Copia", "#000000", db_path=db_path)
    assert database.get_board(copy_id, db_path=db_path)["local_dir"] is None


def test_list_repo_files_respects_gitignore(repo):
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    files = list_repo_files(str(repo))
    assert set(files) == {".gitignore", "README.md", "src/app.py"}


def test_list_repo_files_without_git_skips_dependency_folders(repo):
    files = list_repo_files(str(repo))
    assert "src/app.py" in files and "README.md" in files
    assert not any(f.startswith("venv/") for f in files)
    assert list_repo_files(str(repo), limit=2) == files[:2]


def test_mcp_and_prompt_variables_expose_the_local_dir(db_path, tmp_path):
    board_id, _ = _board_with_task(db_path, str(tmp_path))
    database.set_board_mcp_config(board_id, enabled=True, db_path=db_path)
    board = database.get_board_by_uuid(database.get_board(board_id, db_path=db_path)["board_uuid"], db_path=db_path)
    handler = McpProtocolHandler(board, db_path=db_path)

    assert handler.executor._tool_get_board_info({})["local_directory"] == str(tmp_path)
    assert str(tmp_path) in handler._build_instructions()
    assert prompt_packs.board_variables(board)["repo_path"] == str(tmp_path)
    assert "repo_path" not in prompt_packs.board_variables({"name": "Sin repo"})


def _cleanup(qapp, dlg):
    dlg.close()
    dlg.deleteLater()
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)


def test_at_mentions_offer_repo_files_and_attach_the_picked_one(qapp, db_path, repo):
    board_id, task_id = _board_with_task(db_path, str(repo))
    readme = os.path.normpath(str(repo / "README.md"))
    database.add_task_link(task_id, readme, "README", db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    items = dlg.desc_input.mention_provider()
    assert [i["label"] for i in items if i.get("source") != "repo"] == ["README"]
    repo_labels = {i["label"] for i in items if i.get("source") == "repo"}
    assert "src/app.py" in repo_labels and "README.md" not in repo_labels  # ya adjunto

    from PySide6.QtTest import QTest
    editor = dlg.desc_input
    dlg.setAttribute(Qt.WA_DontShowOnScreen, True)
    dlg.show()
    qapp.processEvents()
    editor.setFocus()
    QTest.keyClicks(editor, "Ver @app")
    completer = editor._mention_completer
    assert completer.currentCompletion() == "src/app.py"
    completer.activated[QModelIndex].emit(completer.currentIndex())

    assert "📄 src/app.py" in editor.toPlainText()
    links = {lnk["url"]: lnk["label"] for lnk in database.get_task_links(task_id, db_path)}
    assert links[os.path.normpath(str(repo / "src" / "app.py"))] == "src/app.py"
    _cleanup(qapp, dlg)


def test_at_mentions_without_local_dir_only_offer_task_links(qapp, db_path):
    _, task_id = _board_with_task(db_path)
    database.add_task_link(task_id, "https://x.dev", "X", db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    assert [i["label"] for i in dlg.desc_input.mention_provider()] == ["X"]
    _cleanup(qapp, dlg)


def test_board_edit_dialog_local_dir_row(qapp, monkeypatch, tmp_path):
    dlg = sidebar.BoardEditDialog("Editar", name="B", local_dir=None, with_local_dir=True)
    assert not dlg.local_dir_clear_btn.isEnabled()

    monkeypatch.setattr(sidebar.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: str(tmp_path).replace("\\", "/")))
    dlg._browse_local_dir()
    assert dlg.local_dir == os.path.normpath(str(tmp_path))
    assert dlg.local_dir_input.text() == dlg.local_dir and dlg.local_dir_clear_btn.isEnabled()

    dlg.local_dir_clear_btn.click()
    assert dlg.local_dir is None and dlg.local_dir_input.text() == ""
    assert dlg.get_data() == ("B", "#3b82f6")

    copy_dlg = sidebar.BoardEditDialog("Copiar", name="B")
    assert not hasattr(copy_dlg, "local_dir_input")


def test_edit_board_persists_the_local_dir(qapp, db_path, monkeypatch, tmp_path):
    board_id = database.create_board("B", db_path=db_path)
    bar = sidebar.SidebarWidget(db_path=db_path)
    bar.reload_boards(select_board_id=board_id)

    def fake_exec(dialog):
        dialog._set_local_dir(str(tmp_path))
        return sidebar.QDialog.Accepted
    monkeypatch.setattr(sidebar.BoardEditDialog, "exec", fake_exec)
    bar.edit_board()

    assert database.get_board(board_id, db_path=db_path)["local_dir"] == str(tmp_path)
    bar.close()


def test_local_folder_wording_is_not_only_a_repo():
    """#146: los tableros socráticos y GTD también enlazan una carpeta de apuntes; la interfaz ya no
    la llama «(repo)» y pone el repo solo como ejemplo."""
    import strings
    keys = ("sidebar.board_edit.local_dir_label", "settings.local_dirs_hint", "board_view.work_link_tooltip",
            "landing.slide2_b2")
    for table in (strings.STRINGS_EN, strings.STRINGS_ES):
        for key in keys:
            assert "(repo)" not in table[key] and "repo files" not in table[key], key
    assert "notes folder" in strings.STRINGS_EN["settings.local_dirs_hint"]
    assert "carpeta de apuntes" in strings.STRINGS_ES["settings.local_dirs_hint"]
