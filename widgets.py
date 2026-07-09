from PySide6.QtCore import Qt, QMimeData, QPoint, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QMenu, QApplication
)
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QCursor
import styles

def hex_to_rgb(hex_str):
    """Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


class TaskCard(QFrame):
    # Emitido cuando se hace click en la tarjeta (y no se ha arrastrado)
    clicked = Signal(int)  # task_id

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data["id"]
        self.drag_start_position = QPoint()
        self.board_color_hex = "#3b82f6"
        
        self.setObjectName("TaskCardFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.init_ui()

    def set_card_style(self, board_color_hex):
        """Aplica dinámicamente el estilo a la tarjeta basándose en el color de fondo del tablero."""
        self.board_color_hex = board_color_hex
        
        # Color base Slate 900 de la ventana (#0f172a)
        base_r, base_g, base_b = 15, 23, 42
        try:
            r, g, b = hex_to_rgb(board_color_hex)
        except Exception:
            r, g, b = 59, 130, 246
            
        alpha = 0.06
        blend_r = int(base_r * (1 - alpha) + r * alpha)
        blend_g = int(base_g * (1 - alpha) + g * alpha)
        blend_b = int(base_b * (1 - alpha) + b * alpha)
        
        # Marco sólido Slate 600 y fondo idéntico al fondo del tablero
        self.setStyleSheet(f"""
            #TaskCardFrame {{
                background-color: rgb({blend_r}, {blend_g}, {blend_b});
                border: 1.5px solid #475569;
                border-radius: 8px;
            }}
            #TaskCardFrame:hover {{
                border: 1.5px solid #3b82f6;
                background-color: rgb({min(255, blend_r + 12)}, {min(255, blend_g + 12)}, {min(255, blend_b + 16)});
            }}
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Título de la tarea
        self.title_label = QLabel(self.task_data["title"])
        self.title_label.setObjectName("TaskCardTitle")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Indicador de descripción y comentarios / diario
        info_layout = QHBoxLayout()
        info_layout.setSpacing(8)

        # Si hay etiqueta, la añadimos
        self.tag_label = QLabel()
        self.tag_label.setObjectName("TaskCardTag")
        self.update_tag(self.task_data.get("tag_text"), self.task_data.get("tag_color"))
        info_layout.addWidget(self.tag_label)
        
        # Spacer para empujar la etiqueta a la izquierda
        info_layout.addStretch()
        layout.addLayout(info_layout)

    def update_tag(self, text, color):
        """Actualiza la etiqueta de la tarea en la interfaz."""
        if text:
            self.tag_label.setText(text.upper())
            self.tag_label.setStyleSheet(
                f"background-color: {color}; color: #ffffff; font-weight: bold; border-radius: 4px; padding: 2px 6px;"
            )
            self.tag_label.show()
        else:
            self.tag_label.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Iniciamos el arrastre (Drag)
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Codificamos el ID de la tarea en formato binario
        mime_data.setData("application/x-ekin-task-id", str(self.task_id).encode("utf-8"))
        # Guardamos el ID de la columna origen
        mime_data.setData("application/x-ekin-source-column-id", str(self.task_data["column_id"]).encode("utf-8"))
        
        drag.setMimeData(mime_data)

        # Generamos una vista preliminar (pixmap) de la tarjeta para mostrarla mientras se arrastra
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        
        # Renderizar directamente sobre el pixmap (es un QPaintDevice)
        self.render(pixmap)
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        # Ocultar la tarjeta original mientras arrastramos
        self.hide()
        
        # Ejecutar la acción drag-and-drop
        drop_action = drag.exec(Qt.MoveAction)
        
        # Si la tarea no se colocó en ningún lado (fue cancelada), volvemos a mostrarla
        if drop_action == Qt.IgnoreAction:
            self.show()

    def mouseReleaseEvent(self, event):
        # Si se soltó el click izquierdo y no se inició drag, se considera un click normal
        if event.button() == Qt.LeftButton:
            click_dist = (event.position().toPoint() - self.drag_start_position).manhattanLength()
            if click_dist < QApplication.startDragDistance():
                self.clicked.emit(self.task_id)
        super().mouseReleaseEvent(event)


class TaskListArea(QWidget):
    # Se emite cuando se completa el drop de una tarea
    # Parámetros: (task_id, target_column_id, position)
    task_dropped = Signal(int, int, int)
    # Se emite cuando una tarea arrastrada entra en esta área
    drag_entered = Signal()
    # Se emite cuando el arrastre sale del área
    drag_left = Signal()

    def __init__(self, column_id, parent=None):
        super().__init__(parent)
        self.column_id = column_id
        self.setAcceptDrops(True)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 10)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignTop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
            self.drag_entered.emit()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drag_left.emit()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasFormat("application/x-ekin-task-id"):
            task_id = int(mime.data("application/x-ekin-task-id").data().decode("utf-8"))
            event.acceptProposedAction()
            self.drag_left.emit()
            
            # Calcular la posición de inserción en base al eje Y
            drop_y = event.position().y()
            target_pos = 0
            
            # Iterar sobre las tarjetas existentes en el layout para ver dónde encajar la nueva
            for i in range(self.layout.count()):
                widget = self.layout.itemAt(i).widget()
                if widget and isinstance(widget, TaskCard):
                    # Si el drop se hizo por encima de la mitad de esta tarjeta
                    card_middle = widget.y() + (widget.height() / 2)
                    if drop_y < card_middle:
                        target_pos = i
                        break
                    else:
                        target_pos = i + 1
            
            self.task_dropped.emit(task_id, self.column_id, target_pos)
        else:
            event.ignore()


class ColumnWidget(QFrame):
    # Señales reenviadas
    task_dropped = Signal(int, int, int) # task_id, column_id, position
    add_task_requested = Signal(int)     # column_id
    edit_column_requested = Signal(int) # column_id
    delete_column_requested = Signal(int) # column_id

    def __init__(self, column_data, parent=None):
        super().__init__(parent)
        self.column_data = column_data
        self.column_id = column_data["id"]
        
        self.setObjectName("ColumnContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.init_ui()

    def init_ui(self):
        # Layout principal de la columna (Vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 1. Cabecera de la columna
        header_widget = QWidget()
        header_widget.setObjectName("ColumnHeaderBar")
        # Aplicamos el color de borde superior correspondiente al color de la columna
        header_widget.setStyleSheet(
            f"#ColumnHeaderBar {{ border-bottom: 3px solid {self.column_data['color']}; padding-bottom: 4px; }}"
        )
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(4)

        # Nombre de la columna
        self.title_label = QLabel(self.column_data["name"])
        self.title_label.setObjectName("ColumnTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Botón de menú para editar/borrar la columna
        self.menu_btn = QPushButton("⋮")
        self.menu_btn.setFixedWidth(24)
        self.menu_btn.setFixedHeight(24)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setStyleSheet("background: transparent; border: none; font-size: 14px; font-weight: bold;")
        self.menu_btn.clicked.connect(self.show_column_menu)
        header_layout.addWidget(self.menu_btn)

        main_layout.addWidget(header_widget)

        # 2. Área scrollable para las tareas
        scroll_area = QScrollArea()
        scroll_area.setObjectName("TaskListArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # El contenedor interno que acepta drops
        self.list_area = TaskListArea(self.column_id)
        self.list_area.task_dropped.connect(self.task_dropped.emit)
        
        # Aplicar el estilo dinámico inicial a la columna
        self.set_column_style(dragging=False)
        
        # Efecto visual al arrastrar sobre esta columna usando su propio color
        self.list_area.drag_entered.connect(lambda: self.set_column_style(dragging=True))
        self.list_area.drag_left.connect(lambda: self.set_column_style(dragging=False))
        
        scroll_area.setWidget(self.list_area)
        main_layout.addWidget(scroll_area)

        # 3. Botón para añadir una nueva tarea
        self.add_task_btn = QPushButton("➕ Añadir Tarea")
        self.add_task_btn.setObjectName("AddTaskButton")
        self.add_task_btn.setCursor(Qt.PointingHandCursor)
        self.add_task_btn.clicked.connect(lambda: self.add_task_requested.emit(self.column_id))
        main_layout.addWidget(self.add_task_btn)

    def set_column_style(self, dragging=False):
        """Establece el diseño de la columna (borde y fondo) basado en su color."""
        try:
            r, g, b = hex_to_rgb(self.column_data["color"])
        except Exception:
            r, g, b = 59, 130, 246  # Azul por defecto
            
        if dragging:
            # Fondo más iluminado y borde discontinuo más grueso
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: rgba({r}, {g}, {b}, 0.12);
                    border: 2px dashed rgba({r}, {g}, {b}, 0.8);
                }}
            """)
        else:
            # Fondo muy sutil y borde semi-transparente que enmarca la columna
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: rgba({r}, {g}, {b}, 0.04);
                    border: 1.5px solid rgba({r}, {g}, {b}, 0.3);
                }}
            """)

    def show_column_menu(self):
        """Muestra el menú contextual de la columna para editarla o borrarla."""
        menu = QMenu(self)
        # Aplicar el tema oscuro al menú
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {styles.COLORS['bg_sidebar']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                color: {styles.COLORS['text_main']};
            }}
            QMenu::item:selected {{
                background-color: {styles.COLORS['accent_blue']};
            }}
        """)
        
        edit_action = menu.addAction("✏️ Editar Columna")
        delete_action = menu.addAction("🗑️ Eliminar Columna")
        
        action = menu.exec(QCursor.pos())
        if action == edit_action:
            self.edit_column_requested.emit(self.column_id)
        elif action == delete_action:
            self.delete_column_requested.emit(self.column_id)

    def clear_tasks(self):
        """Elimina todos los widgets de tarea de la columna."""
        # Limpiar el layout
        while self.list_area.layout.count():
            item = self.list_area.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_task_card(self, card_widget):
        """Añade una tarjeta de tarea a la columna."""
        self.list_area.layout.addWidget(card_widget)
