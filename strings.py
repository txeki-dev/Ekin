"""Cadenas de la interfaz, centralizadas para facilitar una futura traducción.

Uso: `from strings import t` y `t("clave.punteada")`, o `t("clave", nombre=valor)` para
las que llevan interpolación (usa `str.format`). Por ahora español es el único idioma
activo -- STRINGS es un diccionario plano, sin ningún mecanismo de selección de idioma --
pero mover aquí cada cadena visible deja el terreno preparado para añadir un segundo
idioma más adelante sin tocar el resto del código.
"""

STRINGS = {
    # --- main.py: ventana principal, bandeja, actualizaciones, datos de ejemplo ---
    "main.window_title": "Ekin v{version}",
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
    "widgets.card.board_link_tooltip": "Ir al tablero vinculado",
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
    "sidebar.export_btn": "⬇ Exportar...",
    "sidebar.export_tooltip": "Exportar tableros a JSON, CSV o Markdown",
    "sidebar.import_btn": "⬆ Importar...",
    "sidebar.import_tooltip": "Importar tableros, columnas y tareas desde un archivo JSON",
    "sidebar.bell_tooltip": "Tareas atrasadas o que vencen hoy o mañana",
    "sidebar.search_tooltip": "Buscar tareas (Ctrl+F)",
    "sidebar.calendar_tooltip": "Abrir vista de calendario",
    "sidebar.settings_tooltip": "Ajustes (tema, notificaciones)",
    "sidebar.shortcuts_tooltip": "Atajos de teclado (Ctrl+/)",
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

    # --- export_dialog.py & import_dialog.py: exportación e importación avanzada ---
    "export_dialog.window_title": "Exportar Tableros",
    "export_dialog.scope_group": "<b>Alcance de la exportación:</b>",
    "export_dialog.scope_all": "Todos los tableros (incluidos archivados)",
    "export_dialog.scope_current": "Solo el tablero activo: «{name}»",
    "export_dialog.format_group": "<b>Formato de archivo:</b>",
    "export_dialog.format_json": "JSON (.json) — Datos completos o plantillas",
    "export_dialog.json_include_tasks": "Incluir tareas, etiquetas, enlaces y diario",
    "export_dialog.json_template_hint": "Si se desmarca, se exportará únicamente la estructura de columnas como plantilla reusable.",
    "export_dialog.format_csv": "CSV (.csv) — Lista de tareas para hojas de cálculo (Excel / Sheets)",
    "export_dialog.format_markdown": "Markdown (.md) — Informe legible del proyecto",
    "export_dialog.md_include_details": "Incluir descripciones, enlaces y diario en el informe",
    "export_dialog.export_btn": "💾 Exportar a Archivo...",
    "export_dialog.cancel_btn": "Cancelar",
    "export_dialog.save_title": "Guardar archivo de exportación",
    "export_dialog.done_title": "Exportación Completada",
    "export_dialog.done_body": "Exportación {label} guardada correctamente en:\n{path}",
    "export_dialog.error_title": "Error en la exportación",
    "export_dialog.error_body": "No se pudo completar la exportación:\n{error}",

    "import_dialog.window_title": "Importar Tableros desde JSON",
    "import_dialog.open_title": "Seleccionar archivo JSON para importar",
    "import_dialog.file_label": "<b>Archivo:</b> {filename}",
    "import_dialog.summary_label": "Se han detectado <b>{boards}</b> tablero(s), <b>{columns}</b> columna(s) y <b>{tasks}</b> tarea(s).",
    "import_dialog.options_group": "<b>Opciones de importación:</b>",
    "import_dialog.opt_full": "Importar todo (tableros, columnas, tareas, etiquetas, enlaces y diario)",
    "import_dialog.opt_structure_only": "Importar solo estructura de columnas (como plantilla sin tareas)",
    "import_dialog.template_only_hint": "Este archivo contiene únicamente estructura de columnas (plantilla).",
    "import_dialog.import_btn": "📥 Importar a Ekin",
    "import_dialog.cancel_btn": "Cancelar",
    "import_dialog.done_title": "Importación Completada",
    "import_dialog.done_body": "Se han importado {count} tablero(s) con éxito.",
    "import_dialog.error_title": "Error en la importación",
    "import_dialog.error_body": "No se pudo importar el archivo:\n{error}",

    # --- calendar_view.py: vista de calendario + ajustes de sincronización .ics ---
    "calendar.chip_no_title": "(sin título)",
    "calendar.chip_tooltip": "{board} · {title}\nArrastra a otro día para reprogramar",
    "calendar.more_tasks": "+{count} más",
    "calendar.today_btn": "Hoy",
    "calendar.mode_month": "Mes",
    "calendar.mode_week": "Semana",
    "calendar.mode_day": "Día",
    "calendar.mode_tooltip": "Vista del calendario",
    "calendar.board_filter_tooltip": "Filtrar por tablero",
    "calendar.settings_btn": "⚙  Ajustes",
    "calendar.settings_tooltip": "Sincronizar / exportar a Google, Apple u Outlook",
    "calendar.close_btn": "✖  Cerrar",
    "calendar.close_tooltip": "Volver a la vista de tablero",
    "calendar.all_boards": "Todos los tableros",
    "calendar.week_period": "Semana {start} – {end}",
    "calendar.error_title": "Error",

    "calendar.settings_dialog.title": "Ajustes de Calendario",
    "calendar.settings_dialog.header": "🔗 <b>Sincronización de calendario</b>",
    "calendar.settings_dialog.info": (
        "Ekin exporta tus tareas con fecha de vencimiento a un archivo estándar "
        "<b>iCalendar (.ics)</b>, compatible con Google Calendar, Apple Calendar y Outlook."
    ),
    "calendar.settings_dialog.sync_title": "🔄 <b>Sincronización automática</b> (recomendado)",
    "calendar.settings_dialog.sync_desc": (
        "Ekin mantiene un archivo .ics <b>siempre al día</b> (lo reescribe al cambiar "
        "tareas). Guárdalo en una carpeta de Dropbox / OneDrive / Google Drive y "
        "<b>suscríbete</b> a él una sola vez: a partir de ahí se actualiza solo."
    ),
    "calendar.settings_dialog.sync_board_tooltip": "Sincronizar automáticamente todos los tableros o solo uno",
    "calendar.settings_dialog.configure_btn_initial": "📂  Elegir archivo…",
    "calendar.settings_dialog.configure_btn_change": "📂  Cambiar archivo…",
    "calendar.settings_dialog.disable_btn": "Desactivar",
    "calendar.settings_dialog.subscribe_title": "🌐 <b>Suscribirse en tu calendario</b>",
    "calendar.settings_dialog.subscribe_desc": (
        "Sube el archivo .ics a una carpeta pública (Google Drive / Dropbox / OneDrive) "
        "y pega aquí su <b>URL pública</b>. Ekin la guarda y, según el botón, la copia al "
        "portapapeles y abre la página del proveedor para <b>añadir un calendario por URL</b> "
        "(el paso manual que suele fallar). Guía detallada abajo."
    ),
    "calendar.settings_dialog.public_url_placeholder": "https://…/ekin_calendario.ics",
    "calendar.settings_dialog.google_btn_tooltip": "Copiar la URL y abrir «Añadir por URL» de Google Calendar",
    "calendar.settings_dialog.outlook_btn_tooltip": "Copiar la URL y abrir «Suscribirse desde la web» de Outlook",
    "calendar.settings_dialog.apple_btn_tooltip": "Copiar la URL como enlace webcal:// para iPhone/Mac",
    "calendar.export_once_btn": "⬇  Exportar copia…",
    "calendar.export_once_tooltip": "Guardar una copia .ics puntual (snapshot) en otra ubicación",
    "calendar.export_board_tooltip": "Exportar el calendario de todos los tableros o de uno solo",
    "calendar.settings_dialog.close_btn": "Cerrar",
    "calendar.settings_dialog.sync_active": "✅ Sincronizando en:<br><code>{path}</code>",
    "calendar.settings_dialog.sync_inactive": "⚪ Sincronización automática desactivada.",
    "calendar.settings_dialog.configure_file_dialog_title": "Archivo de sincronización",
    "calendar.settings_dialog.configure_error_body": "No se pudo crear el archivo:\n{error}",
    "calendar.settings_dialog.sync_activated_title": "Sincronización activada",
    "calendar.settings_dialog.sync_activated_body": (
        "Ekin mantendrá {count} tarea(s) sincronizadas en:\n{path}\n\n"
        "Suscríbete a este archivo una vez desde tu calendario y se actualizará solo."
    ),
    "calendar.settings_dialog.empty_url_title": "URL vacía",
    "calendar.settings_dialog.empty_url_body": (
        "Pega primero la URL pública de tu archivo .ics (el enlace compartido de la carpeta "
        "en la nube donde lo sincronizas)."
    ),
    "calendar.settings_dialog.google_title": "Google Calendar",
    "calendar.settings_dialog.google_body": (
        "He copiado la URL al portapapeles y abierto Google Calendar (en el ordenador; "
        "la app de móvil no permite añadir por URL).\n\n"
        "1. Menú lateral izquierdo → «Otros calendarios» → «+» → «Desde una URL».\n"
        "2. Pega la URL (Ctrl+V) y pulsa «Añadir calendario».\n\n"
        "Nota: Google recarga los calendarios por URL de forma lenta (cada varias horas, "
        "hasta ~24 h) y no se puede forzar."
    ),
    "calendar.settings_dialog.outlook_title": "Outlook Calendar",
    "calendar.settings_dialog.outlook_body": (
        "He copiado la URL al portapapeles y abierto Outlook en el navegador.\n\n"
        "1. En Outlook.com: «Agregar calendario» → «Suscribirse desde la web».\n"
        "   (En Outlook de trabajo/Microsoft 365 la ruta es outlook.office.com → misma opción.)\n"
        "2. Pega la URL (Ctrl+V), ponle un nombre y color, y pulsa «Importar»/«Suscribirse».\n\n"
        "El Outlook de escritorio (clásico) también admite: Inicio → «Abrir calendario» → "
        "«De Internet…» y pegar la URL."
    ),
    "calendar.settings_dialog.apple_title": "Apple / iCloud",
    "calendar.settings_dialog.apple_body": (
        "He copiado la URL como enlace <b>webcal://</b> al portapapeles (así iOS/macOS la "
        "reconocen como suscripción). Pégala aquí:\n\n"
        "• iPhone/iPad: Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → "
        "«Añadir calendario suscrito» → pega el enlace → Siguiente.\n"
        "• Mac (app Calendario): Archivo → «Nueva suscripción de calendario…» → pega el enlace → "
        "Suscribirse; ahí puedes fijar la frecuencia de actualización (incluso cada pocos minutos).\n\n"
        "La suscripción se guarda en iCloud y se ve en todos tus dispositivos Apple."
    ),
    "calendar.settings_dialog.provider_guide": (
        "<b>📋 Cómo suscribirte (se mantiene sincronizado, sin duplicados)</b>"
        "<p><b>0) Consigue una URL pública y directa del .ics.</b> Guarda el archivo en una "
        "carpeta de la nube y comparte el enlace <i>directo al archivo</i> (no a una página de "
        "vista previa):"
        "<ul>"
        "<li><b>Google Drive</b>: compartir «Cualquiera con el enlace». El enlace normal apunta a "
        "una vista HTML; usa la forma de descarga directa "
        "<code>https://drive.google.com/uc?export=download&id=ID_DEL_ARCHIVO</code>.</li>"
        "<li><b>Dropbox</b>: copia el enlace y cambia el final <code>?dl=0</code> por "
        "<code>?dl=1</code>.</li>"
        "<li><b>OneDrive</b>: «Compartir» → «Cualquier persona con el vínculo» → copia el enlace.</li>"
        "</ul>"
        "Ábrela en una ventana de incógnito: debes ver texto que empieza por "
        "<code>BEGIN:VCALENDAR</code>. Si ves un login o una vista previa, el enlace no sirve.</p>"
        "<p><b>🟦 Google Calendar</b> (solo en el ordenador): menú lateral → «Otros calendarios» → "
        "«+» → «Desde una URL» → pega la URL → «Añadir calendario». Refresco lento (varias horas).</p>"
        "<p><b>🟧 Outlook</b>: en <i>Outlook.com/365 (web)</i> → «Agregar calendario» → «Suscribirse "
        "desde la web» → pega la URL → nombre/color → «Importar». En <i>Outlook de escritorio</i> → "
        "Inicio → «Abrir calendario» → «De Internet…» → pega la URL.</p>"
        "<p><b>🍎 Apple / iCloud</b> (usa un enlace <code>webcal://</code>): "
        "<i>iPhone/iPad</i> → Ajustes → Calendario → Cuentas → Añadir cuenta → Otra → «Añadir "
        "calendario suscrito» → pega el enlace. <i>Mac</i> → app Calendario → Archivo → «Nueva "
        "suscripción de calendario…» → pega el enlace (puedes elegir cada cuánto se actualiza).</p>"
        "<p><b>⚠️ Suscribir ≠ Importar.</b> «Importar» una copia es una foto fija: no refleja "
        "cambios ni borrados y puede duplicar eventos. Suscríbete a la URL para que se actualice solo.</p>"
    ),
    "calendar.export_dialog_title": "Exportar copia del calendario",
    "calendar.export_error_body": "No se pudo exportar el calendario:\n{error}",
    "calendar.export_done_title": "Exportado",
    "calendar.export_done_body": (
        "Se exportaron {count} tarea(s) con fecha a:\n{path}\n\n"
        "Recuerda: una copia importada es una foto fija; para que se mantenga al día, "
        "usa la sincronización automática de arriba y suscríbete al archivo."
    ),

    # --- search_dialog.py: búsqueda global de tareas ---
    "search.window_title": "Buscar tareas",
    "search.header": "🔍 <b>Buscar tareas</b>",
    "search.text_placeholder": "Título o descripción…",
    "search.all_boards": "Todos los tableros",
    "search.all_tags": "Todas las etiquetas",
    "search.only_due_checkbox": "Solo con vencimiento",
    "search.close_btn": "Cerrar",
    "search.result_count": "{count} resultado(s)",
    "search.no_results": "Sin resultados.",
    "search.result_no_title": "(sin título)",
    "search.result_tooltip": "{board} · {column}",

    # --- settings_dialog.py: pantalla de Ajustes (tema, notificaciones) ---
    "settings.window_title": "Ajustes",
    "settings.header": "⚙ <b>Ajustes de Ekin</b>",
    "settings.theme_label": "🎨 Tema:",
    "settings.theme_dark": "Oscuro",
    "settings.theme_light": "Claro",
    "settings.theme_hint": (
        "El tema claro es <i>experimental</i>: algunos colores de tarjetas/tableros están "
        "afinados para el oscuro. Se aplica del todo al reiniciar la app."
    ),
    "settings.notifications_checkbox": "Mostrar avisos de Windows para tareas que vencen hoy",
    "settings.timer_alert_label": "⏱ Avisar en la tarjeta si un temporizador lleva más de:",
    "settings.timer_alert_suffix": " h",
    "settings.timer_alert_hint": (
        "Las tarjetas con un temporizador activo se resaltan en rojo al superar este tiempo. "
        "Las que ya estén abiertas no se recolorean al cambiar este valor hasta que se "
        "recarguen (cambiar de tablero, editar una tarea, etc.)."
    ),
    "settings.geometry_hint": "El tamaño y la posición de la ventana se recuerdan automáticamente.",
    "settings.close_btn": "Cerrar",

    # --- shortcuts_dialog.py: diálogo "Atajos de teclado" (Ctrl+/) ---
    "shortcuts.window_title": "Atajos de teclado",
    "shortcuts.header": "⌨ <b>Atajos de teclado</b>",
    "shortcuts.section_general": "General y navegación",
    "shortcuts.section_editor": "Editor de texto enriquecido (descripción y diario)",
    "shortcuts.item_search": "Ctrl+F — Búsqueda global de tareas",
    "shortcuts.item_new_task": (
        "Ctrl+N — Nueva tarea en la última columna con la que interactuaste (si no hay "
        "ninguna, la primera del tablero activo); dentro del editor de texto, Ctrl+N es Negrita"
    ),
    "shortcuts.item_new_column": "Ctrl+Shift+N — Nueva columna en el tablero activo",
    "shortcuts.item_prev_next_board": "Alt+↑ / Alt+↓ — Tablero anterior / siguiente",
    "shortcuts.item_jump_board": "Ctrl+1 … Ctrl+9 — Saltar directamente al tablero Nº de la barra lateral",
    "shortcuts.item_calendar": "Ctrl+Shift+C — Abrir el Calendario",
    "shortcuts.item_settings": "Ctrl+, — Abrir Ajustes",
    "shortcuts.item_shortcuts": "Ctrl+/ — Mostrar esta ventana",
    "shortcuts.item_undo_redo": "Ctrl+Z / Ctrl+Y (o Ctrl+Shift+Z) — Deshacer / Rehacer",
    "shortcuts.item_close_dialog": "Esc — Cerrar el diálogo abierto",
    "shortcuts.item_bold": "Ctrl+B o Ctrl+N — Negrita (dentro del editor)",
    "shortcuts.item_italic": "Ctrl+K o Ctrl+I — Cursiva (dentro del editor)",
    "shortcuts.item_strike": "Ctrl+Shift+X — Tachado (dentro del editor)",
    "shortcuts.item_nest_bullet": "Tab (sobre una viñeta) — Anidar la viñeta (dentro del editor)",
    "shortcuts.item_arrow": "Escribir «-->» se convierte en → automáticamente (dentro del editor)",
    "shortcuts.item_add_log": "Ctrl+Enter — Añadir la nota al Diario (detalle de tarea)",
    "shortcuts.hint": "Pulsa Ctrl+/ en cualquier momento para volver a ver esta ventana.",
    "shortcuts.close_btn": "Cerrar",

    # --- detail_dialog/markdown_edit.py: editor de texto enriquecido (barra de formato) ---
    "markdown_edit.bold_tooltip": "Negrita (Ctrl+B o Ctrl+N)",
    "markdown_edit.italic_tooltip": "Cursiva (Ctrl+K o Ctrl+I)",
    "markdown_edit.strike_tooltip": "Tachado (Ctrl+Shift+X)",
    "markdown_edit.bullet_tooltip": "Lista con viñetas  ·  también con «* », «- » o «+ »",
    "markdown_edit.hr_tooltip": "Línea separadora  ·  también escribiendo «---»",
    "markdown_edit.arrow_tooltip": "Insertar flecha (→)  ·  también escribiendo «-->»",
    "markdown_edit.color_tooltip": "Color del texto",
    "markdown_edit.color_default": "Color por defecto",
    "markdown_edit.color_more": "Más colores…",
    "markdown_edit.color_dialog_title": "Seleccionar color de texto",
    "markdown_edit.table_tooltip": "Insertar tabla",
    "markdown_edit.table_dialog_title": "Insertar tabla",
    "markdown_edit.table_rows_label": "Filas:",
    "markdown_edit.table_cols_label": "Columnas:",
    "markdown_edit.code_tooltip": "Insertar bloque de código  ·  también con «```»",
    "markdown_edit.code_dialog_title": "Insertar bloque de código",
    "markdown_edit.code_lang_label": "Lenguaje de programación:",
    "markdown_edit.code_text_label": "Código:",
    "markdown_edit.code_insert_btn": "Insertar",
    "markdown_edit.code_cancel_btn": "Cancelar",
    "markdown_edit.delete_code_btn": "Borrar",
    "markdown_edit.delete_code_tooltip": "Eliminar este bloque de código",
    "markdown_edit.delete_code_btn_menu": "Eliminar bloque de código",
    "markdown_edit.link_tooltip": "Insertar enlace web (URL)",
    "markdown_edit.link_dialog_title": "Insertar enlace",
    "markdown_edit.link_url_label": "Dirección web (URL):",
    "markdown_edit.link_text_label": "Texto a mostrar (opcional):",
    "markdown_edit.link_insert_btn": "Insertar",
    "markdown_edit.link_cancel_btn": "Cancelar",

    # --- detail_dialog/log_entry.py: entrada del diario/chat ---
    "log_entry.edit_tooltip": "Editar comentario",
    "log_entry.delete_tooltip": "Eliminar comentario",
    "log_entry.save_btn": "Guardar",
    "log_entry.cancel_btn": "Cancelar",

    # --- detail_dialog/image_preview_dialog.py: vista ampliada de una imagen pegada ---
    "image_preview.window_title": "Vista previa de imagen",

    # --- detail_dialog/tag_manager_dialog.py: gestor del catálogo de etiquetas ---
    "tag_manager.window_title": "Gestionar Etiquetas",
    "tag_manager.header": "🏷️ <b>Etiquetas</b>",
    "tag_manager.add_category_btn": "＋ Nueva",
    "tag_manager.category_action_label": "Renombrar etiqueta",  # tooltip + QInputDialog title (misma frase)
    "tag_manager.delete_category_tooltip": "Eliminar etiqueta",  # tooltip + QMessageBox title (misma frase)
    "tag_manager.values_title_default": "<b>Valores</b>",
    "tag_manager.values_title_for_category": "<b>Valores de «{category}»</b>",
    "tag_manager.new_value_placeholder": "Nuevo valor (ej. Alta)…",
    "tag_manager.new_value_color_tooltip": "Color del nuevo valor",
    "tag_manager.add_value_btn": "Añadir valor",
    "tag_manager.close_btn": "Cerrar",
    "tag_manager.add_category_dialog_title": "Nueva etiqueta",
    "tag_manager.add_category_prompt": "Nombre de la etiqueta (ej. Prioridad):",
    "tag_manager.new_name_prompt": "Nuevo nombre:",  # usado al renombrar etiqueta y al renombrar valor
    "tag_manager.delete_category_body": (
        "¿Eliminar la etiqueta «{category}» y todos sus valores?\n"
        "Se quitará de todas las tareas que la usen."
    ),
    "tag_manager.no_category_hint": "Crea o selecciona una etiqueta a la izquierda para definir sus valores.",
    "tag_manager.no_values_hint": "Aún no hay valores. Añade el primero abajo.",
    "tag_manager.swatch_tooltip": "Cambiar color",
    "tag_manager.rename_value_tooltip": "Renombrar valor",  # tooltip + QInputDialog title (misma frase)
    "tag_manager.delete_value_tooltip": "Eliminar valor",  # tooltip + QMessageBox title (misma frase)
    "tag_manager.color_dialog_title": "Color del valor",
    "tag_manager.warn_title": "Atención",
    "tag_manager.duplicate_value_body": "Ya existe un valor con ese nombre en esta etiqueta.",
    "tag_manager.delete_value_body": (
        "¿Eliminar el valor «{value}»?\nSe quitará de las tareas que lo tengan asignado."
    ),

    # --- detail_dialog/tag_picker_dialog.py: asignar/editar una etiqueta en una tarea ---
    "tag_picker.title_edit": "Editar Etiqueta",
    "tag_picker.title_assign": "Asignar Etiqueta",
    "tag_picker.category_label": "🏷️ <b>Etiqueta</b>",
    "tag_picker.value_label": "<b>Valor</b>",
    "tag_picker.manage_btn": "⚙  Gestionar etiquetas…",
    "tag_picker.accept_btn": "Aceptar",
    "tag_picker.cancel_btn": "Cancelar",
    "tag_picker.none_option": "— Ninguno (ocultar) —",
    "tag_picker.no_categories_hint": "No hay etiquetas definidas. Usa «Gestionar etiquetas…» para crear una.",
    "tag_picker.no_values_hint": "Esta etiqueta no tiene valores. Añádelos en «Gestionar etiquetas…».",
    "tag_picker.warn_title": "Atención",
    "tag_picker.warn_no_category": "Primero crea una etiqueta en «Gestionar etiquetas…».",
    "tag_picker.warn_no_value": "Selecciona un valor (o créalo en «Gestionar etiquetas…»).",

    # --- detail_dialog/task_detail_dialog.py: diálogo principal de detalle de tarea ---
    "task_detail.window_title": "Detalles de la Tarea",
    "task_detail.title_label": "📝 <b>Título de la Tarea</b>",
    "task_detail.title_placeholder": "Ej. Escribir informe mensual...",
    "task_detail.description_label": "📄 <b>Descripción / Notas</b>",
    "task_detail.description_placeholder": "Añade detalles sobre esta tarea...",
    "task_detail.timer_label": "⏱ <b>Temporizador:</b>",
    "task_detail.timer_start_btn": "▶ Iniciar",
    "task_detail.timer_restart_btn": "↺ Reiniciar",
    "task_detail.timer_clear_btn": "✕ Detener",
    "task_detail.timer_clear_tooltip": "Detiene el temporizador y quita la insignia de la tarjeta",
    "task_detail.timer_elapsed": "En marcha desde hace {elapsed}",
    "task_detail.due_label": "📅 <b>Vencimiento:</b>",
    "task_detail.due_enable_checkbox": "Habilitar",
    "task_detail.due_time_checkbox": "Hora",
    "task_detail.due_time_tooltip": "Añadir hora al vencimiento (crea un aviso en el calendario)",
    "task_detail.recurrence_none": "Sin repetir",
    "task_detail.recurrence_daily": "Diaria",
    "task_detail.recurrence_weekly": "Semanal",
    "task_detail.recurrence_monthly": "Mensual",
    "task_detail.recurrence_tooltip": "Repetir la tarea: al pasar la fecha, se adelanta sola",
    "task_detail.tags_label": "🏷️ <b>Etiquetas:</b>",
    "task_detail.assign_tag_btn": "➕ Asignar Etiqueta",
    "task_detail.manage_tags_btn": "⚙ Gestionar",
    "task_detail.manage_tags_tooltip": "Definir etiquetas permanentes y sus valores",
    "task_detail.priority_label": "🚩 <b>Prioridad:</b>",
    "task_detail.priority_tooltip": "Prioridad rápida de la tarea (aparece como etiqueta en el tablero)",
    "task_detail.priority_category_name": "Prioridad",
    "task_detail.priority_none": "— Sin prioridad —",
    "task_detail.priority_low": "Baja",
    "task_detail.priority_medium": "Media",
    "task_detail.priority_high": "Alta",
    "task_detail.linked_board_label": "🔗 <b>Tablero vinculado:</b>",
    "task_detail.linked_board_tooltip": "Enlaza esta tarea con otro tablero (aparece como pastilla clicable en la tarjeta)",
    "task_detail.linked_board_none": "— Sin vincular —",
    "task_detail.links_label": "🔗 <b>Enlaces / adjuntos:</b>",
    "task_detail.link_url_placeholder": "URL o ruta…",
    "task_detail.link_label_placeholder": "Nombre (opcional)",
    "task_detail.add_link_tooltip": "Añadir enlace",
    "task_detail.browse_file_tooltip": "Buscar un archivo local del PC para adjuntar",
    "task_detail.browse_file_title": "Seleccionar archivo para adjuntar",
    "task_detail.link_missing_tooltip": "⚠ Archivo no encontrado: {path}",
    "task_detail.link_open_failed_title": "No se pudo abrir",
    "task_detail.link_open_failed_msg": (
        "No se pudo abrir el enlace o el archivo adjunto. Puede que se haya movido o eliminado."
    ),
    "task_detail.delete_task_btn": "🗑️ Eliminar",
    "task_detail.save_btn": "💾 Guardar Cambios",
    "task_detail.close_btn": "❌ Cerrar",
    "task_detail.log_header": "📖 <b>Log / Diario Personal de la Tarea</b>",
    "task_detail.log_input_placeholder": "Escribe una nota o actualización en el diario... (Ctrl+Enter para guardar)",
    "task_detail.add_log_btn": "✍️ Añadir al Diario",
    "task_detail.load_error_title": "Error",
    "task_detail.load_error_body": "No se pudo cargar la tarea.",
    "task_detail.no_tags_hint": "Sin etiquetas. Pulsa «Asignar Etiqueta».",
    "task_detail.tag_pill_tooltip": "Clic para cambiar el valor",
    "task_detail.tag_pill_remove_tooltip": "Quitar de la tarea",
    "task_detail.warn_title": "Atención",
    "task_detail.warn_empty_title": "El título de la tarea no puede estar vacío.",
    "task_detail.delete_task_title": "Confirmar Eliminación",
    "task_detail.delete_task_body": (
        "¿Estás seguro de que deseas eliminar esta tarea de forma permanente? No se podrá recuperar."
    ),
    "task_detail.no_links_hint": "Sin enlaces.",
    "task_detail.delete_link_tooltip": "Eliminar enlace",
    "task_detail.delete_log_title": "Eliminar Entrada",
    "task_detail.delete_log_body": "¿Estás seguro de que deseas borrar esta entrada del diario?",
}


def t(key, **kwargs):
    """Devuelve la cadena asociada a `key`, interpolando **kwargs si se pasan."""
    text = STRINGS[key]
    return text.format(**kwargs) if kwargs else text
