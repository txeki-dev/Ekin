import sqlite3
import calendar as _cal
from datetime import datetime, date, timedelta

DB_NAME = "ekin_board.db"

def get_connection(db_path=None):
    """Establece una conexión a la base de datos y habilita las claves foráneas."""
    db_path = db_path or DB_NAME
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

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
        conn.commit()

# --- OPERACIONES DE TABLEROS (BOARDS) ---

def create_board(name, color='#3b82f6', db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO boards (name, color) VALUES (?, ?)", (name, color))
        conn.commit()
        return cursor.lastrowid

def get_boards(db_path=None, include_archived=False):
    """Devuelve los tableros. Por defecto excluye los archivados."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT id, name, color, archived, created_at FROM boards"
        if not include_archived:
            query += " WHERE archived = 0"
        query += " ORDER BY id ASC"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]

def get_board(board_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, color, archived, created_at FROM boards WHERE id = ?", (board_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def set_board_archived(board_id, archived, db_path=None):
    """Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra lateral."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET archived = ? WHERE id = ?", (1 if archived else 0, board_id))
        conn.commit()

def update_board(board_id, name, color, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE boards SET name = ?, color = ? WHERE id = ?", (name, color, board_id))
        conn.commit()

def delete_board(board_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM boards WHERE id = ?", (board_id,))
        conn.commit()

# --- OPERACIONES DE COLUMNAS (COLUMNS) ---

def create_column(board_id, name, color='#3b82f6', db_path=None):
    db_path = db_path or DB_NAME
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

def get_columns(board_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, board_id, name, color, position, collapsed FROM columns WHERE board_id = ? ORDER BY position ASC",
            (board_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def update_column(column_id, name, color, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE columns SET name = ?, color = ? WHERE id = ?",
            (name, color, column_id)
        )
        conn.commit()

def set_column_collapsed(column_id, collapsed, db_path=None):
    """Pliega (collapsed=1) o despliega (0) una columna del tablero."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE columns SET collapsed = ? WHERE id = ?", (1 if collapsed else 0, column_id))
        conn.commit()

def update_column_positions(column_positions, db_path=None):
    """Actualiza las posiciones de múltiples columnas.
    column_positions debe ser una lista de tuplas/diccionarios: (column_id, position)
    """
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for col_id, pos in column_positions:
            cursor.execute("UPDATE columns SET position = ? WHERE id = ?", (pos, col_id))
        conn.commit()

def delete_column(column_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))
        conn.commit()

# --- OPERACIONES DE TAREAS (TASKS) ---

def create_task(column_id, title, description="", tag_text="", tag_color="#6b7280", due_date=None, db_path=None):
    db_path = db_path or DB_NAME
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

def get_tasks(column_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at, due_date, due_time, recurrence
               FROM tasks WHERE column_id = ? ORDER BY position ASC""",
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
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, column_id, title, description, tag_text, tag_color, position, created_at, updated_at, due_date, due_time, recurrence
               FROM tasks WHERE id = ?""",
            (task_id,)
        )
        row = cursor.fetchone()
        if row:
            t = dict(row)
            t["tags"] = get_task_tags(t["id"], db_path)
            return t
        return None

def update_task(task_id, title, description, tag_text, tag_color, due_date, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            """UPDATE tasks 
               SET title = ?, description = ?, tag_text = ?, tag_color = ?, due_date = ?, updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (title, description, tag_text, tag_color, due_date, task_id)
        )
        conn.commit()

def update_task_due_date(task_id, due_date, db_path=None):
    """Actualiza solo la fecha de vencimiento de una tarea (usado por el arrastre en el calendario).
    `due_date` es una cadena 'YYYY-MM-DD' o None/'' para quitarla."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET due_date = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (due_date, task_id)
        )
        conn.commit()

def set_task_due_time(task_id, due_time, db_path=None):
    """Fija la hora de vencimiento ('HH:MM') de una tarea, o None para dejarla de día completo."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET due_time = ? WHERE id = ?", (due_time or None, task_id))
        conn.commit()

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
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET recurrence = ? WHERE id = ?", (recurrence or "none", task_id))
        conn.commit()

def advance_recurrence(task_id, db_path=None):
    """Avanza la fecha de vencimiento de una tarea recurrente a su siguiente ocurrencia.
    Devuelve la nueva fecha, o None si no es recurrente o no tiene fecha."""
    db_path = db_path or DB_NAME
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
        conn.commit()
        return nxt

def advance_overdue_recurring(today_iso, db_path=None):
    """Adelanta las tareas recurrentes vencidas a su próxima ocurrencia >= hoy.
    Pensado para ejecutarse al arrancar. Devuelve cuántas tareas se adelantaron."""
    db_path = db_path or DB_NAME
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
        conn.commit()
    return advanced

def get_task_tags(task_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT tv.id AS tag_value_id, tc.id AS category_id, tc.name AS category,
                      tv.value AS value, tv.color AS color
               FROM task_tags tt
               JOIN tag_values tv ON tt.tag_value_id = tv.id
               JOIN tag_categories tc ON tv.category_id = tc.id
               WHERE tt.task_id = ?
               ORDER BY tt.id ASC""",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_task_tags_bulk(task_ids, db_path=None):
    """Devuelve {task_id: [etiquetas]} para varias tareas en UNA sola consulta.

    Evita el patrón N+1 (una conexión/consulta por tarea) al cargar tableros,
    el calendario o la campana. Cada etiqueta tiene la misma forma que en
    get_task_tags (sin incluir task_id)."""
    db_path = db_path or DB_NAME
    result = {tid: [] for tid in task_ids}
    if not task_ids:
        return result
    placeholders = ",".join("?" * len(task_ids))
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"""SELECT tt.task_id AS task_id, tv.id AS tag_value_id, tc.id AS category_id,
                       tc.name AS category, tv.value AS value, tv.color AS color
                FROM task_tags tt
                JOIN tag_values tv ON tt.tag_value_id = tv.id
                JOIN tag_categories tc ON tv.category_id = tc.id
                WHERE tt.task_id IN ({placeholders})
                ORDER BY tt.task_id ASC, tt.id ASC""",
            list(task_ids)
        )
        for row in cursor.fetchall():
            data = dict(row)
            task_id = data.pop("task_id")
            result.setdefault(task_id, []).append(data)
    return result

def set_task_tags(task_id, tag_value_ids, db_path=None):
    """Establece las etiquetas (ids de tag_values) asignadas a una tarea, eliminando las anteriores."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
        for tag_value_id in tag_value_ids:
            conn.execute(
                "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                (task_id, tag_value_id)
            )
        conn.commit()

# --- OPERACIONES DE CATEGORÍAS Y VALORES DE ETIQUETAS (TAG_CATEGORIES / TAG_VALUES) ---

def get_tag_categories(db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM tag_categories ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_tag_values(category_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category_id, value, color FROM tag_values WHERE category_id = ? ORDER BY value ASC",
            (category_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_tag_value(tag_value_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT tv.id AS tag_value_id, tc.id AS category_id, tc.name AS category,
                      tv.value AS value, tv.color AS color
               FROM tag_values tv
               JOIN tag_categories tc ON tv.category_id = tc.id
               WHERE tv.id = ?""",
            (tag_value_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_or_create_tag_value(category_name, value_text, color, db_path=None):
    """Obtiene el id de una etiqueta (categoría + valor), creando la categoría y/o el valor si no existen.
    Si el valor ya existe, se conserva su color original: el color solo se aplica al crear un valor nuevo."""
    db_path = db_path or DB_NAME
    category_name = category_name.strip()
    value_text = value_text.strip()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tag_categories WHERE LOWER(name) = LOWER(?)", (category_name,))
        row = cursor.fetchone()
        if row:
            category_id = row["id"]
        else:
            cursor.execute("INSERT INTO tag_categories (name) VALUES (?)", (category_name,))
            category_id = cursor.lastrowid

        cursor.execute(
            "SELECT id FROM tag_values WHERE category_id = ? AND LOWER(value) = LOWER(?)",
            (category_id, value_text)
        )
        row = cursor.fetchone()
        if row:
            tag_value_id = row["id"]
        else:
            cursor.execute(
                "INSERT INTO tag_values (category_id, value, color) VALUES (?, ?, ?)",
                (category_id, value_text, color)
            )
            tag_value_id = cursor.lastrowid

        conn.commit()
        return tag_value_id

# --- GESTIÓN DEL CATÁLOGO DE ETIQUETAS PERMANENTES (categorías y sus valores) ---

def create_tag_category(name, db_path=None):
    """Crea una etiqueta permanente (categoría). Si ya existe (sin distinguir mayúsculas),
    devuelve el id existente en lugar de duplicarla."""
    db_path = db_path or DB_NAME
    name = name.strip()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tag_categories WHERE LOWER(name) = LOWER(?)", (name,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute("INSERT INTO tag_categories (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid

def rename_tag_category(category_id, new_name, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tag_categories SET name = ? WHERE id = ?", (new_name.strip(), category_id))
        conn.commit()

def delete_tag_category(category_id, db_path=None):
    """Elimina una etiqueta permanente. En cascada borra sus valores y las asignaciones a tareas."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tag_categories WHERE id = ?", (category_id,))
        conn.commit()

def create_tag_value(category_id, value, color, db_path=None):
    """Añade un valor (con color) a una etiqueta permanente. Devuelve su id."""
    db_path = db_path or DB_NAME
    value = value.strip()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tag_values (category_id, value, color) VALUES (?, ?, ?)",
            (category_id, value, color)
        )
        conn.commit()
        return cursor.lastrowid

def value_exists_in_category(category_id, value, exclude_value_id=None, db_path=None):
    """Indica si ya existe un valor (comparación sin mayúsculas) en la categoría dada.
    exclude_value_id permite ignorar un valor concreto (útil al renombrar)."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if exclude_value_id is None:
            cursor.execute(
                "SELECT 1 FROM tag_values WHERE category_id = ? AND LOWER(value) = LOWER(?)",
                (category_id, value.strip())
            )
        else:
            cursor.execute(
                "SELECT 1 FROM tag_values WHERE category_id = ? AND LOWER(value) = LOWER(?) AND id != ?",
                (category_id, value.strip(), exclude_value_id)
            )
        return cursor.fetchone() is not None

def update_tag_value(tag_value_id, value, color, db_path=None):
    """Actualiza el texto y/o color de un valor. Afecta a todas las tareas que lo usen
    (comportamiento esperado en una etiqueta permanente)."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tag_values SET value = ?, color = ? WHERE id = ?",
            (value.strip(), color, tag_value_id)
        )
        conn.commit()

def delete_tag_value(tag_value_id, db_path=None):
    """Elimina un valor. En cascada se retira de las tareas que lo tuvieran asignado."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tag_values WHERE id = ?", (tag_value_id,))
        conn.commit()

# --- CONSULTAS DE VENCIMIENTOS Y CALENDARIO ---

def get_scheduled_tasks(start_date=None, end_date=None, board_id=None, db_path=None):
    """Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.

    Filtros opcionales:
      - start_date / end_date: rango inclusivo en formato 'YYYY-MM-DD'.
      - board_id: limitar a un tablero concreto.
    Cada elemento incluye sus etiquetas. Ordenado por fecha, tablero y posición.
    """
    db_path = db_path or DB_NAME
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
    db_path = db_path or DB_NAME
    query = [
        "SELECT DISTINCT t.id, t.title, t.description, t.due_date, t.column_id, t.updated_at,",
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

# --- AJUSTES DE LA APLICACIÓN (clave/valor) ---

def get_setting(key, default=None, db_path=None):
    """Devuelve el valor de un ajuste, o `default` si no está definido."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def set_setting(key, value, db_path=None):
    """Crea o actualiza un ajuste de la aplicación."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()

def get_task_board_id(task_id, db_path=None):
    """Devuelve el board_id al que pertenece una tarea (o None si no existe)."""
    db_path = db_path or DB_NAME
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

def update_task_position(task_id, new_column_id, new_position, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_column_id, new_position, task_id)
        )
        conn.commit()

def update_task_positions(task_positions, db_path=None):
    """Actualiza de golpe la columna y posición de varias tareas (para reordenación drag-and-drop).
    task_positions: lista de tuplas/diccionarios: (task_id, column_id, position)
    """
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for task_id, col_id, pos in task_positions:
            cursor.execute(
                "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (col_id, pos, task_id)
            )
        conn.commit()

def delete_task(task_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

# --- OPERACIONES DE LOGS/DIARIO (TASK_LOGS) ---

def create_log(task_id, content, db_path=None):
    db_path = db_path or DB_NAME
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

def get_logs(task_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_id, content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

# --- ENLACES / ADJUNTOS DE TAREAS ---

def add_task_link(task_id, url, label=None, db_path=None):
    """Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM task_links WHERE task_id = ?", (task_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
            (task_id, url, label or None, pos)
        )
        conn.commit()
        return cursor.lastrowid

def get_task_links(task_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, task_id, url, label, position FROM task_links WHERE task_id = ? ORDER BY position ASC",
            (task_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def delete_task_link(link_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM task_links WHERE id = ?", (link_id,))
        conn.commit()

def get_task_links_bulk(task_ids, db_path=None):
    """{task_id: [enlaces]} para varias tareas en una consulta (evita N+1 al pintar el tablero)."""
    db_path = db_path or DB_NAME
    result = {tid: [] for tid in task_ids}
    if not task_ids:
        return result
    placeholders = ",".join("?" * len(task_ids))
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT id, task_id, url, label, position FROM task_links "
            f"WHERE task_id IN ({placeholders}) ORDER BY task_id ASC, position ASC",
            list(task_ids)
        )
        for row in cursor.fetchall():
            d = dict(row)
            result.setdefault(d["task_id"], []).append(d)
    return result

def update_log(log_id, content, db_path=None):
    """Edita el contenido (HTML) de una entrada del diario y refresca el updated_at de la tarea."""
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        conn.execute("UPDATE task_logs SET content = ? WHERE id = ?", (content, log_id))
        conn.execute(
            "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP "
            "WHERE id = (SELECT task_id FROM task_logs WHERE id = ?)",
            (log_id,)
        )
        conn.commit()

def delete_log(log_id, db_path=None):
    db_path = db_path or DB_NAME
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

def move_column_to_board(column_id, target_board_id, db_path=None):
    """Mueve una columna a otro tablero y la coloca al final de su lista de columnas."""
    db_path = db_path or DB_NAME
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
    db_path = db_path or DB_NAME
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
    db_path = db_path or DB_NAME
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


# --- SNAPSHOT / RESTORE (para deshacer borrados) ---

def snapshot_task(task_id, db_path=None):
    """Captura todo el contenido de una tarea para poder recrearla (deshacer)."""
    db_path = db_path or DB_NAME
    task = get_task(task_id, db_path)
    if not task:
        return None
    return {
        "column_id": task["column_id"], "title": task["title"],
        "description": task["description"], "position": task["position"],
        "due_date": task.get("due_date"), "due_time": task.get("due_time"),
        "recurrence": task.get("recurrence", "none"),
        "tag_value_ids": [t["tag_value_id"] for t in task.get("tags", [])],
        "logs": [{"content": lg["content"], "created_at": lg["created_at"]}
                 for lg in get_logs(task_id, db_path)],
        "links": [{"url": lk["url"], "label": lk["label"]}
                  for lk in get_task_links(task_id, db_path)],
    }

def restore_task(snap, column_id=None, db_path=None):
    """Recrea una tarea a partir de un snapshot. Devuelve el nuevo id."""
    db_path = db_path or DB_NAME
    column_id = column_id if column_id is not None else snap["column_id"]
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM tasks WHERE column_id = ?", (column_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO tasks (column_id, title, description, position, due_date, due_time, recurrence) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (column_id, snap["title"], snap["description"], pos, snap.get("due_date"),
             snap.get("due_time"), snap.get("recurrence", "none"))
        )
        new_id = cursor.lastrowid
        for tvid in snap.get("tag_value_ids", []):
            cursor.execute(
                "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                (new_id, tvid))
        for lg in snap.get("logs", []):
            cursor.execute("INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                           (new_id, lg["content"], lg["created_at"]))
        for lk in snap.get("links", []):
            cursor.execute("INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, 0)",
                           (new_id, lk["url"], lk["label"]))
        conn.commit()
        return new_id

def snapshot_column(column_id, db_path=None):
    db_path = db_path or DB_NAME
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT board_id, name, color, position, collapsed FROM columns WHERE id = ?", (column_id,))
        row = cursor.fetchone()
    if not row:
        return None
    snap = dict(row)
    snap["tasks"] = [snapshot_task(t["id"], db_path) for t in get_tasks(column_id, db_path)]
    return snap

def restore_column(snap, board_id=None, db_path=None):
    db_path = db_path or DB_NAME
    board_id = board_id if board_id is not None else snap["board_id"]
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
        pos = cursor.fetchone()[0] + 1
        cursor.execute(
            "INSERT INTO columns (board_id, name, color, position, collapsed) VALUES (?, ?, ?, ?, ?)",
            (board_id, snap["name"], snap["color"], pos, snap.get("collapsed", 0)))
        new_col = cursor.lastrowid
        conn.commit()
    for task_snap in snap.get("tasks", []):
        if task_snap:
            restore_task(task_snap, column_id=new_col, db_path=db_path)
    return new_col

def snapshot_board(board_id, db_path=None):
    db_path = db_path or DB_NAME
    board = get_board(board_id, db_path)
    if not board:
        return None
    return {
        "name": board["name"], "color": board["color"], "archived": board.get("archived", 0),
        "columns": [snapshot_column(c["id"], db_path) for c in get_columns(board_id, db_path)],
    }

def restore_board(snap, db_path=None):
    db_path = db_path or DB_NAME
    new_board = create_board(snap["name"], snap["color"], db_path)
    if snap.get("archived"):
        set_board_archived(new_board, True, db_path)
    for col_snap in snap.get("columns", []):
        if col_snap:
            restore_column(col_snap, board_id=new_board, db_path=db_path)
    return new_board
