import uuid
from .connection import get_connection

__all__ = [
    "create_board",
    "get_boards",
    "get_board",
    "get_board_by_uuid",
    "set_board_archived",
    "update_board",
    "delete_board",
    "set_board_mcp_config",
    "get_board_mutation_fingerprint",
]

# --- OPERACIONES DE TABLEROS (BOARDS) ---

def create_board(name, color="#3b82f6", db_path=None, board_uuid=None, ai_system_prompt=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        b_uuid = board_uuid or str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO boards (name, color, board_uuid, ai_system_prompt)
               VALUES (?, ?, ?, ?)""",
            (name, color, b_uuid, ai_system_prompt),
        )
        return cursor.lastrowid

def get_boards(db_path=None, include_archived=False):
    """Devuelve los tableros. Por defecto excluye los archivados."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = (
            "SELECT id, name, color, archived, created_at, sync_path, last_synced_at, "
            "sync_hash, board_uuid, mcp_enabled, mcp_secret, ai_system_prompt FROM boards"
        )
        if not include_archived:
            query += " WHERE archived = 0"
        query += " ORDER BY id ASC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_board(board_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, color, archived, created_at, sync_path, last_synced_at,
                      sync_hash, board_uuid, mcp_enabled, mcp_secret, ai_system_prompt
               FROM boards WHERE id = ?""",
            (board_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_board_by_uuid(board_uuid, db_path=None):
    """Busca un tablero por su UUID único."""
    if not board_uuid:
        return None
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, color, archived, created_at, sync_path, last_synced_at,
                      sync_hash, board_uuid, mcp_enabled, mcp_secret, ai_system_prompt
               FROM boards WHERE board_uuid = ?""",
            (board_uuid,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def set_board_archived(board_id, archived, db_path=None):
    """Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra lateral."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET archived = ? WHERE id = ?", (1 if archived else 0, board_id))

def update_board(board_id, name, color, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET name = ?, color = ? WHERE id = ?", (name, color, board_id))

def set_board_mcp_config(board_id, enabled, secret=None, ai_system_prompt=None, db_path=None):
    """Configura el estado de activación, token secreto y prompt de IA para el tablero."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if secret is not None and ai_system_prompt is not None:
            cursor.execute(
                "UPDATE boards SET mcp_enabled = ?, mcp_secret = ?, ai_system_prompt = ? WHERE id = ?",
                (1 if enabled else 0, secret, ai_system_prompt, board_id),
            )
        elif secret is not None:
            cursor.execute(
                "UPDATE boards SET mcp_enabled = ?, mcp_secret = ? WHERE id = ?",
                (1 if enabled else 0, secret, board_id),
            )
        elif ai_system_prompt is not None:
            cursor.execute(
                "UPDATE boards SET mcp_enabled = ?, ai_system_prompt = ? WHERE id = ?",
                (1 if enabled else 0, ai_system_prompt, board_id),
            )
        else:
            cursor.execute(
                "UPDATE boards SET mcp_enabled = ? WHERE id = ?",
                (1 if enabled else 0, board_id),
            )

def delete_board(board_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))


def get_board_mutation_fingerprint(board_id, db_path=None) -> tuple:
    """Calcula una huella digital determinista y ultrarrápida del estado de un tablero
    (tareas, columnas, diario, temporizadores y metadatos) para detección en tiempo real
    de mutaciones externas realizadas por agentes MCP o procesos paralelos.
    """
    if not board_id or board_id == -1:
        return ()
    with get_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT 
                COUNT(tasks.id), 
                COALESCE(MAX(tasks.updated_at), ''), 
                TOTAL(tasks.position), 
                TOTAL(tasks.column_id),
                TOTAL(tasks.timer_started_at IS NOT NULL),
                (SELECT COUNT(*) FROM columns WHERE board_id = ?),
                (SELECT TOTAL(position) FROM columns WHERE board_id = ?),
                (SELECT TOTAL(collapsed) FROM columns WHERE board_id = ?),
                (SELECT name || '|' || color FROM boards WHERE id = ?)
            FROM tasks 
            JOIN columns ON tasks.column_id = columns.id 
            WHERE columns.board_id = ?
            """,
            (board_id, board_id, board_id, board_id, board_id)
        ).fetchone()
        return tuple(row) if row else ()

