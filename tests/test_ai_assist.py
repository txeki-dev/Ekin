"""Pruebas de los asistentes de IA local offline (local_ai) y su integración:
- suggest_subtasks_offline / parse_subtask_lines / summarize_diary_offline (lógica pura).
- AiAssistDialog: edición + confirmación (headless).
- TaskDetailDialog._apply_breakdown / _apply_summary (crea tareas / publica en diario).
"""
from PySide6.QtWidgets import QMessageBox

import database
import local_ai
import strings
from ai_assist_dialog import AiAssistDialog


# --- Lógica pura --------------------------------------------------------------

def test_suggest_subtasks_from_description_bullets():
    task = {"title": "Feature", "description": "<p>- Design API</p><p>- Build UI</p><p>- Write tests</p>"}
    items = local_ai.suggest_subtasks_offline(task)
    assert items == ["Design API", "Build UI", "Write tests"]


def test_suggest_subtasks_phase_fallback_when_no_hints():
    task = {"title": "Ship it", "description": ""}
    items = local_ai.suggest_subtasks_offline(task)
    assert len(items) == 3
    assert all("Ship it" in it for it in items)  # cada fase referencia el título


def test_parse_subtask_lines_strips_markup():
    text = "## Heading\n- Alpha\n2) Beta\n   \n* `Gamma`"
    assert local_ai.parse_subtask_lines(text) == ["Alpha", "Beta", "Gamma"]


def test_summarize_diary_offline_empty():
    assert local_ai.summarize_diary_offline([]) == strings.t("ai.summary.empty")


def test_summarize_diary_offline_builds_two_sections():
    logs = [
        {"content": "<p>Did the schema</p>", "created_at": "2026-09-10T09:00:00"},
        {"content": "<p>Wired the UI</p>", "created_at": "2026-09-11T09:00:00"},
    ]
    summary = local_ai.summarize_diary_offline(logs, "My task")
    assert summary.count("## ") == 2      # "What happened" + "Next step"
    assert "Did the schema" in summary
    assert "Wired the UI" in summary


# --- AiAssistDialog headless --------------------------------------------------

def test_ai_assist_dialog_confirm_emits_edited_text(qapp):
    dlg = AiAssistDialog("Title", "one\ntwo", "OK", "hint")
    captured = []
    dlg.confirmed.connect(captured.append)
    dlg.editor.setPlainText("one\ntwo\nthree")
    dlg._confirm()
    assert captured == ["one\ntwo\nthree"]


# --- Integración en TaskDetailDialog -----------------------------------------

def _make_task(db_path):
    board_id = database.create_board("B", db_path=db_path)
    col_id = database.create_column(board_id, "C", db_path=db_path)
    task_id = database.create_task(col_id, "Parent", db_path=db_path)
    return board_id, col_id, task_id


def test_apply_breakdown_creates_sibling_tasks(qapp, db_path, monkeypatch):
    from detail_dialog.task_detail_dialog import TaskDetailDialog
    monkeypatch.setattr(QMessageBox, "information", lambda *a, **k: None)
    _board, col_id, task_id = _make_task(db_path)

    dlg = TaskDetailDialog(task_id, db_path)
    dlg._apply_breakdown("Alpha\nBeta")

    titles = [t["title"] for t in database.get_tasks(col_id, db_path)]
    assert "Alpha" in titles and "Beta" in titles
    assert dlg.modified is True


def test_apply_summary_posts_journal_entry(qapp, db_path):
    from detail_dialog.task_detail_dialog import TaskDetailDialog
    _board, _col, task_id = _make_task(db_path)

    dlg = TaskDetailDialog(task_id, db_path)
    before = len(database.get_logs(task_id, db_path))
    dlg._apply_summary("## What happened\n- Did a thing")

    logs = database.get_logs(task_id, db_path)
    assert len(logs) == before + 1
    assert "Did a thing" in logs[-1]["content"]
    assert dlg.modified is True


# --- Mejora por LLM local: prompts + fallback estructural (puro) --------------

def test_build_spec_prompts_task_breakdown_mode():
    sys_p, usr_p = local_ai.build_spec_prompts(
        [{"title": "Ship X", "description": "do it"}], "task_breakdown"
    )
    assert "línea" in sys_p.lower()   # "un título por línea"
    assert "Ship X" in usr_p


def test_build_spec_prompts_diary_summary_mode():
    sys_p, usr_p = local_ai.build_spec_prompts(
        [{"title": "T", "description": "did the thing"}], "diary_summary"
    )
    assert "resume" in sys_p.lower()
    assert "did the thing" in usr_p


def test_generate_structural_spec_breakdown_is_a_plain_list():
    out = local_ai.generate_structural_spec(
        [{"title": "F", "description": "- Alpha\n- Beta"}], "task_breakdown"
    )
    assert local_ai.parse_subtask_lines(out) == ["Alpha", "Beta"]


def test_generate_structural_spec_diary_summary_two_sections():
    out = local_ai.generate_structural_spec(
        [{"title": "T", "description": "Line one\nLine two"}], "diary_summary"
    )
    assert out.count("## ") == 2
    assert "Line one" in out


# --- Botón de mejora en el diálogo -------------------------------------------

def test_enhance_button_only_present_with_mode(qapp):
    assert AiAssistDialog("T", "x", "OK").enhance_btn is None
    dlg = AiAssistDialog("T", "x", "OK", mode="task_breakdown", ai_tasks=[{"title": "A"}])
    assert dlg.enhance_btn is not None


def test_enhance_streams_result_into_editor(qapp, monkeypatch):
    from PySide6.QtCore import QObject, Signal

    class FakeThread(QObject):
        token_received = Signal(str)
        generation_finished = Signal(str)
        error_occurred = Signal(str)

        def __init__(self, tasks, mode, parent=None):
            super().__init__(parent)
            self.tasks, self.mode = tasks, mode

        def start(self):
            self.generation_finished.emit("ENHANCED")

        def cancel(self):
            pass

        def isRunning(self):
            return False

        def wait(self, ms=0):
            return True

    monkeypatch.setattr(local_ai, "SpecGenerationThread", FakeThread)
    dlg = AiAssistDialog("T", "draft", "OK", mode="task_breakdown", ai_tasks=[{"title": "A"}])
    dlg._start_enhance()
    assert dlg.editor.toPlainText() == "ENHANCED"
