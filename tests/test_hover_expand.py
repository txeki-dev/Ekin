import database
from board_view import BoardViewWidget
from widgets import TaskCard


def _collapsed_state(board_id, column_id, db_path):
    for col in database.get_columns(board_id, db_path):
        if col["id"] == column_id:
            return bool(col["collapsed"])
    raise AssertionError(f"column {column_id} not found on board {board_id}")


def _make_board_with_columns(db_path, n=2):
    board_id = database.create_board("Tablero", db_path=db_path)
    column_ids = [
        database.create_column(board_id, f"Col{i}", db_path=db_path) for i in range(n)
    ]
    return board_id, column_ids


def test_hover_expand_persists_and_tracks_column(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    assert board_view._hover_expanded_column_id is None

    board_view.handle_hover_expand_requested(col_a)

    assert board_view._hover_expanded_column_id == col_a
    assert _collapsed_state(board_id, col_a, db_path) is False


def test_finalize_without_drop_recollapses(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    board_view.finalize_hover_expand()

    assert board_view._hover_expanded_column_id is None
    assert _collapsed_state(board_id, col_a, db_path) is True


def test_finalize_is_noop_when_nothing_pending(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    # No debe reventar ni tocar la BD si no hay ninguna expansión de hover pendiente.
    board_view.finalize_hover_expand()
    assert board_view._hover_expanded_column_id is None


def test_real_drop_inside_hover_expanded_column_still_recollapses(qapp, db_path):
    """Por petición del usuario: incluso si el drop aterriza DENTRO de la columna
    expandida por hover, esta debe replegarse igual que si el drag hubiera
    terminado sin soltar ahí -- handle_task_drop ya no limpia el tracking por su
    cuenta; es finalize_hover_expand() (disparado por TaskCard.drag_ended tras
    QDrag.exec()) quien decide el estado final, siempre replegando."""
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)
    task_id = database.create_task(col_a, "Tarea", db_path=db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    # Simula que el drop realmente aterrizó dentro de la columna expandida por hover.
    board_view.handle_task_drop(task_id, col_a, 0)

    # El tracking NO se limpia en el propio drop: sigue pendiente de finalize_hover_expand.
    assert board_view._hover_expanded_column_id == col_a

    # drag_ended (QDrag.exec() ha devuelto el control) dispara el repliegue.
    board_view.finalize_hover_expand()

    assert board_view._hover_expanded_column_id is None
    assert _collapsed_state(board_id, col_a, db_path) is True
    # La tarea sigue en la columna -- solo se oculta al estar colapsada, no se pierde ni se mueve.
    assert [t["id"] for t in database.get_tasks(col_a, db_path)] == [task_id]


def test_hover_expand_switches_between_two_collapsed_columns(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)
    database.set_column_collapsed(col_b, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    assert _collapsed_state(board_id, col_a, db_path) is False

    board_view.handle_hover_expand_requested(col_b)

    assert board_view._hover_expanded_column_id == col_b
    assert _collapsed_state(board_id, col_a, db_path) is True
    assert _collapsed_state(board_id, col_b, db_path) is False


def test_hover_expand_same_column_twice_is_noop(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    board_view.handle_hover_expand_requested(col_a)  # Repetido: no debe re-persistir ni resetear nada

    assert board_view._hover_expanded_column_id == col_a
    assert _collapsed_state(board_id, col_a, db_path) is False


def test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(qapp, db_path):
    """Si el drop real aterriza en OTRA columna (no en la expandida por hover),
    handle_task_drop no debe limpiar el tracking: le toca a finalize_hover_expand
    (disparado por TaskCard.drag_ended al terminar el arrastre) replegarla."""
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)
    task_id = database.create_task(col_b, "Tarea", db_path=db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    board_view.handle_task_drop(task_id, col_b, 0)

    assert board_view._hover_expanded_column_id == col_a
    assert _collapsed_state(board_id, col_a, db_path) is False

    board_view.finalize_hover_expand()

    assert board_view._hover_expanded_column_id is None
    assert _collapsed_state(board_id, col_a, db_path) is True


def test_hover_expand_never_touches_other_columns_widgets(qapp, db_path):
    """Regresión del crash real reportado en producción: al soltar una tarjeta tras un
    hover-expand, la app se cerraba. Causa: handle_hover_expand_requested/
    finalize_hover_expand llamaban a load_board() completo, que hace deleteLater()
    sobre TODAS las columnas -- incluida la columna de ORIGEN del drag en curso (cuyo
    TaskCard seguía "vivo" en la pila de un QDrag.exec() real). Este test verifica que
    la columna A (origen, desplegada, con una tarea real) nunca se toca -- ni su
    ColumnWidget ni su TaskCard cambian de identidad -- durante todo el ciclo
    hover-expand -> finalize de la columna B (destino, colapsada). Con la
    implementación basada en load_board() este test falla (column_widgets[col_a] deja
    de ser la misma instancia); con _rebuild_single_column() pasa."""
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    task_id = database.create_task(col_a, "Tarea en curso de arrastre", db_path=db_path)
    database.set_column_collapsed(col_b, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    old_col_a_widget = board_view.column_widgets[col_a]
    old_task_card = next(
        c for c in old_col_a_widget.findChildren(TaskCard) if c.task_id == task_id
    )

    # --- hover-expand de B: A (origen del "drag") no debe tocarse ---
    board_view.handle_hover_expand_requested(col_b)

    assert board_view.column_widgets[col_a] is old_col_a_widget
    assert old_task_card in old_col_a_widget.findChildren(TaskCard)

    # B sí debe haberse reconstruido: nueva instancia, ahora desplegada.
    assert board_view.column_widgets[col_b] is not None
    assert board_view.column_widgets[col_b].collapsed is False

    # --- finalize (drag termina sin drop en B): A sigue sin tocarse ---
    board_view.finalize_hover_expand()

    assert board_view.column_widgets[col_a] is old_col_a_widget
    assert old_task_card in old_col_a_widget.findChildren(TaskCard)
    assert board_view.column_widgets[col_b].collapsed is True


def test_hover_expand_column_widget_swapped_at_same_layout_position(qapp, db_path):
    """La columna B reconstruida debe ocupar exactamente el mismo índice que tenía
    en columns_layout -- el layout del tablero no debe reordenarse."""
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_b, True, db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    old_col_b_widget = board_view.column_widgets[col_b]
    index_before = board_view.columns_layout.indexOf(old_col_b_widget)

    board_view.handle_hover_expand_requested(col_b)

    new_col_b_widget = board_view.column_widgets[col_b]
    assert new_col_b_widget is not old_col_b_widget
    assert board_view.columns_layout.indexOf(new_col_b_widget) == index_before
    # La columna A no se movió ni se recreó.
    assert board_view.columns_layout.indexOf(board_view.column_widgets[col_a]) != -1
