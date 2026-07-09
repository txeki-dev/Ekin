from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QMessageBox, QDialog, QLineEdit, QColorDialog
)
from PySide6.QtGui import QColor
import database
import styles

def hex_to_rgb(hex_str):
    """Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


class BoardButton(QFrame):
    """Widget personalizado para representar un botón de tablero en la barra lateral."""
    clicked = Signal(int)  # Emite el board_id cuando se pulsa

    def __init__(self, board_id, name, color, active=False, parent=None):
        super().__init__(parent)
        self.board_id = board_id
        self.name = name
        self.color = color
        self.active = active
        
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(6)
        
        self.label = QLabel(self.name)
        self.label.setStyleSheet("font-weight: bold; background: transparent; border: none; color: inherit;")
        self.label.setWordWrap(False)
        layout.addWidget(self.label)
        layout.addStretch()
        
        self.update_style()

    def update_style(self):
        try:
            r, g, b = hex_to_rgb(self.color)
        except Exception:
            r, g, b = 59, 130, 246  # Azul por defecto si falla el parseo
            
        if self.active:
            # Color original vibrante y texto blanco
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgb({r}, {g}, {b});
                    border: 1.5px solid rgb({r}, {g}, {b});
                    border-radius: 6px;
                    color: #ffffff;
                }}
            """)
        else:
            # Estado "Grey Out" con el color original como un tinte suave (12% opacidad)
            # y un borde coloreado al 40% de opacidad. El texto está desaturado.
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba({r}, {g}, {b}, 0.12);
                    border: 1.5px solid rgba({r}, {g}, {b}, 0.4);
                    border-radius: 6px;
                    color: #94a3b8;
                }}
                QFrame:hover {{
                    background-color: rgba({r}, {g}, {b}, 0.25);
                    border-color: rgba({r}, {g}, {b}, 0.7);
                    color: #f8fafc;
                }}
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.board_id)
        super().mousePressEvent(event)


class BoardEditDialog(QDialog):
    """Diálogo personalizado para crear o editar un tablero (nombre y color de fondo)."""
    def __init__(self, title="Editar Tablero", name="", color="#3b82f6", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 180)
        self.color = color

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Nombre del Tablero
        layout.addWidget(QLabel("<b>Nombre del Tablero:</b>"))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Ej. Trabajo, Personal, Viaje...")
        layout.addWidget(self.name_input)

        # Color del Tablero
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("<b>Color de Fondo:</b>"))
        
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(40, 24)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self.choose_color)
        self.update_color_btn_style()
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        layout.addLayout(color_layout)
        layout.addStretch()

        # Botones Guardar / Cancelar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("Guardar")
        self.ok_btn.setObjectName("PrimaryButton")
        self.ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color), self, "Seleccionar Color del Tablero")
        if color.isValid():
            self.color = color.name()
            self.update_color_btn_style()

    def update_color_btn_style(self):
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #ffffff;
            }}
        """)

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Atención", "El nombre del tablero no puede estar vacío.")
            return
        self.accept()

    def get_data(self):
        return self.name_input.text().strip(), self.color


class SidebarWidget(QFrame):
    board_selected = Signal(int)  # Emite el board_id seleccionado
    board_changed = Signal()      # Emite cuando se añade/edita/borra un tablero

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.active_board_id = None
        self.board_buttons = {}  # Guarda referencia a {board_id: BoardButton}
        
        self.setObjectName("SidebarFrame")
        self.init_ui()
        self.reload_boards()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        # Título del panel
        title_label = QLabel("EKIN KANBAN")
        title_label.setObjectName("SidebarTitle")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("Mis Tableros")
        subtitle_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-weight: bold; margin-left: 8px;")
        layout.addWidget(subtitle_label)

        # Contenedor con Scroll para albergar los botones de tableros
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.boards_layout = QVBoxLayout(self.scroll_content)
        self.boards_layout.setContentsMargins(4, 4, 4, 4)
        self.boards_layout.setSpacing(8)
        self.boards_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # Botones de control en la parte inferior
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        # Botón para añadir tablero
        self.add_btn = QPushButton("➕ Nuevo Tablero")
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self.add_board)
        btn_layout.addWidget(self.add_btn)

        # Fila de acciones (Editar, Copiar y Borrar)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(6)

        self.edit_btn = QPushButton("✏️ Editar")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(self.edit_board)
        action_layout.addWidget(self.edit_btn)

        self.copy_btn = QPushButton("📋 Copiar")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_board)
        action_layout.addWidget(self.copy_btn)

        self.delete_btn = QPushButton("🗑️ Borrar")
        self.delete_btn.setObjectName("DangerButton")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self.delete_board)
        action_layout.addWidget(self.delete_btn)

        btn_layout.addLayout(action_layout)
        layout.addLayout(btn_layout)

    def reload_boards(self, select_board_id=None):
        """Vuelve a cargar la lista de tableros como widgets personalizados desde la base de datos."""
        # Limpiar contenedor anterior
        self.board_buttons.clear()
        while self.boards_layout.count():
            item = self.boards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        boards = database.get_boards(self.db_path)
        
        if not boards:
            self.active_board_id = None
            self.board_selected.emit(-1)
            return

        # Si no hay un id seleccionado específico pero había uno activo, intentamos mantenerlo
        if select_board_id is None:
            if self.active_board_id and any(b["id"] == self.active_board_id for b in boards):
                select_board_id = self.active_board_id
            else:
                # Si no, seleccionamos el primero de la lista
                select_board_id = boards[0]["id"]

        self.active_board_id = select_board_id

        # Crear y añadir los botones
        for board in boards:
            board_id = board["id"]
            is_active = (board_id == self.active_board_id)
            
            btn = BoardButton(board_id, board["name"], board["color"], active=is_active, parent=self)
            btn.clicked.connect(self.select_board)
            self.boards_layout.addWidget(btn)
            self.board_buttons[board_id] = btn

        # Emitir la selección del tablero activo para que la vista del tablero se cargue
        self.board_selected.emit(self.active_board_id)

    def select_board(self, board_id):
        """Cambia el tablero activo, actualiza los estilos visuales de los botones y emite la señal."""
        if self.active_board_id == board_id:
            return

        # Desactivar el botón anteriormente activo
        if self.active_board_id in self.board_buttons:
            self.board_buttons[self.active_board_id].active = False
            self.board_buttons[self.active_board_id].update_style()

        # Activar el nuevo botón
        self.active_board_id = board_id
        if self.active_board_id in self.board_buttons:
            self.board_buttons[self.active_board_id].active = True
            self.board_buttons[self.active_board_id].update_style()

        self.board_selected.emit(board_id)

    def add_board(self):
        """Abre el diálogo para crear un nuevo tablero con nombre y color."""
        dialog = BoardEditDialog("Nuevo Tablero", name="", color="#3b82f6", parent=self)
        if dialog.exec() == QDialog.Accepted:
            name, color = dialog.get_data()
            board_id = database.create_board(name, color, self.db_path)
            self.reload_boards(select_board_id=board_id)
            self.board_changed.emit()

    def edit_board(self):
        """Abre el diálogo para editar el nombre y color del tablero activo."""
        if not self.active_board_id or self.active_board_id not in self.board_buttons:
            return

        active_btn = self.board_buttons[self.active_board_id]
        
        dialog = BoardEditDialog(
            "Editar Tablero",
            name=active_btn.name,
            color=active_btn.color,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            name, color = dialog.get_data()
            database.update_board(self.active_board_id, name, color, self.db_path)
            self.reload_boards(select_board_id=self.active_board_id)
            self.board_changed.emit()

    def copy_board(self):
        """Abre el diálogo para copiar el tablero activo con un nuevo nombre."""
        if not self.active_board_id or self.active_board_id not in self.board_buttons:
            return

        active_btn = self.board_buttons[self.active_board_id]
        
        dialog = BoardEditDialog(
            "Copiar Tablero",
            name=f"{active_btn.name} - Copia",
            color=active_btn.color,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            name, color = dialog.get_data()
            new_board_id = database.copy_board(self.active_board_id, name, color, self.db_path)
            self.reload_boards(select_board_id=new_board_id)
            self.board_changed.emit()

    def delete_board(self):
        """Confirma y elimina el tablero activo."""
        if not self.active_board_id or self.active_board_id not in self.board_buttons:
            return

        board_name = self.board_buttons[self.active_board_id].name

        confirm = QMessageBox.question(
            self,
            "Eliminar Tablero",
            f"¿Estás seguro de eliminar el tablero '{board_name}'?\nEsto borrará todas sus columnas, tareas y diarios asociados de forma permanente.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_board(self.active_board_id, self.db_path)
            self.active_board_id = None
            self.reload_boards()
            self.board_changed.emit()
