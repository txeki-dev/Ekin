"""Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.

Funciones puras (devuelven texto) sobre la capa de datos, sin dependencias de Qt, para
poder testearlas de forma aislada. Soporta todos los tableros o un tablero específico,
así como exportación completa o de solo estructura (plantilla).
"""
import csv
import io
import json
import re
from datetime import date

import database


def _plain(html):
    """Convierte HTML (descripción/nota) en texto plano razonable para exportar."""
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|li)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()


def _tags_str(task):
    return ", ".join(f"{t['category']}: {t['value']}" for t in task.get("tags", []))


def _gather(db_path=None, board_id=None, include_tasks=True):
    """Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags, links)."""
    boards = []
    if board_id is not None:
        target_board = database.get_board(board_id, db_path)
        raw_boards = [target_board] if target_board else []
    else:
        raw_boards = database.get_boards(db_path, include_archived=True)

    for board in raw_boards:
        b = {
            "id": board["id"], "name": board["name"], "color": board["color"],
            "archived": bool(board.get("archived", 0)), "columns": [],
        }
        for col in database.get_columns(board["id"], db_path):
            c = {
                "id": col["id"], "name": col["name"], "color": col["color"],
                "collapsed": bool(col.get("collapsed", 0)), "tasks": [],
            }
            if include_tasks:
                tasks = database.get_tasks(col["id"], db_path)
                logs_by_task = database.get_logs_bulk([t["id"] for t in tasks], db_path)
                for task in tasks:
                    t_item = {
                        "id": task["id"], "title": task["title"],
                        "description": _plain(task.get("description")),
                        "due_date": task.get("due_date"), "due_time": task.get("due_time"),
                        "recurrence": task.get("recurrence", "none"),
                        "linked_board_id": task.get("linked_board_id"),
                        "linked_board_name": task.get("linked_board_name"),
                        "timer_started_at": task.get("timer_started_at"),
                        "tags": [
                            {"category": tg["category"], "value": tg["value"], "color": tg.get("color", "#6b7280")}
                            for tg in task.get("tags", [])
                        ],
                        "links": [
                            {"url": lk["url"], "label": lk.get("label"), "position": lk.get("position", 0)}
                            for lk in task.get("links", [])
                        ],
                        "logs": [
                            {"created_at": lg["created_at"], "content": _plain(lg["content"])}
                            for lg in logs_by_task.get(task["id"], [])
                        ],
                    }
                    c["tasks"].append(t_item)
            b["columns"].append(c)
        boards.append(b)
    return boards


def boards_to_json(db_path=None, board_id=None, include_tasks=True):
    """Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como JSON.
    Si `include_tasks=False`, exporta únicamente la estructura de tableros y columnas (plantilla)."""
    boards = _gather(db_path, board_id=board_id, include_tasks=include_tasks)
    return json.dumps(
        {
            "version": "1.0",
            "exported_at": date.today().isoformat(),
            "scope": "single_board" if board_id is not None else "all_boards",
            "include_tasks": include_tasks,
            "boards": boards,
        },
        ensure_ascii=False, indent=2,
    )


def tasks_to_csv(db_path=None, board_id=None):
    """CSV plano de todas las tareas (una fila por tarea). Soporta todos los tableros o uno solo."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "board", "column", "task", "due_date", "due_time", "recurrence", "tags",
        "links_count", "position"
    ])
    if board_id is not None:
        target_board = database.get_board(board_id, db_path)
        raw_boards = [target_board] if target_board else []
    else:
        raw_boards = database.get_boards(db_path, include_archived=True)

    for board in raw_boards:
        for col in database.get_columns(board["id"], db_path):
            for i, task in enumerate(database.get_tasks(col["id"], db_path)):
                writer.writerow([
                    board["name"], col["name"], task["title"],
                    task.get("due_date") or "", task.get("due_time") or "",
                    task.get("recurrence", "none"), _tags_str(task),
                    len(task.get("links", [])), i,
                ])
    return buf.getvalue()


def report_markdown(db_path=None, board_id=None, include_descriptions=True, include_logs=False, include_links=True):
    """Informe de proyecto en Markdown: por tablero, sus columnas y tareas."""
    lines = [f"# Informe de Ekin Kanban — {date.today().isoformat()}", ""]
    if board_id is not None:
        target_board = database.get_board(board_id, db_path)
        raw_boards = [target_board] if target_board else []
    else:
        raw_boards = database.get_boards(db_path, include_archived=True)

    for board in raw_boards:
        suffix = " *(archivado)*" if board.get("archived") else ""
        lines.append(f"## {board['name']}{suffix}")
        lines.append("")
        columns = database.get_columns(board["id"], db_path)
        if not columns:
            lines.append("_Sin columnas._\n")
            continue
        for col in columns:
            tasks = database.get_tasks(col["id"], db_path)
            lines.append(f"### {col['name']}  ({len(tasks)})")
            if not tasks:
                lines.append("- _(vacía)_")
            logs_by_task = database.get_logs_bulk([t["id"] for t in tasks], db_path) if include_logs else {}
            for task in tasks:
                meta = []
                if task.get("due_date"):
                    due = task["due_date"] + (f" {task['due_time']}" if task.get("due_time") else "")
                    meta.append(f"📅 {due}")
                if task.get("recurrence", "none") != "none":
                    meta.append(f"🔁 {task['recurrence']}")
                tags = _tags_str(task)
                if tags:
                    meta.append(f"🏷️ {tags}")
                if task.get("linked_board_name"):
                    meta.append(f"🔗 Tablero: {task['linked_board_name']}")
                suffix = ("  —  " + " · ".join(meta)) if meta else ""
                lines.append(f"- **{task['title']}**{suffix}")
                if include_descriptions and task.get("description"):
                    plain_desc = _plain(task["description"])
                    if plain_desc:
                        for desc_line in plain_desc.splitlines():
                            lines.append(f"  > {desc_line}")
                if include_links and task.get("links"):
                    for lk in task["links"]:
                        lbl = lk.get("label") or lk["url"]
                        lines.append(f"  - 📎 [{lbl}]({lk['url']})")
                if include_logs and logs_by_task.get(task["id"]):
                    for lg in logs_by_task[task["id"]]:
                        plain_log = _plain(lg["content"])
                        lines.append(f"  - 💬 *{lg['created_at']}*: {plain_log}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
