"""
Diagrama del flujo de trabajo con un agente de IA (#137): cómo viaja una tarea de la idea a Done,
paso a paso y con quién actúa en cada uno (tú, Ekin o el agente). Se abre desde la paleta de
comandos, desde Ajustes y desde la guía de bienvenida.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

import styles
from icons import lucide_icon
from strings import t

# (clave de strings.py, icono, quién actúa)
STEPS = (
    ("capture", "list", "you"),
    ("ready", "clipboard-list", "you"),
    ("work", "play", "ekin"),
    ("agent", "sparkles", "agent"),
    ("review", "search", "you"),
    ("done", "check", "you"),
)


def _actor_chip(actor):
    """Píldora con quién actúa en el paso, con un color por actor."""
    fg, bg = {
        "you": (styles.COLORS["on_accent"], styles.COLORS["accent"]),
        "agent": (styles.COLORS["accent_2_ink"], styles.COLORS["accent_2_tint"]),
        "ekin": (styles.COLORS["text_soft"], styles.COLORS["bg_hover"]),
    }[actor]
    chip = QLabel(t(f"workflow.actor_{actor}"))
    chip.setStyleSheet(
        f"background-color: {bg}; color: {fg}; border-radius: 9px; padding: 2px 9px; font-size: 11px; font-weight: 600;"
    )
    return chip


def _step_card(key, icon, actor):
    card = QFrame()
    card.setObjectName("WorkflowStep")
    card.setStyleSheet(
        f"#WorkflowStep {{ background-color: {styles.COLORS['bg_card']}; border: 1px solid {styles.COLORS['border']};"
        f" border-radius: 12px; }}"
    )
    layout = QHBoxLayout(card)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(12)

    icon_lbl = QLabel()
    icon_lbl.setPixmap(lucide_icon(icon, styles.COLORS["accent"], 22).pixmap(22, 22))
    icon_lbl.setStyleSheet("background: transparent;")
    layout.addWidget(icon_lbl, 0, Qt.AlignTop)

    text_col = QVBoxLayout()
    text_col.setSpacing(4)
    head = QHBoxLayout()
    head.setSpacing(8)
    title = QLabel(t(f"workflow.{key}_title"))
    title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {styles.COLORS['text_main']}; background: transparent;")
    head.addWidget(title)
    head.addStretch()
    head.addWidget(_actor_chip(actor))
    text_col.addLayout(head)

    desc = QLabel(t(f"workflow.{key}_desc"))
    desc.setWordWrap(True)
    desc.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_soft']}; background: transparent;")
    text_col.addWidget(desc)
    layout.addLayout(text_col, 1)
    return card


class WorkflowDialog(QDialog):
    """Los pasos del flujo, unidos por flechas, y una nota sobre columnas y traspasos."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.finished.connect(self.deleteLater)
        self.setWindowTitle(t("workflow.title"))
        self.resize(560, 780)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        subtitle = QLabel(t("workflow.subtitle"))
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"font-size: 13px; color: {styles.COLORS['text_soft']};")
        layout.addWidget(subtitle)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        steps_layout = QVBoxLayout(content)
        steps_layout.setContentsMargins(0, 0, 0, 0)
        steps_layout.setSpacing(4)
        for index, (key, icon, actor) in enumerate(STEPS):
            if index:
                arrow = QLabel()
                arrow.setPixmap(lucide_icon("chevron-down", styles.COLORS["text_muted"], 18).pixmap(18, 18))
                arrow.setAlignment(Qt.AlignCenter)
                steps_layout.addWidget(arrow)
            steps_layout.addWidget(_step_card(key, icon, actor))
        steps_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.viewport().setStyleSheet("background: transparent;")
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        note = QLabel(t("workflow.note"))
        note.setWordWrap(True)
        note.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']};")
        layout.addWidget(note)

        buttons = QHBoxLayout()
        buttons.addStretch()
        close_btn = QPushButton(t("workflow.close"))
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
