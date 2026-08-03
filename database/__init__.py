import sqlite3
import contextlib

DB_NAME = "ekin_board.db"

@contextlib.contextmanager
def get_connection(db_path=None):
    """Establece una conexión a la base de datos, habilita las claves foráneas y la
    cierra siempre al salir (commit en éxito, rollback si hay excepción)."""
    db_path = db_path or DB_NAME
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db(db_path=None):
    """Crea las tablas necesarias si no existen."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Tabla de tableros (boards)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#3b82f6',
                archived INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migración: columnas 'color' y 'archived' en 'boards'
        cursor.execute("PRAGMA table_info(boards)")
        columns_info = [row[1] for row in cursor.fetchall()]
        if "color" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN color TEXT NOT NULL DEFAULT '#3b82f6'")
        if "archived" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN archived INTEGER NOT NULL DEFAULT 0")

        # Tabla de columnas (columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#3b82f6',
                position INTEGER NOT NULL,
                collapsed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """)

        # Migración: añadir 'collapsed' (columna plegada) a BD anteriores
        cursor.execute("PRAGMA table_info(columns)")
        columns_cols = [row[1] for row in cursor.fetchall()]
        if "collapsed" not in columns_cols:
            cursor.execute("ALTER TABLE columns ADD COLUMN collapsed INTEGER NOT NULL DEFAULT 0")

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

        # Migración: columnas 'due_date', 'due_time' y 'recurrence' en 'tasks'
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [row[1] for row in cursor.fetchall()]
        if "due_date" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "due_time" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_time TEXT")
        if "recurrence" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT NOT NULL DEFAULT 'none'")

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

        # Tablas para el sistema de etiquetas estructuradas (Categoría: Valor)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                value TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#6b7280',
                UNIQUE(category_id, value),
                FOREIGN KEY(category_id) REFERENCES tag_categories(id) ON DELETE CASCADE
            )
        """)

        # Ajustes de la aplicación (clave/valor): ruta de sincronización .ics, etc.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # Enlaces / adjuntos de una tarea (URL o ruta de archivo, con etiqueta opcional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                label TEXT,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)

        # Migración: enlazar task_tags con tag_values en vez de usar texto/color libres
        cursor.execute("PRAGMA table_info(task_tags)")
        task_tags_columns = [row[1] for row in cursor.fetchall()]
        if "tag_value_id" not in task_tags_columns:
            cursor.execute(
                "ALTER TABLE task_tags ADD COLUMN tag_value_id INTEGER REFERENCES tag_values(id) ON DELETE CASCADE"
            )

            # Migrar las etiquetas de texto libre ya existentes a una categoría "General"
            cursor.execute("SELECT id, task_id, text, color FROM task_tags WHERE tag_value_id IS NULL")
            legacy_rows = cursor.fetchall()
            if legacy_rows:
                cursor.execute("INSERT OR IGNORE INTO tag_categories (name) VALUES ('General')")
                cursor.execute("SELECT id FROM tag_categories WHERE name = 'General'")
                general_category_id = cursor.fetchone()[0]

                value_cache = {}
                for row in legacy_rows:
                    cache_key = (row["text"].strip().lower(), row["color"])
                    if cache_key not in value_cache:
                        cursor.execute(
                            "SELECT id FROM tag_values WHERE category_id = ? AND LOWER(value) = LOWER(?)",
                            (general_category_id, row["text"])
                        )
                        existing = cursor.fetchone()
                        if existing:
                            value_cache[cache_key] = existing["id"]
                        else:
                            cursor.execute(
                                "INSERT INTO tag_values (category_id, value, color) VALUES (?, ?, ?)",
                                (general_category_id, row["text"], row["color"])
                            )
                            value_cache[cache_key] = cursor.lastrowid
                    cursor.execute(
                        "UPDATE task_tags SET tag_value_id = ? WHERE id = ?",
                        (value_cache[cache_key], row["id"])
                    )

        # Rutas de sincronización .ics por tablero (feed auto-sync además del global)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS board_ics_sync (
                board_id INTEGER PRIMARY KEY,
                path TEXT NOT NULL,
                FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


# Re-exportar el API público de cada módulo de dominio, para que
# `database.xxx(...)` siga funcionando exactamente igual que antes del split.
from .boards import *  # noqa: E402,F401,F403
from .columns import *  # noqa: E402,F401,F403
from .tags import *  # noqa: E402,F401,F403
from .links import *  # noqa: E402,F401,F403
from .logs import *  # noqa: E402,F401,F403
from .settings import *  # noqa: E402,F401,F403
from .tasks import *  # noqa: E402,F401,F403
from .scheduling import *  # noqa: E402,F401,F403
from .search import *  # noqa: E402,F401,F403
from .ics_sync import *  # noqa: E402,F401,F403
from .board_ops import *  # noqa: E402,F401,F403
from .snapshots import *  # noqa: E402,F401,F403
