"""Pruebas del exportador (JSON / CSV / informe Markdown)."""
import json

import database
import exporter


def _sample(db_path):
    b = database.create_board("Trabajo", db_path=db_path)
    c = database.create_column(b, "Pendientes", db_path=db_path)
    t = database.create_task(c, "Escribir informe", description="<p>Redactar borrador</p>", due_date="2026-08-01", db_path=db_path)
    tv = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    database.set_task_tags(t, [tv], db_path=db_path)
    database.set_task_recurrence(t, "weekly", db_path=db_path)
    database.set_task_timer_started(t, "2026-08-01T09:00:00", db_path=db_path)
    database.add_task_link(t, "https://example.com/doc", "Doc Link", db_path=db_path)
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
    assert task["timer_started_at"] == "2026-08-01T09:00:00"
    assert task["tags"][0]["category"] == "Prioridad" and task["tags"][0]["value"] == "Alta"
    assert task["links"][0]["url"] == "https://example.com/doc"
    assert task["logs"][0]["content"] == "primera nota"


def test_boards_to_json_single_board_and_template_only(db_path):
    b, c, t = _sample(db_path)

    # 1. Exportar solo un tablero específico con tareas
    single_json = json.loads(exporter.boards_to_json(db_path, board_id=b, include_tasks=True))
    assert single_json["scope"] == "single_board"
    assert len(single_json["boards"]) == 1
    assert single_json["boards"][0]["name"] == "Trabajo"
    assert len(single_json["boards"][0]["columns"][0]["tasks"]) == 1

    # 2. Exportar solo estructura de columnas (plantilla sin tareas)
    template_json = json.loads(exporter.boards_to_json(db_path, board_id=b, include_tasks=False))
    assert template_json["include_tasks"] is False
    assert len(template_json["boards"][0]["columns"][0]["tasks"]) == 0
    assert template_json["boards"][0]["columns"][0]["name"] == "Pendientes"


def test_tasks_to_csv(db_path):
    b, c, t = _sample(db_path)
    csv_text = exporter.tasks_to_csv(db_path)
    lines = csv_text.strip().splitlines()
    assert lines[0] == "board,column,task,due_date,due_time,recurrence,tags,links_count,position"
    assert any("Escribir informe" in ln and "Prioridad: Alta" in ln for ln in lines[1:])

    # Filtrado a tablero único
    single_csv = exporter.tasks_to_csv(db_path, board_id=b)
    single_lines = single_csv.strip().splitlines()
    assert len(single_lines) == 2  # cabecera + 1 tarea


def test_report_markdown(db_path):
    b, c, t = _sample(db_path)
    md = exporter.report_markdown(db_path, include_descriptions=True, include_logs=True, include_links=True)
    assert "# Informe de Ekin Kanban" in md
    assert "## Trabajo" in md
    assert "### Pendientes" in md
    assert "**Escribir informe**" in md
    assert "🔁 weekly" in md
    assert "Redactar borrador" in md
    assert "Doc Link" in md
    assert "primera nota" in md
    assert "*(archivado)*" in md          # el tablero archivado aparece marcado

