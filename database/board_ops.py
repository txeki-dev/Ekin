from . import get_connection

__all__ = ["move_column_to_board", "copy_column_to_board", "copy_board"]

# --- OPERACIONES AVANZADAS DE COLUMNAS (MOVER Y COPIAR A OTROS TABLEROS) ---

def move_column_to_board(column_id, target_board_id, db_path=None):
    """Mueve una columna a otro tablero y la coloca al final de su lista de columnas."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener la posición máxima actual en el tablero de destino
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (target_board_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1

        # Actualizar la columna con el nuevo board_id y posición
        cursor.execute(
            "UPDATE columns SET board_id = ?, position = ? WHERE id = ?",
            (target_board_id, next_pos, column_id)
        )
        conn.commit()

def copy_column_to_board(column_id, target_board_id, db_path=None):
    """Crea una copia de la columna en el tablero de destino, incluyendo todas sus tareas y logs."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Obtener detalles de la columna origen
        cursor.execute("SELECT name, color FROM columns WHERE id = ?", (column_id,))
        col_row = cursor.fetchone()
        if not col_row:
            return None
        col_name, col_color = col_row["name"], col_row["color"]

        # 2. Obtener la posición máxima en el tablero de destino
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (target_board_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1

        # 3. Insertar la nueva columna
        cursor.execute(
            "INSERT INTO columns (board_id, name, color, position) VALUES (?, ?, ?, ?)",
            (target_board_id, col_name, col_color, next_pos)
        )
        new_column_id = cursor.lastrowid

        # 4. Obtener todas las tareas de la columna de origen
        cursor.execute(
            """SELECT id, title, description, tag_text, tag_color, position, due_date
               FROM tasks WHERE column_id = ? ORDER BY position ASC""",
            (column_id,)
        )
        tasks = [dict(row) for row in cursor.fetchall()]

        # 5. Duplicar cada tarea, sus logs y etiquetas
        for task in tasks:
            old_task_id = task["id"]

            cursor.execute(
                """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position, due_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (new_column_id, task["title"], task["description"], task["tag_text"], task["tag_color"], task["position"], task["due_date"])
            )
            new_task_id = cursor.lastrowid

            # Duplicar etiquetas (enlazando a las mismas tag_values compartidas del catálogo)
            cursor.execute(
                "SELECT tag_value_id FROM task_tags WHERE task_id = ? AND tag_value_id IS NOT NULL",
                (old_task_id,)
            )
            tag_value_ids = [row["tag_value_id"] for row in cursor.fetchall()]
            for tag_value_id in tag_value_ids:
                cursor.execute(
                    "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                    (new_task_id, tag_value_id)
                )

            # Obtener logs de la tarea de origen
            cursor.execute(
                "SELECT content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
                (old_task_id,)
            )
            logs = [dict(row) for row in cursor.fetchall()]

            # Insertar los logs duplicando el contenido y la fecha original
            for log in logs:
                cursor.execute(
                    "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                    (new_task_id, log["content"], log["created_at"])
                )

        conn.commit()
        return new_column_id

def copy_board(board_id, new_name, new_color, db_path=None):
    """Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Crear el nuevo tablero
        cursor.execute("INSERT INTO boards (name, color) VALUES (?, ?)", (new_name, new_color))
        new_board_id = cursor.lastrowid

        # 2. Obtener todas las columnas del tablero de origen
        cursor.execute("SELECT id, name, color, position FROM columns WHERE board_id = ? ORDER BY position ASC", (board_id,))
        columns = [dict(row) for row in cursor.fetchall()]

        for col in columns:
            old_col_id = col["id"]

            # Crear nueva columna en el nuevo tablero
            cursor.execute(
                "INSERT INTO columns (board_id, name, color, position) VALUES (?, ?, ?, ?)",
                (new_board_id, col["name"], col["color"], col["position"])
            )
            new_col_id = cursor.lastrowid

            # 3. Obtener todas las tareas de la columna de origen
            cursor.execute(
                """SELECT id, title, description, tag_text, tag_color, position, due_date
                   FROM tasks WHERE column_id = ? ORDER BY position ASC""",
                (old_col_id,)
            )
            tasks = [dict(row) for row in cursor.fetchall()]

            for task in tasks:
                old_task_id = task["id"]

                # Crear nueva tarea
                cursor.execute(
                    """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position, due_date)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (new_col_id, task["title"], task["description"], task["tag_text"], task["tag_color"], task["position"], task["due_date"])
                )
                new_task_id = cursor.lastrowid

                # Duplicar etiquetas (enlazando a las mismas tag_values compartidas del catálogo)
                cursor.execute(
                    "SELECT tag_value_id FROM task_tags WHERE task_id = ? AND tag_value_id IS NOT NULL",
                    (old_task_id,)
                )
                tag_value_ids = [row["tag_value_id"] for row in cursor.fetchall()]
                for tag_value_id in tag_value_ids:
                    cursor.execute(
                        "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                        (new_task_id, tag_value_id)
                    )

                # 4. Obtener todos los logs de la tarea de origen
                cursor.execute(
                    "SELECT content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
                    (old_task_id,)
                )
                logs = [dict(row) for row in cursor.fetchall()]

                for log in logs:
                    cursor.execute(
                        "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                        (new_task_id, log["content"], log["created_at"])
                    )

        conn.commit()
        return new_board_id
