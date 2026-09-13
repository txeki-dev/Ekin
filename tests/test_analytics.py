"""Pruebas del panel de Analíticas (analytics.py + dashboard_view.py):
gather_stats (métricas desde datos existentes), render_report_html (puro),
export_report_pdf (escribe un PDF) y construcción headless del DashboardWidget."""
from datetime import date, timedelta

import analytics
import database


def _iso(days):
    return (date.today() + timedelta(days=days)).isoformat()


def _seed_two_boards(db_path):
    b1 = database.create_board("Alpha", "#c67139", db_path=db_path)
    c1 = database.create_column(b1, "To do", db_path=db_path)
    database.create_task(c1, "overdue", due_date=_iso(-2), db_path=db_path)
    database.create_task(c1, "today", due_date=date.today().isoformat(), db_path=db_path)
    database.create_task(c1, "no due", db_path=db_path)
    running = database.create_task(c1, "running", db_path=db_path)
    database.set_task_timer_started(running, "2026-01-01T09:00:00", db_path=db_path)

    b2 = database.create_board("Beta", "#7a8a5e", db_path=db_path)
    c2 = database.create_column(b2, "To do", db_path=db_path)
    database.create_task(c2, "later", due_date=_iso(30), db_path=db_path)
    return b1, b2


def test_gather_stats_counts(db_path):
    _seed_two_boards(db_path)
    stats = analytics.gather_stats(db_path, today_iso=date.today().isoformat())

    assert stats["totals"]["boards"] == 2
    assert stats["totals"]["tasks"] == 5
    assert stats["totals"]["overdue"] == 1
    assert stats["totals"]["due_this_week"] == 1
    assert stats["totals"]["running_timers"] == 1

    per_board = {b["name"]: b["count"] for b in stats["per_board"]}
    assert per_board == {"Alpha": 4, "Beta": 1}

    ds = stats["due_status"]
    assert ds == {"overdue": 1, "this_week": 1, "later": 1, "no_due": 2}


def test_render_report_html_contains_data_and_escapes():
    stats = {
        "totals": {"boards": 1, "tasks": 2, "with_due": 1, "overdue": 1,
                   "due_this_week": 1, "running_timers": 0},
        "per_board": [{"name": "A & <B>", "color": "#000", "count": 2}],
        "due_status": {"overdue": 1, "this_week": 0, "later": 0, "no_due": 1},
    }
    html = analytics.render_report_html(stats, generated_on="2026-09-13")
    assert "2026-09-13" in html
    assert "A &amp; &lt;B&gt;" in html  # escapado, sin romper el HTML
    assert ">2<" in html                # recuento del tablero


def test_export_report_pdf_writes_file(qapp, tmp_path, db_path):
    _seed_two_boards(db_path)
    stats = analytics.gather_stats(db_path)
    out = str(tmp_path / "report.pdf")
    analytics.export_report_pdf(stats, out)
    import os
    assert os.path.exists(out) and os.path.getsize(out) > 0


def test_dashboard_widget_constructs_and_refreshes(qapp, db_path):
    from dashboard_view import DashboardWidget
    _seed_two_boards(db_path)
    dash = DashboardWidget(db_path)
    # dos tableros en la gráfica por tablero; cuatro filas en la de estado de vencimiento
    assert len(dash.per_board_chart._data) == 2
    assert len(dash.due_chart._data) == 4
