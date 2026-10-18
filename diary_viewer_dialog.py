"""
Visor de solo lectura de los diarios de desarrollo (`diary.md`, `diary_archive.md`) y del resto de
archivos Markdown y de texto del directorio local asociado a un tablero (#142): los de la raíz en
pestañas, los de subcarpetas en el menú «Más…».
"""
import itertools
import os

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QDialog, QHBoxLayout, QMenu, QPushButton, QTabWidget, QTextBrowser, QVBoxLayout

import database
import styles
from detail_dialog.repo_files import _SKIP_DIRS
from strings import t

DIARY_FILES = ("diary.md", "diary_archive.md")
DOC_EXTENSIONS = (".md", ".txt")
MAX_DOC_FILES = 500


def _iter_doc_files(local_dir):
    """Rutas relativas (con «/») de los .md / .txt de `local_dir`, primero los de la raíz. Recorre el
    directorio en vez de usar `git ls-files --exclude-standard`: los diarios suelen estar en .gitignore."""
    for dirpath, dirnames, filenames in os.walk(local_dir):
        dirnames[:] = sorted(
            (d for d in dirnames if d not in _SKIP_DIRS and not d.endswith(".egg-info")), key=str.lower
        )
        rel_dir = os.path.relpath(dirpath, local_dir)
        for name in sorted(filenames, key=str.lower):
            if name.lower().endswith(DOC_EXTENSIONS):
                yield name if rel_dir == "." else f"{rel_dir}/{name}".replace("\\", "/")


def has_doc_files(local_dir):
    """True si `local_dir` tiene algún .md / .txt (se detiene en el primero)."""
    if not local_dir or not os.path.isdir(local_dir):
        return False
    return next(_iter_doc_files(local_dir), None) is not None


def doc_files(local_dir):
    """(raíz, subcarpetas): rutas relativas de los .md / .txt de `local_dir`, como mucho MAX_DOC_FILES.
    En la raíz van primero los diarios y después el resto por orden alfabético."""
    if not local_dir or not os.path.isdir(local_dir):
        return [], []
    files = list(itertools.islice(_iter_doc_files(local_dir), MAX_DOC_FILES))
    root = [f for f in files if "/" not in f]
    diaries = [d for name in DIARY_FILES for d in root if d.lower() == name]
    return diaries + [f for f in root if f not in diaries], [f for f in files if "/" in f]


class DiaryViewerDialog(QDialog):
    """Una pestaña por documento abierto (.md renderizado como Markdown, .txt como texto plano);
    Recargar vuelve a listar los archivos y conserva el scroll de cada pestaña."""

    def __init__(self, board_id, db_path=None, parent=None):
        super().__init__(parent)
        self.finished.connect(self.deleteLater)
        board = database.get_board(board_id, db_path)
        self.setWindowTitle(t("diary_viewer.title", board=board["name"]))
        self.resize(900, 700)
        self.local_dir = board.get("local_dir")
        self.paths = []
        self.browsers = []

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.more_btn = QPushButton(t("diary_viewer.more"))
        self.more_btn.setToolTip(t("diary_viewer.more_tooltip"))
        self.more_btn.setMenu(QMenu(self.more_btn))
        styles.style_menu(self.more_btn.menu())
        self.tabs.setCornerWidget(self.more_btn)
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
        """Relee las pestañas abiertas, abre las de los documentos nuevos de la raíz y rehace «Más…»."""
        for path, browser in zip(self.paths, self.browsers):
            self._load(path, browser)
        root, sub = doc_files(self.local_dir)
        for rel_path in root:
            self._ensure_tab(rel_path)
        self._rebuild_more_menu(sub)

    def _ensure_tab(self, rel_path):
        """Índice de la pestaña de `rel_path`, que se crea (y se lee) si aún no estaba abierta."""
        path = os.path.join(self.local_dir, rel_path)
        if path in self.paths:
            return self.paths.index(path)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        self.paths.append(path)
        self.browsers.append(browser)
        self._load(path, browser)
        return self.tabs.addTab(browser, rel_path)

    def _open_doc(self, rel_path):
        self.tabs.setCurrentIndex(self._ensure_tab(rel_path))

    def _rebuild_more_menu(self, sub):
        """Un submenú por carpeta de primer nivel con sus documentos (ruta dentro de la carpeta)."""
        menu = self.more_btn.menu()
        for folder_menu in menu.findChildren(QMenu):  # clear() no borra los submenús
            folder_menu.deleteLater()
        menu.clear()
        for folder, rel_paths in itertools.groupby(sub, key=lambda p: p.split("/", 1)[0]):
            # Con padre explícito: el QMenu de addMenu(str) lo destruye PySide al salir de ámbito
            folder_menu = QMenu(folder, menu)
            styles.style_menu(folder_menu)
            menu.addMenu(folder_menu)
            for rel_path in rel_paths:
                action = folder_menu.addAction(rel_path.split("/", 1)[1])
                action.triggered.connect(lambda _=False, p=rel_path: self._open_doc(p))
        self.more_btn.setVisible(bool(sub))

    @staticmethod
    def _load(path, browser):
        scroll = browser.verticalScrollBar().value()
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            browser.setPlainText(str(exc))
        else:
            if path.lower().endswith(".md"):
                browser.setMarkdown(text)
            else:
                browser.setPlainText(text)
        browser.verticalScrollBar().setValue(scroll)

    def _open_current_in_editor(self):
        if self.paths:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.paths[self.tabs.currentIndex()]))
