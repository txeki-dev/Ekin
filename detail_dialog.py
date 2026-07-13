from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QScrollArea, QWidget,
    QColorDialog, QMessageBox, QCheckBox, QDateEdit, QComboBox
)
from PySide6.QtGui import (
    QKeySequence, QColor, QShortcut, QFont, QTextCharFormat, QTextListFormat
)
from datetime import datetime
import database
import styles


class RichTextToolbar(QWidget):
    """Barra de formato básica (negrita, cursiva, viñetas) para un QTextEdit."""
    def __init__(self, text_edit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.bold_btn = QPushButton("N")
        self.bold_btn.setToolTip("Negrita")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFixedSize(26, 24)
        self.bold_btn.setStyleSheet("font-weight: bold;")
        self.bold_btn.clicked.connect(self.toggle_bold)
        layout.addWidget(self.bold_btn)

        self.italic_btn = QPushButton("K")
        self.italic_btn.setToolTip("Cursiva")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(26, 24)
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.clicked.connect(self.toggle_italic)
        layout.addWidget(self.italic_btn)

        self.bullet_btn = QPushButton("• ≡")
        self.bullet_btn.setToolTip("Lista con viñetas")
        self.bullet_btn.setFixedSize(34, 24)
        self.bullet_btn.clicked.connect(self.toggle_bullets)
        layout.addWidget(self.bullet_btn)

        layout.addStretch()

        self.text_edit.cursorPositionChanged.connect(self.sync_buttons)

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.bold_btn.isChecked() else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_btn.isChecked())
        self.text_edit.mergeCurrentCharFormat(fmt)
        self.text_edit.setFocus()

    def toggle_bullets(self):
        cursor = self.text_edit.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)
        cursor.createList(list_format)
        self.text_edit.setFocus()

    def sync_buttons(self):
        fmt = self.text_edit.currentCharFormat()
        self.bold_btn.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_btn.setChecked(fmt.fontItalic())


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


class TagAssignDialog(QDialog):
    """Diálogo para asignar una etiqueta estructurada (Categoría: Valor) a una tarea.
    Permite reutilizar categorías/valores ya existentes en el catálogo o crear nuevos sobre la marcha."""
    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle("Asignar Etiqueta")
        self.setFixedSize(300, 230)

        self.selected_color = "#6b7280"
        self.categories = database.get_tag_categories(self.db_path)
        self.current_values = []

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        layout.addWidget(QLabel("<b>Categoría</b> (ej. Prioridad, Estado...):"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems([c["name"] for c in self.categories])
        self.category_combo.setCurrentText("")
        self.category_combo.editTextChanged.connect(self.on_category_changed)
        layout.addWidget(self.category_combo)

        layout.addWidget(QLabel("<b>Valor</b> (ej. Alta, Bloqueado...):"))
        self.value_combo = QComboBox()
        self.value_combo.setEditable(True)
        self.value_combo.editTextChanged.connect(self.on_value_changed)
        layout.addWidget(self.value_combo)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("<b>Color:</b>"))
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(30, 20)
        self.color_btn.setCursor(Qt.PointingHandCursor)
        self.color_btn.clicked.connect(self.choose_color)
        self.update_color_btn_style()
        color_layout.addWidget(self.color_btn)
        self.color_hint_label = QLabel("")
        self.color_hint_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 10px;")
        color_layout.addWidget(self.color_hint_label)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("Añadir")
        ok_btn.setObjectName("PrimaryButton")
        ok_btn.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_category_changed(self, text):
        category = next((c for c in self.categories if c["name"].lower() == text.strip().lower()), None)
        self.value_combo.clear()
        if category:
            self.current_values = database.get_tag_values(category["id"], self.db_path)
            self.value_combo.addItems([v["value"] for v in self.current_values])
        else:
            self.current_values = []
        self.value_combo.setCurrentText("")

    def on_value_changed(self, text):
        match = next((v for v in self.current_values if v["value"].lower() == text.strip().lower()), None)
        if match:
            # Un valor ya existente conserva su color de catálogo (consistencia entre tareas)
            self.selected_color = match["color"]
            self.color_btn.setEnabled(False)
            self.color_hint_label.setText("Color existente")
        else:
            self.color_btn.setEnabled(True)
            self.color_hint_label.setText("Nuevo valor")
        self.update_color_btn_style()

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Seleccionar Color")
        if color.isValid():
            self.selected_color = color.name()
            self.update_color_btn_style()

    def update_color_btn_style(self):
        self.color_btn.setStyleSheet(
            f"background-color: {self.selected_color}; border: 1px solid {styles.COLORS['border']}; border-radius: 4px;"
        )

    def validate_and_accept(self):
        if not self.category_combo.currentText().strip() or not self.value_combo.currentText().strip():
            QMessageBox.warning(self, "Atención", "Debes indicar una categoría y un valor para la etiqueta.")
            return
        self.accept()

    def get_data(self):
        return self.category_combo.currentText().strip(), self.value_combo.currentText().strip(), self.selected_color


class TaskDetailDialog(QDialog):
    def __init__(self, task_id, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.db_path = db_path
        self.current_tags = []      # Lista de diccionarios {'text': '...', 'color': '...'}
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
        left_layout.addWidget(RichTextToolbar(self.desc_input))
        left_layout.addWidget(self.desc_input)

        # 3. Fecha de Vencimiento
        due_section = QWidget()
        due_layout = QHBoxLayout(due_section)
        due_layout.setContentsMargins(0, 0, 0, 0)
        due_layout.setSpacing(10)
        
        due_layout.addWidget(QLabel("📅 <b>Vencimiento:</b>"))
        
        self.due_enable_chk = QCheckBox("Habilitar")
        self.due_enable_chk.setCursor(Qt.PointingHandCursor)
        self.due_enable_chk.stateChanged.connect(lambda state: self.due_date_edit.setEnabled(self.due_enable_chk.isChecked()))
        due_layout.addWidget(self.due_enable_chk)
        
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setEnabled(False)
        due_layout.addWidget(self.due_date_edit)
        due_layout.addStretch()
        
        left_layout.addWidget(due_section)

        # 4. Sección de Etiquetas Múltiples
        tags_section = QWidget()
        tags_layout = QVBoxLayout(tags_section)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(4)
        
        tags_layout.addWidget(QLabel("🏷️ <b>Etiquetas:</b>"))
        
        self.tags_container_widget = QWidget()
        self.tags_container_layout = QHBoxLayout(self.tags_container_widget)
        self.tags_container_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_container_layout.setSpacing(6)
        self.tags_container_layout.setAlignment(Qt.AlignLeft)
        tags_layout.addWidget(self.tags_container_widget)
        
        self.add_tag_btn = QPushButton("➕ Asignar Etiqueta")
        self.add_tag_btn.setCursor(Qt.PointingHandCursor)
        self.add_tag_btn.clicked.connect(self.assign_tag_dialog)
        tags_layout.addWidget(self.add_tag_btn)
        
        left_layout.addWidget(tags_section)
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

        self.log_input = QTextEdit()
        self.log_input.setPlaceholderText("Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)")
        self.log_input.setFixedHeight(90)
        input_layout.addWidget(RichTextToolbar(self.log_input))
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
        
        # Cargar fecha de vencimiento
        due_date = task.get("due_date")
        if due_date:
            self.due_enable_chk.setChecked(True)
            self.due_date_edit.setEnabled(True)
            self.due_date_edit.setDate(QDate.fromString(due_date, "yyyy-MM-dd"))
        else:
            self.due_enable_chk.setChecked(False)
            self.due_date_edit.setEnabled(False)
            self.due_date_edit.setDate(QDate.currentDate())

        # Cargar etiquetas
        self.current_tags = task.get("tags", [])
        self.render_tags()

        # Cargar los logs
        self.reload_logs()

    def render_tags(self):
        """Dibuja las etiquetas en el contenedor horizontal."""
        # Limpiar
        while self.tags_container_layout.count():
            item = self.tags_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Renderizar cada etiqueta como una píldora con un botón de eliminar
        for index, tag in enumerate(self.current_tags):
            pill = QFrame()
            pill.setObjectName("TagPillFrame")
            pill.setStyleSheet(f"""
                #TagPillFrame {{
                    background-color: {tag['color']};
                    border-radius: 4px;
                }}
            """)
            pill_layout = QHBoxLayout(pill)
            pill_layout.setContentsMargins(6, 2, 6, 2)
            pill_layout.setSpacing(4)

            lbl = QLabel(f"{tag['category']}: {tag['value']}".upper())
            lbl.setStyleSheet("color: #ffffff; font-size: 9px; font-weight: bold; background: transparent; border: none;")
            pill_layout.addWidget(lbl)

            del_btn = QPushButton("×")
            del_btn.setFixedSize(14, 14)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 10px;
                }
                QPushButton:hover {
                    color: #ef4444;
                    background-color: rgba(255, 255, 255, 0.2);
                    border-radius: 2px;
                }
            """)
            # Usar captura de índice en lambda
            del_btn.clicked.connect(lambda checked=False, idx=index: self.delete_tag_at(idx))
            pill_layout.addWidget(del_btn)

            self.tags_container_layout.addWidget(pill)

    def delete_tag_at(self, index):
        """Elimina una etiqueta localmente y re-renderiza."""
        if 0 <= index < len(self.current_tags):
            self.current_tags.pop(index)
            self.render_tags()

    def assign_tag_dialog(self):
        """Muestra el diálogo para asignar una etiqueta estructurada (Categoría: Valor) a la tarea."""
        dialog = TagAssignDialog(self.db_path, self)
        if dialog.exec() != QDialog.Accepted:
            return

        category_name, value_text, color = dialog.get_data()
        tag_value_id = database.get_or_create_tag_value(category_name, value_text, color, self.db_path)

        if any(tag["tag_value_id"] == tag_value_id for tag in self.current_tags):
            return  # Ya estaba asignada

        self.current_tags.append(database.get_tag_value(tag_value_id, self.db_path))
        self.render_tags()

    def save_changes(self):
        """Guarda el título, descripción, etiquetas y fecha de vencimiento."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Atención", "El título de la tarea no puede estar vacío.")
            return

        description = self.desc_input.toHtml()

        # Obtener fecha de vencimiento
        due_date = None
        if self.due_enable_chk.isChecked():
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd")

        # Guardar tarea principal (las columnas tag_text/tag_color quedan sin uso: las etiquetas
        # estructuradas viven en task_tags/tag_values)
        database.update_task(self.task_id, title, description, "", "#6b7280", due_date, self.db_path)

        # Guardar las etiquetas asignadas
        tag_value_ids = [tag["tag_value_id"] for tag in self.current_tags]
        database.set_task_tags(self.task_id, tag_value_ids, self.db_path)

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
        if not self.log_input.toPlainText().strip():
            return  # No añadir logs vacíos

        database.create_log(self.task_id, self.log_input.toHtml(), self.db_path)
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
