"""
Diálogo de configuración e integración de MCP (Model Context Protocol) por tablero.
Permite activar/desactivar el acceso para agentes IA y copiar la configuración con 1 clic.
"""

from __future__ import annotations

import json
import secrets
from typing import Optional

from PySide6.QtCore import QSize, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import database
from icons import lucide_icon
from mcp_server import get_mcp_manager
from strings import t
import styles


class McpSyncDialog(QDialog):
    """Diálogo modal para configurar la sincronización de un tablero con agentes de IA vía MCP."""

    def __init__(self, board_id: int, parent=None, db_path: Optional[str] = None):
        super().__init__(parent)
        self.board_id = board_id
        self.db_path = db_path
        self.mcp_manager = get_mcp_manager(self.db_path)

        self.board = database.get_board(self.board_id, db_path=self.db_path) or {}
        self.board_name = self.board.get("name", "Tablero")
        self.board_uuid = self.board.get("board_uuid") or ""
        self.mcp_enabled = bool(self.board.get("mcp_enabled", 0))
        self.mcp_secret = self.board.get("mcp_secret") or ""

        self.setWindowTitle(t("mcp.dialog.title"))
        self.resize(640, 580)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. Cabecera
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(lucide_icon("sparkles", styles.COLORS['accent'], 26).pixmap(26, 26))
        header_layout.addWidget(icon_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_lbl = QLabel(t("mcp.dialog.title"))
        title_lbl.setStyleSheet(
            f"font-family: 'Caprasimo', 'Segoe UI', serif; font-size: 20px; "
            f"font-weight: bold; color: {styles.COLORS['text_main']};"
        )
        title_col.addWidget(title_lbl)

        subtitle_lbl = QLabel(t("mcp.dialog.subtitle"))
        subtitle_lbl.setStyleSheet(f"font-size: 12px; color: {styles.COLORS['text_muted']};")
        subtitle_lbl.setWordWrap(True)
        title_col.addWidget(subtitle_lbl)

        header_layout.addLayout(title_col, 1)
        main_layout.addLayout(header_layout)

        # 2. Tarjeta del Interruptor Maestro y Estado del Servidor
        status_card = QFrame()
        status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        card_layout = QVBoxLayout(status_card)
        card_layout.setSpacing(10)

        # Fila del switch
        switch_row = QHBoxLayout()
        self.enable_checkbox = QCheckBox(t("mcp.dialog.enable_switch"))
        self.enable_checkbox.setChecked(self.mcp_enabled)
        self.enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 14px;
                font-weight: bold;
                color: {styles.COLORS['text_main']};
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.enable_checkbox.toggled.connect(self._on_enable_toggled)
        switch_row.addWidget(self.enable_checkbox)
        switch_row.addStretch()

        self.status_badge = QLabel()
        switch_row.addWidget(self.status_badge)
        card_layout.addLayout(switch_row)

        # Aviso de sandbox
        notice_lbl = QLabel(t("mcp.dialog.sandbox_notice"))
        notice_lbl.setStyleSheet(f"font-size: 11px; color: {styles.COLORS['text_soft']}; background: transparent;")
        notice_lbl.setWordWrap(True)
        card_layout.addWidget(notice_lbl)

        # Guía de conexión paso a paso
        guide_box = QFrame()
        guide_box.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_main']};
                border: 1px dashed {styles.COLORS['border_dashed']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        g_layout = QVBoxLayout(guide_box)
        g_layout.setContentsMargins(10, 8, 10, 8)
        g_layout.setSpacing(5)

        g_title = QLabel(f"<b>{t('mcp.dialog.guide_title')}</b>")
        g_title.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; border: none; background: transparent;")
        g_layout.addWidget(g_title)

        for step_text in [t("mcp.dialog.guide_step1"), t("mcp.dialog.guide_step2"), t("mcp.dialog.guide_step3")]:
            s_lbl = QLabel(f"• {step_text}")
            s_lbl.setStyleSheet(f"color: {styles.COLORS['text_soft']}; font-size: 11px; border: none; background: transparent;")
            s_lbl.setWordWrap(True)
            g_layout.addWidget(s_lbl)

        card_layout.addWidget(guide_box)

        main_layout.addWidget(status_card)

        # 3. Credenciales: UUID y Token Secreto
        cred_card = QFrame()
        cred_card.setStyleSheet(f"""
            QFrame {{
                background-color: {styles.COLORS['bg_card']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 10px;
                padding: 12px;
            }}
        """)
        cred_layout = QVBoxLayout(cred_card)
        cred_layout.setSpacing(10)

        # Fila UUID
        uuid_row = QHBoxLayout()
        uuid_lbl = QLabel(f"<b>{t('mcp.dialog.board_uuid_label')}</b>")
        uuid_lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; background: transparent;")
        uuid_row.addWidget(uuid_lbl)

        self.uuid_input = QLineEdit(self.board_uuid)
        self.uuid_input.setReadOnly(True)
        self.uuid_input.setStyleSheet("font-family: monospace; font-size: 12px;")
        uuid_row.addWidget(self.uuid_input, 1)

        copy_uuid_btn = QPushButton(t("mcp.dialog.copy_btn"))
        copy_uuid_btn.setCursor(Qt.PointingHandCursor)
        copy_uuid_btn.setIcon(lucide_icon("copy", styles.COLORS['text_soft'], 14))
        copy_uuid_btn.clicked.connect(lambda: self._copy_to_clipboard(self.board_uuid, copy_uuid_btn))
        uuid_row.addWidget(copy_uuid_btn)
        cred_layout.addLayout(uuid_row)

        # Fila Token
        token_row = QHBoxLayout()
        token_lbl = QLabel(f"<b>{t('mcp.dialog.token_label')}</b>")
        token_lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; background: transparent;")
        token_row.addWidget(token_lbl)

        self.token_input = QLineEdit(self.mcp_secret)
        self.token_input.setPlaceholderText("Sin token (acceso abierto en localhost)")
        self.token_input.setStyleSheet("font-family: monospace; font-size: 12px;")
        self.token_input.textChanged.connect(self._on_token_changed)
        token_row.addWidget(self.token_input, 1)

        gen_token_btn = QPushButton(t("mcp.dialog.token_generate"))
        gen_token_btn.setCursor(Qt.PointingHandCursor)
        gen_token_btn.clicked.connect(self._generate_new_token)
        token_row.addWidget(gen_token_btn)

        copy_token_btn = QPushButton(t("mcp.dialog.copy_btn"))
        copy_token_btn.setCursor(Qt.PointingHandCursor)
        copy_token_btn.setIcon(lucide_icon("copy", styles.COLORS['text_soft'], 14))
        copy_token_btn.clicked.connect(lambda: self._copy_to_clipboard(self.token_input.text(), copy_token_btn))
        token_row.addWidget(copy_token_btn)
        cred_layout.addLayout(token_row)

        main_layout.addWidget(cred_card)

        # 4. Pestañas de Clientes IA con snippets de configuración listos
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {styles.COLORS['border']};
                border-radius: 8px;
                background: {styles.COLORS['bg_card']};
            }}
            QTabBar::tab {{
                background: {styles.COLORS['bg_main']};
                color: {styles.COLORS['text_muted']};
                padding: 6px 14px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                background: {styles.COLORS['bg_card']};
                color: {styles.COLORS['text_main']};
                font-weight: bold;
            }}
        """)

        # Tab Claude Code
        self.claude_code_edit = self._create_snippet_tab(t("mcp.dialog.tab_claude_code"))
        # Tab Claude Desktop
        self.claude_desktop_edit = self._create_snippet_tab(t("mcp.dialog.tab_claude_desktop"))
        # Tab Cursor
        self.cursor_edit = self._create_snippet_tab(t("mcp.dialog.tab_cursor"))
        # Tab AGY CLI / Stdio
        self.stdio_edit = self._create_snippet_tab(t("mcp.dialog.tab_stdio"))

        main_layout.addWidget(self.tabs, 1)

        # 5. Botones inferiores
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.copy_feedback_lbl = QLabel()
        self.copy_feedback_lbl.setStyleSheet(f"color: {styles.COLORS['success']}; font-size: 12px; font-weight: bold;")
        btn_layout.addWidget(self.copy_feedback_lbl)
        btn_layout.addStretch()

        close_btn = QPushButton(t("mcp.dialog.close_btn"))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        save_btn = QPushButton(t("mcp.dialog.save_btn"))
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_and_apply)
        btn_layout.addWidget(save_btn)

        main_layout.addLayout(btn_layout)

        # Actualizar vista de snippets y badge
        self._update_status_ui()
        self._refresh_snippets()

    def _create_snippet_tab(self, tab_title: str) -> QTextEdit:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(12, 12, 12, 12)
        page_layout.setSpacing(8)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("font-family: monospace; font-size: 11px; background: transparent; border: none;")
        page_layout.addWidget(text_edit, 1)

        copy_btn = QPushButton(f" {t('mcp.dialog.copy_btn')}")
        copy_btn.setIcon(lucide_icon("copy", styles.COLORS['text_soft'], 14))
        copy_btn.setIconSize(QSize(14, 14))
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(text_edit.toPlainText(), copy_btn))

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(copy_btn)
        page_layout.addLayout(btn_row)

        self.tabs.addTab(page, tab_title)
        return text_edit

    def _update_status_ui(self):
        is_active = self.enable_checkbox.isChecked()
        url = self.mcp_manager.get_base_url()
        if is_active:
            self.status_badge.setText(f" ● {t('mcp.dialog.status_active', url=url)} ")
            self.status_badge.setStyleSheet(f"""
                background-color: {styles.COLORS['accent_2_tint']};
                color: {styles.COLORS['accent_2_ink']};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
            """)
        else:
            self.status_badge.setText(f" ○ {t('mcp.dialog.status_inactive')} ")
            self.status_badge.setStyleSheet(f"""
                background-color: {styles.COLORS['bg_hover']};
                color: {styles.COLORS['text_muted']};
                border-radius: 6px;
                font-size: 11px;
                padding: 4px 8px;
            """)

    def _on_enable_toggled(self, checked: bool):
        self._update_status_ui()
        self._refresh_snippets()

    def _on_token_changed(self, text: str):
        self._refresh_snippets()

    def _generate_new_token(self):
        new_token = secrets.token_hex(16)
        self.token_input.setText(new_token)
        self._refresh_snippets()

    def _refresh_snippets(self):
        token = self.token_input.text().strip() or None

        # 1. Claude Code
        cmd = self.mcp_manager.get_claude_code_command(self.board_name, self.board_uuid, token)
        self.claude_code_edit.setPlainText(cmd)

        # 2. Claude Desktop
        desktop_cfg = self.mcp_manager.get_claude_desktop_config(self.board_name, self.board_uuid, token)
        self.claude_desktop_edit.setPlainText(json.dumps(desktop_cfg, indent=2))

        # 3. Cursor
        cursor_cfg = self.mcp_manager.get_cursor_config(self.board_name, self.board_uuid, token)
        self.cursor_edit.setPlainText(json.dumps(cursor_cfg, indent=2))

        # 4. AGY CLI / Stdio
        token_arg = f" --token {token}" if token else ""
        stdio_cmd = f"python -m ekin_mcp --board-uuid {self.board_uuid}{token_arg}"
        self.stdio_edit.setPlainText(stdio_cmd)

    def _copy_to_clipboard(self, text: str, button: Optional[QPushButton] = None):
        if not text:
            return
        QApplication.clipboard().setText(text)
        self.copy_feedback_lbl.setText(t("mcp.dialog.copied"))
        QTimer.singleShot(3000, lambda: self.copy_feedback_lbl.setText(""))

    def _save_and_apply(self):
        enabled = self.enable_checkbox.isChecked()
        secret = self.token_input.text().strip() or None

        database.set_board_mcp_config(
            board_id=self.board_id,
            enabled=enabled,
            secret=secret,
            db_path=self.db_path,
        )

        if enabled:
            # Asegurar que el servidor local esté arrancado
            self.mcp_manager.start()

        self.accept()
