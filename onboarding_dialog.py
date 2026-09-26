"""
Diálogo de bienvenida y recorrido inicial (Landing Process / Guided Tour) de Ekin Kanban.
Guía al usuario en su primer aterrizaje en la aplicación y es accesible en cualquier momento desde Ajustes.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

import database
from icons import lucide_icon
from strings import t
import styles


class LandingTourDialog(QDialog):
    """Diálogo modal interactivo para guiar al usuario en las capacidades clave de Ekin."""

    def __init__(self, parent=None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.db_path = db_path
        self.setWindowTitle(t("landing.window_title"))
        self.setMinimumSize(600, 480)
        self.resize(620, 500)

        self._dots = []
        self._current_index = 0

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(16)

        # 1. Cabecera (Icono + Título Caprasimo + Subtítulo + Botón Cerrar)
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(lucide_icon("sparkles", styles.COLORS["accent"], 28).pixmap(28, 28))
        header_row.addWidget(icon_lbl, 0, Qt.AlignTop)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel(t("landing.header"))
        title_lbl.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 20px; "
            f"font-weight: bold; color: {styles.COLORS['text_main']};"
        )
        title_col.addWidget(title_lbl)

        sub_lbl = QLabel(t("landing.subtitle"))
        sub_lbl.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']};")
        sub_lbl.setWordWrap(True)
        title_col.addWidget(sub_lbl)
        header_row.addLayout(title_col, 1)

        close_btn = QPushButton()
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setIcon(lucide_icon("x", styles.COLORS["text_soft"], 15))
        close_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {styles.COLORS['border']}; border-radius: 15px; }}"
            f"QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}"
        )
        close_btn.clicked.connect(self.accept)
        header_row.addWidget(close_btn, 0, Qt.AlignTop)

        main_layout.addLayout(header_row)

        # 2. Contenedor de Diapositivas (QStackedWidget con tarjetas redondeadas)
        self.stack = QStackedWidget()

        slides_data = [
            {
                "icon": "list",
                "accent": styles.COLORS["accent"],
                "title": t("landing.slide1_title"),
                "desc": t("landing.slide1_desc"),
                "bullets": [
                    ("check", "Arrastrar y soltar fluido con previsualización nítida e inserción en tiempo real."),
                    ("sliders-horizontal", "Límites WIP configurables por columna para mantener flujos ágiles sin sobrecarga."),
                    ("copy", "Plantillas de fábrica (Agile Software, Opositor, GTD, En Blanco) y personalizables."),
                ]
            },
            {
                "icon": "code",
                "accent": "#0ea5e9",
                "title": t("landing.slide2_title"),
                "desc": t("landing.slide2_desc"),
                "bullets": [
                    ("clock", "Diario personal integrado por tarjeta con registro cronológico y trazabilidad."),
                    ("code", "Editor enriquecido con bloques de código resaltados (</>), tablas y formato Markdown."),
                    ("paperclip", "Adjuntos de archivos locales (con detección automática de rutas) y enlaces web."),
                ]
            },
            {
                "icon": "sparkles",
                "accent": styles.COLORS["accent_2_ink"],
                "title": t("landing.slide3_title"),
                "desc": t("landing.slide3_desc"),
                "bullets": [
                    ("cloud", "Servidor local Model Context Protocol (MCP) en HTTP/SSE (127.0.0.1:8765) y STDIO."),
                    ("check", "Sandboxing estricto por tablero y gobernanza de columnas (Human-Only)."),
                    ("sparkles", "Generador de especificaciones técnicas (TDD/SPEC) seleccionando múltiples tareas."),
                ]
            },
            {
                "icon": "command",
                "accent": "#f59e0b",
                "title": t("landing.slide4_title"),
                "desc": t("landing.slide4_desc"),
                "bullets": [
                    ("command", "Ctrl+K: Paleta de comandos universal y captura ultrarrápida (+ título)."),
                    ("list", "Ctrl+0: Vista Mi Trabajo para dominar tus entregas y fechas límite."),
                    ("calendar", "Sincronización en vivo con Google, Apple y Outlook mediante feed .ics."),
                ]
            }
        ]

        for sdata in slides_data:
            self.stack.addWidget(self._create_slide_page(sdata))

        main_layout.addWidget(self.stack, 1)

        # 3. Barra de navegación inferior
        nav_row = QHBoxLayout()
        nav_row.setSpacing(10)

        # Checkbox "No volver a mostrar al inicio"
        self.dont_show_chk = QCheckBox(t("landing.dont_show_again"))
        is_already_shown = database.get_setting("onboarding_tour_shown", "0", self.db_path) == "1"
        self.dont_show_chk.setChecked(is_already_shown)
        self.dont_show_chk.toggled.connect(self._on_dont_show_toggled)
        nav_row.addWidget(self.dont_show_chk)

        nav_row.addStretch()

        # Dots indicadores
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(6)
        for i in range(len(slides_data)):
            dot = QPushButton()
            dot.setFixedSize(10, 10)
            dot.setCursor(Qt.PointingHandCursor)
            dot.clicked.connect(lambda _=False, idx=i: self._go_to_slide(idx))
            self._dots.append(dot)
            dots_layout.addWidget(dot)
        nav_row.addLayout(dots_layout)

        nav_row.addSpacing(12)

        # Botón Anterior
        self.prev_btn = QPushButton(f" {t('landing.prev_btn')}")
        self.prev_btn.setIcon(lucide_icon("chevron-left", styles.COLORS["text_soft"], 14))
        self.prev_btn.setIconSize(QSize(14, 14))
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.clicked.connect(self._on_prev)
        nav_row.addWidget(self.prev_btn)

        # Botón Siguiente / Comenzar
        self.next_btn = QPushButton(t("landing.next_btn"))
        self.next_btn.setObjectName("PrimaryButton")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next)
        nav_row.addWidget(self.next_btn)

        main_layout.addLayout(nav_row)

        self._update_navigation_state()

    def _create_slide_page(self, data: dict) -> QWidget:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 14px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Título de la diapositiva con icono representativo
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        slide_icon = QLabel()
        slide_icon.setPixmap(lucide_icon(data["icon"], data["accent"], 24).pixmap(24, 24))
        title_row.addWidget(slide_icon)

        stitle = QLabel(data["title"])
        stitle.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {styles.COLORS['text_main']}; background: transparent;"
        )
        title_row.addWidget(stitle, 1)
        layout.addLayout(title_row)

        # Descripción principal
        sdesc = QLabel(data["desc"])
        sdesc.setStyleSheet(
            f"font-size: 13px; line-height: 1.4; color: {styles.COLORS['text_soft']}; background: transparent;"
        )
        sdesc.setWordWrap(True)
        layout.addWidget(sdesc)

        layout.addSpacing(4)

        # Viñetas con detalles
        bullets_layout = QVBoxLayout()
        bullets_layout.setSpacing(10)
        for b_icon, b_text in data["bullets"]:
            brow = QHBoxLayout()
            brow.setSpacing(8)
            b_ico_lbl = QLabel()
            b_ico_lbl.setPixmap(lucide_icon(b_icon, styles.COLORS["accent"], 16).pixmap(16, 16))
            brow.addWidget(b_ico_lbl, 0, Qt.AlignTop)

            btxt = QLabel(b_text)
            btxt.setStyleSheet(
                f"font-size: 12px; color: {styles.COLORS['text_main']}; background: transparent;"
            )
            btxt.setWordWrap(True)
            brow.addWidget(btxt, 1)
            bullets_layout.addLayout(brow)

        layout.addLayout(bullets_layout)
        layout.addStretch()
        return card

    def _go_to_slide(self, index: int):
        self._current_index = max(0, min(index, self.stack.count() - 1))
        self.stack.setCurrentIndex(self._current_index)
        self._update_navigation_state()

    def _on_prev(self):
        if self._current_index > 0:
            self._go_to_slide(self._current_index - 1)

    def _on_next(self):
        if self._current_index < self.stack.count() - 1:
            self._go_to_slide(self._current_index + 1)
        else:
            database.set_setting("onboarding_tour_shown", "1", self.db_path)
            self.accept()

    def _on_dont_show_toggled(self, checked: bool):
        database.set_setting("onboarding_tour_shown", "1" if checked else "0", self.db_path)

    def _update_navigation_state(self):
        self.prev_btn.setEnabled(self._current_index > 0)
        self.prev_btn.setVisible(self._current_index > 0)

        is_last = self._current_index == self.stack.count() - 1
        if is_last:
            self.next_btn.setText(f" {t('landing.start_btn')} ")
            self.next_btn.setIcon(lucide_icon("check", styles.COLORS["on_accent"], 14))
            self.next_btn.setIconSize(QSize(14, 14))
        else:
            self.next_btn.setText(f" {t('landing.next_btn')} ")
            self.next_btn.setIcon(lucide_icon("chevron-right", styles.COLORS["on_accent"], 14))
            self.next_btn.setIconSize(QSize(14, 14))

        for i, dot in enumerate(self._dots):
            if i == self._current_index:
                dot.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.COLORS['accent']};
                        border: none;
                        border-radius: 5px;
                    }}
                """)
            else:
                dot.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.COLORS['border']};
                        border: none;
                        border-radius: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: {styles.COLORS['text_muted']};
                    }}
                """)


class InteractiveTourBanner(QFrame):
    """Barra superior interactiva in-situ para guiar al usuario a través del tablero demo."""

    step_changed = Signal(int)
    action_triggered = Signal(int)  # 0, 1, 2, 3
    tour_completed = Signal()
    tour_dismissed = Signal()

    def __init__(self, parent=None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.db_path = db_path
        self._current_step = 0
        self._dots = []
        self.setObjectName("InteractiveTourBanner")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(14)

        # 1. Badge con icono temático
        badge = QFrame()
        badge.setFixedSize(36, 36)
        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_hover']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 18px;
            }}
        """)
        badge_layout = QVBoxLayout(badge)
        badge_layout.setContentsMargins(0, 0, 0, 0)
        badge_layout.setAlignment(Qt.AlignCenter)
        self.badge_icon = QLabel()
        self.badge_icon.setPixmap(lucide_icon("sparkles", styles.COLORS["accent"], 18).pixmap(18, 18))
        self.badge_icon.setAlignment(Qt.AlignCenter)
        badge_layout.addWidget(self.badge_icon)
        layout.addWidget(badge, 0, Qt.AlignVCenter)

        # 2. Textos (Título + Descripción en dos líneas compactas)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(2)

        top_line = QHBoxLayout()
        top_line.setSpacing(10)
        self.step_title = QLabel()
        self.step_title.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {styles.COLORS['text_main']}; background: transparent;"
        )
        top_line.addWidget(self.step_title)

        # Píldoras indicadoras de paso (dots interactivos)
        dots_layout = QHBoxLayout()
        dots_layout.setSpacing(5)
        self._dots.clear()
        for i in range(4):
            dot = QPushButton()
            dot.setCursor(Qt.PointingHandCursor)
            dot.clicked.connect(lambda _=False, idx=i: self.go_to_step(idx))
            self._dots.append(dot)
            dots_layout.addWidget(dot)
        top_line.addLayout(dots_layout)
        top_line.addStretch()
        vbox.addLayout(top_line)

        self.step_desc = QLabel()
        self.step_desc.setWordWrap(True)
        self.step_desc.setStyleSheet(
            f"font-size: 12px; color: {styles.COLORS['text_soft']}; background: transparent; line-height: 1.3;"
        )
        vbox.addWidget(self.step_desc)
        layout.addLayout(vbox, 1)

        # 3. Acciones y navegación a la derecha
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        controls_layout.setAlignment(Qt.AlignVCenter)

        # Botón contextual de acción rápida
        self.action_btn = QPushButton()
        self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 5px 12px;
                color: {styles.COLORS['text_main']};
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_hover']};
                border-color: {styles.COLORS['accent']};
            }}
        """)
        self.action_btn.clicked.connect(lambda: self.action_triggered.emit(self._current_step))
        controls_layout.addWidget(self.action_btn)

        # Botón Anterior
        self.prev_btn = QPushButton(f" {t('tour.banner.prev_btn')}")
        self.prev_btn.setIcon(lucide_icon("chevron-left", styles.COLORS["text_soft"], 14))
        self.prev_btn.setIconSize(QSize(14, 14))
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 5px 10px;
                color: {styles.COLORS['text_soft']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_hover']};
            }}
        """)
        self.prev_btn.clicked.connect(lambda: self.go_to_step(self._current_step - 1))
        controls_layout.addWidget(self.prev_btn)

        # Botón Siguiente / Finalizar
        self.next_btn = QPushButton(f" {t('tour.banner.next_btn')}")
        self.next_btn.setObjectName("PrimaryButton")
        self.next_btn.setIcon(lucide_icon("chevron-right", styles.COLORS["on_accent"], 14))
        self.next_btn.setIconSize(QSize(14, 14))
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.clicked.connect(self._on_next_clicked)
        controls_layout.addWidget(self.next_btn)

        # Botón Cerrar (Descartar)
        self.close_btn = QPushButton()
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setIcon(lucide_icon("x", styles.COLORS["text_muted"], 14))
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.setToolTip(t("tour.banner.close_tooltip"))
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 13px;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_hover']};
            }}
        """)
        self.close_btn.clicked.connect(self.dismiss_tour)
        controls_layout.addWidget(self.close_btn)

        layout.addLayout(controls_layout)
        self.update_style()

    def update_style(self):
        """Aplica colores y refresca los textos según el idioma y tema actuales."""
        self.setStyleSheet(f"""
            #InteractiveTourBanner {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 12px;
                margin: 8px 16px 4px 16px;
            }}
        """)
        self._update_step_ui()

    def go_to_step(self, step: int):
        self._current_step = max(0, min(step, 3))
        self._update_step_ui()
        self.step_changed.emit(self._current_step)

    def _on_next_clicked(self):
        if self._current_step < 3:
            self.go_to_step(self._current_step + 1)
        else:
            self.finish_tour()

    def finish_tour(self):
        database.set_setting("interactive_tour_completed", "1", self.db_path)
        database.set_setting("interactive_tour_dismissed", "1", self.db_path)
        self.tour_completed.emit()
        self.hide()

    def dismiss_tour(self):
        database.set_setting("interactive_tour_dismissed", "1", self.db_path)
        self.tour_dismissed.emit()
        self.hide()

    def _update_step_ui(self):
        steps_info = [
            {
                "title": t("tour.banner.step1_title"),
                "desc": t("tour.banner.step1_desc"),
                "action_text": t("tour.banner.step1_action"),
                "action_icon": "sparkles",
            },
            {
                "title": t("tour.banner.step2_title"),
                "desc": t("tour.banner.step2_desc"),
                "action_text": t("tour.banner.step2_action"),
                "action_icon": "sliders-horizontal",
            },
            {
                "title": t("tour.banner.step3_title"),
                "desc": t("tour.banner.step3_desc"),
                "action_text": t("tour.banner.step3_action"),
                "action_icon": "command",
            },
            {
                "title": t("tour.banner.step4_title"),
                "desc": t("tour.banner.step4_desc"),
                "action_text": t("tour.banner.step4_action"),
                "action_icon": "sliders-horizontal",
            },
        ]
        info = steps_info[self._current_step]
        self.step_title.setText(info["title"])
        self.step_desc.setText(info["desc"])
        self.action_btn.setText(f" {info['action_text']} ")
        self.action_btn.setIcon(lucide_icon(info["action_icon"], styles.COLORS["text_main"], 14))

        self.prev_btn.setEnabled(self._current_step > 0)
        self.prev_btn.setVisible(self._current_step > 0)

        is_last = self._current_step == 3
        if is_last:
            self.next_btn.setText(f" {t('tour.banner.finish_btn')} ")
            self.next_btn.setIcon(lucide_icon("check", styles.COLORS["on_accent"], 14))
        else:
            self.next_btn.setText(f" {t('tour.banner.next_btn')} ")
            self.next_btn.setIcon(lucide_icon("chevron-right", styles.COLORS["on_accent"], 14))

        for i, dot in enumerate(self._dots):
            if i == self._current_step:
                dot.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.COLORS['accent']};
                        border: none;
                        border-radius: 4px;
                        min-width: 18px;
                        max-height: 8px;
                    }}
                """)
            else:
                dot.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {styles.COLORS['border']};
                        border: none;
                        border-radius: 4px;
                        min-width: 8px;
                        max-height: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: {styles.COLORS['text_muted']};
                    }}
                """)
