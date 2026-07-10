import pytest
import database


@pytest.fixture
def db_path(tmp_path):
    """Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin."""
    path = str(tmp_path / "ekin_test.db")
    database.init_db(path)
    return path
