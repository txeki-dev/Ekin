"""Diálogo "Atajos de teclado" (Ctrl+/): referencia estática de todos los atajos de la
app, agrupados por categoría. No depende de la base de datos."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget
)

import styles
from strings import t


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("shortcuts.window_title"))
        self.setMinimumWidth(460)
        self.resize(460, 520)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(QLabel(t("shortcuts.header")))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        general_keys = [
            "shortcuts.item_search",
            "shortcuts.item_new_task",
            "shortcuts.item_new_column",
            "shortcuts.item_prev_next_board",
            "shortcuts.item_jump_board",
            "shortcuts.item_calendar",
            "shortcuts.item_settings",
            "shortcuts.item_shortcuts",
            "shortcuts.item_undo_redo",
            "shortcuts.item_close_dialog",
        ]
        editor_keys = [
            "shortcuts.item_bold",
            "shortcuts.item_italic",
            "shortcuts.item_strike",
            "shortcuts.item_nest_bullet",
            "shortcuts.item_arrow",
            "shortcuts.item_add_log",
        ]

        content_layout.addWidget(self._section_label(t("shortcuts.section_general")))
        for key in general_keys:
            content_layout.addWidget(self._item_label(key))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {styles.COLORS['border']};")
        content_layout.addWidget(line)

        content_layout.addWidget(self._section_label(t("shortcuts.section_editor")))
        for key in editor_keys:
            content_layout.addWidget(self._item_label(key))

        content_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        hint = QLabel(t("shortcuts.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(hint)

        btns = QHBoxLayout()
        btns.addStretch()
        close_btn = QPushButton(t("shortcuts.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _section_label(self, text):
        lbl = QLabel(f"<b>{text}</b>")
        lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; margin-top: 4px;")
        return lbl

    def _item_label(self, key):
        lbl = QLabel(t(key))
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px;")
        return lbl
