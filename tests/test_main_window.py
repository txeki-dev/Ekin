"""Pruebas headless para MainWindow (main.py): comportamientos que solo existen a
ese nivel (no en BoardViewWidget aislado). Requieren QT_QPA_PLATFORM=offscreen (ya
configurado igual que en CI) porque MainWindow construye bandeja del sistema, atajos
y demás -- ya probado en los smoke scripts manuales de este mismo proyecto."""
from PySide6.QtCore import QEvent

import database
import main as main_module


def _make_task_on_board(db_path, board_name="B"):
    board_id = database.create_board(board_name, db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    return board_id, task_id


def _make_window(monkeypatch):
    """Construye una MainWindow apta para tests: __init__ agenda dos
    QTimer.singleShot sueltos (sin padre) para notify_due_today/check_for_updates --
    el segundo dispara subprocess.run(["git", ...]) reales. Sin parche, quedan
    pendientes hasta el teardown de sesión de `qapp` y disparan ahí contra un
    objeto potencialmente ya destruido (causa confirmada de los cuelgues
    intermitentes de STATUS_HEAP_CORRUPTION en CI) además de hacer E/S de red real
    en mitad de un test. Parcheados a no-op en la CLASE antes de instanciar, para
    que la búsqueda de atributo que hace QTimer.singleShot(..., self.<method>) en
    __init__ ya resuelva a la versión parcheada."""
    monkeypatch.setattr(main_module.MainWindow, "notify_due_today", lambda self: None)
    monkeypatch.setattr(main_module.MainWindow, "check_for_updates", lambda self: None)
    return main_module.MainWindow()


def _close_window(qapp, window):
    """Cierra y destruye la ventana de verdad (deleteLater + procesar el evento
    DeferredDelete) en vez de dejarla viva indefinidamente -- evita acumular
    ventanas zombi (con todos sus widgets/timers hijos) hasta el teardown de sesión."""
    window.close()
    window.deleteLater()
    qapp.sendPostedEvents(window, QEvent.Type.DeferredDelete)


def test_on_calendar_task_reloads_board_view_when_editing_the_active_board(qapp, db_path, monkeypatch):
    """Regresión: editar una tarea desde el Calendario dejaba la tarjeta del tablero
    desactualizada porque on_calendar_task nunca recargaba board_view."""
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path)

    window = _make_window(monkeypatch)
    window.sidebar.select_board(board_id)

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: True)
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == [((board_id,), {"notify": False})]
    _close_window(qapp, window)


def test_on_calendar_task_does_not_reload_board_view_for_a_different_board(qapp, db_path, monkeypatch):
    """La tarea editada pertenece a un tablero distinto del que la sidebar tiene
    activo: no debe recargarse board_view (desincronizaría qué tablero muestra
    cargado respecto al que la sidebar resalta)."""
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path, "B1")
    other_board_id, _ = _make_task_on_board(db_path, "B2")

    window = _make_window(monkeypatch)
    window.sidebar.select_board(other_board_id)  # el tablero activo es OTRO distinto

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: True)
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == []
    _close_window(qapp, window)


def test_on_calendar_task_does_nothing_when_dialog_reports_no_changes(qapp, db_path, monkeypatch):
    monkeypatch.setattr(database, "DB_NAME", db_path)
    board_id, task_id = _make_task_on_board(db_path)

    window = _make_window(monkeypatch)
    window.sidebar.select_board(board_id)

    monkeypatch.setattr(window, "_open_task_detail", lambda tid: False)  # sin cambios
    calls = []
    monkeypatch.setattr(window.board_view, "load_board", lambda *a, **k: calls.append((a, k)))

    window.on_calendar_task(task_id, board_id)

    assert calls == []
    _close_window(qapp, window)


def test_main_window_title(qapp, db_path, monkeypatch):
    """Verifica que el título de la ventana principal es 'Ekin vX.X.X'."""
    from version import __version__
    monkeypatch.setattr(database, "DB_NAME", db_path)
    window = _make_window(monkeypatch)
    assert window.windowTitle() == f"Ekin v{__version__}"
    _close_window(qapp, window)
