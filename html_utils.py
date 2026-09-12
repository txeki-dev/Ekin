"""
Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.
Módulo desacoplado sin dependencias de GUI/Qt, seguro para exportadores, workers y modelos.
"""

import html
import re


def clean_html_description(raw: str) -> str:
    """Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o Qt.
    Elimina bloques <head>, <style>, <script>, comentarios y selectores CSS residuales,
    preservando únicamente el texto descriptivo limpio."""
    if not raw or not isinstance(raw, str):
        return ""

    # 1. Eliminar cabeceras, estilos embebidos, scripts y comentarios completos
    text = re.sub(r'<head\b[^>]*>.*?</head>', '', raw, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style\b[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # 2. Convertir etiquetas de bloque o salto de línea en saltos reales
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</p\s*>', '\n\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(?:tr|div|h[1-6])\s*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<li\b[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li\s*>', '\n', text, flags=re.IGNORECASE)

    # 3. Eliminar etiquetas HTML restantes
    text = re.sub(r'<[^>]+>', '', text)

    # 4. Decodificar entidades HTML (&nbsp;, &lt;, &quot;, &#39;, etc.)
    text = html.unescape(text)

    # 5. Barrido preventivo contra reglas CSS que pudieran haberse filtrado sin tags
    text = re.sub(r'(?:[a-zA-Z0-9_\-\.\#\:\s,]+)\s*\{[^}]*\}', '', text)

    # 6. Normalizar saltos de línea y espacios
    lines = [line.rstrip() for line in text.splitlines()]
    text = "\n".join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text
