from .connection import get_connection
from .tags import get_task_tags_bulk

__all__ = ["search_tasks"]

# --- BÚSQUEDA GLOBAL DE TAREAS ---

def search_tasks(text="", board_id=None, tag_value_id=None, only_due=False, db_path=None):
    """Busca tareas en todos los tableros (o en uno) con filtros opcionales.

    - text: subcadena en el título o la descripción (sin distinguir mayúsculas).
    - board_id: limitar a un tablero.
    - tag_value_id: solo tareas que tengan esa etiqueta (Categoría: Valor).
    - only_due: solo tareas con fecha de vencimiento.
    Devuelve dicts enriquecidos con tablero, columna y etiquetas, ordenados por
    tablero y título. Cada elemento incluye board_id/board_name/board_color para
    poder saltar a la tarjeta desde los resultados."""
    query = [
        "SELECT DISTINCT t.id, t.title, t.description, t.due_date, t.due_time, t.recurrence,",
        "       t.timer_started_at, t.column_id, t.updated_at,",
        "       c.board_id AS board_id, b.name AS board_name, b.color AS board_color,",
        "       c.name AS column_name",
        "FROM tasks t",
        "JOIN columns c ON t.column_id = c.id",
        "JOIN boards b ON c.board_id = b.id",
    ]
    params = []
    if tag_value_id is not None:
        query.append("JOIN task_tags tt ON tt.task_id = t.id AND tt.tag_value_id = ?")
        params.append(tag_value_id)
    query.append("WHERE 1 = 1")
    if text:
        query.append("AND (t.title LIKE ? OR t.description LIKE ?)")
        like = f"%{text}%"
        params.extend([like, like])
    if board_id is not None:
        query.append("AND c.board_id = ?")
        params.append(board_id)
    if only_due:
        query.append("AND t.due_date IS NOT NULL AND t.due_date != ''")
    query.append("ORDER BY b.name ASC, t.title ASC")

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("\n".join(query), params)
        tasks = [dict(row) for row in cursor.fetchall()]
    tags_by_task = get_task_tags_bulk([t["id"] for t in tasks], db_path)
    for t in tasks:
        t["tags"] = tags_by_task.get(t["id"], [])
    return tasks
