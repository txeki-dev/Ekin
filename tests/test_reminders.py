"""Pruebas de recordatorios anticipados y resumen semanal (reminders.py):
- lógica pura: current_week_key, should_show_weekly_digest, split_digest_tasks.
- WeeklyDigestDialog: construcción headless y emisión de señales.
"""
from datetime import date, timedelta

from PySide6.QtWidgets import QPushButton

import database
import reminders
from reminders import (
    current_week_key, should_show_weekly_digest, split_digest_tasks, WeeklyDigestDialog,
)


def _iso(days):
    return (date.today() + timedelta(days=days)).isoformat()


# --- Lógica pura --------------------------------------------------------------

def test_current_week_key_format():
    assert current_week_key(date(2026, 1, 5)) == "2026-W02"  # lunes ISO


def test_should_show_weekly_digest_gating():
    today = date(2026, 9, 14)
    this_week = current_week_key(today)
    # No mostrado esta semana -> se muestra
    assert should_show_weekly_digest("2026-W01", today, enabled=True) is True
    # Ya mostrado esta semana -> no
    assert should_show_weekly_digest(this_week, today, enabled=True) is False
    # Desactivado -> nunca
    assert should_show_weekly_digest("", today, enabled=False) is False


def test_split_digest_tasks():
    today = date.today().isoformat()
    tasks = [
        {"id": 1, "due_date": _iso(-2)},
        {"id": 2, "due_date": today},
        {"id": 3, "due_date": _iso(3)},
        {"id": 4, "due_date": None},   # ignorada
    ]
    groups = split_digest_tasks(tasks, today)
    assert [t["id"] for t in groups["overdue"]] == [1]
    assert [t["id"] for t in groups["this_week"]] == [2, 3]


# --- Diálogo headless ---------------------------------------------------------

def _task(tid, title, due):
    return {"id": tid, "title": title, "due_date": due,
            "board_id": 7, "board_name": "Proyecto", "board_color": "#c67139"}


def test_weekly_digest_dialog_lists_and_activates(qapp):
    overdue = [_task(1, "Atrasada", _iso(-1))]
    this_week = [_task(2, "Esta semana", _iso(2))]
    dlg = WeeklyDigestDialog(overdue, this_week)

    items = [b for b in dlg.findChildren(QPushButton) if b.objectName() == "NotificationItem"]
    assert [b.text() for b in items] == ["Atrasada", "Esta semana"]

    captured = []
    dlg.task_activated.connect(lambda tid, bid: captured.append((tid, bid)))
    items[0].click()
    assert captured == [(1, 7)]


def test_weekly_digest_dialog_open_my_work_signal(qapp):
    dlg = WeeklyDigestDialog([], [_task(2, "Esta semana", _iso(1))])
    fired = []
    dlg.open_my_work_requested.connect(lambda: fired.append(True))
    mywork_btn = next(
        b for b in dlg.findChildren(QPushButton) if b.text() == reminders.t("digest.open_my_work_btn")
    )
    mywork_btn.click()
    assert fired == [True]


def test_settings_persists_reminder_and_digest(qapp, db_path):
    from settings_dialog import SettingsDialog
    dlg = SettingsDialog(db_path)
    dlg.reminder_lead_spin.setValue(3)
    dlg.digest_switch.setChecked(False)
    assert database.get_setting("reminder_lead_days", "0", db_path) == "3"
    assert database.get_setting("weekly_digest_enabled", "1", db_path) == "0"
