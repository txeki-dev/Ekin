"""
Diálogo informativo para vincular tableros con proveedores Cloud
(Google Drive, Dropbox, OneDrive o carpetas compartidas en red).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QWidget
)
import styles
from strings import t


class CloudSyncInfoDialog(QDialog):
    """Diálogo modal explicativo previo a seleccionar la ruta de sincronización en la nube."""
    def __init__(self, board_name: str = "", parent=None):
        super().__init__(parent)
        self.board_name = board_name
        self.setWindowTitle(t("sync.info_dialog_title"))
        self.resize(580, 480)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Cabecera
        header_lbl = QLabel(t("sync.info_header"))
        header_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {styles.COLORS['text_main']};")
        layout.addWidget(header_lbl)

        subtitle_lbl = QLabel(t("sync.info_subtitle"))
        subtitle_lbl.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']};")
        subtitle_lbl.setWordWrap(True)
        layout.addWidget(subtitle_lbl)

        # 2. Contenedor con scroll para la guía de proveedores
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(content_widget)
        c_layout.setContentsMargins(0, 4, 10, 4)
        c_layout.setSpacing(12)

        desc_card = QFrame()
        desc_card.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        d_layout = QVBoxLayout(desc_card)
        d_layout.setSpacing(8)

        desc_text = QLabel(t("sync.info_desc"))
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("font-size: 12px; line-height: 140%;")
        d_layout.addWidget(desc_text)
        c_layout.addWidget(desc_card)

        # Guía por proveedor
        guide_card = QFrame()
        guide_card.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        g_layout = QVBoxLayout(guide_card)
        g_layout.setSpacing(10)

        guide_title = QLabel(t("sync.info_providers_title"))
        guide_title.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {styles.COLORS['text_main']};")
        g_layout.addWidget(guide_title)

        providers = [
            t("sync.info_gdrive"),
            t("sync.info_dropbox"),
            t("sync.info_onedrive"),
            t("sync.info_other"),
        ]
        for p_html in providers:
            lbl = QLabel(p_html)
            lbl.setTextFormat(Qt.RichText)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-size: 12px; line-height: 135%;")
            g_layout.addWidget(lbl)

        c_layout.addWidget(guide_card)
        c_layout.addStretch()

        scroll.setWidget(content_widget)
        layout.addWidget(scroll, 1)

        # 3. Botones inferiores
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.continue_btn = QPushButton(t("sync.info_continue_btn"))
        self.continue_btn.setObjectName("PrimaryButton")
        self.continue_btn.setCursor(Qt.PointingHandCursor)
        self.continue_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.continue_btn)

        self.cancel_btn = QPushButton(t("sync.info_cancel_btn"))
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
