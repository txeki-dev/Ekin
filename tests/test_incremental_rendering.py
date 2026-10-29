"""Pruebas unitarias para el renderizado incremental del tablero (mutaciones de elementos únicos)."""

from PySide6.QtWidgets import QInputDialog
import database
from board_view import BoardViewWidget
from widgets import TaskCard


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


def _cards(bv, column_id):
    """Tarjetas de la columna en el orden en que se ven (las retiradas ya no están en el layout)."""
    layout = bv.column_widgets[column_id].list_area.list_layout
    widgets_in_order = [layout.itemAt(i).widget() for i in range(layout.count())]
    return [w for w in widgets_in_order if isinstance(w, TaskCard)]


def _card_ids(bv, column_id):
    return [c.task_id for c in _cards(bv, column_id)]


def _card(bv, column_id, task_id):
    return next(c for c in _cards(bv, column_id) if c.task_id == task_id)


def test_drop_moves_only_the_dropped_card(qapp, db_path):
    """#157: soltar una tarjeta reconstruía las columnas de origen y destino; con 81 tarjetas en
    Done, eso congelaba la GUI ~1 s. Ahora solo se crea la tarjeta soltada: las columnas y el
    resto de tarjetas siguen siendo los mismos objetos, y el contador WIP se actualiza."""
    board_id = database.create_board("Board Drop Fast", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path, wip_limit=3)
    t1 = database.create_task(col_a, "T1", db_path=db_path)
    t2 = database.create_task(col_a, "T2", db_path=db_path)
    b1 = database.create_task(col_b, "B1", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)
    bv.show()
    qapp.processEvents()
    widget_a, widget_b = bv.column_widgets[col_a], bv.column_widgets[col_b]
    card_t2, card_b1 = _card(bv, col_a, t2), _card(bv, col_b, b1)

    bv.handle_task_drop(t1, col_b, 1)
    qapp.processEvents()

    assert bv.column_widgets[col_a] is widget_a and bv.column_widgets[col_b] is widget_b
    assert _card(bv, col_a, t2) is card_t2 and _card(bv, col_b, b1) is card_b1
    assert _card_ids(bv, col_a) == [t2]
    assert _card_ids(bv, col_b) == [b1, t1]
    assert _card(bv, col_b, t1).task_data["column_id"] == col_b
    assert _card(bv, col_b, t1).isVisible()
    assert widget_b.wip_label.text() == "2/3"
    assert [t["id"] for t in database.get_tasks(col_b, db_path)] == [b1, t1]


def test_drop_rebuilds_the_columns_when_the_board_on_screen_is_stale(qapp, db_path):
    """#157: el atajo solo vale si la pantalla refleja la BD. Si un agente cambió la columna
    durante el arrastre (el sondeo espera a que se suelte el ratón), se reconstruye."""
    board_id = database.create_board("Board Drop Stale", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Columna A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Columna B", "#10b981", db_path)
    t1 = database.create_task(col_a, "T1", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)
    agent_task = database.create_task(col_b, "Tarjeta del agente", db_path=db_path)

    bv.handle_task_drop(t1, col_b, 0)

    assert _card_ids(bv, col_b) == [t1, agent_task]


def test_drop_within_the_same_column_reorders_the_cards_on_screen(qapp, db_path):
    """#157: al reordenar dentro de una columna, la tarjeta sale y vuelve al mismo layout."""
    board_id = database.create_board("Board Drop Reorder", "#3b82f6", db_path)
    col = database.create_column(board_id, "Columna", "#3b82f6", db_path)
    t1, t2, t3 = (database.create_task(col, f"T{i}", db_path=db_path) for i in (1, 2, 3))

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)
    widget = bv.column_widgets[col]

    bv.handle_task_drop(t1, col, 2)

    assert bv.column_widgets[col] is widget
    assert _card_ids(bv, col) == [t2, t3, t1] == [t["id"] for t in database.get_tasks(col, db_path)]
