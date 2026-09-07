"""Selector de color por círculos preseleccionados (New board / Edit column).

Seis colores del design system; el elegido lleva doble anillo (relleno + hueco + aro del
propio color). Si el color actual no está entre los presets, se añade como círculo extra.
También ofrece un botón «custom» que abre el QColorDialog para un color libre.
"""
from PySide6.QtCore import Qt, Signal, QRectF, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QAbstractButton, QColorDialog

import styles

PRESET_COLORS = ["#c67139", "#8fa073", "#8c491a", "#56633f", "#82796a", "#474238"]


class _ColorDot(QAbstractButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(30, 30)

    def sizeHint(self):
        return QSize(30, 30)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(self.color)
        cx, cy = 15, 15
        p.setPen(Qt.NoPen)
        if self.isChecked():
            p.setBrush(c)
            p.drawEllipse(QRectF(cx - 15, cy - 15, 30, 30))          # aro exterior
            p.setBrush(QColor(styles.COLORS["bg_main"]))
            p.drawEllipse(QRectF(cx - 12, cy - 12, 24, 24))          # hueco
        p.setBrush(c)
        p.drawEllipse(QRectF(cx - 10, cy - 10, 20, 20))              # relleno
        p.end()


class _CustomDot(QAbstractButton):
    """Círculo punteado con «+» que abre el selector de color libre."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(30, 30)
        self.setToolTip("Custom…")

    def sizeHint(self):
        return QSize(30, 30)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = p.pen()
        pen.setColor(QColor(styles.COLORS["border_dashed"]))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QRectF(5, 5, 20, 20))
        p.setPen(QColor(styles.COLORS["text_muted"]))
        p.drawText(self.rect(), Qt.AlignCenter, "+")
        p.end()


class ColorCirclesPicker(QWidget):
    """Fila de círculos de color con selección única y opción de color personalizado."""
    color_changed = Signal(str)

    def __init__(self, current="#c67139", parent=None):
        super().__init__(parent)
        self._color = current
        self._dots = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        colors = list(PRESET_COLORS)
        if current and current.lower() not in [c.lower() for c in colors]:
            colors.insert(0, current)

        for col in colors:
            dot = _ColorDot(col)
            dot.setChecked(col.lower() == current.lower())
            dot.clicked.connect(lambda _=False, c=col: self._select(c))
            lay.addWidget(dot)
            self._dots.append(dot)

        # Botón «custom»: abre el selector libre de color
        self.custom_btn = _CustomDot()
        self.custom_btn.clicked.connect(self._choose_custom)
        lay.addWidget(self.custom_btn)
        lay.addStretch()

    def _select(self, color):
        self._color = color
        for dot in self._dots:
            dot.setChecked(dot.color.lower() == color.lower())
        self.color_changed.emit(color)

    def _choose_custom(self):
        chosen = QColorDialog.getColor(QColor(self._color), self, "Custom color")
        if chosen.isValid():
            name = chosen.name()
            # Si no hay un dot para ese color, añadirlo al principio
            if name.lower() not in [d.color.lower() for d in self._dots]:
                dot = _ColorDot(name)
                dot.clicked.connect(lambda _=False, c=name: self._select(c))
                self.layout().insertWidget(0, dot)
                self._dots.insert(0, dot)
            self._select(name)

    def color(self):
        return self._color
