"""Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.

Permite definir en una sola vista múltiples tareas especificando título, descripción
y columna de destino, con soporte para añadir/eliminar filas y pegar datos tabulares.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QApplication
)
import database
import styles
from strings import t
from icons import lucide_icon


class BulkAddTaskDialog(QDialog):
    """Diálogo modal con tabla para crear múltiples tareas simultáneamente."""
    def __init__(self, board_id: int, db_path=database.DB_NAME, initial_column_id=None, parent=None):
        super().__init__(parent)
        self.board_id = board_id
        self.db_path = db_path
        self.initial_column_id = initial_column_id
        self.created_count = 0

        self.columns = database.get_columns(self.board_id, self.db_path)

        self.setWindowTitle(t("bulk_add.dialog_title"))
        self.resize(760, 480)
        self.setMinimumSize(640, 360)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # 1. Cabecera e instrucciones
        header = QLabel(t("bulk_add.header"))
        header.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.COLORS['text_main']};")
        layout.addWidget(header)

        instructions = QLabel(t("bulk_add.instructions"))
        instructions.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']};")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # 2. Barra de herramientas de la tabla (Añadir fila, Eliminar fila)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.add_row_btn = QPushButton(f" {t('bulk_add.add_row_btn')}")
        self.add_row_btn.setCursor(Qt.PointingHandCursor)
        self.add_row_btn.setIcon(lucide_icon("plus", styles.COLORS['text_soft'], 14))
        self.add_row_btn.setIconSize(QSize(14, 14))
        self.add_row_btn.clicked.connect(lambda: self.add_table_row())
        toolbar.addWidget(self.add_row_btn)

        self.del_row_btn = QPushButton(f" {t('bulk_add.del_row_btn')}")
        self.del_row_btn.setCursor(Qt.PointingHandCursor)
        self.del_row_btn.setIcon(lucide_icon("trash-2", styles.COLORS['text_soft'], 14))
        self.del_row_btn.setIconSize(QSize(14, 14))
        self.del_row_btn.clicked.connect(self.delete_selected_row)
        toolbar.addWidget(self.del_row_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 3. Tabla de tareas
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            t("bulk_add.col_title"),
            t("bulk_add.col_description"),
            t("bulk_add.col_column"),
        ])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.Stretch)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {styles.COLORS['bg_card']};
                gridline-color: {styles.COLORS['border']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
            }}
            QHeaderView::section {{
                background-color: {styles.COLORS['bg_hover']};
                color: {styles.COLORS['text_main']};
                font-weight: 600;
                padding: 6px;
                border: none;
                border-bottom: 1px solid {styles.COLORS['border']};
            }}
        """)
        layout.addWidget(self.table, 1)

        # Inicializar con 3 filas vacías
        for _ in range(3):
            self.add_table_row()

        # 4. Botones inferiores de acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton(t("bulk_add.cancel_btn"))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.create_btn = QPushButton(t("bulk_add.create_btn"))
        self.create_btn.setObjectName("PrimaryButton")
        self.create_btn.setCursor(Qt.PointingHandCursor)
        self.create_btn.clicked.connect(self.create_tasks)
        btn_layout.addWidget(self.create_btn)

        layout.addLayout(btn_layout)

    def _make_column_combo(self):
        combo = QComboBox()
        combo.setCursor(Qt.PointingHandCursor)
        selected_idx = 0
        for i, col in enumerate(self.columns):
            combo.addItem(col["name"], col["id"])
            if self.initial_column_id and col["id"] == self.initial_column_id:
                selected_idx = i
        if self.columns:
            combo.setCurrentIndex(selected_idx)
        return combo

    def add_table_row(self, title="", description="", column_id=None):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)

        title_item = QTableWidgetItem(title)
        self.table.setItem(row_idx, 0, title_item)

        desc_item = QTableWidgetItem(description)
        self.table.setItem(row_idx, 1, desc_item)

        combo = self._make_column_combo()
        if column_id is not None:
            idx = combo.findData(column_id)
            if idx >= 0:
                combo.setCurrentIndex(idx)
        self.table.setCellWidget(row_idx, 2, combo)

        self.table.setCurrentCell(row_idx, 0)

    add_row = add_table_row

    def delete_selected_row(self):
        curr_row = self.table.currentRow()
        if curr_row >= 0:
            self.table.removeRow(curr_row)
        elif self.table.rowCount() > 0:
            self.table.removeRow(self.table.rowCount() - 1)

    def keyPressEvent(self, event):
        # Permitir pegar filas copiadas de Excel / Sheets con Ctrl+V
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if text and ("\n" in text or "\t" in text):
                self._paste_tabular_text(text)
                event.accept()
                return
        super().keyPressEvent(event)

    def _paste_tabular_text(self, text: str):
        lines = [ln for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if ln.strip()]
        if not lines:
            return

        for line in lines:
            parts = line.split("\t")
            title = parts[0].strip() if len(parts) > 0 else ""
            desc = parts[1].strip() if len(parts) > 1 else ""
            col_name = parts[2].strip().lower() if len(parts) > 2 else ""

            matched_col_id = None
            if col_name:
                for col in self.columns:
                    if col["name"].lower() == col_name:
                        matched_col_id = col["id"]
                        break

            if title or desc:
                self.add_table_row(title=title, description=desc, column_id=matched_col_id)

    def create_tasks(self):
        """Valida e inserta las tareas definidas en la tabla."""
        if not self.columns:
            QMessageBox.warning(self, t("tag_manager.warn_title"), "No hay columnas disponibles en este tablero.")
            return

        tasks_to_create = []
        for row in range(self.table.rowCount()):
            title_item = self.table.item(row, 0)
            desc_item = self.table.item(row, 1)
            combo = self.table.cellWidget(row, 2)

            title = title_item.text().strip() if title_item else ""
            desc = desc_item.text().strip() if desc_item else ""
            col_id = combo.currentData() if isinstance(combo, QComboBox) else (self.columns[0]["id"] if self.columns else None)

            if title:
                tasks_to_create.append((col_id, title, desc))

        if not tasks_to_create:
            QMessageBox.warning(self, t("tag_manager.warn_title"), t("bulk_add.warn_no_tasks"))
            return

        created_ids = database.create_tasks_batch(tasks_to_create, db_path=self.db_path)
        self.created_count = len(created_ids)
        self.accept()

    _on_create = create_tasks
