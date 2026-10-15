"""Pruebas unitarias para BoardSyncController (desacoplamiento de la concurrencia de sincronización)."""

import json
import database
import board_sync
from board_sync_controller import BoardSyncController


def test_controller_initial_state(qapp, db_path):
    controller = BoardSyncController(db_path=db_path)
    assert controller.board_id is None
    assert controller.is_linked is False
    assert controller.current_sync_info is None
    assert controller.is_running() is False
    assert controller.last_sync_summary == ""


def test_controller_set_board_emits_status(qapp, db_path):
    board_id = database.create_board("Test Board", "#3b82f6", db_path)
    controller = BoardSyncController(db_path=db_path)

    emitted_statuses = []
    controller.sync_status_changed.connect(lambda s: emitted_statuses.append(s))

    controller.set_board(board_id)
    assert len(emitted_statuses) == 1
    assert emitted_statuses[0]["sync_path"] is None  # Sin vincular
    assert controller.is_linked is False

    # Deseleccionar tablero
    controller.set_board(-1)
    assert len(emitted_statuses) == 2
    assert emitted_statuses[1] is None


def test_controller_linked_board(qapp, db_path, tmp_path):
    board_id = database.create_board("Linked Board", "#3b82f6", db_path)
    sync_file = tmp_path / "test.ekboard"
    sync_file.write_text(json.dumps({
        "version": 1,
        "board_uuid": database.get_board(board_id, db_path)["board_uuid"],
        "board_name": "Linked Board",
        "board_color": "#3b82f6",
        "columns": [],
        "tasks": [],
        "last_modified": "2026-09-13 12:00:00"
    }), encoding="utf-8")

    database.set_board_sync_path(board_id, str(sync_file), db_path)

    controller = BoardSyncController(db_path=db_path)
    controller.set_board(board_id)

    assert controller.is_linked is True
    assert controller.current_sync_info["sync_path"] == str(sync_file)
    assert controller._watched_sync_path == str(sync_file)

    # Desvincular
    unlinked = controller.unlink_current_board()
    assert unlinked is True
    assert controller.is_linked is False


def test_controller_sync_now_blocking(qapp, db_path, tmp_path):
    board_id = database.create_board("Sync Board", "#3b82f6", db_path)
    sync_file = tmp_path / "sync.ekboard"
    database.set_board_sync_path(board_id, str(sync_file), db_path)

    controller = BoardSyncController(db_path=db_path)
    controller.set_board(board_id)

    results = []
    controller.sync_finished.connect(lambda res, user_init: results.append((res, user_init)))

    res = controller.sync_now(user_initiated=True, blocking=True)
    assert res is not None
    assert res.status in ("exported", "up_to_date")
    assert len(results) == 1
    assert results[0][1] is True  # user_initiated
    assert "Synced" in controller.last_sync_summary or "Exported" in controller.last_sync_summary or "Up to date" in controller.last_sync_summary


def test_controller_board_data_reloaded_signal(qapp, db_path):
    controller = BoardSyncController(db_path=db_path)
    reloaded = []
    controller.board_data_reloaded.connect(lambda: reloaded.append(True))

    # status="merged" debe emitir board_data_reloaded
    res = board_sync.SyncResult(status="merged", board_id=1, tasks_imported=2)
    controller._handle_sync_finished(res, user_initiated=False)
    assert len(reloaded) == 1

    # status="up_to_date" no debe emitirlo
    res_uptodate = board_sync.SyncResult(status="up_to_date", board_id=1)
    controller._handle_sync_finished(res_uptodate, user_initiated=False)
    assert len(reloaded) == 1


def test_controller_retries_a_busy_sync_instead_of_reporting_it(qapp, db_path, monkeypatch):
    """#124: si otra sync del mismo tablero está en curso, el resultado «busy» no se notifica
    como terminado: el controlador la reintenta en un momento."""
    import board_sync_controller
    retries = []
    monkeypatch.setattr(board_sync_controller.QTimer, "singleShot", lambda ms, fn: retries.append(ms))
    controller = BoardSyncController(db_path=db_path)
    finished = []
    controller.sync_finished.connect(lambda res, user_init: finished.append(res))

    controller._handle_sync_finished(board_sync.SyncResult(status="busy", board_id=1), user_initiated=True)

    assert finished == [] and len(retries) == 1


def test_sidebar_sync_now_on_a_busy_board_informs_instead_of_failing(qapp, db_path, monkeypatch, tmp_path):
    """#124: «Sincronizar ahora» mientras la sync automática del mismo tablero sigue en curso
    avisa de que ya se está sincronizando, sin mostrarlo como un error."""
    import sidebar
    board_id = database.create_board("Sync Board", "#3b82f6", db_path)
    database.set_board_sync_path(board_id, str(tmp_path / "sync.ekboard"), db_path)
    shown = []
    monkeypatch.setattr(sidebar.QMessageBox, "information", lambda *a, **k: shown.append(("info", a[1])))
    monkeypatch.setattr(sidebar.QMessageBox, "warning", lambda *a, **k: shown.append(("warning", a[1])))
    bar = sidebar.SidebarWidget(db_path=db_path)

    with board_sync._board_sync_lock(board_id, db_path):
        bar.handle_sync_action(board_id, "sync")

    assert shown == [("info", sidebar.t("sync.busy_title"))]
    bar.deleteLater()
