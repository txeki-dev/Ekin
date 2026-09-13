"""Recordatorios anticipados y resumen semanal (weekly review).

La decisión de mostrar el resumen y el reparto de tareas son lógica pura (sin Qt) para
poder probarlas sin bucle de eventos; WeeklyDigestDialog solo las pinta."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QWidget
)
from PySide6.QtGui import QColor, QPixmap, QIcon

import styles
from strings import t

# Ventana del resumen semanal: hoy .. hoy + THIS_WEEK_DAYS (inclusive).
THIS_WEEK_DAYS = 6


def current_week_key(d):
    """Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas."""
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def should_show_weekly_digest(last_shown_key, today, enabled):
    """True si el resumen está activado y aún no se ha mostrado esta semana ISO."""
    if not enabled:
        return False
    return current_week_key(today) != last_shown_key


def split_digest_tasks(tasks, today_iso):
    """Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en
    adelante). Lógica pura; preserva el orden de entrada."""
    overdue, this_week = [], []
    for task in tasks:
        due = task.get("due_date")
        if not due:
            continue
        (overdue if due < today_iso else this_week).append(task)
    return {"overdue": overdue, "this_week": this_week}


def _swatch_icon(color, size=12):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class WeeklyDigestDialog(QDialog):
    """Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una
    tarea emite `task_activated(task_id, board_id)`; 'Abrir Mi trabajo' emite
    `open_my_work_requested`."""
    task_activated = Signal(int, int)
    open_my_work_requested = Signal()

    def __init__(self, overdue, this_week, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.setWindowTitle(t("digest.window_title"))
        self.setMinimumWidth(440)
        self.resize(440, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title = QLabel(t("digest.header"))
        title.setStyleSheet(
            f"font-family:'Caprasimo','Segoe UI',serif; font-size:22px; color:{styles.COLORS['accent']};"
        )
        layout.addWidget(title)

        summary = QLabel(t("digest.summary", overdue=len(overdue), week=len(this_week)))
        summary.setStyleSheet(f"color:{styles.COLORS['text_muted']}; font-size:12px;")
        layout.addWidget(summary)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignTop)
        self._add_group(vbox, t("digest.group_overdue"), overdue, styles.COLORS["danger"])
        self._add_group(vbox, t("digest.group_this_week"), this_week, None)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        btns = QHBoxLayout()
        mywork_btn = QPushButton(t("digest.open_my_work_btn"))
        mywork_btn.setCursor(Qt.PointingHandCursor)
        mywork_btn.clicked.connect(self._go_my_work)
        btns.addWidget(mywork_btn)
        btns.addStretch()
        close_btn = QPushButton(t("digest.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _go_my_work(self):
        self.open_my_work_requested.emit()
        self.accept()

    def _add_group(self, vbox, label, tasks, color):
        if not tasks:
            return
        color = color or styles.COLORS["text_muted"]
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color:{color}; font-size:11px; font-weight:bold; margin-top:6px; background:transparent;"
        )
        vbox.addWidget(lbl)
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
                lambda _=False, tid=task["id"], bid=task["board_id"]: self._activate(tid, bid)
            )
            vbox.addWidget(btn)

    def _activate(self, task_id, board_id):
        self.task_activated.emit(task_id, board_id)
        self.accept()
