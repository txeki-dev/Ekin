"""
Diálogo de Daily Standup & Salud del Tablero (El Guardián Kanban).

Analiza las tareas del tablero en curso, completadas recientemente, estancadas y límites WIP,
generando un informe estructurado en Markdown listo para copiar a Slack/Teams o pulir con IA local.
"""

from typing import Optional
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QTextCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QFrame
)

import local_ai
import styles
from icons import lucide_icon
from strings import t


class DailyStandupDialog(QDialog):
    """Diálogo modal que presenta el resumen Daily Standup y salud de flujo del tablero."""

    def __init__(self, board_id: int, board_name: str, db_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.finished.connect(self._cancel_thread)

        self.board_id = board_id
        self.board_name = board_name
        self.db_path = db_path
        self._thread = None

        self.setWindowTitle(t("daily_standup.window_title"))
        self.setMinimumSize(560, 520)

        # 1. Recopilar datos y generar borrador determinista
        self.standup_data = local_ai.generate_daily_standup_data(board_id, db_path=db_path)
        self._initial_text = local_ai.format_daily_standup_markdown(self.standup_data, board_name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        # Cabecera
        head_layout = QHBoxLayout()
        heading = QLabel(f"📋 Daily Standup — {board_name}")
        heading.setStyleSheet(
            f"font-family:'Caprasimo','Segoe UI',serif; font-size:20px; color:{styles.COLORS['accent']}; font-weight: bold;"
        )
        head_layout.addWidget(heading)
        head_layout.addStretch()
        layout.addLayout(head_layout)

        # Píldoras de salud del tablero (Metrics Bar)
        metrics_bar = QFrame()
        metrics_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 6px;
            }}
        """)
        metrics_l = QHBoxLayout(metrics_bar)
        metrics_l.setContentsMargins(10, 6, 10, 6)
        metrics_l.setSpacing(14)

        in_prog_count = len(self.standup_data.get("in_progress", []))
        stagnant_count = len(self.standup_data.get("stagnant", []))
        done_count = len(self.standup_data.get("completed_recently", []))

        lbl_prog = QLabel(f"🟡 En curso: <b>{in_prog_count}</b>")
        lbl_prog.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px;")
        metrics_l.addWidget(lbl_prog)

        stag_color = "#ef4444" if stagnant_count > 0 else styles.COLORS['text_muted']
        lbl_stag = QLabel(f"⚠️ Estancadas (>3d): <b>{stagnant_count}</b>")
        lbl_stag.setStyleSheet(f"color: {stag_color}; font-size: 12px;")
        metrics_l.addWidget(lbl_stag)

        lbl_done = QLabel(f"🟢 Hechas recientemente: <b>{done_count}</b>")
        lbl_done.setStyleSheet("color: #10b981; font-size: 12px;")
        metrics_l.addWidget(lbl_done)

        metrics_l.addStretch()
        layout.addWidget(metrics_bar)

        # Editor de texto editable con el standup
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(self._initial_text)
        self.editor.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {styles.COLORS['bg_card']};
                color: {styles.COLORS['text_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }}
        """)
        layout.addWidget(self.editor, 1)

        # Botonera inferior
        btns_layout = QHBoxLayout()
        btns_layout.setSpacing(8)

        # Botón IA Local
        self.enhance_btn = QPushButton(t("daily_standup.enhance_btn"))
        self.enhance_btn.setCursor(Qt.PointingHandCursor)
        self.enhance_btn.setIcon(lucide_icon("sparkles", styles.COLORS['accent'], 14))
        self.enhance_btn.clicked.connect(self._start_enhance)
        btns_layout.addWidget(self.enhance_btn)

        btns_layout.addStretch()

        # Botón copiar al portapapeles
        self.copy_btn = QPushButton(t("daily_standup.copy_btn"))
        self.copy_btn.setObjectName("PrimaryButton")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setIcon(lucide_icon("copy", "#ffffff", 14))
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        btns_layout.addWidget(self.copy_btn)

        # Botón cerrar
        self.close_btn = QPushButton(t("daily_standup.close_btn"))
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        btns_layout.addWidget(self.close_btn)

        layout.addLayout(btns_layout)

    def _copy_to_clipboard(self):
        text = self.editor.toPlainText().strip()
        QGuiApplication.clipboard().setText(text)
        orig_text = self.copy_btn.text()
        self.copy_btn.setText(t("daily_standup.copied"))
        QTimer.singleShot(1800, lambda: self.copy_btn.setText(orig_text))

    def _start_enhance(self):
        if self._thread is not None:
            return
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setText(t("ai.enhance_generating"))
        self.editor.clear()

        ai_tasks = [{
            "title": f"Daily Standup {self.board_name}",
            "description": self._initial_text,
            "links": []
        }]

        self._thread = local_ai.SpecGenerationThread(ai_tasks, "daily_standup", parent=self)
        self._thread.token_received.connect(self._on_token)
        self._thread.generation_finished.connect(self._on_finished)
        self._thread.error_occurred.connect(self._on_error)
        self._thread.start()

    def _on_token(self, token: str):
        self.editor.moveCursor(QTextCursor.End)
        self.editor.insertPlainText(token)

    def _on_finished(self, full_text: str):
        self.editor.setPlainText(full_text)
        self._reset_enhance()

    def _on_error(self, _message: str):
        self.editor.setPlainText(self._initial_text)
        self._reset_enhance()

    def _reset_enhance(self):
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText(t("daily_standup.enhance_btn"))
        self._thread = None

    def _cancel_thread(self):
        if self._thread is not None and self._thread.isRunning():
            self._thread.cancel()
            self._thread.wait(500)
            self._thread = None
