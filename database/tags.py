from . import get_connection

__all__ = [
    "get_task_tags", "get_task_tags_bulk", "set_task_tags",
    "get_tag_categories", "get_tag_values", "get_tag_value", "get_or_create_tag_value",
    "create_tag_category", "rename_tag_category", "delete_tag_category",
    "create_tag_value", "value_exists_in_category", "update_tag_value", "delete_tag_value",
]

# --- ETIQUETAS DE TAREA (TASK_TAGS) ---

def get_task_tags(task_id, db_path=None):
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
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM tag_categories ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]

def get_tag_values(category_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, category_id, value, color FROM tag_values WHERE category_id = ? ORDER BY value ASC",
            (category_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_tag_value(tag_value_id, db_path=None):
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
    with get_connection(db_path) as conn:
        conn.execute("UPDATE tag_categories SET name = ? WHERE id = ?", (new_name.strip(), category_id))
        conn.commit()

def delete_tag_category(category_id, db_path=None):
    """Elimina una etiqueta permanente. En cascada borra sus valores y las asignaciones a tareas."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tag_categories WHERE id = ?", (category_id,))
        conn.commit()

def create_tag_value(category_id, value, color, db_path=None):
    """Añade un valor (con color) a una etiqueta permanente. Devuelve su id."""
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
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE tag_values SET value = ?, color = ? WHERE id = ?",
            (value.strip(), color, tag_value_id)
        )
        conn.commit()

def delete_tag_value(tag_value_id, db_path=None):
    """Elimina un valor. En cascada se retira de las tareas que lo tuvieran asignado."""
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM tag_values WHERE id = ?", (tag_value_id,))
        conn.commit()
