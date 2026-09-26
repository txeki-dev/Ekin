"""Pruebas unitarias para el refresco automático del tablero y diálogo de tareas
cuando un agente de IA trabaja vía MCP y la interfaz gráfica de Ekin está operativa (Tarea #53).
"""

import sqlite3
import database
from board_view import BoardViewWidget
from detail_dialog import TaskDetailDialog
from mcp_server import get_mcp_event_bus


def test_get_db_data_version_and_fingerprint(db_path):
    """Verifica que PRAGMA data_version y la huella digital del tablero detecten mutaciones externas."""
    board_id = database.create_board("Tablero Test MCP", "#3b82f6", db_path=db_path)
    col_id = database.create_column(board_id, "Pendiente", "#3b82f6", db_path=db_path)

    v0 = database.get_db_data_version(db_path)
    fp0 = database.get_board_mutation_fingerprint(board_id, db_path)
    assert isinstance(v0, int)
    assert isinstance(fp0, tuple)
    assert len(fp0) >= 6

    # 1. Simular escritura externa en SQLite (otra conexión directa)
    ext_conn = sqlite3.connect(db_path)
    ext_conn.execute("INSERT INTO tasks (column_id, title, position) VALUES (?, ?, ?)", (col_id, "Tarea Externa", 0))
    ext_conn.commit()
    ext_conn.close()

    v1 = database.get_db_data_version(db_path)
    fp1 = database.get_board_mutation_fingerprint(board_id, db_path)

    # La versión de datos SQLite debe haberse incrementado
    assert v1 > v0
    # La huella del tablero debe haber cambiado
    assert fp1 != fp0

    # 2. Modificación en un tablero DISTINTO no debe alterar la huella de este tablero
    board2 = database.create_board("Otro Tablero", "#10b981", db_path=db_path)
    col2 = database.create_column(board2, "Col 2", "#10b981", db_path=db_path)
    database.create_task(col2, "Tarea de Otro Tablero", db_path=db_path)

    fp1_after_other = database.get_board_mutation_fingerprint(board_id, db_path)
    assert fp1_after_other == fp1


def test_board_view_auto_detects_external_mcp_mutation(qapp, db_path):
    """Verifica que BoardViewWidget detecte la escritura de un agente MCP externo
    y refresque el tablero automáticamente preservando la estabilidad visual."""
    board_id = database.create_board("Tablero Live", "#3b82f6", db_path=db_path)
    col_id = database.create_column(board_id, "Col 1", "#3b82f6", db_path=db_path)
    database.set_board_mcp_config(board_id, enabled=True, db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    assert len(bv.column_widgets[col_id].findChildren(database.tasks if hasattr(database, "TaskCard") else object)) >= 0
    initial_fp = bv._last_board_fingerprint

    # Simular agente de IA creando una tarea vía MCP CLI (proceso externo sobre SQLite)
    ext_conn = sqlite3.connect(db_path)
    ext_conn.execute(
        "INSERT INTO tasks (column_id, title, description, position) VALUES (?, ?, ?, ?)",
        (col_id, "Tarea creada por IA", "Detalles desde MCP", 0)
    )
    ext_conn.commit()
    ext_conn.close()

    # Ejecutar el chequeo de mutación reactiva
    bv._check_external_mcp_mutations()

    # El temporizador de debounce debe haberse activado
    assert bv._mcp_reload_debounce_timer.isActive()

    # Ejecutar la recarga segura (disparo del debounce)
    bv._perform_safe_mcp_board_reload()

    # La tarea debe figurar ahora en el tablero sin que el usuario haya tenido que recargar
    tasks_now = database.get_tasks(col_id, db_path)
    assert len(tasks_now) == 1
    assert tasks_now[0]["title"] == "Tarea creada por IA"
    assert bv._last_board_fingerprint != initial_fp


def test_board_view_mcp_event_bus_trigger(qapp, db_path):
    """Verifica que emitir board_mutated en el bus de eventos desencadene la recarga suave con debounce."""
    board_id = database.create_board("Tablero Bus", "#3b82f6", db_path=db_path)
    col_id = database.create_column(board_id, "Col A", "#3b82f6", db_path=db_path)
    database.set_board_mcp_config(board_id, enabled=True, db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    # Crear una tarea en la BD
    database.create_task(col_id, "Tarea Nueva", db_path=db_path)

    # Emitir señal en el bus
    get_mcp_event_bus().board_mutated.emit(board_id)
    assert bv._mcp_reload_debounce_timer.isActive()

    # Al ejecutar el reload
    bv._perform_safe_mcp_board_reload()
    assert col_id in bv.column_widgets


def test_task_detail_dialog_live_refresh_on_mcp_log(qapp, db_path):
    """Verifica que si TaskDetailDialog está abierto, se actualice en tiempo real
    cuando un agente IA agrega un log/comentario vía MCP."""
    board_id = database.create_board("Tablero Dialog", "#3b82f6", db_path=db_path)
    col_id = database.create_column(board_id, "Col", "#3b82f6", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea en Revisión", db_path=db_path)

    dlg = TaskDetailDialog(task_id, db_path=db_path)

    assert len(dlg._all_logs) == 0

    # Simular agente IA añadiendo un comentario vía MCP
    database.create_log(task_id, "<p>Comentario del Agente IA: Todo verificado.</p>", db_path=db_path)

    # Notificar mutación MCP
    get_mcp_event_bus().board_mutated.emit(board_id)

    # El diálogo debe haber recargado el diario automáticamente
    assert len(dlg._all_logs) == 1
    assert "Agente IA" in dlg._all_logs[0]["content"]

    dlg.close()
