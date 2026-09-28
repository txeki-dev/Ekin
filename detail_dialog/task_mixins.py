"""Mixins de funcionalidad modular para TaskDetailDialog (temporizadores, detección de duplicadas)."""
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

import database
import styles
import local_ai
from strings import t


class TaskTimerMixin:
    """Manejo de estado y UI del temporizador de tareas para TaskDetailDialog."""

    def _on_timer_toggle_clicked(self):
        """Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción
        instantánea (como añadir una nota al diario o un enlace): se persiste en el
        momento, no espera a "Guardar Cambios"."""
        self._timer_started_at = datetime.now().isoformat()
        database.set_task_timer_started(self.task_id, self._timer_started_at, self.db_path)
        self.modified = True
        self._refresh_timer_ui()

    def _on_timer_clear_clicked(self):
        """Detiene y borra el temporizador: deja de contar y quita la insignia de la tarjeta."""
        self._timer_started_at = None
        database.set_task_timer_started(self.task_id, None, self.db_path)
        self.modified = True
        self._refresh_timer_ui()

    def _refresh_timer_ui(self):
        """Actualiza el botón y la etiqueta de tiempo transcurrido según self._timer_started_at.
        Se llama al cargar la tarea, tras cada acción, y cada 30s mientras el diálogo está
        abierto (self._timer_refresh_timer) para que el contador avance en vivo."""
        if self._timer_started_at:
            self.timer_toggle_btn.setText(t("task_detail.timer_restart_btn"))
            self.timer_clear_btn.show()
            try:
                started = datetime.fromisoformat(self._timer_started_at)
                elapsed = datetime.now() - started
                self.timer_elapsed_label.setText(
                    t("task_detail.timer_elapsed", elapsed=styles.format_elapsed_time(elapsed.total_seconds()))
                )
            except ValueError:
                self.timer_elapsed_label.setText("")
        else:
            self.timer_toggle_btn.setText(t("task_detail.timer_start_btn"))
            self.timer_clear_btn.hide()
            self.timer_elapsed_label.setText("")


class TaskAiMixin:
    """IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el tablero."""

    def _check_duplicates_action(self):
        """Comprueba si existen tareas similares o duplicadas en este tablero."""
        curr_title = self.title_input.text().strip()
        curr_desc = self.desc_input.toPlainText().strip()
        task = database.get_task(self.task_id, self.db_path)
        if not task:
            return

        col = database.get_column(task["column_id"], self.db_path)
        board_id = col["board_id"] if col else None
        if not board_id:
            return

        duplicates = local_ai.find_duplicate_tasks(
            curr_title,
            curr_desc,
            board_id=board_id,
            threshold=0.65,
            exclude_task_id=self.task_id,
            db_path=self.db_path
        )

        if duplicates:
            items_str = "\n".join(
                f"• #{d['id']} - {d['title']} ({d['column_name']}) — {int(d['similarity'] * 100)}%"
                for d in duplicates[:5]
            )
            QMessageBox.warning(
                self,
                t("task_detail.check_dups_btn"),
                t("task_detail.dups_found", count=len(duplicates), items=items_str)
            )
        else:
            QMessageBox.information(
                self,
                t("task_detail.check_dups_btn"),
                t("task_detail.dups_none")
            )

