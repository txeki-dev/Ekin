"""Pruebas headless para MainWindow (main.py): comportamientos que solo existen a
ese nivel (no en BoardViewWidget aislado). Requieren QT_QPA_PLATFORM=offscreen (ya
configurado igual que en CI) porque MainWindow construye bandeja del sistema, atajos
y demás -- ya probado en los smoke scripts manuales de este mismo proyecto."""
import database
import main as main_module


def _make_task_on_board(db_path, board_name="B"):
    board_id = database.create_board(board_name, db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    return board_id, task_id


def test_on_calendar_task_reloads_board_view_when_editing_the_active_board(qapp, db_path, monkeypatch):
    """Regresión: editar una tarea desde el Calendario dejaba la tarjeta del tablero
    desactualizada porque on_calendar_task nunca recargaba board_view."""
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path)

    window = main_module.MainWindow()
    window.sidebar.select_board(board_id)

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: True)
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == [((board_id,), {"notify": False})]


def test_on_calendar_task_does_not_reload_board_view_for_a_different_board(qapp, db_path, monkeypatch):
    """La tarea editada pertenece a un tablero distinto del que la sidebar tiene
    activo: no debe recargarse board_view (desincronizaría qué tablero muestra
    cargado respecto al que la sidebar resalta)."""
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path, "B1")
    other_board_id, _ = _make_task_on_board(db_path, "B2")

    window = main_module.MainWindow()
    window.sidebar.select_board(other_board_id)  # el tablero activo es OTRO distinto

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: True)
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == []


def test_on_calendar_task_does_nothing_when_dialog_reports_no_changes(qapp, db_path, monkeypatch):
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path)

    window = main_module.MainWindow()
    window.sidebar.select_board(board_id)

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: False)  # sin cambios
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == []
