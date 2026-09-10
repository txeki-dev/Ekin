import calendar as _cal
from datetime import datetime, date, timedelta
from typing import Optional
from .connection import get_connection
from .tags import get_task_tags, get_task_tags_bulk
from .links import get_task_links, get_task_links_bulk

__all__ = [
    "create_task", "create_tasks_batch", "get_tasks", "get_task", "update_task", "save_task_full",
    "update_task_due_date", "set_task_due_time", "next_occurrence", "set_task_recurrence",
    "advance_recurrence", "advance_overdue_recurring", "update_task_position", "update_task_positions",
    "delete_task", "set_task_linked_board", "set_task_timer_started",
]  # get_task_board_id vive en scheduling.py (junto a get_scheduled_tasks)

# --- OPERACIONES DE TAREAS (TASKS) ---

def create_task(column_id, title, description="", tag_text="", tag_color="#6b7280", due_date=None, db_path=None, task_uuid=None, version=1):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        import uuid
        t_uuid = task_uuid or str(uuid.uuid4())
        # Obtener la posición máxima actual de tareas en esta columna
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1

        cursor.execute(
            """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position, due_date, task_uuid, version)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (column_id, title, description, tag_text, tag_color, next_pos, due_date, t_uuid, version)
        )
        return cursor.lastrowid


def create_tasks_batch(tasks_data, db_path=None):
    """Crea múltiples tareas de forma atómica dentro de una única transacción SQLite.

    tasks_data: iterable de tuplas (column_id, title, description, [tag_text, tag_color, due_date, task_uuid, version])
                o diccionarios con claves equivalentes.
    Retorna la lista de IDs autogenerados de las tareas creadas.
    """
    if not tasks_data:
        return []
    import uuid
    created_ids = []
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        next_pos_by_col = {}

        for item in tasks_data:
            if isinstance(item, dict):
                col_id = item["column_id"]
                title = item["title"]
                desc = item.get("description", "")
                tag_text = item.get("tag_text", "")
                tag_color = item.get("tag_color", "#6b7280")
                due_date = item.get("due_date", None)
                t_uuid = item.get("task_uuid") or str(uuid.uuid4())
                ver = item.get("version", 1)
            else:
                col_id = item[0]
                title = item[1]
                desc = item[2] if len(item) > 2 else ""
                tag_text = item[3] if len(item) > 3 else ""
                tag_color = item[4] if len(item) > 4 else "#6b7280"
                due_date = item[5] if len(item) > 5 else None
                t_uuid = item[6] if len(item) > 6 and item[6] else str(uuid.uuid4())
                ver = item[7] if len(item) > 7 else 1

            if col_id not in next_pos_by_col:
                cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (col_id,))
                max_pos = cursor.fetchone()[0]
                next_pos_by_col[col_id] = max_pos + 1
            else:
                next_pos_by_col[col_id] += 1

            pos = next_pos_by_col[col_id]

            cursor.execute(
                """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position, due_date, task_uuid, version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (col_id, title, desc, tag_text, tag_color, pos, due_date, t_uuid, ver)
            )
            created_ids.append(cursor.lastrowid)

    return created_ids

_TASK_SELECT_COLUMNS = """
    t.id, t.column_id, t.title, t.description, t.tag_text, t.tag_color, t.position,
    t.created_at, t.updated_at, t.due_date, t.due_time, t.recurrence, t.linked_board_id,
    t.timer_started_at, t.task_uuid, t.version, t.synced_version,
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
            t["links"] = get_task_links(t["id"], db_path)
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
               SET title = ?, description = ?, tag_text = ?, tag_color = ?, due_date = ?,
                   version = version + 1, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, tag_text, tag_color, due_date, task_id)
        )

def save_task_full(
    task_id: int,
    title: str,
    description: str = "",
    due_date: Optional[str] = None,
    due_time: Optional[str] = None,
    tag_value_ids: Optional[list[int]] = None,
    recurrence: str = "none",
    linked_board_id: Optional[int] = None,
    tag_text: str = "",
    tag_color: str = "#6b7280",
    db_path: Optional[str] = None,
):
    """Guarda atómicamente todos los atributos de una tarea en una única transacción SQLite:
    título, descripción, fecha/hora de vencimiento, etiquetas, recurrencia y tablero vinculado.
    Incrementa la versión y actualiza updated_at exactamente una vez."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE tasks
               SET title = ?, description = ?, tag_text = ?, tag_color = ?,
                   due_date = ?, due_time = ?, recurrence = ?, linked_board_id = ?,
                   version = version + 1, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                title,
                description,
                tag_text,
                tag_color,
                due_date or None,
                due_time or None,
                recurrence or "none",
                linked_board_id,
                task_id,
            )
        )

        if tag_value_ids is not None:
            cursor.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
            for tag_val_id in tag_value_ids:
                cursor.execute(
                    "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                    (task_id, tag_val_id)
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
