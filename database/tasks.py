import calendar as _cal
from datetime import datetime, date, timedelta
from . import get_connection
from .tags import get_task_tags, get_task_tags_bulk
from .links import get_task_links_bulk

__all__ = [
    "create_task", "get_tasks", "get_task", "update_task", "update_task_due_date",
    "set_task_due_time", "next_occurrence", "set_task_recurrence", "advance_recurrence",
    "advance_overdue_recurring", "update_task_position", "update_task_positions", "delete_task",
    "set_task_linked_board", "set_task_timer_started",
]  # get_task_board_id vive en scheduling.py (junto a get_scheduled_tasks)

# --- OPERACIONES DE TAREAS (TASKS) ---

def create_task(column_id, title, description="", tag_text="", tag_color="#6b7280", due_date=None, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener la posición máxima actual de tareas en esta columna
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1

        cursor.execute(
            """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position, due_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (column_id, title, description, tag_text, tag_color, next_pos, due_date)
        )
        return cursor.lastrowid

_TASK_SELECT_COLUMNS = """
    t.id, t.column_id, t.title, t.description, t.tag_text, t.tag_color, t.position,
    t.created_at, t.updated_at, t.due_date, t.due_time, t.recurrence, t.linked_board_id,
    t.timer_started_at,
    b.name AS linked_board_name, b.color AS linked_board_color
"""

def get_tasks(column_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT {_TASK_SELECT_COLUMNS} FROM tasks t
                LEFT JOIN boards b ON b.id = t.linked_board_id
                WHERE t.column_id = ? ORDER BY t.position ASC""",
            (column_id,)
        )
        tasks = [dict(row) for row in cursor.fetchall()]
    ids = [t["id"] for t in tasks]
    tags_by_task = get_task_tags_bulk(ids, db_path)
    links_by_task = get_task_links_bulk(ids, db_path)
    for t in tasks:
        t["tags"] = tags_by_task.get(t["id"], [])
        t["links"] = links_by_task.get(t["id"], [])
    return tasks

def get_task(task_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT {_TASK_SELECT_COLUMNS} FROM tasks t
                LEFT JOIN boards b ON b.id = t.linked_board_id
                WHERE t.id = ?""",
            (task_id,)
        )
        row = cursor.fetchone()
        if row:
            t = dict(row)
            t["tags"] = get_task_tags(t["id"], db_path)
            return t
        return None

def set_task_linked_board(task_id, board_id, db_path=None):
    """Vincula una tarea con otro tablero (o None para quitar el vínculo)."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET linked_board_id = ? WHERE id = ?", (board_id, task_id))

def set_task_timer_started(task_id, started_at, db_path=None):
    """Inicia (started_at = timestamp ISO de datetime.now()) o borra (started_at = None)
    el temporizador de una tarea."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET timer_started_at = ? WHERE id = ?", (started_at, task_id))

def update_task(task_id, title, description, tag_text, tag_color, due_date, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE tasks
               SET title = ?, description = ?, tag_text = ?, tag_color = ?, due_date = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, tag_text, tag_color, due_date, task_id)
        )

def update_task_due_date(task_id, due_date, db_path=None):
    """Actualiza solo la fecha de vencimiento de una tarea (usado por el arrastre en el calendario).
    `due_date` es una cadena 'YYYY-MM-DD' o None/'' para quitarla."""
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET due_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (due_date, task_id)
        )

def set_task_due_time(task_id, due_time, db_path=None):
    """Fija la hora de vencimiento ('HH:MM') de una tarea, o None para dejarla de día completo."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET due_time = ? WHERE id = ?", (due_time or None, task_id))

# --- RECURRENCIA DE TAREAS ---

def next_occurrence(date_str, recurrence):
    """Siguiente fecha ('YYYY-MM-DD') según la recurrencia (daily/weekly/monthly),
    o None si no aplica. Función pura (fácil de testear)."""
    if not date_str or recurrence in (None, "", "none"):
        return None
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    if recurrence == "daily":
        d = d + timedelta(days=1)
    elif recurrence == "weekly":
        d = d + timedelta(days=7)
    elif recurrence == "monthly":
        month = d.month + 1
        year = d.year + (1 if month > 12 else 0)
        month = month - 12 if month > 12 else month
        last_day = _cal.monthrange(year, month)[1]
        d = date(year, month, min(d.day, last_day))  # recorta si el mes es más corto
    else:
        return None
    return d.isoformat()

def set_task_recurrence(task_id, recurrence, db_path=None):
    """Fija la recurrencia de una tarea ('none'/'daily'/'weekly'/'monthly')."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET recurrence = ? WHERE id = ?", (recurrence or "none", task_id))

def advance_recurrence(task_id, db_path=None):
    """Avanza la fecha de vencimiento de una tarea recurrente a su siguiente ocurrencia.
    Devuelve la nueva fecha, o None si no es recurrente o no tiene fecha."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT due_date, recurrence FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        nxt = next_occurrence(row["due_date"], row["recurrence"])
        if nxt is None:
            return None
        conn.execute(
            "UPDATE tasks SET due_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (nxt, task_id)
        )
        return nxt

def advance_overdue_recurring(today_iso, db_path=None):
    """Adelanta las tareas recurrentes vencidas a su próxima ocurrencia >= hoy.
    Pensado para ejecutarse al arrancar. Devuelve cuántas tareas se adelantaron."""
    advanced = 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, due_date, recurrence FROM tasks "
            "WHERE recurrence IS NOT NULL AND recurrence != 'none' "
            "AND due_date IS NOT NULL AND due_date != '' AND due_date < ?",
            (today_iso,)
        )
        rows = cursor.fetchall()
        for row in rows:
            nxt = row["due_date"]
            guard = 0
            while nxt is not None and nxt < today_iso and guard < 3000:
                nxt = next_occurrence(nxt, row["recurrence"])
                guard += 1
            if nxt is not None and nxt != row["due_date"]:
                conn.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (nxt, row["id"]))
                advanced += 1
    return advanced

def update_task_position(task_id, new_column_id, new_position, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_column_id, new_position, task_id)
        )

def update_task_positions(task_positions, db_path=None):
    """Actualiza de golpe la columna y posición de varias tareas (para reordenación drag-and-drop).
    task_positions: lista de tuplas/diccionarios: (task_id, column_id, position)
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for task_id, col_id, pos in task_positions:
            cursor.execute(
                "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (col_id, pos, task_id)
            )

def delete_task(task_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
