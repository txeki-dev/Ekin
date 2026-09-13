"""Diálogo genérico de asistencia por IA para una tarea concreta.

Muestra un borrador editable (desglose en subtareas o resumen del diario) generado
OFFLINE al instante. Si se le pasa `mode` + `ai_tasks`, ofrece además un botón "Mejorar
con IA local" que reutiliza local_ai.SpecGenerationThread para afinar el borrador con el
modelo local disponible (y recae en el sintetizador estructural si no lo hay). Al
confirmar emite `confirmed(text)` con el texto final; el llamante decide qué hacer."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton
)

import local_ai
import styles
from strings import t


class AiAssistDialog(QDialog):
    confirmed = Signal(str)

    def __init__(self, title, initial_text, confirm_label, hint="",
                 mode=None, ai_tasks=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.finished.connect(self._cancel_thread)
        self.setWindowTitle(title)
        self.setMinimumSize(460, 420)
        self._mode = mode
        self._ai_tasks = ai_tasks
        self._offline_text = initial_text
        self._thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        heading = QLabel(title)
        heading.setStyleSheet(
            f"font-family:'Caprasimo','Segoe UI',serif; font-size:20px; color:{styles.COLORS['accent']};"
        )
        layout.addWidget(heading)

        if hint:
            hint_lbl = QLabel(hint)
            hint_lbl.setWordWrap(True)
            hint_lbl.setStyleSheet(f"color:{styles.COLORS['text_muted']}; font-size:12px;")
            layout.addWidget(hint_lbl)

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(initial_text)
        layout.addWidget(self.editor, 1)

        btns = QHBoxLayout()
        # Botón de mejora por IA local: solo si hay contexto de generación (mode + tareas).
        if mode and ai_tasks:
            self.enhance_btn = QPushButton(t("ai.enhance_btn"))
            self.enhance_btn.setCursor(Qt.PointingHandCursor)
            self.enhance_btn.clicked.connect(self._start_enhance)
            btns.addWidget(self.enhance_btn)
        else:
            self.enhance_btn = None
        btns.addStretch()
        cancel_btn = QPushButton(t("board_view.column_edit.cancel"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)
        confirm_btn = QPushButton(confirm_label)
        confirm_btn.setObjectName("PrimaryButton")
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self._confirm)
        btns.addWidget(confirm_btn)
        layout.addLayout(btns)

    # --- Mejora por IA local (streaming) ---
    def _start_enhance(self):
        if self._thread is not None:
            return
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setText(t("ai.enhance_generating"))
        self.editor.clear()
        self._thread = local_ai.SpecGenerationThread(self._ai_tasks, self._mode, parent=self)
        self._thread.token_received.connect(self._on_token)
        self._thread.generation_finished.connect(self._on_finished)
        self._thread.error_occurred.connect(self._on_error)
        self._thread.start()

    def _on_token(self, token):
        self.editor.moveCursor(QTextCursor.End)
        self.editor.insertPlainText(token)

    def _on_finished(self, full_text):
        self.editor.setPlainText(full_text)
        self._reset_enhance()

    def _on_error(self, _message):
        self.editor.setPlainText(self._offline_text)
        self._reset_enhance()

    def _reset_enhance(self):
        self._thread = None
        if self.enhance_btn is not None:
            self.enhance_btn.setEnabled(True)
            self.enhance_btn.setText(t("ai.enhance_btn"))

    def _cancel_thread(self, *args):
        if self._thread is not None:
            try:
                self._thread.cancel()
                if self._thread.isRunning():
                    self._thread.wait(500)
            except Exception:
                pass
            self._thread = None

    def _confirm(self):
        self.confirmed.emit(self.editor.toPlainText())
        self.accept()
