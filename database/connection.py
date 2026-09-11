"""
Gestor de conexión y configuración global de base de datos SQLite para Ekin.
Desacoplado para evitar ciclos de importación entre los submódulos de database.
"""

import os
import sys
import sqlite3
import contextlib


def get_default_db_path():
    env_path = os.environ.get("EKIN_DB_PATH")
    if env_path:
        return env_path
    if getattr(sys, "frozen", False):
        ekin_dir = os.path.expanduser("~/.ekin")
        os.makedirs(ekin_dir, exist_ok=True)
        target_path = os.path.join(ekin_dir, "ekin_board.db")
        legacy_path = os.path.expanduser("~/EkinKanban/ekin_board.db")
        if not os.path.exists(target_path) and os.path.exists(legacy_path):
            import shutil
            try:
                shutil.copy2(legacy_path, target_path)
            except Exception:
                pass
        return target_path
    return "ekin_board.db"


DB_NAME = get_default_db_path()


@contextlib.contextmanager
def get_connection(db_path=None):
    """Establece una conexión a la base de datos, habilita las claves foráneas y la
    cierra siempre al salir (commit en éxito, rollback si hay excepción)."""
    if db_path is None:
        import database
        db_path = getattr(database, "DB_NAME", DB_NAME)
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 15000;")
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
    except Exception:
        pass
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
