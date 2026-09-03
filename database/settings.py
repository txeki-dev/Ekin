from .connection import get_connection

__all__ = ["get_setting", "set_setting"]

# --- AJUSTES DE LA APLICACIÓN (clave/valor) ---

def get_setting(key, default=None, db_path=None):
    """Devuelve el valor de un ajuste, o `default` si no está definido."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else default

def set_setting(key, value, db_path=None):
    """Crea o actualiza un ajuste de la aplicación."""
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO app_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
