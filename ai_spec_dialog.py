"""
Diálogo de interfaz gráfica para la generación de especificaciones (SPEC)
para agentes de IA a partir de múltiples tarjetas seleccionadas.
"""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QPlainTextEdit, QLineEdit, QMessageBox, QFileDialog,
    QApplication, QFrame
)
from PySide6.QtGui import QFont
import styles
import database
from strings import t
import local_ai


class AiSpecDialog(QDialog):
    """Diálogo modal interactivo para generar especificaciones técnicas con IA local."""

    def __init__(self, task_ids: list[int], board_id: int, db_path: str, parent=None):
        super().__init__(parent)
        self.task_ids = task_ids
        self.board_id = board_id
        self.db_path = db_path
        self.tasks_data = self._load_tasks_data()
        self._gen_thread = None

        self.setWindowTitle(t("ai_spec.dialog_title"))
        self.resize(1080, 680)
        self.setMinimumWidth(980)
        self.init_ui()

    def _load_tasks_data(self) -> list[dict]:
        """Carga la metadata completa de las tareas seleccionadas (incluyendo logs y tags)."""
        loaded = []
        for tid in self.task_ids:
            t_data = database.get_task(tid, self.db_path)
            if t_data:
                t_data["tags"] = database.get_task_tags(tid, self.db_path)
                t_data["logs"] = database.get_logs(tid, self.db_path)
                col = database.get_column(t_data["column_id"], self.db_path)
                t_data["column_name"] = col["name"] if col else "Backlog"
                loaded.append(t_data)
        return loaded

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Cabecera con resumen de tareas seleccionadas
        header_layout = QVBoxLayout()
        header_layout.setSpacing(6)

        title_lbl = QLabel(f"🤖 <b>{t('ai_spec.dialog_title')}</b>")
        title_lbl.setStyleSheet(f"font-size: 16px; color: {styles.COLORS['text_main']};")
        header_layout.addWidget(title_lbl)

        tasks_summary = ", ".join(f"«{t['title']}»" for t in self.tasks_data[:4])
        if len(self.tasks_data) > 4:
            tasks_summary += f" y {len(self.tasks_data) - 4} más"

        desc_lbl = QLabel(f"Tareas seleccionadas ({len(self.tasks_data)}): {tasks_summary}")
        desc_lbl.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        header_layout.addWidget(desc_lbl)

        layout.addLayout(header_layout)

        # 2. Barra de configuración de la SPEC
        config_frame = QFrame()
        config_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        cfg_layout = QVBoxLayout(config_frame)
        cfg_layout.setSpacing(10)

        # Fila 1: Modo de Especificación y Estado del Motor de IA
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.mode_label = QLabel(f"<b>{t('ai_spec.mode_label')}</b>")
        self.mode_label.setWordWrap(False)
        row1.addWidget(self.mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem(t("ai_spec.mode_coding_agent"), "coding_agent")
        self.mode_combo.addItem(t("ai_spec.mode_user_stories"), "user_stories")
        self.mode_combo.addItem(t("ai_spec.mode_qa_plan"), "qa_tests")
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 6px 28px 6px 12px;
                color: {styles.COLORS['text_main']};
                font-size: 12px;
            }}
            QComboBox:focus {{
                border-color: {styles.COLORS['accent_blue']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {styles.COLORS['border']};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: {styles.COLORS['bg_card']};
            }}
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {styles.COLORS['text_muted']};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                selection-background-color: {styles.COLORS['accent_blue']};
                color: {styles.COLORS['text_main']};
                padding: 4px;
            }}
        """)
        row1.addWidget(self.mode_combo, stretch=1)

        # Indicador de estado del motor de IA
        self.engine_status_lbl = QLabel()
        self.engine_status_lbl.setWordWrap(False)
        row1.addWidget(self.engine_status_lbl)

        cfg_layout.addLayout(row1)

        # Fila 2: Selector de Modelo de Ollama, Instrucciones adicionales y Botón Generar
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self.model_label = QLabel(f"<b>{t('ai_spec.model_label')}</b>")
        self.model_label.setWordWrap(False)
        row2.addWidget(self.model_label)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setInsertPolicy(QComboBox.NoInsert)
        self.model_combo.setMinimumWidth(250)
        self.model_combo.setMaximumWidth(290)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 5px 28px 5px 10px;
                color: {styles.COLORS['text_main']};
                font-size: 12px;
            }}
            QComboBox:focus {{
                border-color: {styles.COLORS['accent_blue']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {styles.COLORS['border']};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: {styles.COLORS['bg_card']};
            }}
            QComboBox::down-arrow {{
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {styles.COLORS['text_muted']};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                selection-background-color: {styles.COLORS['accent_blue']};
                color: {styles.COLORS['text_main']};
                padding: 4px;
            }}
        """)
        if self.model_combo.lineEdit():
            self.model_combo.lineEdit().setPlaceholderText("Ej. qwen2.5-coder:1.5b")
            self.model_combo.lineEdit().setStyleSheet(f"""
                QLineEdit {{
                    background: transparent;
                    color: {styles.COLORS['text_main']};
                    border: none;
                    font-size: 12px;
                    padding: 0px 4px 0px 0px;
                }}
            """)
            self.model_combo.lineEdit().setCursorPosition(0)
        self.model_combo.currentIndexChanged.connect(self._reset_model_cursor_pos)
        self.model_combo.currentTextChanged.connect(self._reset_model_cursor_pos)
        row2.addWidget(self.model_combo)

        # Botón para refrescar modelos de Ollama activos
        self.refresh_models_btn = QPushButton("🔄")
        self.refresh_models_btn.setFixedSize(28, 28)
        self.refresh_models_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_models_btn.setToolTip(t("ai_spec.refresh_models_tooltip"))
        self.refresh_models_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                color: {styles.COLORS['text_main']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_card']};
                border-color: {styles.COLORS['accent_blue']};
            }}
        """)
        self.refresh_models_btn.clicked.connect(lambda: self._refresh_engine_status(manual=True))
        row2.addWidget(self.refresh_models_btn)

        # Instrucciones adicionales opcionales
        self.custom_prompt_input = QLineEdit()
        self.custom_prompt_input.setPlaceholderText("Instrucciones adicionales (opcional)…")
        self.custom_prompt_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {styles.COLORS['text_main']};
                font-size: 12px;
            }}
        """)
        row2.addWidget(self.custom_prompt_input, stretch=1)

        self.generate_btn = QPushButton(t("ai_spec.generate_btn"))
        self.generate_btn.setObjectName("PrimaryButton")
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self.start_generation)
        row2.addWidget(self.generate_btn)

        cfg_layout.addLayout(row2)
        layout.addWidget(config_frame)
        self._refresh_engine_status()

        # 3. Editor de salida / previsualización en Markdown
        self.spec_edit = QPlainTextEdit()
        font = QFont("Consolas" if sys.platform == "win32" else "Monospace", 10)
        font.setStyleHint(QFont.Monospace)
        self.spec_edit.setFont(font)
        self.spec_edit.setPlaceholderText("Pulsa «⚡ Generar SPEC» para crear la especificación técnica con IA…")
        self.spec_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
                line-height: 140%;
            }}
        """)
        layout.addWidget(self.spec_edit, stretch=1)

        # 4. Fila de botones de acción inferiores
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.copy_btn = QPushButton(t("ai_spec.copy_btn"))
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_row.addWidget(self.copy_btn)

        self.save_btn = QPushButton(t("ai_spec.save_btn"))
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_to_file)
        btn_row.addWidget(self.save_btn)

        self.create_task_btn = QPushButton(t("ai_spec.create_task_btn"))
        self.create_task_btn.setCursor(Qt.PointingHandCursor)
        self.create_task_btn.clicked.connect(self.create_as_task)
        btn_row.addWidget(self.create_task_btn)

        btn_row.addStretch()

        self.close_btn = QPushButton("Cerrar")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.close_btn)

        layout.addLayout(btn_row)

    def _refresh_engine_status(self, manual: bool = False):
        """Muestra qué motor de IA atenderá la generación y puebla el selector de modelos de Ollama."""
        detect = local_ai.detect_available_llm()
        name = detect["name"]
        ollama_models = local_ai.get_ollama_models()

        current_choice = self.model_combo.currentText().strip()

        self.model_combo.blockSignals(True)
        self.model_combo.clear()

        if ollama_models:
            for m in ollama_models:
                self.model_combo.addItem(m)
            self.engine_status_lbl.setText(f"🟢 Ollama ({len(ollama_models)} mod.)")
            self.engine_status_lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px;")
            self.engine_status_lbl.setToolTip("Conectado a Ollama local (localhost:11434)")
        else:
            for m in local_ai.DEFAULT_OLLAMA_MODELS:
                self.model_combo.addItem(m)

            if detect["type"] == "managed" and detect["status"] == "ready":
                self.engine_status_lbl.setText(f"🟢 {name}")
                self.engine_status_lbl.setStyleSheet("color: #10b981; font-weight: bold; font-size: 11px;")
                self.engine_status_lbl.setToolTip(f"Conectado a {name}")
            elif detect["status"] == "can_start":
                self.engine_status_lbl.setText("🟡 Runner local listo")
                self.engine_status_lbl.setStyleSheet("color: #f59e0b; font-weight: bold; font-size: 11px;")
                self.engine_status_lbl.setToolTip("El runner local se iniciará al generar la SPEC")
            else:
                if manual:
                    self.engine_status_lbl.setText("⚡ Modo Estructural (Ollama desconectado)")
                else:
                    self.engine_status_lbl.setText("⚡ Modo Estructural (Sin descarga)")
                self.engine_status_lbl.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
                self.engine_status_lbl.setToolTip("Ollama no está en ejecución en localhost:11434. Inicia Ollama y pulsa 🔄 para conectarlo.")

        # Restaurar texto previo si existía, o preseleccionar el mejor modelo de código
        if current_choice:
            idx = self.model_combo.findText(current_choice)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
            else:
                self.model_combo.setEditText(current_choice)
        else:
            all_items = [self.model_combo.itemText(i) for i in range(self.model_combo.count())]
            best_idx = next((i for i, m in enumerate(all_items) if any(k in m.lower() for k in ("coder", "qwen", "deepseek", "code"))), 0)
            self.model_combo.setCurrentIndex(best_idx)

        self.model_combo.blockSignals(False)
        self._reset_model_cursor_pos()

    def _reset_model_cursor_pos(self, *args):
        if hasattr(self, "model_combo") and self.model_combo.lineEdit():
            self.model_combo.lineEdit().setCursorPosition(0)

    def start_generation(self):
        """Inicia el proceso de generación de SPEC en segundo plano con streaming."""
        if not self.tasks_data:
            return

        mode = self.mode_combo.currentData()
        custom = self.custom_prompt_input.text().strip()
        selected_model = self.model_combo.currentText().strip() or None

        self.spec_edit.clear()
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText(t("ai_spec.status_generating"))

        self._gen_thread = local_ai.SpecGenerationThread(
            self.tasks_data, mode, custom, model_name=selected_model, parent=self
        )
        self._gen_thread.token_received.connect(self._on_token)
        self._gen_thread.generation_finished.connect(self._on_finished)
        self._gen_thread.error_occurred.connect(self._on_error)
        self._gen_thread.start()

    def _on_token(self, token: str):
        self.spec_edit.insertPlainText(token)
        # Auto-scroll hacia el final mientras fluyen los tokens
        sb = self.spec_edit.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_finished(self, full_text: str):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText(t("ai_spec.generate_btn"))
        self._refresh_engine_status()

    def _on_error(self, err_msg: str):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText(t("ai_spec.generate_btn"))
        self.engine_status_lbl.setText(f"❌ Error: {err_msg[:45]}")
        self.engine_status_lbl.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px;")
        self.engine_status_lbl.setToolTip(err_msg)
        if not self.spec_edit.toPlainText().strip():
            self.spec_edit.setPlainText(
                f"> ❌ {err_msg}\n\n"
                f"Comprueba que el modelo esté descargado en Ollama o usa el motor estructural local."
            )

    def reject(self):
        if hasattr(self, "_gen_thread") and self._gen_thread and self._gen_thread.isRunning():
            self._gen_thread.cancel()
            self._gen_thread.wait(400)
        super().reject()

    def closeEvent(self, event):
        if hasattr(self, "_gen_thread") and self._gen_thread and self._gen_thread.isRunning():
            self._gen_thread.cancel()
            self._gen_thread.wait(400)
        super().closeEvent(event)

    def copy_to_clipboard(self):
        """Copia la SPEC generada al portapapeles del sistema."""
        text = self.spec_edit.toPlainText()
        if not text.strip():
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copiado", t("ai_spec.copied_toast"))

    def save_to_file(self):
        """Guarda la especificación en un archivo Markdown."""
        text = self.spec_edit.toPlainText()
        if not text.strip():
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Especificación de IA",
            "SPEC.md",
            "Markdown (*.md);;Texto (*.txt);;Todos los archivos (*.*)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "Guardado", t("ai_spec.saved_toast"))
            except Exception as e:
                QMessageBox.warning(self, "Error al guardar", f"No se pudo guardar el archivo:\n{e}")

    def create_as_task(self):
        """Crea una nueva tarjeta en la primera columna del tablero actual con la SPEC."""
        text = self.spec_edit.toPlainText()
        if not text.strip():
            return

        # Obtener columnas del tablero actual
        cols = database.get_columns(self.board_id, self.db_path)
        if not cols:
            return

        col_id = cols[0]["id"]
        # Extraer primer título de la SPEC
        first_line = text.strip().split("\n")[0].replace("#", "").strip()
        task_title = first_line if first_line else "SPEC: Iniciativa de IA"

        database.create_task(
            column_id=col_id,
            title=task_title,
            description=f"Especificación técnica generada a partir de {len(self.tasks_data)} tareas:\n\n{text}",
            tag_text="AI:SPEC",
            tag_color="#8b5cf6",
            db_path=self.db_path
        )

        QMessageBox.information(self, "Tarea Creada", t("ai_spec.task_created_toast"))
        self.accept()
