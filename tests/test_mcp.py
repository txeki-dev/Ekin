"""
Pruebas automatizadas para el Servidor MCP (Model Context Protocol),
seguridad de sandbox, bloqueo de columnas y herramientas de manipulación de tareas.
"""

import json
import socket
import urllib.request

import pytest

import database
from mcp_server import (
    McpManager,
    McpProtocolHandler,
    McpSecurityError,
    authenticate_and_get_board,
    get_mcp_event_bus,
)
from mcp_sync_dialog import McpSyncDialog
import templates


@pytest.fixture
def mcp_board(db_path):
    """Crea un tablero de prueba con MCP activado y columnas."""
    tmpl = templates.TEMPLATE_SOFTWARE_AGILE
    board_id = templates.create_board_from_template("Proyecto MCP", "#2563eb", tmpl, db_path=db_path)
    database.set_board_mcp_config(board_id, enabled=True, secret="secret123", db_path=db_path)
    return database.get_board(board_id, db_path=db_path)


def test_mcp_authentication_and_sandboxing(db_path, mcp_board):
    # 1. Autenticación exitosa
    board = authenticate_and_get_board(mcp_board["board_uuid"], "secret123", db_path=db_path)
    assert board["id"] == mcp_board["id"]

    # 2. Token inválido
    with pytest.raises(McpSecurityError, match="Token secreto"):
        authenticate_and_get_board(mcp_board["board_uuid"], "token_erroneo", db_path=db_path)

    # 3. Token no proporcionado cuando hay secret configurado
    with pytest.raises(McpSecurityError, match="Token secreto"):
        authenticate_and_get_board(mcp_board["board_uuid"], None, db_path=db_path)

    # 4. MCP desactivado
    database.set_board_mcp_config(mcp_board["id"], enabled=False, db_path=db_path)
    with pytest.raises(McpSecurityError, match="desactivado por el usuario"):
        authenticate_and_get_board(mcp_board["board_uuid"], "secret123", db_path=db_path)


def test_mcp_columns_mutation_strictly_blocked(db_path, mcp_board):
    """El agente IA tiene bloqueada la creación, modificación y borrado de columnas."""
    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="TestAgent")

    for blocked_action in ["create_column", "delete_column", "update_column", "rename_column"]:
        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": blocked_action, "arguments": {"name": "Nueva Columna"}},
        }
        res = handler.handle(req)
        assert res["error"]["code"] == -32600
        assert "exclusivamente al usuario humano" in res["error"]["message"]


def test_mcp_tools_execution(db_path, mcp_board):
    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="ClaudeCode")
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    col_inbox = columns[0]["id"]
    col_progress = columns[2]["id"]

    # 1. list_columns
    res = handler.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_columns"}})
    cols_data = json.loads(res["result"]["content"][0]["text"])
    assert len(cols_data) == 5

    # 2. create_task
    mutated_events = []
    get_mcp_event_bus().board_mutated.connect(lambda bid: mutated_events.append(bid))

    create_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_task",
            "arguments": {
                "column_id": col_inbox,
                "title": "Refactorizar autenticación",
                "description": "Mejorar hashing de contraseñas.",
                "priority": "P0-Critical",
                "tags": ["security", "refactor"],
            },
        },
    }
    create_res = handler.handle(create_req)
    assert create_res["result"] is not None
    created_info = json.loads(create_res["result"]["content"][0]["text"])
    task_id = created_info["task_id"]
    assert task_id is not None
    assert len(mutated_events) >= 1

    # 3. get_task y verificar auditoría de creación
    task_detail = handler.executor._tool_get_task({"task_id": task_id})
    assert task_detail["title"] == "Refactorizar autenticación"
    assert any("[ClaudeCode]" in log["content"] for log in task_detail["logs"])

    # 4. update_task
    handler.handle({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "update_task",
            "arguments": {
                "task_id": task_id,
                "title": "Refactorizar autenticación y tokens",
                "priority": "P1-High",
            },
        },
    })
    updated_task = database.get_task(task_id, db_path=db_path)
    assert updated_task["title"] == "Refactorizar autenticación y tokens"

    # 5. move_task entre columnas
    handler.handle({
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "move_task",
            "arguments": {
                "task_id": task_id,
                "target_column_id": col_progress,
            },
        },
    })
    moved_task = database.get_task(task_id, db_path=db_path)
    assert moved_task["column_id"] == col_progress

    # 6. Intentar mover a columna de OTRO tablero -> Debe ser bloqueado por Sandbox
    other_board_id = database.create_board("Otro Tablero Ajeno", db_path=db_path)
    foreign_col_id = database.create_column(other_board_id, "Columna Ajena", db_path=db_path)
    cross_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "move_task",
            "arguments": {
                "task_id": task_id,
                "target_column_id": foreign_col_id,
            },
        },
    })
    assert cross_res["error"]["code"] == -32000
    assert "no pertenece al tablero vinculado" in cross_res["error"]["message"]

    # 7. add_task_comment y list_task_comments
    handler.handle({
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "add_task_comment",
            "arguments": {
                "task_id": task_id,
                "comment": "Iniciado desarrollo de la rama feature/auth.",
            },
        },
    })
    comments_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {"name": "list_task_comments", "arguments": {"task_id": task_id}},
    })
    comments = json.loads(comments_res["result"]["content"][0]["text"])
    assert any("feature/auth" in c["content"] for c in comments)


def test_mcp_list_tasks_returns_clean_description(db_path, mcp_board):
    """list_tasks no debe filtrar al agente el HTML/CSS de Qt (DOCTYPE, <style>, etc.)."""
    col_id = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    qt_html = (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
        '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
        "p, li { white-space: pre-wrap; }\n</style></head>"
        '<body style=" font-family:\'Figtree\';"><p>No funciona en el front &amp; sí en la tabla</p></body></html>'
    )
    database.create_task(col_id, "Registrar DIV", description=qt_html, db_path=db_path)

    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="ClaudeCode")
    res = handler.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_tasks"}})
    task = next(t for t in json.loads(res["result"]["content"][0]["text"]) if t["title"] == "Registrar DIV")
    assert task["description"] == "No funciona en el front & sí en la tabla"


def test_mcp_list_tasks_queries_each_column_once(db_path, mcp_board, monkeypatch):
    """list_tasks tenía un primer bucle muerto que repetía las consultas de cada columna."""
    calls = []
    real_get_tasks = database.get_tasks
    monkeypatch.setattr(database, "get_tasks", lambda *a, **k: calls.append(a) or real_get_tasks(*a, **k))

    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="ClaudeCode")
    handler.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "list_tasks"}})

    assert len(calls) == len(database.get_columns(mcp_board["id"], db_path=db_path))


def test_mcp_prompts_synergy(db_path, mcp_board):
    """Verifica que el prompt contextual del tablero (Scrum Master / Opositor) se expone al agente."""
    handler = McpProtocolHandler(mcp_board, db_path=db_path)

    # 1. prompts/list
    p_list = handler.handle({"jsonrpc": "2.0", "id": 1, "method": "prompts/list"})
    prompts = p_list["result"]["prompts"]
    assert len(prompts) == 1
    assert prompts[0]["name"] == "kanban_board_context"

    # 2. prompts/get
    p_get = handler.handle({"jsonrpc": "2.0", "id": 2, "method": "prompts/get", "params": {"name": "kanban_board_context"}})
    text_content = p_get["result"]["messages"][0]["content"]["text"]
    assert "Tech Lead y Scrum Master" in text_content
    assert "NO intentes crear, editar o eliminar columnas" in text_content


def test_mcp_http_server_live(db_path, mcp_board):
    """Prueba el servidor HTTP embebido realizando peticiones directas."""
    manager = McpManager(db_path=db_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        test_port = s.getsockname()[1]
    started = manager.start(port=test_port)
    assert started is True

    try:
        # 1. Endpoint /status
        status_url = f"http://127.0.0.1:{test_port}/status"
        with urllib.request.urlopen(status_url, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["server"] == "ekin-kanban-mcp"

        # 2. Endpoint /rpc para inicializar y listar tools
        rpc_url = f"http://127.0.0.1:{test_port}/rpc?board={mcp_board['board_uuid']}&token=secret123"
        req_body = json.dumps({"jsonrpc": "2.0", "id": 42, "method": "tools/list"}).encode("utf-8")
        req = urllib.request.Request(rpc_url, data=req_body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["id"] == 42
            tools = data["result"]["tools"]
            tool_names = [t["name"] for t in tools]
            assert "create_task" in tool_names
            assert "move_task" in tool_names

    finally:
        manager.stop()
        assert not manager.is_running()


def test_mcp_sync_dialog_headless(qapp, db_path, mcp_board):
    """Prueba el diálogo modal de configuración McpSyncDialog."""
    dlg = McpSyncDialog(mcp_board["id"], db_path=db_path)
    assert dlg.board_uuid == mcp_board["board_uuid"]
    assert dlg.enable_checkbox.isChecked() is True

    # Generar nuevo token
    dlg._generate_new_token()
    new_token = dlg.token_input.text()
    assert len(new_token) == 32

    # Verificar generación de comandos
    assert new_token in dlg.claude_code_edit.toPlainText()
    assert "claude mcp add" in dlg.claude_code_edit.toPlainText()

    # Guardar cambios
    dlg._save_and_apply()

    refreshed_board = database.get_board(mcp_board["id"], db_path=db_path)
    assert refreshed_board["mcp_secret"] == new_token
    assert refreshed_board["mcp_enabled"] == 1
    dlg.reject()


def test_board_view_mcp_btn_states(qapp, db_path, mcp_board):
    """Verifica que el botón MCP en BoardViewWidget refleje el estado activo/inactivo."""
    from board_view import BoardViewWidget
    from strings import t

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(mcp_board["id"])
    assert hasattr(bv, "mcp_btn")
    assert not bv.mcp_btn.isHidden()
    assert bv.mcp_btn.text() == t("mcp.board_btn_active")

    # Desactivar MCP en el tablero y recargar
    database.set_board_mcp_config(mcp_board["id"], enabled=False, db_path=db_path)
    bv.load_board(mcp_board["id"])
    assert bv.mcp_btn.text() == t("mcp.board_btn_inactive")

    # Pantalla de bienvenida (-1)
    bv.load_board(-1)
    assert bv.mcp_btn.isHidden()
    bv.deleteLater()


def test_ekin_mcp_cli_roundtrip(db_path, mcp_board, monkeypatch):
    """Prueba la CLI de transporte stdio ekin_mcp con entrada y salida simuladas."""
    import io
    import ekin_mcp

    req = json.dumps({"jsonrpc": "2.0", "id": 100, "method": "tools/list"})
    fake_stdin = io.StringIO(f"{req}\n")
    fake_stdout = io.StringIO()

    monkeypatch.setattr("sys.stdin", fake_stdin)
    monkeypatch.setattr("sys.stdout", fake_stdout)

    argv = ["--board-uuid", mcp_board["board_uuid"], "--token", "secret123", "--db-path", db_path]
    ekin_mcp.main(argv)

    output = fake_stdout.getvalue()
    assert output.strip() != ""
    resp = json.loads(output.strip())
    assert resp["id"] == 100
    assert "tools" in resp["result"]


def test_ekin_mcp_cli_auth_failure(db_path, mcp_board, monkeypatch):
    """Verifica que ekin_mcp falle limpiamente con código de salida si el token es incorrecto."""
    import ekin_mcp

    argv = ["--board-uuid", mcp_board["board_uuid"], "--token", "wrong_token", "--db-path", db_path]
    with pytest.raises(SystemExit) as exc_info:
        ekin_mcp.main(argv)
    assert exc_info.value.code == 1


def test_mcp_search_tasks_semantic(db_path, mcp_board):
    """Prueba la búsqueda semántica basada en embeddings a través de la herramienta MCP."""
    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="SemanticAgent")
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    col_id = columns[0]["id"]

    # Crear tareas con conceptos diferenciados
    handler.handle({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_task",
            "arguments": {
                "column_id": col_id,
                "title": "Optimizar consultas SQL e índices de base de datos",
                "description": "Configurar PRAGMAs WAL y pool de conexiones SQLite.",
            },
        },
    })
    handler.handle({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_task",
            "arguments": {
                "column_id": col_id,
                "title": "Diseño visual de componentes y paleta de colores",
                "description": "Tokens de estilo Orgánico y tema oscuro. Contacto: dev@example.com sk-proj-123456789012345678901234567890",
            },
        },
    })

    # 1. Búsqueda semántica sobre base de datos
    search_req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_tasks_semantic",
            "arguments": {
                "query": "persistencia sqlite y backend relacional",
                "top_k": 3,
            },
        },
    }
    res = handler.handle(search_req)
    results = json.loads(res["result"]["content"][0]["text"])
    assert len(results) >= 1
    assert "Optimizar consultas SQL" in results[0]["title"]
    assert "similarity" in results[0]
    assert results[0]["similarity"] > 0

    # 2. Búsqueda semántica con sanitización de privacidad (Privacy Shield)
    search_shield_req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "search_tasks_semantic",
            "arguments": {
                "query": "interfaz de usuario colores y estilos",
                "top_k": 3,
                "mask_sensitive": True,
            },
        },
    }
    res_shield = handler.handle(search_shield_req)
    results_shield = json.loads(res_shield["result"]["content"][0]["text"])
    assert len(results_shield) >= 1
    ui_task = next(r for r in results_shield if "Diseño visual" in r["title"])
    assert "[REDACTED_EMAIL]" in ui_task["description"]
    assert "dev@example.com" not in ui_task["description"]


def test_mcp_create_tasks_batch(db_path, mcp_board):
    """Prueba la creación atómica de múltiples tareas en lote (batch) vía MCP."""
    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="BatchAgent")
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    col_id = columns[1]["id"]

    tasks_payload = [
        {"title": "Subtarea 1: Migración", "description": "Detalles migración", "priority": "P0-Critical", "tags": ["db", "v1.2"]},
        {"title": "Subtarea 2: API Endpoints", "description": "Endpoints REST/RPC", "priority": "P1-High", "tags": ["api"]},
        {"title": "Subtarea 3: Tests unitarios", "description": "Cobertura 100%", "priority": "P2-Medium", "tags": ["qa"]},
    ]

    batch_req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "create_tasks_batch",
            "arguments": {
                "column_id": col_id,
                "tasks": tasks_payload,
            },
        },
    }
    res = handler.handle(batch_req)
    data = json.loads(res["result"]["content"][0]["text"])
    assert data["success"] is True
    assert data["created_count"] == 3
    assert len(data["tasks"]) == 3

    # Verificar existencia en BD
    tasks_db = database.get_tasks(col_id, db_path=db_path)
    titles = [t["title"] for t in tasks_db]
    assert "Subtarea 1: Migración" in titles
    assert "Subtarea 2: API Endpoints" in titles
    assert "Subtarea 3: Tests unitarios" in titles

    # Verificar aislamiento Sandbox: columna perteneciente a otro tablero
    other_bid = database.create_board("Tablero Foráneo", db_path=db_path)
    foreign_cid = database.create_column(other_bid, "Columna Foránea", db_path=db_path)
    invalid_req = {
        "jsonrpc": "2.0",
        "id": 11,
        "method": "tools/call",
        "params": {
            "name": "create_tasks_batch",
            "arguments": {
                "column_id": foreign_cid,
                "tasks": [{"title": "Intruso"}],
            },
        },
    }
    err_res = handler.handle(invalid_req)
    assert err_res["error"]["code"] == -32000
    assert "no pertenece al tablero" in err_res["error"]["message"]


def test_mcp_control_task_timer(db_path, mcp_board):
    """Prueba el control de temporizadores de tareas (start, status, stop) vía MCP."""
    handler = McpProtocolHandler(mcp_board, db_path=db_path, client_name="TimerAgent")
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    col_id = columns[0]["id"]

    # Crear una tarea
    create_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 20,
        "method": "tools/call",
        "params": {
            "name": "create_task",
            "arguments": {"column_id": col_id, "title": "Tarea con temporizador"},
        },
    })
    task_id = json.loads(create_res["result"]["content"][0]["text"])["task_id"]

    # 1. Iniciar temporizador
    start_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 21,
        "method": "tools/call",
        "params": {
            "name": "control_task_timer",
            "arguments": {"task_id": task_id, "action": "start"},
        },
    })
    start_data = json.loads(start_res["result"]["content"][0]["text"])
    assert start_data["timer_running"] is True
    assert isinstance(start_data["started_at"], str)

    # 2. Consultar estado
    status_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 22,
        "method": "tools/call",
        "params": {
            "name": "control_task_timer",
            "arguments": {"task_id": task_id, "action": "status"},
        },
    })
    status_data = json.loads(status_res["result"]["content"][0]["text"])
    assert status_data["timer_running"] is True
    assert status_data["elapsed_seconds"] >= 0

    # 3. Detener temporizador
    stop_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 23,
        "method": "tools/call",
        "params": {
            "name": "control_task_timer",
            "arguments": {"task_id": task_id, "action": "stop"},
        },
    })
    stop_data = json.loads(stop_res["result"]["content"][0]["text"])
    assert stop_data["timer_running"] is False
    assert "elapsed_seconds" in stop_data

    # Verificar que el diario de la tarea registre los eventos del temporizador
    logs = database.get_task_logs(task_id, db_path=db_path)
    log_texts = [lg["content"] for lg in logs]
    assert any("Temporizador iniciado" in text for text in log_texts)
    assert any("Temporizador detenido" in text for text in log_texts)

    # 4. Acción inválida
    inv_res = handler.handle({
        "jsonrpc": "2.0",
        "id": 24,
        "method": "tools/call",
        "params": {
            "name": "control_task_timer",
            "arguments": {"task_id": task_id, "action": "pause"},
        },
    })
    assert inv_res["error"]["code"] == -32603
    assert "no reconocida" in inv_res["error"]["message"]


def test_mcp_sse_session_scavenger():
    """Verifica que el recolector de sesiones SSE elimine sesiones inactivas o cerradas."""
    import time
    import threading
    from mcp_server import McpHttpServer, _SseClientSession

    server = McpHttpServer.__new__(McpHttpServer)
    server._sessions = {}
    server._lock = threading.Lock()
    server.is_running = True

    # 1. Sesión activa reciente
    s_active = _SseClientSession(session_id="active-1", board_uuid="uuid-1")
    s_active.last_active_at = time.time()

    # 2. Sesión cerrada
    s_closed = _SseClientSession(session_id="closed-2", board_uuid="uuid-1")
    s_closed.is_closed = True

    # 3. Sesión zombie/inactiva antigua
    s_idle = _SseClientSession(session_id="idle-3", board_uuid="uuid-1")
    s_idle.last_active_at = time.time() - 3600.0  # Hace 1 hora

    server._sessions["active-1"] = s_active
    server._sessions["closed-2"] = s_closed
    server._sessions["idle-3"] = s_idle

    # Ejecutamos la recolección con timeout de 300 segundos
    purged = server.scavenge_stale_sessions(max_idle_seconds=300.0)
    assert purged == 2
    assert "active-1" in server._sessions
    assert "closed-2" not in server._sessions
    assert "idle-3" not in server._sessions


def test_mcp_sse_send_to_session_queue_limit():
    """Verifica el control de contrapresión y límite de cola en sesiones SSE."""
    import threading
    from mcp_server import McpHttpServer, _SseClientSession

    server = McpHttpServer.__new__(McpHttpServer)
    server._sessions = {}
    server._lock = threading.Lock()

    session = _SseClientSession(session_id="queue-test", board_uuid="uuid-1")
    server._sessions["queue-test"] = session

    # Llenamos la cola de 100 mensajes
    for i in range(100):
        assert server.send_to_session("queue-test", {"count": i}) is True

    # El mensaje 101 supera la capacidad -> debe descartarse y marcar sesión como cerrada
    assert server.send_to_session("queue-test", {"count": 101}) is False
    assert session.is_closed is True

