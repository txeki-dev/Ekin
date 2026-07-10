import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QWidget, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
import database
import styles
from sidebar import SidebarWidget
from board_view import BoardViewWidget
from version import __version__

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Ekin Kanban - Trello Lite v{__version__}")
        self.setWindowIcon(QIcon("ekin_icon.png"))
        self.resize(1100, 700)
        self.setMinimumSize(850, 500)
        
        # Inicializar base de datos
        database.init_db()
        self.check_onboarding()

        self.init_ui()

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

        # 2. Vista de tablero (BoardView)
        self.board_view = BoardViewWidget(database.DB_NAME, self)
        splitter.addWidget(self.board_view)

        # Proporciones iniciales: 20% para el sidebar, 80% para el tablero
        splitter.setSizes([220, 880])
        splitter.setCollapsible(0, False)  # Evita colapsar completamente el sidebar por arrastre
        
        main_layout.addWidget(splitter)

        # Conectar señales entre sidebar y board_view
        self.sidebar.board_selected.connect(self.board_view.load_board)
        
        # Si cambia algo en los tableros, recargamos el estado
        self.sidebar.board_changed.connect(self.on_board_changed)

        # Conectar señal de colapso de la barra lateral
        self.board_view.toggle_sidebar_requested.connect(self.toggle_sidebar)

        # Cargar tablero seleccionado inicial (se maneja automáticamente por reload_boards() en la sidebar)
        if self.sidebar.active_board_id:
            self.board_view.load_board(self.sidebar.active_board_id)

    def on_board_changed(self):
        """Manejador si el tablero actual cambió en el sidebar."""
        # Si no queda ningún tablero activo
        if self.sidebar.active_board_id is None:
            self.board_view.load_board(-1)

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
            prog_id = database.create_column(board_id, "En Progreso", "#fbbf24")  # Amarillo/Ambar
            done_id = database.create_column(board_id, "Completado", "#34d399")   # Verde esmeralda
            
            # Crear una tarea de ejemplo
            task_id = database.create_task(
                todo_id,
                "Explorar Ekin Kanban",
                "¡Bienvenido!\n\nEsta es una tarjeta de tarea. Haz click sobre ella para:\n"
                "- Cambiar el título\n"
                "- Añadir una descripción\n"
                "- Configurar etiquetas personalizadas\n"
                "- Registrar tus avances en el Diario personal (a la derecha)",
                "Prioridad Alta",
                "#ef4444"
            )
            
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
    app.setWindowIcon(QIcon("ekin_icon.png"))

    # Aplicar hoja de estilos QSS global
    app.setStyleSheet(styles.QSS)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
