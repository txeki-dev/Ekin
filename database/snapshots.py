from . import get_connection
from .tasks import get_task, get_tasks
from .logs import get_logs
from .links import get_task_links
from .boards import get_board, create_board, set_board_archived
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
        "tag_value_ids": [t["tag_value_id"] for t in task.get("tags", [])],
        "logs": [{"content": lg["content"], "created_at": lg["created_at"]}
                 for lg in get_logs(task_id, db_path)],
        "links": [{"url": lk["url"], "label": lk["label"]}
                  for lk in get_task_links(task_id, db_path)],
    }

def restore_task(snap, column_id=None, db_path=None):
    """Recrea una tarea a partir de un snapshot. Devuelve el nuevo id."""
    column_id = column_id if column_id is not None else snap["column_id"]
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO tasks (column_id, title, description, position, due_date, due_time, recurrence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (column_id, snap["title"], snap["description"], pos, snap.get("due_date"),
             snap.get("due_time"), snap.get("recurrence", "none"))
        )
        new_id = cursor.lastrowid
        for tvid in snap.get("tag_value_ids", []):
            cursor.execute(
                "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                (new_id, tvid))
        for lg in snap.get("logs", []):
            cursor.execute("INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                           (new_id, lg["content"], lg["created_at"]))
        for lk in snap.get("links", []):
            cursor.execute("INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, 0)",
                           (new_id, lk["url"], lk["label"]))
        conn.commit()
        return new_id

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

def restore_column(snap, board_id=None, db_path=None):
    board_id = board_id if board_id is not None else snap["board_id"]
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO columns (board_id, name, color, position, collapsed) VALUES (?, ?, ?, ?, ?)",
            (board_id, snap["name"], snap["color"], pos, snap.get("collapsed", 0)))
        new_col = cursor.lastrowid
        conn.commit()
    for task_snap in snap.get("tasks", []):
        if task_snap:
            restore_task(task_snap, column_id=new_col, db_path=db_path)
    return new_col

def snapshot_board(board_id, db_path=None):
    board = get_board(board_id, db_path)
    if not board:
        return None
    return {
        "name": board["name"], "color": board["color"], "archived": board.get("archived", 0),
        "columns": [snapshot_column(c["id"], db_path) for c in get_columns(board_id, db_path)],
    }

def restore_board(snap, db_path=None):
    new_board = create_board(snap["name"], snap["color"], db_path)
    if snap.get("archived"):
        set_board_archived(new_board, True, db_path)
    for col_snap in snap.get("columns", []):
        if col_snap:
            restore_column(col_snap, board_id=new_board, db_path=db_path)
    return new_board
