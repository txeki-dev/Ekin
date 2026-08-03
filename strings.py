"""Cadenas de la interfaz, centralizadas para facilitar una futura traducción.

Uso: `from strings import t` y `t("clave.punteada")`, o `t("clave", nombre=valor)` para
las que llevan interpolación (usa `str.format`). Por ahora español es el único idioma
activo -- STRINGS es un diccionario plano, sin ningún mecanismo de selección de idioma --
pero mover aquí cada cadena visible deja el terreno preparado para añadir un segundo
idioma más adelante sin tocar el resto del código.
"""

STRINGS = {
    # --- main.py: ventana principal, bandeja, actualizaciones, datos de ejemplo ---
    "main.window_title": "Ekin Kanban - Trello Lite v{version}",
    "main.tray.tooltip": "Ekin Kanban",
    "main.tray.open": "Abrir Ekin",
    "main.tray.quit": "Salir",
    "main.tray.due_today_title": "Ekin — {count} tarea(s) vencen hoy",
    "main.update.available_title": "Actualización Disponible",
    "main.update.available_body": (
        "Hay una nueva versión de Ekin Kanban en GitHub.\n"
        "¿Deseas descargarla y reiniciar la aplicación ahora?"
    ),
    "main.update.done_title": "Actualizado",
    "main.update.done_body": "La aplicación se ha actualizado con éxito. Se reiniciará ahora.",
    "main.onboarding.board_name": "Mi Primer Tablero",
    "main.onboarding.col_todo": "Pendientes",
    "main.onboarding.col_doing": "En Progreso",
    "main.onboarding.col_done": "Completado",
    "main.onboarding.task_title": "Explorar Ekin Kanban",
    "main.onboarding.task_description": (
        "¡Bienvenido!\n\nEsta es una tarjeta de tarea. Haz click sobre ella para:\n"
        "- Cambiar el título\n"
        "- Añadir una descripción\n"
        "- Configurar etiquetas personalizadas\n"
        "- Registrar tus avances en el Diario personal (a la derecha)"
    ),
    "main.onboarding.tag_category": "Prioridad",
    "main.onboarding.tag_value": "Alta",
    "main.onboarding.log_entry": "He inicializado la aplicación por primera vez. ¡Todo listo para empezar a trabajar!",

    # --- board_view.py: tablero, columnas, tareas ---
    "board_view.column_edit.new_title": "Nueva Columna",
    "board_view.column_edit.edit_title": "Editar Columna",
    "board_view.column_edit.name_label": "<b>Nombre de la Columna:</b>",
    "board_view.column_edit.name_placeholder": "Ej. Pendientes, En Proceso...",
    "board_view.column_edit.color_label": "<b>Color de Acento:</b>",
    "board_view.column_edit.color_dialog_title": "Seleccionar Color de Columna",
    "board_view.column_edit.save": "Guardar",
    "board_view.column_edit.cancel": "Cancelar",
    "board_view.column_edit.warn_title": "Atención",
    "board_view.column_edit.warn_empty_name": "El nombre de la columna no puede estar vacío.",
    "board_view.board_selection.target_label": "<b>Selecciona el tablero de destino:</b>",
    "board_view.board_selection.cancel": "Cancelar",
    "board_view.board_selection.no_other_boards": "No hay otros tableros",
    "board_view.header.toggle_sidebar_tooltip": "Mostrar/Ocultar barra lateral",
    "board_view.header.default_title": "Mi Tablero",
    "board_view.welcome": (
        "💻 ¡Bienvenido a Ekin Kanban!\n\n"
        "Crea tu primer tablero en el panel lateral\n"
        "para empezar a organizar tus tareas y diarios."
    ),
    "board_view.add_column_btn": "➕ Nueva Columna",
    "board_view.delete_column.title": "Eliminar Columna",
    "board_view.delete_column.body": (
        "¿Estás seguro de eliminar la columna '{name}'?\n"
        "Esto borrará todas sus tareas de forma permanente."
    ),
    "board_view.delete_column.undo_label": "Eliminar columna",
    "board_view.copy_column.title": "Copiar Columna",
    "board_view.copy_column.action": "Copiar",
    "board_view.copy_column.fallback_board_name": "el tablero seleccionado",
    "board_view.copy_column.done_title": "Columna Copiada",
    "board_view.copy_column.done_body": (
        "La columna '{column}' y todas sus tareas/logs han sido copiadas con éxito a '{board}'."
    ),
    "board_view.add_task.title": "Nueva Tarea",
    "board_view.add_task.prompt": "Introduce el título de la tarea:",
    "board_view.delete_task.undo_label": "Eliminar tarea",

    # --- widgets.py: tarjetas, columnas (tooltips/menú), etiquetas ---
    "widgets.column.collapse_tooltip": "Plegar columna",
    "widgets.column.expand_tooltip": "Desplegar columna",
    "widgets.column.edit_tooltip": "Editar columna (opciones: editar, copiar, eliminar)",
    "widgets.column.title_drag_tooltip": "Arrastra para reordenar o mover esta columna a otro tablero",
    "widgets.column.task_count_tooltip": "{count} tarea(s)",
    "widgets.column.add_task_btn": "➕ Añadir Tarea",
    "widgets.column.menu_edit": "✏️ Editar Columna",
    "widgets.column.menu_copy": "📋 Copiar a otro tablero...",
    "widgets.column.menu_delete": "🗑️ Eliminar Columna",

    # --- sidebar.py: campana, tableros, barra de utilidades, exportar ---
    "sidebar.title": "EKIN",
    "sidebar.boards_subtitle": "Mis Tableros",
    "sidebar.add_board_btn": "➕ Nuevo Tablero",
    "sidebar.edit_board_btn": "✏️ Editar",
    "sidebar.copy_board_btn": "📋 Copiar",
    "sidebar.delete_board_btn": "🗑️ Borrar",
    "sidebar.archived_btn": "🗄 Archivados",
    "sidebar.archived_tooltip": "Mostrar/ocultar los tableros archivados (clic derecho en un tablero para archivar)",
    "sidebar.export_btn": "⬇ Exportar",
    "sidebar.export_tooltip": "Exportar todos los tableros a JSON / CSV / informe Markdown",
    "sidebar.bell_tooltip": "Tareas atrasadas o que vencen hoy o mañana",
    "sidebar.search_tooltip": "Buscar tareas (Ctrl+F)",
    "sidebar.calendar_tooltip": "Abrir vista de calendario",
    "sidebar.settings_tooltip": "Ajustes (tema, notificaciones)",
    "sidebar.notifications.header": "🔔  Vencimientos",
    "sidebar.notifications.empty": "No hay tareas atrasadas ni próximas. ✅",
    "sidebar.notifications.group_overdue": "ATRASADAS",
    "sidebar.notifications.group_today": "HOY",
    "sidebar.notifications.group_tomorrow": "MAÑANA",
    "sidebar.notifications.item_no_title": "(sin título)",
    "sidebar.notifications.item_tooltip": "{board} · vence {due_date}",
    "sidebar.board_button.archived_tooltip": "Tablero archivado — clic derecho para desarchivar",
    "sidebar.board_button.menu_unarchive": "📤 Desarchivar tablero",
    "sidebar.board_button.menu_archive": "🗄 Archivar tablero",
    "sidebar.board_edit.new_title": "Nuevo Tablero",
    "sidebar.board_edit.edit_title": "Editar Tablero",
    "sidebar.board_edit.copy_title": "Copiar Tablero",
    "sidebar.board_edit.copy_default_name": "{name} - Copia",
    "sidebar.board_edit.name_label": "<b>Nombre del Tablero:</b>",
    "sidebar.board_edit.name_placeholder": "Ej. Trabajo, Personal, Viaje...",
    "sidebar.board_edit.color_label": "<b>Color de Fondo:</b>",
    "sidebar.board_edit.color_dialog_title": "Seleccionar Color del Tablero",
    "sidebar.board_edit.save": "Guardar",
    "sidebar.board_edit.cancel": "Cancelar",
    "sidebar.board_edit.warn_title": "Atención",
    "sidebar.board_edit.warn_empty_name": "El nombre del tablero no puede estar vacío.",
    "sidebar.export_menu.json": "JSON (.json)",
    "sidebar.export_menu.csv": "CSV de tareas (.csv)",
    "sidebar.export_menu.markdown": "Informe Markdown (.md)",
    "sidebar.export.dialog_title": "Exportar {label}",
    "sidebar.export.error_title": "Error al exportar",
    "sidebar.export.error_body": "No se pudo exportar:\n{error}",
    "sidebar.export.done_title": "Exportado",
    "sidebar.export.done_body": "Exportación {label} guardada en:\n{path}",
    "sidebar.delete_board.title": "Eliminar Tablero",
    "sidebar.delete_board.body": (
        "¿Estás seguro de eliminar el tablero '{name}'?\n"
        "Esto borrará todas sus columnas, tareas y diarios asociados de forma permanente."
    ),
    "sidebar.delete_board.undo_label": "Eliminar tablero",
}


def t(key, **kwargs):
    """Devuelve la cadena asociada a `key`, interpolando **kwargs si se pasan."""
    text = STRINGS[key]
    return text.format(**kwargs) if kwargs else text
