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


def _card_of(view, task_id):
    from widgets import TaskCard
    return next(c for c in view.findChildren(TaskCard) if c.task_id == task_id)


def test_clicking_a_card_opens_the_detail_after_the_click_event_returns(qapp, board, monkeypatch):
    """Cierre nativo de la app (0xc0000005 en Qt6Widgets.dll, 2026-10-15): el detalle se abría
    con un bucle anidado DENTRO del clic de la tarjeta; si la recarga en vivo destruía la tarjeta
    mientras tanto, al cerrar Qt volvía al evento de un widget ya liberado. Ahora se abre después."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    view = BoardViewWidget(db_path=board["db"])
    view.load_board(board["id"])
    opened = []
    monkeypatch.setattr(view, "open_task_details", lambda task_id: opened.append(task_id))

    QTest.mouseClick(_card_of(view, board["task"]), Qt.LeftButton)
    assert opened == []  # aún dentro del evento de la tarjeta: no se abre nada
    qapp.processEvents()
    assert opened == [board["task"]]
    view.close()


def test_live_reload_while_the_detail_is_open_never_runs_inside_the_cards_event(qapp, board, monkeypatch):
    """Escenario real del cierre: clic en la tarjeta → detalle abierto → un agente cambia el
    tablero → la recarga en vivo destruye la tarjeta → se cierra el detalle. El uso de memoria
    liberada no siempre revienta en headless (comportamiento indefinido), así que se comprueba
    la condición peligrosa en sí: que el detalle no corra con el evento de la tarjeta en la pila."""
    import board_view as bv_module
    import widgets
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    view = BoardViewWidget(db_path=board["db"])
    view.load_board(board["id"])

    in_card_event = []
    original_release = widgets.TaskCard.mouseReleaseEvent

    def tracked_release(card, event):
        in_card_event.append(True)
        try:
            original_release(card, event)
        finally:
            in_card_event.pop()
    monkeypatch.setattr(widgets.TaskCard, "mouseReleaseEvent", tracked_release)

    seen_inside_card_event = []

    class _DetailWhileAgentWorks:
        def __init__(self, task_id, db_path, parent=None):
            self.task_id, self.modified, self.task_deleted = task_id, True, False

        def exec(self):
            seen_inside_card_event.append(bool(in_card_event))
            board["agent"]._tool_move_task({"task_id": self.task_id, "target_column_id": board["cols"][4]})
            view.load_board(board["id"], notify=False)              # recarga en vivo
            qapp.sendPostedEvents(None, QEvent.Type.DeferredDelete)  # destruye la tarjeta ya

    monkeypatch.setattr(bv_module, "TaskDetailDialog", _DetailWhileAgentWorks)
    QTest.mouseClick(_card_of(view, board["task"]), Qt.LeftButton)
    qapp.processEvents()

    assert seen_inside_card_event == [False]
    assert database.get_task(board["task"], board["db"])["column_id"] == board["cols"][4]
    assert _card_of(view, board["task"]) is not None  # el tablero sigue vivo y muestra la tarjeta
    view.close()


def test_detail_header_follows_a_column_move_made_elsewhere(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])
    dlg.title_input.setText("Editando")  # aunque haya cambios sin guardar, la columna se refresca
    board["agent"]._tool_move_task({"task_id": board["task"], "target_column_id": board["cols"][4]})
    dlg._on_mcp_board_mutated(board["id"])
    done_name = database.get_column(board["cols"][4], board["db"])["name"]
    assert done_name.upper() in dlg.kicker_label.text()
    _close(qapp, dlg)


def test_merge_holds_with_the_apps_stylesheet_and_a_shown_dialog(qapp, board):
    """Prueba manual 2 de #103 (2026-10-15): con la hoja de estilos de la app, mostrar el detalle
    cambia la fuente por defecto del editor y con ella el HTML de la descripción; la fusión creía
    que el usuario la había editado y pisaba la del agente (y el refresco en vivo no se aplicaba)."""
    import styles
    qapp.setStyleSheet(styles.build_qss(styles.COLORS))
    try:
        dlg = TaskDetailDialog(board["task"], board["db"])
        dlg.show()
        qapp.processEvents()

        board["agent"]._tool_update_task({"task_id": board["task"], "description": "Del agente, en vivo"})
        dlg._on_mcp_board_mutated(board["id"])
        assert "Del agente, en vivo" in dlg.desc_input.toPlainText()  # sin tocar: se refresca

        dlg.title_input.setText("Título del usuario")
        board["agent"]._tool_update_task({"task_id": board["task"], "description": "Del agente, prueba 2"})
        dlg._on_mcp_board_mutated(board["id"])
        dlg.save_changes()

        task = database.get_task(board["task"], board["db"])
        assert task["title"] == "Título del usuario"
        assert "prueba 2" in task["description"]
        _close(qapp, dlg)
    finally:
        qapp.setStyleSheet("")


def test_a_description_the_user_did_edit_still_wins(qapp, board):
    dlg = TaskDetailDialog(board["task"], board["db"])
    dlg.desc_input.textCursor().insertText(" y lo mío")  # edición del usuario: marca el documento
    board["agent"]._tool_update_task({"task_id": board["task"], "description": "Del agente"})
    dlg.save_changes()
    assert "y lo mío" in database.get_task(board["task"], board["db"])["description"]
    _close(qapp, dlg)
