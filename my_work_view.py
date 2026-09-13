"""Vista "Mi trabajo": panel transversal (todos los tableros) con lo que vence pronto
y las tareas con el temporizador en marcha.

Reutiliza database.get_scheduled_tasks (que ya abarca todos los tableros) y
database.get_active_timer_tasks, más el mismo patrón de agrupación de la campana. Al
pulsar una tarea emite `task_activated(task_id, board_id)`; el botón Cerrar emite
`close_requested` (MainWindow vuelve a la vista de tablero)."""

from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PySide6.QtGui import QColor, QPixmap, QIcon

import database
import styles
from strings import t

# Ventana de "próximo" tras mañana, en días (para el grupo "Esta semana").
UPCOMING_DAYS = 7


def bucket_scheduled_tasks(tasks, today_iso):
    """Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.

    Lógica pura (sin Qt) para poder probarla sin bucle de eventos. `tasks` es una lista
    de dicts con clave 'due_date' ('YYYY-MM-DD'); `today_iso` es hoy en el mismo formato.
    Devuelve un dict con las cuatro listas, cada una preservando el orden de entrada."""
    tomorrow_iso = (date.fromisoformat(today_iso) + timedelta(days=1)).isoformat()
    buckets = {"overdue": [], "today": [], "tomorrow": [], "upcoming": []}
    for task in tasks:
        due = task.get("due_date")
        if not due:
            continue
        if due < today_iso:
            buckets["overdue"].append(task)
        elif due == today_iso:
            buckets["today"].append(task)
        elif due == tomorrow_iso:
            buckets["tomorrow"].append(task)
        else:
            buckets["upcoming"].append(task)
    return buckets


def _swatch_icon(color, size=12):
    """Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)."""
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class MyWorkWidget(QWidget):
    """Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador en
    marcha y las que vencen (atrasadas / hoy / mañana / esta semana)."""
    task_activated = Signal(int, int)  # task_id, board_id
    close_requested = Signal()

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setObjectName("MyWorkView")
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel(t("mywork.title"))
        title.setObjectName("MyWorkTitle")
        header.addWidget(title)
        header.addStretch()

        close_btn = QPushButton(t("mywork.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close_requested.emit)
        header.addWidget(close_btn)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._vbox = QVBoxLayout(self._content)
        self._vbox.setContentsMargins(2, 2, 2, 2)
        self._vbox.setSpacing(4)
        self._vbox.setAlignment(Qt.AlignTop)
        scroll.setWidget(self._content)
        root.addWidget(scroll)

    def refresh(self):
        """Recarga los grupos desde la base de datos (todos los tableros)."""
        while self._vbox.count():
            item = self._vbox.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        today_iso = date.today().isoformat()
        week_end = (date.today() + timedelta(days=UPCOMING_DAYS)).isoformat()
        scheduled = database.get_scheduled_tasks(end_date=week_end, db_path=self.db_path)
        buckets = bucket_scheduled_tasks(scheduled, today_iso)
        running = database.get_active_timer_tasks(self.db_path)

        self._add_group(t("mywork.group_in_progress"), running, color=styles.COLORS["accent"])
        self._add_group(t("mywork.group_overdue"), buckets["overdue"], color=styles.COLORS["danger"])
        self._add_group(t("mywork.group_today"), buckets["today"])
        self._add_group(t("mywork.group_tomorrow"), buckets["tomorrow"])
        self._add_group(t("mywork.group_upcoming"), buckets["upcoming"])

        if not (running or scheduled):
            empty = QLabel(t("mywork.empty"))
            empty.setWordWrap(True)
            empty.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; padding: 8px 2px; background: transparent;"
            )
            self._vbox.addWidget(empty)

    def _add_group(self, label, tasks, color=None):
        if not tasks:
            return
        color = color or styles.COLORS["text_muted"]
        group_label = QLabel(label)
        group_label.setStyleSheet(
            f"color: {color}; font-size: 11px; font-weight: bold;"
            " margin-top: 8px; background: transparent;"
        )
        self._vbox.addWidget(group_label)
        for task in tasks:
            btn = QPushButton(task["title"] or t("sidebar.notifications.item_no_title"))
            btn.setObjectName("NotificationItem")
            btn.setIcon(_swatch_icon(task["board_color"]))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(t(
                "sidebar.notifications.item_tooltip",
                board=task["board_name"], due_date=task.get("due_date") or "—",
            ))
            btn.clicked.connect(
                lambda _=False, tid=task["id"], bid=task["board_id"]: self.task_activated.emit(tid, bid)
            )
            self._vbox.addWidget(btn)
