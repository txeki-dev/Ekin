import sys
import os
import subprocess
from datetime import date
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QWidget, QHBoxLayout, QMessageBox,
    QStackedWidget, QSystemTrayIcon, QMenu
)
from PySide6.QtCore import Qt, QTimer, QByteArray
from PySide6.QtGui import QIcon, QShortcut, QKeySequence
import database
import backups
import styles
from sidebar import SidebarWidget
from board_view import BoardViewWidget
from calendar_view import CalendarViewWidget
from detail_dialog import TaskDetailDialog
from search_dialog import SearchDialog
from settings_dialog import SettingsDialog
from undo import UndoManager
import ics_export
from version import __version__

# Directorio de la app: los iconos deben resolverse por ruta ABSOLUTA. Con ruta relativa,
# al lanzar desde el acceso directo (con otro directorio de trabajo) QIcon no carga el
# archivo y Windows cae al icono genérico de python en la barra de tareas.
_APP_DIR = os.path.dirname(os.path.abspath(__file__))


def app_icon():
    """Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de tareas)."""
    ico = os.path.join(_APP_DIR, "ekin_icon.ico")
    if os.path.exists(ico):
        return QIcon(ico)
    return QIcon(os.path.join(_APP_DIR, "ekin_icon.png"))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Ekin Kanban - Trello Lite v{__version__}")
        self.setWindowIcon(app_icon())
        self.resize(1100, 700)
        self.setMinimumSize(850, 500)
        
        # Copia de seguridad automática ANTES de inicializar (así se guarda una
        # instantánea previa a cualquier migración de esquema). No-op en el primer
        # arranque, cuando la base de datos aún no existe.
        try:
            backups.backup_database(database.DB_NAME)
        except Exception as exc:
            print(f"No se pudo crear la copia de seguridad: {exc}")

        # Inicializar base de datos
        database.init_db()
        # Adelantar tareas recurrentes vencidas a su próxima ocurrencia
        try:
            database.advance_overdue_recurring(date.today().isoformat())
        except Exception as exc:
            print(f"No se pudieron adelantar tareas recurrentes: {exc}")
        self.check_onboarding()

        # Contenido del último .ics sincronizado (para no reescribir si no cambió nada)
        self._last_synced_ics = None

        # Gestor de deshacer/rehacer (borrados)
        self.undo_manager = UndoManager()

        self.init_ui()
        self.board_view.undo_manager = self.undo_manager
        self.sidebar.undo_manager = self.undo_manager

        # Tema guardado + geometría de ventana recordada
        self.apply_theme(database.get_setting("theme", "dark"), reload=False)
        self._restore_geometry()

        # Bandeja del sistema + notificaciones nativas de Windows
        self._last_notified = None
        self.setup_tray()
        QTimer.singleShot(1500, self.notify_due_today)
        self._notify_timer = QTimer(self)
        self._notify_timer.timeout.connect(self._maybe_notify_new_day)
        self._notify_timer.start(60 * 60 * 1000)  # revisión horaria (por cambio de día)

        # Reescritura de seguridad del .ics cada 5 min mientras la app está abierta.
        # sync_ics() solo escribe si el contenido ha cambiado, así que es una red de
        # seguridad barata frente a cualquier cambio que no pasara por load_board.
        self._sync_timer = QTimer(self)
        self._sync_timer.timeout.connect(self.sync_ics)
        self._sync_timer.start(5 * 60 * 1000)

        # Atajo global de búsqueda (Ctrl+F)
        self._search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self._search_shortcut.activated.connect(self.show_search)

        # Ctrl+N: nueva tarea en la primera columna del tablero activo
        self._new_task_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self._new_task_shortcut.activated.connect(self.board_view.quick_add_task)

        # Deshacer / rehacer borrados (Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._do_undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self._do_redo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self._do_redo)

        # Comprobar actualizaciones tras 1 segundo
        QTimer.singleShot(1000, self.check_for_updates)

    def init_ui(self):
        # Widget y layout central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Usamos un QSplitter para permitir redimensionar la barra lateral y el tablero
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {styles.COLORS['border']};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
        """)

        # 1. Panel lateral (Sidebar)
        self.sidebar = SidebarWidget(database.DB_NAME, self)
        splitter.addWidget(self.sidebar)

        # 2. Área central conmutable: vista de tablero <-> vista de calendario
        self.board_view = BoardViewWidget(database.DB_NAME, self)
        self.calendar_view = CalendarViewWidget(database.DB_NAME, self)

        self.center_stack = QStackedWidget()
        self.center_stack.addWidget(self.board_view)     # índice 0
        self.center_stack.addWidget(self.calendar_view)  # índice 1
        splitter.addWidget(self.center_stack)

        # Proporciones iniciales: 20% para el sidebar, 80% para el tablero
        splitter.setSizes([220, 880])
        splitter.setCollapsible(0, False)  # Evita colapsar completamente el sidebar por arrastre

        main_layout.addWidget(splitter)

        # Conectar señales entre sidebar y board_view
        # notify=False: cambiar de tablero es navegación, no una mutación de datos.
        self.sidebar.board_selected.connect(
            lambda board_id: self.board_view.load_board(board_id, notify=False)
        )

        # Si cambia algo en los tableros, recargamos el estado
        self.sidebar.board_changed.connect(self.on_board_changed)

        # Conectar señal de colapso de la barra lateral
        self.board_view.toggle_sidebar_requested.connect(self.toggle_sidebar)

        # Campana de vencimientos y vista de calendario
        self.sidebar.open_calendar_requested.connect(self.show_calendar_view)
        self.sidebar.open_search_requested.connect(self.show_search)
        self.sidebar.open_settings_requested.connect(self.show_settings)
        self.sidebar.open_task_requested.connect(self.on_notification_task)
        self.calendar_view.close_requested.connect(self.show_board_view)
        self.calendar_view.task_activated.connect(self.on_calendar_task)
        # Reprogramar una tarea arrastrándola en el calendario refresca campana y .ics
        self.calendar_view.data_changed.connect(self.sidebar.refresh_notifications)
        self.calendar_view.data_changed.connect(self.sync_ics)

        # Cuando el tablero (re)carga datos, refrescar campana, calendario y el .ics sincronizado
        self.board_view.data_changed.connect(self.sidebar.refresh_notifications)
        self.board_view.data_changed.connect(self.calendar_view.refresh)
        self.board_view.data_changed.connect(self.sync_ics)

        # Cargar tablero seleccionado inicial (se maneja automáticamente por reload_boards() en la sidebar)
        if self.sidebar.active_board_id:
            self.board_view.load_board(self.sidebar.active_board_id, notify=False)

    def on_board_changed(self):
        """Manejador si el tablero actual cambió en el sidebar."""
        # Si no queda ningún tablero activo
        if self.sidebar.active_board_id is None:
            self.board_view.load_board(-1)

    # --- Conmutación entre vista de tablero y calendario ---

    def show_calendar_view(self):
        self.calendar_view.refresh()
        self.center_stack.setCurrentWidget(self.calendar_view)

    def show_board_view(self):
        self.center_stack.setCurrentWidget(self.board_view)

    def show_search(self):
        """Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta."""
        dialog = SearchDialog(database.DB_NAME, self)
        dialog.task_activated.connect(self.on_notification_task)
        dialog.exec()

    def apply_theme(self, theme, reload=True):
        """Aplica el tema (oscuro/claro) al vuelo. `reload` recarga el tablero para que
        las tarjetas/columnas se reconstruyan con la nueva paleta."""
        QApplication.instance().setStyleSheet(styles.set_theme(theme))
        if reload and self.sidebar.active_board_id:
            self.board_view.load_board(self.sidebar.active_board_id, notify=False)

    def show_settings(self):
        """Abre la pantalla de Ajustes (tema, notificaciones)."""
        dlg = SettingsDialog(database.DB_NAME, self)
        dlg.theme_changed.connect(lambda t: self.apply_theme(t, reload=True))
        dlg.exec()

    def _do_undo(self):
        if self.undo_manager.undo():
            self.sidebar.refresh_notifications()
            self.sync_ics()

    def _do_redo(self):
        if self.undo_manager.redo():
            self.sidebar.refresh_notifications()
            self.sync_ics()

    def _restore_geometry(self):
        geo = database.get_setting("window_geometry", "")
        if geo:
            try:
                self.restoreGeometry(QByteArray.fromBase64(geo.encode("ascii")))
            except Exception:
                pass

    def closeEvent(self, event):
        try:
            database.set_setting(
                "window_geometry", bytes(self.saveGeometry().toBase64()).decode("ascii")
            )
        except Exception:
            pass
        super().closeEvent(event)

    def _open_task_detail(self, task_id):
        """Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo
        modificó o borró la tarea (para que el llamante decida si refrescar)."""
        dialog = TaskDetailDialog(task_id, database.DB_NAME, self)
        dialog.exec()
        return getattr(dialog, "modified", False) or getattr(dialog, "task_deleted", False)

    def on_notification_task(self, task_id, board_id):
        """Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle."""
        self.show_board_view()
        if board_id and self.sidebar.active_board_id != board_id:
            self.sidebar.select_board(board_id)
        changed = self._open_task_detail(task_id)
        # Refrescar la vista actual y los indicadores solo si hubo cambios reales
        if changed:
            if self.sidebar.active_board_id:
                self.board_view.load_board(self.sidebar.active_board_id)
            self.sidebar.refresh_notifications()

    def on_calendar_task(self, task_id, board_id):
        """Desde el calendario: abrir el detalle y quedarnos en el calendario."""
        changed = self._open_task_detail(task_id)
        if changed:
            self.calendar_view.refresh()
            self.sidebar.refresh_notifications()
            self.sync_ics()

    def sync_ics(self):
        """Si hay una ruta de sincronización configurada, reescribe el .ics (feed suscribible).
        Solo escribe cuando el contenido ha cambiado, para no generar subidas redundantes
        en carpetas de Dropbox/OneDrive/Drive."""
        path = database.get_setting("ics_sync_path", "")
        if not path:
            return
        try:
            content = ics_export.build_ics(database.DB_NAME)
            if content == self._last_synced_ics:
                return
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            self._last_synced_ics = content
        except Exception as exc:
            print(f"Error al sincronizar el .ics: {exc}")

    # --- Bandeja del sistema y notificaciones ---

    def setup_tray(self):
        """Crea el icono de bandeja (habilita toasts nativos de Windows)."""
        self.tray = QSystemTrayIcon(app_icon(), self)
        self.tray.setToolTip("Ekin Kanban")

        menu = QMenu()
        styles.style_menu(menu)
        open_action = menu.addAction("Abrir Ekin")
        open_action.triggered.connect(self.show_and_raise)
        menu.addSeparator()
        quit_action = menu.addAction("Salir")
        quit_action.triggered.connect(QApplication.quit)
        self.tray.setContextMenu(menu)

        self.tray.activated.connect(self._on_tray_activated)
        self.tray.messageClicked.connect(self._on_toast_clicked)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or \
           reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_and_raise()

    def _on_toast_clicked(self):
        self.show_and_raise()
        self.sidebar.show_notifications()

    def show_and_raise(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def notify_due_today(self):
        """Muestra un toast de Windows con las tareas que vencen hoy (si las hay)."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        if database.get_setting("notifications_enabled", "1") == "0":
            return
        today = date.today().isoformat()
        tasks = database.get_scheduled_tasks(today, today)
        self._last_notified = date.today()
        if not tasks:
            return
        titles = ", ".join(t["title"] for t in tasks[:5])
        if len(tasks) > 5:
            titles += "…"
        self.tray.showMessage(
            f"Ekin — {len(tasks)} tarea(s) vencen hoy",
            titles,
            QSystemTrayIcon.MessageIcon.Information,
            8000
        )

    def _maybe_notify_new_day(self):
        """Con la revisión horaria, notifica de nuevo si ha cambiado el día."""
        if self._last_notified != date.today():
            self.notify_due_today()

    def toggle_sidebar(self):
        """Muestra u oculta la barra lateral."""
        self.sidebar.setVisible(not self.sidebar.isVisible())

    def check_for_updates(self):
        """Verifica de forma silenciosa si hay actualizaciones en el repo de GitHub."""
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # Ocultar ventana de comandos de cmd
                
            # 1. Ejecutar git fetch para actualizar referencias de forma silenciosa
            subprocess.run(
                ["git", "fetch", "origin"],
                startupinfo=startupinfo,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # 2. Ejecutar git status -uno para ver el estado local vs remoto
            result = subprocess.run(
                ["git", "status", "-uno"],
                startupinfo=startupinfo,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Si la salida contiene "behind", significa que estamos desactualizados
            if "behind" in result.stdout:
                confirm = QMessageBox.question(
                    self,
                    "Actualización Disponible",
                    "Hay una nueva versión de Ekin Kanban en GitHub.\n¿Deseas descargarla y reiniciar la aplicación ahora?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if confirm == QMessageBox.Yes:
                    # Ejecutar git pull origin main para descargar cambios
                    subprocess.run(
                        ["git", "pull", "origin", "main"],
                        startupinfo=startupinfo,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    QMessageBox.information(
                        self,
                        "Actualizado",
                        "La aplicación se ha actualizado con éxito. Se reiniciará ahora."
                    )
                    
                    # Reiniciar el script actual de python
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                    sys.exit(0)
        except Exception as e:
            # Fallar en silencio si no hay conexión o no es una instalación Git
            print(f"Error al comprobar actualizaciones: {e}")

    def check_onboarding(self):
        """Verifica si es la primera vez que se abre la app y crea datos de ejemplo."""
        boards = database.get_boards()
        if not boards:
            # Crear tablero inicial de ejemplo
            board_id = database.create_board("Mi Primer Tablero")
            
            # Crear columnas de ejemplo
            todo_id = database.create_column(board_id, "Pendientes", "#60a5fa")  # Azul claro
            database.create_column(board_id, "En Progreso", "#fbbf24")  # Amarillo/Ambar
            database.create_column(board_id, "Completado", "#34d399")   # Verde esmeralda
            
            # Crear una tarea de ejemplo
            task_id = database.create_task(
                todo_id,
                "Explorar Ekin Kanban",
                "¡Bienvenido!\n\nEsta es una tarjeta de tarea. Haz click sobre ella para:\n"
                "- Cambiar el título\n"
                "- Añadir una descripción\n"
                "- Configurar etiquetas personalizadas\n"
                "- Registrar tus avances en el Diario personal (a la derecha)"
            )

            # Asignar una etiqueta de ejemplo (Categoría: Valor)
            priority_tag_id = database.get_or_create_tag_value("Prioridad", "Alta", "#ef4444")
            database.set_task_tags(task_id, [priority_tag_id])

            # Añadir una nota de diario inicial a la tarea
            database.create_log(
                task_id,
                "He inicializado la aplicación por primera vez. ¡Todo listo para empezar a trabajar!"
            )


def main():
    if os.name == 'nt':
        # En Windows, pythonw.exe agrupa la ventana bajo su propio icono genérico en la
        # barra de tareas a menos que el proceso declare un AppUserModelID propio.
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EkinKanban.TrelloLite")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setWindowIcon(app_icon())

    # Aplicar hoja de estilos QSS global
    app.setStyleSheet(styles.QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
