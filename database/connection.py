"""
Gestor de conexión y configuración global de base de datos SQLite para Ekin.
Desacoplado para evitar ciclos de importación entre los submódulos de database.
"""

import os
import sys
import sqlite3
import contextlib


import threading

_local = threading.local()


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


def close_cached_connections(db_path=None):
    """Cierra y purga las conexiones abiertas en el hilo actual para db_path (o todas)."""
    conns = getattr(_local, "connections", None)
    if not conns:
        return
    if db_path is not None:
        norm_path = os.path.abspath(db_path)
        conn = conns.pop(norm_path, None)
        if conn:
            try:
                conn.close()
            except Exception:
                pass
        if hasattr(_local, "depth") and norm_path in _local.depth:
            _local.depth.pop(norm_path, None)
    else:
        for p, conn in list(conns.items()):
            try:
                conn.close()
            except Exception:
                pass
        conns.clear()
        if hasattr(_local, "depth"):
            _local.depth.clear()


@contextlib.contextmanager
def get_connection(db_path=None):
    """Obtiene una conexión reutilizable desde el pool thread-local, habilitando claves foráneas
    y modo WAL una única vez por conexión, garantizando transacciones atómicas seguras."""
    if db_path is None:
        import database
        db_path = getattr(database, "DB_NAME", DB_NAME)

    norm_path = os.path.abspath(db_path)

    # Si el archivo aún no existe, asegurar permisos restrictivos de lectura/escritura (0o600)
    if not os.path.exists(norm_path):
        try:
            with open(norm_path, "a"):
                pass
            if os.name != "nt":
                os.chmod(norm_path, 0o600)
        except Exception:
            pass

    if not hasattr(_local, "connections"):
        _local.connections = {}
        _local.depth = {}

    conn = _local.connections.get(norm_path)
    if conn is None:
        conn = sqlite3.connect(norm_path, timeout=15.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA busy_timeout = 15000;")
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
        except Exception:
            pass
        conn.row_factory = sqlite3.Row
        _local.connections[norm_path] = conn
        _local.depth[norm_path] = 0
    else:
        # Verificar que la conexión almacenada no haya sido cerrada externamente
        try:
            conn.execute("SELECT 1;")
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            conn = sqlite3.connect(norm_path, timeout=15.0)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 15000;")
            try:
                conn.execute("PRAGMA journal_mode = WAL;")
            except Exception:
                pass
            conn.row_factory = sqlite3.Row
            _local.connections[norm_path] = conn
            _local.depth[norm_path] = 0

    _local.depth[norm_path] += 1
    try:
        yield conn
        if _local.depth.get(norm_path) == 1:
            conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        if norm_path in _local.depth:
            _local.depth[norm_path] -= 1


def get_db_data_version(db_path=None) -> int:
    """Devuelve el contador interno PRAGMA data_version de SQLite.
    Permite detectar instantáneamente (en < 5 microsegundos) si alguna otra
    conexión o proceso ha confirmado cambios en el archivo de base de datos."""
    with get_connection(db_path) as conn:
        row = conn.execute("PRAGMA data_version").fetchone()
        return int(row[0]) if row else 0

