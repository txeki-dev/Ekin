"""Importación de tableros, columnas y tareas a Ekin desde archivos JSON.

Funciones puras sobre la capa de datos (database), independientes de la UI de Qt,
para permitir importación completa (tableros, columnas, tareas, etiquetas, diario y enlaces)
o importación de solo estructura (plantillas de columnas sin tareas).
"""
import json

from database import get_connection


def parse_boards_json(data):
    """Parsea y valida la estructura de un JSON de importación.
    `data` puede ser una cadena JSON, un diccionario o una lista.

    Devuelve una tupla `(boards_list, stats)` donde `stats` es un diccionario con
    los conteos de `{"boards": int, "columns": int, "tasks": int}`.
    Lanza `ValueError` con un mensaje explicativo si la estructura no es válida.
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Formato JSON inválido: {exc}")

    boards_list = []
    if isinstance(data, dict):
        if "boards" in data and isinstance(data["boards"], list):
            boards_list = data["boards"]
        elif "board" in data and isinstance(data["board"], dict):
            boards_list = [data["board"]]
        elif "name" in data and ("columns" in data or "id" in data):
            boards_list = [data]
        else:
            raise ValueError("El archivo JSON no contiene una estructura reconocida de tableros ('boards' o 'board').")
    elif isinstance(data, list):
        boards_list = data
    else:
        raise ValueError("El contenido del JSON debe ser un objeto o una lista.")

    if not boards_list:
        raise ValueError("No se encontraron tableros para importar en el archivo.")

    total_columns = 0
    total_tasks = 0
    for b in boards_list:
        if not isinstance(b, dict):
            continue
        cols = b.get("columns", [])
        if isinstance(cols, list):
            total_columns += len(cols)
            for c in cols:
                if isinstance(c, dict):
                    ts = c.get("tasks", [])
                    if isinstance(ts, list):
                        total_tasks += len(ts)

    stats = {
        "boards": len(boards_list),
        "columns": total_columns,
        "tasks": total_tasks,
    }
    return boards_list, stats


def import_boards(boards_list, db_path=None, include_tasks=True):
    """Inserta una lista de tableros en la base de datos dentro de una única transacción atómica.

    - `boards_list`: lista de diccionarios con la definición de tableros y columnas.
    - `include_tasks`: si es False, omite las tareas y solo crea tableros y columnas (plantilla).

    Devuelve la lista de IDs de tableros creados `[new_board_id, ...]`.
    """
    if not boards_list:
        return []

    created_board_ids = []

    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        for b_data in boards_list:
            if not isinstance(b_data, dict):
                continue

            b_name = b_data.get("name") or "Tablero Importado"
            b_color = b_data.get("color") or "#3b82f6"
            b_archived = 1 if b_data.get("archived") else 0

            cursor.execute(
                "INSERT INTO boards (name, color, archived) VALUES (?, ?, ?)",
                (b_name, b_color, b_archived)
            )
            new_board_id = cursor.lastrowid
            created_board_ids.append(new_board_id)

            columns = b_data.get("columns", [])
            if not isinstance(columns, list):
                columns = []

            for c_idx, c_data in enumerate(columns):
                if not isinstance(c_data, dict):
                    continue

                c_name = c_data.get("name") or "Columna"
                c_color = c_data.get("color") or "#3b82f6"
                c_collapsed = 1 if c_data.get("collapsed") else 0
                c_pos = c_idx

                cursor.execute(
                    "INSERT INTO columns (board_id, name, color, position, collapsed) VALUES (?, ?, ?, ?, ?)",
                    (new_board_id, c_name, c_color, c_pos, c_collapsed)
                )
                new_column_id = cursor.lastrowid

                if not include_tasks:
                    continue

                tasks = c_data.get("tasks", [])
                if not isinstance(tasks, list):
                    tasks = []

                for t_idx, t_data in enumerate(tasks):
                    if not isinstance(t_data, dict):
                        continue

                    t_title = t_data.get("title") or "Tarea"
                    t_desc = t_data.get("description") or ""
                    t_due_date = t_data.get("due_date")
                    t_due_time = t_data.get("due_time")
                    t_recurrence = t_data.get("recurrence") or "none"
                    t_timer = t_data.get("timer_started_at")
                    t_pos = t_idx

                    cursor.execute(
                        """INSERT INTO tasks (column_id, title, description, position,
                                              due_date, due_time, recurrence, timer_started_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (new_column_id, t_title, t_desc, t_pos, t_due_date, t_due_time, t_recurrence, t_timer)
                    )
                    new_task_id = cursor.lastrowid

                    # Etiquetas (tags)
                    tags = t_data.get("tags", [])
                    if isinstance(tags, list):
                        for tag in tags:
                            if isinstance(tag, dict):
                                cat_name = tag.get("category") or "General"
                                val_text = tag.get("value") or ""
                                val_color = tag.get("color") or "#6b7280"
                            elif isinstance(tag, str):
                                cat_name = "General"
                                val_text = tag
                                val_color = "#6b7280"
                            else:
                                continue

                            if not val_text:
                                continue

                            # Buscar o crear categoría
                            cursor.execute("SELECT id FROM tag_categories WHERE name = ?", (cat_name,))
                            cat_row = cursor.fetchone()
                            if cat_row:
                                cat_id = cat_row[0]
                            else:
                                cursor.execute("INSERT INTO tag_categories (name) VALUES (?)", (cat_name,))
                                cat_id = cursor.lastrowid

                            # Buscar o crear valor de etiqueta
                            cursor.execute(
                                "SELECT id FROM tag_values WHERE category_id = ? AND value = ?",
                                (cat_id, val_text)
                            )
                            val_row = cursor.fetchone()
                            if val_row:
                                val_id = val_row[0]
                            else:
                                cursor.execute(
                                    "INSERT INTO tag_values (category_id, value, color) VALUES (?, ?, ?)",
                                    (cat_id, val_text, val_color)
                                )
                                val_id = cursor.lastrowid

                            cursor.execute(
                                "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
                                (new_task_id, val_id)
                            )

                    # Logs / Diario
                    logs = t_data.get("logs", [])
                    if isinstance(logs, list):
                        for lg in logs:
                            if isinstance(lg, dict):
                                lg_content = lg.get("content") or ""
                                lg_created = lg.get("created_at")
                            else:
                                lg_content = str(lg)
                                lg_created = None

                            if lg_content:
                                if lg_created:
                                    cursor.execute(
                                        "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                                        (new_task_id, lg_content, lg_created)
                                    )
                                else:
                                    cursor.execute(
                                        "INSERT INTO task_logs (task_id, content) VALUES (?, ?)",
                                        (new_task_id, lg_content)
                                    )

                    # Links / Adjuntos
                    links = t_data.get("links", [])
                    if isinstance(links, list):
                        for l_idx, lk in enumerate(links):
                            if isinstance(lk, dict):
                                lk_url = lk.get("url") or ""
                                lk_label = lk.get("label")
                                lk_pos = lk.get("position", l_idx)
                            else:
                                lk_url = str(lk)
                                lk_label = None
                                lk_pos = l_idx

                            if lk_url:
                                cursor.execute(
                                    "INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
                                    (new_task_id, lk_url, lk_label, lk_pos)
                                )

    return created_board_ids
