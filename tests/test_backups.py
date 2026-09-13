import os
import sqlite3

import backups
import database


def test_backup_creates_valid_copy(db_path, tmp_path):
    # Datos de referencia en la BD original
    board_id = database.create_board("Respáldame", db_path=db_path)

    backup_dir = str(tmp_path / "backups")
    dest = backups.backup_database(db_path, keep=5, backup_dir=backup_dir)

    assert dest is not None
    assert os.path.exists(dest)
    assert dest.endswith(".bak")

    # El backup es una BD SQLite válida con los mismos datos
    conn = sqlite3.connect(dest)
    try:
        rows = conn.execute("SELECT name FROM boards WHERE id = ?", (board_id,)).fetchall()
    finally:
        conn.close()
    assert rows == [("Respáldame",)]


def test_backup_rotation_keeps_only_n(db_path, tmp_path):
    backup_dir = str(tmp_path / "backups")
    keep = 2
    for _ in range(5):
        backups.backup_database(db_path, keep=keep, backup_dir=backup_dir)

    remaining = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
    assert len(remaining) == keep


def test_backup_rapid_calls_never_collide(db_path, tmp_path):
    backup_dir = str(tmp_path / "backups")
    paths = [backups.backup_database(db_path, keep=10, backup_dir=backup_dir) for _ in range(5)]
    assert len(paths) == 5
    assert len(set(paths)) == 5
    for p in paths:
        assert os.path.exists(p)


def test_backup_returns_none_when_source_missing(tmp_path):
    missing = str(tmp_path / "no_existe.db")
    assert backups.backup_database(missing) is None


def test_backup_rotation_zero_or_negative_keep_does_not_prune(db_path, tmp_path):
    backup_dir = str(tmp_path / "backups")
    for _ in range(3):
        backups.backup_database(db_path, keep=0, backup_dir=backup_dir)
    remaining = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
    assert len(remaining) == 3


def test_backup_default_dir_is_sibling_backups_folder(db_path):
    dest = backups.backup_database(db_path, keep=3)
    try:
        expected_dir = os.path.join(os.path.dirname(os.path.abspath(db_path)), "backups")
        assert os.path.dirname(dest) == expected_dir
    finally:
        # Limpieza: no dejar la carpeta de backups del tmp de la prueba
        if dest and os.path.exists(dest):
            os.remove(dest)
