"""Métricas de tableros para el panel de Analíticas y la exportación a PDF.

`gather_stats` consulta la base de datos y devuelve un dict con totales, tareas por
tablero y distribución por estado de vencimiento — todo a partir de datos que la app ya
almacena (sin nuevos esquemas). `render_report_html` es pura (sin Qt) y probable sola;
`export_report_pdf` la renderiza a PDF con QPdfWriter (sin dependencias nuevas)."""

from datetime import date, timedelta

import database

# Ventana de "esta semana" para la distribución por vencimiento.
THIS_WEEK_DAYS = 7


def gather_stats(db_path=None, today_iso=None):
    """Recopila métricas transversales (todos los tableros activos)."""
    today_iso = today_iso or date.today().isoformat()
    week_end_iso = (date.fromisoformat(today_iso) + timedelta(days=THIS_WEEK_DAYS)).isoformat()

    boards = database.get_boards(db_path)
    per_board = []
    total_tasks = 0
    for b in boards:
        count = 0
        for col in database.get_columns(b["id"], db_path):
            count += len(database.get_tasks(col["id"], db_path))
        per_board.append({"name": b["name"], "color": b["color"], "count": count})
        total_tasks += count

    scheduled = database.get_scheduled_tasks(db_path=db_path)  # todas las que tienen due_date
    overdue = [t for t in scheduled if t["due_date"] < today_iso]
    this_week = [t for t in scheduled if today_iso <= t["due_date"] <= week_end_iso]
    later = [t for t in scheduled if t["due_date"] > week_end_iso]
    running = database.get_active_timer_tasks(db_path)

    return {
        "totals": {
            "boards": len(boards),
            "tasks": total_tasks,
            "with_due": len(scheduled),
            "overdue": len(overdue),
            "due_this_week": len(this_week),
            "running_timers": len(running),
        },
        "per_board": per_board,
        "due_status": {
            "overdue": len(overdue),
            "this_week": len(this_week),
            "later": len(later),
            "no_due": total_tasks - len(scheduled),
        },
    }


def render_report_html(stats, title="Ekin — Board Analytics", generated_on=None):
    """Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)."""
    generated_on = generated_on or date.today().isoformat()
    tot = stats["totals"]
    rows = "".join(
        f"<tr><td>{_esc(b['name'])}</td><td align='right'>{b['count']}</td></tr>"
        for b in stats["per_board"]
    ) or "<tr><td colspan='2'><i>No boards.</i></td></tr>"
    ds = stats["due_status"]
    return f"""<html><body style="font-family: sans-serif; color: #201e1d;">
<h1 style="color:#c67139;">{_esc(title)}</h1>
<p style="color:#645c50;">Generated {generated_on}</p>
<h2>Totals</h2>
<ul>
  <li>Boards: <b>{tot['boards']}</b></li>
  <li>Tasks: <b>{tot['tasks']}</b></li>
  <li>With due date: <b>{tot['with_due']}</b></li>
  <li>Overdue: <b>{tot['overdue']}</b></li>
  <li>Due this week: <b>{tot['due_this_week']}</b></li>
  <li>Running timers: <b>{tot['running_timers']}</b></li>
</ul>
<h2>Tasks per board</h2>
<table border="1" cellspacing="0" cellpadding="6" width="100%">
  <tr><th align="left">Board</th><th align="right">Tasks</th></tr>
  {rows}
</table>
<h2>Due status</h2>
<ul>
  <li>Overdue: <b>{ds['overdue']}</b></li>
  <li>This week: <b>{ds['this_week']}</b></li>
  <li>Later: <b>{ds['later']}</b></li>
  <li>No due date: <b>{ds['no_due']}</b></li>
</ul>
</body></html>"""


def export_report_pdf(stats, path, title="Ekin — Board Analytics", generated_on=None):
    """Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)."""
    from PySide6.QtGui import QPdfWriter, QTextDocument, QPageSize

    writer = QPdfWriter(path)
    writer.setPageSize(QPageSize(QPageSize.A4))
    doc = QTextDocument()
    doc.setHtml(render_report_html(stats, title=title, generated_on=generated_on))
    doc.print_(writer)
    return path


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
