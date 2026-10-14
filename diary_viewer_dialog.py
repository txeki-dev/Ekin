"""
Visor de solo lectura, en Markdown, de los diarios de desarrollo (`diary.md`, `diary_archive.md`)
del directorio local asociado a un tablero (los que escriben los agentes de IA al trabajar en él).
"""
import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTabWidget, QTextBrowser, QVBoxLayout

import database
from strings import t

DIARY_FILES = ("diary.md", "diary_archive.md")


def diary_files(local_dir):
    """Rutas de los diarios que existen en `local_dir` (en el orden de DIARY_FILES)."""
    if not local_dir:
        return []
    return [p for p in (os.path.join(local_dir, name) for name in DIARY_FILES) if os.path.isfile(p)]


class DiaryViewerDialog(QDialog):
    """Una pestaña por diario existente, renderizado como Markdown; Recargar conserva el scroll."""

    def __init__(self, board_id, db_path=None, parent=None):
        super().__init__(parent)
        self.finished.connect(self.deleteLater)
        board = database.get_board(board_id, db_path)
        self.setWindowTitle(t("diary_viewer.title", board=board["name"]))
        self.resize(900, 700)
        self.paths = diary_files(board.get("local_dir"))

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.browsers = []
        for path in self.paths:
            browser = QTextBrowser()
            browser.setOpenExternalLinks(True)
            self.browsers.append(browser)
            self.tabs.addTab(browser, os.path.basename(path))
        layout.addWidget(self.tabs, 1)

        buttons = QHBoxLayout()
        self.open_btn = QPushButton(t("diary_viewer.open_in_editor"))
        self.open_btn.clicked.connect(self._open_current_in_editor)
        buttons.addWidget(self.open_btn)
        buttons.addStretch()
        self.reload_btn = QPushButton(t("diary_viewer.reload"))
        self.reload_btn.clicked.connect(self.reload)
        buttons.addWidget(self.reload_btn)
        close_btn = QPushButton(t("diary_viewer.close"))
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

        self.reload()

    def reload(self):
        for path, browser in zip(self.paths, self.browsers):
            scroll = browser.verticalScrollBar().value()
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    browser.setMarkdown(fh.read())
            except OSError as exc:
                browser.setPlainText(str(exc))
            browser.verticalScrollBar().setValue(scroll)

    def _open_current_in_editor(self):
        if self.paths:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.paths[self.tabs.currentIndex()]))
