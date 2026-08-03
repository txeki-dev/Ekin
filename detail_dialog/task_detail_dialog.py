from PySide6.QtCore import Qt, QDate, QTime, QUrl, QSize
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget,
    QMessageBox, QCheckBox, QDateEdit, QTimeEdit, QComboBox
)
from PySide6.QtGui import QKeySequence, QShortcut, QDesktopServices
import database
import styles
from widgets import make_glyph_icon
from .markdown_edit import MarkdownTextEdit, RichTextToolbar
from .log_entry import LogEntryWidget
from .tag_pill import ClickableTagPill
from .tag_manager_dialog import TagManagerDialog
from .tag_picker_dialog import TagPickerDialog


class TaskDetailDialog(QDialog):
    def __init__(self, task_id, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.db_path = db_path
        self.current_tags = []      # Lista de diccionarios {'text': '...', 'color': '...'}
        self.task_deleted = False  # Indica si se borró la tarea desde este diálogo
        self.modified = False      # Indica si hubo algún cambio real (título, tags, diario, enlaces...)

        self.setWindowTitle("Detalles de la Tarea")
        self.resize(1120, 720)
        self.setMinimumSize(940, 580)

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
        self.desc_input = MarkdownTextEdit()
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
        self.due_enable_chk.stateChanged.connect(self._sync_due_enabled)
        due_layout.addWidget(self.due_enable_chk)

        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setEnabled(False)
        due_layout.addWidget(self.due_date_edit)

        # Hora de vencimiento opcional (activa un aviso en el .ics)
        self.due_time_chk = QCheckBox("Hora")
        self.due_time_chk.setCursor(Qt.PointingHandCursor)
        self.due_time_chk.setToolTip("Añadir hora al vencimiento (crea un aviso en el calendario)")
        self.due_time_chk.stateChanged.connect(self._sync_due_enabled)
        due_layout.addWidget(self.due_time_chk)
        self.due_time_edit = QTimeEdit()
        self.due_time_edit.setDisplayFormat("HH:mm")
        self.due_time_edit.setTime(QTime(9, 0))
        self.due_time_edit.setEnabled(False)
        due_layout.addWidget(self.due_time_edit)

        # Recurrencia (repetir la tarea)
        due_layout.addWidget(QLabel("🔁"))
        self._recurrence_values = ["none", "daily", "weekly", "monthly"]
        self.recurrence_combo = QComboBox()
        for label in ("Sin repetir", "Diaria", "Semanal", "Mensual"):
            self.recurrence_combo.addItem(label)
        self.recurrence_combo.setToolTip("Repetir la tarea: al pasar la fecha, se adelanta sola")
        due_layout.addWidget(self.recurrence_combo)
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

        tag_btns_row = QHBoxLayout()
        tag_btns_row.setSpacing(6)
        self.add_tag_btn = QPushButton("➕ Asignar Etiqueta")
        self.add_tag_btn.setCursor(Qt.PointingHandCursor)
        self.add_tag_btn.clicked.connect(self.assign_tag_dialog)
        tag_btns_row.addWidget(self.add_tag_btn)

        self.manage_tags_btn = QPushButton("⚙ Gestionar")
        self.manage_tags_btn.setToolTip("Definir etiquetas permanentes y sus valores")
        self.manage_tags_btn.setCursor(Qt.PointingHandCursor)
        self.manage_tags_btn.clicked.connect(self.open_tag_manager)
        tag_btns_row.addWidget(self.manage_tags_btn)
        tag_btns_row.addStretch()
        tags_layout.addLayout(tag_btns_row)

        left_layout.addWidget(tags_section)

        # 5. Enlaces / adjuntos
        links_section = QWidget()
        links_outer = QVBoxLayout(links_section)
        links_outer.setContentsMargins(0, 0, 0, 0)
        links_outer.setSpacing(4)
        links_outer.addWidget(QLabel("🔗 <b>Enlaces / adjuntos:</b>"))

        self.links_container = QWidget()
        self.links_layout = QVBoxLayout(self.links_container)
        self.links_layout.setContentsMargins(0, 0, 0, 0)
        self.links_layout.setSpacing(2)
        links_outer.addWidget(self.links_container)

        add_link_row = QHBoxLayout()
        add_link_row.setSpacing(6)
        self.link_url_input = QLineEdit()
        self.link_url_input.setPlaceholderText("URL o ruta…")
        self.link_url_input.returnPressed.connect(self.add_link)
        add_link_row.addWidget(self.link_url_input, 2)
        self.link_label_input = QLineEdit()
        self.link_label_input.setPlaceholderText("Nombre (opcional)")
        add_link_row.addWidget(self.link_label_input, 1)
        add_link_btn = QPushButton("➕")
        add_link_btn.setFixedWidth(30)
        add_link_btn.setCursor(Qt.PointingHandCursor)
        add_link_btn.setToolTip("Añadir enlace")
        add_link_btn.clicked.connect(self.add_link)
        add_link_row.addWidget(add_link_btn)
        links_outer.addLayout(add_link_row)

        left_layout.addWidget(links_section)
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
        right_layout.addWidget(self.scroll_area, 1)  # el historial domina el alto

        # Caja de entrada para nuevos logs
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.log_input = MarkdownTextEdit()
        self.log_input.setPlaceholderText("Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)")
        # Caja cómoda que crece con el texto (sin límite de caracteres; solo tope visual)
        self.log_input.setMinimumHeight(110)
        self.log_input.setMaximumHeight(260)
        # Las imágenes pegadas en el chat se ajustan al ancho del histórico (más estrecho)
        self.log_input.image_width_provider = self._chat_image_width
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

    def _sync_due_enabled(self):
        """Habilita/inhabilita fecha y hora según los checks."""
        due_on = self.due_enable_chk.isChecked()
        self.due_date_edit.setEnabled(due_on)
        self.due_time_chk.setEnabled(due_on)
        self.due_time_edit.setEnabled(due_on and self.due_time_chk.isChecked())

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

        # Cargar hora de vencimiento
        due_time = task.get("due_time")
        if due_date and due_time:
            self.due_time_chk.setChecked(True)
            self.due_time_edit.setTime(QTime.fromString(due_time, "HH:mm"))
        else:
            self.due_time_chk.setChecked(False)
        self._sync_due_enabled()

        # Cargar recurrencia
        rec = task.get("recurrence", "none") or "none"
        self.recurrence_combo.setCurrentIndex(
            self._recurrence_values.index(rec) if rec in self._recurrence_values else 0
        )

        # Cargar etiquetas
        self.current_tags = task.get("tags", [])
        self.render_tags()

        # Cargar enlaces y logs
        self.reload_links()
        self.reload_logs()

    def render_tags(self):
        """Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el
        valor; el botón × la retira de la tarea."""
        # Limpiar
        while self.tags_container_layout.count():
            item = self.tags_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not self.current_tags:
            hint = QLabel("Sin etiquetas. Pulsa «Asignar Etiqueta».")
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;")
            self.tags_container_layout.addWidget(hint)
            return

        for index, tag in enumerate(self.current_tags):
            pill = ClickableTagPill()
            pill.setObjectName("TagPillFrame")
            pill.setCursor(Qt.PointingHandCursor)
            pill.setToolTip("Clic para cambiar el valor")
            pill.setStyleSheet(f"#TagPillFrame {{ {styles.tag_pill_css(tag['color'])} }}")
            pill.clicked.connect(lambda idx=index: self.edit_tag_at(idx))
            pill_layout = QHBoxLayout(pill)
            pill_layout.setContentsMargins(6, 2, 6, 2)
            pill_layout.setSpacing(4)

            lbl = QLabel(f"{tag['category']}: {tag['value']}".upper())
            lbl.setStyleSheet("color: #ffffff; font-size: 9px; font-weight: bold; background: transparent; border: none;")
            pill_layout.addWidget(lbl)

            del_btn = QPushButton("×")
            del_btn.setFixedSize(14, 14)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setToolTip("Quitar de la tarea")
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

    def _set_category_value(self, tag):
        """Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un
        único valor por etiqueta en la tarea y conservando la posición existente."""
        idx = next(
            (i for i, t in enumerate(self.current_tags)
             if t["category"].lower() == tag["category"].lower()),
            None
        )
        if idx is None:
            self.current_tags.append(tag)
        else:
            self.current_tags[idx] = tag
            # Eliminar cualquier duplicado posterior de la misma etiqueta
            self.current_tags = [
                t for i, t in enumerate(self.current_tags)
                if i == idx or t["category"].lower() != tag["category"].lower()
            ]
        self.render_tags()

    def delete_tag_at(self, index):
        """Retira una etiqueta de la tarea (localmente) y re-renderiza."""
        if 0 <= index < len(self.current_tags):
            self.current_tags.pop(index)
            self.render_tags()

    def edit_tag_at(self, index):
        """Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno» (retirarla)."""
        if not (0 <= index < len(self.current_tags)):
            return
        tag = self.current_tags[index]
        dialog = TagPickerDialog(
            self.db_path, self,
            fixed_category={"id": tag["category_id"], "name": tag["category"]},
            current_value_id=tag["tag_value_id"],
            allow_none=True
        )
        if dialog.exec() != QDialog.Accepted:
            return

        value_id, is_none = dialog.get_selection()
        if is_none or value_id is None:
            self.current_tags.pop(index)
            self.render_tags()
            return

        new_tag = database.get_tag_value(value_id, self.db_path)
        if new_tag:
            self.current_tags[index] = new_tag
            self.render_tags()

    def assign_tag_dialog(self):
        """Asigna una etiqueta permanente (categoría) con uno de sus valores a la tarea."""
        dialog = TagPickerDialog(self.db_path, self)
        if dialog.exec() != QDialog.Accepted:
            return

        value_id, _ = dialog.get_selection()
        if value_id is None:
            return

        tag = database.get_tag_value(value_id, self.db_path)
        if tag:
            self._set_category_value(tag)

    def open_tag_manager(self):
        """Abre el gestor del catálogo de etiquetas y re-sincroniza las etiquetas asignadas."""
        TagManagerDialog(self.db_path, self).exec()
        self.refresh_current_tags_from_db()

    def refresh_current_tags_from_db(self):
        """Refresca los datos (valor/color) de las etiquetas asignadas y descarta las que
        hayan sido eliminadas del catálogo desde el gestor."""
        refreshed = []
        for tag in self.current_tags:
            latest = database.get_tag_value(tag["tag_value_id"], self.db_path)
            if latest:
                refreshed.append(latest)
        self.current_tags = refreshed
        self.render_tags()

    def save_changes(self):
        """Guarda el título, descripción, etiquetas y fecha de vencimiento."""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Atención", "El título de la tarea no puede estar vacío.")
            return

        description = self.desc_input.toHtml()

        # Obtener fecha y hora de vencimiento
        due_date = None
        due_time = None
        if self.due_enable_chk.isChecked():
            due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
            if self.due_time_chk.isChecked():
                due_time = self.due_time_edit.time().toString("HH:mm")

        # Guardar tarea principal (las columnas tag_text/tag_color quedan sin uso: las etiquetas
        # estructuradas viven en task_tags/tag_values)
        database.update_task(self.task_id, title, description, "", "#6b7280", due_date, self.db_path)
        database.set_task_due_time(self.task_id, due_time, self.db_path)

        # Guardar las etiquetas asignadas
        tag_value_ids = [tag["tag_value_id"] for tag in self.current_tags]
        database.set_task_tags(self.task_id, tag_value_ids, self.db_path)

        # Guardar la recurrencia
        database.set_task_recurrence(
            self.task_id, self._recurrence_values[self.recurrence_combo.currentIndex()], self.db_path
        )

        self.modified = True
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
            # Snapshot antes de borrar, para poder deshacer (Ctrl+Z)
            self.deleted_snapshot = database.snapshot_task(self.task_id, self.db_path)
            database.delete_task(self.task_id, self.db_path)
            self.task_deleted = True
            self.accept()

    # --- Enlaces / adjuntos (persistidos al instante) ---

    def reload_links(self):
        while self.links_layout.count():
            item = self.links_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        links = database.get_task_links(self.task_id, self.db_path)
        if not links:
            hint = QLabel("Sin enlaces.")
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;")
            self.links_layout.addWidget(hint)
            return
        for link in links:
            self.links_layout.addWidget(self._build_link_row(link))

    def _build_link_row(self, link):
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        open_btn = QPushButton("🔗 " + (link["label"] or link["url"]))
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setToolTip(link["url"])
        open_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #60a5fa; text-align: left; }"
            "QPushButton:hover { text-decoration: underline; }"
        )
        open_btn.clicked.connect(lambda _=False, url=link["url"]: QDesktopServices.openUrl(QUrl(url)))
        h.addWidget(open_btn, 1)
        del_btn = QPushButton()
        del_btn.setFixedSize(18, 18)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Eliminar enlace")
        del_btn.setIcon(make_glyph_icon("cross", "#ef4444", 12))
        del_btn.setIconSize(QSize(12, 12))
        del_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        del_btn.clicked.connect(lambda _=False, lid=link["id"]: self.remove_link(lid))
        h.addWidget(del_btn)
        return row

    def add_link(self):
        url = self.link_url_input.text().strip()
        if not url:
            return
        label = self.link_label_input.text().strip() or None
        database.add_task_link(self.task_id, url, label, self.db_path)
        self.link_url_input.clear()
        self.link_label_input.clear()
        self.modified = True
        self.reload_links()

    def remove_link(self, link_id):
        database.delete_task_link(link_id, self.db_path)
        self.modified = True
        self.reload_links()

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
            log_widget = LogEntryWidget(log, self.delete_log_entry, self.edit_log_entry, self)
            self.logs_layout.addWidget(log_widget)

        # Pequeño retardo para dar tiempo a Qt a renderizar antes de bajar el scroll
        self.scroll_to_bottom()

    def edit_log_entry(self, log_id, new_html):
        """Guarda la edición de un comentario (o cancela si new_html es None) y recarga."""
        if new_html is not None:
            database.update_log(log_id, new_html, self.db_path)
            self.modified = True
        self.reload_logs()

    def _chat_image_width(self):
        """Ancho máximo (px) para imágenes pegadas en el chat: el del histórico (más
        estrecho que el editor), reservando márgenes y la barra de scroll para que no
        aparezca scroll horizontal ni tape los botones de la entrada."""
        w = self.scroll_area.viewport().width()
        return max(120, w - 44)

    def add_log_entry(self):
        """Crea una nueva entrada de diario con el texto del input."""
        if not self.log_input.toPlainText().strip():
            return  # No añadir logs vacíos

        database.create_log(self.task_id, self.log_input.toHtml(), self.db_path)
        self.log_input.clear()
        self.modified = True

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
            self.modified = True
            widget.deleteLater()

    def scroll_to_bottom(self):
        """Mueve la barra de desplazamiento del diario hasta abajo."""
        # Usamos un timer de un solo disparo o directamente el valor del scrollbar
        # ya que Qt a veces tarda un instante en actualizar el scroll máximo
        scrollbar = self.scroll_area.verticalScrollBar()
        # Conectamos de forma asíncrona sutil para que se ejecute después del repaint
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, lambda: scrollbar.setValue(scrollbar.maximum()))
