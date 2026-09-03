"""
Gestor de conexión y configuración global de base de datos SQLite para Ekin.
Desacoplado para evitar ciclos de importación entre los submódulos de database.
"""

import sqlite3
import contextlib

DB_NAME = "ekin_board.db"


@contextlib.contextmanager
def get_connection(db_path=None):
    """Establece una conexión a la base de datos, habilita las claves foráneas y la
    cierra siempre al salir (commit en éxito, rollback si hay excepción)."""
    if db_path is None:
        import database
        db_path = getattr(database, "DB_NAME", DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
