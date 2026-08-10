from . import get_connection

__all__ = [
    "create_column", "get_columns", "update_column", "set_column_collapsed",
    "update_column_positions", "delete_column",
]

# --- OPERACIONES DE COLUMNAS (COLUMNS) ---

def create_column(board_id, name, color='#3b82f6', db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Obtener la posición máxima actual para colocar la nueva columna al final
        cursor.execute("SELECT COALESCE(MAX(position), -1) FROM columns WHERE board_id = ?", (board_id,))
        max_pos = cursor.fetchone()[0]
        next_pos = max_pos + 1

        cursor.execute(
            "INSERT INTO columns (board_id, name, color, position) VALUES (?, ?, ?, ?)",
            (board_id, name, color, next_pos)
        )
        return cursor.lastrowid

def get_columns(board_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, board_id, name, color, position, collapsed FROM columns WHERE board_id = ? ORDER BY position ASC",
            (board_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def update_column(column_id, name, color, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE columns SET name = ?, color = ? WHERE id = ?",
            (name, color, column_id)
        )

def set_column_collapsed(column_id, collapsed, db_path=None):
    """Pliega (collapsed=1) o despliega (0) una columna del tablero."""
    with get_connection(db_path) as conn:
        conn.execute("UPDATE columns SET collapsed = ? WHERE id = ?", (1 if collapsed else 0, column_id))

def update_column_positions(column_positions, db_path=None):
    """Actualiza las posiciones de múltiples columnas.
    column_positions debe ser una lista de tuplas/diccionarios: (column_id, position)
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for col_id, pos in column_positions:
            cursor.execute("UPDATE columns SET position = ? WHERE id = ?", (pos, col_id))

def delete_column(column_id, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM columns WHERE id = ?", (column_id,))
