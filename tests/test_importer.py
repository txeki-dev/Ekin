"""Pruebas del importador de tableros desde JSON."""
import pytest

import database
import importer
import exporter


def test_parse_boards_json_valid_structures():
    # 1. Objeto estándar exportado por Ekin
    data_full = {
        "version": "1.0",
        "boards": [
            {
                "name": "Tablero 1",
                "color": "#3b82f6",
                "columns": [
                    {
                        "name": "Columna 1",
                        "tasks": [{"title": "T1"}, {"title": "T2"}]
                    }
                ]
            }
        ]
    }
    boards, stats = importer.parse_boards_json(data_full)
    assert stats["boards"] == 1
    assert stats["columns"] == 1
    assert stats["tasks"] == 2
    assert boards[0]["name"] == "Tablero 1"

    # 2. Objeto singular {"board": {...}}
    data_single = {
        "board": {
            "name": "Tablero Singular",
            "columns": [{"name": "Col A", "tasks": []}]
        }
    }
    boards, stats = importer.parse_boards_json(data_single)
    assert stats["boards"] == 1
    assert stats["columns"] == 1
    assert stats["tasks"] == 0

    # 3. Lista cruda de tableros
    data_list = [
        {"name": "B1", "columns": []},
        {"name": "B2", "columns": []}
    ]
    boards, stats = importer.parse_boards_json(data_list)
    assert stats["boards"] == 2


def test_parse_boards_json_invalid_raises_value_error():
    with pytest.raises(ValueError, match="JSON inválido"):
        importer.parse_boards_json("{ esto no es json }")

    with pytest.raises(ValueError, match="no contiene una estructura reconocida"):
        importer.parse_boards_json({"algo_desconocido": 123})

    with pytest.raises(ValueError, match="No se encontraron tableros"):
        importer.parse_boards_json({"boards": []})


def test_import_boards_full_roundtrip(db_path):
    sample_json = {
        "boards": [
            {
                "name": "Tablero Importado",
                "color": "#10b981",
                "archived": False,
                "columns": [
                    {
                        "name": "Por Hacer",
                        "color": "#3b82f6",
                        "tasks": [
                            {
                                "title": "Comprar pan",
                                "description": "Ir a la panaderia",
                                "due_date": "2026-09-15",
                                "due_time": "18:00",
                                "recurrence": "daily",
                                "timer_started_at": "2026-09-15T09:00:00",
                                "tags": [
                                    {"category": "Urgencia", "value": "Media", "color": "#f59e0b"}
                                ],
                                "links": [
                                    {"url": "https://panaderia.com", "label": "Web Pan"}
                                ],
                                "logs": [
                                    {"content": "Encargado por telefono", "created_at": "2026-09-14 10:00:00"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    boards, stats = importer.parse_boards_json(sample_json)
    created_ids = importer.import_boards(boards, db_path=db_path, include_tasks=True)

    assert len(created_ids) == 1
    new_b_id = created_ids[0]

    board = database.get_board(new_b_id, db_path)
    assert board["name"] == "Tablero Importado"
    assert board["color"] == "#10b981"

    cols = database.get_columns(new_b_id, db_path)
    assert len(cols) == 1
    assert cols[0]["name"] == "Por Hacer"

    tasks = database.get_tasks(cols[0]["id"], db_path)
    assert len(tasks) == 1
    task = tasks[0]
    assert task["title"] == "Comprar pan"
    assert task["description"] == "Ir a la panaderia"
    assert task["due_date"] == "2026-09-15"
    assert task["due_time"] == "18:00"
    assert task["recurrence"] == "daily"
    assert task["timer_started_at"] == "2026-09-15T09:00:00"
    assert task["tags"] == [
        {"tag_value_id": task["tags"][0]["tag_value_id"], "category_id": task["tags"][0]["category_id"],
         "category": "Urgencia", "value": "Media", "color": "#f59e0b"}
    ]
    assert len(task["links"]) == 1
    assert task["links"][0]["url"] == "https://panaderia.com"
    assert task["links"][0]["label"] == "Web Pan"

    logs = database.get_logs(task["id"], db_path)
    assert len(logs) == 1
    assert logs[0]["content"] == "Encargado por telefono"


def test_import_boards_structure_only_as_template(db_path):
    # Un JSON con tareas exportado, importado solo como plantilla (sin tareas)
    sample_json = {
        "boards": [
            {
                "name": "Plantilla Scrum",
                "color": "#6366f1",
                "columns": [
                    {"name": "Backlog", "tasks": [{"title": "Tarea 1"}]},
                    {"name": "Sprint", "tasks": [{"title": "Tarea 2"}]},
                    {"name": "Done", "tasks": [{"title": "Tarea 3"}]}
                ]
            }
        ]
    }

    boards, stats = importer.parse_boards_json(sample_json)
    created_ids = importer.import_boards(boards, db_path=db_path, include_tasks=False)

    assert len(created_ids) == 1
    new_b_id = created_ids[0]

    cols = database.get_columns(new_b_id, db_path)
    assert len(cols) == 3
    col_names = [c["name"] for c in cols]
    assert col_names == ["Backlog", "Sprint", "Done"]

    # Ninguna columna debe tener tareas
    for col in cols:
        tasks = database.get_tasks(col["id"], db_path)
        assert len(tasks) == 0


def test_export_then_import_preserves_everything(db_path, tmp_path):
    # 1. Crear datos en la BD origen
    b_id = database.create_board("Tablero Origen", "#3b82f6", db_path=db_path)
    c_id = database.create_column(b_id, "Col 1", db_path=db_path)
    t_id = database.create_task(c_id, "Tarea Principal", description="Texto de prueba", due_date="2026-10-01", db_path=db_path)
    tag_v = database.get_or_create_tag_value("Tipo", "Bug", "#ef4444", db_path=db_path)
    database.set_task_tags(t_id, [tag_v], db_path=db_path)
    database.add_task_link(t_id, "https://github.com", "Repo", db_path=db_path)
    database.create_log(t_id, "Comentario de log", db_path=db_path)

    # 2. Exportar a JSON
    json_exported = exporter.boards_to_json(db_path, board_id=b_id, include_tasks=True)

    # 3. Importar en una base de datos nueva y limpia
    clean_db = str(tmp_path / "clean.db")
    database.init_db(clean_db)

    boards, stats = importer.parse_boards_json(json_exported)
    imported_ids = importer.import_boards(boards, db_path=clean_db, include_tasks=True)

    assert len(imported_ids) == 1
    imp_b_id = imported_ids[0]

    imp_board = database.get_board(imp_b_id, clean_db)
    assert imp_board["name"] == "Tablero Origen"

    imp_cols = database.get_columns(imp_b_id, clean_db)
    assert len(imp_cols) == 1

    imp_tasks = database.get_tasks(imp_cols[0]["id"], clean_db)
    assert len(imp_tasks) == 1
    it = imp_tasks[0]
    assert it["title"] == "Tarea Principal"
    assert it["description"] == "Texto de prueba"
    assert it["due_date"] == "2026-10-01"
    assert it["tags"][0]["category"] == "Tipo" and it["tags"][0]["value"] == "Bug"
    assert it["links"][0]["url"] == "https://github.com"
    assert it["links"][0]["label"] == "Repo"

    imp_logs = database.get_logs(it["id"], clean_db)
    assert len(imp_logs) == 1
    assert imp_logs[0]["content"] == "Comentario de log"
