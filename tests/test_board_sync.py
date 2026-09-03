import os
import json
import pytest

import database
import board_sync


@pytest.fixture
def sync_test_db(tmp_path):
    """Crea una base de datos temporal para pruebas de sincronización."""
    db_file = str(tmp_path / "sync_test.db")
    database.init_db(db_file)
    board_id = database.create_board("Tablero Sincronizado", color="#3b82f6", db_path=db_file)
    col1_id = database.create_column(board_id, "Por hacer", color="#3b82f6", db_path=db_file)
    col2_id = database.create_column(board_id, "Hecho", color="#10b981", db_path=db_file)

    task1_id = database.create_task(col1_id, "Tarea 1", description="Detalles tarea 1", db_path=db_file)
    task2_id = database.create_task(col2_id, "Tarea 2", description="Detalles tarea 2", db_path=db_file)

    database.create_log(task1_id, "<p>Primer comentario</p>", db_path=db_file)
    database.add_task_link(task1_id, "https://github.com", "Repositorio", db_path=db_file)

    return {
        "db_path": db_file,
        "board_id": board_id,
        "col1_id": col1_id,
        "col2_id": col2_id,
        "task1_id": task1_id,
        "task2_id": task2_id,
        "tmp_path": tmp_path,
    }


def test_export_board_to_sync_dict(sync_test_db):
    """Verifica que export_board_to_sync_dict serializa correctamente todos los campos y UUIDs."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]

    data = board_sync.export_board_to_sync_dict(board_id, db_path)
    assert data["format"] == "ekin_shared_board"
    assert data["board_name"] == "Tablero Sincronizado"
    assert len(data["columns"]) == 2
    assert len(data["tasks"]) == 2

    t1 = next(t for t in data["tasks"] if t["title"] == "Tarea 1")
    assert t1["description"] == "Detalles tarea 1"
    assert len(t1["logs"]) == 1
    assert "Primer comentario" in t1["logs"][0]["content"]
    assert len(t1["links"]) == 1
    assert t1["links"][0]["url"] == "https://github.com"


def test_sync_initial_export_creates_file(sync_test_db):
    """Verifica que la primera sincronización exporta el tablero al archivo .ekboard."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "exported"
    assert os.path.exists(sync_file)

    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    assert file_data["board_name"] == "Tablero Sincronizado"
    assert len(file_data["tasks"]) == 2


def test_sync_up_to_date_when_no_changes(sync_test_db):
    """Verifica que si no hay cambios, el estado devuelto es up_to_date."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    # Primera sincronización (export)
    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # Segunda sincronización sin tocar nada
    res2 = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res2.status == "up_to_date"


def test_sync_exports_local_changes_to_file(sync_test_db):
    """Verifica que al modificar una tarea localmente, la sincronización actualiza el archivo compartido."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # Modificar tarea local
    task1_id = sync_test_db["task1_id"]
    database.update_task(task1_id, "Tarea 1 - Modificada", "Nueva descripción", "", "#6b7280", "2026-09-20", db_path)

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "exported"

    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    t1 = next(t for t in file_data["tasks"] if t["title"] == "Tarea 1 - Modificada")
    assert t1["description"] == "Nueva descripción"


def test_sync_imports_remote_changes_cleanly(sync_test_db):
    """Verifica que cambios en el archivo remoto sin cambios locales se importan directamente."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # Modificar el archivo simulando que un compañero en OneDrive añadió una tarea
    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)

    new_task = {
        "task_uuid": "remote-task-uuid-999",
        "column_uuid": file_data["columns"][0]["column_uuid"],
        "title": "Tarea Remota de OneDrive",
        "description": "Creada por un compañero",
        "tag_text": "Remoto",
        "tag_color": "#ef4444",
        "position": 5,
        "due_date": None,
        "due_time": None,
        "recurrence": "none",
        "version": 1,
        "updated_at": "2026-09-03 18:00:00",
        "tags": [],
        "links": [],
        "logs": [{"content": "<p>Log remoto</p>", "created_at": "2026-09-03 18:00:00"}],
    }
    file_data["tasks"].append(new_task)

    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "imported"
    assert res.tasks_imported >= 1

    # Comprobar que la tarea remota existe en la BD local
    tasks_col1 = database.get_tasks(sync_test_db["col1_id"], db_path)
    assert any(t["title"] == "Tarea Remota de OneDrive" for t in tasks_col1)


def test_sync_collision_no_data_loss_preserves_in_journal(sync_test_db):
    """Verifica que ante una edición concurrente en la misma tarea, no se pierde información:
    se adopta la descripción más reciente y la anterior se archiva en el chat/diario de la tarea."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # 1. Modificación local
    task1_id = sync_test_db["task1_id"]
    database.update_task(task1_id, "Tarea 1", "Mi versión local avanzada", "", "#6b7280", None, db_path)

    # 2. Modificación remota en el archivo (simulando OneDrive)
    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)

    for t in file_data["tasks"]:
        if t["title"] == "Tarea 1":
            t["description"] = "Versión remota del compañero en OneDrive"
            t["version"] = 5
            t["updated_at"] = "2026-09-03 19:30:00"  # Más reciente

    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "merged"
    assert res.conflicts_resolved >= 1

    # Verificar que en la tarea local se adoptó la más reciente
    updated_t1 = database.get_task(task1_id, db_path)
    assert updated_t1["description"] == "Versión remota del compañero en OneDrive"

    # Verificar política NO-DATA-LOSS: la versión local anterior está guardada en los logs del chat!
    logs = database.get_logs(task1_id, db_path)
    assert any("Mi versión local avanzada" in entry["content"] for entry in logs)
    assert any("Sincronización OneDrive" in entry["content"] for entry in logs)


def test_unlink_board_sync(sync_test_db):
    """Verifica que desvincular un tablero borra sync_path y lo deja offline."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert database.get_board_sync_info(board_id, db_path)["sync_path"] == sync_file

    database.unlink_board_sync(board_id, db_path)
    assert database.get_board_sync_info(board_id, db_path)["sync_path"] is None


def test_sync_concurrent_additions_both_preserved(sync_test_db):
    """Verifica que si local y remoto añaden tareas diferentes simultáneamente,
    la sincronización conserva ambas sin pérdida."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    col1_id = sync_test_db["col1_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # 1. Local añade Tarea L
    database.create_task(col1_id, "Tarea Local Nueva", description="Hecha en local", db_path=db_path)

    # 2. Remoto añade Tarea R
    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)

    file_data["tasks"].append({
        "task_uuid": "task-uuid-remota-xyz",
        "column_uuid": file_data["columns"][0]["column_uuid"],
        "title": "Tarea Remota Nueva",
        "description": "Hecha en OneDrive",
        "tag_text": "",
        "tag_color": "#6b7280",
        "position": 10,
        "version": 1,
        "updated_at": "2026-09-03 20:00:00",
    })

    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "merged"

    tasks = database.get_tasks(col1_id, db_path)
    titles = [t["title"] for t in tasks]
    assert "Tarea Local Nueva" in titles
    assert "Tarea Remota Nueva" in titles


def test_sync_corrupted_json_returns_error_safely(sync_test_db):
    """Verifica que un archivo .ekboard corrupto no rompe la aplicación ni corrompe la BD."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # Corromper el archivo
    with open(sync_file, "w", encoding="utf-8") as f:
        f.write("ESTO NO ES UN JSON {{{")

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "error"
    assert "dañado" in res.message or "JSON" in res.message


def test_premerge_backup_created_on_merge(sync_test_db):
    """Verifica que se genera una instantánea de respaldo en backups/ al detectar cambios remotos."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    board_sync.sync_board_with_file(board_id, sync_file, db_path)

    # Añadir cambio remoto
    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    file_data["tasks"][0]["title"] = "Tarea 1 - Modificada en OneDrive"
    file_data["tasks"][0]["version"] = 10
    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status == "imported"

    backup_dir = os.path.join(os.getcwd(), "backups")
    assert os.path.exists(backup_dir)
    backups = [f for f in os.listdir(backup_dir) if f.startswith(f"sync_premerge_board_{board_id}")]
    assert len(backups) >= 1


def test_sync_remote_deletion_does_not_resurrect(sync_test_db):
    """Verifica que si un colaborador elimina una tarea en OneDrive, no se resucita al sincronizar (Bug 3)."""
    db_path = sync_test_db["db_path"]
    board_id = sync_test_db["board_id"]
    col1_id = sync_test_db["col1_id"]
    col2_id = sync_test_db["col2_id"]
    sync_file = str(sync_test_db["tmp_path"] / "tablero_compartido.ekboard")

    # Sincronización inicial: ambas tareas existen y se marcan synced_version > 0
    board_sync.sync_board_with_file(board_id, sync_file, db_path)
    initial_total = len(database.get_tasks(col1_id, db_path)) + len(database.get_tasks(col2_id, db_path))
    assert initial_total == 2

    # El colaborador elimina una de las tareas del archivo .ekboard en OneDrive
    with open(sync_file, "r", encoding="utf-8") as f:
        file_data = json.load(f)

    # Eliminar la primera tarea en el archivo compartido
    del file_data["tasks"][0]
    assert len(file_data["tasks"]) == 1

    with open(sync_file, "w", encoding="utf-8") as f:
        json.dump(file_data, f, indent=2)

    # Sincronizar localmente: debe eliminarse localmente, NO resucitar en el archivo
    res = board_sync.sync_board_with_file(board_id, sync_file, db_path)
    assert res.status in ("imported", "merged")

    remaining_total = len(database.get_tasks(col1_id, db_path)) + len(database.get_tasks(col2_id, db_path))
    assert remaining_total == 1

    # Verificar que el archivo compartido sigue teniendo solo 1 tarea (sin resucitar)
    with open(sync_file, "r", encoding="utf-8") as f:
        reloaded_file = json.load(f)
    assert len(reloaded_file["tasks"]) == 1


