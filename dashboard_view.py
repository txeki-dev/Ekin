"""Panel de Analíticas: métricas transversales (todos los tableros) con tarjetas de
resumen y gráficas de barras pintadas a mano (sin dependencias nuevas), más exportación
a PDF. Los datos vienen de analytics.gather_stats (solo datos que la app ya almacena)."""
from datetime import date

from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame,
    QFileDialog, QMessageBox
)

import analytics
import styles
from strings import t


class BarChartWidget(QWidget):
    """Gráfica de barras horizontales pintada a mano: filas (etiqueta, valor, color)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []
        self.setMinimumHeight(40)

    def set_data(self, data):
        self._data = list(data)
        self.setMinimumHeight(max(40, 8 + len(self._data) * 32))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self._data:
            p.end()
            return
        max_v = max((v for _, v, _ in self._data), default=0) or 1
        label_w = 140
        avail = max(40, self.width() - label_w - 56)
        row_h, gap, y = 26, 6, 4
        for label, value, color in self._data:
            p.setPen(QColor(styles.COLORS["text_soft"]))
            p.drawText(QRectF(0, y, label_w - 8, row_h), Qt.AlignVCenter | Qt.AlignLeft, label)
            bar_w = int(avail * (value / max_v)) if max_v else 0
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(color))
            p.drawRoundedRect(QRectF(label_w, y + 3, max(2, bar_w), row_h - 6), 5, 5)
            p.setPen(QColor(styles.COLORS["text_muted"]))
            p.drawText(QRectF(label_w + bar_w + 8, y, 48, row_h), Qt.AlignVCenter | Qt.AlignLeft, str(value))
            y += row_h + gap
        p.end()


class DashboardWidget(QWidget):
    """Panel de Analíticas conmutable en el área central. `close_requested` vuelve al tablero."""
    close_requested = Signal()

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setObjectName("DashboardView")
        self._stats = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel(t("dashboard.title"))
        title.setObjectName("DashboardTitle")
        header.addWidget(title)
        header.addStretch()
        self.export_btn = QPushButton(t("dashboard.export_btn"))
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.clicked.connect(self._export_pdf)
        header.addWidget(self.export_btn)
        close_btn = QPushButton(t("dashboard.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close_requested.emit)
        header.addWidget(close_btn)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self._col = QVBoxLayout(content)
        self._col.setContentsMargins(0, 0, 0, 0)
        self._col.setSpacing(16)
        self._col.setAlignment(Qt.AlignTop)

        self._tiles_row = QHBoxLayout()
        self._tiles_row.setSpacing(10)
        self._col.addLayout(self._tiles_row)

        self._col.addWidget(self._section_label(t("dashboard.chart_per_board")))
        self.per_board_chart = BarChartWidget()
        self._col.addWidget(self.per_board_chart)

        self._col.addWidget(self._section_label(t("dashboard.chart_due_status")))
        self.due_chart = BarChartWidget()
        self._col.addWidget(self.due_chart)

        self.empty_label = QLabel(t("dashboard.empty"))
        self.empty_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-style: italic;")
        self.empty_label.hide()
        self._col.addWidget(self.empty_label)

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

    def _section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {styles.COLORS['text_main']}; font-size: 13px; font-weight: bold; background: transparent;"
        )
        return lbl

    def _tile(self, value, label, color):
        frame = QFrame()
        frame.setStyleSheet(
            f"QFrame {{ background-color: {styles.COLORS['bg_hover']}; border-radius: 14px; }}"
        )
        v = QVBoxLayout(frame)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(2)
        num = QLabel(str(value))
        num.setStyleSheet(
            f"font-family:'Caprasimo','Segoe UI',serif; font-size:26px; color:{color}; background: transparent;"
        )
        v.addWidget(num)
        cap = QLabel(label)
        cap.setStyleSheet(f"color:{styles.COLORS['text_muted']}; font-size:11px; background: transparent;")
        v.addWidget(cap)
        return frame

    def refresh(self):
        self._stats = analytics.gather_stats(self.db_path)
        tot = self._stats["totals"]

        while self._tiles_row.count():
            item = self._tiles_row.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        tiles = [
            (tot["boards"], t("dashboard.tile_boards"), styles.COLORS["text_main"]),
            (tot["tasks"], t("dashboard.tile_tasks"), styles.COLORS["accent"]),
            (tot["overdue"], t("dashboard.tile_overdue"), styles.COLORS["danger"]),
            (tot["due_this_week"], t("dashboard.tile_due_week"), styles.COLORS["accent_2"]),
            (tot["running_timers"], t("dashboard.tile_timers"), styles.COLORS["text_soft"]),
        ]
        for value, label, color in tiles:
            self._tiles_row.addWidget(self._tile(value, label, color))
        self._tiles_row.addStretch()

        self.per_board_chart.set_data([
            (b["name"], b["count"], b["color"]) for b in self._stats["per_board"]
        ])
        ds = self._stats["due_status"]
        self.due_chart.set_data([
            (t("dashboard.status_overdue"), ds["overdue"], styles.COLORS["danger"]),
            (t("dashboard.status_this_week"), ds["this_week"], styles.COLORS["accent"]),
            (t("dashboard.status_later"), ds["later"], styles.COLORS["accent_2"]),
            (t("dashboard.status_no_due"), ds["no_due"], styles.COLORS["text_muted"]),
        ])

        self.empty_label.setVisible(tot["tasks"] == 0)

    def _export_pdf(self):
        default_name = f"ekin-analytics-{date.today().isoformat()}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, t("dashboard.export_title"), default_name, "PDF (*.pdf)"
        )
        if not path:
            return
        try:
            analytics.export_report_pdf(self._stats, path)
        except Exception as exc:
            QMessageBox.warning(self, t("dashboard.title"), str(exc))
            return
        QMessageBox.information(self, t("dashboard.title"), t("dashboard.export_done", path=path))
