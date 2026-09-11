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


def test_check_for_updates_ignores_untracked_files(qapp, db_path, monkeypatch):
    """Verifica que archivos no rastreados (como .db-wal, .db-shm o temporales)
    no bloquean la comprobación de actualizaciones."""
    orig_check = main_module.MainWindow.check_for_updates
    monkeypatch.setattr(database, "DB_NAME", db_path)
    window = _make_window(monkeypatch)

    commands = []

    def fake_run(cmd, **kwargs):
        commands.append(cmd)
        args = cmd[1:]
        if args == ["rev-parse", "--is-inside-work-tree"]:
            return type("Result", (), {"returncode": 0, "stdout": "true", "stderr": ""})()
        if args == ["fetch", "origin"]:
            return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args == ["status", "-uno"]:
            return type("Result", (), {"returncode": 0, "stdout": "Your branch is behind 'origin/main' by 1 commit.", "stderr": ""})()
        if args == ["status", "--porcelain", "-uno"]:
            return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(main_module.subprocess, "run", fake_run)
    asked = []

    def fake_question(*args, **kwargs):
        asked.append(True)
        return main_module.QMessageBox.No

    monkeypatch.setattr(main_module.QMessageBox, "question", fake_question)
    info_shown = []
    monkeypatch.setattr(
        main_module.QMessageBox,
        "information",
        lambda *args, **kwargs: info_shown.append(args),
    )

    orig_check(window)

    assert ["git", "status", "--porcelain", "-uno"] in commands
    assert asked == [True]
    assert info_shown == []
    _close_window(qapp, window)


def test_check_for_updates_aborts_when_tracked_files_dirty(qapp, db_path, monkeypatch):
    """Verifica que modificaciones en archivos rastreados sí detienen la actualización y avisan."""
    orig_check = main_module.MainWindow.check_for_updates
    monkeypatch.setattr(database, "DB_NAME", db_path)
    window = _make_window(monkeypatch)

    commands = []

    def fake_run(cmd, **kwargs):
        commands.append(cmd)
        args = cmd[1:]
        if args == ["rev-parse", "--is-inside-work-tree"]:
            return type("Result", (), {"returncode": 0, "stdout": "true", "stderr": ""})()
        if args == ["fetch", "origin"]:
            return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args == ["status", "-uno"]:
            return type("Result", (), {"returncode": 0, "stdout": "behind 'origin/main'", "stderr": ""})()
        if args == ["status", "--porcelain", "-uno"]:
            return type("Result", (), {"returncode": 0, "stdout": " M main.py", "stderr": ""})()
        return type("Result", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr(main_module.subprocess, "run", fake_run)
    info_shown = []
    monkeypatch.setattr(
        main_module.QMessageBox,
        "information",
        lambda *args, **kwargs: info_shown.append(args),
    )
    asked = []

    def fake_question(*args, **kwargs):
        asked.append(True)
        return main_module.QMessageBox.No

    monkeypatch.setattr(main_module.QMessageBox, "question", fake_question)

    orig_check(window)

    assert len(info_shown) == 1
    assert asked == []
    _close_window(qapp, window)


def test_parse_version_tuple():
    from main import parse_version_tuple
    assert parse_version_tuple("1.0.0") == (1, 0, 0)
    assert parse_version_tuple("v1.2.3") == (1, 2, 3)
    assert parse_version_tuple("v2.10.4-rc1") == (2, 10, 4, 1)
    assert parse_version_tuple("1.0.0") < parse_version_tuple("1.0.1")
    assert parse_version_tuple("1.9.0") < parse_version_tuple("1.10.0")


def test_get_default_db_path_behavior(monkeypatch, tmp_path):
    from database.connection import get_default_db_path
    import sys

    # Dev mode: returns ekin_board.db
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    monkeypatch.delenv("EKIN_DB_PATH", raising=False)
    assert get_default_db_path() == "ekin_board.db"

    # Frozen mode: returns ~/.ekin/ekin_board.db
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    custom_home = str(tmp_path / "home")
    monkeypatch.setenv("USERPROFILE", custom_home)
    monkeypatch.setenv("HOME", custom_home)
    path = get_default_db_path()
    assert ".ekin" in path
    assert path.endswith("ekin_board.db")


def test_release_check_thread_detects_newer_version(monkeypatch):
    import json
    from main import ReleaseCheckThread

    mock_release = {
        "tag_name": "v99.0.0",
        "body": "Release 99 notes",
        "assets": [
            {
                "name": "Ekin-Setup-v99.0.0.exe",
                "browser_download_url": "https://github.com/txeki-dev/Ekin/releases/download/v99.0.0/Ekin-Setup-v99.0.0.exe",
            }
        ],
    }
    payload = json.dumps(mock_release).encode("utf-8")

    class MockResponse:
        status = 200

        def read(self):
            return payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=6: MockResponse())

    emitted = []
    thread = ReleaseCheckThread()
    thread.update_available.connect(lambda ver, url, notes: emitted.append((ver, url, notes)))
    thread.run()

    assert len(emitted) == 1
    assert emitted[0][0] == "99.0.0"
    assert "Ekin-Setup-v99.0.0.exe" in emitted[0][1]
    assert emitted[0][2] == "Release 99 notes"


def test_release_check_thread_ignores_older_or_same_version(monkeypatch):
    import json
    from main import ReleaseCheckThread

    mock_release = {
        "tag_name": "v0.1.0",
        "assets": [{"name": "Ekin-Setup.exe", "browser_download_url": "http://test"}],
    }
    payload = json.dumps(mock_release).encode("utf-8")

    class MockResponse:
        status = 200

        def read(self):
            return payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=6: MockResponse())

    emitted = []
    thread = ReleaseCheckThread()
    thread.update_available.connect(lambda *args: emitted.append(args))
    thread.run()

    assert emitted == []


def test_installer_download_thread(tmp_path, monkeypatch):
    import io
    from main import InstallerDownloadThread

    content = b"MZ\x90\x00InstallerMockContent"

    class MockDownloadResponse:
        headers = {"Content-Length": str(len(content))}

        def __init__(self):
            self.buf = io.BytesIO(content)

        def read(self, size=65536):
            return self.buf.read(size)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr("urllib.request.urlopen", lambda req, timeout=30: MockDownloadResponse())

    dest_file = str(tmp_path / "Ekin-Setup-Test.exe")
    thread = InstallerDownloadThread("https://example.com/setup.exe", dest_file)
    finished_files = []
    progress_updates = []
    thread.finished.connect(lambda p: finished_files.append(p))
    thread.progress.connect(lambda d, t: progress_updates.append((d, t)))

    thread.run()

    assert finished_files == [dest_file]
    assert len(progress_updates) > 0
    assert progress_updates[-1] == (len(content), len(content))
    with open(dest_file, "rb") as f:
        assert f.read() == content


