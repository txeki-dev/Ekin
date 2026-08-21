"""Diálogos para Exportación e Importación avanzada de tableros en Ekin.

Proporciona:
- `ExportDialog`: selector de alcance (todos o tablero activo), formato (JSON/CSV/MD),
  y opción de volcado completo vs. solo estructura (plantilla).
- `ImportConfirmationDialog`: vista previa del contenido JSON detectado y selector
  de modo de importación (completo vs. plantilla de columnas sin tareas).
"""
import os
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QCheckBox, QButtonGroup, QGroupBox, QFileDialog, QMessageBox, QFrame
)

import database
import exporter
import importer
import styles
from strings import t


def _slugify(name):
    """Genera una cadena amigable para nombres de archivo."""
    s = re.sub(r"[^\w\s-]", "", name.lower())
    return re.sub(r"[-\s]+", "_", s).strip("_") or "tablero"


class ExportDialog(QDialog):
    """Diálogo modal para configurar y ejecutar la exportación de tableros."""

    def __init__(self, db_path=database.DB_NAME, active_board_id=None, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.active_board_id = active_board_id
        self.active_board_name = None
        if self.active_board_id:
            board = database.get_board(self.active_board_id, self.db_path)
            if board:
                self.active_board_name = board["name"]

        self.setWindowTitle(t("export_dialog.window_title"))
        self.setMinimumWidth(480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # 1. Grupo de Alcance (Scope)
        scope_group = QGroupBox(t("export_dialog.scope_group"))
        scope_layout = QVBoxLayout(scope_group)
        scope_layout.setSpacing(8)

        self.scope_btn_group = QButtonGroup(self)
        self.radio_all = QRadioButton(t("export_dialog.scope_all"))
        self.scope_btn_group.addButton(self.radio_all, 0)
        scope_layout.addWidget(self.radio_all)

        current_label = t("export_dialog.scope_current", name=self.active_board_name or "")
        self.radio_current = QRadioButton(current_label)
        self.scope_btn_group.addButton(self.radio_current, 1)
        scope_layout.addWidget(self.radio_current)

        if self.active_board_id and self.active_board_name:
            self.radio_current.setChecked(True)
        else:
            self.radio_current.setEnabled(False)
            self.radio_all.setChecked(True)

        layout.addWidget(scope_group)

        # 2. Grupo de Formato
        format_group = QGroupBox(t("export_dialog.format_group"))
        format_layout = QVBoxLayout(format_group)
        format_layout.setSpacing(10)

        self.format_btn_group = QButtonGroup(self)

        # Opción JSON
        self.radio_json = QRadioButton(t("export_dialog.format_json"))
        self.format_btn_group.addButton(self.radio_json, 0)
        self.radio_json.setChecked(True)
        format_layout.addWidget(self.radio_json)

        # Subopciones JSON
        json_sub_frame = QFrame()
        json_sub_frame.setStyleSheet("margin-left: 20px;")
        json_sub_layout = QVBoxLayout(json_sub_frame)
        json_sub_layout.setContentsMargins(0, 0, 0, 0)
        json_sub_layout.setSpacing(4)

        self.check_json_tasks = QCheckBox(t("export_dialog.json_include_tasks"))
        self.check_json_tasks.setChecked(True)
        json_sub_layout.addWidget(self.check_json_tasks)

        self.label_json_hint = QLabel(t("export_dialog.json_template_hint"))
        self.label_json_hint.setStyleSheet(
            f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;"
        )
        self.label_json_hint.setWordWrap(True)
        json_sub_layout.addWidget(self.label_json_hint)
        format_layout.addWidget(json_sub_frame)

        # Opción CSV
        self.radio_csv = QRadioButton(t("export_dialog.format_csv"))
        self.format_btn_group.addButton(self.radio_csv, 1)
        format_layout.addWidget(self.radio_csv)

        # Opción Markdown
        self.radio_md = QRadioButton(t("export_dialog.format_markdown"))
        self.format_btn_group.addButton(self.radio_md, 2)
        format_layout.addWidget(self.radio_md)

        # Subopciones MD
        md_sub_frame = QFrame()
        md_sub_frame.setStyleSheet("margin-left: 20px;")
        md_sub_layout = QVBoxLayout(md_sub_frame)
        md_sub_layout.setContentsMargins(0, 0, 0, 0)
        self.check_md_details = QCheckBox(t("export_dialog.md_include_details"))
        self.check_md_details.setChecked(True)
        md_sub_layout.addWidget(self.check_md_details)
        format_layout.addWidget(md_sub_frame)

        layout.addWidget(format_group)

        # Habilitar/deshabilitar subopciones según el formato seleccionado
        def _update_options_state():
            is_json = self.radio_json.isChecked()
            is_md = self.radio_md.isChecked()
            self.check_json_tasks.setEnabled(is_json)
            self.label_json_hint.setEnabled(is_json)
            self.check_md_details.setEnabled(is_md)

        self.radio_json.toggled.connect(lambda _: _update_options_state())
        self.radio_csv.toggled.connect(lambda _: _update_options_state())
        self.radio_md.toggled.connect(lambda _: _update_options_state())
        _update_options_state()

        # 3. Botones de Acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(t("export_dialog.cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        export_action_btn = QPushButton(t("export_dialog.export_btn"))
        export_action_btn.setObjectName("PrimaryButton")
        export_action_btn.setCursor(Qt.PointingHandCursor)
        export_action_btn.clicked.connect(self._do_export)
        buttons_layout.addWidget(export_action_btn)

        layout.addLayout(buttons_layout)

    def _do_export(self):
        # Determinar alcance
        is_single = self.radio_current.isChecked()
        target_board_id = self.active_board_id if is_single else None

        # Determinar nombre por defecto y generador
        if self.radio_json.isChecked():
            include_tasks = self.check_json_tasks.isChecked()
            suffix = "_plantilla" if not include_tasks else ""
            if is_single and self.active_board_name:
                default_name = f"ekin_{_slugify(self.active_board_name)}{suffix}.json"
            else:
                default_name = f"ekin_export{suffix}.json"
            file_filter = "JSON (*.json)"
            label = "JSON"

            def build_content():
                return exporter.boards_to_json(
                    self.db_path, board_id=target_board_id, include_tasks=include_tasks
                )

        elif self.radio_csv.isChecked():
            if is_single and self.active_board_name:
                default_name = f"ekin_{_slugify(self.active_board_name)}_tareas.csv"
            else:
                default_name = "ekin_tareas.csv"
            file_filter = "CSV (*.csv)"
            label = "CSV"

            def build_content():
                return exporter.tasks_to_csv(self.db_path, board_id=target_board_id)

        else:  # Markdown
            include_details = self.check_md_details.isChecked()
            if is_single and self.active_board_name:
                default_name = f"ekin_{_slugify(self.active_board_name)}_informe.md"
            else:
                default_name = "ekin_informe.md"
            file_filter = "Markdown (*.md)"
            label = "Markdown"

            def build_content():
                return exporter.report_markdown(
                    self.db_path, board_id=target_board_id,
                    include_descriptions=include_details,
                    include_logs=include_details,
                    include_links=include_details,
                )

        path, _ = QFileDialog.getSaveFileName(
            self, t("export_dialog.save_title"), default_name, file_filter
        )
        if not path:
            return

        try:
            content = build_content()
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(content)
        except Exception as exc:
            QMessageBox.critical(
                self, t("export_dialog.error_title"),
                t("export_dialog.error_body", error=exc)
            )
            return

        QMessageBox.information(
            self, t("export_dialog.done_title"),
            t("export_dialog.done_body", label=label, path=path)
        )
        self.accept()


class ImportConfirmationDialog(QDialog):
    """Diálogo modal para confirmar la importación de tableros desde JSON."""

    def __init__(self, filepath, boards_data, stats, db_path=database.DB_NAME, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.boards_data = boards_data
        self.stats = stats
        self.db_path = db_path
        self.created_board_ids = []

        self.setWindowTitle(t("import_dialog.window_title"))
        self.setMinimumWidth(480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Información del archivo
        filename = os.path.basename(self.filepath)
        file_label = QLabel(t("import_dialog.file_label", filename=filename))
        layout.addWidget(file_label)

        # Resumen de elementos detectados
        summary_card = QFrame()
        summary_card.setStyleSheet(
            f"background: {styles.COLORS['bg_sidebar']}; border: 1px solid {styles.COLORS['border']}; "
            f"border-radius: 6px; padding: 10px;"
        )
        card_layout = QVBoxLayout(summary_card)
        card_layout.setContentsMargins(8, 8, 8, 8)

        stats_text = t(
            "import_dialog.summary_label",
            boards=self.stats["boards"],
            columns=self.stats["columns"],
            tasks=self.stats["tasks"]
        )
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        card_layout.addWidget(stats_label)
        layout.addWidget(summary_card)

        # Opciones de importación si hay tareas en el archivo
        options_group = QGroupBox(t("import_dialog.options_group"))
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(8)

        self.radio_full = QRadioButton(t("import_dialog.opt_full"))
        self.radio_structure = QRadioButton(t("import_dialog.opt_structure_only"))

        if self.stats["tasks"] > 0:
            self.radio_full.setChecked(True)
            options_layout.addWidget(self.radio_full)
            options_layout.addWidget(self.radio_structure)
        else:
            self.radio_structure.setChecked(True)
            hint_label = QLabel(t("import_dialog.template_only_hint"))
            hint_label.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-size: 11px; font-style: italic;"
            )
            options_layout.addWidget(hint_label)

        layout.addWidget(options_group)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton(t("import_dialog.cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        import_action_btn = QPushButton(t("import_dialog.import_btn"))
        import_action_btn.setObjectName("PrimaryButton")
        import_action_btn.setCursor(Qt.PointingHandCursor)
        import_action_btn.clicked.connect(self._do_import)
        buttons_layout.addWidget(import_action_btn)

        layout.addLayout(buttons_layout)

    def _do_import(self):
        include_tasks = self.radio_full.isChecked() if self.stats["tasks"] > 0 else False
        try:
            self.created_board_ids = importer.import_boards(
                self.boards_data, self.db_path, include_tasks=include_tasks
            )
        except Exception as exc:
            QMessageBox.critical(
                self, t("import_dialog.error_title"),
                t("import_dialog.error_body", error=exc)
            )
            return

        self.accept()
