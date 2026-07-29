from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QMessageBox, QDialog, QLineEdit, QColorDialog
)
from PySide6.QtGui import QColor, QPixmap, QIcon
from datetime import date, datetime, timedelta
import database
import styles
from styles import hex_to_rgb

# Nombres cortos en español para el reloj (evita depender de la locale del sistema)
_DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
_MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _swatch_icon(color, size=12):
    """Pequeño icono cuadrado del color indicado (para listar tareas por tablero)."""
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class NotificationsPopup(QDialog):
    """Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.
    Al pulsar una tarea emite `task_activated(task_id, board_id)`."""
    task_activated = Signal(int, int)

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setObjectName("NotificationsPopup")
        self.setFixedWidth(310)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        header = QLabel("🔔  Vencimientos")
        header.setStyleSheet("font-weight: bold; font-size: 13px; background: transparent;")
        layout.addWidget(header)

        if not tasks:
            empty = QLabel("No hay tareas atrasadas ni próximas. ✅")
            empty.setWordWrap(True)
            empty.setStyleSheet(f"color: {styles.COLORS['text_muted']}; padding: 8px 2px; background: transparent;")
            layout.addWidget(empty)
            return

        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setMaximumHeight(360)
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(content)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(4)
        vbox.setAlignment(Qt.AlignTop)

        # Atrasadas = con fecha anterior a hoy. Se muestran arriba y en tono de alerta.
        self._add_group(vbox, "ATRASADAS", [t for t in tasks if t["due_date"] < today],
                        color=styles.COLORS["danger"])
        self._add_group(vbox, "HOY", [t for t in tasks if t["due_date"] == today])
        self._add_group(vbox, "MAÑANA", [t for t in tasks if t["due_date"] == tomorrow])

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _add_group(self, vbox, label, tasks, color=None):
        if not tasks:
            return
        color = color or styles.COLORS['text_muted']
        group_label = QLabel(label)
        group_label.setStyleSheet(
            f"color: {color}; font-size: 10px; font-weight: bold;"
            " margin-top: 4px; background: transparent;"
        )
        vbox.addWidget(group_label)
        for t in tasks:
            btn = QPushButton(t["title"] or "(sin título)")
            btn.setObjectName("NotificationItem")
            btn.setIcon(_swatch_icon(t["board_color"]))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(f"{t['board_name']} · vence {t['due_date']}")
            btn.clicked.connect(
                lambda _=False, tid=t["id"], bid=t["board_id"]: self._activate(tid, bid)
            )
            vbox.addWidget(btn)

    def _activate(self, task_id, board_id):
        self.task_activated.emit(task_id, board_id)
        self.accept()


class BoardButton(QFrame):
    """Widget personalizado para representar un botón de tablero en la barra lateral."""
    clicked = Signal(int)  # Emite el board_id cuando se pulsa
    column_dropped = Signal(int, int)  # column_id, target_board_id (al soltar una columna arrastrada)

    def __init__(self, board_id, name, color, active=False, parent=None):
        super().__init__(parent)
        self.board_id = board_id
        self.name = name
        self.color = color
        self.active = active

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(40)
        self.setAcceptDrops(True)

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-column-id"):
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(59, 130, 246, 0.25);
                    border: 2px dashed {styles.COLORS['accent_blue']};
                    border-radius: 6px;
                    color: #f8fafc;
                }}
            """)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.update_style()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasFormat("application/x-ekin-column-id"):
            column_id = int(mime.data("application/x-ekin-column-id").data().decode("utf-8"))
            event.acceptProposedAction()
            self.update_style()
            self.column_dropped.emit(column_id, self.board_id)
        else:
            event.ignore()


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
    board_selected = Signal(int)          # Emite el board_id seleccionado
    board_changed = Signal()              # Emite cuando se añade/edita/borra un tablero
    open_calendar_requested = Signal()    # Emite al pulsar el botón de calendario
    open_search_requested = Signal()      # Emite al pulsar el botón de búsqueda
    open_task_requested = Signal(int, int)  # (task_id, board_id) desde la campana o la búsqueda

    def __init__(self, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.active_board_id = None
        self.board_buttons = {}  # Guarda referencia a {board_id: BoardButton}

        self.setObjectName("SidebarFrame")
        self.init_ui()
        self.reload_boards()

        # Reloj: refresco periódico de la fecha/hora
        self._update_clock()
        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(10000)  # cada 10 s (precisión de minuto de sobra)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        # Título del panel (logo + nombre)
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_layout.addStretch()

        logo_label = QLabel()
        logo_pixmap = QPixmap("ekin_icon.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(
                logo_pixmap.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        title_layout.addWidget(logo_label)

        title_label = QLabel("EKIN")
        title_label.setObjectName("SidebarTitle")
        title_layout.addWidget(title_label)

        title_layout.addStretch()
        layout.addWidget(title_container)

        # --- Barra de utilidades: reloj + campana de vencimientos + calendario ---
        layout.addWidget(self._build_utility_bar())

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

    def _build_utility_bar(self):
        """Barra con reloj (fecha/hora), campana de vencimientos y acceso al calendario."""
        bar = QFrame()
        bar.setObjectName("UtilityBar")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(10, 6, 8, 6)
        bar_layout.setSpacing(6)

        self.clock_label = QLabel("")
        self.clock_label.setObjectName("ClockLabel")
        bar_layout.addWidget(self.clock_label)
        bar_layout.addStretch()

        # Campana con badge de conteo superpuesto
        bell_container = QWidget()
        bell_container.setFixedSize(34, 28)
        self.bell_btn = QPushButton("🔔", bell_container)
        self.bell_btn.setObjectName("UtilityIconButton")
        self.bell_btn.setGeometry(0, 0, 34, 28)
        self.bell_btn.setCursor(Qt.PointingHandCursor)
        self.bell_btn.setToolTip("Tareas atrasadas o que vencen hoy o mañana")
        self.bell_btn.clicked.connect(self.show_notifications)

        self.bell_badge = QLabel("0", bell_container)
        self.bell_badge.setObjectName("BellBadge")
        self.bell_badge.setAlignment(Qt.AlignCenter)
        self.bell_badge.setFixedSize(15, 15)
        self.bell_badge.move(19, -1)
        self.bell_badge.hide()
        bar_layout.addWidget(bell_container)

        self.search_btn = QPushButton("🔍")
        self.search_btn.setObjectName("UtilityIconButton")
        self.search_btn.setFixedSize(34, 28)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setToolTip("Buscar tareas (Ctrl+F)")
        self.search_btn.clicked.connect(self.open_search_requested.emit)
        bar_layout.addWidget(self.search_btn)

        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setObjectName("UtilityIconButton")
        self.calendar_btn.setFixedSize(34, 28)
        self.calendar_btn.setCursor(Qt.PointingHandCursor)
        self.calendar_btn.setToolTip("Abrir vista de calendario")
        self.calendar_btn.clicked.connect(self.open_calendar_requested.emit)
        bar_layout.addWidget(self.calendar_btn)

        return bar

    def _update_clock(self):
        now = datetime.now()
        text = f"{_DIAS[now.weekday()]} {now.day} {_MESES[now.month - 1]} · {now.strftime('%H:%M')}"
        self.clock_label.setText(text)

    def get_pending_notifications(self):
        """Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.

        Devuelve todo lo que tenga fecha de vencimiento <= mañana: la campana lo
        agrupa en ATRASADAS / HOY / MAÑANA."""
        tomorrow = date.today() + timedelta(days=1)
        return database.get_scheduled_tasks(end_date=tomorrow.isoformat(), db_path=self.db_path)

    def refresh_notifications(self):
        """Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana."""
        if not hasattr(self, "bell_badge"):
            return
        count = len(self.get_pending_notifications())
        if count > 0:
            self.bell_badge.setText(str(count) if count < 10 else "9+")
            self.bell_badge.show()
        else:
            self.bell_badge.hide()

    def show_notifications(self):
        """Muestra el popup de vencimientos anclado bajo la campana."""
        popup = NotificationsPopup(self.get_pending_notifications(), self)
        popup.task_activated.connect(self._on_notification_task)
        pos = self.bell_btn.mapToGlobal(QPoint(0, self.bell_btn.height() + 4))
        popup.move(pos)
        popup.exec()

    def _on_notification_task(self, task_id, board_id):
        self.open_task_requested.emit(task_id, board_id)

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
            self.refresh_notifications()
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
            btn.column_dropped.connect(self.handle_column_dropped)
            self.boards_layout.addWidget(btn)
            self.board_buttons[board_id] = btn

        # Emitir la selección del tablero activo para que la vista del tablero se cargue
        self.board_selected.emit(self.active_board_id)
        self.refresh_notifications()

    def handle_column_dropped(self, column_id, target_board_id):
        """Mueve una columna arrastrada desde el tablero activo hasta el botón de otro tablero."""
        if target_board_id == self.active_board_id:
            return
        database.move_column_to_board(column_id, target_board_id, self.db_path)
        self.reload_boards(select_board_id=self.active_board_id)

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
