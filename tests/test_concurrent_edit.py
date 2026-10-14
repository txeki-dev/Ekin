"""#103: edición concurrente de una tarjeta. Mientras el detalle está abierto, un agente (MCP),
otro proceso o la sync .ekboard pueden cambiar la misma tarea; cerrar el detalle no debe
pisar esos cambios, y la recarga en vivo no debe destruir widgets bajo un bucle anidado."""
import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QMenu

import database
import templates
from board_view import BoardViewWidget
from detail_dialog import TaskDetailDialog
from mcp_server import McpProtocolHandler


@pytest.fixture
def board(db_path):
    board_id = templates.create_board_from_template("SW", "#c67139", templates.TEMPLATE_SOFTWARE_AGILE, db_path=db_path)
    cols = [c["id"] for c in database.get_columns(board_id, db_path=db_path)]
    task_id = database.create_task(cols[0], "Tarea", description="<p>original</p>", due_date="2026-10-20", db_path=db_path)
    agent = McpProtocolHandler(database.get_board(board_id, db_path=db_path), db_path=db_path, client_name="Agente").executor
    return {"id": board_id, "cols": cols, "task": task_id, "agent": agent, "db": db_path}


def _close(qapp, dlg):
    dlg.close()
    dlg.deleteLater()
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)


def test_click_outside_keeps_the_agents_changes(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])          # el usuario abre la tarjeta
    board["agent"]._tool_update_task({"task_id": board["task"], "description": "texto del **agente**"})
    board["agent"]._tool_move_task({"task_id": board["task"], "target_column_id": board["cols"][4]})  # Done
    dlg.save_changes()                                           # clic fuera sin haber tocado nada

    task = database.get_task(board["task"], board["db"])
    assert "agente" in task["description"]
    assert task["due_date"] is None  # la fecha que quitó el paso a Done no vuelve
    _close(qapp, dlg)


def test_fields_the_user_edited_win_and_the_rest_keep_the_agents_values(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])
    dlg.title_input.setText("Título del usuario")
    board["agent"]._tool_update_task({"task_id": board["task"], "title": "Título del agente", "description": "Del agente"})
    dlg.save_changes()

    task = database.get_task(board["task"], board["db"])
    assert task["title"] == "Título del usuario"
    assert "Del agente" in task["description"]
    _close(qapp, dlg)


def test_untouched_detail_shows_the_agents_changes_live(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])
    board["agent"]._tool_update_task({"task_id": board["task"], "title": "Nuevo título", "description": "Nueva descripción"})
    dlg._on_mcp_board_mutated(board["id"])

    assert dlg.title_input.text() == "Nuevo título"
    assert "Nueva descripción" in dlg.desc_input.toPlainText()
    assert dlg.due_enable_chk.isChecked()  # la fecha no cambió
    _close(qapp, dlg)


def test_live_refresh_never_overwrites_what_the_user_is_editing(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])
    dlg.title_input.setText("Escribiendo…")
    board["agent"]._tool_update_task({"task_id": board["task"], "title": "Título del agente"})
    dlg._on_mcp_board_mutated(board["id"])

    assert dlg.title_input.text() == "Escribiendo…"
    _close(qapp, dlg)


def test_task_deleted_by_someone_else_closes_the_detail_without_errors(qapp, board, monkeypatch):
    from detail_dialog import task_detail_dialog as tdd
    notices = []
    monkeypatch.setattr(tdd.QMessageBox, "information", staticmethod(lambda *a, **k: notices.append(a[2])))
    dlg = TaskDetailDialog(board["task"], board["db"])
    database.delete_task(board["task"], board["db"])

    dlg._on_mcp_board_mutated(board["id"])
    assert dlg.task_deleted and len(notices) == 1

    dlg.save_changes()  # p. ej. un clic fuera que llega igualmente: no debe lanzar IntegrityError
    assert database.get_task(board["task"], board["db"]) is None
    _close(qapp, dlg)


def test_live_board_reload_waits_while_a_menu_or_modal_dialog_is_open(qapp, board, monkeypatch):
    view = BoardViewWidget(db_path=board["db"])
    view.load_board(board["id"])
    reloads = []
    monkeypatch.setattr(view, "load_board", lambda *a, **k: reloads.append(a))

    menu = QMenu()
    monkeypatch.setattr(QApplication, "activePopupWidget", staticmethod(lambda: menu))
    view._perform_safe_mcp_board_reload()
    assert reloads == [] and view._mcp_reload_debounce_timer.isActive()

    monkeypatch.setattr(QApplication, "activePopupWidget", staticmethod(lambda: None))
    view._perform_safe_mcp_board_reload()
    assert len(reloads) == 1
    view.close()
