"""#58: reordenar tableros arrastrándolos en la barra lateral (persistido en boards.position).
#150: la lista entera recibe el arrastre, con una línea en el hueco donde caerá el tablero."""
from PySide6.QtCore import QMimeData, QPoint, QPointF, Qt, QEvent
from PySide6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QMouseEvent

import database
from sidebar import SidebarWidget

BOARD_MIME = "application/x-ekin-board-id"


def _names(db_path, **kw):
    return [b["name"] for b in database.get_boards(db_path, **kw)]


def test_move_board_before_and_after_target_persists_order(db_path):
    a, b, c, d = (database.create_board(n, db_path=db_path) for n in "ABCD")

    database.move_board(d, a, after=False, db_path=db_path)
    assert _names(db_path) == ["D", "A", "B", "C"]

    database.move_board(d, b, after=True, db_path=db_path)
    assert _names(db_path) == ["A", "B", "D", "C"]

    database.move_board(c, c, db_path=db_path)  # sobre sí mismo: no-op
    assert _names(db_path) == ["A", "B", "D", "C"]


def test_boards_created_after_a_reorder_go_last(db_path):
    a, b = (database.create_board(n, db_path=db_path) for n in "AB")
    database.move_board(b, a, db_path=db_path)
    database.create_board("C", db_path=db_path)
    database.copy_board(a, "A copia", "#3b82f6", db_path=db_path)
    assert _names(db_path)[:3] == ["B", "A", "C"]
    assert len(_names(db_path)) == 4


def test_reorder_keeps_archived_boards_in_place(db_path):
    a, b, c = (database.create_board(n, db_path=db_path) for n in "ABC")
    database.set_board_archived(b, True, db_path)

    database.move_board(c, a, db_path=db_path)  # con B oculto
    assert _names(db_path) == ["C", "A"]
    assert _names(db_path, include_archived=True) == ["C", "A", "B"]


def _board_drag_event(board_id, y, cls=QDropEvent):
    mime = QMimeData()
    mime.setData(BOARD_MIME, str(board_id).encode("utf-8"))
    ev = cls(QPoint(20, int(y)), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    ev._keepalive = mime
    return ev


def _sidebar(qapp, db_path, names="ABC"):
    ids = [database.create_board(n, db_path=db_path) for n in names]
    sidebar = SidebarWidget(db_path=db_path)
    sidebar.resize(260, 700)
    sidebar.show()
    qapp.processEvents()
    return sidebar, sidebar.scroll_content, ids


def _layout_ids(sidebar):
    return [sidebar.boards_layout.itemAt(i).widget().board_id for i in range(sidebar.boards_layout.count())]


def test_dropping_a_board_reorders_sidebar_and_db(qapp, db_path):
    sidebar, board_list, (a, b, c) = _sidebar(qapp, db_path)
    sidebar.select_board(b)
    selected = []
    sidebar.board_selected.connect(selected.append)
    top_of_a = sidebar.board_buttons[a].geometry().top() + 2

    enter = _board_drag_event(c, top_of_a, QDragEnterEvent)
    board_list.dragEnterEvent(enter)
    assert enter.isAccepted() and board_list.drop_line.isVisible()
    board_list.dropEvent(_board_drag_event(c, top_of_a))  # por encima del centro de A -> antes de A

    assert list(sidebar.board_buttons) == [c, a, b]
    assert _layout_ids(sidebar) == [c, a, b]
    assert _names(db_path) == ["C", "A", "B"]
    assert sidebar.active_board_id == b and selected == []  # no recarga el tablero activo
    assert not board_list.drop_line.isVisible()


def test_a_board_can_be_dropped_in_a_gap_or_below_the_last_one(qapp, db_path):
    sidebar, board_list, (a, b, c) = _sidebar(qapp, db_path)
    gap = (sidebar.board_buttons[b].geometry().bottom() + sidebar.board_buttons[c].geometry().top()) / 2
    move = _board_drag_event(a, gap, QDragMoveEvent)
    board_list.dragMoveEvent(move)
    line = board_list.drop_line.geometry()
    assert move.isAccepted() and board_list.drop_line.isVisible()
    assert sidebar.board_buttons[b].geometry().bottom() <= line.center().y() <= sidebar.board_buttons[c].geometry().top()
    board_list.dropEvent(_board_drag_event(a, gap))
    assert _names(db_path) == ["B", "A", "C"]

    below = sidebar.board_buttons[c].geometry().bottom() + 40
    board_list.dropEvent(_board_drag_event(b, below))
    assert _names(db_path) == ["A", "C", "B"]


def test_dropping_a_board_where_it_already_is_does_nothing(qapp, db_path):
    sidebar, board_list, (a, b, c) = _sidebar(qapp, db_path)
    reorders = []
    board_list.board_reorder_requested.connect(lambda *args: reorders.append(args))
    own = sidebar.board_buttons[b].geometry()
    for y in (own.top() + 2, own.bottom() - 2):  # justo antes o justo después de sí mismo
        move = _board_drag_event(b, y, QDragMoveEvent)
        board_list.dragMoveEvent(move)
        assert move.isAccepted() and not board_list.drop_line.isVisible()
        board_list.dropEvent(_board_drag_event(b, y))
    assert reorders == [] and _names(db_path) == ["A", "B", "C"]


def test_board_button_leaves_board_drags_to_the_list(qapp, db_path):
    sidebar, _, (a, b, _c) = _sidebar(qapp, db_path)
    enter = _board_drag_event(a, 2, QDragEnterEvent)
    enter.setAccepted(False)
    sidebar.board_buttons[b].dragEnterEvent(enter)
    assert not enter.isAccepted()  # sube a BoardList, que dibuja la línea


def _mouse(kind, pos, buttons=Qt.LeftButton):
    return QMouseEvent(kind, QPointF(pos), QPointF(pos), Qt.LeftButton, buttons, Qt.NoModifier)


def test_a_board_is_selected_on_release_not_when_pressed_to_drag(qapp, db_path):
    """#150: pulsar para arrastrar abría el tablero antes de empezar el arrastre."""
    sidebar, _, (a, b, _c) = _sidebar(qapp, db_path)
    sidebar.select_board(a)
    btn = sidebar.board_buttons[b]
    centre = btn.rect().center()

    btn.mousePressEvent(_mouse(QEvent.MouseButtonPress, centre))
    assert sidebar.active_board_id == a
    btn.mouseReleaseEvent(_mouse(QEvent.MouseButtonRelease, centre, Qt.NoButton))
    assert sidebar.active_board_id == b
