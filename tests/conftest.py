import gc

import pytest
from PySide6.QtWidgets import QApplication
import database


@pytest.fixture(scope="session")
def qapp():
    """QApplication compartida para toda la sesión de tests: cualquier test que
    construya un widget de Qt (QDialog, QWidget, ...) debe pedir este fixture."""
    app = QApplication.instance() or QApplication([])
    yield app
    app.closeAllWindows()
    app.processEvents()
    gc.collect()
    app.processEvents()


@pytest.fixture(autouse=True)
def _close_top_level_widgets_after_each_test(qapp):
    """Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test
    haya dejado vivo (BoardViewWidget/TaskDetailDialog/MainWindow construidos sin
    padre, la forma habitual en este suite) en vez de dejarlos acumularse hasta el
    teardown de sesión de `qapp`. Sin esto, cientos de widgets huérfanos (y los
    QTimer parentados a ellos) convergen en una única ráfaga de destrucción al
    final de toda la sesión -- exactamente la "población realista de zombis
    simultáneos" que reprodujo el STATUS_HEAP_CORRUPTION intermitente en CI.
    Repartir la limpieza test a test reduce drásticamente cuántos objetos Qt mueren
    a la vez en cualquier punto dado. No sustituye la limpieza explícita que ya
    hacen algunos tests (p. ej. los de destrucción del diálogo, o
    `_close_window` en test_main_window.py) -- es un cierre de red adicional para
    todos los demás, y es un no-op para lo que un test ya destruyó por su cuenta."""
    yield
    for widget in qapp.topLevelWidgets():
        if hasattr(widget, "close"):
            try:
                widget.close()
            except Exception:
                pass
        if hasattr(widget, "deleteLater"):
            try:
                widget.deleteLater()
            except Exception:
                pass
    qapp.processEvents()


@pytest.fixture
def db_path(tmp_path):
    """Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin."""
    path = str(tmp_path / "ekin_test.db")
    database.init_db(path)
    return path
