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

def create_task(column_id, title, description="", tag_text="", tag_color="#6b7280", db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener la posición máxima actual de tareas en esta columna
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1
        
        cursor.execute(
            """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (column_id, title, description, tag_text, tag_color, next_pos)
        )
        conn.commit()
        return cursor.lastrowid

def get_tasks(column_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at
               FROM tasks WHERE column_id = ? ORDER BY position ASC""",
            (column_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_task(task_id, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at
               FROM tasks WHERE id = ?""",
            (task_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def update_task(task_id, title, description, tag_text, tag_color, db_path=DB_NAME):
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE tasks 
               SET title = ?, description = ?, tag_text = ?, tag_color = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, tag_text, tag_color, task_id)
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
