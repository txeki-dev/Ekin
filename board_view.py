from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QInputDialog, QMessageBox, QDialog, QLineEdit, QColorDialog,
    QComboBox
)
import database
import styles
from styles import hex_to_rgb
from widgets import ColumnWidget, TaskCard, make_glyph_icon
from detail_dialog import TaskDetailDialog
from undo import UndoAction


class BoardColumnsArea(QWidget):
    """Contenedor horizontal de columnas que acepta soltar una columna arrastrada para reordenarla."""
    column_reordered = Signal(int, int)  # column_id, target_position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-column-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-column-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        if not mime.hasFormat("application/x-ekin-column-id"):
            event.ignore()
            return

        column_id = int(mime.data("application/x-ekin-column-id").data().decode("utf-8"))
        event.acceptProposedAction()

        drop_x = event.position().x()
        target_pos = 0
        layout = self.layout()

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget and isinstance(widget, ColumnWidget):
                col_middle = widget.x() + (widget.width() / 2)
                if drop_x < col_middle:
                    target_pos = i
                    break
                else:
                    target_pos = i + 1

        self.column_reordered.emit(column_id, target_pos)

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


class BoardSelectionDialog(QDialog):
    """Diálogo para seleccionar un tablero de destino para mover o copiar una columna."""
    def __init__(self, title, action_text, exclude_board_id=None, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(320, 150)
        self.db_path = db_path
        self.exclude_board_id = exclude_board_id
        
        self.selected_board_id = None
        
        self.init_ui(action_text)
        
    def init_ui(self, action_text):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        layout.addWidget(QLabel("<b>Selecciona el tablero de destino:</b>"))
        
        self.board_combo = QComboBox()
        # Consultar tableros
        boards = database.get_boards(self.db_path)
        
        self.available_boards = []
        for b in boards:
            if b["id"] != self.exclude_board_id:
                self.available_boards.append(b)
                self.board_combo.addItem(b["name"])
                
        layout.addWidget(self.board_combo)
        layout.addStretch()
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton(action_text)
        self.ok_btn.setObjectName("PrimaryButton")
        self.ok_btn.clicked.connect(self.accept_selection)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if not self.available_boards:
            self.ok_btn.setEnabled(False)
            self.board_combo.setEnabled(False)
            self.board_combo.addItem("No hay otros tableros")
            
    def accept_selection(self):
        index = self.board_combo.currentIndex()
        if index >= 0 and index < len(self.available_boards):
            self.selected_board_id = self.available_boards[index]["id"]
            self.accept()
        else:
            self.reject()


class BoardViewWidget(QFrame):
    toggle_sidebar_requested = Signal()
    data_changed = Signal()  # Emitida tras (re)cargar el tablero, para refrescar campana/calendario

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.board_id = None
        self.column_widgets = {}  # Guarda referencia a {column_id: ColumnWidget}
        self.undo_manager = None  # lo inyecta MainWindow
        self.setObjectName("BoardViewWidget")

        self.init_ui()

    def _refresh_current(self):
        if self.board_id and self.board_id != -1:
            self.load_board(self.board_id)

    def _push_delete_undo(self, label, snap, restore_fn, delete_fn):
        """Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)."""
        if self.undo_manager is None or snap is None:
            return
        holder = {}

        def do_undo():
            holder["id"] = restore_fn(snap)
            self._refresh_current()

        def do_redo():
            if holder.get("id") is not None:
                delete_fn(holder["id"], self.db_path)
                self._refresh_current()

        self.undo_manager.push(UndoAction(label, do_undo, do_redo))

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 0. Cabecera del Tablero (Board Header Bar)
        self.board_header = QWidget()
        self.board_header.setObjectName("BoardHeaderBar")
        self.board_header.setFixedHeight(50)
        self.board_header.setStyleSheet(f"""
            #BoardHeaderBar {{
                background-color: {styles.COLORS['bg_sidebar']};
                border-bottom: 1.5px solid {styles.COLORS['border']};
            }}
        """)
        header_layout = QHBoxLayout(self.board_header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        header_layout.setSpacing(10)

        # Botón para colapsar/desplegar la barra lateral (◀ plegar / ▶ desplegar, pintado)
        self._sidebar_visible = True
        self.toggle_sidebar_btn = QPushButton()
        self.toggle_sidebar_btn.setFixedSize(32, 32)
        self.toggle_sidebar_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_sidebar_btn.setToolTip("Mostrar/Ocultar barra lateral")
        self.toggle_sidebar_btn.setIcon(make_glyph_icon("left", "#f8fafc", 16))
        self.toggle_sidebar_btn.setIconSize(QSize(16, 16))
        self.toggle_sidebar_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_card']};
                border-color: {styles.COLORS['accent_blue']};
            }}
        """)
        self.toggle_sidebar_btn.clicked.connect(self._on_toggle_sidebar)
        header_layout.addWidget(self.toggle_sidebar_btn)

        # Título del Tablero
        self.board_title_label = QLabel("Mi Tablero")
        self.board_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(self.board_title_label)
        header_layout.addStretch()

        self.main_layout.addWidget(self.board_header)
        self.board_header.hide()

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
        
        self.board_content = BoardColumnsArea()
        self.board_content.setObjectName("BoardViewContent")
        self.board_content.setStyleSheet("background-color: transparent;")
        self.board_content.column_reordered.connect(self.handle_column_drop)

        self.columns_layout = QHBoxLayout(self.board_content)
        self.columns_layout.setContentsMargins(15, 15, 15, 15)
        self.columns_layout.setSpacing(15)
        self.columns_layout.setAlignment(Qt.AlignLeft)

        self.board_scroll_area.setWidget(self.board_content)
        self.main_layout.addWidget(self.board_scroll_area)
        
        # Por defecto ocultamos la zona del tablero hasta cargar uno
        self.board_scroll_area.hide()

    def load_board(self, board_id, notify=True):
        """Carga las columnas y tareas de un tablero específico. `notify=False` evita
        emitir data_changed cuando la carga es solo navegación (cambio de tablero,
        recarga de tema, arranque) y no refleja una mutación real de datos."""
        self.board_id = board_id

        if board_id == -1:
            # Mostrar pantalla de bienvenida
            self.board_scroll_area.hide()
            self.board_header.hide()
            self.welcome_widget.show()
            self.clear_columns_layout()
            self.setStyleSheet("")
            if notify:
                self.data_changed.emit()
            return

        # Ocultar bienvenida y mostrar scroll area y cabecera
        self.welcome_widget.hide()
        self.board_header.show()
        self.board_scroll_area.show()
        
        self.clear_columns_layout()

        # Obtener información del tablero (incluyendo el color)
        board_info = database.get_board(board_id, self.db_path)
        if board_info:
            self.board_title_label.setText(board_info["name"])
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
            # Cargar las tareas primero: hace falta el contador para la vista plegada.
            tasks = database.get_tasks(col_data["id"], self.db_path)
            col_data["task_count"] = len(tasks)

            col_widget = ColumnWidget(col_data, self)  # fija su propio ancho según collapsed

            # Conectar señales
            col_widget.task_dropped.connect(self.handle_task_drop)
            col_widget.add_task_requested.connect(self.add_task)
            col_widget.edit_column_requested.connect(self.edit_column)
            col_widget.delete_column_requested.connect(self.delete_column)
            col_widget.copy_column_requested.connect(self.copy_column)
            col_widget.collapse_toggle_requested.connect(self.handle_column_collapse)
            col_widget.collapsed_card_drop.connect(self.handle_collapsed_card_drop)

            # Solo montamos las tarjetas si la columna está desplegada
            if not col_data.get("collapsed"):
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

        if notify:
            self.data_changed.emit()

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
            board_id = self.board_id
            snap = database.snapshot_column(column_id, self.db_path)
            database.delete_column(column_id, self.db_path)
            self.load_board(self.board_id)
            self._push_delete_undo(
                "Eliminar columna", snap,
                lambda s: database.restore_column(s, board_id=board_id, db_path=self.db_path),
                database.delete_column,
            )

    def _on_toggle_sidebar(self):
        """Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)."""
        self._sidebar_visible = not self._sidebar_visible
        kind = "left" if self._sidebar_visible else "right"
        self.toggle_sidebar_btn.setIcon(make_glyph_icon(kind, "#f8fafc", 16))
        self.toggle_sidebar_requested.emit()

    def handle_column_collapse(self, column_id):
        """Pliega o despliega una columna (persiste el estado) y recarga el tablero."""
        col_widget = self.column_widgets.get(column_id)
        new_state = not (col_widget.collapsed if col_widget else False)
        database.set_column_collapsed(column_id, new_state, self.db_path)
        self.load_board(self.board_id)

    def handle_collapsed_card_drop(self, task_id, column_id):
        """Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta al final."""
        database.set_column_collapsed(column_id, False, self.db_path)
        # Posición muy alta -> handle_task_drop la recorta al final de la columna destino
        self.handle_task_drop(task_id, column_id, 10 ** 9)

    def handle_column_drop(self, column_id, target_position):
        """Reordena las columnas del tablero actual tras arrastrar una por su título."""
        columns = database.get_columns(self.board_id, self.db_path)

        moved_column = None
        for c in columns:
            if c["id"] == column_id:
                moved_column = c
                columns.remove(c)
                break

        if not moved_column:
            return

        insert_idx = min(max(0, target_position), len(columns))
        columns.insert(insert_idx, moved_column)

        updates = [(c["id"], i) for i, c in enumerate(columns)]
        database.update_column_positions(updates, self.db_path)

        self.load_board(self.board_id)

    def copy_column(self, column_id):
        """Crea una copia de la columna en otro tablero seleccionado."""
        col_widget = self.column_widgets.get(column_id)
        if not col_widget:
            return
            
        dialog = BoardSelectionDialog(
            "Copiar Columna",
            "Copiar",
            exclude_board_id=self.board_id,
            db_path=self.db_path,
            parent=self
        )
        
        if dialog.exec() == QDialog.Accepted and dialog.selected_board_id is not None:
            target_board_id = dialog.selected_board_id
            target_board = database.get_board(target_board_id, self.db_path)
            board_name = target_board["name"] if target_board else "el tablero seleccionado"
            
            database.copy_column_to_board(column_id, target_board_id, self.db_path)
            
            QMessageBox.information(
                self,
                "Columna Copiada",
                f"La columna '{col_widget.column_data['name']}' y todas sus tareas/logs han sido copiadas con éxito a '{board_name}'."
            )
            
            self.load_board(self.board_id)

    # --- ACCIONES DE TAREAS ---

    def quick_add_task(self):
        """Atajo Ctrl+N: añade una tarea a la primera columna del tablero activo."""
        if not self.board_id or self.board_id == -1:
            return
        columns = database.get_columns(self.board_id, self.db_path)
        if columns:
            self.add_task(columns[0]["id"])

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

        # Si se eliminó la tarea desde el diálogo, registrar el deshacer con su snapshot.
        if getattr(dialog, "task_deleted", False) and getattr(dialog, "deleted_snapshot", None):
            self._push_delete_undo(
                "Eliminar tarea", dialog.deleted_snapshot,
                lambda s: database.restore_task(s, db_path=self.db_path),
                database.delete_task,
            )

        # Solo refrescamos el tablero (y notificamos campana/calendario) si el
        # diálogo realmente cambió algo: título, descripción, etiquetas, diario,
        # enlaces o si se eliminó la tarea. Si solo se abrió para consultar, no
        # hace falta recargar nada.
        if getattr(dialog, "modified", False) or getattr(dialog, "task_deleted", False):
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
