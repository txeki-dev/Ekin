"""Pruebas del exportador (JSON / CSV / informe Markdown)."""
import json

import database
import exporter


def _sample(db_path):
    b = database.create_board("Trabajo", db_path=db_path)
    c = database.create_column(b, "Pendientes", db_path=db_path)
    t = database.create_task(c, "Escribir informe", due_date="2026-08-01", db_path=db_path)
    tv = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    database.set_task_tags(t, [tv], db_path=db_path)
    database.set_task_recurrence(t, "weekly", db_path=db_path)
    database.create_log(t, "primera nota", db_path=db_path)
    # un tablero archivado también debe exportarse
    ab = database.create_board("Viejo", db_path=db_path)
    database.set_board_archived(ab, True, db_path=db_path)
    return b, c, t


def test_boards_to_json_roundtrip(db_path):
    _sample(db_path)
    data = json.loads(exporter.boards_to_json(db_path))
    names = [b["name"] for b in data["boards"]]
    assert "Trabajo" in names and "Viejo" in names            # incluye archivados
    trabajo = next(b for b in data["boards"] if b["name"] == "Trabajo")
    task = trabajo["columns"][0]["tasks"][0]
    assert task["title"] == "Escribir informe"
    assert task["due_date"] == "2026-08-01" and task["recurrence"] == "weekly"
    assert task["tags"] == [{"category": "Prioridad", "value": "Alta"}]
    assert task["logs"][0]["content"] == "primera nota"


def test_tasks_to_csv(db_path):
    _sample(db_path)
    csv_text = exporter.tasks_to_csv(db_path)
    lines = csv_text.strip().splitlines()
    assert lines[0] == "board,column,task,due_date,due_time,recurrence,tags,position"
    assert any("Escribir informe" in ln and "Prioridad: Alta" in ln for ln in lines[1:])


def test_report_markdown(db_path):
    _sample(db_path)
    md = exporter.report_markdown(db_path)
    assert "# Informe de Ekin Kanban" in md
    assert "## Trabajo" in md
    assert "### Pendientes" in md
    assert "**Escribir informe**" in md
    assert "🔁 weekly" in md
    assert "*(archivado)*" in md          # el tablero archivado aparece marcado
