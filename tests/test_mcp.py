"""
Pruebas automatizadas para el Servidor MCP (Model Context Protocol),
seguridad de sandbox, bloqueo de columnas y herramientas de manipulación de tareas.
"""

import json
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
    test_port = 8789
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
