from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QPixmap, QColor, QIcon


def color_icon(color, size=13):
    """Genera un pequeño icono cuadrado del color indicado (para combos y listas)."""
    pix = QPixmap(size, size)
    pix.fill(QColor(color))
    return QIcon(pix)


class ClickableTagPill(QFrame):
    """Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor).
    El botón de borrar interno consume su propio clic y no dispara esta señal."""
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
