# Stylesheet for Ekin Kanban
# Contiene el diseño visual moderno de la aplicación mediante QSS (Qt Style Sheets).

def hex_to_rgb(hex_str):
    """Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def contrast_text(bg_hex):
    """Tinta (#201e1d) sobre fondos claros, crema (#f5ead8) sobre fondos oscuros — para que
    el texto de una píldora de color sólido (etiqueta, prioridad) siempre se lea, sin importar
    el color elegido por el usuario."""
    try:
        r, g, b = hex_to_rgb(bg_hex)
    except Exception:
        return "#f5ead8"
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#201e1d" if luminance > 0.58 else "#f5ead8"


# Design system "Organic" — Warm shell (paleta clara, defecto de la app).
# `accent_blue` se conserva como alias de `accent` durante la transición para
# no romper los módulos que aún lo referencian (board_view, widgets, sidebar,
# calendar_view, ai_spec_dialog, markdown_edit).
COLORS = {
    # Fondos
    "bg_main": "#f5ead8",       # crema: ventana y sidebar
    "bg_sidebar": "#f5ead8",    # sidebar = del color del fondo
    "bg_board": "#eae0cf",      # zona del carril, un paso más oscura
    "bg_column": "#f5ead8",     # tarjeta de columna
    "bg_card": "#f9f4ed",       # tarjeta de tarea (neutral-100)
    "bg_hover": "#eee7db",      # hover neutro (neutral-200)
    "bg_dark": "#2e2b25",       # neutral-900 (dock, bloques de código)
    # Líneas
    "border": "rgba(32, 30, 29, 16%)",  # divisor de 1 px
    "border_dashed": "#c0b6a5",         # borde discontinuo (Add task / New column)
    # Texto
    "text_main": "#201e1d",     # texto principal
    "text_muted": "#645c50",    # metadatos (neutral-700)
    "text_soft": "#474238",     # cuerpo secundario (neutral-800)
    # Acento (terracota)
    "accent": "#c67139",
    "accent_blue": "#c67139",   # alias transitorio
    "accent_hover": "#b2622d",  # accent-600
    "accent_pressed": "#8c491a",  # accent-700
    "accent_tint": "#fff2eb",   # accent-100 (relleno tenue)
    "accent_tint_2": "#ffe1d0",  # accent-200 (píldoras de vencimiento)
    "accent_ink": "#643312",    # accent-800 (texto sobre relleno tenue)
    # Segunda voz (salvia)
    "accent_2": "#7a8a5e",
    "accent_2_tint": "#e1eecc",  # accent-2-200
    "accent_2_ink": "#3d472b",  # accent-2-800
    # Destructivo — paso profundo del acento, nunca rojo puro
    "danger": "#8c491a",
    "danger_hover": "#643312",
    "success": "#7a8a5e",       # terminado / validado
    "on_accent": "#f5ead8",     # texto/icono crema SOBRE acento o superficie oscura
    "header_title": "#c67139",  # título del tablero: terracota en claro, blanco/crema en oscuro
}

def style_menu(menu):
    """Aplica el tema oscuro estándar (fondo/borde/item/selección) a un QMenu."""
    menu.setStyleSheet(f"""
        QMenu {{
            background-color: {COLORS['bg_sidebar']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
        }}
        QMenu::item {{
            padding: 6px 20px;
            color: {COLORS['text_main']};
        }}
        QMenu::item:selected {{
            background-color: {COLORS['accent_blue']};
        }}
    """)


def color_swatch_css(color, hover=False):
    """CSS para un botón de muestra de color (color + borde + esquinas redondeadas).
    `hover=True` añade un borde blanco al pasar el ratón."""
    css = f"""
        QPushButton {{
            background-color: {color};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
        }}
    """
    if hover:
        css += """
        QPushButton:hover {
            border-color: #ffffff;
        }
        """
    return css


def tag_pill_css(color):
    """CSS base para una pastilla de etiqueta coloreada (fondo + esquinas redondeadas).
    Cada sitio de uso añade encima sus propias reglas de fuente/relleno/marco."""
    return f"background-color: {color}; border-radius: 4px;"


def format_elapsed_time(total_seconds):
    """Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'."""
    total_seconds = max(0, int(total_seconds))
    minutes = total_seconds // 60
    hours = minutes // 60
    days = hours // 24
    if days > 0:
        return f"{days}d {hours % 24}h"
    if hours > 0:
        return f"{hours}h {minutes % 60}m"
    return f"{minutes}m"


def build_qss(c):
    return f"""
/* --- Estilos Generales --- */
QWidget {{
    font-family: 'Figtree', 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    color: {c["text_main"]};
}}

QMainWindow {{
    background-color: {c["bg_main"]};
}}

QDialog {{
    background-color: {c["bg_main"]};
    border: 1px solid {c["border"]};
    border-radius: 28px;
}}

/* --- Barra Lateral (Sidebar) --- */
#SidebarFrame {{
    background-color: {c["bg_sidebar"]};
    border-right: 1px solid {c["border"]};
}}

#SidebarTitle {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 17px;
    color: {c["text_main"]};
    margin-bottom: 10px;
}}

/* --- Lista de Tableros (QListWidget) --- */
QListWidget {{
    background-color: transparent;
    border: none;
    outline: 0;
}}

QListWidget::item {{
    padding: 0px 14px;
    min-height: 42px;
    margin: 3px 0px;
    border-radius: 16px;
    color: {c["text_main"]};
    font-weight: 500;
}}

QListWidget::item:hover {{
    background-color: {c["bg_hover"]};
    color: {c["text_main"]};
}}

QListWidget::item:selected {{
    background-color: {c["accent"]};
    color: {c["on_accent"]};
    font-weight: 600;
}}

/* --- Columnas de Kanban --- */
#ColumnContainer {{
    background-color: {c["bg_column"]};
    border-radius: 28px;
}}

#ColumnTitle {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 17px;
    color: {c["text_main"]};
}}

#ColumnHeaderBar {{
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}}

#TaskListArea {{
    background-color: transparent;
    border: none;
}}

/* El título del tablero se estila por objectName (los QLabel sí toman color/fuente de la
   QSS global, reactivo al tema). El fondo del carril y de la barra de cabecera NO se pueden
   pintar vía QSS global en estos QWidget/QFrame contenedores: se re-aplican inline en
   board_view.load_board(). */
#BoardHeaderTitle {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 25px;
    color: {c["header_title"]};
    background: transparent;
}}

#BoardCountsChip {{
    background-color: {c["bg_hover"]};
    color: {c["text_muted"]};
    font-size: 12px;
    border-radius: 11px;
    padding: 4px 12px;
    margin-left: 6px;
}}

/* --- Tarjeta de Tarea (TaskCard) --- */
/* Sin borde: la sombra (sm -> md en hover) la aplica QGraphicsDropShadowEffect. */
#TaskCardFrame {{
    background-color: {c["bg_card"]};
    border: none;
    border-radius: 16px;
    padding: 14px;
}}

#TaskCardTitle {{
    font-size: 15px;
    font-weight: 600;
    color: {c["text_main"]};
}}

#TaskCardTag {{
    font-size: 11px;
    padding: 3px 9px;
    border-radius: 9px;
    color: {c["text_soft"]};
}}

/* --- Botones --- */
QPushButton {{
    background-color: transparent;
    border: 1px solid {c["border"]};
    border-radius: 999px;
    padding: 7px 14px;
    font-weight: 500;
    color: {c["text_main"]};
}}

QPushButton:hover {{
    background-color: {c["bg_hover"]};
}}

QPushButton:pressed {{
    background-color: {c["bg_hover"]};
}}

#PrimaryButton {{
    background-color: {c["accent"]};
    border: none;
    color: {c["on_accent"]};
    font-weight: 600;
}}

#PrimaryButton:hover {{
    background-color: {c["accent_hover"]};
}}

#PrimaryButton:pressed {{
    background-color: {c["accent_pressed"]};
}}

#DangerButton {{
    background-color: {c["danger"]};
    border: none;
    color: {c["on_accent"]};
}}

#DangerButton:hover {{
    background-color: {c["danger_hover"]};
}}

#DangerButton:pressed {{
    background-color: {c["danger_hover"]};
}}

#AddTaskButton {{
    background-color: {c["bg_column"]};
    border: 1px dashed {c["border_dashed"]};
    color: {c["text_muted"]};
    border-radius: 999px;
    padding: 8px;
    font-weight: 600;
}}

#AddTaskButton:hover {{
    background-color: {c["accent_tint"]};
    border-color: {c["accent"]};
    color: {c["accent_pressed"]};
}}

/* --- Botones de la Barra de Formato de Texto (Negrita, Cursiva, Viñetas) --- */
#FormatButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 0px;
    color: {c["text_soft"]};
    font-size: 15px;
}}

#FormatButton:hover {{
    background-color: {c["bg_hover"]};
    color: {c["text_main"]};
}}

#FormatButton:checked {{
    background-color: {c["accent"]};
    border-color: {c["accent"]};
    color: {c["on_accent"]};
}}

#FormatButton:pressed {{
    background-color: {c["accent_hover"]};
    color: {c["bg_main"]};
}}

/* --- Inputs (QLineEdit, QTextEdit) --- */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 16px;
    padding: 6px 10px;
    color: {c["text_main"]};
    selection-background-color: {c["accent"]};
    selection-color: {c["on_accent"]};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {c["accent"]};
}}

/* --- Controles de formulario (combos, spin/date/time, checkboxes) --- */
/* Sin estas reglas, Qt los pinta con su paleta clara por defecto y quedan blancos
   sobre el tema oscuro. Se estilan de forma global para todas las pantallas. */
QComboBox {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 5px 26px 5px 10px;
    color: {c["text_main"]};
}}
QComboBox:hover {{ border-color: {c["text_muted"]}; }}
QComboBox:focus {{ border-color: {c["accent"]}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border: none;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {c["text_muted"]};
    width: 0;
    height: 0;
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    selection-background-color: {c["accent"]};
    selection-color: {c["on_accent"]};
    color: {c["text_main"]};
    outline: none;
}}

QAbstractSpinBox {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
    padding: 4px 8px;
    color: {c["text_main"]};
    selection-background-color: {c["accent"]};
    selection-color: {c["on_accent"]};
}}
QAbstractSpinBox:focus {{ border-color: {c["accent"]}; }}

QCheckBox {{
    color: {c["text_main"]};
    background: transparent;
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {c["border_dashed"]};
    border-radius: 4px;
    background-color: {c["bg_card"]};
}}
QCheckBox::indicator:checked {{
    background-color: {c["accent"]};
    border-color: {c["accent"]};
}}
QCheckBox::indicator:disabled {{ opacity: 0.4; }}

/* --- Task detail: cabecera y paneles --- */
#TaskDetailKicker {{
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
    color: {c["text_muted"]};
    background: transparent;
}}

/* Título editable en sitio: sin caja de input visible, tipo display grande */
#TaskDetailTitle {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 25px;
    color: {c["text_main"]};
    background: transparent;
    border: none;
    padding: 0px;
}}

#TaskDetailTitle:focus {{
    border: none;
    border-bottom: 1px solid {c["accent"]};
}}

#JournalHeader {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 17px;
    color: {c["text_main"]};
    background: transparent;
}}

/* --- Scrollbars Personalizadas (Sleek Scrollbar) --- */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {c["border_dashed"]};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c["text_muted"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c["border_dashed"]};
    min-width: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c["text_muted"]};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* --- Elementos de Chat/Diario --- */
#ChatScrollArea {{
    background-color: transparent;
    border: none;
}}

#LogEntryWidget {{
    background-color: {c["bg_card"]};
    border: none;
    border-radius: 20px;
}}

#LogTimestamp {{
    font-size: 10px;
    color: {c["text_muted"]};
    font-weight: bold;
    background-color: {c["bg_card"]};
}}

#LogContent {{
    font-size: 13px;
    color: {c["text_main"]};
    background-color: {c["bg_card"]};
}}

/* --- Filas de valores en el Gestor de Etiquetas --- */
#TagValueRow {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 16px;
}}

/* --- Barra de utilidades de la Sidebar (reloj + campana + calendario) --- */
#UtilityBar {{
    background-color: transparent;
    border: none;
}}

#ClockLabel {{
    color: {c["text_muted"]};
    font-size: 12px;
    font-weight: 600;
    background: transparent;
    border: none;
}}

#UtilityIconButton {{
    background-color: transparent;
    border: none;
    border-radius: 15px;
    padding: 0px;
    font-size: 15px;
}}

#UtilityIconButton:hover {{
    background-color: {c["bg_hover"]};
}}

#UtilityIconButton:pressed {{
    background-color: {c["bg_hover"]};
}}

#BellBadge {{
    background-color: {c["accent"]};
    color: {c["on_accent"]};
    font-size: 9px;
    font-weight: bold;
    border-radius: 7px;
    border: 2px solid {c["bg_main"]};
}}

/* --- Popup de vencimientos --- */
#NotificationsPopup {{
    background-color: {c["bg_main"]};
    border: 1px solid {c["border"]};
    border-radius: 28px;
}}

#NotificationItem {{
    background-color: transparent;
    border: none;
    border-radius: 16px;
    padding: 10px 12px;
    text-align: left;
    font-weight: 500;
}}

#NotificationItem:hover {{
    background-color: {c["bg_hover"]};
}}

/* --- Vista de Calendario --- */
#CalendarView {{
    background-color: {c["bg_main"]};
}}

#CalendarMonthLabel {{
    font-family: 'Caprasimo', 'Segoe UI', serif;
    font-size: 32px;
    color: {c["text_main"]};
}}

#WeekdayHeader {{
    color: {c["text_muted"]};
    font-size: 11px;
    font-weight: bold;
    padding-bottom: 2px;
}}

#CalNavButton {{
    background-color: transparent;
    border: 1px solid {c["border"]};
    border-radius: 17px;
    font-size: 16px;
    padding: 0px;
    color: {c["text_soft"]};
}}

#CalNavButton:hover {{
    background-color: {c["bg_hover"]};
    border-color: {c["border"]};
    color: {c["text_main"]};
}}

#DayCell {{
    background-color: {c["bg_card"]};
    border: none;
    border-radius: 16px;
}}

#DayNumber {{
    color: {c["text_muted"]};
    font-size: 12px;
    font-weight: bold;
    background: transparent;
    border: none;
}}

#CalendarChip {{
    background-color: {c["bg_hover"]};
    border: none;
    border-radius: 11px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 500;
    text-align: left;
    color: {c["text_soft"]};
}}

#CalendarChip:hover {{
    background-color: {c["accent"]};
    color: {c["on_accent"]};
}}
"""


LIGHT = dict(COLORS)

# Paleta oscura "Night lanes": espresso cálido + el mismo acento terracota, con la
# misma jerarquía de niveles que "Warm shell" (el carril un paso más oscuro que el
# fondo, y las columnas/tarjetas como cartas más claras encima).
DARK = {
    "bg_main": "#2f2b25",       # ventana + sidebar + columnas (encima del carril)
    "bg_sidebar": "#2f2b25",
    "bg_board": "#201d19",      # carril: el nivel más oscuro
    "bg_column": "#2f2b25",     # tarjeta de columna (= bg_main, sobre el carril más oscuro)
    "bg_card": "#3c362e",       # tarjeta de tarea: el nivel más claro (elevada)
    "bg_hover": "#473f35",
    "bg_dark": "#18150f",
    "border": "rgba(245, 234, 216, 13%)",
    "border_dashed": "#5c5648",
    "text_main": "#f5ead8",
    "text_muted": "#b3a892",
    "text_soft": "#d6cab6",
    "accent": "#d67f48",
    "accent_blue": "#d67f48",
    "accent_hover": "#f6a06b",
    "accent_pressed": "#c67139",
    "accent_tint": "#3a2a1f",
    "accent_tint_2": "#4a3527",
    "accent_ink": "#ffc6a5",
    "accent_2": "#8fa073",
    "accent_2_tint": "#2f3a23",
    "accent_2_ink": "#ccdbb2",
    "danger": "#c1683a",
    "danger_hover": "#a5551f",
    "success": "#8fa073",
    "on_accent": "#f5ead8",
    "header_title": "#f5ead8",  # título del tablero en oscuro: blanco/crema
}


def set_theme(name):
    """Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente."""
    COLORS.clear()
    COLORS.update(LIGHT if name == "light" else DARK)
    return build_qss(COLORS)
