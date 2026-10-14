"""
Semáforo de cuota restante de las CLIs de IA (#88): el punto de color de la barra lateral y el
popup con el detalle por CLI instalada.
"""
from datetime import datetime

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QVBoxLayout

import cli_quota
import cli_tools
import styles
from strings import t

_AMBER = "#d4a24c"


def state_color(state):
    return {
        cli_quota.GREEN: styles.COLORS["success"],
        cli_quota.AMBER: _AMBER,
        cli_quota.RED: styles.COLORS["danger"],
    }.get(state, styles.COLORS["text_muted"])


def quota_dot_icon(state, size=17):
    """Icono del semáforo: un punto relleno del color del estado."""
    pm = QPixmap(QSize(size, size))
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(state_color(state)))
    margin = size // 5
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    painter.end()
    return QIcon(pm)


def _reset_text(epoch):
    moment = datetime.fromtimestamp(epoch)
    return moment.strftime("%H:%M") if moment.date() == datetime.now().date() else moment.strftime("%a %d %H:%M")


def quota_lines(snapshot):
    """Líneas legibles de la cuota restante de Claude Code (una por ventana vigente)."""
    lines = []
    for key, label in cli_quota.WINDOWS:
        if snapshot and key in snapshot:
            window = snapshot[key]
            lines.append(t(f"quota.{label}", left=f"{100 - window['used_percentage']:.0f}",
                           reset=_reset_text(window["resets_at"])))
    return lines


def tooltip_text(snapshot):
    lines = quota_lines(snapshot)
    return t("quota.tooltip") + ("\n" + "\n".join(lines) if lines else "")


class QuotaPopup(QDialog):
    """Detalle de la cuota por CLI instalada; permite activar o quitar la lectura de Claude Code."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setObjectName("NotificationsPopup")
        self.setFixedWidth(320)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        title = QLabel(t("quota.title"))
        title.setStyleSheet("font-weight: 700;")
        layout.addWidget(title)

        installed = cli_tools.detect_installed()
        if not installed:
            layout.addWidget(self._muted(t("quota.no_cli")))
        for tool, _ in installed:
            layout.addWidget(QLabel(f"<b>{tool.name}</b>"))
            if tool.id != "claude":
                layout.addWidget(self._muted(t("quota.not_exposed")))
                continue
            if not cli_quota.is_installed():
                layout.addWidget(self._muted(t("quota.enable_hint")))
                self.enable_btn = QPushButton(t("quota.enable_btn"))
                self.enable_btn.clicked.connect(self._enable)
                layout.addWidget(self.enable_btn)
                continue
            snapshot = cli_quota.read_quota()
            if snapshot:
                for line in quota_lines(snapshot):
                    layout.addWidget(QLabel(line))
                captured = datetime.fromtimestamp(snapshot["captured_at"]).strftime("%H:%M")
                layout.addWidget(self._muted(t("quota.captured_at", time=captured)))
            else:
                layout.addWidget(self._muted(t("quota.waiting")))
            self.disable_btn = QPushButton(t("quota.disable_btn"))
            self.disable_btn.clicked.connect(self._disable)
            layout.addWidget(self.disable_btn)

    @staticmethod
    def _muted(text):
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        return label

    def _enable(self):
        confirm = QMessageBox.question(self, t("quota.title"), t("quota.enable_confirm", path=cli_quota.CLAUDE_SETTINGS))
        if confirm != QMessageBox.Yes:
            return
        try:
            cli_quota.install_claude_statusline()
        except (OSError, ValueError, RuntimeError) as exc:
            QMessageBox.warning(self, t("quota.title"), str(exc))
            return
        self.accept()

    def _disable(self):
        cli_quota.uninstall_claude_statusline()
        self.accept()
