"""Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas
pocas propiedades estructurales, sin interacción profunda. Necesitan el fixture
`qapp` (ver conftest.py) y se ejecutan bien con QT_QPA_PLATFORM=offscreen (igual
que en CI) o con un display real."""
from datetime import date, datetime, timedelta

import pytest
from PySide6.QtCore import Qt, QPoint, QMimeData, QEvent
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent, QImage, QMouseEvent
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

import database
import styles
from calendar_view import CalendarViewWidget
from sidebar import NotificationsPopup
from settings_dialog import SettingsDialog
from shortcuts_dialog import ShortcutsDialog
from detail_dialog import TaskDetailDialog
from detail_dialog.log_entry import LogEntryWidget
import detail_dialog.task_detail_dialog as task_detail_dialog_module
import detail_dialog.markdown_edit as markdown_edit_module
import detail_dialog.image_preview_dialog as image_preview_module
import detail_dialog.log_entry as log_entry_module
from widgets import ColumnWidget, TaskCard
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
    assert "última columna" in text
    assert "primera columna del tablero activo" not in text


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
    assert "⏱" in card.timer_badge_label.text()
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
    qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)
    # No debe lanzar ni comportarse de forma distinta a como ya lo hacía sin el fix.


# --- TaskDetailDialog: adjuntar archivos locales a los enlaces (post-v0.9.0) ---

def test_is_local_link_classifies_urls_vs_paths():
    _is_local_link = task_detail_dialog_module._is_local_link
    assert _is_local_link("https://x.com") is False
    assert _is_local_link("http://x.com") is False
    assert _is_local_link("mailto:a@b.com") is False
    assert _is_local_link("file://C:/x.txt") is False
    assert _is_local_link(r"C:\Users\foo\bar.pdf") is True
    assert _is_local_link("/home/user/file.txt") is True


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
    assert any(b.text().startswith("📎") for b in buttons)


def test_add_link_with_web_url_renders_with_link_icon(qapp, db_path):
    task_id = _make_task(db_path)
    dlg = TaskDetailDialog(task_id, db_path)

    dlg.link_url_input.setText("https://example.com")
    dlg.add_link()

    buttons = dlg.links_container.findChildren(QPushButton)
    assert any(b.text().startswith("🔗") for b in buttons)


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


def test_markdown_text_edit_wraps_pasted_image_in_anchor(qapp):
    editor = markdown_edit_module.MarkdownTextEdit()

    editor._insert_image(QImage(4, 4, QImage.Format.Format_RGB32))

    assert '<a href="data:image/png;base64,' in editor.toHtml()


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

    pos = QPoint(10, 10)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
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

    press_pos = QPoint(10, 10)
    release_pos = QPoint(50, 60)
    press = QMouseEvent(QEvent.Type.MouseButtonPress, press_pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    release = QMouseEvent(QEvent.Type.MouseButtonRelease, release_pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    editor.mousePressEvent(press)
    editor.mouseReleaseEvent(release)

    assert calls == []


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


def test_log_entry_widget_plain_text_keeps_default_cursor(qapp):
    log_data = {"id": 1, "content": "solo texto, sin imagen", "created_at": "2026-08-12 10:00:00"}

    widget = LogEntryWidget(log_data, lambda *a: None, lambda *a: None)

    assert widget.content_label.cursor().shape() != Qt.CursorShape.PointingHandCursor
