import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from datetime import datetime
import styles
from icons import lucide_icon
from strings import t
from .markdown_edit import MarkdownTextEdit, RichTextToolbar
from .image_preview_dialog import show_image_preview


from .html_utils import fit_html_images, linkify_urls


class LogEntryWidget(QFrame):
    """Una entrada del diario/chat, con botones (pintados) de editar y eliminar y
    edición en línea del contenido."""
    def __init__(self, log_data, delete_callback, save_edit_callback, parent=None):
        super().__init__(parent)
        self.log_data = log_data
        self.log_id = log_data["id"]
        self.delete_callback = delete_callback
        self.save_edit_callback = save_edit_callback
        self._editing = False

        self.setObjectName("LogEntryWidget")
        self.init_ui(log_data)

    def _icon_button(self, kind, color, tooltip, hover_bg):
        btn = QPushButton()
        btn.setFixedSize(22, 22)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setIcon(lucide_icon(kind, color, 13))
        btn.setIconSize(QSize(13, 13))
        btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            f"QPushButton:hover {{ background-color: {hover_bg}; border-radius: 11px; }}"
        )
        return btn

    def init_ui(self, log_data):
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 8, 10, 8)
        self._layout.setSpacing(4)

        # Fila superior: Fecha/Hora + botones de editar y eliminar
        top_layout = QHBoxLayout()

        raw_date = log_data["created_at"]
        try:
            # Ej: '2026-07-09 19:30:00' -> '09/07/2026 19:30'
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S")
            formatted_date = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted_date = raw_date

        timestamp_label = QLabel(formatted_date)
        timestamp_label.setObjectName("LogTimestamp")
        top_layout.addWidget(timestamp_label)
        top_layout.addStretch()

        self.edit_btn = self._icon_button(
            "pencil", styles.COLORS['text_muted'], t("log_entry.edit_tooltip"), styles.COLORS['bg_hover'])
        self.edit_btn.clicked.connect(self._enter_edit_mode)
        top_layout.addWidget(self.edit_btn)

        self.delete_btn = self._icon_button(
            "x", styles.COLORS['danger'], t("log_entry.delete_tooltip"), styles.COLORS['accent_tint'])
        self.delete_btn.clicked.connect(lambda: self.delete_callback(self.log_id, self))
        top_layout.addWidget(self.delete_btn)

        self._layout.addLayout(top_layout)

        # Contenido de la entrada: ajustar imágenes para que no desborden y activar enlaces
        parent = self.parent()
        max_w = None
        if parent and hasattr(parent, "_chat_image_width"):
            max_w = parent._chat_image_width()
        content = linkify_urls(log_data["content"])
        content = fit_html_images(content, max_w)

        self.content_label = QLabel(content)
        self.content_label.setObjectName("LogContent")
        self.content_label.setWordWrap(True)
        self.content_label.setMinimumWidth(0)
        self.content_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # TextSelectableByMouse a solas SUSTITUYE el conjunto de flags (no lo amplía),
        # anulando LinksAccessibleByMouse -- sin él, linkActivated nunca se dispara con un
        # clic real aunque el resto del cableado esté bien (bug confirmado: la vista ampliada
        # funcionaba al componer una entrada pero no en una ya enviada).
        self.content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        self.content_label.setOpenExternalLinks(False)
        self.content_label.linkActivated.connect(self._on_content_link_activated)
        if "<img" in log_data["content"] or "<a" in content.lower():
            self.content_label.setCursor(Qt.PointingHandCursor)
        self._layout.addWidget(self.content_label)

    def update_content_width(self, max_w=None):
        """Actualiza el ancho de las imágenes y tablas del comentario para ajustarse
        al ancho dinámico disponible en el contenedor del chat."""
        if self._editing:
            return
        if max_w is None:
            parent = self.parent()
            if parent and hasattr(parent, "_chat_image_width"):
                max_w = parent._chat_image_width()
            else:
                max_w = 280
        content = linkify_urls(self.log_data["content"])
        content = fit_html_images(content, max_w)
        self.content_label.setText(content)

    def _enter_edit_mode(self):
        """Sustituye el contenido por un editor en línea con Guardar/Cancelar y soporte de atajos."""
        if self._editing:
            return
        self._editing = True
        self.content_label.hide()
        self.edit_btn.setEnabled(False)

        self._editor = MarkdownTextEdit()
        target_w = None
        parent = self.parent()
        if parent and hasattr(parent, "_chat_image_width"):
            self._editor.image_width_provider = parent._chat_image_width
            target_w = parent._chat_image_width()
        # Reajustar imágenes en el contenido cargado al ancho actual de la caja de edición
        content = fit_html_images(self.log_data["content"], target_w)
        self._editor.setHtml(content)
        self._editor.setMinimumHeight(110)
        self._editor.setMaximumHeight(260)

        self._edit_toolbar = RichTextToolbar(self._editor)
        self._layout.addWidget(self._edit_toolbar)
        self._layout.addWidget(self._editor)

        self._edit_btns_widget = QFrame()
        self._edit_btns_widget.setStyleSheet("background: transparent; border: none;")
        btns = QHBoxLayout(self._edit_btns_widget)
        btns.setContentsMargins(0, 4, 0, 0)
        btns.setSpacing(8)

        hint_lbl = QLabel("Ctrl+Enter para guardar · Esc para cancelar")
        hint_lbl.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
        btns.addWidget(hint_lbl)
        btns.addStretch()

        save_btn = QPushButton(t("log_entry.save_btn"))
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_edit)
        btns.addWidget(save_btn)

        cancel_btn = QPushButton(t("log_entry.cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self._cancel_edit)
        btns.addWidget(cancel_btn)

        self._layout.addWidget(self._edit_btns_widget)

        # Atajos de teclado para guardar y cancelar
        self._shortcut_save = QShortcut(QKeySequence("Ctrl+Return"), self._editor)
        self._shortcut_save.activated.connect(self._save_edit)
        self._shortcut_save2 = QShortcut(QKeySequence("Ctrl+Enter"), self._editor)
        self._shortcut_save2.activated.connect(self._save_edit)
        self._shortcut_cancel = QShortcut(QKeySequence("Escape"), self._editor)
        self._shortcut_cancel.activated.connect(self._cancel_edit)

        self._editor.setFocus()

    def _cancel_edit(self):
        """Cancela la edición volviendo al estado de lectura de forma instantánea y sin parpadeos."""
        if not self._editing:
            return
        self._exit_edit_mode()

    def _save_edit(self):
        """Guarda la edición del comentario invocando el callback."""
        if not self._editing or not hasattr(self, "_editor") or self._editor is None:
            return
        target_w = None
        parent = self.parent()
        if parent and hasattr(parent, "_chat_image_width"):
            target_w = parent._chat_image_width()
        new_html = fit_html_images(self._editor.toHtml(), target_w)
        if self.save_edit_callback:
            try:
                self.save_edit_callback(self.log_id, new_html, self)
            except TypeError:
                self.save_edit_callback(self.log_id, new_html)

    def update_content_in_place(self, new_html):
        """Actualiza el contenido renderizado tras guardar sin recrear el widget ni mover el scroll."""
        self.log_data["content"] = new_html
        parent = self.parent()
        max_w = None
        if parent and hasattr(parent, "_chat_image_width"):
            max_w = parent._chat_image_width()
        content = linkify_urls(new_html)
        content = fit_html_images(content, max_w)
        self.content_label.setText(content)
        if "<img" in new_html or "<a" in content.lower():
            self.content_label.setCursor(Qt.PointingHandCursor)
        else:
            self.content_label.setCursor(Qt.ArrowCursor)
        self._exit_edit_mode()

    def _exit_edit_mode(self):
        """Limpia los widgets temporales de edición y reactiva la etiqueta de lectura."""
        if hasattr(self, "_shortcut_save") and self._shortcut_save:
            self._shortcut_save.deleteLater()
            self._shortcut_save = None
        if hasattr(self, "_shortcut_save2") and self._shortcut_save2:
            self._shortcut_save2.deleteLater()
            self._shortcut_save2 = None
        if hasattr(self, "_shortcut_cancel") and self._shortcut_cancel:
            self._shortcut_cancel.deleteLater()
            self._shortcut_cancel = None

        if hasattr(self, "_edit_toolbar") and self._edit_toolbar:
            self._edit_toolbar.deleteLater()
            self._edit_toolbar = None
        if hasattr(self, "_editor") and self._editor:
            self._editor.deleteLater()
            self._editor = None
        if hasattr(self, "_edit_btns_widget") and self._edit_btns_widget:
            self._edit_btns_widget.deleteLater()
            self._edit_btns_widget = None

        self.content_label.show()
        self.edit_btn.setEnabled(True)
        self._editing = False

    def _on_content_link_activated(self, url):
        """Maneja los enlaces clicados dentro de una entrada ya enviada (imágenes, URLs web o borrar código)."""
        if url == "action:delete_code_block":
            self._enter_edit_mode()
            return
        elif url.startswith("data:image/"):
            show_image_preview(url, self)
        elif url.startswith(("http://", "https://", "mailto:", "file:", "ftp://")):
            from .security_utils import open_link_safely
            open_link_safely(self.window(), url)
        elif url and (os.path.exists(url) or (len(url) > 2 and url[1] == ":" and url[2] in ("/", "\\")) or url.startswith(("\\\\", "//"))):
            from .security_utils import open_link_safely
            open_link_safely(self.window(), url)
