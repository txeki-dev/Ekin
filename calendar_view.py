"""Vista de calendario mensual para Ekin: muestra las tareas por su fecha de vencimiento
y permite exportar a iCalendar (.ics) desde su diálogo de Ajustes."""
import calendar as _cal
from datetime import date

from PySide6.QtCore import Qt, Signal, QMimeData, QPoint, QUrl
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QDialog, QFileDialog, QMessageBox, QSizePolicy, QApplication, QLineEdit,
    QScrollArea
)
from PySide6.QtGui import QColor, QPixmap, QIcon, QDrag, QDesktopServices

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

    def set_day(self, day_number, tasks, is_today=False, cell_date=None):
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

        max_show = 3
        for t in tasks[:max_show]:
            title = t["title"] or "(sin título)"
            label = title if len(title) <= 20 else title[:19] + "…"
            chip = CalendarChip(t["id"], label)
            chip.setObjectName("CalendarChip")
            chip.setIcon(_swatch_icon(t["board_color"]))
            chip.setCursor(Qt.PointingHandCursor)
            chip.setToolTip(f"{t['board_name']} · {title}\nArrastra a otro día para reprogramar")
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


class CalendarViewWidget(QWidget):
    """Vista mensual completa. Sustituye a la vista de tablero cuando está activa."""
    close_requested = Signal()
    task_activated = Signal(int, int)  # task_id, board_id
    data_changed = Signal()            # tras reprogramar una tarea (refresca campana/.ics)

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
                cell.task_rescheduled.connect(self._on_task_rescheduled)
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
                    cell_date=cell_date,
                )
            else:
                cell.set_day(None, [])

    def _on_task_rescheduled(self, task_id, iso_date):
        """Cambia la fecha de vencimiento de una tarea arrastrada a otro día."""
        database.update_task_due_date(task_id, iso_date, self.db_path)
        self.refresh()
        # Avisar a la app para refrescar la campana y reescribir el .ics sincronizado.
        self.data_changed.emit()

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

        subscribe_title = QLabel("🌐 <b>Suscribirse en tu calendario</b>")
        subscribe_layout.addWidget(subscribe_title)

        subscribe_desc = QLabel(
            "Sube el archivo .ics a una carpeta pública (Google Drive / Dropbox / OneDrive) "
            "y pega aquí su <b>URL pública</b>. Ekin la guarda y, según el botón, la copia al "
            "portapapeles y abre la página del proveedor para <b>añadir un calendario por URL</b> "
            "(el paso manual que suele fallar). Guía detallada abajo."
        )
        subscribe_desc.setWordWrap(True)
        subscribe_desc.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        subscribe_layout.addWidget(subscribe_desc)

        self.public_url_input = QLineEdit(database.get_setting("ics_public_url", "", self.db_path))
        self.public_url_input.setPlaceholderText("https://…/ekin_calendario.ics")
        subscribe_layout.addWidget(self.public_url_input)

        provider_btns = QHBoxLayout()
        provider_btns.setSpacing(6)
        self.subscribe_btn = QPushButton("Google")
        self.subscribe_btn.setObjectName("PrimaryButton")
        self.subscribe_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_btn.setToolTip("Copiar la URL y abrir «Añadir por URL» de Google Calendar")
        self.subscribe_btn.clicked.connect(self.subscribe_google)
        provider_btns.addWidget(self.subscribe_btn)

        self.subscribe_outlook_btn = QPushButton("Outlook")
        self.subscribe_outlook_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_outlook_btn.setToolTip("Copiar la URL y abrir «Suscribirse desde la web» de Outlook")
        self.subscribe_outlook_btn.clicked.connect(self.subscribe_outlook)
        provider_btns.addWidget(self.subscribe_outlook_btn)

        self.subscribe_apple_btn = QPushButton("Apple / iCloud")
        self.subscribe_apple_btn.setCursor(Qt.PointingHandCursor)
        self.subscribe_apple_btn.setToolTip("Copiar la URL como enlace webcal:// para iPhone/Mac")
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

    def _subscribe_url(self):
        """Valida y persiste la URL pública. Devuelve la URL, o None si está vacía."""
        url = self.public_url_input.text().strip()
        if not url:
            QMessageBox.warning(
                self, "URL vacía",
                "Pega primero la URL pública de tu archivo .ics (el enlace compartido de la carpeta "
                "en la nube donde lo sincronizas)."
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
            self, "Google Calendar",
            "He copiado la URL al portapapeles y abierto Google Calendar (en el ordenador; "
            "la app de móvil no permite añadir por URL).\n\n"
            "1. Menú lateral izquierdo → «Otros calendarios» → «+» → «Desde una URL».\n"
            "2. Pega la URL (Ctrl+V) y pulsa «Añadir calendario».\n\n"
            "Nota: Google recarga los calendarios por URL de forma lenta (cada varias horas, "
            "hasta ~24 h) y no se puede forzar."
        )

    def subscribe_outlook(self):
        """Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com."""
        url = self._subscribe_url()
        if not url:
            return
        QApplication.clipboard().setText(url)
        QDesktopServices.openUrl(QUrl("https://outlook.live.com/calendar/0/addcalendar"))
        QMessageBox.information(
            self, "Outlook Calendar",
            "He copiado la URL al portapapeles y abierto Outlook en el navegador.\n\n"
            "1. En Outlook.com: «Agregar calendario» → «Suscribirse desde la web».\n"
            "   (En Outlook de trabajo/Microsoft 365 la ruta es outlook.office.com → misma opción.)\n"
            "2. Pega la URL (Ctrl+V), ponle un nombre y color, y pulsa «Importar»/«Suscribirse».\n\n"
            "El Outlook de escritorio (clásico) también admite: Inicio → «Abrir calendario» → "
            "«De Internet…» y pegar la URL."
        )

    def subscribe_apple(self):
        """Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud)."""
        url = self._subscribe_url()
        if not url:
            return
        webcal = url.replace("https://", "webcal://").replace("http://", "webcal://")
        QApplication.clipboard().setText(webcal)
        QMessageBox.information(
            self, "Apple / iCloud",
            "He copiado la URL como enlace <b>webcal://</b> al portapapeles (así iOS/macOS la "
            "reconocen como suscripción). Pégala aquí:\n\n"
            "• iPhone/iPad: Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → "
            "«Añadir calendario suscrito» → pega el enlace → Siguiente.\n"
            "• Mac (app Calendario): Archivo → «Nueva suscripción de calendario…» → pega el enlace → "
            "Suscribirse; ahí puedes fijar la frecuencia de actualización (incluso cada pocos minutos).\n\n"
            "La suscripción se guarda en iCloud y se ve en todos tus dispositivos Apple."
        )

    @staticmethod
    def _provider_guide_html():
        """Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes)."""
        return (
            "<b>📋 Cómo suscribirte (se mantiene sincronizado, sin duplicados)</b>"
            "<p><b>0) Consigue una URL pública y directa del .ics.</b> Guarda el archivo en una "
            "carpeta de la nube y comparte el enlace <i>directo al archivo</i> (no a una página de "
            "vista previa):"
            "<ul>"
            "<li><b>Google Drive</b>: compartir «Cualquiera con el enlace». El enlace normal apunta a "
            "una vista HTML; usa la forma de descarga directa "
            "<code>https://drive.google.com/uc?export=download&id=ID_DEL_ARCHIVO</code>.</li>"
            "<li><b>Dropbox</b>: copia el enlace y cambia el final <code>?dl=0</code> por "
            "<code>?dl=1</code>.</li>"
            "<li><b>OneDrive</b>: «Compartir» → «Cualquier persona con el vínculo» → copia el enlace.</li>"
            "</ul>"
            "Ábrela en una ventana de incógnito: debes ver texto que empieza por "
            "<code>BEGIN:VCALENDAR</code>. Si ves un login o una vista previa, el enlace no sirve.</p>"
            "<p><b>🟦 Google Calendar</b> (solo en el ordenador): menú lateral → «Otros calendarios» → "
            "«+» → «Desde una URL» → pega la URL → «Añadir calendario». Refresco lento (varias horas).</p>"
            "<p><b>🟧 Outlook</b>: en <i>Outlook.com/365 (web)</i> → «Agregar calendario» → «Suscribirse "
            "desde la web» → pega la URL → nombre/color → «Importar». En <i>Outlook de escritorio</i> → "
            "Inicio → «Abrir calendario» → «De Internet…» → pega la URL.</p>"
            "<p><b>🍎 Apple / iCloud</b> (usa un enlace <code>webcal://</code>): "
            "<i>iPhone/iPad</i> → Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → «Añadir "
            "calendario suscrito» → pega el enlace. <i>Mac</i> → app Calendario → Archivo → «Nueva "
            "suscripción de calendario…» → pega el enlace (puedes elegir cada cuánto se actualiza).</p>"
            "<p><b>⚠️ Suscribir ≠ Importar.</b> «Importar» una copia es una foto fija: no refleja "
            "cambios ni borrados y puede duplicar eventos. Suscríbete a la URL para que se actualice solo.</p>"
        )

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
