"""board_sync_controller.py - Controlador de sincronización desacoplado de BoardViewWidget.

Extrae el ciclo de vida del hilo BoardSyncWorker, el sistema de cola asíncrona,
el vigilante de archivos QFileSystemWatcher reactivo con debounce para OneDrive/Dropbox,
y la gestión del estado de vinculación y sincronización de un tablero.
"""

import os
from typing import Optional
from PySide6.QtCore import QObject, Signal, QTimer, QFileSystemWatcher

import database
import board_sync


def format_sync_summary(res) -> str:
    """Genera un resumen conciso de un SyncResult para mostrar en la interfaz."""
    from strings import t
    status = getattr(res, "status", "")
    if status == "up_to_date":
        return t("sync.summary_up_to_date")
    if status == "exported":
        return t("sync.summary_exported")
    parts = [t("sync.summary_synced")]
    if getattr(res, "tasks_imported", 0):
        parts.append(t("sync.summary_updated", count=res.tasks_imported))
    if getattr(res, "conflicts_resolved", 0):
        parts.append(t("sync.summary_conflicts", count=res.conflicts_resolved))
    return " · ".join(parts)


class BoardSyncController(QObject):
    """Controlador de sincronización autónomo para un tablero Kanban.

    Emite señales de alto nivel que la vista (BoardViewWidget) puede consumir
    para actualizar su botón de estado, tooltips o recargar los datos cuando
    una sincronización entrante modifica tareas o columnas.
    """

    sync_started = Signal(bool)           # user_initiated: bool
    sync_finished = Signal(object, bool)  # res: SyncResult, user_initiated: bool
    sync_status_changed = Signal(object)  # sync_info: Optional[dict]
    board_data_reloaded = Signal()        # emitido cuando la sincronización importó o fusionó cambios

    def __init__(self, parent=None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.db_path = db_path or database.DB_NAME
        self.board_id: Optional[int] = None
        self._current_sync_info: Optional[dict] = None
        self._sync_worker: Optional[board_sync.BoardSyncWorker] = None
        self._sync_queued: bool = False
        self._watched_sync_path: Optional[str] = None
        self._last_sync_summary: str = ""

        # Vigilante reactivo de cambios en el archivo compartido (.ekboard)
        self._file_watcher = QFileSystemWatcher(self)
        self._file_watcher.fileChanged.connect(self._on_sync_file_changed)

        self._sync_debounce_timer = QTimer(self)
        self._sync_debounce_timer.setSingleShot(True)
        self._sync_debounce_timer.setInterval(600)
        self._sync_debounce_timer.timeout.connect(self._on_debounced_file_sync)

    @property
    def is_linked(self) -> bool:
        """Indica si el tablero actual está vinculado a un archivo .ekboard compartido."""
        return bool(self._current_sync_info and self._current_sync_info.get("sync_path"))

    @property
    def current_sync_info(self) -> Optional[dict]:
        return self._current_sync_info

    @property
    def last_sync_summary(self) -> str:
        return self._last_sync_summary

    @property
    def worker(self) -> Optional[board_sync.BoardSyncWorker]:
        return self._sync_worker

    def set_board(self, board_id: int, db_path: Optional[str] = None):
        """Asigna el tablero activo e inicializa su estado y su vigilante de archivos."""
        self.board_id = board_id
        if db_path is not None:
            self.db_path = db_path

        if not self.board_id or self.board_id == -1:
            self._current_sync_info = None
            self.setup_file_watcher(None)
            self.sync_status_changed.emit(None)
            return

        sync_info = database.get_board_sync_info(self.board_id, self.db_path)
        self._current_sync_info = sync_info
        path = sync_info.get("sync_path") if sync_info else None
        self.setup_file_watcher(path)
        self.sync_status_changed.emit(sync_info)

    def setup_file_watcher(self, path: Optional[str]):
        """Configura el watcher para detectar reactivamente cambios externos."""
        existing = self._file_watcher.files()
        if existing:
            self._file_watcher.removePaths(existing)

        if path and os.path.exists(path):
            self._file_watcher.addPath(path)
            self._watched_sync_path = path
        else:
            self._watched_sync_path = None

    def ensure_watcher_path_active(self):
        """Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos."""
        if (
            self._watched_sync_path
            and os.path.exists(self._watched_sync_path)
            and self._watched_sync_path not in self._file_watcher.files()
        ):
            self._file_watcher.addPath(self._watched_sync_path)

    def _on_sync_file_changed(self, _path: str):
        """Disparado por el sistema de archivos ante modificaciones externas."""
        self._sync_debounce_timer.start()

    def _on_debounced_file_sync(self):
        """Ejecuta la sincronización en diferido cuando finalizan las escrituras."""
        self.sync_now(user_initiated=False)

    def sync_now(
        self,
        user_initiated: bool = False,
        blocking: bool = False,
        file_path: Optional[str] = None
    ) -> Optional[board_sync.SyncResult]:
        """Inicia una sincronización del tablero activo.

        Si blocking=True, se ejecuta sincrónicamente y devuelve SyncResult.
        Si blocking=False, se ejecuta en un hilo BoardSyncWorker y emite señales.
        """
        if not self.board_id or self.board_id == -1:
            return None

        if blocking:
            res = board_sync.sync_board_with_file(self.board_id, file_path, self.db_path)
            self._handle_sync_finished(res, user_initiated=user_initiated)
            return res

        if self._sync_worker and self._sync_worker.isRunning():
            self._sync_queued = True
            return None

        self.sync_started.emit(user_initiated)
        self._sync_worker = board_sync.BoardSyncWorker(
            self.board_id,
            sync_path=file_path,
            db_path=self.db_path,
            parent=self
        )
        self._sync_worker.sync_finished.connect(
            lambda res: self._handle_sync_finished(res, user_initiated=user_initiated)
        )
        self._sync_worker.start()
        return None

    def _handle_sync_finished(self, res: board_sync.SyncResult, user_initiated: bool = False):
        """Procesa la finalización de una sincronización."""
        self._sync_worker = None
        self.ensure_watcher_path_active()

        self._last_sync_summary = format_sync_summary(res)
        if self.board_id and self.board_id != -1:
            self._current_sync_info = database.get_board_sync_info(self.board_id, self.db_path)

        self.sync_finished.emit(res, user_initiated)
        self.sync_status_changed.emit(self._current_sync_info)

        if res.status in ("imported", "merged"):
            self.board_data_reloaded.emit()

        if self._sync_queued:
            self._sync_queued = False
            self.sync_now(user_initiated=False)

    def trigger_auto_sync_export(self):
        """Exporta automáticamente los cambios locales si el tablero está vinculado."""
        if self.board_id and self.board_id != -1 and self.is_linked:
            self.sync_now(user_initiated=False)

    def unlink_current_board(self) -> bool:
        """Desvincula el tablero actual de su archivo compartido."""
        if not self.board_id or self.board_id == -1:
            return False
        database.unlink_board_sync(self.board_id, self.db_path)
        self.set_board(self.board_id, self.db_path)
        return True

    def wait_for_worker(self, timeout_ms: int = 2000):
        """Espera a que termine cualquier hilo de sincronización en ejecución."""
        if self._sync_worker and self._sync_worker.isRunning():
            self._sync_worker.wait(timeout_ms)

    def is_running(self) -> bool:
        """Devuelve True si hay una sincronización en segundo plano activa."""
        return bool(self._sync_worker and self._sync_worker.isRunning())
