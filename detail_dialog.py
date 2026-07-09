from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPlainTextEdit, QPushButton, QScrollArea, QWidget,
    QColorDialog, QMessageBox
)
from PySide6.QtGui import QKeySequence, QColor, QShortcut
from datetime import datetime
import database
import styles

class LogEntryWidget(QFrame):
    """Representa una única entrada en el diario/chat de la tarea."""
    def __init__(self, log_data, delete_callback, parent=None):
        super().__init__(parent)
        self.log_id = log_data["id"]
        self.delete_callback = delete_callback
        
        self.setObjectName("LogEntryWidget")
        self.init_ui(log_data)

    def init_ui(self, log_data):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Fila superior: Fecha/Hora y botón de eliminar
        top_layout = QHBoxLayout()
        
        # Formatear la fecha
        raw_date = log_data["created_at"]
        try:
            # SQLite por defecto guarda en UTC o local text. Formateamos para mejor lectura
            # Ejemplo: '2026-07-09 19:30:00' -> '09/07/2026 19:30'
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_date = raw_date  # Fallback
            
        timestamp_label = QLabel(formatted_date)
        timestamp_label.setObjectName("LogTimestamp")
        top_layout.addWidget(timestamp_label)
        top_layout.addStretch()

        # Botón sutil para borrar la entrada del diario
        delete_btn = QPushButton("×")
        delete_btn.setFixedSize(16, 16)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ef4444;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #dc2626;
                background-color: rgba(239, 68, 68, 0.1);
                border-radius: 2px;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_callback(self.log_id, self))
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)

        # Contenido de la entrada
        content_label = QLabel(log_data["content"])
        content_label.setObjectName("LogContent")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(content_label)


class TaskDetailDialog(QDialog):
    def __init__(self, task_id, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.db_path = db_path
        self.tag_color = "#6b7280"  # Color por defecto
        self.task_deleted = False  # Indica si se borró la tarea desde este diálogo
        
        self.setWindowTitle("Detalles de la Tarea")
        self.resize(800, 550)
        self.setMinimumSize(700, 450)
        
        self.init_ui()
        self.load_task_data()

    def init_ui(self):
        # Layout principal horizontal (Izquierda: Formulario, Derecha: Diario/Log)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ==========================================
        # PANEL IZQUIERDO: DETALLES DE LA TAREA
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # 1. Título
        left_layout.addWidget(QLabel("📝 <b>Título de la Tarea</b>"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ej. Escribir informe mensual...")
        left_layout.addWidget(self.title_input)

        # 2. Descripción
        left_layout.addWidget(QLabel("📄 <b>Descripción / Notas</b>"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Añade detalles sobre esta tarea...")
        left_layout.addWidget(self.desc_input)

        # 3. Etiqueta (Tag y Color)
        tag_section = QWidget()
        tag_layout = QHBoxLayout(tag_section)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(10)

        # Campo de texto de la etiqueta
        tag_text_widget = QWidget()
        tag_text_layout = QVBoxLayout(tag_text_widget)
        tag_text_layout.setContentsMargins(0, 0, 0, 0)
        tag_text_layout.setSpacing(4)
        tag_text_layout.addWidget(QLabel("🏷️ <b>Etiqueta (Status/Prioridad)</b>"))
        self.tag_text_input = QLineEdit()
        self.tag_text_input.setPlaceholderText("Ej. Alta, En progreso, Idea")
        tag_text_layout.addWidget(self.tag_text_input)
        tag_layout.addWidget(tag_text_widget, 3)

        # Botón selector de color de la etiqueta
        tag_color_widget = QWidget()
        tag_color_layout = QVBoxLayout(tag_color_widget)
        tag_color_layout.setContentsMargins(0, 0, 0, 0)
        tag_color_layout.setSpacing(4)
        tag_color_layout.addWidget(QLabel("🎨 <b>Color Etiqueta</b>"))
        
        self.color_picker_btn = QPushButton("🎨 Seleccionar")
        self.color_picker_btn.setCursor(Qt.PointingHandCursor)
        self.color_picker_btn.clicked.connect(self.select_tag_color)
        tag_color_layout.addWidget(self.color_picker_btn)
        tag_layout.addWidget(tag_color_widget, 1)

        left_layout.addWidget(tag_section)
        left_layout.addStretch()

        # Botones de Acción de la Tarea (Guardar, Eliminar, Cerrar)
        action_layout = QHBoxLayout()
        
        self.delete_task_btn = QPushButton("🗑️ Eliminar")
        self.delete_task_btn.setObjectName("DangerButton")
        self.delete_task_btn.setCursor(Qt.PointingHandCursor)
        self.delete_task_btn.clicked.connect(self.delete_task)
        action_layout.addWidget(self.delete_task_btn)
        
        action_layout.addStretch()

        self.save_btn = QPushButton("💾 Guardar Cambios")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_changes)
        action_layout.addWidget(self.save_btn)

        self.close_btn = QPushButton("❌ Cerrar")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.reject)
        action_layout.addWidget(self.close_btn)

        left_layout.addLayout(action_layout)
        main_layout.addWidget(left_panel, 4)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {styles.COLORS['border']};")
        main_layout.addWidget(separator)

        # ==========================================
        # PANEL DERECHO: DIARIO / HISTORIAL (LOGS)
        # ==========================================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        right_layout.addWidget(QLabel("📖 <b>Log / Diario Personal de la Tarea</b>"))

        # Área de Scroll para ver el historial
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        
        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(6, 6, 6, 6)
        self.logs_layout.setSpacing(8)
        self.logs_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.logs_container)
        right_layout.addWidget(self.scroll_area)

        # Caja de entrada para nuevos logs
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.log_input = QPlainTextEdit()
        self.log_input.setPlaceholderText("Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)")
        self.log_input.setFixedHeight(70)
        input_layout.addWidget(self.log_input)

        log_btn_layout = QHBoxLayout()
        log_btn_layout.addStretch()
        self.add_log_btn = QPushButton("✍️ Añadir al Diario")
        self.add_log_btn.setObjectName("PrimaryButton")
        self.add_log_btn.setCursor(Qt.PointingHandCursor)
        self.add_log_btn.clicked.connect(self.add_log_entry)
        log_btn_layout.addWidget(self.add_log_btn)
        
        input_layout.addLayout(log_btn_layout)
        right_layout.addWidget(input_container)

        main_layout.addWidget(right_panel, 5)

        # Atajo teclado Ctrl+Enter para añadir entrada al diario
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self.add_log_entry)
        
        # También mapear Ctrl+Enter del teclado numérico
        shortcut_num = QShortcut(QKeySequence("Ctrl+Enter"), self)
        shortcut_num.activated.connect(self.add_log_entry)

    def load_task_data(self):
        """Carga los datos iniciales de la tarea y sus logs desde la base de datos."""
        task = database.get_task(self.task_id, self.db_path)
        if not task:
            QMessageBox.critical(self, "Error", "No se pudo cargar la tarea.")
            self.reject()
            return

        self.title_input.setText(task["title"])
        self.desc_input.setHtml(task["description"] or "")
        self.tag_text_input.setText(task["tag_text"] or "")
        self.tag_color = task["tag_color"] or "#6b7280"
        self.update_color_button_style()

        # Cargar los logs
        self.reload_logs()

    def select_tag_color(self):
        """Abre un diálogo de color para personalizar la etiqueta."""
        initial_color = QColor(self.tag_color)
        color = QColorDialog.getColor(initial_color, self, "Seleccionar Color de Etiqueta")
        if color.isValid():
            self.tag_color = color.name()
            self.update_color_button_style()

    def update_color_button_style(self):
        """Actualiza el fondo del botón de color para reflejar la selección actual."""
        self.color_picker_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tag_color};
                color: #ffffff;
                font-weight: bold;
                border: 1px solid {styles.COLORS['border']};
            }}
            QPushButton:hover {{
                background-color: {self.tag_color};
                border-color: #ffffff;
            }}
        """)

    def save_changes(self):
        """Guarda el título, descripción, etiqueta y color de la tarea."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Atención", "El título de la tarea no puede estar vacío.")
            return

        description = self.desc_input.toHtml()
        tag_text = self.tag_text_input.text().strip()
        
        database.update_task(self.task_id, title, description, tag_text, self.tag_color, self.db_path)
        self.accept()

    def delete_task(self):
        """Borra definitivamente la tarea actual de la base de datos."""
        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            "¿Estás seguro de que deseas eliminar esta tarea de forma permanente? No se podrá recuperar.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_task(self.task_id, self.db_path)
            self.task_deleted = True
            self.accept()

    def reload_logs(self):
        """Limpia y vuelve a cargar todos los logs/entradas del diario."""
        # Limpiar contenedor de logs
        while self.logs_layout.count():
            item = self.logs_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Consultar y agregar los logs
        logs = database.get_logs(self.task_id, self.db_path)
        for log in logs:
            log_widget = LogEntryWidget(log, self.delete_log_entry, self)
            self.logs_layout.addWidget(log_widget)
        
        # Pequeño retardo para dar tiempo a Qt a renderizar antes de bajar el scroll
        self.scroll_to_bottom()

    def add_log_entry(self):
        """Crea una nueva entrada de diario con el texto del input."""
        content = self.log_input.toPlainText().strip()
        if not content:
            return  # No añadir logs vacíos

        database.create_log(self.task_id, content, self.db_path)
        self.log_input.clear()
        
        # En vez de recargar todo, recargamos para asegurar sincronización limpia
        self.reload_logs()

    def delete_log_entry(self, log_id, widget):
        """Elimina una entrada de diario tras confirmación."""
        confirm = QMessageBox.question(
            self,
            "Eliminar Entrada",
            "¿Estás seguro de que deseas borrar esta entrada del diario?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_log(log_id, self.db_path)
            widget.deleteLater()

    def scroll_to_bottom(self):
        """Mueve la barra de desplazamiento del diario hasta abajo."""
        # Usamos un timer de un solo disparo o directamente el valor del scrollbar
        # ya que Qt a veces tarda un instante en actualizar el scroll máximo
        scrollbar = self.scroll_area.verticalScrollBar()
        # Conectamos de forma asíncrona sutil para que se ejecute después del repaint
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: scrollbar.setValue(scrollbar.maximum()))
