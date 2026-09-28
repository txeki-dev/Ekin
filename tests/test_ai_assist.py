"""Pruebas del resumen determinista del diario (local_ai.summarize_diary_offline), que el
servidor MCP usa en get_task_condensed_context para ahorrar tokens al agente."""
import local_ai
import strings


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
