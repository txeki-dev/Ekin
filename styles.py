# Stylesheet for Ekin Kanban
# Contiene el diseño visual moderno de la aplicación mediante QSS (Qt Style Sheets).

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

QSS = f"""
/* --- Estilos Generales --- */
QWidget {{
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: {COLORS["text_main"]};
}}

QMainWindow {{
    background-color: {COLORS["bg_main"]};
}}

QDialog {{
    background-color: {COLORS["bg_sidebar"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

/* --- Barra Lateral (Sidebar) --- */
#SidebarFrame {{
    background-color: {COLORS["bg_sidebar"]};
    border-right: 1px solid {COLORS["border"]};
}}

#SidebarTitle {{
    font-size: 18px;
    font-weight: bold;
    color: {COLORS["text_main"]};
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
    color: {COLORS["text_muted"]};
    font-weight: 500;
}}

QListWidget::item:hover {{
    background-color: {COLORS["bg_card"]};
    color: {COLORS["text_main"]};
}}

QListWidget::item:selected {{
    background-color: {COLORS["accent_blue"]};
    color: {COLORS["text_main"]};
    font-weight: bold;
}}

/* --- Columnas de Kanban --- */
#ColumnContainer {{
    border-radius: 10px;
}}

#ColumnTitle {{
    font-size: 14px;
    font-weight: bold;
    color: {COLORS["text_main"]};
}}

#ColumnHeaderBar {{
    border-bottom: 2px solid {COLORS["accent_blue"]};
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}}

#TaskListArea {{
    background-color: transparent;
    border: none;
}}

/* --- Tarjeta de Tarea (TaskCard) --- */
#TaskCardFrame {{
    background-color: {COLORS["bg_sidebar"]};
    border: 1.5px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 10px;
}}

#TaskCardFrame:hover {{
    border: 1.5px solid {COLORS["accent_blue"]};
    background-color: {COLORS["bg_card"]};
}}

#TaskCardTitle {{
    font-size: 13px;
    font-weight: 600;
    color: {COLORS["text_main"]};
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
    background-color: {COLORS["bg_card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #475569;
    border-color: {COLORS["text_muted"]};
}}

QPushButton:pressed {{
    background-color: {COLORS["bg_sidebar"]};
}}

#PrimaryButton {{
    background-color: {COLORS["accent_blue"]};
    border: none;
    color: #ffffff;
    font-weight: bold;
}}

#PrimaryButton:hover {{
    background-color: {COLORS["accent_hover"]};
}}

#PrimaryButton:pressed {{
    background-color: #1d4ed8;
}}

#DangerButton {{
    background-color: {COLORS["danger"]};
    border: none;
    color: #ffffff;
}}

#DangerButton:hover {{
    background-color: {COLORS["danger_hover"]};
}}

#DangerButton:pressed {{
    background-color: #b91c1c;
}}

#AddTaskButton {{
    background-color: transparent;
    border: 1px dashed {COLORS["border"]};
    color: {COLORS["text_muted"]};
    border-radius: 6px;
    padding: 8px;
    font-weight: bold;
}}

#AddTaskButton:hover {{
    background-color: {COLORS["bg_card"]};
    border-color: {COLORS["accent_blue"]};
    color: {COLORS["text_main"]};
}}

/* --- Inputs (QLineEdit, QTextEdit) --- */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {COLORS["bg_main"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 6px;
    color: {COLORS["text_main"]};
    selection-background-color: {COLORS["accent_blue"]};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {COLORS["accent_blue"]};
}}

/* --- Scrollbars Personalizadas (Sleek Scrollbar) --- */
QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    min-height: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["text_muted"]};
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
    background-color: {COLORS["border"]};
    min-width: 20px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS["text_muted"]};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* --- Elementos de Chat/Diario --- */
#ChatScrollArea {{
    background-color: {COLORS["bg_main"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

#LogEntryWidget {{
    background-color: {COLORS["bg_card"]};
    border-radius: 8px;
    margin: 4px;
    padding: 8px;
}}

#LogTimestamp {{
    font-size: 10px;
    color: {COLORS["text_muted"]};
    font-weight: bold;
}}

#LogContent {{
    font-size: 12.5px;
    color: {COLORS["text_main"]};
}}
"""
