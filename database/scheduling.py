from . import get_connection
from .tags import get_task_tags_bulk

__all__ = ["get_scheduled_tasks", "get_task_board_id"]

# --- CONSULTAS DE VENCIMIENTOS Y CALENDARIO ---

def get_scheduled_tasks(start_date=None, end_date=None, board_id=None, db_path=None):
    """Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.

    Filtros opcionales:
      - start_date / end_date: rango inclusivo en formato 'YYYY-MM-DD'.
      - board_id: limitar a un tablero concreto.
    Cada elemento incluye sus etiquetas. Ordenado por fecha, tablero y posición.
    """
    query = [
        "SELECT t.id, t.title, t.description, t.due_date, t.due_time, t.recurrence, t.column_id, t.updated_at,",
        "       c.board_id AS board_id, b.name AS board_name, b.color AS board_color",
        "FROM tasks t",
        "JOIN columns c ON t.column_id = c.id",
        "JOIN boards b ON c.board_id = b.id",
        "WHERE t.due_date IS NOT NULL AND t.due_date != ''",
    ]
    params = []
    if start_date is not None:
        query.append("AND t.due_date >= ?")
        params.append(start_date)
    if end_date is not None:
        query.append("AND t.due_date <= ?")
        params.append(end_date)
    if board_id is not None:
        query.append("AND c.board_id = ?")
        params.append(board_id)
    query.append("ORDER BY t.due_date ASC, b.name ASC, t.position ASC")

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("\n".join(query), params)
        tasks = [dict(row) for row in cursor.fetchall()]
    tags_by_task = get_task_tags_bulk([t["id"] for t in tasks], db_path)
    for t in tasks:
        t["tags"] = tags_by_task.get(t["id"], [])
    return tasks

def get_task_board_id(task_id, db_path=None):
    """Devuelve el board_id al que pertenece una tarea (o None si no existe)."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT c.board_id FROM tasks t
               JOIN columns c ON t.column_id = c.id
               WHERE t.id = ?""",
            (task_id,)
        )
        row = cursor.fetchone()
        return row["board_id"] if row else None
