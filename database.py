import sqlite3
import os
from datetime import datetime

DB_NAME = "ekin_board.db"

def get_connection(db_path=DB_NAME):
    """Establece una conexión a la base de datos y habilita las claves foráneas."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def init_db(db_path=DB_NAME):
    """Crea las tablas necesarias si no existen."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Tabla de tableros (boards)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#3b82f6',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migración: Verificar si la columna 'color' existe en 'boards'
        cursor.execute("PRAGMA table_info(boards)")
        columns_info = [row[1] for row in cursor.fetchall()]
        if "color" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN color TEXT NOT NULL DEFAULT '#3b82f6'")
        
        # Tabla de columnas (columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#3b82f6',
                position INTEGER NOT NULL,
                FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de tareas (tasks)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                column_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                tag_text TEXT,
                tag_color TEXT DEFAULT '#6b7280',
                position INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(column_id) REFERENCES columns(id) ON DELETE CASCADE
            )
        """)
        
        # Migración: Verificar si la columna 'due_date' existe en 'tasks'
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [row[1] for row in cursor.fetchall()]
        if "due_date" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        
        # Tabla de logs/diario (task_logs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Migración/Creación: Tabla para múltiples etiquetas (task_tags)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_tags';")
        table_exists = cursor.fetchone()
        if not table_exists:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    color TEXT NOT NULL DEFAULT '#6b7280',
                    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            # Migrar tags antiguos individuales a la nueva tabla
            cursor.execute("SELECT id, tag_text, tag_color FROM tasks WHERE tag_text IS NOT NULL AND tag_text != '';")
            rows = cursor.fetchall()
            for row in rows:
                cursor.execute(
                    "INSERT INTO task_tags (task_id, text, color) VALUES (?, ?, ?)",
                    (row["id"], row["tag_text"], row["tag_color"])
                )
        conn.commit()

# --- OPERACIONES DE TABLEROS (BOARDS) ---

def create_board(name, color='#3b82f6', db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO boards (name, color) VALUES (?, ?)", (name, color))
        conn.commit()
        return cursor.lastrowid

def get_boards(db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, color, created_at FROM boards ORDER BY id ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_board(board_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, color, created_at FROM boards WHERE id = ?", (board_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_board(board_id, name, color, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET name = ?, color = ? WHERE id = ?", (name, color, board_id))
        conn.commit()

def delete_board(board_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        conn.commit()

# --- OPERACIONES DE COLUMNAS (COLUMNS) ---

def create_column(board_id, name, color='#3b82f6', db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener la posición máxima actual para colocar la nueva columna al final
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1
        
        cursor.execute(
            "INSERT INTO columns (board_id, name, color, position) VALUES (?, ?, ?, ?)",
            (board_id, name, color, next_pos)
        )
        conn.commit()
        return cursor.lastrowid

def get_columns(board_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, board_id, name, color, position FROM columns WHERE board_id = ? ORDER BY position ASC",
            (board_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def update_column(column_id, name, color, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE columns SET name = ?, color = ? WHERE id = ?",
            (name, color, column_id)
        )
        conn.commit()

def update_column_positions(column_positions, db_path=DB_NAME):
    """Actualiza las posiciones de múltiples columnas.
    column_positions debe ser una lista de tuplas/diccionarios: (column_id, position)
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for col_id, pos in column_positions:
            cursor.execute("UPDATE columns SET position = ? WHERE id = ?", (pos, col_id))
        conn.commit()

def delete_column(column_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))
        conn.commit()

# --- OPERACIONES DE TAREAS (TASKS) ---

def create_task(column_id, title, description="", tag_text="", tag_color="#6b7280", due_date=None, db_path=DB_NAME):
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
        conn.commit()
        return cursor.lastrowid

def get_tasks(column_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at, due_date
               FROM tasks WHERE column_id = ? ORDER BY position ASC""",
            (column_id,)
        )
        tasks = [dict(row) for row in cursor.fetchall()]
        for t in tasks:
            cursor.execute("SELECT text, color FROM task_tags WHERE task_id = ? ORDER BY id ASC", (t["id"],))
            t["tags"] = [dict(r) for r in cursor.fetchall()]
        return tasks

def get_task(task_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at, due_date
               FROM tasks WHERE id = ?""",
            (task_id,)
        )
        row = cursor.fetchone()
        if row:
            t = dict(row)
            cursor.execute("SELECT text, color FROM task_tags WHERE task_id = ? ORDER BY id ASC", (t["id"],))
            t["tags"] = [dict(r) for r in cursor.fetchall()]
            return t
        return None

def update_task(task_id, title, description, tag_text, tag_color, due_date, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE tasks 
               SET title = ?, description = ?, tag_text = ?, tag_color = ?, due_date = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, tag_text, tag_color, due_date, task_id)
        )
        conn.commit()

def get_task_tags(task_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, text, color FROM task_tags WHERE task_id = ? ORDER BY id ASC", (task_id,))
        return [dict(row) for row in cursor.fetchall()]

def set_task_tags(task_id, tags_list, db_path=DB_NAME):
    """Establece las etiquetas para una tarea, eliminando las anteriores."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
        for tag in tags_list:
            conn.execute(
                "INSERT INTO task_tags (task_id, text, color) VALUES (?, ?, ?)",
                (task_id, tag["text"], tag["color"])
            )
        conn.commit()

def update_task_position(task_id, new_column_id, new_position, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_column_id, new_position, task_id)
        )
        conn.commit()

def update_task_positions(task_positions, db_path=DB_NAME):
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
        conn.commit()

def delete_task(task_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

# --- OPERACIONES DE LOGS/DIARIO (TASK_LOGS) ---

def create_log(task_id, content, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO task_logs (task_id, content) VALUES (?, ?)",
            (task_id, content)
        )
        conn.commit()
        
        # También actualizamos la fecha de modificación de la tarea madre
        conn.execute(
            "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,)
        )
        conn.commit()
        return cursor.lastrowid

def get_logs(task_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_id, content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def delete_log(log_id, db_path=DB_NAME):
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
        conn.commit()

# --- OPERACIONES AVANZADAS DE COLUMNAS (MOVER Y COPIAR A OTROS TABLEROS) ---

def move_column_to_board(column_id, target_board_id, db_path=DB_NAME):
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

def copy_column_to_board(column_id, target_board_id, db_path=DB_NAME):
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
            
            # Duplicar etiquetas
            cursor.execute("SELECT text, color FROM task_tags WHERE task_id = ?", (old_task_id,))
            tags = [dict(row) for row in cursor.fetchall()]
            for tag in tags:
                cursor.execute(
                    "INSERT INTO task_tags (task_id, text, color) VALUES (?, ?, ?)",
                    (new_task_id, tag["text"], tag["color"])
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

def copy_board(board_id, new_name, new_color, db_path=DB_NAME):
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
                
                # Duplicar etiquetas
                cursor.execute("SELECT text, color FROM task_tags WHERE task_id = ?", (old_task_id,))
                tags = [dict(row) for row in cursor.fetchall()]
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO task_tags (task_id, text, color) VALUES (?, ?, ?)",
                        (new_task_id, tag["text"], tag["color"])
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
