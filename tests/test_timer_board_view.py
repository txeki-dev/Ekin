from datetime import datetime, timedelta

import database
import styles
from board_view import BoardViewWidget
from widgets import TaskCard


def _make_board_with_task(db_path, started_at=None):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea", db_path=db_path)
    if started_at:
        database.set_task_timer_started(task_id, started_at, db_path=db_path)
    return board_id, col_id, task_id


def _card_for(board_view, col_id, task_id):
    return next(
        c for c in board_view.column_widgets[col_id].findChildren(TaskCard) if c.task_id == task_id
    )


def test_build_column_widget_applies_configured_threshold(qapp, db_path):
    database.set_setting("timer_alert_hours", "10", db_path)
    started = (datetime.now() - timedelta(hours=15)).isoformat()
    board_id, col_id, task_id = _make_board_with_task(db_path, started_at=started)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    card = _card_for(board_view, col_id, task_id)
    assert card._timer_alert_hours == 10
    # 15h de transcurrido >= 10h de umbral -> rojo
    assert styles.COLORS['danger'] in card.timer_badge_label.styleSheet()


def test_build_column_widget_defaults_threshold_when_unset(qapp, db_path):
    board_id, col_id, task_id = _make_board_with_task(db_path)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    card = _card_for(board_view, col_id, task_id)
    assert card._timer_alert_hours == 24


def test_refresh_timer_badges_updates_existing_card_without_reload(qapp, db_path):
    started = (datetime.now() - timedelta(hours=1)).isoformat()
    board_id, col_id, task_id = _make_board_with_task(db_path, started_at=started)

    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    card = _card_for(board_view, col_id, task_id)
    assert styles.COLORS['danger'] not in card.timer_badge_label.styleSheet()

    # No hay ningún cambio en BD: bajamos el umbral directamente en la tarjeta viva
    # (equivalente a que el tiempo transcurrido supere el umbral con el paso del tiempo)
    # y confirmamos que refresh_timer_badges() SÍ recalcula sin tocar column_widgets.
    old_col_widget = board_view.column_widgets[col_id]
    card._timer_alert_hours = 0  # cualquier tiempo transcurrido ya "supera" este umbral

    board_view.refresh_timer_badges()

    assert board_view.column_widgets[col_id] is old_col_widget  # no se reconstruyó nada
    assert styles.COLORS['danger'] in card.timer_badge_label.styleSheet()


def test_refresh_timer_badges_noop_on_board_with_no_timers(qapp, db_path):
    board_id, col_id, task_id = _make_board_with_task(db_path)
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(board_id)

    # No debe reventar aunque ninguna tarjeta tenga temporizador activo.
    board_view.refresh_timer_badges()

    card = _card_for(board_view, col_id, task_id)
    assert card.timer_container.isHidden()


def test_refresh_timer_badges_noop_on_welcome_screen(qapp, db_path):
    board_view = BoardViewWidget(db_path=db_path)
    board_view.load_board(-1)

    board_view.refresh_timer_badges()  # column_widgets está vacío: no debe reventar
