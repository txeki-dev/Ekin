"""Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.

Funciones puras (devuelven texto) sobre la capa de datos, sin dependencias de Qt, para
poder testearlas de forma aislada. Incluye los tableros archivados."""
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


def _gather(db_path=None):
    """Estructura anidada de todo el contenido: tableros -> columnas -> tareas (+logs)."""
    boards = []
    for board in database.get_boards(db_path, include_archived=True):
        b = {
            "id": board["id"], "name": board["name"], "color": board["color"],
            "archived": bool(board.get("archived", 0)), "columns": [],
        }
        for col in database.get_columns(board["id"], db_path):
            c = {"id": col["id"], "name": col["name"], "color": col["color"], "tasks": []}
            for task in database.get_tasks(col["id"], db_path):
                c["tasks"].append({
                    "id": task["id"], "title": task["title"],
                    "description": _plain(task.get("description")),
                    "due_date": task.get("due_date"), "due_time": task.get("due_time"),
                    "recurrence": task.get("recurrence", "none"),
                    "tags": [{"category": t["category"], "value": t["value"]} for t in task.get("tags", [])],
                    "logs": [
                        {"created_at": lg["created_at"], "content": _plain(lg["content"])}
                        for lg in database.get_logs(task["id"], db_path)
                    ],
                })
            b["columns"].append(c)
        boards.append(b)
    return boards


def boards_to_json(db_path=None):
    """Volcado completo (tableros, columnas, tareas, etiquetas y diario) como JSON."""
    return json.dumps(
        {"exported_at": date.today().isoformat(), "boards": _gather(db_path)},
        ensure_ascii=False, indent=2,
    )


def tasks_to_csv(db_path=None):
    """CSV plano de todas las tareas (una fila por tarea)."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["board", "column", "task", "due_date", "due_time", "recurrence", "tags", "position"])
    for board in database.get_boards(db_path, include_archived=True):
        for col in database.get_columns(board["id"], db_path):
            for i, task in enumerate(database.get_tasks(col["id"], db_path)):
                writer.writerow([
                    board["name"], col["name"], task["title"],
                    task.get("due_date") or "", task.get("due_time") or "",
                    task.get("recurrence", "none"), _tags_str(task), i,
                ])
    return buf.getvalue()


def report_markdown(db_path=None):
    """Informe de proyecto en Markdown: por tablero, sus columnas y tareas."""
    lines = [f"# Informe de Ekin Kanban — {date.today().isoformat()}", ""]
    for board in database.get_boards(db_path, include_archived=True):
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
                suffix = ("  —  " + " · ".join(meta)) if meta else ""
                lines.append(f"- **{task['title']}**{suffix}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
