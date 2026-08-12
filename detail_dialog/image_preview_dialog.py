from PySide6.QtCore import Qt, QByteArray
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

import styles
from strings import t


class ImagePreviewDialog(QDialog):
    """Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra
    con un clic en cualquier parte de la ventana, con Esc, o con el botón de cerrar."""

    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("image_preview.window_title"))
        self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {styles.COLORS['bg_main']}; }}")

        screen = self.screen() or QApplication.primaryScreen()
        available = screen.availableGeometry()
        max_w = int(available.width() * 0.9)
        max_h = int(available.height() * 0.9)
        # Siempre se escala (hacia arriba o hacia abajo) al recuadro objetivo -- una imagen
        # pequeña (ya reducida al ancho del chat/descripción al pegarla) debe verse
        # notablemente más grande aquí, no quedarse a su tamaño nativo.
        pixmap = pixmap.scaled(
            max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label)
        self.resize(pixmap.size())

        # Sin esto, cada imagen previsualizada deja un ImagePreviewDialog zombi (con su
        # QPixmap, potencialmente de varios MB) colgado para siempre del widget que lo abrió.
        self.finished.connect(self.deleteLater)

    def mousePressEvent(self, event):
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def pixmap_from_data_uri(data_uri):
    """Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo
    (isNull()) si el URI no trae una coma separadora o el base64 no decodifica a una
    imagen válida -- defensivo, nunca debería pasar con URIs generados por
    MarkdownTextEdit._insert_image, pero un click en contenido corrupto/antiguo no debe
    poder reventar la UI."""
    if "," not in data_uri:
        return QPixmap()
    b64 = data_uri.split(",", 1)[1]
    raw = QByteArray.fromBase64(b64.encode("ascii"))
    pixmap = QPixmap()
    pixmap.loadFromData(raw)
    return pixmap


def show_image_preview(data_uri, parent=None):
    """Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una
    imagen válida."""
    pixmap = pixmap_from_data_uri(data_uri)
    if pixmap.isNull():
        return
    dlg = ImagePreviewDialog(pixmap, parent)
    dlg.exec()
