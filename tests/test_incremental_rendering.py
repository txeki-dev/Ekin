"""Pruebas unitarias para el renderizado incremental del tablero (mutaciones de elementos únicos)."""

from PySide6.QtWidgets import QInputDialog
import database
from board_view import BoardViewWidget


def test_create_quick_task_incremental_rendering(qapp, db_path):
    """create_quick_task solo debe reconstruir la columna de destino, preservando las demás intactas."""
    board_id = database.create_board("Board Incremental", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_a_before = bv.column_widgets[col_a]
    widget_b_before = bv.column_widgets[col_b]

    # Crear tarea rápida dirigida a Columna A
    bv._set_last_active_column(col_a)
    task_id = bv.create_quick_task("Tarea Incremental")
    assert task_id is not None

    # Columna B NO debe haberse destruido ni reconstruido (mismo objeto en memoria)
    assert bv.column_widgets[col_b] is widget_b_before

    # Columna A sí debe ser un nuevo widget que contiene la nueva tarea
    assert bv.column_widgets[col_a] is not widget_a_before
    tasks_a = database.get_tasks(col_a, db_path)
    assert any(t["id"] == task_id for t in tasks_a)


def test_handle_task_drop_same_column_incremental(qapp, db_path):
    """Mover una tarea dentro de la misma columna solo debe reconstruir esa columna."""
    board_id = database.create_board("Board Drop Same", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)

    t1 = database.create_task(col_a, "T1", db_path=db_path)
    database.create_task(col_a, "T2", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_b_before = bv.column_widgets[col_b]

    # Reordenar t1 al final de col_a
    bv.handle_task_drop(t1, col_a, 1)

    # Columna B intacta
    assert bv.column_widgets[col_b] is widget_b_before


def test_handle_task_drop_across_columns_incremental(qapp, db_path):
    """Mover una tarea entre dos columnas solo debe reconstruir origen y destino, dejando las terceras intactas."""
    board_id = database.create_board("Board Drop Across", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)
    col_c = database.create_column(board_id, "Columna C", "#f59e0b", db_path)

    t1 = database.create_task(col_a, "T1", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_c_before = bv.column_widgets[col_c]

    # Mover t1 de col_a a col_b
    bv.handle_task_drop(t1, col_b, 0)

    # Columna C intacta
    assert bv.column_widgets[col_c] is widget_c_before
    # Verificación en BD
    task_after = database.get_task(t1, db_path)
    assert task_after["column_id"] == col_b


def test_handle_column_collapse_incremental(qapp, db_path):
    """Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del tablero."""
    board_id = database.create_board("Board Collapse", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_b_before = bv.column_widgets[col_b]

    bv.handle_column_collapse(col_a)

    # Columna B intacta
    assert bv.column_widgets[col_b] is widget_b_before
    # Columna A ahora está colapsada
    assert bv.column_widgets[col_a].collapsed is True


def test_add_task_incremental(qapp, db_path, monkeypatch):
    """add_task debe reconstruir solo la columna destino y actualizar el chip de conteo."""
    board_id = database.create_board("Board Add Task", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_b_before = bv.column_widgets[col_b]

    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Nueva Tarea Incremental", True))
    bv.add_task(col_a)

    assert bv.column_widgets[col_b] is widget_b_before
    assert "1" in bv.board_counts_chip.text()
