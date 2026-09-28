"""#58: reordenar tableros arrastrándolos en la barra lateral (persistido en boards.position)."""
from PySide6.QtCore import QMimeData, QPoint, Qt
from PySide6.QtGui import QDragEnterEvent, QDropEvent

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


def _board_drop_event(board_id, y, cls=QDropEvent):
    mime = QMimeData()
    mime.setData(BOARD_MIME, str(board_id).encode("utf-8"))
    ev = cls(QPoint(5, y), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    ev._keepalive = mime
    return ev


def test_dropping_a_board_on_another_reorders_sidebar_and_db(qapp, db_path):
    a, b, c = (database.create_board(n, db_path=db_path) for n in "ABC")
    sidebar = SidebarWidget(db_path=db_path)
    sidebar.select_board(b)
    selected = []
    sidebar.board_selected.connect(selected.append)
    target = sidebar.board_buttons[a]

    enter = _board_drop_event(c, 2, QDragEnterEvent)
    target.dragEnterEvent(enter)
    assert enter.isAccepted()
    target.dropEvent(_board_drop_event(c, 2))  # mitad superior -> antes de A

    assert list(sidebar.board_buttons) == [c, a, b]
    layout_ids = [sidebar.boards_layout.itemAt(i).widget().board_id for i in range(sidebar.boards_layout.count())]
    assert layout_ids == [c, a, b]
    assert _names(db_path) == ["C", "A", "B"]
    assert sidebar.active_board_id == b and selected == []  # no recarga el tablero activo

    sidebar.board_buttons[b].dropEvent(_board_drop_event(c, target.height() - 2))  # mitad inferior -> después
    assert list(sidebar.board_buttons) == [a, b, c]


def test_board_button_ignores_drag_of_itself(qapp, db_path):
    a = database.create_board("A", db_path=db_path)
    sidebar = SidebarWidget(db_path=db_path)
    enter = _board_drop_event(a, 2, QDragEnterEvent)
    enter.setAccepted(False)
    sidebar.board_buttons[a].dragEnterEvent(enter)
    assert not enter.isAccepted()
