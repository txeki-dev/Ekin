"""Diálogos modales para el editor enriquecido (bloques de código, enlaces, inserción de tablas)."""
import re
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QPlainTextEdit, QFormLayout, QSpinBox
)

import styles
from strings import t


class CodeBlockDialog(QDialog):
    """Diálogo modal para insertar un bloque de código formateado."""
    LANGUAGES = [
        ("Python", "python"),
        ("JavaScript", "javascript"),
        ("TypeScript", "typescript"),
        ("HTML", "html"),
        ("CSS", "css"),
        ("SQL", "sql"),
        ("Bash / Shell", "bash"),
        ("JSON", "json"),
        ("C / C++", "cpp"),
        ("C#", "csharp"),
        ("Rust", "rust"),
        ("Go", "go"),
        ("Java", "java"),
        ("PHP", "php"),
        ("YAML", "yaml"),
        ("Markdown", "markdown"),
        ("Texto plano", "text"),
    ]

    def __init__(self, initial_code="", initial_lang="python", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.setWindowTitle(t("markdown_edit.code_dialog_title"))
        self.setMinimumSize(480, 360)
        self.resize(520, 400)
        if isinstance(initial_code, bool) or initial_code is None:
            initial_code = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(t("markdown_edit.code_lang_label")))
        self.lang_combo = QComboBox()
        for label, val in self.LANGUAGES:
            self.lang_combo.addItem(label, val)

        idx = -1
        for i, (_, val) in enumerate(self.LANGUAGES):
            if val.lower() == (initial_lang or "").lower():
                idx = i
                break
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        lang_layout.addWidget(self.lang_combo, 1)
        layout.addLayout(lang_layout)

        layout.addWidget(QLabel(t("markdown_edit.code_text_label")))
        self.code_edit = QPlainTextEdit()
        font = self.font()
        font.setFamily("Consolas")
        self.code_edit.setFont(font)
        self.code_edit.setStyleSheet("font-family: Consolas, 'Courier New', monospace; font-size: 12px;")
        self.code_edit.setPlainText(str(initial_code))
        self.code_edit.setPlaceholderText("def main():\n    print('Hello World')")
        layout.addWidget(self.code_edit, 1)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.insert_btn = QPushButton(t("markdown_edit.code_insert_btn"))
        self.insert_btn.setObjectName("PrimaryButton")
        self.insert_btn.setCursor(Qt.PointingHandCursor)
        self.insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.insert_btn)

        cancel_btn = QPushButton(t("markdown_edit.code_cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_data(self):
        return self.code_edit.toPlainText(), self.lang_combo.currentData()


class LinkDialog(QDialog):
    """Diálogo modal para insertar un enlace (URL)."""
    def __init__(self, initial_url="", initial_text="", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.setWindowTitle(t("markdown_edit.link_dialog_title"))
        self.setMinimumWidth(380)
        if isinstance(initial_url, bool) or initial_url is None:
            initial_url = ""
        if isinstance(initial_text, bool) or initial_text is None:
            initial_text = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(QLabel(t("markdown_edit.link_url_label")))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://ejemplo.com")
        self.url_input.setText(initial_url)
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel(t("markdown_edit.link_text_label")))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Ej. Mi enlace")
        self.text_input.setText(initial_text)
        layout.addWidget(self.text_input)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.insert_btn = QPushButton(t("markdown_edit.link_insert_btn"))
        self.insert_btn.setObjectName("PrimaryButton")
        self.insert_btn.setCursor(Qt.PointingHandCursor)
        self.insert_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.insert_btn)

        cancel_btn = QPushButton(t("markdown_edit.link_cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def get_data(self):
        url = self.url_input.text().strip()
        label = self.text_input.text().strip()
        if url and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
            url = f"https://{url}"
        return url, label or url


class TableInsertDialog(QDialog):
    """Diálogo modal para configurar e insertar una tabla con número inicial de filas y columnas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.finished.connect(self.deleteLater)
        self.setWindowTitle(t("markdown_edit.table_dialog_title"))
        self.setFixedWidth(320)
        self.selected_rows = 3
        self.selected_cols = 3

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel(f"<b>{t('markdown_edit.table_dialog_title')}</b>")
        header.setStyleSheet(f"font-size: 14px; color: {styles.COLORS['text_main']};")
        layout.addWidget(header)

        form = QFormLayout()
        form.setSpacing(10)

        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 50)
        self.rows_spin.setValue(3)
        self.rows_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {styles.COLORS['bg_card']};
                color: {styles.COLORS['text_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """)

        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 20)
        self.cols_spin.setValue(3)
        self.cols_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {styles.COLORS['bg_card']};
                color: {styles.COLORS['text_main']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 6px;
                padding: 4px 8px;
            }}
        """)

        lbl_rows = QLabel(t("markdown_edit.table_rows_label"))
        lbl_cols = QLabel(t("markdown_edit.table_cols_label"))
        form.addRow(lbl_rows, self.rows_spin)
        form.addRow(lbl_cols, self.cols_spin)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton(t("markdown_edit.link_cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)

        accept_btn = QPushButton(t("markdown_edit.code_insert_btn"))
        accept_btn.setObjectName("PrimaryButton")
        accept_btn.setDefault(True)
        accept_btn.setCursor(Qt.PointingHandCursor)
        accept_btn.clicked.connect(self.accept)
        btns.addWidget(accept_btn)

        layout.addLayout(btns)

    def accept(self):
        self.selected_rows = self.rows_spin.value()
        self.selected_cols = self.cols_spin.value()
        super().accept()

    def get_dimensions(self) -> tuple[int, int]:
        return self.selected_rows, self.selected_cols
