import os
from datetime import datetime
from PySide6.QtCore import Qt, QDate, QTime, QUrl, QSize, QTimer, QEvent, QObject, QEventLoop
from PySide6.QtWidgets import (
    QDialog, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget,
    QMessageBox, QCheckBox, QDateEdit, QTimeEdit, QComboBox, QFileDialog,
    QApplication
)
from PySide6.QtGui import QKeySequence, QShortcut, QDesktopServices
import database
import styles
from strings import t
from widgets import make_glyph_icon
from .markdown_edit import MarkdownTextEdit, RichTextToolbar
from .log_entry import LogEntryWidget
from .tag_pill import ClickableTagPill, color_icon
from .tag_manager_dialog import TagManagerDialog
from .tag_picker_dialog import TagPickerDialog

_WEB_LINK_SCHEMES = ("http://", "https://", "ftp://", "mailto:", "file://")


def _is_local_link(url):
    """True a menos que la cadena empiece por un esquema web reconocido (case-insensitive)."""
    return not url.lower().startswith(_WEB_LINK_SCHEMES)


class _ClickOutsideFilter(QObject):
    """Filtro de eventos que detecta clics fuera del diálogo dentro de la ventana
    principal de Ekin. Al hacer clic fuera, guarda automáticamente los cambios y
    cierra el diálogo (equivalente a pulsar el botón 'Guardar Cambios')."""
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog

    def eventFilter(self, obj, event):
        if event.type() in (QEvent.MouseButtonPress, QEvent.NonClientAreaMouseButtonPress):
            # Si hay un diálogo modal hijo abierto (ej. selector de etiquetas, confirmación), no cerrar
            if QApplication.activeModalWidget() is not None:
                return False
            # Si hay un menú o popup desplegable activo (ej. combo box), permitir que Qt lo cierre primero
            if QApplication.activePopupWidget() is not None:
                return False
            if isinstance(obj, QWidget):
                # Si el clic es dentro del propio diálogo o de alguno de sus hijos
                if obj == self.dialog or self.dialog.isAncestorOf(obj):
                    return False
                top_level = obj.window()
                if top_level == self.dialog or self.dialog.isAncestorOf(top_level):
                    return False

                # Clic fuera del diálogo dentro de la aplicación principal: autoguardar y cerrar
                self.dialog.save_changes()
                return True
        return False


class TaskDetailDialog(QDialog):
    def __init__(self, task_id, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.db_path = db_path
        self.current_tags = []      # Lista de diccionarios {'text': '...', 'color': '...'}
        self.task_deleted = False  # Indica si se borró la tarea desde este diálogo
        self.modified = False      # Indica si hubo algún cambio real (título, tags, diario, enlaces...)
        self._timer_started_at = None  # Timestamp ISO del temporizador en marcha, o None
        self._click_outside_filter = None

        self.setWindowTitle(t("task_detail.window_title"))
        self.resize(1120, 720)
        self.setMinimumSize(940, 580)

        self.init_ui()
        self.load_task_data()

        # Refresco periódico (solo UI, sin leer la BD) para que el contador de tiempo
        # transcurrido avance en vivo mientras el diálogo está abierto.
        self._timer_refresh_timer = QTimer(self)
        self._timer_refresh_timer.timeout.connect(self._refresh_timer_ui)
        self._timer_refresh_timer.start(30_000)

        # El diálogo se parenta a MainWindow/BoardViewWidget (viven toda la sesión), así que
        # nada lo destruye por sí solo cuando se cierra -- sin esto, cada tarea abierta deja un
        # TaskDetailDialog zombi con su _timer_refresh_timer disparando para siempre.
        self.finished.connect(self.deleteLater)

    def exec(self):
        """Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo
        que al hacer clic fuera se guarden automáticamente los cambios."""
        self.setWindowModality(Qt.NonModal)
        self.show()
        self.scroll_to_bottom()
        self._click_outside_filter = _ClickOutsideFilter(self)
        QApplication.instance().installEventFilter(self._click_outside_filter)

        loop = QEventLoop(self)
        self.finished.connect(lambda _: loop.quit())
        loop.exec()

        if getattr(self, "_click_outside_filter", None):
            QApplication.instance().removeEventFilter(self._click_outside_filter)
            self._click_outside_filter = None

        return self.result()

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
        left_layout.addWidget(QLabel(t("task_detail.title_label")))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(t("task_detail.title_placeholder"))
        left_layout.addWidget(self.title_input)

        # 2. Descripción
        left_layout.addWidget(QLabel(t("task_detail.description_label")))
        self.desc_input = MarkdownTextEdit()
        # Mismo ancho por defecto para imágenes pegadas que en el chat (self._chat_image_width,
        # asignado también a log_input más abajo) -- evita que una imagen pegada aquí desborde
        # si el diálogo se redimensiona más estrecho después de pegarla.
        self.desc_input.image_width_provider = self._chat_image_width
        self.desc_input.setPlaceholderText(t("task_detail.description_placeholder"))
        left_layout.addWidget(RichTextToolbar(self.desc_input))
        left_layout.addWidget(self.desc_input)

        # 2.5 Temporizador
        timer_section = QWidget()
        timer_section_layout = QHBoxLayout(timer_section)
        timer_section_layout.setContentsMargins(0, 0, 0, 0)
        timer_section_layout.setSpacing(10)

        timer_section_layout.addWidget(QLabel(t("task_detail.timer_label")))

        self.timer_toggle_btn = QPushButton(t("task_detail.timer_start_btn"))
        self.timer_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.timer_toggle_btn.clicked.connect(self._on_timer_toggle_clicked)
        timer_section_layout.addWidget(self.timer_toggle_btn)

        self.timer_clear_btn = QPushButton(t("task_detail.timer_clear_btn"))
        self.timer_clear_btn.setCursor(Qt.PointingHandCursor)
        self.timer_clear_btn.setToolTip(t("task_detail.timer_clear_tooltip"))
        self.timer_clear_btn.clicked.connect(self._on_timer_clear_clicked)
        timer_section_layout.addWidget(self.timer_clear_btn)

        self.timer_elapsed_label = QLabel("")
        self.timer_elapsed_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        timer_section_layout.addWidget(self.timer_elapsed_label)
        timer_section_layout.addStretch()

        left_layout.addWidget(timer_section)

        # 3. Fecha de Vencimiento
        due_section = QWidget()
        due_layout = QHBoxLayout(due_section)
        due_layout.setContentsMargins(0, 0, 0, 0)
        due_layout.setSpacing(10)

        due_layout.addWidget(QLabel(t("task_detail.due_label")))

        self.due_enable_chk = QCheckBox(t("task_detail.due_enable_checkbox"))
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
        self.due_time_chk = QCheckBox(t("task_detail.due_time_checkbox"))
        self.due_time_chk.setCursor(Qt.PointingHandCursor)
        self.due_time_chk.setToolTip(t("task_detail.due_time_tooltip"))
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
        for label in (
            t("task_detail.recurrence_none"), t("task_detail.recurrence_daily"),
            t("task_detail.recurrence_weekly"), t("task_detail.recurrence_monthly")
        ):
            self.recurrence_combo.addItem(label)
        self.recurrence_combo.setToolTip(t("task_detail.recurrence_tooltip"))
        due_layout.addWidget(self.recurrence_combo)
        due_layout.addStretch()

        left_layout.addWidget(due_section)

        # 4. Sección de Etiquetas Múltiples
        tags_section = QWidget()
        tags_layout = QVBoxLayout(tags_section)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(4)

        tags_layout.addWidget(QLabel(t("task_detail.tags_label")))

        self.tags_container_widget = QWidget()
        self.tags_container_layout = QHBoxLayout(self.tags_container_widget)
        self.tags_container_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_container_layout.setSpacing(6)
        self.tags_container_layout.setAlignment(Qt.AlignLeft)
        tags_layout.addWidget(self.tags_container_widget)

        tag_btns_row = QHBoxLayout()
        tag_btns_row.setSpacing(6)
        self.add_tag_btn = QPushButton(t("task_detail.assign_tag_btn"))
        self.add_tag_btn.setCursor(Qt.PointingHandCursor)
        self.add_tag_btn.clicked.connect(self.assign_tag_dialog)
        tag_btns_row.addWidget(self.add_tag_btn)

        self.manage_tags_btn = QPushButton(t("task_detail.manage_tags_btn"))
        self.manage_tags_btn.setToolTip(t("task_detail.manage_tags_tooltip"))
        self.manage_tags_btn.setCursor(Qt.PointingHandCursor)
        self.manage_tags_btn.clicked.connect(self.open_tag_manager)
        tag_btns_row.addWidget(self.manage_tags_btn)
        tag_btns_row.addStretch()
        tags_layout.addLayout(tag_btns_row)

        # Selector rápido de Prioridad, a la derecha de Etiquetas
        priority_section = QWidget()
        priority_layout = QVBoxLayout(priority_section)
        priority_layout.setContentsMargins(0, 0, 0, 0)
        priority_layout.setSpacing(4)
        priority_layout.addWidget(QLabel(t("task_detail.priority_label")))
        self.priority_combo = QComboBox()
        self.priority_combo.setToolTip(t("task_detail.priority_tooltip"))
        self.priority_combo.setCursor(Qt.PointingHandCursor)
        self._refresh_priority_combo()
        self.priority_combo.currentIndexChanged.connect(self._on_priority_changed)
        priority_layout.addWidget(self.priority_combo)
        priority_layout.addStretch()

        # Selector rápido de Tablero vinculado, junto a Etiquetas y Prioridad
        board_link_section = QWidget()
        board_link_layout = QVBoxLayout(board_link_section)
        board_link_layout.setContentsMargins(0, 0, 0, 0)
        board_link_layout.setSpacing(4)
        board_link_layout.addWidget(QLabel(t("task_detail.linked_board_label")))
        self.linked_board_combo = QComboBox()
        self.linked_board_combo.setToolTip(t("task_detail.linked_board_tooltip"))
        self.linked_board_combo.setCursor(Qt.PointingHandCursor)
        board_link_layout.addWidget(self.linked_board_combo)
        board_link_layout.addStretch()

        tags_priority_row = QHBoxLayout()
        tags_priority_row.setSpacing(12)
        tags_priority_row.addWidget(tags_section, 2)
        tags_priority_row.addWidget(priority_section, 1)
        tags_priority_row.addWidget(board_link_section, 1)
        left_layout.addLayout(tags_priority_row)

        # 5. Enlaces / adjuntos
        links_section = QWidget()
        links_outer = QVBoxLayout(links_section)
        links_outer.setContentsMargins(0, 0, 0, 0)
        links_outer.setSpacing(4)
        links_outer.addWidget(QLabel(t("task_detail.links_label")))

        self.links_container = QWidget()
        self.links_layout = QVBoxLayout(self.links_container)
        self.links_layout.setContentsMargins(0, 0, 0, 0)
        self.links_layout.setSpacing(2)
        links_outer.addWidget(self.links_container)

        add_link_row = QHBoxLayout()
        add_link_row.setSpacing(6)
        self.browse_link_btn = QPushButton("📁")
        self.browse_link_btn.setFixedWidth(30)
        self.browse_link_btn.setCursor(Qt.PointingHandCursor)
        self.browse_link_btn.setToolTip(t("task_detail.browse_file_tooltip"))
        self.browse_link_btn.clicked.connect(self.browse_local_file)
        add_link_row.addWidget(self.browse_link_btn)
        self.link_url_input = QLineEdit()
        self.link_url_input.setPlaceholderText(t("task_detail.link_url_placeholder"))
        self.link_url_input.returnPressed.connect(self.add_link)
        add_link_row.addWidget(self.link_url_input, 2)
        self.link_label_input = QLineEdit()
        self.link_label_input.setPlaceholderText(t("task_detail.link_label_placeholder"))
        add_link_row.addWidget(self.link_label_input, 1)
        add_link_btn = QPushButton("➕")
        add_link_btn.setFixedWidth(30)
        add_link_btn.setCursor(Qt.PointingHandCursor)
        add_link_btn.setToolTip(t("task_detail.add_link_tooltip"))
        add_link_btn.clicked.connect(self.add_link)
        add_link_row.addWidget(add_link_btn)
        links_outer.addLayout(add_link_row)

        left_layout.addWidget(links_section)
        left_layout.addStretch()

        # Botones de Acción de la Tarea (Guardar, Eliminar, Cerrar)
        action_layout = QHBoxLayout()

        self.delete_task_btn = QPushButton(t("task_detail.delete_task_btn"))
        self.delete_task_btn.setObjectName("DangerButton")
        self.delete_task_btn.setCursor(Qt.PointingHandCursor)
        self.delete_task_btn.clicked.connect(self.delete_task)
        action_layout.addWidget(self.delete_task_btn)

        action_layout.addStretch()

        self.save_btn = QPushButton(t("task_detail.save_btn"))
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_changes)
        action_layout.addWidget(self.save_btn)

        self.close_btn = QPushButton(t("task_detail.close_btn"))
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

        right_layout.addWidget(QLabel(t("task_detail.log_header")))

        # Área de Scroll para ver el historial
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.logs_container = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_container)
        self.logs_layout.setContentsMargins(6, 6, 6, 6)
        self.logs_layout.setSpacing(8)

        self.scroll_area.setWidget(self.logs_container)
        right_layout.addWidget(self.scroll_area, 1)  # el historial domina el alto

        # Caja de entrada para nuevos logs
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)

        self.log_input = MarkdownTextEdit()
        self.log_input.setPlaceholderText(t("task_detail.log_input_placeholder"))
        # Caja cómoda que crece con el texto (sin límite de caracteres; solo tope visual)
        self.log_input.setMinimumHeight(110)
        self.log_input.setMaximumHeight(260)
        # Las imágenes pegadas en el chat se ajustan al ancho del histórico (más estrecho)
        self.log_input.image_width_provider = self._chat_image_width
        input_layout.addWidget(RichTextToolbar(self.log_input))
        input_layout.addWidget(self.log_input)

        log_btn_layout = QHBoxLayout()
        log_btn_layout.addStretch()
        self.add_log_btn = QPushButton(t("task_detail.add_log_btn"))
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
            QMessageBox.critical(self, t("task_detail.load_error_title"), t("task_detail.load_error_body"))
            self.reject()
            return

        self.title_input.setText(task["title"])
        self.desc_input.setHtml(task["description"] or "")

        # Cargar temporizador
        self._timer_started_at = task.get("timer_started_at")
        self._refresh_timer_ui()

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

        # Cargar tablero vinculado
        self._refresh_linked_board_combo(task.get("linked_board_id"))

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
            hint = QLabel(t("task_detail.no_tags_hint"))
            hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;")
            self.tags_container_layout.addWidget(hint)
            self._sync_priority_combo_selection()
            return

        for index, tag in enumerate(self.current_tags):
            pill = ClickableTagPill()
            pill.setObjectName("TagPillFrame")
            pill.setCursor(Qt.PointingHandCursor)
            pill.setToolTip(t("task_detail.tag_pill_tooltip"))
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
            del_btn.setToolTip(t("task_detail.tag_pill_remove_tooltip"))
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

        self._sync_priority_combo_selection()

    def _ensure_priority_category(self):
        """Devuelve el id de la etiqueta permanente «Prioridad», asegurando que existan sus
        niveles por defecto (Baja/Media/Alta) sin duplicar valores que ya existan (p. ej. la
        etiqueta de ejemplo «Prioridad: Alta» del onboarding)."""
        cat_id = database.create_tag_category(t("task_detail.priority_category_name"), self.db_path)
        defaults = (
            (t("task_detail.priority_low"), "#10b981"),
            (t("task_detail.priority_medium"), "#f59e0b"),
            (t("task_detail.priority_high"), "#ef4444"),
        )
        for value, color in defaults:
            if not database.value_exists_in_category(cat_id, value, db_path=self.db_path):
                database.create_tag_value(cat_id, value, color, self.db_path)
        return cat_id

    def _refresh_priority_combo(self):
        """Rellena el selector rápido de Prioridad con los valores actuales del catálogo
        (categoría «Prioridad», creada bajo demanda) y refleja la prioridad de la tarea."""
        self._priority_category_id = self._ensure_priority_category()
        self.priority_combo.blockSignals(True)
        self.priority_combo.clear()
        self.priority_combo.addItem(t("task_detail.priority_none"), None)
        # Orden Baja/Media/Alta para los niveles por defecto en vez del orden alfabético
        # genérico del catálogo; cualquier valor adicional que el usuario añada va detrás.
        order = [t("task_detail.priority_low"), t("task_detail.priority_medium"), t("task_detail.priority_high")]
        values = database.get_tag_values(self._priority_category_id, self.db_path)
        values.sort(key=lambda v: (order.index(v["value"]) if v["value"] in order else len(order), v["value"]))
        for value in values:
            self.priority_combo.addItem(color_icon(value["color"]), value["value"], value["id"])
        self.priority_combo.blockSignals(False)
        self._sync_priority_combo_selection()

    def _sync_priority_combo_selection(self):
        """Ajusta la selección del combo de Prioridad a lo que haya en current_tags,
        sin disparar _on_priority_changed."""
        current = next(
            (tg for tg in self.current_tags if tg.get("category_id") == self._priority_category_id),
            None
        )
        self.priority_combo.blockSignals(True)
        if current:
            idx = self.priority_combo.findData(current["tag_value_id"])
            self.priority_combo.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.priority_combo.setCurrentIndex(0)
        self.priority_combo.blockSignals(False)

    def _on_priority_changed(self, index):
        value_id = self.priority_combo.currentData()
        if value_id is None:
            self.current_tags = [
                tg for tg in self.current_tags if tg.get("category_id") != self._priority_category_id
            ]
            self.render_tags()
        else:
            tag = database.get_tag_value(value_id, self.db_path)
            if tag:
                self._set_category_value(tag)

    def _refresh_linked_board_combo(self, current_board_id):
        """Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo el
        propio tablero de la tarea, para no poder enlazarla consigo misma) y selecciona el
        vínculo actual de la tarea, si tiene uno."""
        own_board_id = database.get_task_board_id(self.task_id, self.db_path)
        self.linked_board_combo.blockSignals(True)
        self.linked_board_combo.clear()
        self.linked_board_combo.addItem(t("task_detail.linked_board_none"), None)
        for board in database.get_boards(self.db_path):
            if board["id"] != own_board_id:
                self.linked_board_combo.addItem(color_icon(board["color"]), board["name"], board["id"])
        idx = self.linked_board_combo.findData(current_board_id) if current_board_id else 0
        self.linked_board_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.linked_board_combo.blockSignals(False)

    def _set_category_value(self, tag):
        """Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un
        único valor por etiqueta en la tarea y conservando la posición existente."""
        idx = next(
            (i for i, tg in enumerate(self.current_tags)
             if tg["category"].lower() == tag["category"].lower()),
            None
        )
        if idx is None:
            self.current_tags.append(tag)
        else:
            self.current_tags[idx] = tag
            # Eliminar cualquier duplicado posterior de la misma etiqueta
            self.current_tags = [
                tg for i, tg in enumerate(self.current_tags)
                if i == idx or tg["category"].lower() != tag["category"].lower()
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
            QMessageBox.warning(self, t("task_detail.warn_title"), t("task_detail.warn_empty_title"))
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

        # Guardar el tablero vinculado
        database.set_task_linked_board(self.task_id, self.linked_board_combo.currentData(), self.db_path)

        self.modified = True
        self.accept()

    def _on_timer_toggle_clicked(self):
        """Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción
        instantánea (como añadir una nota al diario o un enlace): se persiste en el
        momento, no espera a "Guardar Cambios"."""
        self._timer_started_at = datetime.now().isoformat()
        database.set_task_timer_started(self.task_id, self._timer_started_at, self.db_path)
        self.modified = True
        self._refresh_timer_ui()

    def _on_timer_clear_clicked(self):
        """Detiene y borra el temporizador: deja de contar y quita la insignia de la tarjeta."""
        self._timer_started_at = None
        database.set_task_timer_started(self.task_id, None, self.db_path)
        self.modified = True
        self._refresh_timer_ui()

    def _refresh_timer_ui(self):
        """Actualiza el botón y la etiqueta de tiempo transcurrido según self._timer_started_at.
        Se llama al cargar la tarea, tras cada acción, y cada 30s mientras el diálogo está
        abierto (self._timer_refresh_timer) para que el contador avance en vivo."""
        if self._timer_started_at:
            self.timer_toggle_btn.setText(t("task_detail.timer_restart_btn"))
            self.timer_clear_btn.show()
            try:
                started = datetime.fromisoformat(self._timer_started_at)
                elapsed = datetime.now() - started
                self.timer_elapsed_label.setText(
                    t("task_detail.timer_elapsed", elapsed=styles.format_elapsed_time(elapsed.total_seconds()))
                )
            except ValueError:
                self.timer_elapsed_label.setText("")
        else:
            self.timer_toggle_btn.setText(t("task_detail.timer_start_btn"))
            self.timer_clear_btn.hide()
            self.timer_elapsed_label.setText("")

    def delete_task(self):
        """Borra definitivamente la tarea actual de la base de datos."""
        confirm = QMessageBox.question(
            self,
            t("task_detail.delete_task_title"),
            t("task_detail.delete_task_body"),
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
            hint = QLabel(t("task_detail.no_links_hint"))
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

        is_local = _is_local_link(link["url"])
        missing = is_local and not os.path.exists(link["url"])
        icon = "📎" if is_local else "🔗"

        open_btn = QPushButton(icon + " " + (link["label"] or link["url"]))
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setToolTip(
            t("task_detail.link_missing_tooltip", path=link["url"]) if missing else link["url"]
        )
        text_color = styles.COLORS["danger"] if missing else "#60a5fa"
        open_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {text_color}; text-align: left; }}"
            "QPushButton:hover { text-decoration: underline; }"
        )
        open_btn.clicked.connect(lambda _=False, url=link["url"], loc=is_local: self._open_link(url, loc))
        h.addWidget(open_btn, 1)
        del_btn = QPushButton()
        del_btn.setFixedSize(18, 18)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip(t("task_detail.delete_link_tooltip"))
        del_btn.setIcon(make_glyph_icon("cross", "#ef4444", 12))
        del_btn.setIconSize(QSize(12, 12))
        del_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        del_btn.clicked.connect(lambda _=False, lid=link["id"]: self.remove_link(lid))
        h.addWidget(del_btn)
        return row

    def _open_link(self, url, is_local):
        qurl = QUrl.fromLocalFile(url) if is_local else QUrl(url)
        if not QDesktopServices.openUrl(qurl):
            QMessageBox.warning(
                self, t("task_detail.link_open_failed_title"), t("task_detail.link_open_failed_msg")
            )

    def browse_local_file(self):
        path, _ = QFileDialog.getOpenFileName(self, t("task_detail.browse_file_title"))
        if path:
            self._apply_browsed_file(path)

    def _apply_browsed_file(self, path):
        self.link_url_input.setText(path)
        if not self.link_label_input.text().strip():
            self.link_label_input.setText(os.path.basename(path))

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
        self.logs_layout.addStretch()

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
            t("task_detail.delete_log_title"),
            t("task_detail.delete_log_body"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            database.delete_log(log_id, self.db_path)
            self.modified = True
            widget.deleteLater()

    def scroll_to_bottom(self):
        """Mueve la barra de desplazamiento del diario hasta abajo."""
        # Usamos un timer de un solo disparo ya que Qt a veces tarda un instante en
        # actualizar el scroll máximo tras repintar. Parentado a self (en vez de un
        # QTimer.singleShot suelto) para que Qt lo destruya junto con el diálogo -- uno
        # sin padre sigue vivo y puede disparar más tarde contra un scrollbar ya
        # destruido si el diálogo se cierra antes de que pasen los 50ms.
        scrollbar = self.scroll_area.verticalScrollBar()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: scrollbar.setValue(scrollbar.maximum()))
        timer.start(50)
