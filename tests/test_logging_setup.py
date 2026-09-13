"""Pruebas del registro de diagnóstico y captura de errores (logging_setup.py)."""
import logging
import sys
from logging.handlers import RotatingFileHandler

import logging_setup


def test_get_log_dir_creates_dir():
    d = logging_setup.get_log_dir()
    import os
    assert d.endswith("logs")
    assert os.path.isdir(d)


def test_setup_logging_writes_to_file(tmp_path):
    root = logging.getLogger()
    added_before = list(root.handlers)
    try:
        log_path = logging_setup.setup_logging(log_dir=str(tmp_path))
        logging.getLogger("ekin").info("marker-xyz")
        for h in root.handlers:
            h.flush()
        import os
        assert os.path.exists(log_path)
        with open(log_path, encoding="utf-8") as f:
            content = f.read()
        assert "marker-xyz" in content
    finally:
        # Limpieza: quitar los handlers rotativos que añadimos apuntando al tmp
        for h in list(root.handlers):
            if isinstance(h, RotatingFileHandler) and h not in added_before:
                root.removeHandler(h)
                h.close()


def test_install_excepthook_sets_and_logs(monkeypatch):
    # Un QApplication de sesión puede existir; evitar el diálogo modal del hook.
    from PySide6.QtWidgets import QMessageBox
    monkeypatch.setattr(QMessageBox, "critical", lambda *a, **k: None)
    original = sys.excepthook
    try:
        logging_setup.install_excepthook()
        assert sys.excepthook is not original
        # No debe propagar la excepción ni requerir UI (sin QApplication en este test)
        try:
            raise ValueError("boom")
        except ValueError:
            sys.excepthook(*sys.exc_info())  # no debe lanzar
    finally:
        sys.excepthook = original
