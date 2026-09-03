from .connection import get_connection

__all__ = [
    "get_board_ics_sync_path", "set_board_ics_sync_path",
    "delete_board_ics_sync_path", "get_all_board_ics_sync_paths",
]

# --- RUTAS DE SINCRONIZACIÓN .ics POR TABLERO ---

def get_board_ics_sync_path(board_id, db_path=None):
    """Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM board_ics_sync WHERE board_id = ?", (board_id,))
        row = cursor.fetchone()
        return row["path"] if row else None

def set_board_ics_sync_path(board_id, path, db_path=None):
    """Crea o actualiza la ruta de auto-sync de un tablero."""
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO board_ics_sync (board_id, path) VALUES (?, ?) "
            "ON CONFLICT(board_id) DO UPDATE SET path = excluded.path",
            (board_id, path)
        )

def delete_board_ics_sync_path(board_id, db_path=None):
    """Desactiva la sincronización automática de un tablero."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM board_ics_sync WHERE board_id = ?", (board_id,))

def get_all_board_ics_sync_paths(db_path=None):
    """Devuelve {board_id: path} para todos los tableros con auto-sync configurado."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT board_id, path FROM board_ics_sync")
        return {row["board_id"]: row["path"] for row in cursor.fetchall()}
