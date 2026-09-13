"""Pruebas de los límites WIP por columna: persistencia y aviso visual en el header."""
import database
import styles
from board_view import BoardViewWidget


def test_wip_limit_roundtrip(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path, wip_limit=3)
    assert database.get_column(c, db_path)["wip_limit"] == 3
    database.update_column(c, "C", "#ffffff", db_path, wip_limit=5)
    assert database.get_column(c, db_path)["wip_limit"] == 5
    database.update_column(c, "C", "#ffffff", db_path, wip_limit=None)
    assert database.get_column(c, db_path)["wip_limit"] is None


def _board_with(db_path, wip_limit, n_tasks):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path, wip_limit=wip_limit)
    for i in range(n_tasks):
        database.create_task(c, f"T{i}", db_path=db_path)
    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(b)
    return bv, c


def test_column_widget_shows_wip_over_limit_in_danger(qapp, db_path):
    bv, c = _board_with(db_path, wip_limit=2, n_tasks=3)
    cw = bv.column_widgets[c]
    assert cw.wip_label.text() == "3/2"
    assert styles.COLORS["danger"] in cw.wip_label.styleSheet()


def test_column_widget_wip_under_limit_is_muted(qapp, db_path):
    bv, c = _board_with(db_path, wip_limit=3, n_tasks=2)
    cw = bv.column_widgets[c]
    assert cw.wip_label.text() == "2/3"
    assert styles.COLORS["danger"] not in cw.wip_label.styleSheet()


def test_column_widget_no_wip_label_when_unset(qapp, db_path):
    bv, c = _board_with(db_path, wip_limit=None, n_tasks=2)
    assert not hasattr(bv.column_widgets[c], "wip_label")
