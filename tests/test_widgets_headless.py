"""Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas
pocas propiedades estructurales, sin interacción profunda. Necesitan el fixture
`qapp` (ver conftest.py) y se ejecutan bien con QT_QPA_PLATFORM=offscreen (igual
que en CI) o con un display real."""
from datetime import date, timedelta

from PySide6.QtCore import Qt, QPoint, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent

import database
from calendar_view import CalendarViewWidget
from sidebar import NotificationsPopup
from settings_dialog import SettingsDialog
from widgets import ColumnWidget
from strings import t


def _task_drag_mime():
    mime = QMimeData()
    mime.setData("application/x-ekin-task-id", b"1")
    return mime


def _drag_enter_event():
    # PySide6 no mantiene viva la QMimeData por su cuenta: si el único
    # QMimeData pasado al constructor no se referencia desde ningún otro
    # sitio, se recolecta en cuanto termina la expresión y event.mimeData()
    # devuelve un QObject genérico (sin .hasFormat). _keepalive fija su vida a
    # la del propio evento.
    mime = _task_drag_mime()
    ev = QDragEnterEvent(QPoint(5, 5), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    ev._keepalive = mime
    return ev


def _drop_event():
    mime = _task_drag_mime()
    ev = QDropEvent(QPoint(5, 5), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    ev._keepalive = mime
    return ev


# --- CalendarViewWidget ---

def test_calendar_view_constructs_and_shows_current_month(qapp, db_path):
    cal = CalendarViewWidget(db_path)
    assert cal.view_mode == "month"
    assert cal.period_label.text() != ""
    assert len(cal.cells) == 42  # 6 filas x 7 columnas en vista de mes


def test_calendar_view_cycles_all_modes(qapp, db_path):
    cal = CalendarViewWidget(db_path)
    for index, expected_mode in enumerate(("month", "week", "day")):
        cal.mode_combo.setCurrentIndex(index)
        assert cal.view_mode == expected_mode
    # Vista de día: una sola celda
    assert len(cal.cells) == 1


def test_calendar_view_shows_scheduled_tasks(qapp, db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    database.create_task(col_id, "Due today", due_date=date.today().isoformat(), db_path=db_path)
    cal = CalendarViewWidget(db_path)
    total_chips = sum(c._layout.count() - 1 for c in cal.cells if c.cell_date is not None)
    assert total_chips >= 1


# --- NotificationsPopup (campana de vencimientos, sidebar.py) ---

def test_notifications_popup_empty(qapp):
    popup = NotificationsPopup([])
    # Con la lista vacía, el constructor añade solo la cabecera + el mensaje vacío
    assert popup.layout().count() == 2


def test_notifications_popup_with_tasks(qapp):
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    tasks = [
        {"id": 1, "title": "Overdue", "due_date": "2020-01-01",
         "board_id": 1, "board_name": "B", "board_color": "#3b82f6"},
        {"id": 2, "title": "", "due_date": today,
         "board_id": 1, "board_name": "B", "board_color": "#3b82f6"},
        {"id": 3, "title": "Tomorrow task", "due_date": tomorrow,
         "board_id": 1, "board_name": "B", "board_color": "#3b82f6"},
    ]
    popup = NotificationsPopup(tasks)
    # Cabecera + scroll area (los 3 grupos ATRASADAS/HOY/MAÑANA viven dentro del scroll)
    assert popup.layout().count() == 2


# --- SettingsDialog ---

def test_settings_dialog_constructs_with_saved_theme(qapp, db_path):
    database.set_setting("theme", "light", db_path)
    dlg = SettingsDialog(db_path)
    assert dlg.windowTitle() == t("settings.window_title")
    assert dlg.theme_combo.currentText() == t("settings.theme_light")


def test_settings_dialog_notification_checkbox_reflects_saved_value(qapp, db_path):
    database.set_setting("notifications_enabled", "0", db_path)
    dlg = SettingsDialog(db_path)
    assert dlg.notif_chk.isChecked() is False


# --- ColumnWidget: temporizador de hover-expand sobre columna plegada ---
# No se simula un QDrag.exec() nativo (no es viable en pytest/CI): se invocan los
# manejadores de evento directamente con un QDragEnterEvent/QDragLeaveEvent real,
# igual que haría Qt al despachar un drag en curso.

def _collapsed_column_widget(column_id=1):
    col_data = {
        "id": column_id, "board_id": 1, "name": "Col", "color": "#3b82f6",
        "position": 0, "collapsed": 1, "task_count": 0,
    }
    return ColumnWidget(col_data)


def test_hover_timer_starts_on_drag_enter(qapp):
    col = _collapsed_column_widget()
    assert not col._hover_timer.isActive()

    col.dragEnterEvent(_drag_enter_event())

    assert col._hover_timer.isActive()


def test_hover_timer_stops_on_drag_leave(qapp):
    col = _collapsed_column_widget()
    col.dragEnterEvent(_drag_enter_event())
    assert col._hover_timer.isActive()

    col.dragLeaveEvent(QDragLeaveEvent())

    assert not col._hover_timer.isActive()


def test_hover_timer_stops_on_drop_before_timeout(qapp):
    col = _collapsed_column_widget()
    col.dragEnterEvent(_drag_enter_event())
    assert col._hover_timer.isActive()

    dropped = []
    col.collapsed_card_drop.connect(lambda task_id, col_id: dropped.append((task_id, col_id)))

    col.dropEvent(_drop_event())

    assert not col._hover_timer.isActive()
    assert dropped == [(1, 1)]


def test_hover_timeout_emits_signal_only_while_collapsed(qapp):
    col = _collapsed_column_widget(column_id=7)
    emitted = []
    col.hover_expand_requested.connect(lambda cid: emitted.append(cid))

    col._on_hover_timeout()
    assert emitted == [7]

    # Si mientras tanto ya se desplegó (collapsed=False), un timeout tardío no debe emitir nada.
    col.collapsed = False
    col._on_hover_timeout()
    assert emitted == [7]
