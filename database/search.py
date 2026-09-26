import re
import sqlite3
from .connection import get_connection
from .tags import get_task_tags_bulk

__all__ = ["search_tasks"]


def _sanitize_fts_query(text: str) -> str:
    """Sanea el texto de búsqueda para FTS5 generando términos con comodín de prefijo."""
    clean = re.sub(r"[^\w\s]", " ", (text or "")).strip()
    tokens = [t for t in clean.split() if t]
    if not tokens:
        return ""
    # Prefijo con comodín para búsqueda interactiva/as-you-type
    return " ".join(f'"{token}"*' for token in tokens)


def _search_tasks_fts(fts_match, board_id=None, tag_value_id=None, only_due=False, db_path=None):
    """Búsqueda de texto completo de alto rendimiento con FTS5 y ordenación por relevancia BM25."""
    query = [
        "SELECT DISTINCT t.id, t.title, t.description, t.due_date, t.due_time, t.recurrence,",
        "       t.timer_started_at, t.column_id, t.updated_at,",
        "       c.board_id AS board_id, b.name AS board_name, b.color AS board_color,",
        "       c.name AS column_name,",
        "       bm25(tasks_fts) AS rank",
        "FROM tasks_fts",
        "JOIN tasks t ON tasks_fts.task_id = t.id",
        "JOIN columns c ON t.column_id = c.id",
        "JOIN boards b ON c.board_id = b.id",
    ]
    params = []
    if tag_value_id is not None:
        query.append("JOIN task_tags tt ON tt.task_id = t.id AND tt.tag_value_id = ?")
        params.append(tag_value_id)
    query.append("WHERE tasks_fts MATCH ?")
    params.append(fts_match)
    if board_id is not None:
        query.append("AND c.board_id = ?")
        params.append(board_id)
    if only_due:
        query.append("AND t.due_date IS NOT NULL AND t.due_date != ''")
    query.append("ORDER BY rank ASC, b.name ASC, t.title ASC")

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("\n".join(query), params)
        tasks = [dict(row) for row in cursor.fetchall()]

    tags_by_task = get_task_tags_bulk([t["id"] for t in tasks], db_path)
    for t in tasks:
        t["tags"] = tags_by_task.get(t["id"], [])
    return tasks


def _search_tasks_like(text="", board_id=None, tag_value_id=None, only_due=False, db_path=None):
    """Búsqueda tradicional mediante SQL LIKE utilizada cuando no hay texto o como fallback."""
    query = [
        "SELECT DISTINCT t.id, t.title, t.description, t.due_date, t.due_time, t.recurrence,",
        "       t.timer_started_at, t.column_id, t.updated_at,",
        "       c.board_id AS board_id, b.name AS board_name, b.color AS board_color,",
        "       c.name AS column_name",
        "FROM tasks t",
        "JOIN columns c ON t.column_id = c.id",
        "JOIN boards b ON c.board_id = b.id",
    ]
    params = []
    if tag_value_id is not None:
        query.append("JOIN task_tags tt ON tt.task_id = t.id AND tt.tag_value_id = ?")
        params.append(tag_value_id)
    query.append("WHERE 1 = 1")
    if text:
        query.append("AND (t.title LIKE ? OR t.description LIKE ?)")
        like = f"%{text}%"
        params.extend([like, like])
    if board_id is not None:
        query.append("AND c.board_id = ?")
        params.append(board_id)
    if only_due:
        query.append("AND t.due_date IS NOT NULL AND t.due_date != ''")
    query.append("ORDER BY b.name ASC, t.title ASC")

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("\n".join(query), params)
        tasks = [dict(row) for row in cursor.fetchall()]

    tags_by_task = get_task_tags_bulk([t["id"] for t in tasks], db_path)
    for t in tasks:
        t["tags"] = tags_by_task.get(t["id"], [])
    return tasks


def search_tasks(text="", board_id=None, tag_value_id=None, only_due=False, db_path=None):
    """Busca tareas en todos los tableros (o en uno) con filtros opcionales.

    Utiliza SQLite FTS5 acelerado con ranking de relevancia BM25 indexando títulos,
    descripciones y notas/diario (`task_logs`). Si FTS5 no está disponible o el
    término no es indexable, recurre de forma transparente a búsqueda SQL LIKE.

    - text: término de búsqueda libre en título, descripción o diario.
    - board_id: limitar a un tablero.
    - tag_value_id: solo tareas que tengan esa etiqueta (Categoría: Valor).
    - only_due: solo tareas con fecha de vencimiento.
    Devuelve dicts enriquecidos con tablero, columna y etiquetas, ordenados por
    relevancia BM25, tablero y título.
    """
    clean_text = (text or "").strip()
    fts_query_str = _sanitize_fts_query(clean_text) if clean_text else ""

    if fts_query_str:
        try:
            return _search_tasks_fts(
                fts_query_str,
                board_id=board_id,
                tag_value_id=tag_value_id,
                only_due=only_due,
                db_path=db_path
            )
        except (sqlite3.OperationalError, Exception):
            pass

    return _search_tasks_like(
        clean_text,
        board_id=board_id,
        tag_value_id=tag_value_id,
        only_due=only_due,
        db_path=db_path
    )

