"""Pantalla de Ajustes de la aplicación: tema, notificaciones y persistencia.

Guarda las preferencias en la tabla `app_settings`. El tamaño/posición de la ventana
se persiste desde `main` (al cerrar/abrir), aquí solo se gestionan tema y avisos."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QFrame, QSpinBox
)

import database
import styles
from strings import t


class SettingsDialog(QDialog):
    theme_changed = Signal(str)   # "dark" | "light"

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle(t("settings.window_title"))
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(QLabel(t("settings.header")))

        # --- Tema ---
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel(t("settings.theme_label")))
        self.theme_combo = QComboBox()
        self._themes = ["dark", "light"]
        self.theme_combo.addItem(t("settings.theme_dark"))
        self.theme_combo.addItem(t("settings.theme_light"))
        current = database.get_setting("theme", "dark", self.db_path)
        self.theme_combo.setCurrentIndex(self._themes.index(current) if current in self._themes else 0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        theme_hint = QLabel(t("settings.theme_hint"))
        theme_hint.setWordWrap(True)
        theme_hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(theme_hint)

        # --- Notificaciones ---
        self.notif_chk = QCheckBox(t("settings.notifications_checkbox"))
        self.notif_chk.setCursor(Qt.PointingHandCursor)
        self.notif_chk.setChecked(database.get_setting("notifications_enabled", "1", self.db_path) != "0")
        self.notif_chk.toggled.connect(
            lambda on: database.set_setting("notifications_enabled", "1" if on else "0", self.db_path)
        )
        layout.addWidget(self.notif_chk)

        # --- Temporizador de tareas ---
        timer_row = QHBoxLayout()
        timer_row.addWidget(QLabel(t("settings.timer_alert_label")))
        self.timer_alert_spin = QSpinBox()
        self.timer_alert_spin.setRange(1, 720)
        self.timer_alert_spin.setSuffix(t("settings.timer_alert_suffix"))
        self.timer_alert_spin.setValue(int(database.get_setting("timer_alert_hours", "24", self.db_path)))
        self.timer_alert_spin.valueChanged.connect(
            lambda hours: database.set_setting("timer_alert_hours", str(hours), self.db_path)
        )
        timer_row.addWidget(self.timer_alert_spin)
        timer_row.addStretch()
        layout.addLayout(timer_row)

        timer_hint = QLabel(t("settings.timer_alert_hint"))
        timer_hint.setWordWrap(True)
        timer_hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(timer_hint)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {styles.COLORS['border']};")
        layout.addWidget(line)

        info = QLabel(t("settings.geometry_hint"))
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(info)

        layout.addStretch()

        btns = QHBoxLayout()
        btns.addStretch()
        close_btn = QPushButton(t("settings.close_btn"))
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _on_theme_changed(self, index):
        theme = self._themes[index]
        database.set_setting("theme", theme, self.db_path)
        self.theme_changed.emit(theme)
