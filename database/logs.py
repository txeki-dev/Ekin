from . import get_connection

__all__ = ["create_log", "get_logs", "get_logs_bulk", "update_log", "delete_log"]

# --- OPERACIONES DE LOGS/DIARIO (TASK_LOGS) ---

def create_log(task_id, content, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO task_logs (task_id, content) VALUES (?, ?)",
            (task_id, content)
        )

        # También actualizamos la fecha de modificación de la tarea madre
        conn.execute(
            "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,)
        )
        return cursor.lastrowid

def get_logs(task_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_id, content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_logs_bulk(task_ids, db_path=None):
    """{task_id: [entradas de diario]} para varias tareas en UNA sola consulta (evita
    el patrón N+1 al exportar). Cada entrada tiene la misma forma que en get_logs."""
    result = {tid: [] for tid in task_ids}
    if not task_ids:
        return result
    placeholders = ",".join("?" * len(task_ids))
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT id, task_id, content, created_at FROM task_logs "
            f"WHERE task_id IN ({placeholders}) ORDER BY task_id ASC, id ASC",
            list(task_ids)
        )
        for row in cursor.fetchall():
            data = dict(row)
            task_id = data.pop("task_id")
            result.setdefault(task_id, []).append(data)
    return result

def update_log(log_id, content, db_path=None):
    """Edita el contenido (HTML) de una entrada del diario y refresca el updated_at de la tarea."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE task_logs SET content = ? WHERE id = ?", (content, log_id))
        conn.execute(
            "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP "
            "WHERE id = (SELECT task_id FROM task_logs WHERE id = ?)",
            (log_id,)
        )

def delete_log(log_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener el task_id antes de borrar para actualizar su updated_at
        cursor.execute("SELECT task_id FROM task_logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        task_id = row[0] if row else None

        cursor.execute("DELETE FROM task_logs WHERE id = ?", (log_id,))

        if task_id:
            conn.execute(
                "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (task_id,)
            )
