"""
Módulo de snapshots y restauración para acciones Deshacer / Rehacer (Undo/Redo).
Preserva la identidad global (UUIDs) de tareas, columnas y tableros para
no romper la sincronización con OneDrive (.ekboard).
"""

import uuid
from .connection import get_connection

__all__ = [
    "snapshot_task", "restore_task", "snapshot_column", "restore_column",
    "snapshot_board", "restore_board",
]


# --- SNAPSHOT / RESTORE (para deshacer borrados) ---

def _snapshot_task_in_conn(task_id, conn):
    cur = conn.cursor()
    cur.execute(
        """SELECT column_id, title, description, position, due_date, due_time,
                  recurrence, linked_board_id, timer_started_at, task_uuid
           FROM tasks WHERE id = ?""",
        (task_id,)
    )
    row = cur.fetchone()
    if not row:
        return None
    task = dict(row)

    cur.execute(
        "SELECT tag_value_id FROM task_tags WHERE task_id = ? AND tag_value_id IS NOT NULL",
        (task_id,)
    )
    tag_value_ids = [r[0] for r in cur.fetchall()]

    cur.execute(
        "SELECT content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
        (task_id,)
    )
    logs = [{"content": r[0], "created_at": r[1]} for r in cur.fetchall()]

    cur.execute(
        "SELECT url, label, position FROM task_links WHERE task_id = ? ORDER BY position ASC",
        (task_id,)
    )
    links = [{"url": r[0], "label": r[1], "position": r[2]} for r in cur.fetchall()]

    return {
        "column_id": task["column_id"],
        "title": task["title"],
        "description": task["description"],
        "position": task["position"],
        "due_date": task.get("due_date"),
        "due_time": task.get("due_time"),
        "recurrence": task.get("recurrence", "none") or "none",
        "linked_board_id": task.get("linked_board_id"),
        "timer_started_at": task.get("timer_started_at"),
        "task_uuid": task.get("task_uuid"),
        "tag_value_ids": tag_value_ids,
        "logs": logs,
        "links": links,
    }


def snapshot_task(task_id, db_path=None, conn=None):
    """Captura todo el contenido de una tarea para poder recrearla (deshacer),
    incluyendo su identidad global (task_uuid) para mantener compatibilidad con sincronización."""
    if conn is not None:
        return _snapshot_task_in_conn(task_id, conn)
    with get_connection(db_path) as c:
        return _snapshot_task_in_conn(task_id, c)


def _restore_task_in_conn(snap, column_id, conn):
    cur = conn.cursor()
    # Si la columna de destino ya no existe (p. ej. se borró mientras esta acción seguía
    # pendiente en la pila de deshacer), no hay dónde insertar la tarea -- devolver None en
    # vez de violar la FK de tasks.column_id y reventar sin capturar.
    cur.execute("SELECT id FROM columns WHERE id = ?", (column_id,))
    if cur.fetchone() is None:
        return None
    # Si el tablero enlazado ya no existe (se borró mientras tanto), no lo restauramos:
    # violaría la clave foránea en vez de simplemente perder el vínculo.
    linked_board_id = snap.get("linked_board_id")
    if linked_board_id is not None:
        cur.execute("SELECT id FROM boards WHERE id = ?", (linked_board_id,))
        if cur.fetchone() is None:
            linked_board_id = None
    # Mismo razonamiento para las etiquetas: si una tag_value del catálogo se borró
    # mientras tanto, insertar su id violaría la FK de task_tags (ON DELETE CASCADE,
    # PRAGMA foreign keys = ON).
    tag_value_ids = []
    for tvid in snap.get("tag_value_ids", []):
        cur.execute("SELECT id FROM tag_values WHERE id = ?", (tvid,))
        if cur.fetchone() is not None:
            tag_value_ids.append(tvid)

    cur.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
    pos = cur.fetchone()[0] + 1
    t_uuid = snap.get("task_uuid") or str(uuid.uuid4())
    cur.execute(
        "INSERT INTO tasks (column_id, title, description, position, due_date, due_time, "
        "recurrence, linked_board_id, timer_started_at, task_uuid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (column_id, snap["title"], snap["description"], pos, snap.get("due_date"),
         snap.get("due_time"), snap.get("recurrence", "none"), linked_board_id,
         snap.get("timer_started_at"), t_uuid)
    )
    new_id = cur.lastrowid
    for tvid in tag_value_ids:
        cur.execute(
            "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
            (new_id, tvid))
    for lg in snap.get("logs", []):
        cur.execute("INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                    (new_id, lg["content"], lg["created_at"]))
    for lk in snap.get("links", []):
        cur.execute("INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
                    (new_id, lk["url"], lk["label"], lk["position"]))
    return new_id


def restore_task(snap, column_id=None, db_path=None, conn=None):
    """Recrea una tarea a partir de un snapshot. Devuelve el nuevo id."""
    column_id = column_id if column_id is not None else snap["column_id"]
    if conn is not None:
        return _restore_task_in_conn(snap, column_id, conn)
    with get_connection(db_path) as c:
        return _restore_task_in_conn(snap, column_id, c)


def _snapshot_column_in_conn(column_id, conn):
    cur = conn.cursor()
    cur.execute("SELECT board_id, name, color, position, collapsed, column_uuid FROM columns WHERE id = ?", (column_id,))
    row = cur.fetchone()
    if not row:
        return None
    snap = dict(row)
    cur.execute("SELECT id FROM tasks WHERE column_id = ? ORDER BY position ASC", (column_id,))
    task_ids = [r[0] for r in cur.fetchall()]
    snap["tasks"] = [_snapshot_task_in_conn(tid, conn) for tid in task_ids]
    return snap


def snapshot_column(column_id, db_path=None, conn=None):
    if conn is not None:
        return _snapshot_column_in_conn(column_id, conn)
    with get_connection(db_path) as conn_ctx:
        return _snapshot_column_in_conn(column_id, conn_ctx)


def _restore_column_in_conn(snap, board_id, conn):
    cur = conn.cursor()
    # Si el tablero de destino ya no existe, no hay dónde insertar la columna -- devolver None
    cur.execute("SELECT id FROM boards WHERE id = ?", (board_id,))
    if cur.fetchone() is None:
        return None
    cur.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
    pos = cur.fetchone()[0] + 1
    c_uuid = snap.get("column_uuid") or str(uuid.uuid4())
    cur.execute(
        "INSERT INTO columns (board_id, name, color, position, collapsed, column_uuid) VALUES (?, ?, ?, ?, ?, ?)",
        (board_id, snap["name"], snap["color"], pos, snap.get("collapsed", 0), c_uuid))
    new_col = cur.lastrowid
    for task_snap in snap.get("tasks", []):
        if task_snap:
            _restore_task_in_conn(task_snap, new_col, conn)
    return new_col


def restore_column(snap, board_id=None, db_path=None, conn=None):
    board_id = board_id if board_id is not None else snap["board_id"]
    if conn is not None:
        return _restore_column_in_conn(snap, board_id, conn)
    with get_connection(db_path) as c:
        return _restore_column_in_conn(snap, board_id, c)


def _snapshot_board_in_conn(board_id, conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name, color, archived, board_uuid, sync_path FROM boards WHERE id = ?", (board_id,))
    row = cur.fetchone()
    if not row:
        return None
    board = dict(row)
    cur.execute("SELECT id FROM columns WHERE board_id = ? ORDER BY position ASC", (board_id,))
    col_ids = [r[0] for r in cur.fetchall()]
    return {
        "name": board["name"],
        "color": board["color"],
        "archived": board.get("archived", 0),
        "board_uuid": board.get("board_uuid"),
        "sync_path": board.get("sync_path"),
        "columns": [_snapshot_column_in_conn(cid, conn) for cid in col_ids],
    }


def snapshot_board(board_id, db_path=None, conn=None):
    if conn is not None:
        return _snapshot_board_in_conn(board_id, conn)
    with get_connection(db_path) as c:
        return _snapshot_board_in_conn(board_id, c)


def _restore_board_in_conn(snap, conn):
    cur = conn.cursor()
    b_uuid = snap.get("board_uuid") or str(uuid.uuid4())
    sync_path = snap.get("sync_path")
    cur.execute("INSERT INTO boards (name, color, archived, board_uuid, sync_path) VALUES (?, ?, ?, ?, ?)",
                (snap["name"], snap["color"], 1 if snap.get("archived") else 0, b_uuid, sync_path))
    new_board = cur.lastrowid
    for col_snap in snap.get("columns", []):
        if col_snap:
            _restore_column_in_conn(col_snap, new_board, conn)
    return new_board


def restore_board(snap, db_path=None, conn=None):
    if conn is not None:
        return _restore_board_in_conn(snap, conn)
    with get_connection(db_path) as c:
        return _restore_board_in_conn(snap, c)
