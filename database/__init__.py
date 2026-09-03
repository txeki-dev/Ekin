from .connection import DB_NAME, get_connection


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
        if "sync_path" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN sync_path TEXT DEFAULT NULL")
        if "last_synced_at" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN last_synced_at TEXT DEFAULT NULL")
        if "sync_hash" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN sync_hash TEXT DEFAULT NULL")
        if "board_uuid" not in columns_info:
            cursor.execute("ALTER TABLE boards ADD COLUMN board_uuid TEXT DEFAULT NULL")
            cursor.execute("SELECT id FROM boards WHERE board_uuid IS NULL")
            import uuid
            for r in cursor.fetchall():
                cursor.execute("UPDATE boards SET board_uuid = ? WHERE id = ?", (str(uuid.uuid4()), r[0]))

        # Tabla de columnas (columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS columns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                board_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT NOT NULL DEFAULT '#3b82f6',
                position INTEGER NOT NULL,
                collapsed INTEGER NOT NULL DEFAULT 0,
                column_uuid TEXT DEFAULT NULL,
                FOREIGN KEY(board_id) REFERENCES boards(id) ON DELETE CASCADE
            )
        """)

        # Migración: añadir 'collapsed' y 'column_uuid' a BD anteriores
        cursor.execute("PRAGMA table_info(columns)")
        columns_cols = [row[1] for row in cursor.fetchall()]
        if "collapsed" not in columns_cols:
            cursor.execute("ALTER TABLE columns ADD COLUMN collapsed INTEGER NOT NULL DEFAULT 0")
        if "column_uuid" not in columns_cols:
            cursor.execute("ALTER TABLE columns ADD COLUMN column_uuid TEXT DEFAULT NULL")
            cursor.execute("SELECT id FROM columns WHERE column_uuid IS NULL")
            import uuid
            for r in cursor.fetchall():
                cursor.execute("UPDATE columns SET column_uuid = ? WHERE id = ?", (str(uuid.uuid4()), r[0]))

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
                task_uuid TEXT DEFAULT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(column_id) REFERENCES columns(id) ON DELETE CASCADE
            )
        """)

        # Migración: columnas 'due_date', 'due_time', 'recurrence', 'task_uuid' y 'version' en 'tasks'
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = [row[1] for row in cursor.fetchall()]
        if "due_date" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "due_time" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN due_time TEXT")
        if "recurrence" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT NOT NULL DEFAULT 'none'")
        if "task_uuid" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN task_uuid TEXT DEFAULT NULL")
            cursor.execute("SELECT id FROM tasks WHERE task_uuid IS NULL")
            import uuid
            for r in cursor.fetchall():
                cursor.execute("UPDATE tasks SET task_uuid = ? WHERE id = ?", (str(uuid.uuid4()), r[0]))
        if "version" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN version INTEGER NOT NULL DEFAULT 1")
        if "synced_version" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN synced_version INTEGER NOT NULL DEFAULT 0")

        # Migración: vínculo opcional de una tarea con OTRO tablero (p. ej. una tarea
        # resumen en "Tareas" que enlaza al detalle en el tablero "SW X")
        if "linked_board_id" not in tasks_columns:
            cursor.execute(
                "ALTER TABLE tasks ADD COLUMN linked_board_id INTEGER REFERENCES boards(id) ON DELETE SET NULL"
            )

        # Migración: temporizador de una tarea (fecha/hora de inicio, o NULL si no está en marcha)
        if "timer_started_at" not in tasks_columns:
            cursor.execute("ALTER TABLE tasks ADD COLUMN timer_started_at TEXT")

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
from .sync import *  # noqa: E402,F401,F403
