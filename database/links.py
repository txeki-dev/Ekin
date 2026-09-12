from .connection import get_connection

__all__ = ["add_task_link", "get_task_links", "delete_task_link", "get_task_links_bulk"]

# --- ENLACES / ADJUNTOS DE TAREAS ---

def add_task_link(task_id, url, label=None, db_path=None):
    """Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM task_links WHERE task_id = ?", (task_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
            (task_id, url, label or None, pos)
        )
        return cursor.lastrowid

def get_task_links(task_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_id, url, label, position FROM task_links WHERE task_id = ? ORDER BY position ASC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def delete_task_link(link_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM task_links WHERE id = ?", (link_id,))

def get_task_links_bulk(task_ids, db_path=None, chunk_size=500):
    """{task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el límite SQL de SQLite)."""
    result = {tid: [] for tid in task_ids}
    id_list = list(task_ids)
    if not id_list:
        return result
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for i in range(0, len(id_list), chunk_size):
            chunk = id_list[i:i + chunk_size]
            placeholders = ",".join("?" * len(chunk))
            cursor.execute(
                f"SELECT id, task_id, url, label, position FROM task_links "
                f"WHERE task_id IN ({placeholders}) ORDER BY task_id ASC, position ASC",
                chunk
            )
            for row in cursor.fetchall():
                d = dict(row)
                result.setdefault(d["task_id"], []).append(d)
    return result
