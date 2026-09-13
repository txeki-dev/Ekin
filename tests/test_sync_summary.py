"""Prueba del resumen conciso de sincronización (board_view.format_sync_summary)."""
import board_sync
import strings
from board_view import format_sync_summary


def test_summary_up_to_date():
    res = board_sync.SyncResult(status="up_to_date", board_id=1)
    assert format_sync_summary(res) == strings.t("sync.summary_up_to_date")


def test_summary_exported():
    res = board_sync.SyncResult(status="exported", board_id=1, tasks_exported=3)
    assert format_sync_summary(res) == strings.t("sync.summary_exported")


def test_summary_merged_lists_updates_and_conflicts():
    res = board_sync.SyncResult(status="merged", board_id=1, tasks_imported=2, conflicts_resolved=1)
    summary = format_sync_summary(res)
    assert "·" in summary
    assert "2" in summary   # tareas actualizadas
    assert "1" in summary   # conflictos autoarchivados


def test_summary_imported_without_conflicts():
    res = board_sync.SyncResult(status="imported", board_id=1, tasks_imported=5)
    summary = format_sync_summary(res)
    assert "5" in summary
    assert strings.t("sync.summary_conflicts", count=1) not in summary
