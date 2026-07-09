from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QInputDialog, QMessageBox, QDialog, QLineEdit, QColorDialog
)
import database
import styles
from widgets import ColumnWidget, TaskCard
from detail_dialog import TaskDetailDialog

class ColumnEditDialog(QDialog):
    """Diálogo para crear o editar una columna (nombre y color)."""
    def __init__(self, title="Editar Columna", name="", color="#3b82f6", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 180)
        self.color = color

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Nombre de la columna
        layout.addWidget(QLabel("<b>Nombre de la Columna:</b>"))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText("Ej. Pendientes, En Proceso...")
        layout.addWidget(self.name_input)

        # Color de la columna
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("<b>Color de Acento:</b>"))
        
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(40, 24)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self.choose_color)
        self.update_color_btn_style()
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        layout.addLayout(color_layout)
        layout.addStretch()

        # Botones OK / Cancelar
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
        color = QColorDialog.getColor(self.color, self, "Seleccionar Color de Columna")
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
            QMessageBox.warning(self, "Atención", "El nombre de la columna no puede estar vacío.")
            return
        self.accept()

    def get_data(self):
        return self.name_input.text().strip(), self.color


def hex_to_rgb(hex_str):
    """Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


class BoardViewWidget(QFrame):
    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.board_id = None
        self.column_widgets = {}  # Guarda referencia a {column_id: ColumnWidget}
        self.setObjectName("BoardViewWidget")
        
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Contenedor de bienvenida (se muestra si no hay tableros)
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel(
            "💻 ¡Bienvenido a Ekin Kanban!\n\n"
            "Crea tu primer tablero en el panel lateral\n"
            "para empezar a organizar tus tareas y diarios."
        )
        welcome_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {styles.COLORS['text_muted']};
                font-weight: bold;
                line-height: 150%;
            }}
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(welcome_label)
        self.main_layout.addWidget(self.welcome_widget)

        # 2. Contenedor de Tablero Activo (Scroll horizontal para columnas)
        self.board_scroll_area = QScrollArea()
        self.board_scroll_area.setWidgetResizable(True)
        self.board_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.board_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.board_scroll_area.setStyleSheet("background-color: transparent; border: none;")
        
        self.board_content = QWidget()
        self.board_content.setObjectName("BoardViewContent")
        self.board_content.setStyleSheet("background-color: transparent;")
        
        self.columns_layout = QHBoxLayout(self.board_content)
        self.columns_layout.setContentsMargins(15, 15, 15, 15)
        self.columns_layout.setSpacing(15)
        self.columns_layout.setAlignment(Qt.AlignLeft)
        
        self.board_scroll_area.setWidget(self.board_content)
        self.main_layout.addWidget(self.board_scroll_area)
        
        # Por defecto ocultamos la zona del tablero hasta cargar uno
        self.board_scroll_area.hide()

    def load_board(self, board_id):
        """Carga las columnas y tareas de un tablero específico."""
        self.board_id = board_id
        
        if board_id == -1:
            # Mostrar pantalla de bienvenida
            self.board_scroll_area.hide()
            self.welcome_widget.show()
            self.clear_columns_layout()
            self.setStyleSheet("")
            return

        # Ocultar bienvenida y mostrar scroll area
        self.welcome_widget.hide()
        self.board_scroll_area.show()
        
        self.clear_columns_layout()

        # Obtener información del tablero (incluyendo el color)
        board_info = database.get_board(board_id, self.db_path)
        if board_info:
            board_color = board_info["color"]
            try:
                r, g, b = hex_to_rgb(board_color)
            except Exception:
                r, g, b = 15, 23, 42
            
            # Aplicamos un fondo uniforme de color continuo (mezcla sutil de 6% opacidad)
            self.setStyleSheet(f"""
                #BoardViewWidget {{
                    background-color: rgba({r}, {g}, {b}, 0.06);
                }}
            """)
        else:
            self.setStyleSheet("")

        # Obtener columnas de la DB
        columns = database.get_columns(board_id, self.db_path)
        
        for col_data in columns:
            col_widget = ColumnWidget(col_data, self)
            col_widget.setFixedWidth(280)  # Ancho estándar para columnas Kanban
            
            # Conectar señales
            col_widget.task_dropped.connect(self.handle_task_drop)
            col_widget.add_task_requested.connect(self.add_task)
            col_widget.edit_column_requested.connect(self.edit_column)
            col_widget.delete_column_requested.connect(self.delete_column)

            # Cargar tareas de la columna
            tasks = database.get_tasks(col_data["id"], self.db_path)
            for task_data in tasks:
                card = TaskCard(task_data, self)
                if board_info:
                    card.set_card_style(board_color)
                card.clicked.connect(self.open_task_details)
                col_widget.add_task_card(card)

            self.columns_layout.addWidget(col_widget)
            self.column_widgets[col_data["id"]] = col_widget

        # Añadir el botón "+ Añadir Columna" al final
        self.add_column_card = QFrame()
        self.add_column_card.setFixedWidth(280)
        self.add_column_card.setObjectName("ColumnContainer")
        self.add_column_card.setStyleSheet(f"""
            #ColumnContainer {{
                background-color: transparent;
                border: 2px dashed {styles.COLORS['border']};
                border-radius: 10px;
            }}
            #ColumnContainer:hover {{
                border-color: {styles.COLORS['accent_blue']};
            }}
        """)
        
        add_col_layout = QVBoxLayout(self.add_column_card)
        add_col_layout.setAlignment(Qt.AlignCenter)
        
        add_col_btn = QPushButton("➕ Nueva Columna")
        add_col_btn.setObjectName("PrimaryButton")
        add_col_btn.setCursor(Qt.PointingHandCursor)
        add_col_btn.clicked.connect(self.add_column)
        add_col_layout.addWidget(add_col_btn)
        
        self.columns_layout.addWidget(self.add_column_card)

    def clear_columns_layout(self):
        """Limpia todos los widgets del layout de columnas."""
        self.column_widgets.clear()
        while self.columns_layout.count():
            item = self.columns_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # --- ACCIONES DE COLUMNAS ---

    def add_column(self):
        """Abre el diálogo para crear una columna."""
        if not self.board_id:
            return
        
        dialog = ColumnEditDialog("Nueva Columna", name="", color="#3b82f6", parent=self)
        if dialog.exec() == QDialog.Accepted:
            name, color = dialog.get_data()
            database.create_column(self.board_id, name, color, self.db_path)
            self.load_board(self.board_id)

    def edit_column(self, column_id):
        """Abre el diálogo para editar nombre y color de una columna."""
        col_widget = self.column_widgets.get(column_id)
        if not col_widget:
            return

        dialog = ColumnEditDialog(
            "Editar Columna",
            name=col_widget.column_data["name"],
            color=col_widget.column_data["color"],
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            name, color = dialog.get_data()
            database.update_column(column_id, name, color, self.db_path)
            self.load_board(self.board_id)

    def delete_column(self, column_id):
        """Confirma y borra una columna."""
        col_widget = self.column_widgets.get(column_id)
        if not col_widget:
            return

        confirm = QMessageBox.question(
            self,
            "Eliminar Columna",
            f"¿Estás seguro de eliminar la columna '{col_widget.column_data['name']}'?\nEsto borrará todas sus tareas de forma permanente.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_column(column_id, self.db_path)
            self.load_board(self.board_id)

    # --- ACCIONES DE TAREAS ---

    def add_task(self, column_id):
        """Crea una tarea solicitando el título rápidamente."""
        title, ok = QInputDialog.getText(
            self, "Nueva Tarea", "Introduce el título de la tarea:",
            text=""
        )
        if ok and title.strip():
            database.create_task(column_id, title.strip(), db_path=self.db_path)
            self.load_board(self.board_id)

    def open_task_details(self, task_id):
        """Abre el diálogo de detalle/chat de una tarea."""
        dialog = TaskDetailDialog(task_id, self.db_path, self)
        dialog.exec()
        
        # Al cerrarse el diálogo, refrescamos el tablero completo por si hubo
        # cambios en el título, descripción, etiquetas o si se eliminó la tarea.
        self.load_board(self.board_id)

    # --- DRAG & DROP DE TAREAS ---

    def handle_task_drop(self, task_id, target_column_id, target_position):
        """Maneja la lógica de recolocación de tareas tras arrastrarlas."""
        task_data = database.get_task(task_id, self.db_path)
        if not task_data:
            return

        source_column_id = task_data["column_id"]

        # 1. Obtener todas las tareas de la columna origen
        source_tasks = database.get_tasks(source_column_id, self.db_path)
        
        # 2. Obtener todas las tareas de la columna destino (si es distinta)
        if source_column_id != target_column_id:
            target_tasks = database.get_tasks(target_column_id, self.db_path)
        else:
            target_tasks = source_tasks

        # Remover la tarea que se está moviendo de la lista de origen
        moved_task = None
        for t in source_tasks:
            if t["id"] == task_id:
                moved_task = t
                source_tasks.remove(t)
                break
        
        if not moved_task:
            return

        # Insertar la tarea en la nueva posición de la columna de destino
        # Asegurar que el índice no exceda los límites
        insert_idx = min(max(0, target_position), len(target_tasks))
        
        if source_column_id == target_column_id:
            # Reinsertar en la misma lista
            source_tasks.insert(insert_idx, moved_task)
            
            # Generar updates para escribir en DB
            updates = []
            for i, task in enumerate(source_tasks):
                updates.append((task["id"], source_column_id, i))
        else:
            # Insertar en la lista destino
            target_tasks.insert(insert_idx, moved_task)
            
            updates = []
            # Updates para origen
            for i, task in enumerate(source_tasks):
                updates.append((task["id"], source_column_id, i))
            # Updates para destino
            for i, task in enumerate(target_tasks):
                updates.append((task["id"], target_column_id, i))

        # 3. Guardar las nuevas posiciones en la base de datos
        database.update_task_positions(updates, self.db_path)

        # 4. Recargar el tablero para actualizar la UI con la base de datos como fuente de verdad
        self.load_board(self.board_id)
