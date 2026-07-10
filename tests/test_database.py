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
    database.set_task_tags(task_id, [{"text": "Bug", "color": "#ff0000"}], db_path=db_path)

    task = database.get_task(task_id, db_path)
    assert task["tags"] == [{"text": "Bug", "color": "#ff0000"}]


def test_update_task(db_path):
    board_id = database.create_board("Board", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Original", db_path=db_path)

    database.update_task(task_id, "Editada", "desc", "tag", "#abcdef", "2026-08-01", db_path=db_path)

    task = database.get_task(task_id, db_path)
    assert task["title"] == "Editada"
    assert task["description"] == "desc"
    assert task["due_date"] == "2026-08-01"


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

    database.set_task_tags(task_id, [{"text": "Uno", "color": "#111111"}], db_path=db_path)
    database.set_task_tags(task_id, [{"text": "Dos", "color": "#222222"}], db_path=db_path)

    tags = database.get_task_tags(task_id, db_path)
    assert len(tags) == 1
    assert tags[0]["text"] == "Dos"


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
    assert [l["id"] for l in logs] == [log1, log2]
    assert [l["content"] for l in logs] == ["Primero", "Segundo"]


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
    database.set_task_tags(task_id, [{"text": "Tag", "color": "#123456"}], db_path=db_path)
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
    assert copied_tasks[0]["tags"] == [{"text": "Tag", "color": "#123456"}]

    copied_logs = database.get_logs(copied_tasks[0]["id"], db_path)
    assert [l["content"] for l in copied_logs] == ["nota"]


def test_copy_board_duplicates_full_hierarchy(db_path):
    board_id = database.create_board("Original", "#654321", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    database.set_task_tags(task_id, [{"text": "Tag", "color": "#111111"}], db_path=db_path)
    database.create_log(task_id, "nota", db_path=db_path)

    new_board_id = database.copy_board(board_id, "Copia", "#654321", db_path=db_path)

    assert new_board_id != board_id
    new_columns = database.get_columns(new_board_id, db_path)
    assert len(new_columns) == 1
    assert new_columns[0]["id"] != col_id

    new_tasks = database.get_tasks(new_columns[0]["id"], db_path)
    assert len(new_tasks) == 1
    assert new_tasks[0]["id"] != task_id
    assert new_tasks[0]["tags"] == [{"text": "Tag", "color": "#111111"}]

    new_logs = database.get_logs(new_tasks[0]["id"], db_path)
    assert [l["content"] for l in new_logs] == ["nota"]

    # El tablero original sigue intacto
    assert len(database.get_columns(board_id, db_path)) == 1
