"""Pruebas de la vista "Mi trabajo" (my_work_view):
- bucket_scheduled_tasks: lógica pura de agrupación por vencimiento (sin Qt).
- MyWorkWidget: construcción headless, listado y emisión de task_activated.
"""
from datetime import date, timedelta

from PySide6.QtWidgets import QPushButton

import database
from my_work_view import bucket_scheduled_tasks, MyWorkWidget


def _iso(days):
    return (date.today() + timedelta(days=days)).isoformat()


# --- Lógica pura de agrupación -------------------------------------------------

def test_bucket_scheduled_tasks_groups_by_due():
    today = date.today().isoformat()
    tasks = [
        {"id": 1, "due_date": _iso(-3)},   # atrasada
        {"id": 2, "due_date": today},      # hoy
        {"id": 3, "due_date": _iso(1)},    # mañana
        {"id": 4, "due_date": _iso(4)},    # esta semana
    ]
    buckets = bucket_scheduled_tasks(tasks, today)
    assert [t["id"] for t in buckets["overdue"]] == [1]
    assert [t["id"] for t in buckets["today"]] == [2]
    assert [t["id"] for t in buckets["tomorrow"]] == [3]
    assert [t["id"] for t in buckets["upcoming"]] == [4]


def test_bucket_scheduled_tasks_ignores_missing_due():
    today = date.today().isoformat()
    buckets = bucket_scheduled_tasks(
        [{"id": 1, "due_date": None}, {"id": 2, "due_date": ""}], today
    )
    assert all(not v for v in buckets.values())


# --- Widget headless -----------------------------------------------------------

def _seed(db_path):
    board_id = database.create_board("Proyecto", db_path=db_path)
    col_id = database.create_column(board_id, "To do", db_path=db_path)
    return board_id, col_id


def _item_texts(widget):
    return [
        b.text() for b in widget.findChildren(QPushButton)
        if b.objectName() == "NotificationItem"
    ]


def test_my_work_widget_lists_due_and_running(qapp, db_path):
    _board, col = _seed(db_path)
    database.create_task(col, "Vencida", due_date=_iso(-1), db_path=db_path)
    database.create_task(col, "Hoy", due_date=date.today().isoformat(), db_path=db_path)
    database.create_task(col, "Lejana", due_date=_iso(30), db_path=db_path)  # fuera de la ventana
    running = database.create_task(col, "En marcha", db_path=db_path)
    database.set_task_timer_started(running, "2026-01-01T09:00:00", db_path=db_path)

    widget = MyWorkWidget(db_path=db_path)
    texts = _item_texts(widget)

    assert "Vencida" in texts
    assert "Hoy" in texts
    assert "En marcha" in texts       # temporizador en marcha, aunque sin fecha
    assert "Lejana" not in texts      # a 30 días queda fuera de la ventana de 7


def test_my_work_widget_click_emits_task_activated(qapp, db_path):
    board_id, col = _seed(db_path)
    task_id = database.create_task(col, "Hoy", due_date=date.today().isoformat(), db_path=db_path)

    widget = MyWorkWidget(db_path=db_path)
    captured = []
    widget.task_activated.connect(lambda tid, bid: captured.append((tid, bid)))

    item = next(b for b in widget.findChildren(QPushButton) if b.objectName() == "NotificationItem")
    item.click()

    assert captured == [(task_id, board_id)]


def test_my_work_widget_empty_state(qapp, db_path):
    _seed(db_path)  # tablero y columna, pero ninguna tarea con fecha ni temporizador
    widget = MyWorkWidget(db_path=db_path)
    assert _item_texts(widget) == []
