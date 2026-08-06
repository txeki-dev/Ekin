import database
from board_view import BoardViewWidget


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


def test_real_drop_inside_hover_expanded_column_sticks(qapp, db_path):
    board_id, (col_a, col_b) = _make_board_with_columns(db_path)
    database.set_column_collapsed(col_a, True, db_path)
    task_id = database.create_task(col_a, "Tarea", db_path=db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.handle_hover_expand_requested(col_a)
    # Simula que el drop realmente aterrizó dentro de la columna expandida por hover.
    board_view.handle_task_drop(task_id, col_a, 0)

    assert board_view._hover_expanded_column_id is None

    # Un finalize posterior (drag_ended tras el drop) no debe deshacer el drop real.
    board_view.finalize_hover_expand()
    assert _collapsed_state(board_id, col_a, db_path) is False


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
