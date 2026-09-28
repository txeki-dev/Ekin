"""Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas
pocas propiedades estructurales, sin interacción profunda. Necesitan el fixture
`qapp` (ver conftest.py) y se ejecutan bien con QT_QPA_PLATFORM=offscreen (igual
que en CI) o con un display real."""
import re
from datetime import date, datetime, timedelta

import pytest
from PySide6.QtCore import Qt, QPoint, QPointF, QMimeData, QEvent
from PySide6.QtGui import (
    QDragEnterEvent, QDragLeaveEvent, QDropEvent, QImage, QMouseEvent,
    QTextCursor, QKeyEvent
)
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

import database
import styles
from calendar_view import CalendarViewWidget
from sidebar import NotificationsPopup
from settings_dialog import SettingsDialog
from shortcuts_dialog import ShortcutsDialog
from export_dialog import ExportDialog, ImportConfirmationDialog
from detail_dialog import TaskDetailDialog
from detail_dialog.log_entry import LogEntryWidget
import detail_dialog.task_detail_dialog as task_detail_dialog_module
import detail_dialog.markdown_edit as markdown_edit_module
import detail_dialog.image_preview_dialog as image_preview_module
import detail_dialog.log_entry as log_entry_module
from widgets import ColumnWidget, TaskCard
import strings
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


def _shown_expanded_column(qapp, name, wip_limit=None):
    col = ColumnWidget({
        "id": 1, "board_id": 1, "name": name, "color": "#3b82f6",
        "position": 0, "collapsed": 0, "task_count": 2, "wip_limit": wip_limit,
    })
    col.setAttribute(Qt.WA_DontShowOnScreen, True)
    col.show()
    qapp.processEvents()
    return col


def test_column_title_elides_long_name_to_fit_header(qapp):
    """#59: un nombre largo no debe cortarse a mitad de carácter ni empujar los botones
    fuera de la cabecera: se recorta con «…» y el nombre completo queda en el tooltip."""
    long_name = "Una columna con un nombre larguísimo que no cabe en la cabecera"
    col = _shown_expanded_column(qapp, long_name, wip_limit=5)
    title = col.title_label

    assert title.text().endswith("…")
    assert title.fontMetrics().horizontalAdvance(title.text()) <= title.contentsRect().width()
    assert long_name in title.toolTip()
    header = col.menu_btn.parentWidget()
    assert col.menu_btn.geometry().right() <= header.width()
    col.close()


def test_column_title_short_name_is_not_elided(qapp):
    col = _shown_expanded_column(qapp, "Backlog")
    assert col.title_label.text() == "Backlog"
    col.close()


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


# --- ShortcutsDialog (Ctrl+/): referencia estática de atajos de teclado ---

def test_shortcuts_dialog_constructs_with_both_sections(qapp):
    dlg = ShortcutsDialog()
    assert dlg.windowTitle() == t("shortcuts.window_title")

    label_texts = [lbl.text() for lbl in dlg.findChildren(QLabel)]
    assert any(t("shortcuts.section_general") in text for text in label_texts)
    assert any(t("shortcuts.section_editor") in text for text in label_texts)
    # Una muestra representativa de atajos (nuevos y preexistentes) debe aparecer en algún QLabel.
    assert any(t("shortcuts.item_new_column") == text for text in label_texts)
    assert any(t("shortcuts.item_jump_board") == text for text in label_texts)
    assert any(t("shortcuts.item_bold") == text for text in label_texts)


def test_shortcuts_item_new_task_describes_last_active_column_behavior():
    """Regresión: el texto describía el comportamiento antiguo de Ctrl+N (siempre la
    primera columna) después de que quick_add_task ya usara la última columna activa."""
    text = t("shortcuts.item_new_task")
    assert "last column" in text
    assert "interacted with" in text


# --- TaskCard.update_timer_badge / set_timer_alert_hours (v0.9.0) ---

def _card_with_timer(started_at, alert_hours=24):
    card = TaskCard({"id": 1, "title": "Tarea", "timer_started_at": started_at})
    card.set_timer_alert_hours(alert_hours)
    return card


def test_timer_badge_hidden_when_no_timer(qapp):
    card = _card_with_timer(started_at=None)
    assert card.timer_container.isHidden()
    assert card.timer_badge_label.text() == ""


def test_timer_badge_shown_muted_under_threshold(qapp):
    started = (datetime.now() - timedelta(hours=1)).isoformat()
    card = _card_with_timer(started_at=started, alert_hours=24)

    assert not card.timer_container.isHidden()
    assert card.timer_badge_label.text().endswith("m")
    assert styles.COLORS['danger'] not in card.timer_badge_label.styleSheet()
    assert styles.COLORS['text_muted'] in card.timer_badge_label.styleSheet()


def test_timer_badge_shown_danger_at_or_above_threshold(qapp):
    started = (datetime.now() - timedelta(hours=30)).isoformat()
    card = _card_with_timer(started_at=started, alert_hours=24)

    assert not card.timer_container.isHidden()
    assert styles.COLORS['danger'] in card.timer_badge_label.styleSheet()


def test_timer_badge_updates_when_threshold_changed(qapp):
    started = (datetime.now() - timedelta(hours=10)).isoformat()
    card = _card_with_timer(started_at=started, alert_hours=24)
    assert styles.COLORS['danger'] not in card.timer_badge_label.styleSheet()

    card.set_timer_alert_hours(5)  # ahora 10h ya supera el nuevo umbral de 5h
    assert styles.COLORS['danger'] in card.timer_badge_label.styleSheet()


def test_timer_badge_hides_on_invalid_timestamp(qapp):
    card = _card_with_timer(started_at="no-es-una-fecha-valida")
    assert card.timer_container.isHidden()


# --- TaskDetailDialog: temporizador (v0.9.0) ---

def _make_task(db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    return database.create_task(col_id, "Tarea", db_path=db_path)


def test_task_detail_dialog_starts_with_no_timer(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    assert dlg.timer_toggle_btn.text() == t("task_detail.timer_start_btn")
    assert dlg.timer_clear_btn.isHidden()
    assert dlg.timer_elapsed_label.text() == ""


def test_task_detail_dialog_loads_existing_timer(qapp, db_path):
    task_id = _make_task(db_path)
    database.set_task_timer_started(task_id, datetime.now().isoformat(), db_path=db_path)

    dlg = TaskDetailDialog(task_id, db_path)

    assert dlg.timer_toggle_btn.text() == t("task_detail.timer_restart_btn")
    assert not dlg.timer_clear_btn.isHidden()
    assert dlg.timer_elapsed_label.text() != ""


def test_task_detail_dialog_start_timer_persists_instantly(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg._on_timer_toggle_clicked()

    assert database.get_task(task_id, db_path)["timer_started_at"] is not None
    assert dlg.modified is True
    assert dlg.timer_toggle_btn.text() == t("task_detail.timer_restart_btn")
    assert not dlg.timer_clear_btn.isHidden()


def test_task_detail_dialog_restart_timer_updates_timestamp(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg._on_timer_toggle_clicked()
    first = database.get_task(task_id, db_path)["timer_started_at"]

    dlg._on_timer_toggle_clicked()
    second = database.get_task(task_id, db_path)["timer_started_at"]

    assert second >= first  # timestamps ISO son comparables lexicográficamente


def test_task_detail_dialog_clear_timer_persists_instantly(qapp, db_path):
    task_id = _make_task(db_path)
    database.set_task_timer_started(task_id, datetime.now().isoformat(), db_path=db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg._on_timer_clear_clicked()

    assert database.get_task(task_id, db_path)["timer_started_at"] is None
    assert dlg.modified is True
    assert dlg.timer_toggle_btn.text() == t("task_detail.timer_start_btn")
    assert dlg.timer_clear_btn.isHidden()


def test_task_detail_dialog_is_destroyed_after_closing_when_parented(qapp, db_path):
    """Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/
    BoardViewWidget, como hacen los call sites reales) debe autodestruirse
    (deleteLater vía self.finished) al cerrarse -- no debe quedar zombi con su
    _timer_refresh_timer de 30s corriendo para siempre. Antes del fix, este mismo
    escenario dejaba el diálogo vivo indefinidamente."""
    task_id = _make_task(db_path)
    parent = QWidget()
    dlg = TaskDetailDialog(task_id, db_path, parent)

    dlg.reject()  # equivalente a "Cerrar" o Esc
    # Acotado a `dlg`: sendPostedEvents(None, ...) procesaría TODOS los DeferredDelete
    # pendientes de toda la sesión de tests (qapp es de ámbito de sesión), arriesgando
    # tocar objetos de otros módulos de test que ya estén a mitad de su propia limpieza.
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)

    with pytest.raises(RuntimeError):
        dlg.windowTitle()


def test_task_detail_dialog_without_parent_still_works_as_before(qapp, db_path):
    """El nuevo self.finished.connect(self.deleteLater) no debe romper el patrón ya
    usado por los tests existentes (diálogo sin padre, recogido por el GC de Python
    normal): accept()/reject() deben seguir funcionando con normalidad."""
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    dlg.reject()
    assert dlg.result() == 0
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)
    with pytest.raises(RuntimeError):
        dlg.windowTitle()




# --- TaskDetailDialog: adjuntar archivos locales a los enlaces (post-v0.9.0) ---

def test_is_local_link_classifies_urls_vs_paths():
    _is_local_link = task_detail_dialog_module._is_local_link
    assert _is_local_link("https://x.com") is False
    assert _is_local_link("http://x.com") is False
    assert _is_local_link("mailto:a@b.com") is False
    assert _is_local_link("file://C:/x.txt") is False
    assert _is_local_link("calc:") is False
    assert _is_local_link("powershell:test") is False
    assert _is_local_link("javascript:alert(1)") is False
    assert _is_local_link("ms-msdt:") is False
    assert _is_local_link(r"C:\Users\foo\bar.pdf") is True
    assert _is_local_link("C:/Users/foo/bar.pdf") is True
    assert _is_local_link("/home/user/file.txt") is True
    assert _is_local_link(r"\\server\share\doc.pdf") is True
    assert _is_local_link("relative/path/file.txt") is True
    assert _is_local_link("") is False
    assert _is_local_link(None) is False


def test_browse_local_file_fills_url_and_autofills_empty_label(qapp, db_path):
    # Qt's QFileDialog always returns "/"-separated paths, even on Windows (native
    # backslashes are only produced by QDir.toNativeSeparators()) -- use that shape here
    # so os.path.basename() behaves the same on every OS/CI runner this test executes on.
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg._apply_browsed_file("C:/docs/report.pdf")

    assert dlg.link_url_input.text() == "C:/docs/report.pdf"
    assert dlg.link_label_input.text() == "report.pdf"


def test_browse_local_file_does_not_overwrite_existing_label(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    dlg.link_label_input.setText("Mi informe")

    dlg._apply_browsed_file("C:/docs/report.pdf")

    assert dlg.link_label_input.text() == "Mi informe"


def test_add_link_with_local_path_renders_with_attachment_icon(qapp, db_path, tmp_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    file_path = tmp_path / "adjunto.txt"
    file_path.write_text("contenido")

    dlg.link_url_input.setText(str(file_path))
    dlg.add_link()

    buttons = dlg.links_container.findChildren(QPushButton)
    assert any((not b.icon().isNull()) and str(file_path) in b.text() for b in buttons)


def test_add_link_with_web_url_renders_with_link_icon(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg.link_url_input.setText("https://example.com")
    dlg.add_link()

    buttons = dlg.links_container.findChildren(QPushButton)
    assert any((not b.icon().isNull()) and "example.com" in b.text() for b in buttons)


def test_open_link_warns_when_target_cannot_be_opened(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *_a: False)
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda *a, **k: warnings.append((a, k))
    )

    dlg._open_link(r"C:\nope.txt", True)

    assert len(warnings) == 1


def test_open_link_no_warning_when_openurl_succeeds(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *_a: True)
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda *a, **k: warnings.append((a, k))
    )

    dlg._open_link(r"C:\nope.txt", True)

    assert warnings == []


def test_is_unc_path_detection():
    _is_unc_path = task_detail_dialog_module._is_unc_path
    assert _is_unc_path(r"\\server\share\file.pdf") is True
    assert _is_unc_path("//server/share/file.pdf") is True
    assert _is_unc_path("file://server/share/file.pdf") is True
    assert _is_unc_path("file:////server/share/file.pdf") is True
    assert _is_unc_path(r"C:\Users\foo\bar.pdf") is False
    assert _is_unc_path("/home/user/file.txt") is False
    assert _is_unc_path("file:///C:/Users/foo/bar.pdf") is False
    assert _is_unc_path("https://example.com") is False
    assert _is_unc_path("") is False
    assert _is_unc_path(None) is False


def _cleanup_dialog(qapp, dlg):
    dlg.close()
    dlg.deleteLater()
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)


def test_open_link_warns_and_blocks_executable_when_cancelled(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Cancel
        )[1]
    )

    try:
        dlg._open_link(r"C:\danger\payload.exe", True)
        assert len(warnings) == 1
        assert "payload.exe" in warnings[0][1]
        assert calls == []
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_allows_executable_when_user_confirms(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a) or True)
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Open
        )[1]
    )

    try:
        dlg._open_link(r"C:\tools\build.bat", True)
        assert len(warnings) == 1
        assert "build.bat" in warnings[0][1]
        assert len(calls) == 1
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_warns_and_blocks_unc_when_cancelled(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Cancel
        )[1]
    )

    try:
        dlg._open_link(r"\\remote-server\share\document.pdf", True)
        assert len(warnings) == 1
        assert "network share" in warnings[0][1].lower() or "unc" in warnings[0][1].lower()
        assert calls == []
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_handles_unc_executable(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Cancel
        )[1]
    )

    try:
        dlg._open_link(r"\\remote-server\share\payload.ps1", True)
        assert len(warnings) == 1
        msg_lower = warnings[0][1].lower()
        assert "payload.ps1" in msg_lower
        assert "network share" in msg_lower or "remote" in msg_lower
        assert calls == []
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_blocks_file_uri_executable_bypass(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Cancel
        )[1]
    )

    try:
        # is_local is False for file:// per _is_local_link, but it must still be intercepted
        dlg._open_link("file:///C:/malicious.cmd", False)
        assert len(warnings) == 1
        assert "malicious.cmd" in warnings[0][1]
        assert calls == []
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_blocks_untrusted_uri_scheme_when_cancelled(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Cancel
        )[1]
    )

    try:
        # powershell: scheme must be intercepted even if is_local was passed as True or False
        dlg._open_link("powershell:Invoke-Item", True)
        assert len(warnings) == 1
        assert "powershell" in warnings[0][1].lower()
        assert calls == []
    finally:
        _cleanup_dialog(qapp, dlg)


def test_open_link_allows_untrusted_uri_scheme_when_confirmed(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    calls = []
    monkeypatch.setattr(task_detail_dialog_module.QDesktopServices, "openUrl", lambda *a: calls.append(a) or True)
    warnings = []
    monkeypatch.setattr(
        task_detail_dialog_module.QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            task_detail_dialog_module.QMessageBox.StandardButton.Open
        )[1]
    )

    try:
        dlg._open_link("calc:", False)
        assert len(warnings) == 1
        assert "calc" in warnings[0][1].lower()
        assert len(calls) == 1
    finally:
        _cleanup_dialog(qapp, dlg)


def test_build_link_row_skips_exists_check_on_unc(qapp, db_path, monkeypatch):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)
    exists_calls = []
    monkeypatch.setattr(
        task_detail_dialog_module.os.path, "exists",
        lambda p: exists_calls.append(p) or True
    )

    link = {"id": 1, "url": r"\\slow-server\share\doc.pdf", "label": "Remote Doc"}
    row = dlg._build_link_row(link)

    try:
        assert len(exists_calls) == 0
    finally:
        row.deleteLater()
        _cleanup_dialog(qapp, dlg)


def test_markdown_edit_untrusted_link_blocks_executable_when_cancelled(qapp, monkeypatch):
    from detail_dialog.markdown_edit import MarkdownTextEdit
    from detail_dialog.security_utils import QMessageBox, QDesktopServices
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QMouseEvent

    editor = MarkdownTextEdit()
    editor.setHtml('<p><a href="C:\\danger\\run.bat">Run Me</a></p>')

    calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            QMessageBox.StandardButton.Cancel
        )[1]
    )

    # Simular clic sobre el enlace
    editor._press_pos = QPoint(2, 2)
    monkeypatch.setattr(editor, "anchorAt", lambda pos: r"C:\danger\run.bat")
    from PySide6.QtCore import QPointF
    ev = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(2, 2), QPointF(2, 2), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    editor.mouseReleaseEvent(ev)

    assert len(warnings) == 1
    assert "run.bat" in warnings[0][1]
    assert calls == []


def test_log_entry_untrusted_link_blocks_executable_when_cancelled(qapp, monkeypatch):
    from detail_dialog.log_entry import LogEntryWidget
    from detail_dialog.security_utils import QMessageBox, QDesktopServices

    log_data = {"id": 1, "content": "Test log", "created_at": "2026-09-10 12:00:00"}
    entry = LogEntryWidget(log_data, delete_callback=lambda: None, save_edit_callback=lambda id, txt: None)

    calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda *a: calls.append(a))
    warnings = []
    monkeypatch.setattr(
        QMessageBox, "warning",
        lambda parent, title, msg, btns=None, default=None: (
            warnings.append((title, msg)),
            QMessageBox.StandardButton.Cancel
        )[1]
    )

    entry._on_content_link_activated(r"\\evil-server\share\exploit.ps1")

    assert len(warnings) == 1
    assert "exploit.ps1" in warnings[0][1]
    assert calls == []


# --- SettingsDialog: umbral de aviso del temporizador (v0.9.0) ---

def test_settings_dialog_timer_alert_spin_reflects_saved_value(qapp, db_path):
    database.set_setting("timer_alert_hours", "48", db_path)
    dlg = SettingsDialog(db_path)
    assert dlg.timer_alert_spin.value() == 48


def test_settings_dialog_timer_alert_spin_defaults_to_24(qapp, db_path):
    dlg = SettingsDialog(db_path)
    assert dlg.timer_alert_spin.value() == 24


def test_settings_dialog_timer_alert_spin_persists_on_change(qapp, db_path):
    dlg = SettingsDialog(db_path)
    dlg.timer_alert_spin.setValue(72)
    assert database.get_setting("timer_alert_hours", None, db_path) == "72"


# --- Click-to-enlarge pasted images (post-v0.9.1) ---

_TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
_TINY_PNG_DATA_URI = f"data:image/png;base64,{_TINY_PNG_B64}"


def test_pixmap_from_data_uri_decodes_valid_png():
    pixmap = image_preview_module.pixmap_from_data_uri(_TINY_PNG_DATA_URI)
    assert not pixmap.isNull()


def test_pixmap_from_data_uri_returns_null_for_garbage():
    assert image_preview_module.pixmap_from_data_uri("not-a-data-uri").isNull()
    assert image_preview_module.pixmap_from_data_uri("data:image/png;base64,not-valid-base64!!").isNull()


def test_show_image_preview_opens_dialog_for_valid_image(qapp, monkeypatch):
    calls = []
    monkeypatch.setattr(image_preview_module.ImagePreviewDialog, "exec", lambda self: calls.append(1))

    image_preview_module.show_image_preview(_TINY_PNG_DATA_URI)

    assert len(calls) == 1


def test_show_image_preview_noop_for_invalid_uri(qapp, monkeypatch):
    calls = []
    monkeypatch.setattr(image_preview_module.ImagePreviewDialog, "exec", lambda self: calls.append(1))

    image_preview_module.show_image_preview("garbage")

    assert calls == []


def test_image_preview_dialog_upscales_small_pixmap(qapp):
    """Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña (como
    las pegadas en el chat/descripción, reducidas al pegarlas) se mostraba a su tamaño
    nativo en la vista ampliada -- lejos de sentirse "más grande"."""
    from PySide6.QtGui import QPixmap

    small = QPixmap(20, 20)
    small.fill(Qt.GlobalColor.red)

    dlg = image_preview_module.ImagePreviewDialog(small)

    shown = dlg.findChild(QLabel).pixmap()
    assert shown.width() > 20 and shown.height() > 20


def test_image_preview_dialog_is_destroyed_after_closing_when_parented(qapp):
    """Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog debe
    autodestruirse (deleteLater vía self.finished) al cerrarse en vez de quedar colgado
    para siempre del widget que lo abrió."""
    from PySide6.QtGui import QPixmap

    parent = QWidget()
    pixmap = QPixmap(10, 10)
    pixmap.fill(Qt.GlobalColor.red)
    dlg = image_preview_module.ImagePreviewDialog(pixmap, parent)

    # reject(), no close(): un QDialog nunca mostrado no emite finished() al cerrarse con
    # close() (Qt lo trata como no-op sobre un widget invisible), pero reject() sí lo hace
    # incondicionalmente -- mismo motivo por el que test_task_detail_dialog_is_destroyed_
    # after_closing_when_parented usa reject() en vez de close().
    dlg.reject()
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)

    with pytest.raises(RuntimeError):
        dlg.windowTitle()


def test_markdown_text_edit_wraps_pasted_image_in_anchor(qapp):
    editor = markdown_edit_module.MarkdownTextEdit()

    editor._insert_image(QImage(4, 4, QImage.Format.Format_RGB32))

    assert '<a href="data:image/png;base64,' in editor.toHtml()


def test_markdown_text_edit_stores_higher_res_copy_for_preview(qapp):
    """Regresión: antes href y src eran el MISMO data URI (la miniatura ya reducida al
    ancho del chat/descripción), así que ImagePreviewDialog tenía que estirarla hacia
    arriba y se veía borrosa. Ahora href guarda una copia de mayor resolución aparte."""
    editor = markdown_edit_module.MarkdownTextEdit()
    big_image = QImage(2400, 1600, QImage.Format.Format_RGB32)
    big_image.fill(Qt.GlobalColor.blue)

    editor._insert_image(big_image)
    html = editor.toHtml()

    href = re.search(r'<a href="(data:image/[^"]+)"', html).group(1)
    src = re.search(r'<img src="(data:image/[^"]+)"', html).group(1)
    href_pixmap = image_preview_module.pixmap_from_data_uri(href)
    src_pixmap = image_preview_module.pixmap_from_data_uri(src)

    assert href_pixmap.width() > src_pixmap.width()
    assert href_pixmap.width() <= markdown_edit_module.MarkdownTextEdit._PREVIEW_MAX_WIDTH


def test_markdown_text_edit_small_image_reuses_same_data_for_preview_and_inline(qapp):
    """Cuando la imagen original ya es más pequeña que ambos objetivos (inline y
    preview), href y src acaban siendo el mismo data URI -- comportamiento correcto,
    no un caso a evitar: no hay ninguna resolución mayor que guardar."""
    editor = markdown_edit_module.MarkdownTextEdit()
    tiny = QImage(50, 50, QImage.Format.Format_RGB32)
    tiny.fill(Qt.GlobalColor.green)

    editor._insert_image(tiny)
    html = editor.toHtml()

    href = re.search(r'<a href="(data:image/[^"]+)"', html).group(1)
    src = re.search(r'<img src="(data:image/[^"]+)"', html).group(1)
    assert href == src


def test_markdown_text_edit_click_on_image_anchor_opens_preview(qapp, monkeypatch):
    """anchorAt() se parchea directamente: probar esto contra la geometría real del
    layout de texto sería frágil y no es lo que este test necesita verificar -- el
    comportamiento bajo prueba es la distinción click/arrastre y el despacho a
    show_image_preview, no el motor de layout de Qt."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor._insert_image(QImage(4, 4, QImage.Format.Format_RGB32))
    monkeypatch.setattr(editor, "anchorAt", lambda pos: _TINY_PNG_DATA_URI)
    calls = []
    monkeypatch.setattr(markdown_edit_module, "show_image_preview", lambda uri, parent=None: calls.append(uri))

    pos = QPointF(10, 10)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    editor.mousePressEvent(press)
    editor.mouseReleaseEvent(release)

    assert calls == [_TINY_PNG_DATA_URI]


def test_markdown_text_edit_drag_does_not_open_preview(qapp, monkeypatch):
    """Regresión: un arrastre de selección que termine sobre una imagen no debe
    abrir la vista ampliada -- solo un clic real (press y release casi en el mismo
    punto) debe hacerlo."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor._insert_image(QImage(4, 4, QImage.Format.Format_RGB32))
    monkeypatch.setattr(editor, "anchorAt", lambda pos: _TINY_PNG_DATA_URI)
    calls = []
    monkeypatch.setattr(markdown_edit_module, "show_image_preview", lambda uri, parent=None: calls.append(uri))

    press_pos = QPointF(10, 10)
    release_pos = QPointF(50, 60)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, press_pos, press_pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, release_pos, release_pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    editor.mousePressEvent(press)
    editor.mouseReleaseEvent(release)

    assert calls == []


def test_markdown_text_edit_insert_horizontal_rule(qapp):
    """insert_horizontal_rule() inserta una etiqueta <hr /> visible en el HTML."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor.setPlainText("Línea 1\nLínea 2")
    editor.insert_horizontal_rule()
    html = editor.toHtml()
    assert "<hr" in html.lower()


def test_markdown_text_edit_three_hyphens_creates_hr(qapp):
    """Escribir '---' o pulsar Enter sobre '---' inserta automáticamente una línea separadora."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor.setPlainText("--")
    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.End)
    editor.setTextCursor(cursor)

    # Pulsar el 3er guion '-'
    ev = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_Minus, Qt.NoModifier, "-")
    editor.keyPressEvent(ev)
    assert "<hr" in editor.toHtml().lower()

    # Probar también con Enter sobre "---"
    editor2 = markdown_edit_module.MarkdownTextEdit()
    editor2.setPlainText("---")
    cursor2 = editor2.textCursor()
    cursor2.movePosition(QTextCursor.End)
    editor2.setTextCursor(cursor2)
    ev_enter = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_Return, Qt.NoModifier)
    editor2.keyPressEvent(ev_enter)
    assert "<hr" in editor2.toHtml().lower()


def test_markdown_text_edit_code_block_formatting(qapp):
    """format_code_block_html() aplica pygments y insert_code_block() lo embebe en el editor."""
    code = "def suma(a, b):\n    return a + b"
    html_block = markdown_edit_module.format_code_block_html(code, "python")
    assert "<table" in html_block.lower()
    assert "<pre" in html_block.lower()
    assert "PYTHON" in html_block

    editor = markdown_edit_module.MarkdownTextEdit()
    editor.insert_code_block(code, "python")
    out_html = editor.toHtml()
    assert "<table" in out_html.lower()
    assert "suma" in out_html


def test_markdown_text_edit_delete_code_block_via_action(qapp, monkeypatch):
    """Hacer clic en '✕ Borrar' en la cabecera del bloque de código elimina la tabla por completo."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor.insert_code_block("x = 10", "python")
    assert "<table" in editor.toHtml().lower()

    # Simular clic en el enlace action:delete_code_block
    monkeypatch.setattr(editor, "anchorAt", lambda pos: "action:delete_code_block")
    editor._press_pos = QPoint(5, 5)
    pos = QPointF(5, 5)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    editor.mouseReleaseEvent(release)

    assert "<table" not in editor.toHtml().lower()
    assert "x = 10" not in editor.toPlainText()


def test_markdown_text_edit_open_code_dialog_bool_safe(qapp, monkeypatch):
    """open_code_dialog() no falla si se le pasa un booleano desde la señal clicked de un botón."""
    editor = markdown_edit_module.MarkdownTextEdit()
    # Simular que QDialog.exec devuelve Rejected para no bloquear el test
    exec_called = []
    monkeypatch.setattr(markdown_edit_module.CodeBlockDialog, "exec", lambda self: exec_called.append(True) or 0)
    # No debe levantar TypeError: PySide6.QtWidgets.QPlainTextEdit.setPlainText(bool)
    editor.open_code_dialog(False)
    editor.open_code_dialog(True)
    editor.open_code_dialog(None)
    assert len(exec_called) == 3



def test_markdown_text_edit_text_color_formatting(qapp):
    """apply_text_color aplica el color especificado al texto seleccionado."""
    editor = markdown_edit_module.MarkdownTextEdit()
    toolbar = markdown_edit_module.RichTextToolbar(editor)
    editor.setPlainText("Texto coloreado")
    cursor = editor.textCursor()
    cursor.setPosition(0)
    cursor.setPosition(5, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)

    toolbar.apply_text_color("#ef4444")
    html = editor.toHtml()
    assert "#ef4444" in html.lower()


def test_markdown_text_edit_paste_url_wraps_or_inserts_link(qapp):
    """Pegar una URL envuelve el texto seleccionado en un enlace <a href>, o inserta el enlace directo."""
    editor = markdown_edit_module.MarkdownTextEdit()
    editor.setPlainText("visita mi web")
    cursor = editor.textCursor()
    cursor.setPosition(10)
    cursor.setPosition(13, QTextCursor.KeepAnchor)
    editor.setTextCursor(cursor)

    mime = QMimeData()
    mime.setText("https://ekin.app")
    editor.insertFromMimeData(mime)

    html = editor.toHtml()
    assert '<a href="https://ekin.app"' in html
    assert "web" in html


def test_markdown_text_edit_click_external_link_opens_browser(qapp, monkeypatch):
    """Hacer clic en un enlace web dentro del editor abre el navegador mediante QDesktopServices."""
    from PySide6.QtGui import QDesktopServices
    calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: calls.append(url.toString()))

    editor = markdown_edit_module.MarkdownTextEdit()
    monkeypatch.setattr(editor, "anchorAt", lambda pos: "https://github.com/txeki/ekin")

    pos = QPointF(10, 10)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    editor.mousePressEvent(press)
    editor.mouseReleaseEvent(release)

    assert calls == ["https://github.com/txeki/ekin"]


def test_log_entry_linkify_and_external_link_open(qapp, monkeypatch):
    """LogEntryWidget convierte URLs sin enlace en hipervínculos clicables y los abre con openUrl."""
    from PySide6.QtGui import QDesktopServices
    calls = []
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: calls.append(url.toString()))

    log_data = {
        "id": 1,
        "content": "Revisa https://github.com/txeki/ekin para novedades.",
        "created_at": "2026-08-12 10:00:00",
    }
    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)
    assert '<a href="https://github.com/txeki/ekin"' in widget.content_label.text()

    widget._on_content_link_activated("https://github.com/txeki/ekin")
    assert calls == ["https://github.com/txeki/ekin"]


def test_log_entry_strips_doctype_and_does_not_leak_dtd(qapp):
    """Regresión: toHtml() genera <!DOCTYPE ... strict.dtd> que antes era transformado
    erróneamente por linkify_urls en un <a> inválido, haciendo que QLabel mostrase
    'http://www.w3.org/TR/REC-html40/strict.dtd">' como texto visible al inicio de cada comentario."""
    raw_html = (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
        '<html><head><meta name="qrichtext" content="1" /></head><body>'
        '<p>Comentario normal sin basura de DTD y con enlace https://txek.dev</p>'
        '</body></html>'
    )
    log_data = {"id": 2, "content": raw_html, "created_at": "2026-09-04 10:00:00"}
    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)
    rendered = widget.content_label.text()
    assert "strict.dtd" not in rendered
    assert "<!DOCTYPE" not in rendered
    assert '<a href="https://txek.dev">https://txek.dev</a>' in rendered


def test_rich_text_toolbar_all_buttons_exist(qapp):
    """Verifica que la barra de formato contiene todos los botones requeridos."""
    editor = markdown_edit_module.MarkdownTextEdit()
    tb = markdown_edit_module.RichTextToolbar(editor)
    assert hasattr(tb, "bold_btn")
    assert hasattr(tb, "italic_btn")
    assert hasattr(tb, "strike_btn")
    assert hasattr(tb, "color_btn")
    assert hasattr(tb, "bullet_btn")
    assert hasattr(tb, "hr_btn")
    assert hasattr(tb, "table_btn")
    assert hasattr(tb, "code_btn")
    assert hasattr(tb, "link_btn")
    assert hasattr(tb, "arrow_btn")


def _editor_with_all_selected(text="hola mundo"):
    editor = markdown_edit_module.MarkdownTextEdit()
    tb = markdown_edit_module.RichTextToolbar(editor)
    editor.setPlainText(text)
    cursor = editor.textCursor()
    cursor.select(QTextCursor.Document)
    editor.setTextCursor(cursor)
    return editor, tb


def test_underline_button_and_shortcuts_toggle_underline(qapp):
    """#68: subrayado desde el botón «U» y con Ctrl+U / Ctrl+S (Subrayado en Word en español)."""
    editor, tb = _editor_with_all_selected()

    tb.underline_btn.click()
    assert editor.textCursor().charFormat().fontUnderline()
    assert "text-decoration: underline" in editor.toHtml()
    assert tb.underline_btn.isChecked()

    editor.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_U, Qt.ControlModifier))
    assert not editor.textCursor().charFormat().fontUnderline()
    assert not tb.underline_btn.isChecked()

    editor.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_S, Qt.ControlModifier))
    assert editor.textCursor().charFormat().fontUnderline()
    assert tb.underline_btn.isChecked()


def test_ctrl_shift_u_still_uppercases_not_underlines(qapp):
    editor, _ = _editor_with_all_selected("hola")
    editor.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_U, Qt.ControlModifier | Qt.ShiftModifier))
    assert editor.toPlainText() == "HOLA"
    assert not editor.textCursor().charFormat().fontUnderline()


def test_log_entry_widget_routes_image_link_to_preview(qapp, monkeypatch):
    calls = []
    monkeypatch.setattr(log_entry_module, "show_image_preview", lambda uri, parent=None: calls.append(uri))
    log_data = {
        "id": 1,
        "content": f'<a href="{_TINY_PNG_DATA_URI}"><img src="{_TINY_PNG_DATA_URI}" /></a>',
        "created_at": "2026-08-12 10:00:00",
    }

    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)
    widget._on_content_link_activated(_TINY_PNG_DATA_URI)

    assert calls == [_TINY_PNG_DATA_URI]
    assert widget.content_label.cursor().shape() == Qt.CursorShape.PointingHandCursor


def test_log_entry_widget_real_click_on_posted_image_opens_preview(qapp, monkeypatch):
    """Regresión: setTextInteractionFlags(Qt.TextSelectableByMouse) A SOLAS anulaba
    LinksAccessibleByMouse y linkActivated nunca se disparaba con un clic real, aunque
    _on_content_link_activated (probado por separado arriba) funcionase perfectamente si
    se llamaba a mano. Este test dispara un QMouseEvent real para que un futuro cambio de
    flags no pueda romper esto en silencio otra vez."""
    calls = []
    monkeypatch.setattr(log_entry_module, "show_image_preview", lambda uri, parent=None: calls.append(uri))
    log_data = {
        "id": 1,
        "content": f'<a href="{_TINY_PNG_DATA_URI}"><img src="{_TINY_PNG_DATA_URI}" width="80" height="80"/></a>',
        "created_at": "2026-08-12 10:00:00",
    }

    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)
    widget.show()
    qapp.processEvents()

    pos = QPointF(20, 20)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    qapp.sendEvent(widget.content_label, press)
    qapp.sendEvent(widget.content_label, release)
    qapp.processEvents()

    assert calls == [_TINY_PNG_DATA_URI]


def test_log_entry_widget_plain_text_keeps_default_cursor(qapp):
    log_data = {"id": 1, "content": "solo texto, sin imagen", "created_at": "2026-08-12 10:00:00"}

    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)

    assert widget.content_label.cursor().shape() != Qt.CursorShape.PointingHandCursor


def test_task_detail_dialog_click_outside_auto_saves_and_closes(qapp, db_path):
    """Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan
    automáticamente los cambios y se cierra el diálogo (equivalente a pulsar Guardar)."""
    board_id = database.create_board("Tablero Test", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Titulo Original", db_path=db_path)

    parent_window = QWidget()
    parent_window.resize(1000, 800)
    parent_window.show()
    qapp.processEvents()

    dlg = TaskDetailDialog(task_id, db_path=db_path, parent=parent_window)

    def _simulate_outside_click():
        # Modificar título
        dlg.title_input.setText("Titulo Modificado")
        # Simular clic en la ventana padre fuera del diálogo
        pos = QPointF(10, 10)
        press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        qapp.sendEvent(parent_window, press)

    from PySide6.QtCore import QTimer
    QTimer.singleShot(50, _simulate_outside_click)
    res = dlg.exec()

    assert res == TaskDetailDialog.Accepted
    assert dlg.modified is True
    updated_task = database.get_task(task_id, db_path)
    assert updated_task["title"] == "Titulo Modificado"
    parent_window.close()


def test_task_detail_dialog_click_inside_does_not_close(qapp, db_path):
    """Clics dentro de los controles de TaskDetailDialog no deben disparar el autoguardado/cierre prematuro."""
    board_id = database.create_board("Tablero Test", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Titulo", db_path=db_path)

    dlg = TaskDetailDialog(task_id, db_path=db_path)
    dlg.show()
    qapp.processEvents()

    pos = QPointF(5, 5)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    qapp.sendEvent(dlg.title_input, press)
    qapp.processEvents()

    assert dlg.isVisible()
    dlg.reject()


def test_log_entry_widget_fit_html_images_constrains_width():
    """fit_html_images ajusta o añade width para evitar desbordamiento horizontal."""
    from detail_dialog.log_entry import fit_html_images

    html_in = '<p><img src="data:image/png;base64,1234" /></p>'
    html_out = fit_html_images(html_in, max_width=320)
    assert 'width="320"' in html_out

    # Con width previo mayor
    html_in2 = '<p><img width="800" src="data:image/png;base64,1234" /></p>'
    html_out2 = fit_html_images(html_in2, max_width=300)
    assert 'width="300"' in html_out2
    assert 'width="800"' not in html_out2

    # Con tabla con width previo mayor
    html_tbl = '<table width="900"><tr><td>A</td></tr></table>'
    html_tbl_out = fit_html_images(html_tbl, max_width=350)
    assert 'width="350"' in html_tbl_out
    assert 'width="900"' not in html_tbl_out

    # Con max_width=None usa el valor por defecto seguro
    html_def = fit_html_images('<p><img width="800" src="test.png" /></p>', max_width=None)
    assert 'width="280"' in html_def


def test_log_entry_widget_multiline_text_vertical_sizing(qapp):
    """Verifica que un comentario multilínea tiene tamaño vertical y no se colapsa."""
    log_data = {
        "id": 1,
        "content": "<p>Primera línea de texto largo editado.</p><p>Segunda línea de texto.</p><p>Tercera línea.</p>",
        "created_at": "2026-08-18 10:00:00",
    }
    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)
    widget.show()
    qapp.processEvents()

    assert widget.content_label.wordWrap() is True
    assert widget.content_label.sizePolicy().horizontalPolicy() == widget.content_label.sizePolicy().Policy.Preferred


def test_task_detail_dialog_logs_scroll_to_latest(qapp, db_path):
    """Al abrir TaskDetailDialog con múltiples comentarios, el scroll muestra el último
    comentario sin espacios vacíos desmesurados debajo."""
    board_id = database.create_board("Tablero Test", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea con logs", db_path=db_path)
    for i in range(8):
        database.create_log(task_id, f"<p>Comentario {i+1} de prueba en el diario</p>", db_path)

    dlg = TaskDetailDialog(task_id, db_path=db_path)
    dlg.show()
    qapp.processEvents()

    # Procesar eventos para que el timer de scroll_to_bottom dispare
    from PySide6.QtCore import QTimer
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: None)
    timer.start(100)
    while timer.isActive():
        qapp.processEvents()

    sb = dlg.scroll_area.verticalScrollBar()
    # El scrollbar debe estar en su posición máxima
    assert sb.value() == sb.maximum()

    # El último comentario debe estar en la región visible del viewport
    last_widget = None
    for i in range(dlg.logs_layout.count() - 1, -1, -1):
        item = dlg.logs_layout.itemAt(i)
        if item and item.widget():
            last_widget = item.widget()
            break

    assert last_widget is not None
    visible_top = sb.value()
    visible_bottom = sb.value() + dlg.scroll_area.viewport().height()
    # El final del último widget está dentro o al borde visible
    assert visible_top <= last_widget.geometry().bottom() <= visible_bottom + 15
    dlg.reject()


def test_qss_font_sizes_valid_integers():
    """Verifica que los estilos QSS no contienen tamaños de fuente fraccionales inválidos (ej. 12.5px)."""
    qss = styles.build_qss(styles.COLORS)
    # Buscar patrones como font-size: X.Ypx
    fractional_font_sizes = re.findall(r"font-size:\s*\d+\.\d+px", qss)
    assert fractional_font_sizes == []


def test_task_detail_dialog_link_row_rendering_states(qapp, db_path, tmp_path):
    """Verifica el renderizado de enlaces:
    1. Archivo local existente: icono 📎, color azul (#60a5fa), tooltip con ruta.
    2. Archivo local inexistente: icono 📎, color peligro (danger), tooltip de advertencia.
    3. Enlace web: icono 🔗, color azul (#60a5fa), tooltip con URL.
    """
    real_file = tmp_path / "documento.pdf"
    real_file.write_text("contenido")
    missing_file = tmp_path / "no_existe.pdf"

    board_id = database.create_board("Tablero Links", db_path=db_path)
    col_id = database.create_column(board_id, "Col Links", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea con enlaces", db_path=db_path)

    database.add_task_link(task_id, str(real_file), "Doc Real", db_path=db_path)
    database.add_task_link(task_id, str(missing_file), "Doc Faltante", db_path=db_path)
    database.add_task_link(task_id, "https://github.com", "GitHub", db_path=db_path)

    dlg = TaskDetailDialog(task_id, db_path=db_path)

    # 3 enlaces en el links_layout
    assert dlg.links_layout.count() == 3

    # Fila 1: Archivo local existente
    row1 = dlg.links_layout.itemAt(0).widget()
    btn1 = row1.layout().itemAt(0).widget()
    assert "Doc Real" in btn1.text()
    assert not btn1.icon().isNull()
    assert styles.COLORS["danger"] not in btn1.styleSheet()
    assert styles.COLORS["accent"] in btn1.styleSheet()
    assert btn1.toolTip() == str(real_file)

    # Fila 2: Archivo local faltante
    row2 = dlg.links_layout.itemAt(1).widget()
    btn2 = row2.layout().itemAt(0).widget()
    assert "Doc Faltante" in btn2.text()
    assert styles.COLORS["danger"] in btn2.styleSheet()
    assert t("task_detail.link_missing_tooltip", path=str(missing_file)) in btn2.toolTip()

    # Fila 3: Enlace web
    row3 = dlg.links_layout.itemAt(2).widget()
    btn3 = row3.layout().itemAt(0).widget()
    assert "GitHub" in btn3.text()
    assert not btn3.icon().isNull()
    assert styles.COLORS["danger"] not in btn3.styleSheet()
    assert styles.COLORS["accent"] in btn3.styleSheet()
    assert btn3.toolTip() == "https://github.com"

    dlg.reject()


def test_calendar_view_refresh_skips_when_hidden(qapp, db_path, monkeypatch):
    """CalendarViewWidget.refresh() omite consultas costosas cuando el widget está oculto,
    marcando _dirty=True para refrescarse al volver a ser visible."""
    cal = CalendarViewWidget(db_path)
    assert cal.isVisible() is False
    cal._dirty = False

    called = []
    original_get_scheduled_tasks = database.get_scheduled_tasks

    def mock_get_scheduled_tasks(*args, **kwargs):
        called.append(True)
        return original_get_scheduled_tasks(*args, **kwargs)

    monkeypatch.setattr(database, "get_scheduled_tasks", mock_get_scheduled_tasks)

    # Llamar a refresh() mientras está oculto
    cal.refresh()
    assert cal._dirty is True
    assert len(called) == 0  # No ejecutó la consulta pesada

    # Llamar a refresh(force=True)
    cal.refresh(force=True)
    assert cal._dirty is False
    assert len(called) > 0


def test_export_dialog_initial_state_and_toggles(qapp, db_path):
    board_id = database.create_board("Tablero Export", db_path=db_path)
    dlg = ExportDialog(db_path=db_path, active_board_id=board_id)

    assert dlg.radio_current.isChecked()
    assert dlg.radio_json.isChecked()
    assert dlg.check_json_tasks.isEnabled()
    assert dlg.check_json_tasks.isChecked()

    # Cambiar a CSV: la opción de tareas en JSON se deshabilita
    dlg.radio_csv.setChecked(True)
    assert dlg.check_json_tasks.isEnabled() is False

    # Cambiar a Markdown: se habilita la opción de detalles
    dlg.radio_md.setChecked(True)
    assert dlg.check_md_details.isEnabled() is True

    dlg.reject()


def test_import_confirmation_dialog_initial_state(qapp, db_path):
    boards_data = [
        {
            "name": "B1",
            "columns": [
                {"name": "C1", "tasks": [{"title": "T1"}]}
            ]
        }
    ]
    stats = {"boards": 1, "columns": 1, "tasks": 1}
    dlg = ImportConfirmationDialog("test.json", boards_data, stats, db_path=db_path)

    assert dlg.radio_full.isChecked()
    assert dlg.radio_structure.isChecked() is False

    dlg.reject()


def test_board_view_sync_btn_states(qapp, db_path, tmp_path):
    """Verifica que el botón de sincronización de la cabecera muestra el estado correcto (desvinculado y vinculado)."""
    from board_view import BoardViewWidget
    import database
    import board_sync

    board_id = database.create_board("Tablero UI Sync", db_path=db_path)
    database.create_column(board_id, "Col1", db_path=db_path)

    view = BoardViewWidget(db_path=db_path)
    view.load_board(board_id)

    # Estado desvinculado
    assert "Link" in view.sync_btn.text()

    # Vincular a archivo compartido
    sync_file = str(tmp_path / "ui_test.ekboard")
    board_sync.sync_board_with_file(board_id, sync_file, db_path=db_path)

    # Recargar tablero
    view.load_board(board_id)
    assert "Synced" in view.sync_btn.text()
    assert sync_file in view.sync_btn.toolTip()


def test_sidebar_board_button_cloud_badge(qapp):
    """Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral."""
    from sidebar import BoardButton

    btn_local = BoardButton(1, "Local", "#3b82f6", sync_path=None)
    assert "☁️" not in btn_local.label.text()
    assert btn_local.label.text() == "Local"

    btn_synced = BoardButton(2, "Compartido", "#3b82f6", sync_path="C:/OneDrive/tablero.ekboard")
    assert not btn_synced.badge_icon.pixmap().isNull()
    assert "Compartido" in btn_synced.label.text()


def test_task_card_ctrl_click_and_selection_state(qapp):
    """Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto visual."""
    from widgets import TaskCard
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtCore import QEvent, QPointF, Qt

    card = TaskCard({"id": 10, "title": "Test Multi-Select", "column_id": 1})
    assert card.is_selected is False
    assert card.selection_badge.isHidden() is True

    card.set_selected(True)
    assert card.is_selected is True
    assert card.selection_badge.isHidden() is False

    # Comprobar emisión de ctrl_clicked con modificador Control
    events_received = []
    card.ctrl_clicked.connect(lambda tid: events_received.append(("ctrl", tid)))
    card.clicked.connect(lambda tid: events_received.append(("normal", tid)))

    pos = QPointF(10, 10)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ControlModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.ControlModifier)
    card.mousePressEvent(press)
    card.mouseReleaseEvent(release)

    assert events_received == [("ctrl", 10)]


def test_board_view_multi_selection_bar_and_escape(qapp, db_path):
    """Verifica que seleccionar tarjetas muestra la barra inferior y Escape las deselecciona."""
    from board_view import BoardViewWidget
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent, Qt
    import database

    board_id = database.create_board("Tablero Selección", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    t1 = database.create_task(col_id, "Tarea A", db_path=db_path)
    t2 = database.create_task(col_id, "Tarea B", db_path=db_path)

    view = BoardViewWidget(db_path=db_path)
    view.load_board(board_id)

    assert view.selection_bar.isHidden() is True
    assert len(view.selected_task_ids) == 0

    # Simular selección de t1
    view._handle_task_ctrl_clicked(t1, col_id)
    assert view.selection_bar.isHidden() is False
    assert len(view.selected_task_ids) == 1
    assert "1" in view.selection_bar_label.text()

    # Simular selección de t2
    view._handle_task_ctrl_clicked(t2, col_id)
    assert len(view.selected_task_ids) == 2
    assert "2" in view.selection_bar_label.text()

    # Simular Escape para deseleccionar
    key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
    view.keyPressEvent(key_event)

    assert len(view.selected_task_ids) == 0
    assert view.selection_bar.isHidden() is True


def test_ai_spec_dialog_loads_and_generates(qapp, db_path):
    """Verifica la carga del diálogo de SPEC y la generación de especificación técnica."""
    from ai_spec_dialog import AiSpecDialog
    import database

    board_id = database.create_board("Tablero IA", db_path=db_path)
    col_id = database.create_column(board_id, "Backlog", db_path=db_path)
    t1 = database.create_task(col_id, "Autenticación OAuth2", description="Flujo PKCE", db_path=db_path)
    t2 = database.create_task(col_id, "Tokens en SQLite", description="Almacenar cifrado", db_path=db_path)

    dlg = AiSpecDialog([t1, t2], board_id, db_path)
    assert len(dlg.tasks_data) == 2

    # Ejecutar generación (usará el generador estructural integrado si no hay LLM externo corriendo)
    dlg.start_generation()
    if dlg._gen_thread:
        dlg._gen_thread.wait(5000)
    qapp.processEvents()

    spec_text = dlg.spec_edit.toPlainText()
    assert "# FEATURE PLAN:" in spec_text or "# SPEC:" in spec_text
    assert "Autenticación OAuth2" in spec_text
    assert "Tokens en SQLite" in spec_text

    dlg.reject()


def test_cloud_sync_info_dialog_constructs_and_accepts(qapp):
    """Verifica que CloudSyncInfoDialog se construye con las instrucciones de los proveedores y emite accept."""
    from cloud_sync_dialog import CloudSyncInfoDialog
    dlg = CloudSyncInfoDialog("Tablero_Test")
    assert dlg.windowTitle() == "Link board to Cloud"
    assert hasattr(dlg, "continue_btn")
    assert hasattr(dlg, "cancel_btn")
    dlg.continue_btn.click()
    assert dlg.result() == 1  # Accepted


def test_markdown_edit_table_word_style(qapp):
    """Verifica que insert_table genera tablas estilo Word con celdas centradas."""
    from detail_dialog.markdown_edit import MarkdownTextEdit
    edit = MarkdownTextEdit()
    edit.insert_table(rows=2, cols=3)
    html = edit.toHtml()
    assert "<table" in html.lower()
    # Verifica bordes y alineación centrada
    assert "border:" in html or "border=" in html
    assert "center" in html.lower()


def test_markdown_edit_text_alignment(qapp):
    """Verifica alineaciones de texto (izq, centro, der, justificado) y sincronización de toolbar."""
    from detail_dialog.markdown_edit import MarkdownTextEdit, RichTextToolbar
    edit = MarkdownTextEdit()
    toolbar = RichTextToolbar(edit)
    edit.setPlainText("Texto para probar alineacion")

    edit.align_center()
    toolbar.sync_buttons()
    assert bool(edit.alignment() & Qt.AlignHCenter)
    assert toolbar.align_center_btn.isChecked() is True
    assert toolbar.align_left_btn.isChecked() is False

    edit.align_right()
    toolbar.sync_buttons()
    assert bool(edit.alignment() & Qt.AlignRight)
    assert toolbar.align_right_btn.isChecked() is True

    edit.align_justify()
    toolbar.sync_buttons()
    assert bool(edit.alignment() & Qt.AlignJustify)
    assert toolbar.align_justify_btn.isChecked() is True

    edit.align_left()
    toolbar.sync_buttons()
    assert bool(edit.alignment() & Qt.AlignLeft) or edit.alignment() == Qt.AlignLeft
    assert toolbar.align_left_btn.isChecked() is True


def test_markdown_edit_case_conversions(qapp):
    """Verifica la conversión a MAYÚSCULAS y minúsculas con selección y palabra bajo cursor."""
    from PySide6.QtGui import QTextCursor
    from detail_dialog.markdown_edit import MarkdownTextEdit

    edit = MarkdownTextEdit()
    edit.setPlainText("hola mundo")

    # Selección completa
    cursor = edit.textCursor()
    cursor.select(QTextCursor.Document)
    edit.setTextCursor(cursor)

    edit.to_uppercase()
    assert edit.toPlainText() == "HOLA MUNDO"

    edit.to_lowercase()
    assert edit.toPlainText() == "hola mundo"

    edit.toggle_case()
    assert edit.toPlainText() == "HOLA MUNDO"

    edit.toggle_case()
    assert edit.toPlainText() == "hola mundo"

    # Conversión de la palabra bajo el cursor (sin selección)
    cursor.setPosition(2)
    edit.setTextCursor(cursor)
    edit.to_uppercase()
    assert edit.toPlainText() == "HOLA mundo"


def test_shortcuts_dialog_includes_new_editor_shortcuts(qapp):
    """Verifica que ShortcutsDialog carga y contiene los nuevos atajos de edición."""
    from shortcuts_dialog import ShortcutsDialog
    dlg = ShortcutsDialog()
    assert dlg.windowTitle() != ""
    labels = [c.text() for c in dlg.findChildren(QLabel)]
    combined = " ".join(labels)
    assert "Align text" in combined
    assert "UPPERCASE" in combined


def test_task_detail_dialog_width_and_toolbar_single_line(qapp, db_path):
    """Verifica que TaskDetailDialog tenga suficiente anchura y que el panel derecho acomode los botones en 1 línea."""
    import database
    from detail_dialog import TaskDetailDialog

    board_id = database.create_board("B1", db_path=db_path)
    col_id = database.create_column(board_id, "C1", db_path=db_path)
    t_id = database.create_task(col_id, "T1", db_path=db_path)

    dlg = TaskDetailDialog(t_id, db_path=db_path)
    assert dlg.width() >= 1200
    assert dlg.right_panel.minimumWidth() >= 480
    dlg.close()


def test_ai_spec_dialog_expanded_widths(qapp, db_path):
    """Verifica que AiSpecDialog tenga suficiente anchura y que mode_combo y model_combo no se trunquen."""
    import database
    from ai_spec_dialog import AiSpecDialog

    board_id = database.create_board("B2", db_path=db_path)
    col_id = database.create_column(board_id, "C2", db_path=db_path)
    t_id = database.create_task(col_id, "T2", db_path=db_path)

    dlg = AiSpecDialog([t_id], board_id, db_path=db_path)
    assert dlg.width() >= 1000
    assert dlg.minimumWidth() >= 980
    assert dlg.model_combo.minimumWidth() >= 240
    if dlg.model_combo.lineEdit():
        assert dlg.model_combo.lineEdit().cursorPosition() == 0
    dlg.close()


def test_bulk_add_task_dialog(qapp, db_path):
    """Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas seleccionadas."""
    import database
    from bulk_add_dialog import BulkAddTaskDialog

    board_id = database.create_board("Tablero Bulk", db_path=db_path)
    col1_id = database.create_column(board_id, "Columna 1", db_path=db_path)
    col2_id = database.create_column(board_id, "Columna 2", db_path=db_path)

    dlg = BulkAddTaskDialog(board_id, db_path=db_path)
    dlg.table.item(0, 0).setText("Tarea Bulk 1")
    dlg.table.item(0, 1).setText("Desc Bulk 1")
    dlg.add_row()
    dlg.table.item(1, 0).setText("Tarea Bulk 2")
    dlg.table.item(1, 1).setText("Desc Bulk 2")
    combo2 = dlg.table.cellWidget(1, 2)
    combo2.setCurrentIndex(1)

    dlg._on_create()

    tasks1 = database.get_tasks(col1_id, db_path=db_path)
    tasks2 = database.get_tasks(col2_id, db_path=db_path)
    assert len(tasks1) == 1
    assert tasks1[0]["title"] == "Tarea Bulk 1"
    assert tasks1[0]["description"] == "Desc Bulk 1"
    assert len(tasks2) == 1
    assert tasks2[0]["title"] == "Tarea Bulk 2"
    assert tasks2[0]["description"] == "Desc Bulk 2"
    dlg.close()


def test_task_detail_notes_edited_and_row_c(qapp, db_path):
    """Verifica el label de última edición de notas y que Priority y LinkedIn board estén en la tercera fila."""
    import database
    from detail_dialog import TaskDetailDialog

    board_id = database.create_board("B_Notes", db_path=db_path)
    col_id = database.create_column(board_id, "C_Notes", db_path=db_path)
    t_id = database.create_task(col_id, "T_Notes", description="Texto inicial", db_path=db_path)

    dlg = TaskDetailDialog(t_id, db_path=db_path)
    assert hasattr(dlg, "notes_edited_label")
    assert dlg.notes_edited_label.text() != ""

    assert hasattr(dlg, "priority_combo")
    assert hasattr(dlg, "linked_board_combo")
    assert dlg.priority_combo.count() > 0
    dlg.close()


def test_markdown_edit_quote_and_local_link(qapp):
    """Verifica la inserción de citas estructuradas y la emisión de señal para enlaces locales."""
    import os
    from detail_dialog.markdown_edit import MarkdownTextEdit
    from PySide6.QtCore import QMimeData, QUrl

    editor = MarkdownTextEdit()
    editor.insert_quote()
    html_content = editor.toHtml()
    assert "<table" in html_content
    assert "border=" in html_content or "cellpadding=" in html_content

    received = []
    editor.local_link_pasted.connect(lambda url, label: received.append((url, label)))

    mime = QMimeData()
    test_file = os.path.abspath("documento.pdf")
    mime.setUrls([QUrl.fromLocalFile(test_file)])
    editor.insertFromMimeData(mime)

    assert len(received) == 1
    assert "documento.pdf" in received[0][0]
    assert received[0][1] == "documento.pdf"


def test_markdown_edit_image_resize_methods(qapp):
    """Verifica que el método _resize_image calcula y aplica las dimensiones escaladas."""
    from detail_dialog.markdown_edit import MarkdownTextEdit
    from PySide6.QtGui import QImage, QTextCursor

    editor = MarkdownTextEdit()
    editor._insert_image(QImage(200, 100, QImage.Format.Format_RGB32))

    cursor = editor.textCursor()
    cursor.movePosition(QTextCursor.Start)
    cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)

    editor._resize_image(cursor, 0.5)
    fmt = cursor.charFormat().toImageFormat()
    assert fmt.isValid()
    assert fmt.width() == 100.0
    assert fmt.height() == 50.0

    editor._resize_image(cursor, custom_width=300, custom_height=150)
    fmt2 = cursor.charFormat().toImageFormat()
    assert fmt2.width() == 300.0
    assert fmt2.height() == 150.0


# --- i18n & SettingsDialog: Idioma / Polish ---

def test_settings_dialog_constructs_with_saved_language(qapp, db_path):
    database.set_setting("language", "es", db_path)
    dlg = SettingsDialog(db_path)
    assert dlg.lang_combo.currentIndex() == 1
    # Cleanup
    strings.set_language("en")


def test_settings_dialog_language_change_persists_and_emits(qapp, db_path):
    database.set_setting("language", "en", db_path)
    dlg = SettingsDialog(db_path)
    emitted = []
    dlg.language_changed.connect(emitted.append)
    dlg.lang_combo.setCurrentIndex(1)
    assert emitted == ["es"]
    assert database.get_setting("language", "en", db_path) == "es"
    assert strings.get_language() == "es"
    # Cleanup
    strings.set_language("en")


def test_i18n_strings_catalog_and_fallback():
    langs = strings.get_available_languages()
    assert "en" in langs and "es" in langs
    assert strings.get_language() == "en"

    # Switch to Spanish
    strings.set_language("es")
    assert strings.get_language() == "es"
    assert strings.t("settings.header") == "Ajustes"
    assert strings.t("main.window_title", version="1.2.3") == "Ekin v1.2.3"

    # Switch back to English
    strings.set_language("en")
    assert strings.get_language() == "en"
    assert strings.t("settings.header") == "Settings"

    # Fallback to English when key missing in Spanish
    orig_es = strings.STRINGS_ES.get("test.only_in_en")
    try:
        strings.STRINGS_EN["test.only_in_en"] = "Hello English Only"
        if "test.only_in_en" in strings.STRINGS_ES:
            del strings.STRINGS_ES["test.only_in_en"]
        strings.set_language("es")
        assert strings.t("test.only_in_en") == "Hello English Only"
    finally:
        strings.STRINGS_EN.pop("test.only_in_en", None)
        if orig_es:
            strings.STRINGS_ES["test.only_in_en"] = orig_es
        strings.set_language("en")


def test_styles_qcalendarwidget_rules():
    qss = styles.build_qss(styles.COLORS)
    assert "QCalendarWidget" in qss
    assert "qt_calendar_navigationbar" in qss
    assert "QCalendarWidget QTableView" in qss
    assert "QCalendarWidget QToolButton" in qss


def test_warm_syntax_highlighting_style():
    from detail_dialog.markdown_edit import format_code_block_html, _get_warm_pygments_style
    style_cls = _get_warm_pygments_style()
    assert style_cls is not None
    html_code = format_code_block_html("def foo():\n    return 'bar'", "python")
    assert "<pre" in html_code
    assert "action:delete_code_block" in html_code
    assert "#2e2b25" in html_code


def test_sidebar_anchors_logo_path(qapp, db_path):
    """Verifica que SidebarWidget localiza el logo de la aplicación anclado a _APP_DIR."""
    import os
    from sidebar import SidebarWidget, _APP_DIR
    sb = SidebarWidget(db_path=db_path)
    assert os.path.exists(os.path.join(_APP_DIR, "ekin_icon.png"))
    labels = sb.findChildren(QLabel)
    logo_labels = [lbl for lbl in labels if lbl.pixmap() is not None and not lbl.pixmap().isNull()]
    assert len(logo_labels) >= 1


def test_secondary_dialogs_schedule_delete_later_on_finished(qapp, db_path):
    """Verifica que los diálogos secundarios conectan deleteLater al emitir finished para no fugar memoria."""
    from PySide6.QtCore import QEvent
    from settings_dialog import SettingsDialog
    from bulk_add_dialog import BulkAddTaskDialog
    from shortcuts_dialog import ShortcutsDialog
    from cloud_sync_dialog import CloudSyncInfoDialog
    import database

    parent = QWidget()

    b_id = database.create_board("Test Board", db_path=db_path)
    database.create_column(b_id, "Col", db_path=db_path)

    dlg_settings = SettingsDialog(db_path, parent=parent)
    assert dlg_settings in parent.children()
    dlg_settings.accept()
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)
    assert dlg_settings not in parent.children()

    dlg_bulk = BulkAddTaskDialog(b_id, db_path=db_path, parent=parent)
    assert dlg_bulk in parent.children()
    dlg_bulk.reject()
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)
    assert dlg_bulk not in parent.children()

    dlg_shortcuts = ShortcutsDialog(parent=parent)
    assert dlg_shortcuts in parent.children()
    dlg_shortcuts.accept()
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)
    assert dlg_shortcuts not in parent.children()

    dlg_sync = CloudSyncInfoDialog(parent=parent)
    assert dlg_sync in parent.children()
    dlg_sync.reject()
    qapp.sendPostedEvents(None, QEvent.DeferredDelete)
    assert dlg_sync not in parent.children()


def test_column_edit_dialog_validation_and_data(qapp):
    from board_dialogs import ColumnEditDialog
    from PySide6.QtWidgets import QMessageBox

    dlg = ColumnEditDialog(title="Nueva Columna", name="", color="#3b82f6", wip_limit=5)
    # Nombre vacío no debe aceptar
    dlg.name_input.setText("   ")
    warned = []
    orig_warn = QMessageBox.warning
    try:
        QMessageBox.warning = lambda *a, **k: warned.append(a)
        dlg.validate_and_accept()
        assert len(warned) == 1
        assert dlg.result() != ColumnEditDialog.Accepted

        # Con nombre válido
        dlg.name_input.setText("En Revisión")
        dlg.validate_and_accept()
        assert dlg.result() == ColumnEditDialog.Accepted
        name, color, wip = dlg.get_data()
        assert name == "En Revisión"
        assert color == "#3b82f6"
        assert wip == 5
    finally:
        QMessageBox.warning = orig_warn
        dlg.close()


def test_board_selection_dialog_empty_and_selection(qapp, db_path):
    from board_dialogs import BoardSelectionDialog
    import database

    # Caso 1: Sin otros tableros disponibles
    b1 = database.create_board("Tablero 1", db_path=db_path)
    dlg_empty = BoardSelectionDialog("Mover", "Mover Columna", exclude_board_id=b1, db_path=db_path)
    assert not dlg_empty.ok_btn.isEnabled()
    dlg_empty.close()

    # Caso 2: Con tableros disponibles
    b2 = database.create_board("Tablero 2", db_path=db_path)
    dlg = BoardSelectionDialog("Mover", "Mover Columna", exclude_board_id=b1, db_path=db_path)
    assert dlg.ok_btn.isEnabled()
    assert len(dlg.available_boards) == 1
    assert dlg.available_boards[0]["id"] == b2
    dlg.accept_selection()
    assert dlg.selected_board_id == b2
    dlg.close()


def test_task_list_area_drop_indicator(qapp):
    from widgets import TaskListArea, TaskCard
    from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
    from PySide6.QtCore import QMimeData, QPointF, Qt

    area = TaskListArea(column_id=10)
    task1 = {"id": 101, "title": "Card 1", "column_id": 10, "due_date": None, "timer_started_at": None, "subtasks": []}
    task2 = {"id": 102, "title": "Card 2", "column_id": 10, "due_date": None, "timer_started_at": None, "subtasks": []}
    card1 = TaskCard(task1, parent=area)
    card2 = TaskCard(task2, parent=area)
    area.list_layout.addWidget(card1)
    area.list_layout.addWidget(card2)

    mime = QMimeData()
    mime.setData("application/x-ekin-task-id", b"999")

    # Simular dragEnter
    enter_ev = QDragEnterEvent(QPointF(10, 5).toPoint(), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    area.dragEnterEvent(enter_ev)
    assert area._drop_indicator is not None
    assert not area._drop_indicator.isHidden()
    assert area.list_layout.indexOf(area._drop_indicator) == 0

    # Simular dragLeave
    leave_ev = QDragLeaveEvent()
    area.dragLeaveEvent(leave_ev)
    assert area._drop_indicator.parent() is None

    # Simular drop
    dropped = []
    area.task_dropped.connect(lambda tid, cid, pos: dropped.append((tid, cid, pos)))
    drop_ev = QDropEvent(QPointF(10, 150).toPoint(), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    area.dropEvent(drop_ev)
    assert len(dropped) == 1
    assert dropped[0][0] == 999
    assert dropped[0][1] == 10
    assert area._drop_indicator.parent() is None


def test_search_dialog_filters_and_activation(qapp, db_path):
    """Verifica que SearchDialog liste tareas, filtre por texto/tablero y emita task_activated."""
    from search_dialog import SearchDialog

    board_id = database.create_board("Tablero Busqueda", "#2563eb", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    database.create_task(col_id, "Comprar leche", description="Desnatada", db_path=db_path)
    t2 = database.create_task(col_id, "Llamar al dentista", description="Cita anual", db_path=db_path)

    dlg = SearchDialog(db_path=db_path)
    dlg.refresh_results()
    assert dlg.results_layout.count() >= 2

    # Filtrar por texto
    dlg.text_input.setText("dentista")
    assert dlg.results_layout.count() == 1

    # Verificar emisión de señal task_activated al hacer clic
    activated = []
    dlg.task_activated.connect(lambda tid, bid: activated.append((tid, bid)))
    item = dlg.results_layout.itemAt(0)
    assert item is not None and item.widget() is not None
    item.widget().click()
    assert len(activated) == 1
    assert activated[0] == (t2, board_id)
    dlg.deleteLater()


def test_color_circles_picker_selection_and_signal(qapp):
    """Verifica que ColorCirclesPicker seleccione colores y emita color_changed."""
    from color_picker import ColorCirclesPicker

    picker = ColorCirclesPicker(current="#ef4444")
    assert picker.get_color() == "#ef4444"

    emitted = []
    picker.color_changed.connect(lambda c: emitted.append(c))

    picker.set_color("#10b981")
    assert picker.get_color() == "#10b981"
    assert "#10b981" in emitted
    picker.deleteLater()


# --- SettingsDialog & LandingTourDialog (v1.0.3) ---

def test_settings_dialog_check_updates_button_emits_signal(qapp, db_path):
    """Verifica que el botón 'Buscar ahora' en ajustes emita check_updates_requested."""
    from settings_dialog import SettingsDialog

    dlg = SettingsDialog(db_path)
    emitted = []
    dlg.check_updates_requested.connect(lambda: emitted.append(True))

    buttons = dlg.findChildren(QPushButton)
    update_btn = next((b for b in buttons if t("settings.check_updates_btn").strip() in b.text()), None)
    assert update_btn is not None
    update_btn.click()
    assert len(emitted) == 1
    dlg.deleteLater()


def test_landing_tour_dialog_navigation_and_persistence(qapp, db_path):
    """Verifica la navegación paso a paso y la persistencia de LandingTourDialog."""
    from onboarding_dialog import LandingTourDialog

    database.set_setting("onboarding_tour_shown", "0", db_path)
    dlg = LandingTourDialog(db_path=db_path)

    # Estado inicial: primera diapositiva (índice 0)
    assert dlg._current_index == 0
    assert dlg.stack.currentIndex() == 0
    assert dlg.prev_btn.isHidden() or not dlg.prev_btn.isEnabled()
    assert t("landing.next_btn").strip() in dlg.next_btn.text()

    # Avanzar a la diapositiva 1
    dlg.next_btn.click()
    assert dlg._current_index == 1
    assert dlg.stack.currentIndex() == 1
    assert dlg.prev_btn.isEnabled()

    # Ir directamente a la última diapositiva (índice 3)
    dlg._go_to_slide(3)
    assert dlg._current_index == 3
    assert t("landing.start_btn").strip() in dlg.next_btn.text()

    # Retroceder una
    dlg.prev_btn.click()
    assert dlg._current_index == 2

    # Avanzar a la última y pulsar Comenzar
    dlg.next_btn.click()
    assert dlg._current_index == 3
    dlg.next_btn.click()
    assert database.get_setting("onboarding_tour_shown", "0", db_path) == "1"

    dlg.deleteLater()


def test_landing_tour_dialog_dont_show_checkbox(qapp, db_path):
    """Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el ajuste."""
    from onboarding_dialog import LandingTourDialog

    database.set_setting("onboarding_tour_shown", "0", db_path)
    dlg = LandingTourDialog(db_path=db_path)
    assert not dlg.dont_show_chk.isChecked()

    dlg.dont_show_chk.setChecked(True)
    assert database.get_setting("onboarding_tour_shown", "0", db_path) == "1"

    dlg.dont_show_chk.setChecked(False)
    assert database.get_setting("onboarding_tour_shown", "0", db_path) == "0"

    dlg.deleteLater()


def test_interactive_tour_banner_navigation_and_actions(qapp, db_path):
    """Verifica la navegación paso a paso, emisión de señales y finalización de InteractiveTourBanner."""
    from onboarding_dialog import InteractiveTourBanner

    database.set_setting("interactive_tour_dismissed", "0", db_path)
    database.set_setting("interactive_tour_completed", "0", db_path)

    banner = InteractiveTourBanner(db_path=db_path)
    banner.show()

    # Estado inicial: Paso 0
    assert banner._current_step == 0
    assert not banner.prev_btn.isEnabled()
    assert t("tour.banner.next_btn").strip() in banner.next_btn.text()
    assert t("tour.banner.step1_title") in banner.step_title.text()

    # Probar señal de acción en paso 0
    actions_emitted = []
    banner.action_triggered.connect(lambda s: actions_emitted.append(s))
    banner.action_btn.click()
    assert actions_emitted == [0]

    # Avanzar a paso 1
    steps_emitted = []
    banner.step_changed.connect(lambda s: steps_emitted.append(s))
    banner.next_btn.click()
    assert banner._current_step == 1
    assert steps_emitted == [1]
    assert banner.prev_btn.isEnabled()
    assert t("tour.banner.step2_title") in banner.step_title.text()

    # Probar navegación directa mediante los dots interactivos
    banner._dots[2].click()
    assert banner._current_step == 2
    assert t("tour.banner.step3_title") in banner.step_title.text()

    # Probar botón anterior
    banner.prev_btn.click()
    assert banner._current_step == 1

    # Ir a paso 3 (último)
    banner.go_to_step(3)
    assert banner._current_step == 3
    assert t("tour.banner.finish_btn").replace("✓", "").strip() in banner.next_btn.text()

    # Finalizar tour pulsando el botón final
    completed_emitted = []
    banner.tour_completed.connect(lambda: completed_emitted.append(True))
    banner.next_btn.click()
    assert len(completed_emitted) == 1
    assert banner.isHidden()
    assert database.get_setting("interactive_tour_completed", "0", db_path) == "1"
    assert database.get_setting("interactive_tour_dismissed", "0", db_path) == "1"

    banner.deleteLater()


def test_interactive_tour_banner_dismiss(qapp, db_path):
    """Verifica que el botón cerrar descarte el tour y persista interactive_tour_dismissed."""
    from onboarding_dialog import InteractiveTourBanner

    database.set_setting("interactive_tour_dismissed", "0", db_path)
    banner = InteractiveTourBanner(db_path=db_path)
    banner.show()

    dismissed = []
    banner.tour_dismissed.connect(lambda: dismissed.append(True))
    banner.close_btn.click()

    assert len(dismissed) == 1
    assert banner.isHidden()
    assert database.get_setting("interactive_tour_dismissed", "0", db_path) == "1"

    banner.deleteLater()


def test_board_view_interactive_tour_lifecycle(qapp, db_path):
    """Verifica que BoardViewWidget muestre y oculte el banner del tour según el tablero y su estado."""
    from board_view import BoardViewWidget
    from templates import create_getting_started_board

    database.set_setting("interactive_tour_dismissed", "0", db_path)
    getting_started_id = create_getting_started_board(db_path=db_path)
    blank_board_id = database.create_board("Tablero Usuario", "#10b981", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.show()

    # 1. Al cargar el tablero demo Primeros Pasos, el banner debe mostrarse
    bv.load_board(getting_started_id, notify=False)
    assert hasattr(bv, "tour_banner")
    assert not bv.tour_banner.isHidden()

    # 2. Al conmutar a otro tablero, el banner se oculta automáticamente
    bv.load_board(blank_board_id, notify=False)
    assert bv.tour_banner.isHidden()

    # 3. Forzar show_interactive_tour / hide_interactive_tour
    bv.show_interactive_tour(step=2)
    assert bv.tour_banner.isVisible()
    assert bv.tour_banner._current_step == 2

    bv.hide_interactive_tour()
    assert bv.tour_banner.isHidden()

    bv.deleteLater()


def test_settings_dialog_interactive_tour_button(qapp, db_path):
    """Verifica que el botón de Tour Interactivo en Ajustes emita interactive_tour_requested."""
    from settings_dialog import SettingsDialog

    dlg = SettingsDialog(db_path)
    emitted = []
    dlg.interactive_tour_requested.connect(lambda: emitted.append(True))

    buttons = dlg.findChildren(QPushButton)
    interactive_btn = next((b for b in buttons if t("settings.landing_interactive_tour_btn").strip() in b.text()), None)
    assert interactive_btn is not None
    interactive_btn.click()
    assert len(emitted) == 1

    dlg.deleteLater()


def test_calendar_view_weekdays_and_months_localization(qapp, db_path):
    """Verifica que CalendarViewWidget obtenga nombres de meses y días de la semana dinámicos según el idioma."""
    from calendar_view import CalendarViewWidget
    from strings import set_language

    cal = CalendarViewWidget(db_path=db_path)

    # En Español
    set_language("es")
    assert cal._get_weekdays() == ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
    assert cal._get_month_name(1) == "Enero"
    assert cal._get_month_name(12) == "Diciembre"
    assert cal._get_weekday_name(0) == "LUN"

    # En Inglés
    set_language("en")
    assert cal._get_weekdays() == ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    assert cal._get_month_name(1) == "January"
    assert cal._get_month_name(12) == "December"
    assert cal._get_weekday_name(0) == "MON"

    # Restaurar
    set_language("es")
    cal.deleteLater()


def test_calendar_view_on_task_rescheduled_and_drag_drop(qapp, db_path):
    """Verifica que _on_task_rescheduled actualice la fecha en la BD y emita data_changed."""
    from calendar_view import CalendarViewWidget, DayCell, _CAL_TASK_MIME
    from PySide6.QtCore import QMimeData, QByteArray, QPointF, Qt
    from PySide6.QtGui import QDropEvent
    from datetime import date

    # 1. Crear tarea con fecha inicial
    b_id = database.create_board("Cal Test Board", db_path=db_path)
    col_id = database.create_column(b_id, "Todo", db_path=db_path)
    t_id = database.create_task(col_id, "Tarea a Reprogramar", due_date="2026-09-01", db_path=db_path)

    cal = CalendarViewWidget(db_path=db_path)
    emitted = []
    cal.data_changed.connect(lambda: emitted.append(True))

    # 2. Invocar _on_task_rescheduled directamente
    cal._on_task_rescheduled(t_id, "2026-09-20")

    task = database.get_task(t_id, db_path=db_path)
    assert task["due_date"] == "2026-09-20"
    assert len(emitted) == 1

    # 3. Probar DayCell.dropEvent con QMimeData simulado
    cell = DayCell()
    cell.cell_date = date(2026, 9, 25)
    cell_emitted = []
    cell.task_rescheduled.connect(lambda tid, d: cell_emitted.append((tid, d)))

    mime = QMimeData()
    mime.setData(_CAL_TASK_MIME, QByteArray(str(t_id).encode("utf-8")))

    # Simular evento de soltado (drop)
    drop_ev = QDropEvent(
        QPointF(10, 10),
        Qt.DropAction.MoveAction,
        mime,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    cell.dropEvent(drop_ev)

    assert cell_emitted == [(t_id, "2026-09-25")]

    cal.deleteLater()
    cell.deleteLater()


def test_board_config_dialog_cloud_options(qapp):
    """Verifica que BoardConfigDialog muestre las opciones adecuadas según si el tablero está o no sincronizado."""
    from sidebar import BoardConfigDialog

    # No sincronizado
    dlg_unsynced = BoardConfigDialog(archived=False, is_synced=False)
    actions_unsynced = [btn.text().strip() for btn in dlg_unsynced.findChildren(QPushButton)]
    assert any(t("sync.link_btn").strip() in a for a in actions_unsynced)
    assert any(t("sync.menu_open_shared").strip() in a for a in actions_unsynced)
    assert not any(t("sync.menu_sync_now").strip() in a for a in actions_unsynced)
    dlg_unsynced.deleteLater()

    # Sincronizado
    dlg_synced = BoardConfigDialog(archived=False, is_synced=True)
    actions_synced = [btn.text().strip() for btn in dlg_synced.findChildren(QPushButton)]
    assert any(t("sync.menu_sync_now").strip() in a for a in actions_synced)
    assert any(t("sync.menu_unlink").strip() in a for a in actions_synced)
    assert not any(t("sync.link_btn").strip() in a for a in actions_synced)
    dlg_synced.deleteLater()
