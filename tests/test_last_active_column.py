from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QMouseEvent

import database
import board_view as board_view_module
from board_view import BoardViewWidget
from widgets import ColumnWidget


def _make_board(db_path, n=2):
    board_id = database.create_board("Tablero", db_path=db_path)
    column_ids = [
        database.create_column(board_id, f"Col{i}", db_path=db_path) for i in range(n)
    ]
    return board_id, column_ids


# --- ColumnWidget.mousePressEvent -> column_activated ---

def test_column_widget_mouse_press_emits_column_activated(qapp):
    col_data = {
        "id": 5, "board_id": 1, "name": "Col", "color": "#3b82f6",
        "position": 0, "collapsed": 0, "task_count": 0,
    }
    col = ColumnWidget(col_data)
    emitted = []
    col.column_activated.connect(lambda cid: emitted.append(cid))

    ev = QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(1, 1), QPointF(1, 1),
        Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier,
    )
    col.mousePressEvent(ev)

    assert emitted == [5]


# --- BoardViewWidget: rastreo de la última columna activa ---

def test_column_background_click_sets_last_active_column(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    assert board_view._last_active_column_id is None

    board_view.column_widgets[col_b].column_activated.emit(col_b)

    assert board_view._last_active_column_id == col_b


def test_task_card_click_sets_last_active_column(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    task_id = database.create_task(col_b, "Tarea", db_path=db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    # Evitamos abrir el diálogo real de detalle (modal, .exec() bloquearía el test).
    opened = []
    board_view.open_task_details = lambda tid: opened.append(tid)

    board_view._handle_task_card_clicked(task_id, col_b)

    assert board_view._last_active_column_id == col_b
    assert opened == [task_id]


def test_add_task_sets_last_active_column(qapp, db_path, monkeypatch):
    # QInputDialog.getText es modal (.exec() bloquearía el test): simulamos "cancelado".
    monkeypatch.setattr(
        board_view_module.QInputDialog, "getText",
        staticmethod(lambda *args, **kwargs: (None, False)),
    )
    board_id, (col_a, col_b) = _make_board(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view.add_task(col_b)

    assert board_view._last_active_column_id == col_b


def test_quick_add_task_uses_last_active_column(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    calls = []
    board_view.add_task = lambda cid: calls.append(cid)
    board_view._last_active_column_id = col_b

    board_view.quick_add_task()

    assert calls == [col_b]


def test_quick_add_task_falls_back_to_first_column_when_nothing_active(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    calls = []
    board_view.add_task = lambda cid: calls.append(cid)
    # board_view._last_active_column_id sigue en None (nada se ha clicado aún).

    board_view.quick_add_task()

    assert calls == [col_a]


def test_quick_add_task_falls_back_when_last_active_column_belongs_to_another_board(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    _other_board_id, (other_col,) = _make_board(db_path, n=1)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    calls = []
    board_view.add_task = lambda cid: calls.append(cid)
    board_view._last_active_column_id = other_col  # pertenece a OTRO tablero

    board_view.quick_add_task()

    assert calls == [col_a]  # cae a la primera columna del tablero ACTIVO


def test_quick_add_task_falls_back_when_last_active_column_was_deleted(qapp, db_path):
    board_id, (col_a, col_b) = _make_board(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    board_view._last_active_column_id = col_b
    database.delete_column(col_b, db_path)

    calls = []
    board_view.add_task = lambda cid: calls.append(cid)

    board_view.quick_add_task()

    assert calls == [col_a]


def test_quick_add_task_noop_with_no_board_selected(qapp, db_path):
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(-1)

    calls = []
    board_view.add_task = lambda cid: calls.append(cid)

    board_view.quick_add_task()

    assert calls == []
