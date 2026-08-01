"""Pantalla de Ajustes de la aplicación: tema, notificaciones y persistencia.

Guarda las preferencias en la tabla `app_settings`. El tamaño/posición de la ventana
se persiste desde `main` (al cerrar/abrir), aquí solo se gestionan tema y avisos."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QFrame
)

import database
import styles


class SettingsDialog(QDialog):
    theme_changed = Signal(str)   # "dark" | "light"

    def __init__(self, db_path, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setWindowTitle("Ajustes")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addWidget(QLabel("⚙ <b>Ajustes de Ekin</b>"))

        # --- Tema ---
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("🎨 Tema:"))
        self.theme_combo = QComboBox()
        self._themes = ["dark", "light"]
        self.theme_combo.addItem("Oscuro")
        self.theme_combo.addItem("Claro")
        current = database.get_setting("theme", "dark", self.db_path)
        self.theme_combo.setCurrentIndex(self._themes.index(current) if current in self._themes else 0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo)
        theme_row.addStretch()
        layout.addLayout(theme_row)

        theme_hint = QLabel(
            "El tema claro es <i>experimental</i>: algunos colores de tarjetas/tableros están "
            "afinados para el oscuro. Se aplica del todo al reiniciar la app."
        )
        theme_hint.setWordWrap(True)
        theme_hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(theme_hint)

        # --- Notificaciones ---
        self.notif_chk = QCheckBox("Mostrar avisos de Windows para tareas que vencen hoy")
        self.notif_chk.setCursor(Qt.PointingHandCursor)
        self.notif_chk.setChecked(database.get_setting("notifications_enabled", "1", self.db_path) != "0")
        self.notif_chk.toggled.connect(
            lambda on: database.set_setting("notifications_enabled", "1" if on else "0", self.db_path)
        )
        layout.addWidget(self.notif_chk)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {styles.COLORS['border']};")
        layout.addWidget(line)

        info = QLabel("El tamaño y la posición de la ventana se recuerdan automáticamente.")
        info.setWordWrap(True)
        info.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        layout.addWidget(info)

        layout.addStretch()

        btns = QHBoxLayout()
        btns.addStretch()
        close_btn = QPushButton("Cerrar")
        close_btn.setObjectName("PrimaryButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

    def _on_theme_changed(self, index):
        theme = self._themes[index]
        database.set_setting("theme", theme, self.db_path)
        self.theme_changed.emit(theme)
