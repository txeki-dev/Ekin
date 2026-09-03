from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from datetime import datetime
from widgets import make_glyph_icon
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

    def _icon_button(self, kind, color, tooltip, hover_rgba):
        btn = QPushButton()
        btn.setFixedSize(20, 20)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setIcon(make_glyph_icon(kind, color, 13))
        btn.setIconSize(QSize(13, 13))
        btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            f"QPushButton:hover {{ background-color: {hover_rgba}; border-radius: 3px; }}"
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
            "pencil", "#94a3b8", t("log_entry.edit_tooltip"), "rgba(148, 163, 184, 0.20)")
        self.edit_btn.clicked.connect(self._enter_edit_mode)
        top_layout.addWidget(self.edit_btn)

        self.delete_btn = self._icon_button(
            "cross", "#ef4444", t("log_entry.delete_tooltip"), "rgba(239, 68, 68, 0.15)")
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
        """Sustituye el contenido por un editor en línea con Guardar/Cancelar."""
        if self._editing:
            return
        self._editing = True
        self.content_label.hide()
        self.edit_btn.setEnabled(False)

        self._editor = MarkdownTextEdit()
        target_w = None
        if self.parent() and hasattr(self.parent(), "_chat_image_width"):
            self._editor.image_width_provider = self.parent()._chat_image_width
            target_w = self.parent()._chat_image_width()
        # Reajustar imágenes en el contenido cargado al ancho actual de la caja de edición
        content = fit_html_images(self.log_data["content"], target_w)
        self._editor.setHtml(content)
        self._editor.setMinimumHeight(90)
        self._layout.addWidget(RichTextToolbar(self._editor))
        self._layout.addWidget(self._editor)

        btns = QHBoxLayout()
        btns.addStretch()
        save_btn = QPushButton(t("log_entry.save_btn"))
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(lambda: self.save_edit_callback(self.log_id, fit_html_images(self._editor.toHtml(), target_w)))
        btns.addWidget(save_btn)
        cancel_btn = QPushButton(t("log_entry.cancel_btn"))
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self.save_edit_callback(self.log_id, None))
        btns.addWidget(cancel_btn)
        self._layout.addLayout(btns)
        self._editor.setFocus()

    def _on_content_link_activated(self, url):
        """Maneja los enlaces clicados dentro de una entrada ya enviada (imágenes, URLs web o borrar código)."""
        if url == "action:delete_code_block":
            self._enter_edit_mode()
            return
        elif url.startswith("data:image/"):
            show_image_preview(url, self)
        elif url.startswith(("http://", "https://", "mailto:", "file:", "ftp://")):
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl(url))
