"""Iconos Lucide coloreados por estado.

Los SVG de Lucide usan `stroke="currentColor"` y `stroke-width="2"`; el diseño pide
2.75. Este módulo lee el SVG, sustituye color y grosor de trazo, y lo rasteriza a un
QPixmap/QIcon del tamaño pedido. Sustituye a los emoji de la versión anterior.
"""
import os
from functools import lru_cache

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

_ICON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icons", "lucide")


@lru_cache(maxsize=256)
def _svg_data(name, color, stroke):
    with open(os.path.join(_ICON_DIR, f"{name}.svg"), "r", encoding="utf-8") as fh:
        svg = fh.read()
    svg = svg.replace("currentColor", color).replace('stroke-width="2"', f'stroke-width="{stroke}"')
    return svg.encode("utf-8")


@lru_cache(maxsize=1024)
def lucide_pixmap(name, color="#645c50", size=18, stroke=2.75):
    """QPixmap cuadrado (size x size) del icono Lucide `name`, trazado en `color`."""
    renderer = QSvgRenderer(QByteArray(_svg_data(name, color, stroke)))
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return pm


def lucide_icon(name, color="#645c50", size=18, stroke=2.75):
    """QIcon del icono Lucide `name` trazado en `color`."""
    return QIcon(lucide_pixmap(name, color, size, stroke))
