"""Vista de calendario mensual para Ekin: muestra las tareas por su fecha de vencimiento
y permite exportar a iCalendar (.ics) desde su diálogo de Ajustes."""
import calendar as _cal
from datetime import date

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QDialog, QFileDialog, QMessageBox, QSizePolicy
)
from PySide6.QtGui import QColor, QPixmap, QIcon

import database
import styles
import ics_export

_WEEKDAYS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
_MONTHS = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]


def _swatch_icon(color, size=11):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class DayCell(QFrame):
    """Celda de un día del calendario: número + chips de tareas que vencen ese día."""
    task_clicked = Signal(int, int)  # task_id, board_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DayCell")
        self.setMinimumHeight(78)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(5, 4, 5, 4)
        self._layout.setSpacing(2)
        self._layout.setAlignment(Qt.AlignTop)

        self.day_label = QLabel("")
        self.day_label.setObjectName("DayNumber")
        self._layout.addWidget(self.day_label)

    def set_day(self, day_number, tasks, is_today=False):
        # Vaciar los chips previos (se conserva la etiqueta del día en el índice 0)
        while self._layout.count() > 1:
            item = self._layout.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if day_number is None:
            self.day_label.setText("")
            self.setStyleSheet(
                f"#DayCell {{ background-color: transparent; border: 1px solid transparent; border-radius: 8px; }}"
            )
            return

        self.day_label.setText(str(day_number))
        if is_today:
            self.setStyleSheet(
                f"#DayCell {{ background-color: rgba(59,130,246,0.18);"
                f" border: 1.5px solid {styles.COLORS['accent_blue']}; border-radius: 8px; }}"
                f"#DayNumber {{ color: {styles.COLORS['accent_blue']}; font-weight: bold; }}"
            )
        else:
            self.setStyleSheet(
                f"#DayCell {{ background-color: {styles.COLORS['bg_column']};"
                f" border: 1px solid {styles.COLORS['border']}; border-radius: 8px; }}"
                f"#DayNumber {{ color: {styles.COLORS['text_muted']}; font-weight: bold; }}"
            )

        max_show = 3
        for t in tasks[:max_show]:
            title = t["title"] or "(sin título)"
            label = title if len(title) <= 20 else title[:19] + "…"
            chip = QPushButton(label)
            chip.setObjectName("CalendarChip")
            chip.setIcon(_swatch_icon(t["board_color"]))
            chip.setCursor(Qt.PointingHandCursor)
            chip.setToolTip(f"{t['board_name']} · {title}")
            # Evita que un título largo ensanche la columna
            chip.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            chip.clicked.connect(
                lambda _=False, tid=t["id"], bid=t["board_id"]: self.task_clicked.emit(tid, bid)
            )
            self._layout.addWidget(chip)

        if len(tasks) > max_show:
            more = QLabel(f"+{len(tasks) - max_show} más")
            more.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-size: 9px; background: transparent; padding-left: 2px;"
            )
            self._layout.addWidget(more)


class CalendarViewWidget(QWidget):
    """Vista mensual completa. Sustituye a la vista de tablero cuando está activa."""
    close_requested = Signal()
    task_activated = Signal(int, int)  # task_id, board_id

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setObjectName("CalendarView")
        today = date.today()
        self.year = today.year
        self.month = today.month
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # --- Cabecera: navegación + acciones ---
        header = QHBoxLayout()
        header.setSpacing(6)

        prev_btn = QPushButton("‹")
        prev_btn.setObjectName("CalNavButton")
        prev_btn.setFixedSize(30, 28)
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self.prev_month)

        next_btn = QPushButton("›")
        next_btn.setObjectName("CalNavButton")
        next_btn.setFixedSize(30, 28)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self.next_month)

        self.month_label = QLabel("")
        self.month_label.setObjectName("CalendarMonthLabel")

        today_btn = QPushButton("Hoy")
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self.go_today)

        header.addWidget(prev_btn)
        header.addWidget(next_btn)
        header.addSpacing(8)
        header.addWidget(self.month_label)
        header.addStretch()

        settings_btn = QPushButton("⚙  Ajustes")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setToolTip("Sincronizar / exportar a Google, Apple u Outlook")
        settings_btn.clicked.connect(self.open_settings)

        close_btn = QPushButton("✖  Cerrar")
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip("Volver a la vista de tablero")
        close_btn.clicked.connect(self.close_requested.emit)

        header.addWidget(today_btn)
        header.addWidget(settings_btn)
        header.addWidget(close_btn)
        root.addLayout(header)

        # --- Rejilla: fila 0 = cabecera de días de la semana; filas 1-6 = semanas ---
        grid = QGridLayout()
        grid.setSpacing(6)
        for col, name in enumerate(_WEEKDAYS):
            lbl = QLabel(name)
            lbl.setObjectName("WeekdayHeader")
            lbl.setAlignment(Qt.AlignCenter)
            grid.addWidget(lbl, 0, col)

        self.cells = []
        for week in range(6):
            for dow in range(7):
                cell = DayCell()
                cell.task_clicked.connect(self.task_activated.emit)
                grid.addWidget(cell, week + 1, dow)
                self.cells.append(cell)

        for col in range(7):
            grid.setColumnStretch(col, 1)
        for row in range(1, 7):
            grid.setRowStretch(row, 1)

        root.addLayout(grid, 1)

    def refresh(self):
        """Vuelve a pintar el mes actual con sus tareas."""
        self.month_label.setText(f"{_MONTHS[self.month - 1]} {self.year}")

        first_weekday, num_days = _cal.monthrange(self.year, self.month)  # first_weekday: 0=lunes
        start = date(self.year, self.month, 1)
        end = date(self.year, self.month, num_days)
        tasks = database.get_scheduled_tasks(start.isoformat(), end.isoformat(), db_path=self.db_path)

        by_day = {}
        for t in tasks:
            by_day.setdefault(t["due_date"], []).append(t)

        today = date.today()
        for idx, cell in enumerate(self.cells):
            day_number = idx - first_weekday + 1
            if 1 <= day_number <= num_days:
                cell_date = date(self.year, self.month, day_number)
                cell.set_day(
                    day_number,
                    by_day.get(cell_date.isoformat(), []),
                    is_today=(cell_date == today),
                )
            else:
                cell.set_day(None, [])

    def prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self.refresh()

    def next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self.refresh()

    def go_today(self):
        today = date.today()
        self.year, self.month = today.year, today.month
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
        self.setWindowTitle("Ajustes de Calendario")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        layout.addWidget(QLabel("🔗 <b>Sincronización de calendario</b>"))

        info = QLabel(
            "Ekin exporta tus tareas con fecha de vencimiento a un archivo estándar "
            "<b>iCalendar (.ics)</b>, compatible con Google Calendar, Apple Calendar y Outlook."
        )
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

        sync_title = QLabel("🔄 <b>Sincronización automática</b> (recomendado)")
        sync_layout.addWidget(sync_title)

        sync_desc = QLabel(
            "Ekin mantiene un archivo .ics <b>siempre al día</b> (lo reescribe al cambiar "
            "tareas). Guárdalo en una carpeta de Dropbox / OneDrive / Google Drive y "
            "<b>suscríbete</b> a él una sola vez: a partir de ahí se actualiza solo."
        )
        sync_desc.setWordWrap(True)
        sync_desc.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        sync_layout.addWidget(sync_desc)

        self.sync_path_label = QLabel("")
        self.sync_path_label.setWordWrap(True)
        self.sync_path_label.setStyleSheet("font-size: 11px;")
        sync_layout.addWidget(self.sync_path_label)

        sync_btns = QHBoxLayout()
        self.configure_btn = QPushButton("📂  Elegir archivo…")
        self.configure_btn.setObjectName("PrimaryButton")
        self.configure_btn.setCursor(Qt.PointingHandCursor)
        self.configure_btn.clicked.connect(self.configure_sync)
        sync_btns.addWidget(self.configure_btn)
        self.disable_btn = QPushButton("Desactivar")
        self.disable_btn.setCursor(Qt.PointingHandCursor)
        self.disable_btn.clicked.connect(self.disable_sync)
        sync_btns.addWidget(self.disable_btn)
        sync_btns.addStretch()
        sync_layout.addLayout(sync_btns)

        layout.addWidget(sync_frame)

        steps = QLabel(
            "<b>Suscribirse</b> (se mantiene sincronizado):"
            "<ul>"
            "<li><b>Google</b>: Otros calendarios → Desde una URL (necesita enlace público del archivo).</li>"
            "<li><b>Apple/iOS</b>: Archivo → Nueva suscripción de calendario (admite archivo local en Mac).</li>"
            "<li><b>Outlook</b>: Agregar calendario → Suscribirse desde la web.</li>"
            "</ul>"
            "<b>Importar</b> una copia puntual es una foto fija: no refleja cambios ni borrados."
        )
        steps.setTextFormat(Qt.RichText)
        steps.setWordWrap(True)
        steps.setStyleSheet("font-size: 12px;")
        layout.addWidget(steps)

        layout.addStretch()

        btns = QHBoxLayout()
        export_btn = QPushButton("⬇  Exportar copia…")
        export_btn.setCursor(Qt.PointingHandCursor)
        export_btn.setToolTip("Guardar una copia .ics puntual (snapshot) en otra ubicación")
        export_btn.clicked.connect(self.export_once)
        btns.addWidget(export_btn)
        btns.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        self._refresh_sync_label()

    def _refresh_sync_label(self):
        path = database.get_setting("ics_sync_path", "", self.db_path)
        if path:
            self.sync_path_label.setText(f"✅ Sincronizando en:<br><code>{path}</code>")
            self.sync_path_label.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['success']};")
            self.disable_btn.setEnabled(True)
            self.configure_btn.setText("📂  Cambiar archivo…")
        else:
            self.sync_path_label.setText("⚪ Sincronización automática desactivada.")
            self.sync_path_label.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['text_muted']};")
            self.disable_btn.setEnabled(False)
            self.configure_btn.setText("📂  Elegir archivo…")

    def configure_sync(self):
        current = database.get_setting("ics_sync_path", "", self.db_path)
        default = current or "ekin_calendario.ics"
        path, _ = QFileDialog.getSaveFileName(
            self, "Archivo de sincronización", default, "iCalendar (*.ics)"
        )
        if not path:
            return
        try:
            count = ics_export.export_ics(path, self.db_path)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo crear el archivo:\n{exc}")
            return
        database.set_setting("ics_sync_path", path, self.db_path)
        self._refresh_sync_label()
        QMessageBox.information(
            self, "Sincronización activada",
            f"Ekin mantendrá {count} tarea(s) sincronizadas en:\n{path}\n\n"
            "Suscríbete a este archivo una vez desde tu calendario y se actualizará solo."
        )

    def disable_sync(self):
        database.set_setting("ics_sync_path", "", self.db_path)
        self._refresh_sync_label()

    def export_once(self):
        default_name = f"ekin_calendario_{date.today().isoformat()}.ics"
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar copia del calendario", default_name, "iCalendar (*.ics)"
        )
        if not path:
            return
        try:
            count = ics_export.export_ics(path, self.db_path)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo exportar el calendario:\n{exc}")
            return
        QMessageBox.information(
            self, "Exportado",
            f"Se exportaron {count} tarea(s) con fecha a:\n{path}\n\n"
            "Recuerda: una copia importada es una foto fija; para que se mantenga al día, "
            "usa la sincronización automática de arriba y suscríbete al archivo."
        )
