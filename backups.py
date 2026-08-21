"""Copias de seguridad automáticas de la base de datos de Ekin.

En cada arranque se hace una copia consistente de `ekin_board.db` en una carpeta
`backups/` y se conservan solo las `keep` más recientes. Es una red de seguridad
barata frente a corrupción, migraciones fallidas o borrados accidentales.

Sin dependencias externas: usa la API `Connection.backup()` de `sqlite3`, que produce
una copia coherente incluso si la base de datos está abierta o a mitad de una escritura.
"""
import glob
import os
import sqlite3
from datetime import datetime


def backup_database(db_path, keep=5, backup_dir=None):
    """Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.

    Devuelve la ruta del backup creado, o None si la base de datos aún no existe
    (por ejemplo en el primer arranque, antes de crearla).

    - `backup_dir` por defecto es `<carpeta de db_path>/backups` (se crea si falta).
    - El nombre incluye una marca de tiempo con microsegundos, de modo que es único
      y ordenable cronológicamente por orden lexicográfico.
    """
    if not os.path.exists(db_path):
        return None

    base = os.path.basename(db_path)
    if backup_dir is None:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(db_path)), "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    dest = os.path.join(backup_dir, f"{base}.{timestamp}.bak")

    # Copia consistente con la API de backup de SQLite (soporta BD abierta/en uso).
    src = sqlite3.connect(db_path)
    try:
        dst = sqlite3.connect(dest)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()

    _prune_backups(backup_dir, base, keep)
    return dest


def _prune_backups(backup_dir, base, keep):
    """Deja solo las `keep` copias más recientes de `base` en `backup_dir`."""
    if keep <= 0:
        return
    pattern = os.path.join(backup_dir, f"{base}.*.bak")
    # El sufijo de marca de tiempo hace que el orden lexicográfico == cronológico.
    backups = sorted(glob.glob(pattern))
    excess = len(backups) - keep
    if excess > 0:
        for old in backups[:excess]:
            try:
                os.remove(old)
            except OSError:
                pass
