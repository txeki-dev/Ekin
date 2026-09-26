"""
Diálogos para la selección, creación y gestión de plantillas de tableros en Ekin Kanban.
"""

from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from color_picker import ColorCirclesPicker
from icons import lucide_icon
from strings import t
import styles
import templates
import database
from templates import BoardTemplate
from widgets import FlowLayout


class TemplateCardWidget(QFrame):
    """Tarjeta interactiva para visualizar y seleccionar una plantilla de tablero."""
    selected_changed = Signal(str)  # Emite el template.id al ser seleccionada
    delete_requested = Signal(str)  # Emite el template.id para plantillas personalizadas

    def __init__(self, template: BoardTemplate, selected: bool = False, parent=None):
        super().__init__(parent)
        self.template = template
        self.is_selected = selected
        self.setCursor(Qt.PointingHandCursor)
        self.init_ui()
        self.update_style()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Fila superior: Icono + Título + Badge de Categoría + Botón borrar si custom
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        # Icono
        icon_lbl = QLabel()
        icon_lbl.setPixmap(lucide_icon(self.template.icon, self.template.color, 20).pixmap(20, 20))
        icon_lbl.setStyleSheet("background: transparent;")
        top_row.addWidget(icon_lbl)

        # Nombre de la plantilla
        title_lbl = QLabel(self.template.name)
        title_lbl.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {styles.COLORS['text_main']}; background: transparent;")
        title_lbl.setWordWrap(True)
        top_row.addWidget(title_lbl)

        # Badge de Categoría
        cat_lbl = QLabel(f" {self.template.category} ")
        cat_lbl.setStyleSheet(f"""
            background-color: {styles.COLORS['bg_hover']};
            color: {styles.COLORS['text_muted']};
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            padding: 2px 4px;
        """)
        top_row.addWidget(cat_lbl)
        top_row.addStretch()

        # Botón de eliminar si es personalizada
        if not self.template.is_builtin:
            del_btn = QPushButton()
            del_btn.setIcon(lucide_icon("trash-2", styles.COLORS['text_muted'], 14))
            del_btn.setIconSize(QSize(14, 14))
            del_btn.setFixedSize(24, 24)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet("QPushButton { border: none; background: transparent; } QPushButton:hover { background: #fee2e2; border-radius: 4px; }")
            del_btn.setToolTip(t("templates.delete_confirm_title"))
            del_btn.clicked.connect(lambda: self.delete_requested.emit(self.template.id))
            top_row.addWidget(del_btn)

        layout.addLayout(top_row)

        # Descripción
        if self.template.description:
            desc_lbl = QLabel(self.template.description)
            desc_lbl.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_soft']}; background: transparent;")
            desc_lbl.setWordWrap(True)
            layout.addWidget(desc_lbl)

        # Flujo de columnas (chips visuales con salto de línea automático)
        cols_flow = FlowLayout(margin=0, spacing=6)
        if self.template.columns:
            for col in self.template.columns:
                wip_str = f" ({col.wip_limit})" if col.wip_limit else ""
                chip = QLabel(f"{col.name}{wip_str}")
                chip.setStyleSheet(f"""
                    background-color: {styles.COLORS['bg_main']};
                    color: {styles.COLORS['text_main']};
                    border-left: 3px solid {col.color};
                    border-radius: 3px;
                    font-size: 11px;
                    padding: 2px 6px;
                """)
                cols_flow.addWidget(chip)
        else:
            chip = QLabel(t("templates.create_dialog.no_columns"))
            chip.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['text_muted']}; font-style: italic; background: transparent;")
            cols_flow.addWidget(chip)

        layout.addLayout(cols_flow)

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet(f"""
                TemplateCardWidget {{
                    background-color: {styles.COLORS['accent_tint']};
                    border: 2px solid {styles.COLORS['accent']};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                TemplateCardWidget {{
                    background-color: {styles.COLORS['bg_card']};
                    border: 1px solid {styles.COLORS['border']};
                    border-radius: 10px;
                }}
                TemplateCardWidget:hover {{
                    background-color: {styles.COLORS['bg_hover']};
                    border: 1px solid {styles.COLORS['border_dashed']};
                }}
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_changed.emit(self.template.id)
        super().mousePressEvent(event)


class CreateBoardDialog(QDialog):
    """Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o en blanco."""

    def __init__(self, parent=None, templates_dir: Optional[str] = None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.templates_dir = templates_dir
        self.db_path = db_path
        self.connect_requested = False
        self.selected_template: BoardTemplate = templates.TEMPLATE_SOFTWARE_AGILE
        self.card_widgets: List[TemplateCardWidget] = []

        self.setWindowTitle(t("templates.create_dialog.title"))
        self.resize(680, 620)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. Cabecera
        header_title = QLabel(t("templates.create_dialog.title"))
        header_title.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 22px; "
            f"font-weight: bold; color: {styles.COLORS['text_main']};"
        )
        main_layout.addWidget(header_title)

        subtitle = QLabel(t("templates.create_dialog.subtitle"))
        subtitle.setStyleSheet(f"font-size: 13px; color: {styles.COLORS['text_muted']};")
        main_layout.addWidget(subtitle)

        # 2. Filtros de categoría (Píldoras)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        self.category_group = QButtonGroup(self)

        categories = [
            ("all", t("templates.category.all")),
            ("builtin", t("templates.category.builtin")),
            ("custom", t("templates.category.custom")),
        ]
        for idx, (cat_key, cat_label) in enumerate(categories):
            btn = QPushButton(cat_label)
            btn.setCheckable(True)
            btn.setChecked(idx == 0)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {styles.COLORS['bg_card']};
                    border: 1px solid {styles.COLORS['border']};
                    border-radius: 14px;
                    padding: 4px 12px;
                    font-size: 12px;
                    color: {styles.COLORS['text_soft']};
                }}
                QPushButton:checked {{
                    background: {styles.COLORS['accent']};
                    border-color: {styles.COLORS['accent']};
                    color: {styles.COLORS['on_accent']};
                    font-weight: bold;
                }}
            """)
            self.category_group.addButton(btn, idx)
            filter_layout.addWidget(btn)

        self.category_group.idClicked.connect(self._on_category_filter_changed)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        # 3. Lista con scroll de tarjetas de plantilla
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 4, 8, 4)
        self.cards_layout.setSpacing(10)

        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll, 1)

        # 4. Sección de personalización (Nombre y Color)
        config_frame = QFrame()
        config_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        config_layout = QVBoxLayout(config_frame)
        config_layout.setSpacing(10)

        # Fila Nombre del Tablero
        name_row = QHBoxLayout()
        name_lbl = QLabel(f"<b>{t('templates.create_dialog.board_name')}:</b>")
        name_lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; border: none; background: transparent;")
        name_row.addWidget(name_lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(t("sidebar.board_edit.name_placeholder"))
        name_row.addWidget(self.name_input, 1)
        config_layout.addLayout(name_row)

        # Fila Color del Tablero
        color_row = QHBoxLayout()
        color_lbl = QLabel(f"<b>{t('templates.create_dialog.board_color')}:</b>")
        color_lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; border: none; background: transparent;")
        color_row.addWidget(color_lbl)

        self.color_picker = ColorCirclesPicker(self.selected_template.color)
        self.color_picker.setStyleSheet("border: none; background: transparent;")
        self.color_picker.color_changed.connect(self._on_color_picked)
        color_row.addWidget(self.color_picker)
        color_row.addStretch()
        config_layout.addLayout(color_row)

        main_layout.addWidget(config_frame)

        # 5. Botones inferiores
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Enlace para conectar carpeta compartida (Sync Cloud)
        self.connect_btn = QPushButton(f" {t('sync.menu_open_shared')}")
        self.connect_btn.setCursor(Qt.PointingHandCursor)
        self.connect_btn.setIcon(lucide_icon("cloud", styles.COLORS['text_soft'], 15))
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {styles.COLORS['text_muted']};
                font-size: 12px;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {styles.COLORS['text_main']};
            }}
        """)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        btn_layout.addWidget(self.connect_btn)

        btn_layout.addStretch()

        self.cancel_btn = QPushButton(t("templates.create_dialog.cancel_btn"))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(t("templates.create_dialog.create_btn"))
        self.ok_btn.setObjectName("PrimaryButton")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(self.ok_btn)

        main_layout.addLayout(btn_layout)

        # Cargar tarjetas iniciales
        self._load_templates()

    def _load_templates(self, filter_mode="all"):
        # Limpiar tarjetas anteriores
        for w in self.card_widgets:
            w.setParent(None)
            w.deleteLater()
        self.card_widgets.clear()

        all_tmpls = templates.get_all_templates(self.templates_dir)
        filtered = []
        for t_item in all_tmpls:
            if filter_mode == "builtin" and not t_item.is_builtin:
                continue
            if filter_mode == "custom" and t_item.is_builtin:
                continue
            filtered.append(t_item)

        # Si la seleccionada actualmente no está en el filtro, tomar la primera
        if filtered and not any(t_item.id == self.selected_template.id for t_item in filtered):
            self.selected_template = filtered[0]

        for tmpl in filtered:
            is_sel = (tmpl.id == self.selected_template.id)
            card = TemplateCardWidget(tmpl, selected=is_sel, parent=self.cards_container)
            card.selected_changed.connect(self._on_template_selected)
            card.delete_requested.connect(self._on_template_delete)
            self.cards_layout.addWidget(card)
            self.card_widgets.append(card)

        self.cards_layout.addStretch()
        self._update_form_with_template(self.selected_template)

    def _on_category_filter_changed(self, btn_id):
        modes = ["all", "builtin", "custom"]
        mode = modes[btn_id] if 0 <= btn_id < len(modes) else "all"
        # Limpiar layout
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.card_widgets.clear()
        self._load_templates(filter_mode=mode)

    def _on_template_selected(self, template_id: str):
        tmpl = templates.get_template_by_id(template_id, self.templates_dir)
        if not tmpl:
            return
        self.selected_template = tmpl
        for card in self.card_widgets:
            card.set_selected(card.template.id == template_id)
        self._update_form_with_template(tmpl)

    def _update_form_with_template(self, tmpl: BoardTemplate):
        self.name_input.setText(tmpl.name)
        self.name_input.selectAll()
        self.color_picker.set_color(tmpl.color)

    def _on_color_picked(self, color: str):
        # Color actualizado por el usuario
        pass

    def _on_template_delete(self, template_id: str):
        tmpl = templates.get_template_by_id(template_id, self.templates_dir)
        name = tmpl.name if tmpl else template_id
        confirm = QMessageBox.question(
            self,
            t("templates.delete_confirm_title"),
            t("templates.delete_confirm_body", name=name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            templates.delete_custom_template(template_id, self.templates_dir)
            active_btn_id = self.category_group.checkedId()
            self._on_category_filter_changed(active_btn_id)

    def _on_connect_clicked(self):
        self.connect_requested = True
        self.accept()

    def _validate_and_accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                t("sidebar.board_edit.warn_title"),
                t("sidebar.board_edit.warn_empty_name"),
            )
            self.name_input.setFocus()
            return
        self.accept()

    def get_data(self):
        return (
            self.name_input.text().strip(),
            self.color_picker.get_color(),
            self.selected_template,
        )


class SaveAsTemplateDialog(QDialog):
    """Diálogo modal para guardar el tablero actual como plantilla personalizada de usuario."""

    def __init__(self, board_id: int, parent=None, templates_dir: Optional[str] = None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.board_id = board_id
        self.templates_dir = templates_dir
        self.db_path = db_path

        self.setWindowTitle(t("templates.save_dialog.title"))
        self.setMinimumWidth(460)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Título
        title = QLabel(t("templates.save_dialog.title"))
        title.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 18px; "
            f"font-weight: bold; color: {styles.COLORS['text_main']};"
        )
        layout.addWidget(title)

        board = database.get_board(self.board_id, db_path=self.db_path)
        board_name = board["name"] if board else "Mi Tablero"

        # Nombre de la plantilla
        layout.addWidget(QLabel(f"<b>{t('templates.save_dialog.name_label')}</b>"))
        self.name_input = QLineEdit(f"{board_name} (Plantilla)")
        layout.addWidget(self.name_input)

        # Categoría
        layout.addWidget(QLabel(f"<b>{t('templates.save_dialog.category_label')}</b>"))
        self.cat_combo = QComboBox()
        self.cat_combo.setEditable(True)
        self.cat_combo.addItems([
            t("templates.category.custom"),
            "Ingeniería & Software",
            "Estudio & Oposiciones",
            "Productividad Personal",
            "General",
        ])
        layout.addWidget(self.cat_combo)

        # Descripción
        layout.addWidget(QLabel(f"<b>{t('templates.save_dialog.desc_label')}</b>"))
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Descripción del flujo de trabajo...")
        layout.addWidget(self.desc_input)

        # Checkbox incluir tareas
        self.include_tasks_chk = QCheckBox(t("templates.save_dialog.include_tasks"))
        self.include_tasks_chk.setChecked(False)
        layout.addWidget(self.include_tasks_chk)

        layout.addSpacing(10)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton(t("templates.save_dialog.cancel_btn"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton(t("templates.save_dialog.save_btn"))
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self._save_template)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _save_template(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                t("sidebar.board_edit.warn_title"),
                t("templates.save_dialog.warn_empty_name"),
            )
            return

        import uuid
        template_id = f"custom_{uuid.uuid4().hex[:8]}"
        desc = self.desc_input.text().strip()
        cat = self.cat_combo.currentText().strip() or "Mis Plantillas"
        inc_tasks = self.include_tasks_chk.isChecked()

        tmpl = templates.export_board_to_template(
            board_id=self.board_id,
            template_id=template_id,
            name=name,
            description=desc,
            category=cat,
            include_tasks=inc_tasks,
            db_path=self.db_path,
        )
        templates.save_custom_template(tmpl, templates_dir=self.templates_dir)

        QMessageBox.information(
            self,
            t("templates.save_dialog.success_title"),
            t("templates.save_dialog.success_body", name=name),
        )
        self.accept()
