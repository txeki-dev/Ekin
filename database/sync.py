from .connection import get_connection

__all__ = [
    "set_board_sync_path",
    "get_board_sync_info",
    "update_board_sync_state",
    "unlink_board_sync",
    "get_synced_boards",
    "get_board_by_uuid",
    "get_board_last_local_modified",
    "mark_board_tasks_synced",
]


def set_board_sync_path(board_id, sync_path, db_path=None):
    """Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta compartida).
    Asegura que el tablero tenga un board_uuid asignado."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT board_uuid FROM boards WHERE id = ?", (board_id,))
        row = cursor.fetchone()
        import uuid
        b_uuid = row["board_uuid"] if row and row["board_uuid"] else str(uuid.uuid4())
        cursor.execute(
            "UPDATE boards SET sync_path = ?, board_uuid = ? WHERE id = ?",
            (sync_path, b_uuid, board_id)
        )


def get_board_sync_info(board_id, db_path=None):
    """Devuelve la información de sincronización de un tablero."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, sync_path, last_synced_at, sync_hash, board_uuid FROM boards WHERE id = ?",
            (board_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_board_sync_state(board_id, last_synced_at, sync_hash, db_path=None):
    """Actualiza la marca de tiempo de sincronización y el hash del archivo."""
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE boards SET last_synced_at = ?, sync_hash = ? WHERE id = ?",
            (last_synced_at, sync_hash, board_id)
        )


def unlink_board_sync(board_id, db_path=None):
    """Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline."""
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE boards SET sync_path = NULL, last_synced_at = NULL, sync_hash = NULL WHERE id = ?",
            (board_id,)
        )


def get_synced_boards(db_path=None):
    """Devuelve todos los tableros que tienen una ruta de sincronización activa."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, color, sync_path, last_synced_at, sync_hash, board_uuid FROM boards WHERE sync_path IS NOT NULL AND sync_path != ''"
        )
        return [dict(row) for row in cursor.fetchall()]


def get_board_by_uuid(board_uuid, db_path=None):
    """Busca un tablero local por su UUID."""
    if not board_uuid:
        return None
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, color, archived, sync_path, last_synced_at, sync_hash, board_uuid FROM boards WHERE board_uuid = ?",
            (board_uuid,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_board_last_local_modified(board_id, db_path=None):
    """Devuelve la fecha máxima de actualización local de las tareas de un tablero."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT MAX(t.updated_at)
               FROM tasks t
               JOIN columns c ON c.id = t.column_id
               WHERE c.board_id = ?""",
            (board_id,)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else None


def mark_board_tasks_synced(board_id, db_path=None):
    """Marca todas las tareas del tablero como sincronizadas con el archivo compartido,
    igualando synced_version = version."""
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE tasks
               SET synced_version = version
               WHERE column_id IN (SELECT id FROM columns WHERE board_id = ?)""",
            (board_id,)
        )

