"""Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando
database.search_tasks, el mismo backend que la búsqueda global) y ofrece comandos de la
app, más captura rápida de tareas escribiendo `+ <título>`.

Contratos de señal:
  - command_invoked(command_id)          -> MainWindow ejecuta la acción.
  - task_activated(task_id, board_id)     -> saltar a la tarea (como campana/búsqueda).
  - quick_capture_requested(title)        -> crear una tarea con ese título.
"""
from functools import partial

from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget, QFrame
)
from PySide6.QtGui import QColor, QPixmap, QIcon

import database
import styles
from icons import lucide_icon
from strings import t

# Máximo de tareas mostradas para no desbordar la lista.
MAX_TASK_RESULTS = 8


def _swatch_icon(color, size=12):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class CommandPalette(QDialog):
    command_invoked = Signal(str)
    task_activated = Signal(int, int)
    quick_capture_requested = Signal(str)

    def __init__(self, db_path, commands, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.db_path = db_path
        self.commands = list(commands)  # [(command_id, label), ...]
        self._rows = []                 # [(button, activate_callable), ...]
        self._selected = -1
        self.setObjectName("CommandPalette")
        self.setWindowTitle(t("palette.window_title"))
        self.setMinimumWidth(560)
        self.resize(560, 460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.input = QLineEdit()
        self.input.setPlaceholderText(t("palette.placeholder"))
        self.input.textChanged.connect(self.refresh)
        self.input.installEventFilter(self)  # navegación ↑/↓/Enter
        layout.addWidget(self.input)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        self._content = QWidget()
        self._content.setStyleSheet("background: transparent;")
        self._vbox = QVBoxLayout(self._content)
        self._vbox.setContentsMargins(0, 0, 0, 0)
        self._vbox.setSpacing(4)
        self._vbox.setAlignment(Qt.AlignTop)
        scroll.setWidget(self._content)
        layout.addWidget(scroll, 1)

        self.input.setFocus()
        self.refresh()

    # --- Navegación por teclado (el foco vive en el QLineEdit) ---
    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Down:
                self._select(self._selected + 1)
                return True
            if key == Qt.Key_Up:
                self._select(self._selected - 1)
                return True
            if key in (Qt.Key_Return, Qt.Key_Enter):
                self._activate(self._selected)
                return True
        return super().eventFilter(obj, event)

    def _select(self, index):
        if not self._rows:
            self._selected = -1
            return
        index = max(0, min(index, len(self._rows) - 1))
        for i, (btn, _) in enumerate(self._rows):
            btn.setStyleSheet(self._selected_css() if i == index else "")
        self._selected = index

    def _activate(self, index):
        if 0 <= index < len(self._rows):
            self._rows[index][1]()

    def _selected_css(self):
        return (
            "text-align: left; padding: 6px 8px; border-radius: 8px;"
            f" background-color: {styles.COLORS['bg_hover']};"
            f" border: 1px solid {styles.COLORS['accent']};"
        )

    # --- Contenido ---
    def refresh(self):
        while self._vbox.count():
            item = self._vbox.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._rows = []

        raw = self.input.text().strip()

        # Modo captura rápida: "+ <título>"
        if raw.startswith("+"):
            title = raw[1:].strip()
            if title:
                self._add_row(
                    t("palette.quick_capture", title=title),
                    partial(self._emit_quick_capture, title),
                    icon_name="plus",
                )
            self._select(0)
            return

        query = raw.lower()

        matching = [(cid, lbl) for cid, lbl in self.commands if not query or query in lbl.lower()]
        if matching:
            self._add_section(t("palette.section_commands"))
            for cid, lbl in matching:
                self._add_row(lbl, partial(self._emit_command, cid), icon_name="command")

        if raw:
            tasks = database.search_tasks(text=raw, db_path=self.db_path)[:MAX_TASK_RESULTS]
            if tasks:
                self._add_section(t("palette.section_tasks"))
                for row in tasks:
                    self._add_task_row(row)

        if not self._rows:
            empty = QLabel(t("palette.no_results"))
            empty.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-style: italic; padding: 8px 2px;"
            )
            self._vbox.addWidget(empty)
        self._select(0)

    def _add_section(self, label):
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {styles.COLORS['text_muted']}; font-size: 10px; font-weight: bold;"
            " margin-top: 6px; background: transparent;"
        )
        self._vbox.addWidget(lbl)

    def _add_row(self, text, activate, icon_name=None):
        btn = QPushButton(text)
        btn.setObjectName("CommandItem")
        btn.setCursor(Qt.PointingHandCursor)
        if icon_name:
            btn.setIcon(lucide_icon(icon_name, styles.COLORS["text_soft"], 15))
        btn.clicked.connect(lambda _=False, fn=activate: fn())
        self._vbox.addWidget(btn)
        self._rows.append((btn, activate))

    def _add_task_row(self, row):
        title = row["title"] or t("search.result_no_title")
        due = f"   📅 {row['due_date']}" if row.get("due_date") else ""
        btn = QPushButton(f"{title}{due}")
        btn.setObjectName("NotificationItem")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setIcon(_swatch_icon(row["board_color"]))
        btn.setToolTip(t("search.result_tooltip", board=row["board_name"], column=row["column_name"]))
        activate = partial(self._emit_task, row["id"], row["board_id"])
        btn.clicked.connect(lambda _=False, fn=activate: fn())
        self._vbox.addWidget(btn)
        self._rows.append((btn, activate))

    def _emit_command(self, command_id):
        self.command_invoked.emit(command_id)
        self.accept()

    def _emit_task(self, task_id, board_id):
        self.task_activated.emit(task_id, board_id)
        self.accept()

    def _emit_quick_capture(self, title):
        self.quick_capture_requested.emit(title)
        self.accept()
