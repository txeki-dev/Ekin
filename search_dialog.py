"""Diálogo de búsqueda global de tareas.

Filtra por texto (título/descripción), tablero, etiqueta y vencimiento, y permite
saltar a la tarjeta encontrada emitiendo `task_activated(task_id, board_id)` — el mismo
contrato que usan la campana y el calendario."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QScrollArea, QWidget, QFrame
)
from PySide6.QtGui import QColor, QPixmap, QIcon

import database
import styles


def _swatch_icon(color, size=12):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class SearchDialog(QDialog):
    """Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento."""
    task_activated = Signal(int, int)  # task_id, board_id

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setObjectName("SearchDialog")
        self.setWindowTitle("Buscar tareas")
        self.setMinimumSize(480, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel("🔍 <b>Buscar tareas</b>"))

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Título o descripción…")
        self.text_input.textChanged.connect(self.refresh_results)
        layout.addWidget(self.text_input)

        # Filtros: tablero + etiqueta
        filters = QHBoxLayout()
        filters.setSpacing(8)

        self.board_combo = QComboBox()
        self.board_combo.addItem("Todos los tableros", None)
        for b in database.get_boards(self.db_path):
            self.board_combo.addItem(b["name"], b["id"])
        self.board_combo.currentIndexChanged.connect(self.refresh_results)
        filters.addWidget(self.board_combo, 1)

        self.tag_combo = QComboBox()
        self.tag_combo.addItem("Todas las etiquetas", None)
        for cat in database.get_tag_categories(self.db_path):
            for val in database.get_tag_values(cat["id"], self.db_path):
                self.tag_combo.addItem(f"{cat['name']}: {val['value']}", val["id"])
        self.tag_combo.currentIndexChanged.connect(self.refresh_results)
        filters.addWidget(self.tag_combo, 1)

        layout.addLayout(filters)

        self.due_chk = QCheckBox("Solo con vencimiento")
        self.due_chk.setCursor(Qt.PointingHandCursor)
        self.due_chk.stateChanged.connect(self.refresh_results)
        layout.addWidget(self.due_chk)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(self.count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent;")
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(4)
        self.results_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.results_container)
        layout.addWidget(scroll, 1)

        close_row = QHBoxLayout()
        close_row.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_row.addWidget(close_btn)
        layout.addLayout(close_row)

        self.text_input.setFocus()
        self.refresh_results()

    def refresh_results(self):
        """Reejecuta la búsqueda con los filtros actuales y repinta la lista."""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        results = database.search_tasks(
            text=self.text_input.text().strip(),
            board_id=self.board_combo.currentData(),
            tag_value_id=self.tag_combo.currentData(),
            only_due=self.due_chk.isChecked(),
            db_path=self.db_path,
        )
        self.count_label.setText(f"{len(results)} resultado(s)")

        if not results:
            empty = QLabel("Sin resultados.")
            empty.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-style: italic; padding: 8px 2px;"
            )
            self.results_layout.addWidget(empty)
            return

        for t in results:
            self.results_layout.addWidget(self._build_result(t))

    def _build_result(self, t):
        title = t["title"] or "(sin título)"
        due = f"   📅 {t['due_date']}" if t.get("due_date") else ""
        btn = QPushButton(f"{title}{due}")
        btn.setObjectName("NotificationItem")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(_swatch_icon(t["board_color"]))
        btn.setToolTip(f"{t['board_name']} · {t['column_name']}")
        btn.clicked.connect(
            lambda _=False, tid=t["id"], bid=t["board_id"]: self._activate(tid, bid)
        )
        return btn

    def _activate(self, task_id, board_id):
        self.task_activated.emit(task_id, board_id)
        self.accept()
