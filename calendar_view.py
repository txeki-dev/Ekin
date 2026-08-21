"""Vista de calendario mensual para Ekin: muestra las tareas por su fecha de vencimiento
y permite exportar a iCalendar (.ics) desde su diálogo de Ajustes."""
import calendar as _cal
from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QDialog, QFileDialog, QMessageBox, QSizePolicy, QApplication, QLineEdit,
    QScrollArea, QComboBox
)
from PySide6.QtGui import QColor, QPixmap, QIcon, QDrag, QDesktopServices

import database
import styles
import ics_export
from strings import t

_WEEKDAYS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
_MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def _swatch_icon(color, size=11):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


_CAL_TASK_MIME = "application/x-ekin-cal-task-id"


class CalendarChip(QPushButton):
    """Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día
    para cambiar su fecha de vencimiento."""
    def __init__(self, task_id, label, parent=None):
        super().__init__(label, parent)
        self.task_id = task_id
        self._drag_start = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return super().mouseMoveEvent(event)
        if (event.position().toPoint() - self._drag_start).manhattanLength() < QApplication.startDragDistance():
            return super().mouseMoveEvent(event)

        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(_CAL_TASK_MIME, str(self.task_id).encode("utf-8"))
        drag.setMimeData(mime)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        drag.exec(Qt.MoveAction)


class DayCell(QFrame):
    """Celda de un día del calendario: número + chips de tareas que vencen ese día.
    Acepta soltar un chip arrastrado para reprogramar su fecha de vencimiento."""
    task_clicked = Signal(int, int)  # task_id, board_id
    task_rescheduled = Signal(int, str)  # task_id, nueva_fecha_iso

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DayCell")
        self.setMinimumHeight(78)
        self.setAcceptDrops(True)
        self.cell_date = None       # date del día (None para celdas vacías)
        self._base_style = ""       # estilo actual, para restaurar tras el resalte de arrastre
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(5, 4, 5, 4)
        self._layout.setSpacing(2)
        self._layout.setAlignment(Qt.AlignTop)

        self.day_label = QLabel("")
        self.day_label.setObjectName("DayNumber")
        self._layout.addWidget(self.day_label)

    def _apply_style(self, style):
        self._base_style = style
        self.setStyleSheet(style)

    def set_day(self, day_number, tasks, is_today=False, cell_date=None, max_show=3):
        # Vaciar los chips previos (se conserva la etiqueta del día en el índice 0)
        while self._layout.count() > 1:
            item = self._layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cell_date = cell_date

        if day_number is None:
            self.day_label.setText("")
            self._apply_style(
                "#DayCell { background-color: transparent; border: 1px solid transparent; border-radius: 8px; }"
            )
            return

        self.day_label.setText(str(day_number))
        if is_today:
            self._apply_style(
                f"#DayCell {{ background-color: rgba(59,130,246,0.18);"
                f" border: 1.5px solid {styles.COLORS['accent_blue']}; border-radius: 8px; }}"
                f"#DayNumber {{ color: {styles.COLORS['accent_blue']}; font-weight: bold; }}"
            )
        else:
            self._apply_style(
                f"#DayCell {{ background-color: {styles.COLORS['bg_column']};"
                f" border: 1px solid {styles.COLORS['border']}; border-radius: 8px; }}"
                f"#DayNumber {{ color: {styles.COLORS['text_muted']}; font-weight: bold; }}"
            )

        for task in tasks[:max_show]:
            title = task["title"] or t("calendar.chip_no_title")
            label = title if len(title) <= 20 else title[:19] + "…"
            chip = CalendarChip(task["id"], label)
            chip.setObjectName("CalendarChip")
            chip.setIcon(_swatch_icon(task["board_color"]))
            chip.setCursor(Qt.PointingHandCursor)
            chip.setToolTip(t("calendar.chip_tooltip", board=task['board_name'], title=title))
            # Evita que un título largo ensanche la columna
            chip.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            chip.clicked.connect(
                lambda _=False, tid=task["id"], bid=task["board_id"]: self.task_clicked.emit(tid, bid)
            )
            self._layout.addWidget(chip)

        if len(tasks) > max_show:
            more = QLabel(t("calendar.more_tasks", count=len(tasks) - max_show))
            more.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-size: 9px; background: transparent; padding-left: 2px;"
            )
            self._layout.addWidget(more)

    def dragEnterEvent(self, event):
        if self.cell_date is not None and event.mimeData().hasFormat(_CAL_TASK_MIME):
            event.acceptProposedAction()
            self.setStyleSheet(
                f"#DayCell {{ background-color: rgba(59,130,246,0.30);"
                f" border: 1.5px dashed {styles.COLORS['accent_blue']}; border-radius: 8px; }}"
                f"#DayNumber {{ color: {styles.COLORS['accent_blue']}; font-weight: bold; }}"
            )
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.cell_date is not None and event.mimeData().hasFormat(_CAL_TASK_MIME):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self._base_style)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        self.setStyleSheet(self._base_style)
        if self.cell_date is not None and mime.hasFormat(_CAL_TASK_MIME):
            task_id = int(mime.data(_CAL_TASK_MIME).data().decode("utf-8"))
            event.acceptProposedAction()
            self.task_rescheduled.emit(task_id, self.cell_date.isoformat())
        else:
            event.ignore()


def _group_by_day(tasks):
    by_day = {}
    for task in tasks:
        by_day.setdefault(task["due_date"], []).append(task)
    return by_day


class CalendarViewWidget(QWidget):
    """Vista de calendario (mes / semana / día) con filtro por tablero y leyenda."""
    close_requested = Signal()
    task_activated = Signal(int, int)  # task_id, board_id
    data_changed = Signal()            # tras reprogramar una tarea (refresca campana/.ics)

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setObjectName("CalendarView")
        self.view_mode = "month"   # month | week | day
        self.anchor = date.today()
        self.cells = []
        self._modes = ["month", "week", "day"]
        self._dirty = False
        self._build_ui()
        self._rebuild_grid()
        self.refresh(force=True)

    def _build_ui(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(16, 16, 16, 16)
        self._root.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(6)

        prev_btn = QPushButton("‹")
        prev_btn.setObjectName("CalNavButton")
        prev_btn.setFixedSize(30, 28)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self.go_prev)

        next_btn = QPushButton("›")
        next_btn.setObjectName("CalNavButton")
        next_btn.setFixedSize(30, 28)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.go_next)

        self.period_label = QLabel("")
        self.period_label.setObjectName("CalendarMonthLabel")

        today_btn = QPushButton(t("calendar.today_btn"))
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self.go_today)

        header.addWidget(prev_btn)
        header.addWidget(next_btn)
        header.addSpacing(8)
        header.addWidget(self.period_label)
        header.addStretch()

        # Selector de vista (Mes/Semana/Día)
        self.mode_combo = QComboBox()
        for lbl in (t("calendar.mode_month"), t("calendar.mode_week"), t("calendar.mode_day")):
            self.mode_combo.addItem(lbl)
        self.mode_combo.setToolTip(t("calendar.mode_tooltip"))
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        header.addWidget(self.mode_combo)

        # Filtro por tablero
        self.board_combo = QComboBox()
        self.board_combo.setToolTip(t("calendar.board_filter_tooltip"))
        self.board_combo.currentIndexChanged.connect(lambda _=0: self.refresh())
        header.addWidget(self.board_combo)

        header.addWidget(today_btn)

        settings_btn = QPushButton(t("calendar.settings_btn"))
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setToolTip(t("calendar.settings_tooltip"))
        settings_btn.clicked.connect(self.open_settings)

        close_btn = QPushButton(t("calendar.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip(t("calendar.close_tooltip"))
        close_btn.clicked.connect(self.close_requested.emit)

        header.addWidget(settings_btn)
        header.addWidget(close_btn)
        self._root.addLayout(header)

        # Leyenda de tableros (color + nombre)
        legend_host = QWidget()
        self.legend = QHBoxLayout(legend_host)
        self.legend.setContentsMargins(2, 0, 2, 0)
        self.legend.setSpacing(12)
        self._root.addWidget(legend_host)

        # Rejilla (se reconstruye según el modo)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setSpacing(6)
        self._root.addWidget(self.grid_host, 1)

    def _make_cell(self):
        cell = DayCell()
        cell.task_clicked.connect(self.task_activated.emit)
        cell.task_rescheduled.connect(self._on_task_rescheduled)
        return cell

    def _rebuild_grid(self):
        """Reconstruye la rejilla de celdas según el modo de vista."""
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.cells = []
        for c in range(7):
            self.grid.setColumnStretch(c, 0)
        for r in range(7):
            self.grid.setRowStretch(r, 0)

        if self.view_mode == "day":
            cell = self._make_cell()
            self.grid.addWidget(cell, 0, 0)
            self.cells.append(cell)
            self.grid.setColumnStretch(0, 1)
            self.grid.setRowStretch(0, 1)
            return

        for col, name in enumerate(_WEEKDAYS):
            lbl = QLabel(name)
            lbl.setObjectName("WeekdayHeader")
            lbl.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(lbl, 0, col)
            self.grid.setColumnStretch(col, 1)

        rows = 6 if self.view_mode == "month" else 1
        for r in range(rows):
            for dow in range(7):
                cell = self._make_cell()
                self.grid.addWidget(cell, r + 1, dow)
                self.cells.append(cell)
            self.grid.setRowStretch(r + 1, 1)

    def _reload_board_filter(self):
        current = self.board_combo.currentData()
        self.board_combo.blockSignals(True)
        self.board_combo.clear()
        self.board_combo.addItem(t("calendar.all_boards"), None)
        for b in database.get_boards(self.db_path, include_archived=True):
            self.board_combo.addItem(b["name"], b["id"])
        idx = self.board_combo.findData(current)
        self.board_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.board_combo.blockSignals(False)

    def _reload_legend(self):
        while self.legend.count():
            item = self.legend.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        for b in database.get_boards(self.db_path):
            lab = QLabel(f"● {b['name']}")
            lab.setStyleSheet(f"color: {b['color']}; font-size: 11px; font-weight: bold; background: transparent;")
            self.legend.addWidget(lab)
        self.legend.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        if getattr(self, "_dirty", False):
            self.refresh(force=True)

    def refresh(self, force=False):
        """Recarga filtro/leyenda y pinta el periodo actual según el modo."""
        if not force and not self.isVisible():
            self._dirty = True
            return
        self._dirty = False
        self._reload_board_filter()
        self._reload_legend()
        board_id = self.board_combo.currentData()
        today = date.today()

        if self.view_mode == "month":
            self.period_label.setText(f"{_MONTHS[self.anchor.month - 1]} {self.anchor.year}")
            first_weekday, num_days = _cal.monthrange(self.anchor.year, self.anchor.month)
            start = date(self.anchor.year, self.anchor.month, 1)
            end = date(self.anchor.year, self.anchor.month, num_days)
            by_day = _group_by_day(database.get_scheduled_tasks(
                start.isoformat(), end.isoformat(), board_id=board_id, db_path=self.db_path))
            for idx, cell in enumerate(self.cells):
                day_number = idx - first_weekday + 1
                if 1 <= day_number <= num_days:
                    cd = date(self.anchor.year, self.anchor.month, day_number)
                    cell.set_day(day_number, by_day.get(cd.isoformat(), []),
                                 is_today=(cd == today), cell_date=cd)
                else:
                    cell.set_day(None, [])

        elif self.view_mode == "week":
            monday = self.anchor - timedelta(days=self.anchor.weekday())
            sunday = monday + timedelta(days=6)
            self.period_label.setText(
                t("calendar.week_period", start=monday.strftime('%d/%m'), end=sunday.strftime('%d/%m/%Y'))
            )
            by_day = _group_by_day(database.get_scheduled_tasks(
                monday.isoformat(), sunday.isoformat(), board_id=board_id, db_path=self.db_path))
            for i, cell in enumerate(self.cells):
                cd = monday + timedelta(days=i)
                cell.set_day(cd.day, by_day.get(cd.isoformat(), []),
                             is_today=(cd == today), cell_date=cd, max_show=8)

        else:  # day
            self.period_label.setText(f"{_WEEKDAYS[self.anchor.weekday()]} {self.anchor.strftime('%d/%m/%Y')}")
            tasks = database.get_scheduled_tasks(
                self.anchor.isoformat(), self.anchor.isoformat(), board_id=board_id, db_path=self.db_path)
            self.cells[0].set_day(self.anchor.day, tasks, is_today=(self.anchor == today),
                                  cell_date=self.anchor, max_show=50)

    def _on_mode_changed(self, index):
        self.view_mode = self._modes[index]
        self._rebuild_grid()
        self.refresh()

    def _on_task_rescheduled(self, task_id, iso_date):
        """Cambia la fecha de vencimiento de una tarea arrastrada a otro día."""
        database.update_task_due_date(task_id, iso_date, self.db_path)
        self.refresh()
        # Avisar a la app para refrescar la campana y reescribir el .ics sincronizado.
        self.data_changed.emit()

    def _shift(self, direction):
        if self.view_mode == "month":
            m = self.anchor.month - 1 + direction
            year = self.anchor.year + (m // 12)
            month = m % 12 + 1
            last = _cal.monthrange(year, month)[1]
            self.anchor = date(year, month, min(self.anchor.day, last))
        elif self.view_mode == "week":
            self.anchor = self.anchor + timedelta(days=7 * direction)
        else:
            self.anchor = self.anchor + timedelta(days=direction)
        self.refresh()

    def go_prev(self):
        self._shift(-1)

    def go_next(self):
        self._shift(1)

    def go_today(self):
        self.anchor = date.today()
        self.refresh()

    def open_settings(self):
        CalendarSettingsDialog(self.db_path, self).exec()


class CalendarSettingsDialog(QDialog):
    """Ajustes del calendario: sincronización iCalendar (.ics) para Google/Apple/Outlook.

    Modo recomendado: un archivo .ics que Ekin mantiene siempre al día y al que te
    suscribes UNA vez desde tu calendario (así altas/cambios/bajas se reflejan solos,
    sin duplicados). También ofrece una exportación puntual (copia snapshot).
    """
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle(t("calendar.settings_dialog.title"))
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(QLabel(t("calendar.settings_dialog.header")))

        info = QLabel(t("calendar.settings_dialog.info"))
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {styles.COLORS['text_muted']};")
        layout.addWidget(info)

        # --- Sincronización automática (feed suscribible) ---
        sync_frame = QFrame()
        sync_frame.setObjectName("SyncFrame")
        sync_frame.setStyleSheet(
            f"#SyncFrame {{ background-color: {styles.COLORS['bg_column']};"
            f" border: 1px solid {styles.COLORS['border']}; border-radius: 8px; }}"
        )
        sync_layout = QVBoxLayout(sync_frame)
        sync_layout.setContentsMargins(12, 12, 12, 12)
        sync_layout.setSpacing(8)

        sync_title = QLabel(t("calendar.settings_dialog.sync_title"))
        sync_layout.addWidget(sync_title)

        sync_desc = QLabel(t("calendar.settings_dialog.sync_desc"))
        sync_desc.setWordWrap(True)
        sync_desc.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        sync_layout.addWidget(sync_desc)

        # Feed por tablero: la sincronización automática puede ser global (un único
        # archivo con todos los tableros) o una por tablero (varios feeds independientes).
        self.sync_board_combo = QComboBox()
        self.sync_board_combo.setToolTip(t("calendar.settings_dialog.sync_board_tooltip"))
        self.sync_board_combo.addItem(t("calendar.all_boards"), None)
        for b in database.get_boards(self.db_path, include_archived=True):
            self.sync_board_combo.addItem(b["name"], b["id"])
        self.sync_board_combo.currentIndexChanged.connect(lambda *_: self._refresh_sync_label())
        sync_layout.addWidget(self.sync_board_combo)

        self.sync_path_label = QLabel("")
        self.sync_path_label.setWordWrap(True)
        self.sync_path_label.setStyleSheet("font-size: 11px;")
        sync_layout.addWidget(self.sync_path_label)

        sync_btns = QHBoxLayout()
        self.configure_btn = QPushButton(t("calendar.settings_dialog.configure_btn_initial"))
        self.configure_btn.setObjectName("PrimaryButton")
        self.configure_btn.setCursor(Qt.PointingHandCursor)
        self.configure_btn.clicked.connect(self.configure_sync)
        sync_btns.addWidget(self.configure_btn)
        self.disable_btn = QPushButton(t("calendar.settings_dialog.disable_btn"))
        self.disable_btn.setCursor(Qt.PointingHandCursor)
        self.disable_btn.clicked.connect(self.disable_sync)
        sync_btns.addWidget(self.disable_btn)
        sync_btns.addStretch()
        sync_layout.addLayout(sync_btns)

        layout.addWidget(sync_frame)

        # --- Suscribirse en tu calendario (pegar la URL pública del feed .ics) ---
        subscribe_frame = QFrame()
        subscribe_frame.setObjectName("SubscribeFrame")
        subscribe_frame.setStyleSheet(
            f"#SubscribeFrame {{ background-color: {styles.COLORS['bg_column']};"
            f" border: 1px solid {styles.COLORS['border']}; border-radius: 8px; }}"
        )
        subscribe_layout = QVBoxLayout(subscribe_frame)
        subscribe_layout.setContentsMargins(12, 12, 12, 12)
        subscribe_layout.setSpacing(8)

        subscribe_title = QLabel(t("calendar.settings_dialog.subscribe_title"))
        subscribe_layout.addWidget(subscribe_title)

        subscribe_desc = QLabel(t("calendar.settings_dialog.subscribe_desc"))
        subscribe_desc.setWordWrap(True)
        subscribe_desc.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        subscribe_layout.addWidget(subscribe_desc)

        self.public_url_input = QLineEdit(database.get_setting("ics_public_url", "", self.db_path))
        self.public_url_input.setPlaceholderText(t("calendar.settings_dialog.public_url_placeholder"))
        subscribe_layout.addWidget(self.public_url_input)

        provider_btns = QHBoxLayout()
        provider_btns.setSpacing(6)
        self.subscribe_btn = QPushButton("Google")
        self.subscribe_btn.setObjectName("PrimaryButton")
        self.subscribe_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_btn.setToolTip(t("calendar.settings_dialog.google_btn_tooltip"))
        self.subscribe_btn.clicked.connect(self.subscribe_google)
        provider_btns.addWidget(self.subscribe_btn)

        self.subscribe_outlook_btn = QPushButton("Outlook")
        self.subscribe_outlook_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_outlook_btn.setToolTip(t("calendar.settings_dialog.outlook_btn_tooltip"))
        self.subscribe_outlook_btn.clicked.connect(self.subscribe_outlook)
        provider_btns.addWidget(self.subscribe_outlook_btn)

        self.subscribe_apple_btn = QPushButton("Apple / iCloud")
        self.subscribe_apple_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_apple_btn.setToolTip(t("calendar.settings_dialog.apple_btn_tooltip"))
        self.subscribe_apple_btn.clicked.connect(self.subscribe_apple)
        provider_btns.addWidget(self.subscribe_apple_btn)
        provider_btns.addStretch()
        subscribe_layout.addLayout(provider_btns)

        layout.addWidget(subscribe_frame)

        # Guía detallada por proveedor (en un área con scroll para no alargar el diálogo)
        steps = QLabel(self._provider_guide_html())
        steps.setTextFormat(Qt.RichText)
        steps.setWordWrap(True)
        steps.setOpenExternalLinks(True)
        steps.setStyleSheet("font-size: 12px;")
        steps_scroll = QScrollArea()
        steps_scroll.setWidgetResizable(True)
        steps_scroll.setFrameShape(QFrame.NoFrame)
        steps_scroll.setStyleSheet("background: transparent; border: none;")
        steps_scroll.setMinimumHeight(150)
        steps_wrap = QWidget()
        steps_wrap.setStyleSheet("background: transparent;")
        steps_wrap_layout = QVBoxLayout(steps_wrap)
        steps_wrap_layout.setContentsMargins(2, 2, 2, 2)
        steps_wrap_layout.addWidget(steps)
        steps_wrap_layout.addStretch()
        steps_scroll.setWidget(steps_wrap)
        layout.addWidget(steps_scroll, 1)

        btns = QHBoxLayout()
        export_btn = QPushButton(t("calendar.export_once_btn"))
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setToolTip(t("calendar.export_once_tooltip"))
        export_btn.clicked.connect(self.export_once)
        btns.addWidget(export_btn)
        # Feed por tablero: exportar todos o solo un tablero
        self.export_board_combo = QComboBox()
        self.export_board_combo.setToolTip(t("calendar.export_board_tooltip"))
        self.export_board_combo.addItem(t("calendar.all_boards"), None)
        for b in database.get_boards(self.db_path, include_archived=True):
            self.export_board_combo.addItem(b["name"], b["id"])
        btns.addWidget(self.export_board_combo)
        btns.addStretch()
        close_btn = QPushButton(t("calendar.settings_dialog.close_btn"))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        self._refresh_sync_label()

    def _current_sync_board_id(self):
        """None = feed global (todos los tableros); si no, el id del tablero elegido."""
        return self.sync_board_combo.currentData()

    def _get_current_sync_path(self):
        board_id = self._current_sync_board_id()
        if board_id is None:
            return database.get_setting("ics_sync_path", "", self.db_path)
        return database.get_board_ics_sync_path(board_id, self.db_path) or ""

    def _refresh_sync_label(self):
        path = self._get_current_sync_path()
        if path:
            self.sync_path_label.setText(t("calendar.settings_dialog.sync_active", path=path))
            self.sync_path_label.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['success']};")
            self.disable_btn.setEnabled(True)
            self.configure_btn.setText(t("calendar.settings_dialog.configure_btn_change"))
        else:
            self.sync_path_label.setText(t("calendar.settings_dialog.sync_inactive"))
            self.sync_path_label.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['text_muted']};")
            self.disable_btn.setEnabled(False)
            self.configure_btn.setText(t("calendar.settings_dialog.configure_btn_initial"))

    def configure_sync(self):
        board_id = self._current_sync_board_id()
        current = self._get_current_sync_path()
        default = current or "ekin_calendario.ics"
        path, _ = QFileDialog.getSaveFileName(
            self, t("calendar.settings_dialog.configure_file_dialog_title"), default, "iCalendar (*.ics)"
        )
        if not path:
            return
        try:
            count = ics_export.export_ics(path, self.db_path, board_id=board_id)
        except Exception as exc:
            QMessageBox.critical(
                self, t("calendar.error_title"), t("calendar.settings_dialog.configure_error_body", error=exc)
            )
            return
        if board_id is None:
            database.set_setting("ics_sync_path", path, self.db_path)
        else:
            database.set_board_ics_sync_path(board_id, path, self.db_path)
        self._refresh_sync_label()
        QMessageBox.information(
            self, t("calendar.settings_dialog.sync_activated_title"),
            t("calendar.settings_dialog.sync_activated_body", count=count, path=path)
        )

    def disable_sync(self):
        board_id = self._current_sync_board_id()
        if board_id is None:
            database.set_setting("ics_sync_path", "", self.db_path)
        else:
            database.delete_board_ics_sync_path(board_id, self.db_path)
        self._refresh_sync_label()

    def _subscribe_url(self):
        """Valida y persiste la URL pública. Devuelve la URL, o None si está vacía."""
        url = self.public_url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, t("calendar.settings_dialog.empty_url_title"),
                t("calendar.settings_dialog.empty_url_body")
            )
            return None
        database.set_setting("ics_public_url", url, self.db_path)
        return url

    def subscribe_google(self):
        """Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google."""
        url = self._subscribe_url()
        if not url:
            return
        QApplication.clipboard().setText(url)
        QDesktopServices.openUrl(
            QUrl("https://calendar.google.com/calendar/u/0/r/settings/addbyurl")
        )
        QMessageBox.information(
            self, t("calendar.settings_dialog.google_title"), t("calendar.settings_dialog.google_body")
        )

    def subscribe_outlook(self):
        """Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com."""
        url = self._subscribe_url()
        if not url:
            return
        QApplication.clipboard().setText(url)
        QDesktopServices.openUrl(QUrl("https://outlook.live.com/calendar/0/addcalendar"))
        QMessageBox.information(
            self, t("calendar.settings_dialog.outlook_title"), t("calendar.settings_dialog.outlook_body")
        )

    def subscribe_apple(self):
        """Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud)."""
        url = self._subscribe_url()
        if not url:
            return
        webcal = url.replace("https://", "webcal://").replace("http://", "webcal://")
        QApplication.clipboard().setText(webcal)
        QMessageBox.information(
            self, t("calendar.settings_dialog.apple_title"), t("calendar.settings_dialog.apple_body")
        )

    @staticmethod
    def _provider_guide_html():
        """Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes)."""
        return t("calendar.settings_dialog.provider_guide")

    def export_once(self):
        board_id = self.export_board_combo.currentData()
        board_txt = "" if board_id is None else f"_{self.export_board_combo.currentText()}"
        default_name = f"ekin_calendario{board_txt}_{date.today().isoformat()}.ics"
        path, _ = QFileDialog.getSaveFileName(
            self, t("calendar.export_dialog_title"), default_name, "iCalendar (*.ics)"
        )
        if not path:
            return
        try:
            count = ics_export.export_ics(path, self.db_path, board_id=board_id)
        except Exception as exc:
            QMessageBox.critical(self, t("calendar.error_title"), t("calendar.export_error_body", error=exc))
            return
        QMessageBox.information(
            self, t("calendar.export_done_title"), t("calendar.export_done_body", count=count, path=path)
        )
