# Graph Report - .  (2026-08-13)

## Corpus Check
- 83 files · ~96,116 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1137 nodes · 2029 edges · 106 communities (66 shown, 40 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 102 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Calendar View Widgets
- Markdown Editor List Formatting
- Tag Manager Dialog
- Detail Dialog Package Modules
- Image Preview & Settings Dialog
- iCalendar (.ics) Export
- Task Detail Save Logic
- Task Detail Dialog & Links
- Forensic Bug-Hunt Backlog Items
- Task Data Access (tasks.py)
- Board Data Access (boards.py)
- Tag Pill Widgets
- Column Widget Management
- Tag Catalog Data Access
- Board/Task Exporter
- Task Card Styling
- Column Data Access (columns.py)
- Diary Log Entry Widget
- Export Menu & Search Shortcuts
- Board View Sidebar Toggle & Timer Badges
- Image Preview Dialog
- Hover-Expand Regression Tests
- Graphify Extraction Spec Rules
- Main Window Controller
- Flow Layout
- Sidebar & Notifications Popup
- Elapsed Time Formatting
- Column Widget Drag & Drop
- v0.6.0 Feature Set
- CI Workflow (ruff + pytest)
- DB Init & Scheduling Queries
- Collapsed Column UI
- Database Backups
- MainWindow Test Fixtures
- Column Edit Dialog
- Board Edit Dialog
- Board Columns Drag Area
- App Startup & Onboarding
- Timer Threshold Tests
- Drag-and-Drop Logic Tests
- Early Bug-Fix Batch (P1)
- Hover-Expand Drag Bug Fix
- Global Search Feature
- Ctrl+Z & Test-Suite Crash Fixes
- Board/Column Copy Operations
- Per-Board ICS Sync Paths
- Sidebar Board Button
- Board List & Archive Actions
- Quick-Add Task Shortcuts
- Hover-Expand Column Rebuild
- Pytest Fixtures (qapp/db_path)
- Draggable Column Title
- Keyboard Shortcuts Wave
- Board Selection Dialog
- Calendar Task Sync
- Task Jump Navigation Handlers
- Sidebar Utility Bar
- Undo/Redo Manager
- Task List Area Drag Events
- Task Links Data Access
- Due-Date Notifications Bell
- Sidebar Board Selection
- v0.9.2 Image/Icon Fixes
- App Settings Data Access
- Calendar Drag-to-Reschedule
- Graphify Multi-Repo Merge
- Theme Apply & Settings Open
- Daily Due-Today Toast
- Board Delete & Undo
- Subtask Progress Badge
- Local File Attachments Feature
- Release Notes Extraction Script
- Calendar Chip & Day Cell
- Drag-End Hover Collapse Signal
- Column Hover-Expand Signal/Timer
- Column/Board Copy Data-Loss Fix
- Export N+1 Query Fix
- Ctrl+Z Deleted-Tag Crash Fix
- TaskDetailDialog Leak Fix
- Image Preview Resolution Fix
- CI Unparented QTimer Fix
- restore_task Link Ordering Fix
- Graphify Extraction Rules
- Graphify Path/Explain Commands
- Graphify Feedback Loop
- Graphify Detect & Extract Steps
- Global Search Dialog Open
- create_log Atomicity Test
- DB_NAME Late Resolution Test
- restore_task FK Guard Test
- restore_column FK Guard Test
- Link Order Restore Test
- create_log Atomicity Fix
- Dead setStyleSheet Removal
- Shortcuts Help Text Fix
- Timer Threshold N+1 Fix
- Shortcuts Dialog Signal
- add_column Guard Fix
- Ekin Kanban Backlog Doc
- Graphify Token Benchmark
- Graphify Video Transcription
- Ekin App Icon
- Ekin Kanban Project Root

## God Nodes (most connected - your core abstractions)
1. `t()` - 116 edges
2. `get_connection()` - 80 edges
3. `BoardViewWidget` - 63 edges
4. `TaskDetailDialog` - 61 edges
5. `MainWindow` - 39 edges
6. `SidebarWidget` - 34 edges
7. `MarkdownTextEdit` - 28 edges
8. `ColumnWidget` - 27 edges
9. `CalendarViewWidget` - 24 edges
10. `TagManagerDialog` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `BoardColumnsArea` --uses--> `UndoAction`  [INFERRED]
  board_view.py → undo.py
- `BoardColumnsArea` --uses--> `ColumnWidget`  [INFERRED]
  board_view.py → widgets.py
- `BoardColumnsArea` --uses--> `TaskCard`  [INFERRED]
  board_view.py → widgets.py
- `ColumnEditDialog` --uses--> `UndoAction`  [INFERRED]
  board_view.py → undo.py

## Import Cycles
- 3-file cycle: `database/__init__.py -> database/snapshots.py -> database/boards.py -> database/__init__.py`
- 3-file cycle: `database/__init__.py -> database/snapshots.py -> database/columns.py -> database/__init__.py`

## Hyperedges (group relationships)
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]

## Communities (106 total, 40 thin omitted)

### Community 0 - "Calendar View Widgets"
Cohesion: 0.05
Nodes (26): CalendarChip, CalendarSettingsDialog, CalendarViewWidget, DayCell, _group_by_day(), QDialog, QFrame, QWidget (+18 more)

### Community 2 - "Markdown Editor List Formatting"
Cohesion: 0.05
Nodes (25): Sustituye el contenido por un editor en línea con Guardar/Cancelar., MarkdownTextEdit, QWidget, QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Al pegar: las imágenes se insertan como imagen; una tabla (de Excel/Sheets/Word…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor, con el estilo del…, Codifica un QImage como data URI PNG en base64. (+17 more)

### Community 3 - "Tag Manager Dialog"
Cohesion: 0.09
Nodes (17): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog, QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog, QLabel (+9 more)

### Community 4 - "Detail Dialog Package Modules"
Cohesion: 0.12
Nodes (17): color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas)., Diálogo de búsqueda global de tareas. Filtra por texto (título/descripción),…, Pantalla de Ajustes de la aplicación: tema, notificaciones y persistencia.…, Diálogo "Atajos de teclado" (Ctrl+/): referencia estática de todos los atajos…, Cadenas de la interfaz, centralizadas para facilitar una futura traducción.…, build_qss(), color_swatch_css() (+9 more)

### Community 5 - "Image Preview & Settings Dialog"
Cohesion: 0.10
Nodes (31): pixmap_from_data_uri(), Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, _is_local_link(), True a menos que la cadena empiece por un esquema web reconocido (case-…, QDialog, SettingsDialog, _card_with_timer(), _collapsed_column_widget() (+23 more)

### Community 6 - "iCalendar (.ics) Export"
Cohesion: 0.12
Nodes (27): build_ics(), _escape(), export_ics(), _fold_line(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano razonable. (+19 more)

### Community 7 - "Task Detail Save Logic"
Cohesion: 0.09
Nodes (15): Habilita/inhabilita fecha y hora según los checks., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Devuelve el id de la etiqueta permanente «Prioridad», asegurando que existan…, Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Guarda el título, descripción, etiquetas y fecha de vencimiento., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la… (+7 more)

### Community 8 - "Task Detail Dialog & Links"
Cohesion: 0.13
Nodes (19): QDialog, Ancho máximo (px) para imágenes pegadas en el chat: el del histórico (más…, TaskDetailDialog, _make_task(), Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/…, El nuevo self.finished.connect(self.deleteLater) no debe romper el patrón ya…, test_add_link_with_local_path_renders_with_attachment_icon(), test_add_link_with_web_url_renders_with_link_icon() (+11 more)

### Community 9 - "Forensic Bug-Hunt Backlog Items"
Cohesion: 0.09
Nodes (25): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+17 more)

### Community 10 - "Task Data Access (tasks.py)"
Cohesion: 0.09
Nodes (24): get_task_tags(), advance_overdue_recurring(), advance_recurrence(), create_task(), delete_task(), get_task(), next_occurrence(), Fija la hora de vencimiento ('HH:MM') de una tarea, o None para dejarla de día… (+16 more)

### Community 11 - "Board Data Access (boards.py)"
Cohesion: 0.15
Nodes (21): create_board(), delete_board(), get_board(), get_boards(), Devuelve los tableros. Por defecto excluye los archivados., Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra…, set_board_archived(), update_board() (+13 more)

### Community 12 - "Tag Pill Widgets"
Cohesion: 0.10
Nodes (11): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza., Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno»… (+3 more)

### Community 13 - "Column Widget Management"
Cohesion: 0.11
Nodes (9): QFrame, Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Limpia todos los widgets del layout de columnas., Confirma y borra una columna., Pliega o despliega una columna (persiste el estado) y recarga el tablero., Reordena las columnas del tablero actual tras arrastrar una por su título. (+1 more)

### Community 14 - "Tag Catalog Data Access"
Cohesion: 0.10
Nodes (19): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_values(), Crea una etiqueta permanente (categoría). Si ya existe (sin distinguir… (+11 more)

### Community 15 - "Board/Task Exporter"
Cohesion: 0.16
Nodes (17): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Convierte HTML (descripción/nota) en texto plano razonable para exportar., Estructura anidada de todo el contenido: tableros -> columnas -> tareas (+logs)., Volcado completo (tableros, columnas, tareas, etiquetas y diario) como JSON., CSV plano de todas las tareas (una fila por tarea). (+9 more)

### Community 16 - "Task Card Styling"
Cohesion: 0.15
Nodes (10): hex_to_rgb(), Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b)., QFrame, QWidget, Aplica dinámicamente el estilo a la tarjeta basándose en el color de fondo del…, Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Umbral (en horas) a partir del cual la insignia del temporizador se resalta en…, Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo… (+2 more)

### Community 17 - "Column Data Access (columns.py)"
Cohesion: 0.18
Nodes (16): create_column(), delete_column(), Pliega (collapsed=1) o despliega (0) una columna del tablero., Actualiza las posiciones de múltiples columnas. column_positions debe ser una…, set_column_collapsed(), update_column(), update_column_positions(), get_connection() (+8 more)

### Community 18 - "Diary Log Entry Widget"
Cohesion: 0.12
Nodes (11): LogEntryWidget, QFrame, Una entrada del diario/chat, con botones (pintados) de editar y eliminar y…, Limpia y vuelve a cargar todos los logs/entradas del diario., Guarda la edición de un comentario (o cancela si new_html es None) y recarga., Crea una nueva entrada de diario con el texto del input., Mueve la barra de desplazamiento del diario hasta abajo., Regresión: setTextInteractionFlags(Qt.TextSelectableByMouse) A SOLAS anulaba… (+3 more)

### Community 19 - "Export Menu & Search Shortcuts"
Cohesion: 0.15
Nodes (14): Menú para exportar todos los tableros a JSON / CSV / informe Markdown., SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir…, El fix del guard no debe bloquear el caso normal: con un tablero real…, test_add_column_shortcut_noop_when_no_board_selected() (+6 more)

### Community 20 - "Board View Sidebar Toggle & Timer Badges"
Cohesion: 0.25
Nodes (13): BoardViewWidget, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)., _make_board(), test_add_task_sets_last_active_column(), test_column_background_click_sets_last_active_column(), test_column_widget_mouse_press_emits_column_activated(), test_quick_add_task_falls_back_to_first_column_when_nothing_active() (+5 more)

### Community 21 - "Image Preview Dialog"
Cohesion: 0.12
Nodes (12): ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Maneja los enlaces clicados dentro de una entrada ya enviada. Hoy el único tipo…, Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog… (+4 more)

### Community 22 - "Hover-Expand Regression Tests"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 23 - "Graphify Extraction Spec Rules"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 24 - "Main Window Controller"
Cohesion: 0.15
Nodes (6): MainWindow, Manejador si el tablero actual cambió en el sidebar., Abre la ventana de referencia de atajos de teclado (Ctrl+/)., Muestra u oculta la barra lateral., Verifica de forma silenciosa si hay actualizaciones en el repo de GitHub., QMainWindow

### Community 25 - "Flow Layout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 26 - "Sidebar & Notifications Popup"
Cohesion: 0.18
Nodes (9): NotificationsPopup, QDialog, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, _swatch_icon(), test_notifications_popup_empty(), test_notifications_popup_with_tasks(), Pila simple de deshacer/rehacer para acciones destructivas (borrar… (+1 more)

### Community 27 - "Elapsed Time Formatting"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 28 - "Column Widget Drag & Drop"
Cohesion: 0.16
Nodes (6): ColumnWidget, Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Establece el diseño de la columna (borde y fondo) basado en su color., Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Elimina todos los widgets de tarea de la columna., Añade una tarjeta de tarea a la columna (no-op si está plegada).

### Community 29 - "v0.6.0 Feature Set"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 30 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 31 - "DB Init & Scheduling Queries"
Cohesion: 0.19
Nodes (10): init_db(), Crea las tablas necesarias si no existen., get_scheduled_tasks(), get_task_board_id(), Devuelve el board_id al que pertenece una tarea (o None si no existe)., Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.…, Busca tareas en todos los tableros (o en uno) con filtros opcionales. - text:…, search_tasks() (+2 more)

### Community 32 - "Collapsed Column UI"
Cohesion: 0.18
Nodes (3): Etiqueta con el texto girado 90° (nombre de una columna plegada)., Columna plegada: tira estrecha con botón de desplegar, contador y nombre…, VerticalLabel

### Community 33 - "Database Backups"
Cohesion: 0.24
Nodes (10): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., Pruebas de las copias de seguridad automáticas de la base de datos., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder() (+2 more)

### Community 34 - "MainWindow Test Fixtures"
Cohesion: 0.30
Nodes (11): _close_window(), _make_task_on_board(), _make_window(), Pruebas headless para MainWindow (main.py): comportamientos que solo existen a…, Construye una MainWindow apta para tests: __init__ agenda dos QTimer.singleShot…, Cierra y destruye la ventana de verdad (deleteLater + procesar el evento…, Regresión: editar una tarea desde el Calendario dejaba la tarjeta del tablero…, La tarea editada pertenece a un tablero distinto del que la sidebar tiene… (+3 more)

### Community 35 - "Column Edit Dialog"
Cohesion: 0.22
Nodes (4): ColumnEditDialog, Abre el diálogo para crear una columna., Abre el diálogo para editar nombre y color de una columna., Diálogo para crear o editar una columna (nombre y color).

### Community 36 - "Board Edit Dialog"
Cohesion: 0.22
Nodes (4): BoardEditDialog, Diálogo personalizado para crear o editar un tablero (nombre y color de fondo)., Abre el diálogo para editar el nombre y color del tablero activo., Abre el diálogo para copiar el tablero activo con un nuevo nombre.

### Community 37 - "Board Columns Drag Area"
Cohesion: 0.27
Nodes (3): BoardColumnsArea, QWidget, Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…

### Community 38 - "App Startup & Onboarding"
Cohesion: 0.22
Nodes (5): app_icon(), main(), Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo.

### Community 39 - "Timer Threshold Tests"
Cohesion: 0.38
Nodes (9): _card_for(), _make_board_with_task(), Antes del fix, _build_column_widget releía el ajuste una vez POR COLUMNA…, test_build_column_widget_applies_configured_threshold(), test_build_column_widget_defaults_threshold_when_unset(), test_load_board_reads_timer_alert_hours_once_regardless_of_column_count(), test_refresh_timer_badges_noop_on_board_with_no_timers(), test_refresh_timer_badges_noop_on_welcome_screen() (+1 more)

### Community 40 - "Drag-and-Drop Logic Tests"
Cohesion: 0.29
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una tarjeta soltada en `drop_y`. `cards_geom` es una…

### Community 41 - "Early Bug-Fix Batch (P1)"
Cohesion: 0.22
Nodes (8): backup_database() Function, backups.py Module, db_path Normalization (P1), Dead #TaskCardDueDate Object Name, iCalendar Line-Folding Off-by-One, Overdue Tasks in Notification Bell, Release v0.4.0, Subscribe-in-Google Helper

### Community 42 - "Hover-Expand Drag Bug Fix"
Cohesion: 0.25
Nodes (9): compute_drop_index() Function, Same-Column Drag Off-by-One Bug, handle_hover_expand_requested() Method, BoardViewWidget._hover_expanded_column_id, Hover-to-Expand Collapsed Column, QDrag.exec() Return as Drag-End Checkpoint, _build_column_widget() Helper, load_board() Mid-Drag Crash Bug (+1 more)

### Community 43 - "Global Search Feature"
Cohesion: 0.22
Nodes (9): Ctrl+F Search Shortcut, Global Search & Filter Feature, Immediate-Persistence Pattern, on_notification_task Handler Reuse, Release v0.5.0, SearchDialog Class, search_tasks() Function, Subtask Checklist UI (Task Detail Dialog) (+1 more)

### Community 44 - "Ctrl+Z & Test-Suite Crash Fixes"
Cohesion: 0.22
Nodes (9): QMimeData GC Lifetime Bug (Test-Only), tests/test_hover_expand.py, Ctrl+Z FK IntegrityError Crash Fix (Fix 2), Git-Stash Empirical Regression Verification, STATUS_HEAP_CORRUPTION Test-Suite Crash, Stale Board Card on Calendar Edit Fix (Fix 4), conftest.py QApplication Teardown Fix, restore_task() Function (+1 more)

### Community 45 - "Board/Column Copy Operations"
Cohesion: 0.28
Nodes (8): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), move_column_to_board(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…, Mueve una columna a otro tablero y la coloca al final de su lista de columnas.

### Community 46 - "Per-Board ICS Sync Paths"
Cohesion: 0.22
Nodes (8): delete_board_ics_sync_path(), get_all_board_ics_sync_paths(), get_board_ics_sync_path(), Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene., Crea o actualiza la ruta de auto-sync de un tablero., Desactiva la sincronización automática de un tablero., Devuelve {board_id: path} para todos los tableros con auto-sync configurado., set_board_ics_sync_path()

### Community 48 - "Board List & Archive Actions"
Cohesion: 0.22
Nodes (4): Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Archiva/desarchiva un tablero y recarga la lista., Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero con nombre y color.

### Community 49 - "Quick-Add Task Shortcuts"
Cohesion: 0.21
Nodes (4): Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…, Atajo Ctrl+N: añade una tarea a la última columna con la que se ha interactuado…, Crea una tarea solicitando el título rápidamente., Maneja la lógica de recolocación de tareas tras arrastrarlas.

### Community 50 - "Hover-Expand Column Rebuild"
Cohesion: 0.29
Nodes (4): Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de…

### Community 51 - "Pytest Fixtures (qapp/db_path)"
Cohesion: 0.32
Nodes (7): fixture, _close_top_level_widgets_after_each_test(), db_path(), qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 52 - "Draggable Column Title"
Cohesion: 0.25
Nodes (3): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…

### Community 53 - "Keyboard Shortcuts Wave"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 54 - "Board Selection Dialog"
Cohesion: 0.29
Nodes (4): BoardSelectionDialog, QDialog, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Crea una copia de la columna en otro tablero seleccionado.

### Community 56 - "Task Jump Navigation Handlers"
Cohesion: 0.29
Nodes (3): Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero.

### Community 60 - "Task Links Data Access"
Cohesion: 0.33
Nodes (5): add_task_link(), delete_task_link(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en una consulta (evita N+1 al pintar el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id.

### Community 61 - "Due-Date Notifications Bell"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

### Community 62 - "Sidebar Board Selection"
Cohesion: 0.33
Nodes (3): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…

### Community 63 - "v0.9.2 Image/Icon Fixes"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 64 - "App Settings Data Access"
Cohesion: 0.40
Nodes (4): get_setting(), Crea o actualiza un ajuste de la aplicación., Devuelve el valor de un ajuste, o `default` si no está definido., set_setting()

### Community 65 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 66 - "Graphify Multi-Repo Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 70 - "Subtask Progress Badge"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 71 - "Local File Attachments Feature"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

## Knowledge Gaps
- **92 isolated node(s):** `ekin-kanban`, `Step 0: GitHub Clone & Multi-Path Merge`, `Step 2: Detect Files`, `Step 2.5: Video/Audio Transcription`, `Step 3: Extract Entities & Relationships` (+87 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `Task Detail Save Logic` to `Calendar View Widgets`, `Markdown Editor List Formatting`, `Tag Manager Dialog`, `Detail Dialog Package Modules`, `Image Preview & Settings Dialog`, `Task Detail Dialog & Links`, `Tag Pill Widgets`, `Column Widget Management`, `Task Card Styling`, `Diary Log Entry Widget`, `Export Menu & Search Shortcuts`, `Image Preview Dialog`, `Main Window Controller`, `Sidebar & Notifications Popup`, `Column Widget Drag & Drop`, `Collapsed Column UI`, `Column Edit Dialog`, `Board Edit Dialog`, `Board Columns Drag Area`, `App Startup & Onboarding`, `Sidebar Board Button`, `Board List & Archive Actions`, `Quick-Add Task Shortcuts`, `Board Selection Dialog`, `Sidebar Utility Bar`, `Task List Area Drag Events`, `Daily Due-Today Toast`, `Board Delete & Undo`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `Board View Sidebar Toggle & Timer Badges` to `Column Edit Dialog`, `Detail Dialog Package Modules`, `Board Columns Drag Area`, `App Startup & Onboarding`, `Timer Threshold Tests`, `Column Widget Management`, `Task Card Styling`, `Quick-Add Task Shortcuts`, `Hover-Expand Column Rebuild`, `Export Menu & Search Shortcuts`, `Board Selection Dialog`, `Hover-Expand Regression Tests`, `Main Window Controller`, `Sidebar & Notifications Popup`, `Column Widget Drag & Drop`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `TaskDetailDialog` connect `Task Detail Dialog & Links` to `Markdown Editor List Formatting`, `Tag Manager Dialog`, `Detail Dialog Package Modules`, `Image Preview & Settings Dialog`, `Task Detail Save Logic`, `Tag Pill Widgets`, `Column Widget Management`, `Diary Log Entry Widget`, `Task Jump Navigation Handlers`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `BoardViewWidget` (e.g. with `UndoAction` and `ColumnWidget`) actually correct?**
  _`BoardViewWidget` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `TaskDetailDialog` (e.g. with `LogEntryWidget` and `MarkdownTextEdit`) actually correct?**
  _`TaskDetailDialog` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MainWindow` (e.g. with `BoardViewWidget` and `CalendarViewWidget`) actually correct?**
  _`MainWindow` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ekin-kanban`, `Step 0: GitHub Clone & Multi-Path Merge`, `Step 2: Detect Files` to the rest of the system?**
  _92 weakly-connected nodes found - possible documentation gaps or missing edges._