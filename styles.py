# Stylesheet for Ekin Kanban
# Contiene el diseño visual moderno de la aplicación mediante QSS (Qt Style Sheets).

def hex_to_rgb(hex_str):
    """Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)."""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 3:
        hex_str = ''.join(c*2 for c in hex_str)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


COLORS = {
    "bg_main": "#0f172a",       # Slate 900
    "bg_sidebar": "#1e293b",    # Slate 800
    "bg_card": "#334155",       # Slate 700
    "bg_column": "#1e293b",     # Slate 800
    "border": "#475569",        # Slate 600
    "text_main": "#f8fafc",     # Slate 50
    "text_muted": "#94a3b8",    # Slate 400
    "accent_blue": "#3b82f6",   # Blue 500
    "accent_hover": "#2563eb",  # Blue 600
    "danger": "#ef4444",        # Red 500
    "danger_hover": "#dc2626",  # Red 600
    "success": "#10b981",       # Emerald 500
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
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: {c["text_main"]};
}}

QMainWindow {{
    background-color: {c["bg_main"]};
}}

QDialog {{
    background-color: {c["bg_sidebar"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
}}

/* --- Barra Lateral (Sidebar) --- */
#SidebarFrame {{
    background-color: {c["bg_sidebar"]};
    border-right: 1px solid {c["border"]};
}}

#SidebarTitle {{
    font-size: 18px;
    font-weight: bold;
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
    padding: 10px 15px;
    margin: 4px 8px;
    border-radius: 6px;
    color: {c["text_muted"]};
    font-weight: 500;
}}

QListWidget::item:hover {{
    background-color: {c["bg_card"]};
    color: {c["text_main"]};
}}

QListWidget::item:selected {{
    background-color: {c["accent_blue"]};
    color: {c["text_main"]};
    font-weight: bold;
}}

/* --- Columnas de Kanban --- */
#ColumnContainer {{
    border-radius: 10px;
}}

#ColumnTitle {{
    font-size: 14px;
    font-weight: bold;
    color: {c["text_main"]};
}}

#ColumnHeaderBar {{
    border-bottom: 2px solid {c["accent_blue"]};
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

#TaskListArea {{
    background-color: transparent;
    border: none;
}}

/* --- Tarjeta de Tarea (TaskCard) --- */
#TaskCardFrame {{
    background-color: {c["bg_sidebar"]};
    border: 1.5px solid {c["border"]};
    border-radius: 8px;
    padding: 10px;
}}

#TaskCardFrame:hover {{
    border: 1.5px solid {c["accent_blue"]};
    background-color: {c["bg_card"]};
}}

#TaskCardTitle {{
    font-size: 13px;
    font-weight: 600;
    color: {c["text_main"]};
}}

#TaskCardTag {{
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
    color: #ffffff;
}}

/* --- Botones --- */
QPushButton {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #475569;
    border-color: {c["text_muted"]};
}}

QPushButton:pressed {{
    background-color: {c["bg_sidebar"]};
}}

#PrimaryButton {{
    background-color: {c["accent_blue"]};
    border: none;
    color: #ffffff;
    font-weight: bold;
}}

#PrimaryButton:hover {{
    background-color: {c["accent_hover"]};
}}

#PrimaryButton:pressed {{
    background-color: #1d4ed8;
}}

#DangerButton {{
    background-color: {c["danger"]};
    border: none;
    color: #ffffff;
}}

#DangerButton:hover {{
    background-color: {c["danger_hover"]};
}}

#DangerButton:pressed {{
    background-color: #b91c1c;
}}

#AddTaskButton {{
    background-color: transparent;
    border: 1px dashed {c["border"]};
    color: {c["text_muted"]};
    border-radius: 6px;
    padding: 8px;
    font-weight: bold;
}}

#AddTaskButton:hover {{
    background-color: {c["bg_card"]};
    border-color: {c["accent_blue"]};
    color: {c["text_main"]};
}}

/* --- Botones de la Barra de Formato de Texto (Negrita, Cursiva, Viñetas) --- */
#FormatButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 0px;
    color: {c["text_muted"]};
    font-size: 15px;
}}

#FormatButton:hover {{
    background-color: {c["bg_card"]};
    border-color: {c["border"]};
    color: {c["text_main"]};
}}

#FormatButton:checked {{
    background-color: {c["accent_blue"]};
    border-color: {c["accent_blue"]};
    color: #ffffff;
}}

#FormatButton:pressed {{
    background-color: {c["accent_hover"]};
    color: #ffffff;
}}

/* --- Inputs (QLineEdit, QTextEdit) --- */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {c["bg_main"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    padding: 6px;
    color: {c["text_main"]};
    selection-background-color: {c["accent_blue"]};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {c["accent_blue"]};
}}

/* --- Scrollbars Personalizadas (Sleek Scrollbar) --- */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {c["border"]};
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
    background-color: {c["border"]};
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
    background-color: {c["bg_main"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
}}

#LogEntryWidget {{
    background-color: {c["bg_card"]};
    border-radius: 8px;
    margin: 4px;
    padding: 8px;
}}

#LogTimestamp {{
    font-size: 10px;
    color: {c["text_muted"]};
    font-weight: bold;
}}

#LogContent {{
    font-size: 12.5px;
    color: {c["text_main"]};
}}

/* --- Filas de valores en el Gestor de Etiquetas --- */
#TagValueRow {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
}}

/* --- Barra de utilidades de la Sidebar (reloj + campana + calendario) --- */
#UtilityBar {{
    background-color: {c["bg_main"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
}}

#ClockLabel {{
    color: {c["text_muted"]};
    font-size: 12px;
    font-weight: bold;
    background: transparent;
    border: none;
}}

#UtilityIconButton {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 0px;
    font-size: 15px;
}}

#UtilityIconButton:hover {{
    background-color: {c["bg_card"]};
    border-color: {c["border"]};
}}

#UtilityIconButton:pressed {{
    background-color: {c["bg_sidebar"]};
}}

#BellBadge {{
    background-color: {c["danger"]};
    color: #ffffff;
    font-size: 9px;
    font-weight: bold;
    border-radius: 7px;
    border: 1px solid {c["bg_main"]};
}}

/* --- Popup de vencimientos --- */
#NotificationsPopup {{
    background-color: {c["bg_sidebar"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
}}

#NotificationItem {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 8px;
    text-align: left;
    font-weight: 500;
}}

#NotificationItem:hover {{
    background-color: {c["bg_card"]};
    border-color: {c["accent_blue"]};
}}

/* --- Vista de Calendario --- */
#CalendarView {{
    background-color: {c["bg_main"]};
}}

#CalendarMonthLabel {{
    font-size: 18px;
    font-weight: bold;
    color: {c["text_main"]};
}}

#WeekdayHeader {{
    color: {c["text_muted"]};
    font-size: 11px;
    font-weight: bold;
    padding-bottom: 2px;
}}

#CalNavButton {{
    background-color: {c["bg_card"]};
    border: 1px solid {c["border"]};
    border-radius: 6px;
    font-size: 16px;
    font-weight: bold;
    padding: 0px;
}}

#CalNavButton:hover {{
    background-color: {c["accent_blue"]};
    border-color: {c["accent_blue"]};
    color: #ffffff;
}}

#DayCell {{
    background-color: {c["bg_column"]};
    border: 1px solid {c["border"]};
    border-radius: 8px;
}}

#DayNumber {{
    color: {c["text_muted"]};
    font-size: 11px;
    font-weight: bold;
    background: transparent;
    border: none;
}}

#CalendarChip {{
    background-color: {c["bg_card"]};
    border: none;
    border-radius: 4px;
    padding: 2px 4px;
    font-size: 10px;
    font-weight: 500;
    text-align: left;
    color: {c["text_main"]};
}}

#CalendarChip:hover {{
    background-color: {c["accent_blue"]};
    color: #ffffff;
}}
"""


DARK = dict(COLORS)
LIGHT = {
    "bg_main": "#f1f5f9",       # Slate 100
    "bg_sidebar": "#e2e8f0",    # Slate 200
    "bg_card": "#ffffff",       # White
    "bg_column": "#e2e8f0",     # Slate 200
    "border": "#cbd5e1",        # Slate 300
    "text_main": "#0f172a",     # Slate 900
    "text_muted": "#64748b",    # Slate 500
    "accent_blue": "#3b82f6",
    "accent_hover": "#2563eb",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "success": "#10b981",
}


def set_theme(name):
    """Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente."""
    COLORS.clear()
    COLORS.update(LIGHT if name == "light" else DARK)
    return build_qss(COLORS)
