import os
from PySide6.QtCore import Qt, Signal, QSize, QTimer, QFileSystemWatcher, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QInputDialog, QMessageBox, QDialog, QLineEdit, QColorDialog,
    QComboBox, QFileDialog, QMenu
)
import database
import board_sync
import styles
from styles import hex_to_rgb
from strings import t
from widgets import ColumnWidget, TaskCard, make_glyph_icon
from detail_dialog import TaskDetailDialog
from undo import UndoAction
from cloud_sync_dialog import CloudSyncInfoDialog


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
        layout.addWidget(QLabel(t("board_view.column_edit.name_label")))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText(t("board_view.column_edit.name_placeholder"))
        layout.addWidget(self.name_input)

        # Color de la columna
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel(t("board_view.column_edit.color_label")))
        
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
        
        self.ok_btn = QPushButton(t("board_view.column_edit.save"))
        self.ok_btn.setObjectName("PrimaryButton")
        self.ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(t("board_view.column_edit.cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.color, self, t("board_view.column_edit.color_dialog_title"))
        if color.isValid():
            self.color = color.name()
            self.update_color_btn_style()

    def update_color_btn_style(self):
        self.color_btn.setStyleSheet(styles.color_swatch_css(self.color, hover=True))

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, t("board_view.column_edit.warn_title"), t("board_view.column_edit.warn_empty_name")
            )
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
        
        layout.addWidget(QLabel(t("board_view.board_selection.target_label")))
        
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
        
        self.cancel_btn = QPushButton(t("board_view.board_selection.cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        if not self.available_boards:
            self.ok_btn.setEnabled(False)
            self.board_combo.setEnabled(False)
            self.board_combo.addItem(t("board_view.board_selection.no_other_boards"))
            
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
    board_link_activated = Signal(int)  # board_id: pulsada la pastilla de tablero enlazado de una tarjeta

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.board_id = None
        self.column_widgets = {}  # Guarda referencia a {column_id: ColumnWidget}
        # Última columna con la que el usuario interactuó (tarjeta, "+ Añadir Tarea"
        # o clic en la propia columna) -- pista para Ctrl+N; se revalida contra las
        # columnas del tablero activo en el momento de usarla (quick_add_task), nunca
        # se confía en ella a ciegas (puede apuntar a otro tablero o a una columna ya
        # borrada).
        self._last_active_column_id = None
        self.undo_manager = None  # lo inyecta MainWindow
        # Columna actualmente expandida por HOVER durante un arrastre en curso (o None).
        # Vive aquí (no en ColumnWidget) porque load_board() recrea todos los ColumnWidget.
        self._hover_expanded_column_id = None
        self.selected_task_ids = set()
        self.setObjectName("BoardViewWidget")

        self._timer_badge_refresh_timer = QTimer(self)
        self._timer_badge_refresh_timer.timeout.connect(self.refresh_timer_badges)
        self._timer_badge_refresh_timer.start(60_000)  # refresca las insignias cada 60s

        self.init_ui()
        self.data_changed.connect(self._trigger_auto_sync_export)

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
        self.toggle_sidebar_btn.setToolTip(t("board_view.header.toggle_sidebar_tooltip"))
        self.toggle_sidebar_btn.setIcon(make_glyph_icon("left", styles.COLORS['text_main'], 16))
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
        self.board_title_label = QLabel(t("board_view.header.default_title"))
        self.board_title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.COLORS['text_main']};")
        header_layout.addWidget(self.board_title_label)
        header_layout.addStretch()

        # Botón de Sincronización OneDrive / Carpeta compartida
        self.sync_btn = QPushButton(t("sync.link_btn"))
        self.sync_btn.setCursor(Qt.PointingHandCursor)
        self.sync_btn.clicked.connect(self._on_sync_btn_clicked)
        header_layout.addWidget(self.sync_btn)

        self.main_layout.addWidget(self.board_header)
        self.board_header.hide()

        # 1. Contenedor de bienvenida (se muestra si no hay tableros)
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        
        welcome_label = QLabel(t("board_view.welcome"))
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

        # 3. Barra de acción para selección múltiple de tarjetas
        self.selection_bar = QFrame()
        self.selection_bar.setObjectName("SelectionBar")
        self.selection_bar.setFixedHeight(50)
        self.selection_bar.setStyleSheet(f"""
            #SelectionBar {{
                background-color: {styles.COLORS['bg_sidebar']};
                border-top: 1.5px solid {styles.COLORS['accent_blue']};
            }}
        """)
        sel_layout = QHBoxLayout(self.selection_bar)
        sel_layout.setContentsMargins(20, 0, 20, 0)
        sel_layout.setSpacing(12)

        self.selection_bar_label = QLabel(t("ai_spec.selection_count", count=0))
        self.selection_bar_label.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {styles.COLORS['text_main']};")
        sel_layout.addWidget(self.selection_bar_label)

        sel_layout.addStretch()

        self.ai_spec_btn = QPushButton(t("ai_spec.generate_spec_btn"))
        self.ai_spec_btn.setObjectName("PrimaryButton")
        self.ai_spec_btn.setCursor(Qt.PointingHandCursor)
        self.ai_spec_btn.clicked.connect(self.open_ai_spec_dialog)
        sel_layout.addWidget(self.ai_spec_btn)

        self.clear_sel_btn = QPushButton(t("ai_spec.clear_selection_btn"))
        self.clear_sel_btn.setCursor(Qt.PointingHandCursor)
        self.clear_sel_btn.clicked.connect(self.clear_task_selection)
        sel_layout.addWidget(self.clear_sel_btn)

        self.main_layout.addWidget(self.selection_bar)
        self.selection_bar.hide()
        
        # Por defecto ocultamos la zona del tablero hasta cargar uno
        self.board_scroll_area.hide()

    def _build_column_widget(self, col_data, tasks, board_info, timer_alert_hours):
        """Construye un ColumnWidget completo (señales conectadas y, si está desplegada,
        sus TaskCard) para una columna dada. No lo añade a ningún layout ni a
        self.column_widgets -- eso lo decide el llamante: load_board() para reconstruir
        el tablero entero, _rebuild_single_column() para sustituir solo una columna sin
        tocar el resto (necesario para no destruir la columna de ORIGEN de un drag en
        curso -- ver _rebuild_single_column)."""
        col_widget = ColumnWidget(col_data, self)

        col_widget.task_dropped.connect(self.handle_task_drop)
        col_widget.add_task_requested.connect(self.add_task)
        col_widget.edit_column_requested.connect(self.edit_column)
        col_widget.delete_column_requested.connect(self.delete_column)
        col_widget.copy_column_requested.connect(self.copy_column)
        col_widget.collapse_toggle_requested.connect(self.handle_column_collapse)
        col_widget.collapsed_card_drop.connect(self.handle_collapsed_card_drop)
        col_widget.hover_expand_requested.connect(self.handle_hover_expand_requested)
        col_widget.column_activated.connect(self._set_last_active_column)

        if not col_data.get("collapsed"):
            for task_data in tasks:
                card = TaskCard(task_data, self)
                if board_info:
                    card.set_card_style(board_info["color"])
                card.set_timer_alert_hours(timer_alert_hours)
                if card.task_id in self.selected_task_ids:
                    card.set_selected(True)
                card.clicked.connect(lambda tid, cid=col_data["id"]: self._handle_task_card_clicked(tid, cid))
                card.ctrl_clicked.connect(lambda tid, cid=col_data["id"]: self._handle_task_ctrl_clicked(tid, cid))
                card.board_link_clicked.connect(self.board_link_activated.emit)
                card.drag_ended.connect(self.finalize_hover_expand)
                col_widget.add_task_card(card)

        return col_widget

    def _rebuild_single_column(self, column_id):
        """Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la
        BD) y lo sustituye en su misma posición dentro de columns_layout, sin tocar
        ninguna otra columna. A diferencia de load_board(), esto SÍ es seguro de llamar
        a mitad de un QDrag.exec() nativo en curso: el hover-expand solo actúa sobre
        columnas colapsadas, y una tarjeta solo puede arrastrarse desde una columna ya
        desplegada, así que la columna de origen del arrastre nunca puede coincidir con
        la columna que aquí se reconstruye -- nunca se le llama deleteLater()."""
        old_widget = self.column_widgets.get(column_id)
        if old_widget is None or not self.board_id or self.board_id == -1:
            return

        index = self.columns_layout.indexOf(old_widget)
        if index == -1:
            return

        columns = database.get_columns(self.board_id, self.db_path)
        col_data = next((c for c in columns if c["id"] == column_id), None)
        if col_data is None:
            return

        tasks = database.get_tasks(column_id, self.db_path)
        col_data["task_count"] = len(tasks)
        board_info = database.get_board(self.board_id, self.db_path)
        timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))

        new_widget = self._build_column_widget(col_data, tasks, board_info, timer_alert_hours)

        self.columns_layout.removeWidget(old_widget)
        old_widget.deleteLater()
        self.columns_layout.insertWidget(index, new_widget)
        self.column_widgets[column_id] = new_widget

    def refresh_timer_badges(self):
        """Refresca la insignia de tiempo transcurrido en todas las tarjetas con un
        temporizador activo, sin recargar el tablero -- el tiempo transcurrido cambia solo
        con el paso del tiempo, no hay datos nuevos que leer de la BD; solo hace falta
        recalcular el texto/color ya mostrado en cada TaskCard viva."""
        for col_widget in self.column_widgets.values():
            for card in col_widget.findChildren(TaskCard):
                card.update_timer_badge()

    def load_board(self, board_id, notify=True):
        """Carga las columnas y tareas de un tablero específico. `notify=False` evita
        emitir data_changed cuando la carga es solo navegación (cambio de tablero,
        recarga de tema, arranque) y no refleja una mutación real de datos."""
        if self.board_id != board_id:
            self.selected_task_ids.clear()
        self.board_id = board_id

        if board_id == -1:
            # Mostrar pantalla de bienvenida
            self.board_scroll_area.hide()
            self.board_header.hide()
            self.selection_bar.hide()
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
        timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))

        for col_data in columns:
            # Cargar las tareas primero: hace falta el contador para la vista plegada.
            tasks = database.get_tasks(col_data["id"], self.db_path)
            col_data["task_count"] = len(tasks)

            col_widget = self._build_column_widget(col_data, tasks, board_info, timer_alert_hours)

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
        
        add_col_btn = QPushButton(t("board_view.add_column_btn"))
        add_col_btn.setObjectName("PrimaryButton")
        add_col_btn.setCursor(Qt.PointingHandCursor)
        add_col_btn.clicked.connect(self.add_column)
        add_col_layout.addWidget(add_col_btn)

        self.columns_layout.addWidget(self.add_column_card)

        # Actualizar botón de sincronización y file watcher reactivo
        self._update_sync_ui(board_id)

        # Actualizar visibilidad de selección múltiple
        self._update_cards_selection_ui()

        if notify:
            self.data_changed.emit()

    def _update_sync_ui(self, board_id):
        """Actualiza el botón y estado de sincronización con OneDrive."""
        sync_info = database.get_board_sync_info(board_id, self.db_path)
        self._current_sync_info = sync_info
        if sync_info and sync_info.get("sync_path"):
            path = sync_info["sync_path"]
            self.sync_btn.setText(t("sync.synced_badge"))
            last_sync = sync_info.get("last_synced_at") or "-"
            self.sync_btn.setToolTip(f"Sincronizado con:\n{path}\nÚltima sincronización: {last_sync}")
            self.sync_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(16, 185, 129, 0.15);
                    border: 1px solid rgba(16, 185, 129, 0.4);
                    border-radius: 6px;
                    color: #10b981;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(16, 185, 129, 0.25);
                    border-color: #10b981;
                }
            """)
            self._setup_file_watcher(path)
        else:
            self.sync_btn.setText(t("sync.link_btn"))
            self.sync_btn.setToolTip(t("sync.link_tooltip"))
            self.sync_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {styles.COLORS['border']};
                    border-radius: 6px;
                    color: {styles.COLORS['text_muted']};
                    padding: 4px 10px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {styles.COLORS['bg_card']};
                    border-color: {styles.COLORS['accent_blue']};
                    color: {styles.COLORS['text_main']};
                }}
            """)
            self._setup_file_watcher(None)

    def _setup_file_watcher(self, path):
        """Configura el watcher para detectar reactivamente cambios externos en el archivo .ekboard."""
        if not hasattr(self, "_file_watcher"):
            self._file_watcher = QFileSystemWatcher(self)
            self._file_watcher.fileChanged.connect(self._on_sync_file_changed)
            self._sync_debounce_timer = QTimer(self)
            self._sync_debounce_timer.setSingleShot(True)
            self._sync_debounce_timer.setInterval(600)
            self._sync_debounce_timer.timeout.connect(self._on_debounced_file_sync)

        existing = self._file_watcher.files()
        if existing:
            self._file_watcher.removePaths(existing)
        if path and os.path.exists(path):
            self._file_watcher.addPath(path)
            self._watched_sync_path = path
        else:
            self._watched_sync_path = None

    def _on_sync_file_changed(self, path):
        """Evento de cambio detectado por el sistema de archivos (OneDrive)."""
        self._sync_debounce_timer.start()

    def _ensure_watcher_path_active(self):
        """Asegura que el archivo sincronizado esté registrado en QFileSystemWatcher tras reemplazo atómico en Windows."""
        if hasattr(self, "_watched_sync_path") and self._watched_sync_path and hasattr(self, "_file_watcher"):
            if self._watched_sync_path not in self._file_watcher.files() and os.path.exists(self._watched_sync_path):
                self._file_watcher.addPath(self._watched_sync_path)

    def _on_debounced_file_sync(self):
        """Ejecuta la sincronización en diferido cuando OneDrive termina de escribir."""
        if not self.board_id or self.board_id == -1:
            return
        res = board_sync.sync_board_with_file(self.board_id, db_path=self.db_path)
        if res.status in ("imported", "merged"):
            self.load_board(self.board_id, notify=False)
        self._ensure_watcher_path_active()

    def _trigger_auto_sync_export(self):
        """Exporta cambios locales en segundo plano si el tablero está vinculado."""
        if hasattr(self, "board_id") and self.board_id and self.board_id != -1:
            sync_info = database.get_board_sync_info(self.board_id, self.db_path)
            if sync_info and sync_info.get("sync_path"):
                board_sync.sync_board_with_file(self.board_id, db_path=self.db_path)
                self._ensure_watcher_path_active()

    def _on_sync_btn_clicked(self):
        """Maneja el clic en el botón de sincronización de la cabecera."""
        if not self.board_id or self.board_id == -1:
            return
        sync_info = database.get_board_sync_info(self.board_id, self.db_path)
        if not sync_info or not sync_info.get("sync_path"):
            board_name = self.board_title_label.text().strip().replace(" ", "_")
            info_dlg = CloudSyncInfoDialog(board_name=board_name, parent=self.window())
            if info_dlg.exec() != QDialog.Accepted:
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                t("sync.dialog_title_link"),
                f"{board_name}.ekboard",
                t("sync.dialog_filter")
            )
            if file_path:
                res = board_sync.sync_board_with_file(self.board_id, file_path, self.db_path)
                if res.status != "error":
                    self.load_board(self.board_id)
                    parent_win = self.window()
                    if hasattr(parent_win, "sidebar"):
                        parent_win.sidebar.reload_boards()
                else:
                    QMessageBox.warning(self, t("sync.error_title"), res.message)
        else:
            # Menú de opciones del tablero ya vinculado
            menu = QMenu(self)
            styles.style_menu(menu)
            sync_now_act = menu.addAction(t("sync.menu_sync_now"))
            open_loc_act = menu.addAction(t("sync.menu_open_location"))
            menu.addSeparator()
            unlink_act = menu.addAction(t("sync.menu_unlink"))

            chosen = menu.exec(self.sync_btn.mapToGlobal(self.sync_btn.rect().bottomLeft()))
            if chosen == sync_now_act:
                self.sync_current_board_now()
            elif chosen == open_loc_act:
                folder = os.path.dirname(os.path.abspath(sync_info["sync_path"]))
                if os.path.exists(folder):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
            elif chosen == unlink_act:
                reply = QMessageBox.question(
                    self,
                    t("sync.unlink_confirm_title"),
                    t("sync.unlink_confirm_body"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    database.unlink_board_sync(self.board_id, self.db_path)
                    self.load_board(self.board_id)
                    parent_win = self.window()
                    if hasattr(parent_win, "sidebar"):
                        parent_win.sidebar.reload_boards()

    def sync_current_board_now(self):
        """Sincroniza el tablero actual inmediatamente y notifica si hubo fusión."""
        if not self.board_id or self.board_id == -1:
            return
        res = board_sync.sync_board_with_file(self.board_id, db_path=self.db_path)
        if res.status == "error":
            QMessageBox.warning(self, t("sync.error_title"), res.message)
        else:
            if res.status in ("imported", "merged"):
                self.load_board(self.board_id, notify=False)
            if res.status == "merged" and res.conflicts_resolved > 0:
                QMessageBox.information(
                    self,
                    t("sync.success_title"),
                    t("sync.conflict_merged_toast") + f"\n({res.conflicts_resolved} conflicto(s) archivado(s) en el diario)."
                )

    # --- SELECCIÓN MÚLTIPLE DE TARJETAS & IA LOCAL ---

    def _handle_task_ctrl_clicked(self, task_id, column_id):
        """Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic."""
        self._set_last_active_column(column_id)
        if task_id in self.selected_task_ids:
            self.selected_task_ids.remove(task_id)
        else:
            self.selected_task_ids.add(task_id)
        self._update_cards_selection_ui()

    def _update_cards_selection_ui(self):
        """Actualiza el estado visual de selección en todas las tarjetas y la barra inferior."""
        for col_widget in self.column_widgets.values():
            for card in col_widget.findChildren(TaskCard):
                card.set_selected(card.task_id in self.selected_task_ids)

        count = len(self.selected_task_ids)
        if count > 0:
            self.selection_bar.show()
            self.selection_bar_label.setText(t("ai_spec.selection_count", count=count))
        else:
            self.selection_bar.hide()

    def clear_task_selection(self):
        """Deselecciona todas las tareas activas."""
        self.selected_task_ids.clear()
        self._update_cards_selection_ui()

    def open_ai_spec_dialog(self):
        """Abre el generador modal de especificaciones para agentes de IA."""
        if not self.selected_task_ids:
            return
        from ai_spec_dialog import AiSpecDialog
        dlg = AiSpecDialog(list(self.selected_task_ids), self.board_id, self.db_path, parent=self)
        if dlg.exec():
            # Si el diálogo creó una tarjeta con la SPEC generada, recargar el tablero
            self.load_board(self.board_id)
            self.clear_task_selection()

    def keyPressEvent(self, event):
        """Escape deselecciona tarjetas múltiples."""
        if event.key() == Qt.Key_Escape and self.selected_task_ids:
            self.clear_task_selection()
            event.accept()
            return
        super().keyPressEvent(event)


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
        if not self.board_id or self.board_id == -1:
            return
        
        dialog = ColumnEditDialog(t("board_view.column_edit.new_title"), name="", color="#3b82f6", parent=self)
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
            t("board_view.column_edit.edit_title"),
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
            t("board_view.delete_column.title"),
            t("board_view.delete_column.body", name=col_widget.column_data['name']),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            board_id = self.board_id
            snap = database.snapshot_column(column_id, self.db_path)
            database.delete_column(column_id, self.db_path)
            self.load_board(self.board_id)
            self._push_delete_undo(
                t("board_view.delete_column.undo_label"), snap,
                lambda s: database.restore_column(s, board_id=board_id, db_path=self.db_path),
                database.delete_column,
            )

    def _on_toggle_sidebar(self):
        """Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)."""
        self._sidebar_visible = not self._sidebar_visible
        kind = "left" if self._sidebar_visible else "right"
        self.toggle_sidebar_btn.setIcon(make_glyph_icon(kind, styles.COLORS['text_main'], 16))
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

    def handle_hover_expand_requested(self, column_id):
        """Expansión temporal (por hover durante un arrastre) de una columna
        plegada: permite elegir la posición de destino en vez de caer siempre al
        final. Si había otra columna expandida por hover en este mismo
        arrastre, se repliega primero."""
        if column_id == self._hover_expanded_column_id:
            return
        self._collapse_hover_expanded_column()
        database.set_column_collapsed(column_id, False, self.db_path)
        self._hover_expanded_column_id = column_id
        self._rebuild_single_column(column_id)

    def _collapse_hover_expanded_column(self):
        """Repliega (BD + widget) la columna actualmente expandida por hover, si la
        hay. Reconstruye solo esa columna -- nunca toca el resto del tablero."""
        if self._hover_expanded_column_id is not None:
            column_id = self._hover_expanded_column_id
            database.set_column_collapsed(column_id, True, self.db_path)
            self._hover_expanded_column_id = None
            self._rebuild_single_column(column_id)

    def finalize_hover_expand(self):
        """Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier
        arrastre de tarjeta (soltada donde sea, o cancelado). Si queda una
        columna expandida por hover sin haber recibido el drop, se repliega."""
        self._collapse_hover_expanded_column()

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
            t("board_view.copy_column.title"),
            t("board_view.copy_column.action"),
            exclude_board_id=self.board_id,
            db_path=self.db_path,
            parent=self
        )

        if dialog.exec() == QDialog.Accepted and dialog.selected_board_id is not None:
            target_board_id = dialog.selected_board_id
            target_board = database.get_board(target_board_id, self.db_path)
            board_name = target_board["name"] if target_board else t("board_view.copy_column.fallback_board_name")

            database.copy_column_to_board(column_id, target_board_id, self.db_path)

            QMessageBox.information(
                self,
                t("board_view.copy_column.done_title"),
                t("board_view.copy_column.done_body", column=col_widget.column_data['name'], board=board_name)
            )
            
            self.load_board(self.board_id)

    # --- ACCIONES DE TAREAS ---

    def quick_add_task(self):
        """Atajo Ctrl+N: añade una tarea a la última columna con la que se ha
        interactuado (tarjeta abierta, botón "+ Añadir Tarea", o clic en la propia
        columna). Si no hay ninguna registrada -- o ya no pertenece al tablero
        activo (p. ej. se borró, o se cambió de tablero desde entonces) -- cae a
        la primera columna, como antes."""
        if not self.board_id or self.board_id == -1:
            return
        columns = database.get_columns(self.board_id, self.db_path)
        if not columns:
            return
        column_ids = [c["id"] for c in columns]
        target_id = (
            self._last_active_column_id
            if self._last_active_column_id in column_ids
            else column_ids[0]
        )
        self.add_task(target_id)

    def _set_last_active_column(self, column_id):
        self._last_active_column_id = column_id

    def add_task(self, column_id):
        """Crea una tarea solicitando el título rápidamente."""
        self._last_active_column_id = column_id
        title, ok = QInputDialog.getText(
            self, t("board_view.add_task.title"), t("board_view.add_task.prompt"),
            text=""
        )
        if ok and title.strip():
            database.create_task(column_id, title.strip(), db_path=self.db_path)
            self.load_board(self.board_id)

    def _handle_task_card_clicked(self, task_id, column_id):
        self._set_last_active_column(column_id)
        self.open_task_details(task_id)

    def open_task_details(self, task_id):
        """Abre el diálogo de detalle/chat de una tarea."""
        dialog = TaskDetailDialog(task_id, self.db_path, self)
        dialog.exec()

        # Si se eliminó la tarea desde el diálogo, registrar el deshacer con su snapshot.
        if getattr(dialog, "task_deleted", False) and getattr(dialog, "deleted_snapshot", None):
            self._push_delete_undo(
                t("board_view.delete_task.undo_label"), dialog.deleted_snapshot,
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
        for task in source_tasks:
            if task["id"] == task_id:
                moved_task = task
                source_tasks.remove(task)
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
