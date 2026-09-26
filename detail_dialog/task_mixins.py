"""Mixins de funcionalidad modular para TaskDetailDialog (temporizadores, asistentes IA)."""
from datetime import datetime
from PySide6.QtWidgets import QMessageBox

import database
import styles
import local_ai
from strings import t
from html_utils import clean_html_description
from ai_assist_dialog import AiAssistDialog


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
    """Asistentes de IA local (offline) por tarea para TaskDetailDialog."""

    def _open_breakdown(self):
        """Abre el asistente que desglosa esta tarea en subtareas (tareas hermanas en la
        misma columna). Offline y determinista; el usuario edita antes de crear."""
        task = database.get_task(self.task_id, self.db_path)
        if not task:
            return
        titles = local_ai.suggest_subtasks_offline(task)
        dlg = AiAssistDialog(
            t("ai.breakdown.title"), "\n".join(titles),
            t("ai.breakdown.confirm_btn"), t("ai.breakdown.hint"),
            mode="task_breakdown", ai_tasks=[task], parent=self,
        )
        dlg.confirmed.connect(self._apply_breakdown)
        dlg.exec()

    def _apply_breakdown(self, text):
        task = database.get_task(self.task_id, self.db_path)
        if not task:
            return
        titles = local_ai.parse_subtask_lines(text)
        if not titles:
            return
        for title in titles:
            database.create_task(task["column_id"], title, db_path=self.db_path)
        self.modified = True
        QMessageBox.information(
            self, t("ai.breakdown.title"), t("ai.breakdown.created", count=len(titles))
        )

    def _open_summary(self):
        """Abre el asistente que resume el diario de esta tarea (offline)."""
        logs = database.get_logs(self.task_id, self.db_path)
        task = database.get_task(self.task_id, self.db_path)
        title = task["title"] if task else ""
        # Para la mejora por IA: una tarea sintética cuyo "description" lleva el texto del
        # diario, de modo que el prompt de resumen lo reciba sin tocar el generador.
        diary_text = "\n".join(
            clean_html_description(log.get("content", "") or "") for log in logs
        )
        ai_tasks = [{"title": title, "description": diary_text, "links": []}]
        dlg = AiAssistDialog(
            t("ai.summary.title"), local_ai.summarize_diary_offline(logs, title),
            t("ai.summary.confirm_btn"), t("ai.summary.hint"),
            mode="diary_summary", ai_tasks=ai_tasks, parent=self,
        )
        dlg.confirmed.connect(self._apply_summary)
        dlg.exec()

    def _apply_summary(self, text):
        text = (text or "").strip()
        if not text:
            return

        def _esc(s):
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        html_body = "".join(f"<p>{_esc(line)}</p>" for line in text.split("\n") if line.strip())
        database.create_log(self.task_id, html_body, self.db_path)
        self.modified = True
        self.reload_logs()

    def _open_extract_checklist(self):
        """Extrae criterios de aceptación de la descripción/notas y los presenta en un diálogo editable."""
        desc_text = self.desc_input.toPlainText().strip()
        task = database.get_task(self.task_id, self.db_path)
        title = task["title"] if task else self.title_input.text()

        items = local_ai.extract_checklist_offline(desc_text)
        formatted_items = "\n".join(f"- [ ] {item}" if not item.startswith("- [") else item for item in items)

        ai_tasks = [{"title": title, "description": desc_text or title, "links": []}]
        dlg = AiAssistDialog(
            t("ai.checklist.title"),
            formatted_items,
            t("ai.checklist.confirm_btn"),
            t("ai.checklist.hint"),
            mode="extract_checklist",
            ai_tasks=ai_tasks,
            parent=self,
        )
        dlg.confirmed.connect(self._apply_checklist)
        dlg.exec()

    def _apply_checklist(self, text: str):
        """Inserta la checklist confirmada en las notas/descripción de la tarea."""
        checklist_str = (text or "").strip()
        if not checklist_str:
            return

        current_desc = self.desc_input.toPlainText().strip()
        if not current_desc:
            new_desc = f"### Criterios de Aceptación\n{checklist_str}"
        else:
            new_desc = f"{current_desc}\n\n### Criterios de Aceptación\n{checklist_str}"

        self.desc_input.setPlainText(new_desc)
        self.modified = True

    def _suggest_title_action(self):
        """Sugiere un título en formato Conventional Commits basándose en el título actual y notas."""
        curr_title = self.title_input.text().strip()
        curr_desc = self.desc_input.toPlainText().strip()
        suggested = local_ai.suggest_conventional_title(curr_title, curr_desc)
        if suggested and suggested != curr_title:
            self.title_input.setText(suggested)
            self.modified = True

    def _suggest_tags_action(self):
        """Sugiere etiquetas aplicables a la tarea basándose en su contenido."""
        curr_title = self.title_input.text().strip()
        curr_desc = self.desc_input.toPlainText().strip()

        # Recopilar todos los tag_values existentes en la base de datos
        db_values = []
        categories = database.get_tag_categories(self.db_path)
        for cat in categories:
            for val in database.get_tag_values(cat["id"], self.db_path):
                db_values.append(val)

        available_names = [v["value"] for v in db_values]
        suggested_names = local_ai.suggest_tags_offline(curr_title, curr_desc, available_names)

        added = 0
        for name in suggested_names:
            # Buscar si coincide con algún valor existente en la BD
            match = next((v for v in db_values if v["value"].lower() == name.lower()), None)
            if match:
                # Comprobar que no esté ya asignado
                if not any(t.get("tag_value_id") == match["id"] for t in self.current_tags):
                    self._set_category_value(match)
                    added += 1

        if added > 0:
            self.modified = True
            QMessageBox.information(
                self,
                t("task_detail.suggest_tags_btn"),
                t("task_detail.suggest_tags_added", count=added)
            )
        else:
            QMessageBox.information(
                self,
                t("task_detail.suggest_tags_btn"),
                t("task_detail.suggest_tags_none")
            )

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

