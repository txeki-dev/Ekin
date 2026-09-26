"""
Manejo de persistencia vectorial para búsqueda semántica y detección de duplicados en Ekin.
Permite almacenar y recuperar embeddings como BLOBs empaquetados en SQLite de alto rendimiento.
"""

import struct
from typing import Optional, List, Tuple
from .connection import get_connection, DB_NAME


def save_task_embedding(
    task_id: int,
    vector: List[float],
    model_name: str = "local_embedding",
    db_path: Optional[str] = None
):
    """Guarda o actualiza el vector de embedding de una tarea empaquetado en binario BLOB."""
    if not vector:
        return
    dim = len(vector)
    blob = struct.pack(f"{dim}f", *vector)
    with get_connection(db_path or DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_embeddings (task_id, embedding, model_name, dim, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(task_id) DO UPDATE SET
                embedding = excluded.embedding,
                model_name = excluded.model_name,
                dim = excluded.dim,
                updated_at = CURRENT_TIMESTAMP
        """, (task_id, blob, model_name, dim))


def get_task_embedding(task_id: int, db_path: Optional[str] = None) -> Optional[List[float]]:
    """Recupera y desempaqueta el vector de embedding de una tarea."""
    with get_connection(db_path or DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT embedding, dim FROM task_embeddings WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        blob, dim = row["embedding"], row["dim"]
        return list(struct.unpack(f"{dim}f", blob))


def get_board_embeddings(board_id: int, db_path: Optional[str] = None) -> List[Tuple[int, List[float]]]:
    """Obtiene los embeddings de todas las tareas pertenecientes a las columnas de un tablero."""
    with get_connection(db_path or DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.task_id, e.embedding, e.dim
            FROM task_embeddings e
            JOIN tasks t ON e.task_id = t.id
            JOIN columns c ON t.column_id = c.id
            WHERE c.board_id = ?
        """, (board_id,))
        results = []
        for row in cursor.fetchall():
            blob, dim = row["embedding"], row["dim"]
            vec = list(struct.unpack(f"{dim}f", blob))
            results.append((row["task_id"], vec))
        return results


def delete_task_embedding(task_id: int, db_path: Optional[str] = None):
    """Elimina el embedding de una tarea específica."""
    with get_connection(db_path or DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM task_embeddings WHERE task_id = ?", (task_id,))
