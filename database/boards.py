from . import get_connection

__all__ = ["create_board", "get_boards", "get_board", "set_board_archived", "update_board", "delete_board"]

# --- OPERACIONES DE TABLEROS (BOARDS) ---

def create_board(name, color='#3b82f6', db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO boards (name, color) VALUES (?, ?)", (name, color))
        conn.commit()
        return cursor.lastrowid

def get_boards(db_path=None, include_archived=False):
    """Devuelve los tableros. Por defecto excluye los archivados."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT id, name, color, archived, created_at FROM boards"
        if not include_archived:
            query += " WHERE archived = 0"
        query += " ORDER BY id ASC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_board(board_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, color, archived, created_at FROM boards WHERE id = ?", (board_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def set_board_archived(board_id, archived, db_path=None):
    """Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra lateral."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET archived = ? WHERE id = ?", (1 if archived else 0, board_id))
        conn.commit()

def update_board(board_id, name, color, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET name = ?, color = ? WHERE id = ?", (name, color, board_id))
        conn.commit()

def delete_board(board_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        conn.commit()
