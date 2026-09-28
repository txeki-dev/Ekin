"""AI Prompt Clipboard del tablero: los prompts del pack del tablero (DEV, Opositor, GTD o uno
importado de AI-Dev-Prompt-Clipboard) listos para copiar, con las variables del tablero
({{board_name}}, {{mcp_server}}) ya rellenadas y el resto pedidas al copiar."""
import html

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
)

import database
import prompt_packs
import styles
from icons import lucide_icon
from strings import t


def _swatch_icon(color, size=12):
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


def ask_variable_values(parent, names):
    """Pide el valor de cada variable {{...}} pendiente. Devuelve {nombre: valor}, o None si se cancela."""
    dlg = QDialog(parent)
    dlg.setWindowTitle(t("prompt_clipboard.vars_title"))
    dlg.setMinimumWidth(420)
    layout = QVBoxLayout(dlg)
    layout.addWidget(QLabel(t("prompt_clipboard.vars_hint")))
    form = QFormLayout()
    inputs = {}
    for name in names:
        inputs[name] = QLineEdit()
        form.addRow(name.replace("_", " ").capitalize() + ":", inputs[name])
    layout.addLayout(form)
    buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    buttons.accepted.connect(dlg.accept)
    buttons.rejected.connect(dlg.reject)
    layout.addWidget(buttons)
    if dlg.exec() != QDialog.Accepted:
        return None
    return {name: edit.text().strip() for name, edit in inputs.items()}


class PromptClipboardDialog(QDialog):
    """Modal con el pack de prompts del tablero: filtro por categoría, búsqueda, vista previa y copiar."""

    def __init__(self, board_id, db_path=None, parent=None):
        super().__init__(parent)
        self.board_id = board_id
        self.db_path = db_path
        board = database.get_board(board_id, db_path)
        self.board_vars = prompt_packs.board_variables(board)
        self.prompts = []
        self.visible_prompts = []
        self.setWindowTitle(t("prompt_clipboard.window_title", board=board["name"]))
        self.setMinimumSize(900, 580)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        top = QHBoxLayout()
        top.addWidget(QLabel(t("prompt_clipboard.pack_label")))
        self.pack_combo = QComboBox()
        top.addWidget(self.pack_combo, 1)
        self.import_btn = QPushButton(t("prompt_clipboard.import_btn"))
        self.import_btn.setIcon(lucide_icon("download", styles.COLORS['text_soft'], 14))
        self.import_btn.setToolTip(t("prompt_clipboard.import_tooltip"))
        self.import_btn.setCursor(Qt.PointingHandCursor)
        self.import_btn.clicked.connect(self._import_pack)
        top.addWidget(self.import_btn)
        root.addLayout(top)

        filters = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("prompt_clipboard.search_placeholder"))
        self.search_input.textChanged.connect(self._refresh_list)
        filters.addWidget(self.search_input, 2)
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self._refresh_list)
        filters.addWidget(self.category_combo, 1)
        root.addLayout(filters)

        body = QHBoxLayout()
        self.prompt_list = QListWidget()
        self.prompt_list.setFixedWidth(280)
        self.prompt_list.currentRowChanged.connect(self._show_preview)
        self.prompt_list.itemDoubleClicked.connect(lambda _item: self.copy_current())
        body.addWidget(self.prompt_list)
        right = QVBoxLayout()
        self.meta_label = QLabel("")
        self.meta_label.setWordWrap(True)
        self.meta_label.setTextFormat(Qt.RichText)
        right.addWidget(self.meta_label)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Consolas", 9))
        right.addWidget(self.preview, 1)
        body.addLayout(right, 1)
        root.addLayout(body, 1)

        bottom = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {styles.COLORS['text_muted']};")
        bottom.addWidget(self.status_label, 1)
        self.copy_btn = QPushButton(t("prompt_clipboard.copy_btn"))
        self.copy_btn.setObjectName("PrimaryButton")
        self.copy_btn.setIcon(lucide_icon("copy", styles.COLORS['on_accent'], 15))
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_current)
        bottom.addWidget(self.copy_btn)
        close_btn = QPushButton(t("prompt_clipboard.close_btn"))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        bottom.addWidget(close_btn)
        root.addLayout(bottom)

        self._reload_packs(prompt_packs.resolve_pack_id(board.get("prompt_pack")))
        self.pack_combo.currentIndexChanged.connect(self._on_pack_changed)

    def _reload_packs(self, select_id):
        self.pack_combo.blockSignals(True)
        self.pack_combo.clear()
        for pack_id, name in prompt_packs.list_packs():
            self.pack_combo.addItem(name, pack_id)
        self.pack_combo.setCurrentIndex(max(0, self.pack_combo.findData(select_id)))
        self.pack_combo.blockSignals(False)
        self._load_current_pack()

    def _on_pack_changed(self, _index):
        database.set_board_prompt_pack(self.board_id, self.pack_combo.currentData(), self.db_path)
        self._load_current_pack()

    def _load_current_pack(self):
        try:
            self.prompts = prompt_packs.load_pack(self.pack_combo.currentData())
            self.status_label.setText("")
        except (OSError, ValueError) as exc:
            self.prompts = []
            self.status_label.setText(t("prompt_clipboard.load_error", error=str(exc)))
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(t("prompt_clipboard.all_categories"), None)
        for category in dict.fromkeys(p["category"] for p in self.prompts if p["category"]):
            self.category_combo.addItem(category, category)
        self.category_combo.blockSignals(False)
        self._refresh_list()

    def _refresh_list(self):
        query = self.search_input.text().strip().lower()
        category = self.category_combo.currentData()
        self.visible_prompts = [
            p for p in self.prompts
            if (category is None or p["category"] == category)
            and (not query or any(query in p[k].lower() for k in ("title", "tag", "role", "description")))
        ]
        self.prompt_list.blockSignals(True)
        self.prompt_list.clear()
        for p in self.visible_prompts:
            item = QListWidgetItem(p["title"])
            if QColor(p["color"]).isValid():
                item.setIcon(_swatch_icon(p["color"]))
            item.setToolTip(p["description"] or p["role"])
            self.prompt_list.addItem(item)
        self.prompt_list.blockSignals(False)
        self.prompt_list.setCurrentRow(0 if self.visible_prompts else -1)
        self._show_preview(self.prompt_list.currentRow())

    def _show_preview(self, row):
        if not 0 <= row < len(self.visible_prompts):
            self.meta_label.setText("")
            self.preview.clear()
            self.copy_btn.setEnabled(False)
            return
        p = self.visible_prompts[row]
        heading = " · ".join(html.escape(x) for x in (p["tag"] or p["title"], p["category"], p["role"]) if x)
        self.meta_label.setText(
            f"<b>{heading}</b><br><span style='color:{styles.COLORS['text_muted']};'>{html.escape(p['description'])}</span>"
        )
        self.preview.setPlainText(prompt_packs.fill_variables(p["prompt"], self.board_vars))
        self.copy_btn.setEnabled(True)

    def copy_current(self):
        """Copia el prompt seleccionado con las variables del tablero; pide las que falten."""
        row = self.prompt_list.currentRow()
        if not 0 <= row < len(self.visible_prompts):
            return
        prompt = self.visible_prompts[row]
        text = prompt_packs.fill_variables(prompt["prompt"], self.board_vars)
        pending = prompt_packs.find_variables(text)
        if pending:
            values = ask_variable_values(self, pending)
            if values is None:
                return
            text = prompt_packs.fill_variables(text, values)
        QApplication.clipboard().setText(text)
        self.status_label.setText(t("prompt_clipboard.copied", title=prompt["title"]))

    def _import_pack(self):
        path, _ = QFileDialog.getOpenFileName(self, t("prompt_clipboard.import_title"), "", "JSON (*.json)")
        if not path:
            return
        try:
            pack_id = prompt_packs.import_pack(path)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, t("prompt_clipboard.import_title"), t("prompt_clipboard.import_error", error=str(exc)))
            return
        database.set_board_prompt_pack(self.board_id, pack_id, self.db_path)
        self._reload_packs(pack_id)
