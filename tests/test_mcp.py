"""
Pruebas automatizadas para el Servidor MCP (Model Context Protocol),
seguridad de sandbox, bloqueo de columnas y herramientas de manipulación de tareas.
"""

import json
import socket
import urllib.request
from types import SimpleNamespace

import pytest

import database
from mcp_server import (
    McpManager,
    McpProtocolHandler,
    McpSecurityError,
    authenticate_and_get_board,
    get_mcp_event_bus,
)
from html_utils import clean_html_description
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
    with pytest.raises(McpSecurityError, match="secret token"):
        authenticate_and_get_board(mcp_board["board_uuid"], "token_erroneo", db_path=db_path)

    # 3. Token no proporcionado cuando hay secret configurado
    with pytest.raises(McpSecurityError, match="secret token"):
        authenticate_and_get_board(mcp_board["board_uuid"], None, db_path=db_path)

    # 4. MCP desactivado
    database.set_board_mcp_config(mcp_board["id"], enabled=False, db_path=db_path)
    with pytest.raises(McpSecurityError, match="disabled by the user"):
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
        assert "reserved to the human user" in res["error"]["message"]


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
    assert "does not belong to the linked board" in cross_res["error"]["message"]

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
    assert "Columns are human-only" in text_content


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


def test_board_view_mcp_btn_states(qapp, db_path, mcp_board, monkeypatch):
    """Verifica que el botón MCP en BoardViewWidget refleje el estado activo/inactivo."""
    from board_view import BoardViewWidget
    from strings import t

    import board_mixins
    running = SimpleNamespace(is_running=lambda: True, port=8765)
    monkeypatch.setattr(board_mixins, "get_mcp_manager", lambda db_path=None: running)

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
    assert "does not belong to the linked board" in err_res["error"]["message"]


def test_audit_cards_round_trip_through_the_audit_tag(db_path, mcp_board):
    """#111: el prompt AUDIT crea sus tarjetas con `tags: ["audit", <categoría>]` y `priority`, y
    REMEDIATE arma su cola con `list_tasks(tag="audit")`: solo deben volver esas tarjetas."""
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    executor._tool_create_task({"column_id": col, "title": "Feature sin auditar", "tags": ["ux"]})
    executor._tool_create_tasks_batch({"column_id": col, "tasks": [
        {"title": "[HIGH] [BUG] a.py: x", "priority": "P1-High", "tags": ["audit", "bug"]},
        {"title": "[LOW] [CLEANUP] b.py: y", "priority": "P3-Low", "tags": ["audit", "cleanup"]},
    ]})

    queue = executor._tool_list_tasks({"tag": "audit"})
    assert sorted(t["title"] for t in queue) == ["[HIGH] [BUG] a.py: x", "[LOW] [CLEANUP] b.py: y"]
    assert all("audit" in t["tags"] and t["column_id"] == col for t in queue)
    assert "P1-High" in next(t for t in queue if t["title"].startswith("[HIGH]"))["tags"]


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
    assert "Unknown timer action" in inv_res["error"]["message"]


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



def test_mcp_move_task_bumps_version_only_on_column_change(db_path, mcp_board):
    """#97: el move_task del MCP sube `version` al cambiar de columna (para que la sync .ekboard
    lo vea como cambio local) y no al recolocar dentro de la misma columna."""
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    task_id = database.create_task(columns[0]["id"], "Versionada", db_path=db_path)
    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor

    v0 = database.get_task(task_id, db_path)["version"]
    executor._tool_move_task({"task_id": task_id, "target_column_id": columns[0]["id"], "target_position": 0})
    assert database.get_task(task_id, db_path)["version"] == v0

    executor._tool_move_task({"task_id": task_id, "target_column_id": columns[2]["id"]})
    assert database.get_task(task_id, db_path)["version"] == v0 + 1


def _done_and_other_columns(db_path, board_id):
    import column_roles
    columns = database.get_columns(board_id, db_path=db_path)
    done = next(c for c in columns if column_roles.classify_column(c["name"]) == column_roles.DONE)
    other = next(c for c in columns if c["id"] != done["id"])
    return done, other


@pytest.mark.parametrize("template", [templates.TEMPLATE_SOFTWARE_AGILE, templates.TEMPLATE_GTD_PERSONAL])
def test_mcp_move_task_to_done_clears_due_date(db_path, template):
    """#83: cuando un agente pasa una tarjeta a Done (en cualquier tablero) se le quita la fecha,
    para que no siga en el Calendario ni en Mi trabajo; la fecha antigua queda en el diario."""
    board_id = templates.create_board_from_template("Tablero", "#2563eb", template, db_path=db_path)
    board = database.get_board(board_id, db_path=db_path)
    done, other = _done_and_other_columns(db_path, board_id)
    task_id = database.create_task(other["id"], "Con fecha", due_date="2026-10-20", db_path=db_path)
    database.save_task_full(task_id, "Con fecha", due_date="2026-10-20", due_time="10:30", db_path=db_path)
    version = database.get_task(task_id, db_path)["version"]

    executor = McpProtocolHandler(board, db_path=db_path, client_name="Agente").executor
    res = executor._tool_move_task({"task_id": task_id, "target_column_id": done["id"]})

    task = database.get_task(task_id, db_path)
    assert (task["due_date"], task["due_time"]) == (None, None)
    assert task["version"] == version + 1
    assert res["due_date_cleared"] is True
    assert any("2026-10-20 10:30" in log["content"] for log in database.get_task_logs(task_id, db_path=db_path))
    assert all(t["id"] != task_id for t in database.get_scheduled_tasks(db_path=db_path))


def test_mcp_move_task_to_other_column_keeps_due_date(db_path, mcp_board):
    done, other = _done_and_other_columns(db_path, mcp_board["id"])
    target = next(c for c in database.get_columns(mcp_board["id"], db_path=db_path) if c["id"] not in (done["id"], other["id"]))
    task_id = database.create_task(other["id"], "Con fecha", due_date="2026-10-20", db_path=db_path)

    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor
    res = executor._tool_move_task({"task_id": task_id, "target_column_id": target["id"]})

    assert database.get_task(task_id, db_path)["due_date"] == "2026-10-20"
    assert res["due_date_cleared"] is False


def test_mcp_move_task_to_done_without_due_date_logs_no_date(db_path, mcp_board):
    done, other = _done_and_other_columns(db_path, mcp_board["id"])
    task_id = database.create_task(other["id"], "Sin fecha", db_path=db_path)

    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor
    res = executor._tool_move_task({"task_id": task_id, "target_column_id": done["id"]})

    assert res["due_date_cleared"] is False
    assert not any("Fecha de vencimiento" in log["content"] for log in database.get_task_logs(task_id, db_path=db_path))


def _task_with_every_field(db_path, board_id):
    col = database.get_columns(board_id, db_path=db_path)[0]["id"]
    linked = database.create_board("Enlazado", db_path=db_path)
    task_id = database.create_task(col, "Original", db_path=db_path)
    tag_id = database.get_or_create_tag_value("General", "backend", "#6b7280", db_path=db_path)
    database.save_task_full(
        task_id, "Original", description="desc", due_date="2026-10-20", due_time="09:00",
        tag_value_ids=[tag_id], recurrence="weekly", linked_board_id=linked,
        tag_text="legacy", tag_color="#ff0000", db_path=db_path,
    )
    return task_id, linked


def test_mcp_update_task_preserves_fields_it_does_not_receive(db_path, mcp_board):
    """#98: update_task usaba el database.update_task legado, que pisaba tag_text/tag_color y
    no conocía due_time. Ahora solo cambia lo que recibe, en una transacción y una versión."""
    task_id, linked = _task_with_every_field(db_path, mcp_board["id"])
    version = database.get_task(task_id, db_path)["version"]

    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor
    executor._tool_update_task({"task_id": task_id, "title": "Renombrada"})

    task = database.get_task(task_id, db_path)
    assert task["title"] == "Renombrada"
    assert (task["description"], task["due_date"], task["due_time"]) == ("desc", "2026-10-20", "09:00")
    assert (task["recurrence"], task["linked_board_id"]) == ("weekly", linked)
    assert (task["tag_text"], task["tag_color"]) == ("legacy", "#ff0000")
    assert [tg["value"] for tg in task["tags"]] == ["backend"]
    assert task["version"] == version + 1


def test_mcp_update_task_sets_due_time_and_clears_date_and_time(db_path, mcp_board):
    task_id, _ = _task_with_every_field(db_path, mcp_board["id"])
    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor

    executor._tool_update_task({"task_id": task_id, "due_date": "2026-11-02", "due_time": "18:15"})
    task = database.get_task(task_id, db_path)
    assert (task["due_date"], task["due_time"]) == ("2026-11-02", "18:15")

    executor._tool_update_task({"task_id": task_id, "due_date": ""})
    task = database.get_task(task_id, db_path)
    assert (task["due_date"], task["due_time"]) == (None, None)

    schema = next(tool for tool in __import__("mcp_server").get_mcp_tools_schema() if tool["name"] == "update_task")
    assert "due_time" in schema["inputSchema"]["properties"]


def test_mcp_update_task_replaces_tags_and_priority_like_before(db_path, mcp_board):
    task_id, _ = _task_with_every_field(db_path, mcp_board["id"])
    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor

    executor._tool_update_task({"task_id": task_id, "priority": "P1-High"})
    values = {(tg["category"], tg["value"]) for tg in database.get_task_tags(task_id, db_path=db_path)}
    assert values == {("Priority", "P1-High"), ("General", "backend")}

    executor._tool_update_task({"task_id": task_id, "tags": ["frontend"]})
    values = {(tg["category"], tg["value"]) for tg in database.get_task_tags(task_id, db_path=db_path)}
    assert values == {("Priority", "P1-High"), ("General", "frontend")}


MD_DESC = "### DoD\n\n- [ ] tests\n- [ ] docs"


def test_mcp_writes_markdown_as_qt_html(db_path, mcp_board):
    """#99: create_task, create_tasks_batch, update_task y add_task_comment guardan el Markdown
    del agente como HTML de Qt (la app lo pinta con setHtml / QLabel rich text)."""
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor

    created = executor._tool_create_task({"column_id": col, "title": "A", "description": MD_DESC})["task_id"]
    batch = executor._tool_create_tasks_batch({"column_id": col, "tasks": [{"title": "B", "description": MD_DESC}]})
    updated = batch["tasks"][0]["task_id"]
    executor._tool_update_task({"task_id": updated, "description": "Nueva\n\n- x"})
    executor._tool_add_task_comment({"task_id": created, "comment": "DONE:\n- uno\n- <b>dos</b>"})

    for task_id in (created, updated):
        assert '<li class="unchecked"' in database.get_task(created, db_path)["description"]
        assert "<li" in database.get_task(task_id, db_path)["description"]
    comment = database.get_task_logs(created, db_path=db_path)[-1]["content"]
    assert "<li" in comment and "&lt;b&gt;dos&lt;/b&gt;" in comment
    assert clean_html_description(comment).startswith("[Claude Code]: DONE:")


QT_HTML = (
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
    '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
    "p, li { white-space: pre-wrap; }\n</style></head>"
    '<body style=" font-family:\'Figtree\';"><p>Escribe a dev@ejemplo.com</p></body></html>'
)


def test_mcp_exposes_column_roles_and_active_task(db_path, mcp_board):
    """#84: list_columns, get_board_info, las instrucciones y el resumen exponen el rol de cada
    columna y la tarea activa, para que los prompts no dependan del nombre o la posición."""
    columns = database.get_columns(mcp_board["id"], db_path=db_path)
    for c in columns:  # la plantilla siembra tareas de ejemplo
        for task in database.get_tasks(c["id"], db_path=db_path):
            database.delete_task(task["id"], db_path=db_path)
    ready = database.create_task(columns[1]["id"], "Lista para dev@ejemplo.com", db_path=db_path)
    handler = McpProtocolHandler(mcp_board, db_path=db_path)
    executor = handler.executor

    roles = [c["role"] for c in executor._tool_list_columns({})]
    assert roles == ["backlog", "ready", "in_progress", "review", "done"]
    assert [c["role"] for c in executor._tool_get_board_info({})["columns"]] == roles
    assert "role: ready" in handler._build_instructions()

    summary = executor._tool_get_board_executive_summary({"mask_sensitive": True})
    assert summary["active_task"]["id"] == ready and summary["active_task"]["role"] == "ready"
    assert "dev@ejemplo.com" not in json.dumps(summary, ensure_ascii=False)
    assert [c["role"] for c in summary["columns_flow"]] == roles


def test_mcp_comments_and_get_task_return_clean_text(db_path, mcp_board):
    """#84: list_task_comments y get_task devolvían el HTML de Qt crudo (DOCTYPE, <style>)."""
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    task_id = database.create_task(col, "T", description=QT_HTML, db_path=db_path)
    database.add_task_log(task_id, QT_HTML, db_path=db_path)
    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor

    comments = executor._tool_list_task_comments({"task_id": task_id})
    assert comments[-1]["content"] == "Escribe a dev@ejemplo.com"
    masked = executor._tool_list_task_comments({"task_id": task_id, "mask_sensitive": True})
    assert "dev@ejemplo.com" not in masked[-1]["content"]

    task = executor._tool_get_task({"task_id": task_id})
    assert task["description"] == "Escribe a dev@ejemplo.com"
    assert all("<!DOCTYPE" not in log["content"] for log in task["logs"])

    schema = next(t for t in __import__("mcp_server").get_mcp_tools_schema() if t["name"] == "list_task_comments")
    assert "mask_sensitive" in schema["inputSchema"]["properties"]


def test_mcp_condensed_context_includes_latest_comment(db_path, mcp_board):
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    task_id = database.create_task(col, "T", db_path=db_path)
    database.add_task_log(task_id, "<p>Primera</p>", db_path=db_path)
    database.add_task_log(task_id, QT_HTML, db_path=db_path)
    executor = McpProtocolHandler(mcp_board, db_path=db_path).executor

    ctx = executor._tool_get_task_condensed_context({"task_id": task_id, "mask_sensitive": True})
    assert ctx["latest_comment"].startswith("Escribe a ") and "dev@ejemplo.com" not in ctx["latest_comment"]


def test_second_mcp_manager_cannot_bind_a_port_already_in_use(db_path):
    """#107: en Windows, SO_REUSEADDR dejaba que un segundo Ekin se enlazara al 8765 con el primero
    escuchando: las peticiones seguían yendo al primero y el segundo creía tener su MCP en marcha."""
    first, second = McpManager(db_path=db_path), McpManager(db_path=db_path)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    assert first.start(port=port) is True
    try:
        assert second.start(port=port) is False
        assert not second.is_running()
    finally:
        second.stop()
        first.stop()


def test_board_view_mcp_btn_shows_unavailable_when_server_is_not_running(qapp, db_path, mcp_board, monkeypatch):
    """#107: con el MCP activado en el tablero pero el servidor de este Ekin parado (el puerto lo
    tiene otro programa, p. ej. otro Ekin abierto), el botón ya no dice que el agente está conectado."""
    import board_mixins
    from board_view import BoardViewWidget
    from strings import t

    manager = SimpleNamespace(running=False, port=8765)
    manager.is_running = lambda: manager.running
    monkeypatch.setattr(board_mixins, "get_mcp_manager", lambda db_path=None: manager)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(mcp_board["id"])
    assert bv.mcp_btn.text() == t("mcp.board_btn_unavailable")
    assert "8765" in bv.mcp_btn.toolTip()

    manager.running = True
    bv._update_mcp_btn_ui()
    assert bv.mcp_btn.text() == t("mcp.board_btn_active")
    bv.deleteLater()


def test_mcp_text_with_a_tag_in_its_first_line_is_stored_escaped(db_path, mcp_board):
    """#112: create_task, update_task y add_task_comment guardaban sin filtrar el texto cuya
    primera línea parecía HTML; ahora pasa por el Markdown sin HTML embebido como el resto."""
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    text = "Nota <b>x</b> <img src=x>\n- a"

    created = executor._tool_create_task({"column_id": col, "title": "A", "description": text})["task_id"]
    updated = executor._tool_create_task({"column_id": col, "title": "B"})["task_id"]
    executor._tool_update_task({"task_id": updated, "description": text})
    executor._tool_add_task_comment({"task_id": created, "comment": text})

    stored = [database.get_task(created, db_path)["description"], database.get_task(updated, db_path)["description"],
              database.get_task_logs(created, db_path=db_path)[-1]["content"]]
    for html_text in stored:
        assert "<img" not in html_text and "&lt;b&gt;" in html_text


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _read_sse_event(stream, wanted):
    """Lee eventos SSE (líneas `event:` / `data:`) hasta el primero de tipo `wanted`; devuelve su data."""
    event = None
    while True:
        line = stream.readline().decode("utf-8").rstrip("\r\n")
        if line.startswith("event: "):
            event = line[len("event: "):]
        elif line.startswith("data: ") and event == wanted:
            return line[len("data: "):]


def test_mcp_sse_transport_routes_responses_to_the_stream_and_frees_the_session(db_path, mcp_board):
    """#121: Claude Code se registra por SSE, pero solo /health y /rpc tenían tests. El handshake
    da el endpoint con session_id, la respuesta a un POST /message llega por el stream y, al
    cerrar el cliente, la sesión se libera."""
    import http.client
    import time
    manager = McpManager(db_path=db_path)
    port = _free_port()
    assert manager.start(port=port) is True
    try:
        sse = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        sse.request("GET", f"/sse?board={mcp_board['board_uuid']}&token=secret123")
        stream = sse.getresponse()
        assert stream.status == 200 and stream.getheader("Content-Type") == "text/event-stream"
        endpoint = _read_sse_event(stream, "endpoint")
        assert endpoint.startswith("/message?session_id=")

        post = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        post.request("POST", endpoint, body=json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/list"}),
                     headers={"Content-Type": "application/json"})
        assert post.getresponse().status == 202
        message = json.loads(_read_sse_event(stream, "message"))
        assert message["id"] == 7 and "create_task" in {t["name"] for t in message["result"]["tools"]}

        stream.close()
        sse.close()
        deadline = time.monotonic() + 5
        while manager.server._sessions and time.monotonic() < deadline:
            time.sleep(0.05)
        assert manager.server._sessions == {}
    finally:
        manager.stop()


def test_mcp_cors_only_answers_local_origins(db_path, mcp_board):
    """#121: el preflight CORS devuelve Allow-Origin a orígenes localhost y a nadie más."""
    import http.client
    manager = McpManager(db_path=db_path)
    port = _free_port()
    assert manager.start(port=port) is True
    try:
        allowed = {}
        for origin in ("http://localhost:3000", "https://example.invalid"):
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            conn.request("OPTIONS", "/rpc", headers={"Origin": origin})
            allowed[origin] = conn.getresponse().getheader("Access-Control-Allow-Origin")
            conn.close()
        assert allowed == {"http://localhost:3000": "http://localhost:3000", "https://example.invalid": None}
    finally:
        manager.stop()


def test_mcp_link_tools_stay_inside_the_board(db_path, mcp_board):
    """#121: add_task_link / delete_task_link no salen del tablero enlazado. delete_task_link
    comprobaba la tarea pero borraba cualquier link_id, también uno de otro tablero."""
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    own_task = executor._tool_create_task({"column_id": col, "title": "Propia"})["task_id"]
    other_board = database.create_board("Ajeno", db_path=db_path)
    other_task = database.create_task(database.create_column(other_board, "C", db_path=db_path), "Ajena", db_path=db_path)
    other_link = database.add_task_link(other_task, "https://example.com/ajeno", db_path=db_path)

    link_id = executor._tool_add_task_link({"task_id": own_task, "url": "https://example.com/a", "label": "A"})["link_id"]
    assert [lk["id"] for lk in database.get_task_links(own_task, db_path=db_path)] == [link_id]
    with pytest.raises(McpSecurityError):
        executor._tool_add_task_link({"task_id": other_task, "url": "https://example.com/b"})
    with pytest.raises(McpSecurityError):
        executor._tool_delete_task_link({"task_id": own_task, "link_id": other_link})
    assert [lk["id"] for lk in database.get_task_links(other_task, db_path=db_path)] == [other_link]

    executor._tool_delete_task_link({"task_id": own_task, "link_id": link_id})
    assert database.get_task_links(own_task, db_path=db_path) == []


@pytest.mark.parametrize("bad", [{"due_date": "2026-10-16T10:00"}, {"due_date": "next week"},
                                 {"due_date": "2026-02-30"}, {"due_date": "2026-10-16", "due_time": "25:00"}])
def test_mcp_rejects_malformed_due_dates_without_changing_anything(db_path, mcp_board, bad):
    """#126: el MCP guardaba cualquier cadena como fecha u hora; la tarjeta no la mostraba, el
    calendario la colocaba en ningún día y Mi trabajo la clasificaba mal, sin avisar al agente."""
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    task_id = executor._tool_create_task({"column_id": col, "title": "T", "due_date": "2026-10-20"})["task_id"]
    before = len(database.get_tasks(col, db_path))

    with pytest.raises(ValueError):
        executor._tool_update_task({"task_id": task_id, **bad})
    if "due_time" not in bad:
        with pytest.raises(ValueError):
            executor._tool_create_task({"column_id": col, "title": "U", **bad})
        with pytest.raises(ValueError):
            executor._tool_create_tasks_batch({"column_id": col, "tasks": [{"title": "V"}, {"title": "W", **bad}]})

    assert database.get_task(task_id, db_path)["due_date"] == "2026-10-20"
    assert len(database.get_tasks(col, db_path)) == before


def test_mcp_accepts_valid_due_dates_and_empty_still_removes_them(db_path, mcp_board):
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    task_id = executor._tool_create_task({"column_id": col, "title": "T", "due_date": "2026-10-20"})["task_id"]
    executor._tool_update_task({"task_id": task_id, "due_date": "2026-10-21", "due_time": "09:30"})
    task = database.get_task(task_id, db_path)
    assert (task["due_date"], task["due_time"]) == ("2026-10-21", "09:30")
    executor._tool_update_task({"task_id": task_id, "due_date": ""})
    task = database.get_task(task_id, db_path)
    assert (task["due_date"], task["due_time"]) == (None, None)


def test_mcp_embedding_index_failure_is_logged_and_the_task_is_still_created(db_path, mcp_board, monkeypatch, caplog):
    """#128: si fallaba el índice semántico de una tarea creada por MCP no quedaba rastro."""
    import local_ai

    def fail(*_a, **_k):
        raise RuntimeError("índice bloqueado")

    monkeypatch.setattr(local_ai, "index_task_embedding", fail)
    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    with caplog.at_level("WARNING", logger="ekin.mcp"):
        task_id = executor._tool_create_task({"column_id": col, "title": "T"})["task_id"]
    assert database.get_task(task_id, db_path)
    assert any(r.exc_info and "índice bloqueado" in str(r.exc_info[1]) for r in caplog.records)


def test_enabling_mcp_with_an_empty_token_generates_one(qapp, db_path, monkeypatch):
    """#114: activar el MCP con el campo del token vacío lo dejaba abierto a cualquiera que
    conociera el UUID del tablero (que viaja en el .ekboard compartido). Al activarlo se genera
    uno; un tablero que ya lo tenía activo sin token conserva su configuración."""
    import mcp_sync_dialog
    manager = mcp_sync_dialog.get_mcp_manager(db_path)
    monkeypatch.setattr(manager, "start", lambda *a, **k: True)  # sin abrir el puerto real
    new_board = database.create_board("Nuevo", db_path=db_path)
    legacy = database.create_board("Abierto", db_path=db_path)
    database.set_board_mcp_config(legacy, enabled=True, secret=None, db_path=db_path)

    dlg = McpSyncDialog(new_board, db_path=db_path)
    dlg.enable_checkbox.setChecked(True)
    dlg.token_input.setText("")
    dlg._save_and_apply()
    secret = database.get_board(new_board, db_path=db_path)["mcp_secret"]
    assert secret and len(secret) == 32

    dlg = McpSyncDialog(legacy, db_path=db_path)
    dlg._save_and_apply()
    assert database.get_board(legacy, db_path=db_path)["mcp_secret"] is None


def test_mcp_server_drops_a_client_that_stalls_mid_request(db_path, mcp_board, monkeypatch):
    """#115: sin timeout de socket, un cliente que anuncia un cuerpo y no lo envía dejaba su hilo
    del servidor bloqueado para siempre en rfile.read."""
    import time
    from mcp_server import McpHttpHandler
    assert McpHttpHandler.timeout and McpHttpHandler.timeout <= 60
    monkeypatch.setattr(McpHttpHandler, "timeout", 0.5)
    manager = McpManager(db_path=db_path)
    port = _free_port()
    assert manager.start(port=port) is True
    try:
        stalled = socket.create_connection(("127.0.0.1", port), timeout=5)
        stalled.sendall(f"POST /rpc?board={mcp_board['board_uuid']}&token=secret123 HTTP/1.0\r\n"
                        "Content-Length: 100\r\n\r\n{".encode("ascii"))
        start = time.monotonic()
        while stalled.recv(1024):
            pass
        assert time.monotonic() - start < 4
        stalled.close()

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3.0) as resp:
            assert json.loads(resp.read())["status"] == "ok"
    finally:
        manager.stop()


def test_list_tasks_and_get_task_advertise_and_apply_masking(db_path, mcp_board):
    """#119: los dos enmascaraban si se les pedía, pero su esquema no declaraba mask_sensitive y
    los agentes no lo enviaban; las descripciones y diarios salían con los secretos."""
    from mcp_server import get_mcp_tools_schema
    schemas = {s["name"]: s["inputSchema"]["properties"] for s in get_mcp_tools_schema()}
    assert "mask_sensitive" in schemas["list_tasks"] and "mask_sensitive" in schemas["get_task"]

    executor = McpProtocolHandler(mcp_board, db_path=db_path, client_name="Claude Code").executor
    col = database.get_columns(mcp_board["id"], db_path=db_path)[0]["id"]
    secret = "gh" + "p_" + "F4k3" * 10  # falso, montado por partes
    task_id = executor._tool_create_task({"column_id": col, "title": "T", "description": f"token {secret}"})["task_id"]
    executor._tool_add_task_comment({"task_id": task_id, "comment": f"usa {secret}"})

    task = executor._tool_get_task({"task_id": task_id, "mask_sensitive": True})
    listed = executor._tool_list_tasks({"column_id": col, "mask_sensitive": True})
    texts = [task["description"], *(lg["content"] for lg in task["logs"]), *(t["description"] for t in listed)]
    assert all(secret not in text for text in texts)
    assert "[REDACTED_GITHUB_TOKEN]" in task["description"]
