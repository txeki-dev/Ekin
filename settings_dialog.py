"""Pantalla de Ajustes de la aplicación: tema, notificaciones y persistencia.

Guarda las preferencias en la tabla `app_settings`. El tamaño/posición de la ventana
se persiste desde `main` (al cerrar/abrir), aquí solo se gestionan tema y avisos.

Los controles visibles (segmentado / interruptor / stepper) son la cara del diseño; la
lógica de estado y persistencia sigue viviendo en tres widgets de respaldo ocultos
(`theme_combo`, `notif_chk`, `timer_alert_spin`) que los controles visuales manejan.
"""
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton,
    QFrame, QSpinBox, QButtonGroup, QSizePolicy
)

import database
import styles
import strings
from strings import t
from icons import lucide_icon


class ToggleSwitch(QCheckBox):
    """Interruptor 46×26: pista redondeada + perilla; acento cuando está activo."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(46, 26)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        on = self.isChecked()
        track = QColor(styles.COLORS["accent"] if on else styles.COLORS["border_dashed"])
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(0, 0, 46, 26), 13, 13)
        knob = QColor(styles.COLORS["on_accent"] if on else styles.COLORS["bg_card"])
        p.setBrush(knob)
        x = 23 if on else 3
        p.drawEllipse(QRectF(x, 3, 20, 20))
        p.end()


class SettingsDialog(QDialog):
    theme_changed = Signal(str)      # "dark" | "light"
    language_changed = Signal(str)   # "en" | "es"

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.db_path = db_path
        self.setWindowTitle(t("settings.window_title"))
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(18)

        # --- Cabecera: título Caprasimo + cerrar ---
        head = QHBoxLayout()
        title = QLabel(t("settings.header"))
        title.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 20px; color: {styles.COLORS['text_main']};"
        )
        head.addWidget(title)
        head.addStretch()
        close_circle = QPushButton()
        close_circle.setFixedSize(30, 30)
        close_circle.setCursor(Qt.PointingHandCursor)
        close_circle.setIcon(lucide_icon("x", styles.COLORS["text_soft"], 15))
        close_circle.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {styles.COLORS['border']}; border-radius: 15px; }}"
            f"QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}"
        )
        close_circle.clicked.connect(self.accept)
        head.addWidget(close_circle)
        layout.addLayout(head)

        # === Backing widgets ocultos (estado + persistencia; los tests dependen de ellos) ===
        self.lang_combo = QComboBox()
        self._languages = ["en", "es"]
        self.lang_combo.addItem(t("settings.language_en"))
        self.lang_combo.addItem(t("settings.language_es"))
        current_lang = database.get_setting("language", "en", self.db_path)
        self.lang_combo.setCurrentIndex(
            self._languages.index(current_lang) if current_lang in self._languages else 0
        )
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        self.lang_combo.hide()

        self.theme_combo = QComboBox()
        self._themes = ["dark", "light"]
        self.theme_combo.addItem(t("settings.theme_dark"))
        self.theme_combo.addItem(t("settings.theme_light"))
        current_theme = database.get_setting("theme", "light", self.db_path)
        self.theme_combo.setCurrentIndex(self._themes.index(current_theme) if current_theme in self._themes else 0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.theme_combo.hide()

        self.notif_chk = QCheckBox()
        self.notif_chk.setChecked(database.get_setting("notifications_enabled", "1", self.db_path) != "0")
        self.notif_chk.toggled.connect(
            lambda on: database.set_setting("notifications_enabled", "1" if on else "0", self.db_path)
        )
        self.notif_chk.hide()

        self.timer_alert_spin = QSpinBox()
        self.timer_alert_spin.setRange(1, 720)
        self.timer_alert_spin.setValue(int(database.get_setting("timer_alert_hours", "24", self.db_path)))
        self.timer_alert_spin.valueChanged.connect(self._on_timer_value_changed)
        self.timer_alert_spin.hide()

        # === Fila 1: Idioma (segmentado English / Español) ===
        layout.addWidget(self._row(
            t("settings.language_label"), t("settings.language_desc"), self._build_language_segment()
        ))
        layout.addWidget(self._divider())

        # === Fila 2: Tema (segmentado Light / Dark) ===
        layout.addWidget(self._row(
            t("settings.theme_label"), t("settings.theme_desc"), self._build_theme_segment()
        ))
        layout.addWidget(self._divider())

        # === Fila 3: Notificaciones (interruptor) ===
        self.notif_switch = ToggleSwitch()
        self.notif_switch.setChecked(self.notif_chk.isChecked())
        self.notif_switch.toggled.connect(self.notif_chk.setChecked)
        layout.addWidget(self._row(
            t("settings.notifications_label"), t("settings.notifications_desc"), self.notif_switch
        ))
        layout.addWidget(self._divider())

        # === Fila 3: Umbral del temporizador (stepper) ===
        layout.addWidget(self._row(
            t("settings.timer_alert_label"), t("settings.timer_alert_desc"), self._build_stepper()
        ))

        layout.addStretch()

        info = QLabel(t("settings.geometry_hint"))
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(info)

        btns = QHBoxLayout()
        btns.addStretch()
        close_btn = QPushButton(t("settings.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _row(self, label_text, desc_text, control):
        """Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a la derecha."""
        row = QFrame()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(12)
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        lbl = QLabel(label_text)
        lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {styles.COLORS['text_main']}; background: transparent;")
        text_col.addWidget(lbl)
        desc = QLabel(desc_text)
        desc.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']}; background: transparent;")
        text_col.addWidget(desc)
        h.addLayout(text_col, 1)
        h.addWidget(control, 0, Qt.AlignVCenter)
        return row

    def _divider(self):
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {styles.COLORS['border']};")
        return line

    def _build_language_segment(self):
        """Segmentado English / Español que maneja el lang_combo de respaldo."""
        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ border: 1px solid {styles.COLORS['border']}; border-radius: 19px; background: transparent; }}"
        )
        h = QHBoxLayout(seg)
        h.setContentsMargins(4, 4, 4, 4)
        h.setSpacing(4)
        self._lang_group = QButtonGroup(self)
        self._lang_group.setExclusive(True)
        labels = [(t("settings.language_en"), "en"), (t("settings.language_es"), "es")]
        current_lang = self._languages[self.lang_combo.currentIndex()]
        for text, key in labels:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setChecked(key == current_lang)
            b.setStyleSheet(self._segment_button_css())
            b.clicked.connect(lambda _=False, k=key: self.lang_combo.setCurrentIndex(self._languages.index(k)))
            self._lang_group.addButton(b)
            h.addWidget(b)
        return seg

    def _build_theme_segment(self):
        """Segmentado Light / Dark que maneja el theme_combo de respaldo."""
        seg = QFrame()
        seg.setStyleSheet(
            f"QFrame {{ border: 1px solid {styles.COLORS['border']}; border-radius: 19px; background: transparent; }}"
        )
        h = QHBoxLayout(seg)
        h.setContentsMargins(4, 4, 4, 4)
        h.setSpacing(4)
        self._theme_group = QButtonGroup(self)
        self._theme_group.setExclusive(True)
        labels = [(t("settings.theme_light"), "light"), (t("settings.theme_dark"), "dark")]
        current_theme = self._themes[self.theme_combo.currentIndex()]
        for text, key in labels:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setChecked(key == current_theme)
            b.setStyleSheet(self._segment_button_css())
            b.clicked.connect(lambda _=False, k=key: self.theme_combo.setCurrentIndex(self._themes.index(k)))
            self._theme_group.addButton(b)
            h.addWidget(b)
        return seg

    def _segment_button_css(self):
        # Borde transparente OBLIGATORIO: en Qt, border-radius no recorta el fondo de un
        # QPushButton si `border: none` (quedaría un rectángulo). Con un borde (aunque sea
        # transparente) el segmento activo se pinta como una píldora limpia.
        return (
            f"QPushButton {{ background: transparent; border: 1px solid transparent; border-radius: 16px; "
            f"padding: 7px 20px; color: {styles.COLORS['text_soft']}; }}"
            f"QPushButton:checked {{ background-color: {styles.COLORS['accent']}; color: {styles.COLORS['on_accent']}; font-weight: 600; }}"
            f"QPushButton:hover:!checked {{ background-color: {styles.COLORS['bg_hover']}; }}"
        )

    def _build_stepper(self):
        """Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de respaldo."""
        wrap = QFrame()
        h = QHBoxLayout(wrap)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        def round_btn(icon_name, delta):
            b = QPushButton()
            b.setFixedSize(30, 30)
            b.setCursor(Qt.PointingHandCursor)
            b.setIcon(lucide_icon(icon_name, styles.COLORS["text_soft"], 15))
            b.setStyleSheet(
                f"QPushButton {{ background: transparent; border: 1px solid {styles.COLORS['border']}; border-radius: 15px; }}"
                f"QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}"
            )
            b.clicked.connect(lambda: self.timer_alert_spin.setValue(self.timer_alert_spin.value() + delta))
            return b

        h.addWidget(round_btn("minus", -1))
        self._stepper_value = QLabel(f"{self.timer_alert_spin.value()} h")
        self._stepper_value.setAlignment(Qt.AlignCenter)
        self._stepper_value.setMinimumWidth(56)
        self._stepper_value.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 17px; color: {styles.COLORS['text_main']}; background: transparent;"
        )
        self._stepper_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        h.addWidget(self._stepper_value)
        h.addWidget(round_btn("plus", 1))
        return wrap

    def _on_timer_value_changed(self, hours):
        database.set_setting("timer_alert_hours", str(hours), self.db_path)
        if hasattr(self, "_stepper_value"):
            self._stepper_value.setText(f"{hours} h")

    def _on_theme_changed(self, index):
        theme = self._themes[index]
        database.set_setting("theme", theme, self.db_path)
        self.theme_changed.emit(theme)

    def _on_language_changed(self, index):
        lang = self._languages[index]
        database.set_setting("language", lang, self.db_path)
        strings.set_language(lang)
        self.language_changed.emit(lang)

