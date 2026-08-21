from . import get_connection
from .tasks import get_task, get_tasks
from .logs import get_logs
from .links import get_task_links
from .boards import get_board
from .columns import get_columns

__all__ = [
    "snapshot_task", "restore_task", "snapshot_column", "restore_column",
    "snapshot_board", "restore_board",
]

# --- SNAPSHOT / RESTORE (para deshacer borrados) ---

def snapshot_task(task_id, db_path=None):
    """Captura todo el contenido de una tarea para poder recrearla (deshacer)."""
    task = get_task(task_id, db_path)
    if not task:
        return None
    return {
        "column_id": task["column_id"], "title": task["title"],
        "description": task["description"], "position": task["position"],
        "due_date": task.get("due_date"), "due_time": task.get("due_time"),
        "recurrence": task.get("recurrence", "none"),
        "linked_board_id": task.get("linked_board_id"),
        "timer_started_at": task.get("timer_started_at"),
        "tag_value_ids": [t["tag_value_id"] for t in task.get("tags", [])],
        "logs": [{"content": lg["content"], "created_at": lg["created_at"]}
                 for lg in get_logs(task_id, db_path)],
        "links": [{"url": lk["url"], "label": lk["label"], "position": lk["position"]}
                  for lk in get_task_links(task_id, db_path)],
    }


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
    cur.execute(
        "INSERT INTO tasks (column_id, title, description, position, due_date, due_time, "
        "recurrence, linked_board_id, timer_started_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (column_id, snap["title"], snap["description"], pos, snap.get("due_date"),
         snap.get("due_time"), snap.get("recurrence", "none"), linked_board_id,
         snap.get("timer_started_at"))
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


def snapshot_column(column_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT board_id, name, color, position, collapsed FROM columns WHERE id = ?", (column_id,))
        row = cursor.fetchone()
    if not row:
        return None
    snap = dict(row)
    snap["tasks"] = [snapshot_task(t["id"], db_path) for t in get_tasks(column_id, db_path)]
    return snap


def _restore_column_in_conn(snap, board_id, conn):
    cur = conn.cursor()
    # Si el tablero de destino ya no existe, no hay dónde insertar la columna -- devolver None
    cur.execute("SELECT id FROM boards WHERE id = ?", (board_id,))
    if cur.fetchone() is None:
        return None
    cur.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
    pos = cur.fetchone()[0] + 1
    cur.execute(
        "INSERT INTO columns (board_id, name, color, position, collapsed) VALUES (?, ?, ?, ?, ?)",
        (board_id, snap["name"], snap["color"], pos, snap.get("collapsed", 0)))
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


def snapshot_board(board_id, db_path=None):
    board = get_board(board_id, db_path)
    if not board:
        return None
    return {
        "name": board["name"], "color": board["color"], "archived": board.get("archived", 0),
        "columns": [snapshot_column(c["id"], db_path) for c in get_columns(board_id, db_path)],
    }


def _restore_board_in_conn(snap, conn):
    cur = conn.cursor()
    cur.execute("INSERT INTO boards (name, color, archived) VALUES (?, ?, ?)",
                (snap["name"], snap["color"], 1 if snap.get("archived") else 0))
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
