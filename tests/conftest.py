import pytest
from PySide6.QtWidgets import QApplication
import database


@pytest.fixture(scope="session")
def qapp():
    """QApplication compartida para toda la sesión de tests: cualquier test que
    construya un widget de Qt (QDialog, QWidget, ...) debe pedir este fixture."""
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def db_path(tmp_path):
    """Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin."""
    path = str(tmp_path / "ekin_test.db")
    database.init_db(path)
    return path
