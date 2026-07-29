import os
import sqlite3
import database


# --- init_db ---

def test_init_db_creates_expected_tables(db_path):
    conn = sqlite3.connect(db_path)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert {"boards", "columns", "tasks", "task_logs", "task_tags"} <= tables


def test_init_db_is_idempotent(db_path):
    board_id = database.create_board("Persistente", db_path=db_path)
    database.init_db(db_path)  # No debe borrar datos ni fallar al re-ejecutarse
    assert database.get_board(board_id, db_path) is not None


# --- Boards ---

def test_create_and_get_board(db_path):
    board_id = database.create_board("Trabajo", "#111111", db_path=db_path)
    board = database.get_board(board_id, db_path)
    assert board["name"] == "Trabajo"
    assert board["color"] == "#111111"


def test_get_boards_returns_all_ordered_by_id(db_path):
    id1 = database.create_board("A", db_path=db_path)
    id2 = database.create_board("B", db_path=db_path)
    boards = database.get_boards(db_path)
    assert [b["id"] for b in boards] == [id1, id2]


def test_update_board(db_path):
    board_id = database.create_board("Original", "#000000", db_path=db_path)
    database.update_board(board_id, "Renombrado", "#ffffff", db_path=db_path)
    board = database.get_board(board_id, db_path)
    assert board["name"] == "Renombrado"
    assert board["color"] == "#ffffff"


def test_delete_board_cascades_to_columns_and_tasks(db_path):
    board_id = database.create_board("Efímero", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    database.create_log(task_id, "nota", db_path=db_path)

    database.delete_board(board_id, db_path=db_path)

    assert database.get_board(board_id, db_path) is None
    assert database.get_columns(board_id, db_path) == []
    assert database.get_task(task_id, db_path) is None
    assert database.get_logs(task_id, db_path) == []


# --- Columns ---

def test_create_column_assigns_incrementing_positions(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    c1 = database.create_column(board_id, "Uno", db_path=db_path)
    c2 = database.create_column(board_id, "Dos", db_path=db_path)
    columns = database.get_columns(board_id, db_path)
    assert [c["id"] for c in columns] == [c1, c2]
    assert [c["position"] for c in columns] == [0, 1]


def test_update_column(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Nombre", "#111111", db_path=db_path)
    database.update_column(col_id, "Nuevo Nombre", "#222222", db_path=db_path)
    col = database.get_columns(board_id, db_path)[0]
    assert col["name"] == "Nuevo Nombre"
    assert col["color"] == "#222222"


def test_update_column_positions_reorders(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    c1 = database.create_column(board_id, "Uno", db_path=db_path)
    c2 = database.create_column(board_id, "Dos", db_path=db_path)
    database.update_column_positions([(c1, 1), (c2, 0)], db_path=db_path)
    columns = database.get_columns(board_id, db_path)
    assert [c["id"] for c in columns] == [c2, c1]


def test_delete_column_cascades_to_tasks(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)

    database.delete_column(col_id, db_path=db_path)

    assert database.get_task(task_id, db_path) is None


# --- Tasks ---

def test_create_task_assigns_incrementing_positions(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    t1 = database.create_task(col_id, "Uno", db_path=db_path)
    t2 = database.create_task(col_id, "Dos", db_path=db_path)
    tasks = database.get_tasks(col_id, db_path)
    assert [t["id"] for t in tasks] == [t1, t2]
    assert [t["position"] for t in tasks] == [0, 1]


def test_get_task_includes_tags(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    tag_value_id = database.get_or_create_tag_value("Estado", "Bug", "#ff0000", db_path=db_path)
    database.set_task_tags(task_id, [tag_value_id], db_path=db_path)

    task = database.get_task(task_id, db_path)
    estado_cat_id = next(c["id"] for c in database.get_tag_categories(db_path) if c["name"] == "Estado")
    assert task["tags"] == [
        {"tag_value_id": tag_value_id, "category_id": estado_cat_id,
         "category": "Estado", "value": "Bug", "color": "#ff0000"}
    ]


def test_update_task(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Original", db_path=db_path)

    database.update_task(task_id, "Editada", "desc", "tag", "#abcdef", "2026-08-01", db_path=db_path)

    task = database.get_task(task_id, db_path)
    assert task["title"] == "Editada"
    assert task["description"] == "desc"
    assert task["due_date"] == "2026-08-01"


def test_update_task_due_date_sets_and_clears(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", due_date="2026-01-01", db_path=db_path)

    database.update_task_due_date(task_id, "2026-02-02", db_path=db_path)
    assert database.get_task(task_id, db_path)["due_date"] == "2026-02-02"

    # No toca el resto de campos
    assert database.get_task(task_id, db_path)["title"] == "Tarea"

    database.update_task_due_date(task_id, None, db_path=db_path)
    assert database.get_task(task_id, db_path)["due_date"] is None


def test_delete_task(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)

    database.delete_task(task_id, db_path=db_path)

    assert database.get_task(task_id, db_path) is None


# --- Task tags ---

def test_set_task_tags_replaces_previous_tags(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)

    uno_id = database.get_or_create_tag_value("Prioridad", "Uno", "#111111", db_path=db_path)
    dos_id = database.get_or_create_tag_value("Prioridad", "Dos", "#222222", db_path=db_path)

    database.set_task_tags(task_id, [uno_id], db_path=db_path)
    database.set_task_tags(task_id, [dos_id], db_path=db_path)

    tags = database.get_task_tags(task_id, db_path)
    assert len(tags) == 1
    assert tags[0]["value"] == "Dos"


# --- Tag categories & values (catálogo de etiquetas estructuradas) ---

def test_get_or_create_tag_value_is_idempotent(db_path):
    id1 = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    id2 = database.get_or_create_tag_value("prioridad", "alta", "#000000", db_path=db_path)

    assert id1 == id2
    # El color original se conserva; no se sobrescribe en la segunda llamada
    tag = database.get_tag_value(id1, db_path)
    assert tag["color"] == "#ef4444"
    assert tag["category"] == "Prioridad"
    assert tag["value"] == "Alta"


def test_get_tag_categories_and_values(db_path):
    database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    database.get_or_create_tag_value("Prioridad", "Baja", "#22c55e", db_path=db_path)
    database.get_or_create_tag_value("Estado", "Bloqueado", "#f97316", db_path=db_path)

    categories = database.get_tag_categories(db_path)
    assert [c["name"] for c in categories] == ["Estado", "Prioridad"]

    prioridad = next(c for c in categories if c["name"] == "Prioridad")
    values = database.get_tag_values(prioridad["id"], db_path)
    assert sorted(v["value"] for v in values) == ["Alta", "Baja"]


# --- Task positions (drag & drop) ---

def test_update_task_positions_moves_between_columns(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_a = database.create_column(board_id, "A", db_path=db_path)
    col_b = database.create_column(board_id, "B", db_path=db_path)
    task_id = database.create_task(col_a, "Tarea", db_path=db_path)

    database.update_task_positions([(task_id, col_b, 0)], db_path=db_path)

    assert database.get_tasks(col_a, db_path) == []
    moved = database.get_tasks(col_b, db_path)
    assert len(moved) == 1 and moved[0]["id"] == task_id


# --- Task logs (diario) ---

def test_create_log_and_get_logs_ordered(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)

    log1 = database.create_log(task_id, "Primero", db_path=db_path)
    log2 = database.create_log(task_id, "Segundo", db_path=db_path)

    logs = database.get_logs(task_id, db_path)
    assert [lg["id"] for lg in logs] == [log1, log2]
    assert [lg["content"] for lg in logs] == ["Primero", "Segundo"]


def test_create_log_updates_task_updated_at(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    original_updated_at = database.get_task(task_id, db_path)["updated_at"]

    database.create_log(task_id, "nota", db_path=db_path)

    assert database.get_task(task_id, db_path)["updated_at"] >= original_updated_at


def test_delete_log(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    log_id = database.create_log(task_id, "nota", db_path=db_path)

    database.delete_log(log_id, db_path=db_path)

    assert database.get_logs(task_id, db_path) == []


# --- Mover / copiar columnas entre tableros ---

def test_move_column_to_board(db_path):
    board_a = database.create_board("A", db_path=db_path)
    board_b = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_a, "Col", db_path=db_path)

    database.move_column_to_board(col_id, board_b, db_path=db_path)

    assert database.get_columns(board_a, db_path) == []
    moved = database.get_columns(board_b, db_path)
    assert len(moved) == 1 and moved[0]["id"] == col_id


def test_copy_column_to_board_duplicates_tasks_tags_and_logs(db_path):
    board_a = database.create_board("A", db_path=db_path)
    board_b = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_a, "Col", "#ababab", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    tag_value_id = database.get_or_create_tag_value("Estado", "Tag", "#123456", db_path=db_path)
    database.set_task_tags(task_id, [tag_value_id], db_path=db_path)
    database.create_log(task_id, "nota", db_path=db_path)

    new_col_id = database.copy_column_to_board(col_id, board_b, db_path=db_path)

    # El original permanece intacto
    assert database.get_columns(board_a, db_path)[0]["id"] == col_id

    copied_col = database.get_columns(board_b, db_path)[0]
    assert copied_col["id"] == new_col_id
    assert copied_col["name"] == "Col"

    copied_tasks = database.get_tasks(new_col_id, db_path)
    assert len(copied_tasks) == 1
    assert copied_tasks[0]["id"] != task_id
    assert copied_tasks[0]["title"] == "Tarea"
    # La copia comparte la misma etiqueta del catálogo (no se duplica la definición)
    estado_cat_id = next(c["id"] for c in database.get_tag_categories(db_path) if c["name"] == "Estado")
    assert copied_tasks[0]["tags"] == [
        {"tag_value_id": tag_value_id, "category_id": estado_cat_id,
         "category": "Estado", "value": "Tag", "color": "#123456"}
    ]

    copied_logs = database.get_logs(copied_tasks[0]["id"], db_path)
    assert [lg["content"] for lg in copied_logs] == ["nota"]


def test_copy_board_duplicates_full_hierarchy(db_path):
    board_id = database.create_board("Original", "#654321", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    tag_value_id = database.get_or_create_tag_value("Estado", "Tag", "#111111", db_path=db_path)
    database.set_task_tags(task_id, [tag_value_id], db_path=db_path)
    database.create_log(task_id, "nota", db_path=db_path)

    new_board_id = database.copy_board(board_id, "Copia", "#654321", db_path=db_path)

    assert new_board_id != board_id
    new_columns = database.get_columns(new_board_id, db_path)
    assert len(new_columns) == 1
    assert new_columns[0]["id"] != col_id

    new_tasks = database.get_tasks(new_columns[0]["id"], db_path)
    assert len(new_tasks) == 1
    assert new_tasks[0]["id"] != task_id
    estado_cat_id = next(c["id"] for c in database.get_tag_categories(db_path) if c["name"] == "Estado")
    assert new_tasks[0]["tags"] == [
        {"tag_value_id": tag_value_id, "category_id": estado_cat_id,
         "category": "Estado", "value": "Tag", "color": "#111111"}
    ]

    new_logs = database.get_logs(new_tasks[0]["id"], db_path)
    assert [lg["content"] for lg in new_logs] == ["nota"]

    # El tablero original sigue intacto
    assert len(database.get_columns(board_id, db_path)) == 1


# --- get_task_tags_bulk ---

def test_get_task_tags_bulk_matches_single_and_groups(db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    t1 = database.create_task(col_id, "T1", db_path=db_path)
    t2 = database.create_task(col_id, "T2", db_path=db_path)
    t3 = database.create_task(col_id, "T3", db_path=db_path)  # sin etiquetas
    alta = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    area = database.get_or_create_tag_value("Área", "Backend", "#3b82f6", db_path=db_path)
    database.set_task_tags(t1, [alta, area], db_path=db_path)
    database.set_task_tags(t2, [alta], db_path=db_path)

    bulk = database.get_task_tags_bulk([t1, t2, t3], db_path)
    # Idéntico a la consulta individual, para cada tarea
    for tid in (t1, t2, t3):
        assert bulk[tid] == database.get_task_tags(tid, db_path)
    assert bulk[t3] == []
    # Entrada vacía es segura
    assert database.get_task_tags_bulk([], db_path) == {}


# --- get_scheduled_tasks / get_task_board_id ---

def test_get_scheduled_tasks_filters_by_range_and_board(db_path):
    b1 = database.create_board("B1", db_path=db_path)
    c1 = database.create_column(b1, "Col", db_path=db_path)
    b2 = database.create_board("B2", db_path=db_path)
    c2 = database.create_column(b2, "Col", db_path=db_path)

    database.create_task(c1, "Sin fecha", db_path=db_path)
    t_low = database.create_task(c1, "2026-01-10", due_date="2026-01-10", db_path=db_path)
    t_mid = database.create_task(c2, "2026-01-15", due_date="2026-01-15", db_path=db_path)
    t_high = database.create_task(c1, "2026-01-30", due_date="2026-01-30", db_path=db_path)

    # Solo las que tienen fecha, ordenadas ascendentemente
    allsched = database.get_scheduled_tasks(db_path=db_path)
    assert [t["id"] for t in allsched] == [t_low, t_mid, t_high]
    assert allsched[0]["board_name"] == "B1" and allsched[0]["board_color"]

    # Rango inclusivo
    mid = database.get_scheduled_tasks("2026-01-11", "2026-01-20", db_path=db_path)
    assert [t["id"] for t in mid] == [t_mid]

    # Filtro por tablero
    only_b1 = database.get_scheduled_tasks(board_id=b1, db_path=db_path)
    assert {t["id"] for t in only_b1} == {t_low, t_high}


def test_get_task_board_id(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "Col", db_path=db_path)
    t = database.create_task(c, "T", db_path=db_path)
    assert database.get_task_board_id(t, db_path) == b
    assert database.get_task_board_id(999999, db_path) is None


# --- app_settings (get_setting / set_setting) ---

def test_settings_get_default_set_and_upsert(db_path):
    assert database.get_setting("missing", "fallback", db_path) == "fallback"
    database.set_setting("ics_sync_path", "/a/b.ics", db_path)
    assert database.get_setting("ics_sync_path", "", db_path) == "/a/b.ics"
    database.set_setting("ics_sync_path", "/c/d.ics", db_path)  # upsert, no duplica
    assert database.get_setting("ics_sync_path", "", db_path) == "/c/d.ics"


# --- db_path se resuelve en tiempo de llamada (no congelado al importar) ---

def test_db_name_is_resolved_at_call_time(tmp_path, monkeypatch):
    """Reasignar database.DB_NAME debe ser respetado por TODAS las funciones cuando
    se llaman sin db_path explícito (el arreglo P1). monkeypatch lo restaura al final."""
    target = str(tmp_path / "reassigned.db")
    monkeypatch.setattr(database, "DB_NAME", target)

    database.init_db()                    # sin db_path -> usa el nuevo DB_NAME
    board_id = database.create_board("X")  # sin db_path
    boards = database.get_boards()         # sin db_path

    assert [b["id"] for b in boards] == [board_id]
    assert os.path.exists(target)          # el archivo se creó en la ruta reasignada


# --- Subtareas / checklist ---

def _task(db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    return database.create_task(col_id, "T", db_path=db_path)


def test_create_and_get_subtasks_ordered(db_path):
    task_id = _task(db_path)
    s1 = database.create_subtask(task_id, "Uno", db_path=db_path)
    s2 = database.create_subtask(task_id, "Dos", db_path=db_path)
    subs = database.get_subtasks(task_id, db_path=db_path)
    assert [s["id"] for s in subs] == [s1, s2]
    assert [s["position"] for s in subs] == [0, 1]
    assert all(s["done"] == 0 for s in subs)


def test_set_subtask_done_toggles(db_path):
    task_id = _task(db_path)
    s1 = database.create_subtask(task_id, "Uno", db_path=db_path)
    database.set_subtask_done(s1, True, db_path=db_path)
    assert database.get_subtasks(task_id, db_path=db_path)[0]["done"] == 1
    database.set_subtask_done(s1, False, db_path=db_path)
    assert database.get_subtasks(task_id, db_path=db_path)[0]["done"] == 0


def test_update_subtask_title_and_delete(db_path):
    task_id = _task(db_path)
    s1 = database.create_subtask(task_id, "Original", db_path=db_path)
    database.update_subtask_title(s1, "Renombrada", db_path=db_path)
    assert database.get_subtasks(task_id, db_path=db_path)[0]["title"] == "Renombrada"
    database.delete_subtask(s1, db_path=db_path)
    assert database.get_subtasks(task_id, db_path=db_path) == []


def test_delete_task_cascades_subtasks(db_path):
    task_id = _task(db_path)
    database.create_subtask(task_id, "Uno", db_path=db_path)
    database.delete_task(task_id, db_path=db_path)
    assert database.get_subtasks(task_id, db_path=db_path) == []


def test_get_subtasks_progress_bulk(db_path):
    t1 = _task(db_path)
    board_id = database.create_board("B2", db_path=db_path)
    col2 = database.create_column(board_id, "C2", db_path=db_path)
    t2 = database.create_task(col2, "T2", db_path=db_path)
    t3 = database.create_task(col2, "T3", db_path=db_path)  # sin subtareas

    a = database.create_subtask(t1, "a", db_path=db_path)
    database.create_subtask(t1, "b", db_path=db_path)
    database.set_subtask_done(a, True, db_path=db_path)
    database.create_subtask(t2, "c", db_path=db_path)

    progress = database.get_subtasks_progress_bulk([t1, t2, t3], db_path=db_path)
    assert progress[t1] == (1, 2)
    assert progress[t2] == (0, 1)
    assert t3 not in progress                       # sin subtareas -> ausente
    assert database.get_subtasks_progress_bulk([], db_path=db_path) == {}


def test_get_tasks_exposes_subtask_progress(db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    t_with = database.create_task(col_id, "con", db_path=db_path)
    t_without = database.create_task(col_id, "sin", db_path=db_path)
    d = database.create_subtask(t_with, "x", db_path=db_path)
    database.create_subtask(t_with, "y", db_path=db_path)
    database.set_subtask_done(d, True, db_path=db_path)

    by_id = {t["id"]: t for t in database.get_tasks(col_id, db_path=db_path)}
    assert (by_id[t_with]["subtasks_done"], by_id[t_with]["subtasks_total"]) == (1, 2)
    assert (by_id[t_without]["subtasks_done"], by_id[t_without]["subtasks_total"]) == (0, 0)


def test_copy_board_duplicates_subtasks(db_path):
    board_id = database.create_board("Orig", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col_id, "T", db_path=db_path)
    done = database.create_subtask(task_id, "hecha", db_path=db_path)
    database.create_subtask(task_id, "pendiente", db_path=db_path)
    database.set_subtask_done(done, True, db_path=db_path)

    new_board_id = database.copy_board(board_id, "Copia", "#654321", db_path=db_path)
    new_col = database.get_columns(new_board_id, db_path=db_path)[0]
    new_task = database.get_tasks(new_col["id"], db_path=db_path)[0]

    copied = database.get_subtasks(new_task["id"], db_path=db_path)
    assert [(s["title"], s["done"]) for s in copied] == [("hecha", 1), ("pendiente", 0)]


# --- Búsqueda global (search_tasks) ---

def test_search_matches_title_and_description(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path)
    t_title = database.create_task(c, "Comprar leche", db_path=db_path)
    t_desc = database.create_task(c, "Otra", description="recordar la LECHE del super", db_path=db_path)
    database.create_task(c, "Nada que ver", db_path=db_path)

    ids = {t["id"] for t in database.search_tasks("leche", db_path=db_path)}
    assert ids == {t_title, t_desc}          # coincide en título y en descripción, sin distinguir mayúsculas
    assert database.search_tasks("inexistente", db_path=db_path) == []


def test_search_filter_by_board(db_path):
    b1 = database.create_board("B1", db_path=db_path)
    c1 = database.create_column(b1, "C", db_path=db_path)
    b2 = database.create_board("B2", db_path=db_path)
    c2 = database.create_column(b2, "C", db_path=db_path)
    t1 = database.create_task(c1, "tarea x", db_path=db_path)
    database.create_task(c2, "tarea x", db_path=db_path)

    res = database.search_tasks("tarea", board_id=b1, db_path=db_path)
    assert [t["id"] for t in res] == [t1]
    assert res[0]["board_name"] == "B1" and res[0]["board_color"]


def test_search_filter_by_tag_and_only_due(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path)
    tagged = database.create_task(c, "con tag", due_date="2026-09-01", db_path=db_path)
    database.create_task(c, "sin tag", db_path=db_path)
    tv = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444", db_path=db_path)
    database.set_task_tags(tagged, [tv], db_path=db_path)

    by_tag = database.search_tasks(tag_value_id=tv, db_path=db_path)
    assert [t["id"] for t in by_tag] == [tagged]
    assert by_tag[0]["tags"][0]["value"] == "Alta"    # resultados enriquecidos con etiquetas

    only_due = {t["id"] for t in database.search_tasks(only_due=True, db_path=db_path)}
    assert only_due == {tagged}
