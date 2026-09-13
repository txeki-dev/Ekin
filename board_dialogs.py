"""Diálogos y componentes de interfaz auxiliares para la gestión de columnas y tableros en Ekin."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QLineEdit, QComboBox, QMessageBox, QSpinBox
)
import database
from strings import t
from color_picker import ColorCirclesPicker
from widgets import ColumnWidget


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
    def __init__(self, title="Editar Columna", name="", color="#3b82f6", wip_limit=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(440)
        self.color = color

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Nombre de la columna
        layout.addWidget(QLabel(t("board_view.column_edit.name_label")))
        self.name_input = QLineEdit(name)
        self.name_input.setPlaceholderText(t("board_view.column_edit.name_placeholder"))
        layout.addWidget(self.name_input)

        # Color de la columna: círculos preseleccionados
        layout.addWidget(QLabel(t("board_view.column_edit.color_label")))
        self.color_picker = ColorCirclesPicker(self.color)
        self.color_picker.color_changed.connect(self._on_color_picked)
        layout.addWidget(self.color_picker)

        # Límite WIP (0 = sin límite): aviso visual cuando la columna lo supera
        layout.addWidget(QLabel(t("board_view.column_edit.wip_label")))
        self.wip_input = QSpinBox()
        self.wip_input.setRange(0, 99)
        self.wip_input.setValue(int(wip_limit or 0))
        self.wip_input.setSpecialValueText(t("board_view.column_edit.wip_none"))  # texto para el 0
        layout.addWidget(self.wip_input)
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

    def _on_color_picked(self, color):
        self.color = color

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, t("board_view.column_edit.warn_title"), t("board_view.column_edit.warn_empty_name")
            )
            return
        self.accept()

    def get_data(self):
        wip = self.wip_input.value()
        return self.name_input.text().strip(), self.color, (wip or None)


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
