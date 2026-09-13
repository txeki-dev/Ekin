"""Registro de diagnóstico y captura global de errores para Ekin.

Escribe un log rotativo en ~/.ekin/logs/ekin.log, enruta los mensajes de Qt al log y
sustituye el excepthook por uno que registra la traza y muestra un aviso NO fatal en vez
de terminar el proceso en silencio (la clase de fallo de varios crashes históricos)."""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

_LOGGER_NAME = "ekin"


def get_log_dir():
    """Directorio de logs (se crea si no existe): ~/.ekin/logs."""
    d = os.path.join(os.path.expanduser("~/.ekin"), "logs")
    os.makedirs(d, exist_ok=True)
    return d


def setup_logging(log_dir=None, level=logging.INFO):
    """Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del log."""
    log_dir = log_dir or get_log_dir()
    log_path = os.path.join(log_dir, "ekin.log")
    root = logging.getLogger()
    for h in root.handlers:
        if isinstance(h, RotatingFileHandler) and getattr(h, "_ekin", False):
            return log_path  # ya configurado
    handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    handler._ekin = True
    root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger(_LOGGER_NAME).info("Logging initialized")
    return log_path


def install_excepthook():
    """Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)."""
    logger = logging.getLogger(_LOGGER_NAME)
    previous = sys.excepthook

    def _hook(exc_type, exc, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            previous(exc_type, exc, tb)
            return
        logger.error("Unhandled exception", exc_info=(exc_type, exc, tb))
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            if QApplication.instance() is not None:
                QMessageBox.critical(None, "Ekin", f"{exc_type.__name__}: {exc}")
        except Exception:
            pass

    sys.excepthook = _hook


def install_qt_message_handler():
    """Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin."""
    from PySide6.QtCore import qInstallMessageHandler, QtMsgType
    logger = logging.getLogger("ekin.qt")

    def _handler(mode, context, message):
        if mode == QtMsgType.QtWarningMsg:
            logger.warning(message)
        elif mode in (QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
            logger.error(message)
        else:
            logger.info(message)

    qInstallMessageHandler(_handler)
