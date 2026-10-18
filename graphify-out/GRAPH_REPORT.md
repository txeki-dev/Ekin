# Graph Report - Ekin  (2026-10-18)

## Corpus Check
- 160 files · ~216,566 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3065 nodes · 5663 edges · 228 communities (166 shown, 62 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 247 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `12cdb011`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_local_dir.py
- test_main_window.py
- test_ics_export.py
- MyWorkWidget
- _collapsed_column_widget
- test_board_sync.py
- MarkdownTextEdit
- tasks.py
- logs.py
- DashboardWidget
- DiaryViewerDialog
- test_ux_enhancements.py
- BoardSyncController
- TagManagerDialog
- SettingsDialog
- prompt_packs.py
- TagPickerDialog
- CommandPalette
- LogEntryWidget
- /graphify Pipeline
- sync_board_with_file
- ._rebuild_single_column
- TaskDetailDialog
- .reload_boards
- get_task_tags_bulk
- RichTextToolbar
- strings.py
- BoardSyncUiMixin
- CalendarViewWidget
- tags.py
- QPixmap
- .show_command_palette
- ColorCirclesPicker
- MainWindow
- templates.py
- format_code_block_html
- lucide_icon
- get_connection
- test_mcp.py
- logging_setup.py
- DraggableColumnTitle
- CalendarSettingsDialog
- .contextMenuEvent
- SearchDialog
- markdown_to_qt_html
- test_prompt_clipboard.py
- Any
- McpManager
- .load_task_data
- sync.py
- summarize_diary_offline
- PromptClipboardDialog
- test_templates.py
- snapshots.py
- BulkAddTaskDialog
- markdown_edit.py
- test_hover_expand.py
- test_batch_drag_drop.py
- Part B: Semantic Extraction (Subagents)
- InteractiveTourBanner
- FlowLayout
- test_reminders.py
- format_elapsed_time
- TemplateCardWidget
- backup_database
- Release v0.6.0
- 2. Implementation Tasks
- export_dialog.py
- CI Workflow (ruff + pytest)
- test_start_working.py
- .__init__
- BoardMcpUiMixin
- BoardButton
- LocalAiCircuitBreaker
- test_incremental_rendering.py
- quota_popup.py
- test_mcp_live_refresh.py
- .__init__
- privacy_shield.py
- local_ai.py
- BoardViewWidget
- t
- test_widgets_headless.py
- test_column_roles.py
- BoardEditDialog
- .render_tags
- BoardConfigDialog
- ColumnWidget
- TaskCard
- test_timer_board_view.py
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- TECHNICAL DESIGN DOCUMENT
- authenticate_and_get_board
- copy_board
- connection.py
- start_working.py
- .insertFromMimeData
- create_premerge_backup
- .load_board
- QuotaPopup
- _board_sync_lock
- connect_shared_board_from_file
- CreateBoardDialog
- task_mixins.py
- TaskListArea
- BoardSelectionMixin
- .mouseReleaseEvent
- create_getting_started_board
- pixmap_from_data_uri
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- .sync_ics
- test_release_notes.py
- ._handle_sync_finished
- format_sync_summary
- .notify_due_today
- bump_version.py
- test_wip_limit.py
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- CLAUDE.md
- test_cli_quota.py
- 2. Implementation Tasks
- compute_drop_index
- build_qss
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- DayCell
- .__init__
- Calendar Drag-to-Reschedule
- Cross-Repo Graph Merge
- test_concurrent_edit.py
- test_unlink_board_sync
- test_last_active_column.py
- LandingTourDialog
- .handle_task_drop
- get_subtasks_progress_bulk() Function
- v0.9.1: Local File Attachments on Task Links
- ensure_mcp_registered
- extract_release_notes.py
- _ClickOutsideFilter
- CalendarChip Class
- TaskCard.drag_ended Signal
- ColumnWidget.hover_expand_requested Signal
- Column/Board Copy Data-Loss Fix (Fix 5)
- Export N+1 Query Fix (Fix 9)
- Backlog Item: Ctrl+Z Crash from Deleted Tag During Undo
- Backlog Item: TaskDetailDialog Leaked Forever
- Backlog Step 20: Image Preview Resolution Fix
- Backlog Item: CI Crash Root Cause (Unparented QTimer)
- Backlog Item: restore_task() Loses task_links Ordering
- Hyperedges Rule
- /graphify explain Command
- save-result Feedback Loop
- Step 2: Detect Files
- test_snapshot_and_restore_preserves_uuids
- test_create_tasks_batch
- test_copy_operations_generate_uuids
- test_save_task_full_atomic_update
- test_snapshot_and_restore_board_single_connection
- test_bulk_queries_chunking_handles_large_task_lists
- test_create_log_has_no_intermediate_commit_call
- test_db_name_is_resolved_at_call_time
- test_restore_task_returns_none_if_column_was_deleted_in_the_meantime
- test_restore_column_returns_none_if_board_was_deleted_in_the_meantime
- test_snapshot_and_restore_task_preserves_link_order
- BoardSyncWorker
- create_log() Atomicity Fix (Fix 6)
- Dead app.setStyleSheet() Removal (Fix 8)
- Stale Shortcuts Help Text Fix (Fix 3)
- timer_alert_hours N+1 Read Fix (Fix 7)
- open_shortcuts_requested Signal
- add_column() board_id==-1 Guard Fix
- backlog.md — Ekin Kanban Backlog
- Token Reduction Benchmark
- transcribe_all() Video/Audio Transcription
- TableInsertDialog
- Ekin App Icon
- ekin-kanban
- .reload_logs
- ImagePreviewDialog
- mcp_server.py
- .apply_theme
- test_extract_template_preserves_ai_system_prompt
- ._build_language_segment
- _column_with_cards
- WeeklyDigestDialog
- ._update_local_dir_buttons
- hex_to_rgb
- _editor_with_all_selected
- SidebarWidget
- set_language
- test_local_ai_rdi.py
- McpHttpServer
- TaskTimerMixin
- ._open_logs_folder
- Any
- QPushButton
- mcp_board
- .show_shortcuts
- color_swatch_css
- NotificationsPopup
- _shown_expanded_column
- test_sync_corrupted_json_returns_error_safely
- ._maybe_show_weekly_digest
- test_database_sync_helpers_lifecycle
- test_connection_pooling_and_lifecycle
- test_fts5_search_and_triggers
- test_fts5_search_fallback_on_error
- test_update_task_positions_bumps_version_only_on_column_change
- .show_my_work_view
- QFrame
- .check_for_updates
- QWidget
- test_get_synced_boards_lifecycle
- QFrame
- QDialog
- claude_statusline.py
- conftest.py
- sync_test_db
- QLabel

## God Nodes (most connected - your core abstractions)
1. `t()` - 260 edges
2. `BoardViewWidget` - 125 edges
3. `TaskDetailDialog` - 110 edges
4. `get_connection()` - 108 edges
5. `MarkdownTextEdit` - 94 edges
6. `MainWindow` - 55 edges
7. `SidebarWidget` - 49 edges
8. `lucide_icon()` - 45 edges
9. `TaskCard` - 40 edges
10. `McpProtocolHandler` - 39 edges

## Surprising Connections (you probably didn't know these)
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `BoardViewWidget` --uses--> `DiaryViewerDialog`  [INFERRED]
  board_view.py → diary_viewer_dialog.py
- `InstallerDownloadThread` --uses--> `BoardViewWidget`  [INFERRED]
  main.py → board_view.py
- `MainWindow` --uses--> `BoardViewWidget`  [INFERRED]
  main.py → board_view.py
- `ReleaseCheckThread` --uses--> `BoardViewWidget`  [INFERRED]
  main.py → board_view.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (228 total, 62 thin omitted)

### Community 1 - "test_local_dir.py"
Cohesion: 0.07
Nodes (45): list_repo_files(), Archivos del directorio local (repo) asociado a un tablero, para ofrecerlos en…, Rutas relativas (con «/») de los archivos de `root`, como mucho `limit`., boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas. (+37 more)

### Community 2 - "test_main_window.py"
Cohesion: 0.06
Nodes (54): installer_sha256_from_notes(), InstallerDownloadThread, parse_version_tuple(), QThread, Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, SHA-256 del instalador según la línea «SHA-256: <hash>» que el workflow de…, Muestra confirmación al usuario y descarga el instalador si acepta., ReleaseCheckThread (+46 more)

### Community 3 - "test_ics_export.py"
Cohesion: 0.11
Nodes (28): build_ics(), _escape(), export_ics(), _fold_line(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar. (+20 more)

### Community 4 - "MyWorkWidget"
Cohesion: 0.16
Nodes (17): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon() (+9 more)

### Community 5 - "_collapsed_column_widget"
Cohesion: 0.36
Nodes (8): _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _task_drag_mime(), test_hover_timeout_emits_signal_only_while_collapsed(), test_hover_timer_starts_on_drag_enter(), test_hover_timer_stops_on_drag_leave(), test_hover_timer_stops_on_drop_before_timeout()

### Community 6 - "test_board_sync.py"
Cohesion: 0.05
Nodes (50): _all_titles(), _edit_remote_task(), Verifica que cambios en el archivo remoto sin cambios locales se importan…, Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que si local y remoto añaden tareas diferentes simultáneamente, la…, Verifica que se genera una instantánea de respaldo en backups/ al detectar…, Verifica que si un colaborador elimina una tarea en OneDrive, no se resucita al…, Verifica que si la copia de seguridad pre-fusión falla (ej. disco lleno), la… (+42 more)

### Community 7 - "MarkdownTextEdit"
Cohesion: 0.03
Nodes (50): MarkdownTextEdit, QTextEdit, Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Elige el símbolo de viñeta según el nivel de anidamiento (las listas numeradas…, Aumenta (Tab) o reduce (Shift+Tab) el nivel de anidamiento de la viñeta actual., Inserta una línea separadora horizontal en la posición del cursor., Abre el diálogo para insertar o editar un enlace web. (+42 more)

### Community 8 - "tasks.py"
Cohesion: 0.07
Nodes (34): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), advance_overdue_recurring() (+26 more)

### Community 9 - "logs.py"
Cohesion: 0.25
Nodes (7): create_log(), delete_log(), get_logs(), get_logs_bulk(), {task_id: [entradas de diario]} para varias tareas en lotes paginados (evita el…, Edita el contenido (HTML) de una entrada del diario y refresca el updated_at de…, update_log()

### Community 10 - "DashboardWidget"
Cohesion: 0.10
Nodes (20): _esc(), export_report_pdf(), gather_stats(), Métricas de tableros para el panel de Analíticas y la exportación a PDF.…, Recopila métricas transversales (todos los tableros activos)., Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)., Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)., render_report_html() (+12 more)

### Community 11 - "DiaryViewerDialog"
Cohesion: 0.11
Nodes (24): Abre los diarios de desarrollo y demás .md / .txt del directorio local., DiaryViewerDialog, doc_files(), has_doc_files(), _iter_doc_files(), Visor de solo lectura de los diarios de desarrollo (`diary.md`,…, Índice de la pestaña de `rel_path`, que se crea (y se lee) si aún no estaba…, Un submenú por carpeta de primer nivel con sus documentos (ruta dentro de la… (+16 more)

### Community 12 - "test_ux_enhancements.py"
Cohesion: 0.09
Nodes (23): clear_fit_html_cache(), Limpia la caché en memoria de transformaciones de imágenes y tablas HTML., Pruebas exhaustivas para las 4 mejoras de UX: 1. Tablas interactivas y formato…, Verifica las proporciones, márgenes simétricos, scroll fluido y edición in-…, Verifica inserción inicial de tabla y manipulación mediante acciones de…, Verifica la eliminación total de CSS (<style>) residual de Qt., Verifica que los metadatos se organicen en 4 filas dentro del panel izquierdo,…, Verifica que el editor de descripción/diario y los widgets de log apliquen… (+15 more)

### Community 13 - "BoardSyncController"
Cohesion: 0.09
Nodes (18): BoardSyncController, QObject, Configura el watcher para detectar reactivamente cambios externos., Disparado por el sistema de archivos ante modificaciones externas., Desvincula el tablero actual de su archivo compartido., Espera a que termine cualquier hilo de sincronización en ejecución., Devuelve True si hay una sincronización en segundo plano activa., Controlador de sincronización autónomo para un tablero Kanban. Emite señales de… (+10 more)

### Community 14 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 15 - "SettingsDialog"
Cohesion: 0.12
Nodes (12): QDialog, Pestaña Directorios locales: cada tablero con su carpeta (repo), con Examinar y…, SettingsDialog, Verifica que el botón 'Buscar ahora' en ajustes emita check_updates_requested., Verifica que el botón de Tour Interactivo en Ajustes emita…, test_settings_dialog_check_updates_button_emits_signal(), test_settings_dialog_constructs_with_saved_theme(), test_settings_dialog_interactive_tour_button() (+4 more)

### Community 16 - "prompt_packs.py"
Cohesion: 0.10
Nodes (29): claude_code_server_name(), Nombre del servidor MCP del tablero en el comando `claude mcp add` (p. ej.…, board_variables(), fill_variables(), find_variables(), import_pack(), list_packs(), load_pack() (+21 more)

### Community 17 - "TagPickerDialog"
Cohesion: 0.09
Nodes (18): ensure_priority_category(), Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si…, QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog, color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas). (+10 more)

### Community 18 - "CommandPalette"
Cohesion: 0.14
Nodes (12): CommandPalette, QDialog, _swatch_icon(), Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, Verifica que CommandPalette no tenga WA_DeleteOnClose activo y no sufra…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query() (+4 more)

### Community 19 - "LogEntryWidget"
Cohesion: 0.08
Nodes (21): LogEntryWidget, QFrame, Sustituye el contenido por un editor en línea con Guardar/Cancelar y soporte de…, Una entrada del diario/chat, con botones (pintados) de editar y eliminar y…, Cancela la edición volviendo al estado de lectura de forma instantánea y sin…, Guarda la edición del comentario invocando el callback., Actualiza el contenido renderizado tras guardar sin recrear el widget ni mover…, Limpia los widgets temporales de edición y reactiva la etiqueta de lectura. (+13 more)

### Community 20 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 21 - "sync_board_with_file"
Cohesion: 0.11
Nodes (22): _apply_remote_board_clean(), calculate_file_hash(), _execute_two_way_merge(), _merge_fields(), _merge_task_fields(), _merge_task_sub_entities(), now_utc_iso(), Devuelve la fecha/hora actual en formato ISO 8601 UTC. (+14 more)

### Community 22 - "._rebuild_single_column"
Cohesion: 0.10
Nodes (11): Maneja las acciones interactivas directas asociadas a cada paso del tour., Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de… (+3 more)

### Community 23 - "TaskDetailDialog"
Cohesion: 0.07
Nodes (22): QDialog, Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la…, Ancho máximo (px) para imágenes en las notas (panel izquierdo ancho)., Al pegar un enlace o archivo local en Notas o Diario, se añade automáticamente…, Lo que se ofrece al escribir «@»: los Enlaces / Adjuntos actuales de la tarea…, Borra definitivamente la tarea actual de la base de datos., TaskDetailDialog (+14 more)

### Community 24 - ".reload_boards"
Cohesion: 0.10
Nodes (13): Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo)., Abre el selector de archivo JSON y el diálogo de confirmación de importación., Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero a partir de una plantilla o en…, Abre el diálogo para editar el nombre y color del tablero activo., Abre el diálogo para copiar el tablero activo con un nuevo nombre., Confirma y elimina el tablero activo., Registra deshacer/rehacer del borrado de un tablero (restaurar desde snapshot). (+5 more)

### Community 25 - "get_task_tags_bulk"
Cohesion: 0.18
Nodes (14): get_active_timer_tasks(), get_scheduled_tasks(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.…, Sanea el texto de búsqueda para FTS5 generando términos con comodín de prefijo., Búsqueda de texto completo de alto rendimiento con FTS5 y ordenación por…, Búsqueda tradicional mediante SQL LIKE utilizada cuando no hay texto o como…, Busca tareas en todos los tableros (o en uno) con filtros opcionales. Utiliza… (+6 more)

### Community 26 - "RichTextToolbar"
Cohesion: 0.09
Nodes (14): _color_icon(), QWidget, Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar, apply_text_color aplica el color especificado al texto seleccionado., Verifica que la barra de formato contiene todos los botones requeridos. (+6 more)

### Community 27 - "strings.py"
Cohesion: 0.06
Nodes (34): Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, board_mixins.py - Mixins modulares para BoardViewWidget. Separa la gestión de…, board_sync_controller.py - Controlador de sincronización desacoplado de…, board_sync.py - Motor de sincronización asíncrona y fusión (Merge Engine) de…, Diálogos para la selección, creación y gestión de plantillas de tableros en…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,… (+26 more)

### Community 28 - "BoardSyncUiMixin"
Cohesion: 0.11
Nodes (12): BoardSyncUiMixin, Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para…, Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Gestiona el diálogo de resultado cuando la sincronización es manual., Exporta cambios locales en segundo plano delegando en el controlador. (+4 more)

### Community 29 - "CalendarViewWidget"
Cohesion: 0.09
Nodes (16): CalendarViewWidget, _group_by_day(), Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Devuelve los nombres cortos de los días de la semana según el idioma activo., Devuelve el nombre del mes (1..12) según el idioma activo., Devuelve el nombre del día de la semana (0..6) según el idioma activo., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo. (+8 more)

### Community 30 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 31 - "QPixmap"
Cohesion: 0.33
Nodes (5): _align_icon(), Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, QPixmap, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., _swatch_icon()

### Community 32 - ".show_command_palette"
Cohesion: 0.18
Nodes (5): Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o…, Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Inicia o reanuda el tour interactivo in-situ en el tablero demo '🚀 Primeros…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero.

### Community 33 - "ColorCirclesPicker"
Cohesion: 0.06
Nodes (20): BoardColumnsArea, BoardSelectionDialog, ColumnEditDialog, QDialog, QWidget, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…, Diálogo para crear o editar una columna (nombre y color). (+12 more)

### Community 34 - "MainWindow"
Cohesion: 0.11
Nodes (8): MainWindow, Muestra el tour interactivo in-situ en el primer inicio si no se ha descartado., Manejador si el tablero actual cambió en el sidebar., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Sincroniza inmediatamente el tablero activo con su archivo en la nube., Abre el diálogo para vincular el tablero activo a un nuevo archivo .ekboard., Muestra u oculta la barra lateral., QMainWindow

### Community 35 - "templates.py"
Cohesion: 0.16
Nodes (19): apply_template_to_board(), BoardTemplate, ColumnTemplate, export_board_to_template(), get_builtin_templates(), get_custom_templates(), get_templates_dir(), Any (+11 more)

### Community 36 - "format_code_block_html"
Cohesion: 0.20
Nodes (9): format_code_block_html(), _get_warm_pygments_style(), Abre el diálogo para insertar un bloque de código formateado., Inserta un bloque de código formateado con resaltado de sintaxis., Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting() (+1 more)

### Community 37 - "lucide_icon"
Cohesion: 0.14
Nodes (10): lucide_icon(), lucide_pixmap(), QPixmap cuadrado (size x size) del icono Lucide `name`, trazado en `color`., QIcon del icono Lucide `name` trazado en `color`., _svg_data(), McpSyncDialog, QDialog, QTextEdit (+2 more)

### Community 38 - "get_connection"
Cohesion: 0.10
Nodes (31): create_board(), delete_board(), get_board(), get_board_by_uuid(), get_board_mutation_fingerprint(), get_boards(), move_board(), Recuerda el pack del AI Prompt Clipboard elegido para el tablero. (+23 more)

### Community 39 - "test_mcp.py"
Cohesion: 0.05
Nodes (65): get_mcp_tools_schema(), McpProtocolHandler, Retorna la especificación JSON-Schema de las herramientas expuestas por Ekin…, Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol., _done_and_other_columns(), parametrize, Pruebas automatizadas para el Servidor MCP (Model Context Protocol), seguridad…, #128: si fallaba el índice semántico de una tarea creada por MCP no quedaba… (+57 more)

### Community 40 - "logging_setup.py"
Cohesion: 0.17
Nodes (13): get_log_dir(), install_excepthook(), install_qt_message_handler(), Registro de diagnóstico y captura global de errores para Ekin. Escribe un log…, Directorio de logs (se crea si no existe): ~/.ekin/logs., Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del…, Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)., Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin. (+5 more)

### Community 41 - "DraggableColumnTitle"
Cohesion: 0.11
Nodes (5): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Etiqueta con el texto girado 90° (nombre de una columna plegada)., Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…, VerticalLabel

### Community 42 - "CalendarSettingsDialog"
Cohesion: 0.14
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 43 - ".contextMenuEvent"
Cohesion: 0.13
Nodes (9): format_single_cell(), format_table_all_cells(), Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen., Identifica si una tabla corresponde a un bloque de código. (+1 more)

### Community 44 - "SearchDialog"
Cohesion: 0.19
Nodes (8): Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon(), Verifica que SearchDialog liste tareas, filtre por texto/tablero y emita…, test_search_dialog_filters_and_activation()

### Community 45 - "markdown_to_qt_html"
Cohesion: 0.16
Nodes (19): author_entry_html(), markdown_to_qt_html(), migrate_plain_text_content(), Conversión a HTML de Qt del Markdown / texto plano que envían los agentes por…, Fragmento HTML de Qt para `text`. Lo que ya es HTML (empieza por una etiqueta)…, Entrada del diario «[autor]: texto» con el texto en Markdown. Los corchetes se…, Migración única: pasa a HTML las descripciones y entradas del diario guardadas…, _blocks() (+11 more)

### Community 46 - "test_prompt_clipboard.py"
Cohesion: 0.15
Nodes (18): _dialog(), fixture, parametrize, #67: AI Prompt Clipboard por tablero (packs DEV / Opositor / GTD con el esquema…, #84: los prompts DEV adivinaban columnas por posición ("the column right after…, #111: INITIAL y MIGRATE mandaban `graphify build` y `graphifyy claude`, que no…, test_boards_created_from_templates_get_their_prompt_pack(), test_builtin_packs_are_valid_and_target_the_board_mcp() (+10 more)

### Community 47 - "Any"
Cohesion: 0.15
Nodes (11): Any, _check_due(), _clean_text(), get_mcp_event_bus(), McpSecurityError, McpToolExecutor, ValueError si la fecha u hora no siguen YYYY-MM-DD / HH:MM; vacías significan…, Texto plano de un HTML de Qt (sin DOCTYPE/<style>), enmascarado si se pide. (+3 more)

### Community 48 - "McpManager"
Cohesion: 0.11
Nodes (15): McpManager, Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban., _free_port(), #115: sin timeout de socket, un cliente que anuncia un cuerpo y no lo envía…, Prueba el servidor HTTP embebido realizando peticiones directas., #107: en Windows, SO_REUSEADDR dejaba que un segundo Ekin se enlazara al 8765…, Lee eventos SSE (líneas `event:` / `data:`) hasta el primero de tipo `wanted`;…, #121: Claude Code se registra por SSE, pero solo /health y /rpc tenían tests.… (+7 more)

### Community 49 - ".load_task_data"
Cohesion: 0.11
Nodes (10): Refresca en vivo la tarea si otro (agente vía MCP, otro proceso, sync) la…, Habilita/inhabilita fecha y hora según los checks., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Kicker de cabecera: TABLERO · COLUMNA (en mayúsculas). Se repinta en vivo si…, Vuelca en el formulario los campos editables de `task` y toma la foto con la…, Campos editables tal y como están ahora en el formulario., Los mismos campos que _form_state(), con los valores guardados en la base de…, La tarea se borró fuera de este diálogo (agente, otro proceso, sync): avisar y… (+2 more)

### Community 50 - "sync.py"
Cohesion: 0.13
Nodes (14): get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero., Actualiza la marca de tiempo de sincronización y el hash del archivo., Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline. (+6 more)

### Community 51 - "summarize_diary_offline"
Cohesion: 0.40
Nodes (5): Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas)…, summarize_diary_offline(), Pruebas del resumen determinista del diario (local_ai.summarize_diary_offline),…, test_summarize_diary_offline_builds_two_sections(), test_summarize_diary_offline_empty()

### Community 52 - "PromptClipboardDialog"
Cohesion: 0.18
Nodes (8): Abre el AI Prompt Clipboard con el pack de prompts del tablero activo., ask_variable_values(), PromptClipboardDialog, QDialog, Copia el prompt seleccionado con las variables del tablero; pide las que falten., Pide el valor de cada variable {{...}} pendiente. Devuelve {nombre: valor}, o…, Modal con el pack de prompts del tablero: filtro por categoría, búsqueda, vista…, _swatch_icon()

### Community 53 - "test_templates.py"
Cohesion: 0.17
Nodes (17): create_board_from_template(), delete_custom_template(), get_all_templates(), get_template_by_id(), Retorna la lista unificada de plantillas de fábrica + personalizadas del…, Busca una plantilla por su identificador único., Elimina una plantilla personalizada de disco si existe, con validación anti…, Crea un nuevo tablero en la base de datos a partir de una plantilla dada. (+9 more)

### Community 54 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 55 - "BulkAddTaskDialog"
Cohesion: 0.20
Nodes (6): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas…, test_bulk_add_task_dialog()

### Community 56 - "markdown_edit.py"
Cohesion: 0.09
Nodes (34): apply_word_style_to_qt_table(), fit_html_images(), _is_network_target(), linkify_urls(), Utilidades compartidas para procesamiento y saneamiento de HTML en…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,…, Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Vacía las imágenes y fondos (`src`, `background`, `url(...)`) que apuntan a una… (+26 more)

### Community 57 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 58 - "test_batch_drag_drop.py"
Cohesion: 0.11
Nodes (18): Pruebas unitarias para la funcionalidad de Multi-Card Batch Drag-and-Drop…, Verifica la recolocación en lote entre columnas: atomicidad DB y renderizado…, Verifica el reordenamiento en lote dentro de la misma columna., Verifica que el movimiento en lote registre acción deshacer/rehacer y restaure…, Soltar un lote sobre una columna plegada debe desplegarla y colocar todas las…, test_batch_move_undo_and_redo(), test_board_view_batch_task_drop_across_columns_and_incremental(), test_board_view_batch_task_drop_same_column() (+10 more)

### Community 59 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 60 - "InteractiveTourBanner"
Cohesion: 0.18
Nodes (8): InteractiveTourBanner, QFrame, Barra superior interactiva in-situ para guiar al usuario a través del tablero…, Aplica colores y refresca los textos según el idioma y tema actuales., Verifica la navegación paso a paso, emisión de señales y finalización de…, Verifica que el botón cerrar descarte el tour y persista…, test_interactive_tour_banner_dismiss(), test_interactive_tour_banner_navigation_and_actions()

### Community 61 - "FlowLayout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 62 - "test_reminders.py"
Cohesion: 0.21
Nodes (15): current_week_key(), Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, should_show_weekly_digest(), split_digest_tasks(), _iso(), Pruebas de recordatorios anticipados y resumen semanal (reminders.py): - lógica… (+7 more)

### Community 63 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 64 - "TemplateCardWidget"
Cohesion: 0.18
Nodes (7): QDialog, QFrame, Tarjeta interactiva para visualizar y seleccionar una plantilla de tablero., Diálogo modal para guardar el tablero actual como plantilla personalizada de…, SaveAsTemplateDialog, TemplateCardWidget, test_save_as_template_dialog_headless()

### Community 65 - "backup_database"
Cohesion: 0.24
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder(), test_backup_rapid_calls_never_collide() (+3 more)

### Community 66 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 67 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 68 - "export_dialog.py"
Cohesion: 0.12
Nodes (13): ExportDialog, ImportConfirmationDialog, QDialog, Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Diálogo modal para confirmar la importación de tableros desde JSON., Genera una cadena amigable para nombres de archivo., Diálogo modal para configurar y ejecutar la exportación de tableros., _slugify() (+5 more)

### Community 69 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 70 - "test_start_working.py"
Cohesion: 0.13
Nodes (23): build_launch(), (argv, prompt_por_portapapeles). Un shim .cmd/.bat (instalación npm) pasa por…, Ejecuta START WORKING para el tablero. Devuelve el id de la CLI abierta, o None…, start_working(), flow(), no_real_quota(), fixture, #87: START WORKING abre la CLI del agente en el directorio local del tablero,… (+15 more)

### Community 71 - ".__init__"
Cohesion: 0.19
Nodes (6): CalendarChip, QFrame, QPushButton, QWidget, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes).

### Community 72 - "BoardMcpUiMixin"
Cohesion: 0.29
Nodes (5): BoardMcpUiMixin, Manejo de la interfaz del botón de integración MCP en la cabecera del tablero., Actualiza el estado visual del botón MCP en la cabecera del tablero., Abre el diálogo modal de configuración MCP para el tablero actual., Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el…

### Community 73 - "BoardButton"
Cohesion: 0.18
Nodes (6): BoardButton, Widget personalizado para representar un botón de tablero en la barra lateral., Arrastrar el tablero por la barra lateral para cambiar su orden., Línea de acento en el borde (superior o inferior) donde caerá el tablero., Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral., test_sidebar_board_button_cloud_badge()

### Community 74 - "LocalAiCircuitBreaker"
Cohesion: 0.15
Nodes (7): LocalAiCircuitBreaker, Disyuntor (Circuit Breaker) para el servicio local de inferencia y embeddings.…, Determina si se debe permitir el intento de llamada al servicio local de IA., Registra una respuesta satisfactoria del servicio local, cerrando el circuito., Registra un fallo o timeout del servicio local. Si supera el umbral, abre el…, Restablece manualmente el disyuntor al estado inicial CLOSED., test_local_ai_circuit_breaker_lifecycle()

### Community 75 - "test_incremental_rendering.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el renderizado incremental del tablero (mutaciones de…, Mover una tarea dentro de la misma columna solo debe reconstruir esa columna., Mover una tarea entre dos columnas solo debe reconstruir origen y destino,…, Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del…, create_quick_task solo debe reconstruir la columna de destino, preservando las…, add_task debe reconstruir solo la columna destino y actualizar el chip de…, test_add_task_incremental(), test_create_quick_task_incremental_rendering() (+3 more)

### Community 76 - "quota_popup.py"
Cohesion: 0.27
Nodes (9): quota_dot_icon(), quota_lines(), Semáforo de cuota restante de las CLIs de IA (#88): el punto de color de la…, Icono del semáforo: un punto relleno del color del estado., Líneas legibles de la cuota restante de Claude Code (una por ventana vigente)., _reset_text(), state_color(), tooltip_text() (+1 more)

### Community 77 - "test_mcp_live_refresh.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el refresco automático del tablero y diálogo de tareas…, Verifica que si TaskDetailDialog está abierto, se actualice en tiempo real…, Verifica que PRAGMA data_version y la huella digital del tablero detecten…, #125: la recarga tras un cambio del agente usaba notify=False, así que…, Verifica que BoardViewWidget detecte la escritura de un agente MCP externo y…, Verifica que emitir board_mutated en el bus de eventos desencadene la recarga…, test_board_view_auto_detects_external_mcp_mutation(), test_board_view_mcp_event_bus_trigger() (+3 more)

### Community 78 - ".__init__"
Cohesion: 0.18
Nodes (6): QCheckBox, Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de…, Stepper −/+ genérico ligado a un QSpinBox de respaldo; muestra `valor suffix`., ToggleSwitch

### Community 79 - "privacy_shield.py"
Cohesion: 0.22
Nodes (9): has_sensitive_data(), Escudo de Privacidad Local para Ekin Kanban. Filtra, sanitiza y protege…, Sanitiza el texto eliminando tokens sensibles y credenciales. Devuelve…, Comprueba rápidamente si un texto contiene algún patrón confidencial., sanitize_text(), parametrize, #118: mask_sensitive dejaba pasar tokens fine-grained de GitHub, claves de…, test_privacy_shield_masks_more_secret_formats() (+1 more)

### Community 80 - "local_ai.py"
Cohesion: 0.12
Nodes (25): clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, check_http_endpoint(), compute_fallback_embedding(), cosine_similarity(), find_duplicate_tasks(), get_llm_circuit_breaker() (+17 more)

### Community 81 - "BoardViewWidget"
Cohesion: 0.06
Nodes (21): BoardViewWidget, Muestra la barra del tour interactivo in-situ y navega al paso especificado., Oculta la barra del tour interactivo in-situ., Muestra celebración tras completar los 4 pasos del tour interactivo., Monitorea mutaciones en la base de datos realizadas por agentes de IA vía MCP…, Inicia o reinicia el temporizador de debounce para recargar el tablero de forma…, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Espera a que termine cualquier hilo de sincronización activo antes de destruir… (+13 more)

### Community 82 - "t"
Cohesion: 0.20
Nodes (9): PriorityManagerDialog, QDialog, Modal propio e independiente para gestionar los niveles y colores de Prioridad.…, Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Crea el icono de bandeja (habilita toasts nativos de Windows)., Returns the localized string for `key`, falling back to English if missing., t(), La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni… (+1 more)

### Community 83 - "test_widgets_headless.py"
Cohesion: 0.07
Nodes (52): _card_with_timer(), _cleanup_dialog(), _drop_files(), _make_task(), _mention_editor(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, Verifica que CloudSyncInfoDialog se construye con las instrucciones de los…, #61: archivos insertados en la Descripción o al editar una entrada ya publicada… (+44 more)

### Community 84 - "test_column_roles.py"
Cohesion: 0.18
Nodes (16): classify_column(), column_roles(), Rol de cada columna en el flujo del tablero (backlog, ready, in_progress,…, Rol de una columna según su nombre; OTHER si ninguna palabra clave encaja., {column_id: rol} para las columnas de un tablero (en orden de `position`). Si…, _words(), parametrize, Pruebas del clasificador de roles de columna (column_roles.py) sobre las… (+8 more)

### Community 85 - "BoardEditDialog"
Cohesion: 0.24
Nodes (3): BoardEditDialog, Diálogo personalizado para crear o editar un tablero (nombre, color y, al…, test_board_edit_dialog_local_dir_row()

### Community 86 - ".render_tags"
Cohesion: 0.10
Nodes (11): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas (excluyendo Prioridad, que tiene…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza., Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno»… (+3 more)

### Community 87 - "BoardConfigDialog"
Cohesion: 0.29
Nodes (5): BoardConfigDialog, QDialog, Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…, Verifica que BoardConfigDialog muestre las opciones adecuadas según si el…, test_board_config_dialog_cloud_options()

### Community 88 - "ColumnWidget"
Cohesion: 0.16
Nodes (7): ColumnWidget, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada)., Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…

### Community 89 - "TaskCard"
Cohesion: 0.08
Nodes (18): Verifica que _create_drag_pixmap genere una imagen con dimensiones válidas para…, test_task_card_drag_pixmap_badge(), Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, #109: los agentes citan las tarjetas por su id (#108...); la tarjeta lo…, #102: `clicked` abre el detalle con exec() (bucle anidado); si mientras tanto…, test_task_card_click_handler_may_destroy_the_card(), test_task_card_ctrl_click_and_selection_state(), test_task_card_shows_its_id_next_to_the_title() (+10 more)

### Community 90 - "test_timer_board_view.py"
Cohesion: 0.38
Nodes (9): _card_for(), _make_board_with_task(), Antes del fix, _build_column_widget releía el ajuste una vez POR COLUMNA…, test_build_column_widget_applies_configured_threshold(), test_build_column_widget_defaults_threshold_when_unset(), test_load_board_reads_timer_alert_hours_once_regardless_of_column_count(), test_refresh_timer_badges_noop_on_board_with_no_timers(), test_refresh_timer_badges_noop_on_welcome_screen() (+1 more)

### Community 91 - "Release v0.4.0"
Cohesion: 0.22
Nodes (8): backup_database() Function, backups.py Module, db_path Normalization (P1), Dead #TaskCardDueDate Object Name, iCalendar Line-Folding Off-by-One, Overdue Tasks in Notification Bell, Release v0.4.0, Subscribe-in-Google Helper

### Community 92 - "Hover-to-Expand Collapsed Column"
Cohesion: 0.25
Nodes (9): compute_drop_index() Function, Same-Column Drag Off-by-One Bug, handle_hover_expand_requested() Method, BoardViewWidget._hover_expanded_column_id, Hover-to-Expand Collapsed Column, QDrag.exec() Return as Drag-End Checkpoint, _build_column_widget() Helper, load_board() Mid-Drag Crash Bug (+1 more)

### Community 93 - "Global Search & Filter Feature"
Cohesion: 0.22
Nodes (9): Ctrl+F Search Shortcut, Global Search & Filter Feature, Immediate-Persistence Pattern, on_notification_task Handler Reuse, Release v0.5.0, SearchDialog Class, search_tasks() Function, Subtask Checklist UI (Task Detail Dialog) (+1 more)

### Community 94 - "Git-Stash Empirical Regression Verification"
Cohesion: 0.22
Nodes (9): QMimeData GC Lifetime Bug (Test-Only), tests/test_hover_expand.py, Ctrl+Z FK IntegrityError Crash Fix (Fix 2), Git-Stash Empirical Regression Verification, STATUS_HEAP_CORRUPTION Test-Suite Crash, Stale Board Card on Calendar Edit Fix (Fix 4), conftest.py QApplication Teardown Fix, restore_task() Function (+1 more)

### Community 95 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.22
Nodes (8): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, Item 1 — Ctrl+N targets the last-interacted-with column, Item 2 — Two-row utility bar, Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 96 - "authenticate_and_get_board"
Cohesion: 0.17
Nodes (10): BaseHTTPRequestHandler, main(), Punto de entrada de línea de comandos (CLI) para MCP vía transporte STDIO.…, authenticate_and_get_board(), McpHttpHandler, Manejador HTTP para Server-Sent Events (SSE) y llamadas JSON-RPC directas., Envía cabeceras CORS restrictivas para evitar que sitios web maliciosos lean…, Maneja peticiones preflight CORS de clientes web o navegadores. (+2 more)

### Community 97 - "copy_board"
Cohesion: 0.33
Nodes (6): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…

### Community 98 - "connection.py"
Cohesion: 0.06
Nodes (33): move_column_to_board(), Mueve una columna a otro tablero y la coloca al final de su lista de columnas., close_cached_connections(), get_db_data_version(), get_default_db_path(), Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, Devuelve el contador interno PRAGMA data_version de SQLite. Permite detectar…, Cierra y purga las conexiones abiertas en el hilo actual para db_path (o todas). (+25 more)

### Community 99 - "start_working.py"
Cohesion: 0.11
Nodes (16): CliTool, detect_installed(), launch(), CLIs de agentes de IA que Ekin sabe lanzar desde un tablero (START WORKING):…, [(CliTool, ruta del ejecutable)] de las CLIs conocidas que están en el PATH., Actualiza la CLI. Devuelve (ok, mensaje). Nunca lanza: un fallo no debe…, Abre la CLI en una consola nueva (Windows Terminal si es la consola por…, _run() (+8 more)

### Community 100 - ".insertFromMimeData"
Cohesion: 0.17
Nodes (6): Al pegar: archivos locales se insertan como enlaces y se emite señal para…, Inserta cada archivo local como enlace «📄 nombre» y emite local_link_pasted…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor con diseño estilo…, Codifica un QImage como data URI PNG en base64., Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se…

### Community 101 - "create_premerge_backup"
Cohesion: 0.17
Nodes (12): create_premerge_backup(), export_board_to_sync_dict(), _prune_premerge_backups(), Serializa un tablero completo con sus columnas, tareas, etiquetas, enlaces y…, Conserva únicamente las `keep` copias de seguridad más recientes de sync para…, Crea una instantánea local automática del tablero antes de fusionar cambios,…, Verifica que create_premerge_backup usa el directorio canónico de la BD y poda…, Verifica que export_board_to_sync_dict serializa correctamente todos los campos… (+4 more)

### Community 102 - ".load_board"
Cohesion: 0.08
Nodes (12): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Ejecuta una recarga suave y segura del tablero cuando el agente de IA realiza…, Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Abre el diálogo para crear una columna., Confirma y borra una columna. (+4 more)

### Community 103 - "QuotaPopup"
Cohesion: 0.17
Nodes (6): QDialog, QuotaPopup, Detalle de la cuota por CLI instalada; permite activar o quitar la lectura de…, Colorea el semáforo según la cuota restante de Claude Code (gris sin datos)., Muestra el detalle de la cuota por CLI anclado bajo el semáforo., Re-aplica los colores dependientes del tema en los widgets de la barra lateral…

### Community 104 - "_board_sync_lock"
Cohesion: 0.33
Nodes (6): _board_sync_lock(), Lock, #124: «Sincronizar ahora» mientras la sync automática del mismo tablero sigue…, test_sidebar_sync_now_on_a_busy_board_informs_instead_of_failing(), #124: la sync manual de la barra lateral llamaba a sync_board_with_file en…, test_sync_of_a_board_already_syncing_returns_busy_without_touching_anything()

### Community 105 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Carga y conecta a la base de datos local un tablero sincronizado existente…, Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 106 - "CreateBoardDialog"
Cohesion: 0.23
Nodes (3): CreateBoardDialog, Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o…, test_create_board_dialog_headless()

### Community 107 - "task_mixins.py"
Cohesion: 0.33
Nodes (4): Mixins de funcionalidad modular para TaskDetailDialog (temporizadores,…, IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el…, Comprueba si existen tareas similares o duplicadas en este tablero., TaskAiMixin

### Community 108 - "TaskListArea"
Cohesion: 0.31
Nodes (3): Verifica que TaskListArea emita batch_tasks_dropped cuando se suelta un payload…, test_task_list_area_batch_drop_event(), TaskListArea

### Community 109 - "BoardSelectionMixin"
Cohesion: 0.21
Nodes (7): BoardSelectionMixin, Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej.…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero., Escape deselecciona tarjetas múltiples.

### Community 110 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 111 - "create_getting_started_board"
Cohesion: 0.33
Nodes (6): create_getting_started_board(), Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su…, Verifica que la plantilla de Primeros Pasos instancie las 4 columnas…, test_create_getting_started_board(), Verifica que BoardViewWidget muestre y oculte el banner del tour según el…, test_board_view_interactive_tour_lifecycle()

### Community 112 - "pixmap_from_data_uri"
Cohesion: 0.20
Nodes (10): pixmap_from_data_uri(), Decodifica 'data:image/xxx;base64,....' a un QPixmap con caché en memoria…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Regresión: antes href y src eran el MISMO data URI (la miniatura ya reducida al…, test_markdown_text_edit_stores_higher_res_copy_for_preview(), test_pixmap_from_data_uri_decodes_valid_png(), test_pixmap_from_data_uri_returns_null_for_garbage() (+2 more)

### Community 113 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 114 - ".sync_ics"
Cohesion: 0.18
Nodes (4): Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde el calendario: abrir el detalle y quedarnos en el calendario., Campana, Calendario, Mi trabajo, Analíticas y .ics tras cambios fuera del…, Reescribe cada feed .ics con auto-sync configurado (el global de todos los…

### Community 115 - "test_release_notes.py"
Cohesion: 0.47
Nodes (4): El workflow de release (windows-latest, pwsh) extrae las notas de CHANGELOG.md…, _run(), test_notes_on_stdout_are_utf8_whatever_the_console_encoding(), test_notes_with_emoji_are_written_as_utf8_to_the_output_file()

### Community 116 - "._handle_sync_finished"
Cohesion: 0.20
Nodes (5): Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Exporta automáticamente los cambios locales si el tablero está vinculado.

### Community 117 - "format_sync_summary"
Cohesion: 0.36
Nodes (7): format_sync_summary(), Genera un resumen conciso de un SyncResult para mostrar en la interfaz., Prueba del resumen conciso de sincronización (board_view.format_sync_summary)., test_summary_exported(), test_summary_imported_without_conflicts(), test_summary_merged_lists_updates_and_conflicts(), test_summary_up_to_date()

### Community 119 - "bump_version.py"
Cohesion: 0.52
Nodes (6): calculate_next_version(), get_current_version(), main(), update_changelog(), update_installer_iss(), update_version_py()

### Community 120 - "test_wip_limit.py"
Cohesion: 0.43
Nodes (5): _board_with(), Pruebas de los límites WIP por columna: persistencia y aviso visual en el…, test_column_widget_no_wip_label_when_unset(), test_column_widget_shows_wip_over_limit_in_danger(), test_column_widget_wip_under_limit_is_muted()

### Community 121 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 122 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 123 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 124 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 125 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 126 - "CLAUDE.md"
Cohesion: 0.29
Nodes (5): 1. Think Before Coding, 2. Simplicity First, 3. Surgical Changes, 4. Goal-Driven Execution, graphify

### Community 127 - "test_cli_quota.py"
Cohesion: 0.12
Nodes (29): _command(), install_claude_statusline(), is_installed(), _load_settings(), _python_for_scripts(), quota_state(), Cuota restante de las CLIs de IA (#88). Claude Code la expone de forma…, Quita la status line de Ekin y restaura la que hubiera antes. (+21 more)

### Community 128 - "2. Implementation Tasks"
Cohesion: 0.09
Nodes (22): 0. Estado (2026-10-15, tras el OUTRO b063add), #101 — BUG: el servidor MCP no arranca al abrir Ekin  `[S]`, #102 — BUG: «TaskCard already deleted» al cerrar el detalle  `[S]`, 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, #74 — Respuestas MCP en inglés para ahorrar tokens  `[A: S · B: S · C: M]`, #81 — PWA Ekin Móvil  `[XL — épica]` (+14 more)

### Community 129 - "compute_drop_index"
Cohesion: 0.25
Nodes (10): Verifica que compute_drop_index excluya todas las tareas del lote para evitar…, test_compute_drop_index_multi_card(), Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last() (+2 more)

### Community 130 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 131 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 132 - "DayCell"
Cohesion: 0.20
Nodes (5): DayCell, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon(), Verifica que _on_task_rescheduled actualice la fecha en la BD y emita…, test_calendar_view_on_task_rescheduled_and_drag_drop()

### Community 134 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 135 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 136 - "test_concurrent_edit.py"
Cohesion: 0.18
Nodes (17): _card_of(), _close(), #103: edición concurrente de una tarjeta. Mientras el detalle está abierto, un…, Cierre nativo de la app (0xc0000005 en Qt6Widgets.dll, 2026-10-15): el detalle…, Escenario real del cierre: clic en la tarjeta → detalle abierto → un agente…, Prueba manual 2 de #103 (2026-10-15): con la hoja de estilos de la app, mostrar…, test_a_description_the_user_did_edit_still_wins(), test_click_outside_keeps_the_agents_changes() (+9 more)

### Community 138 - "test_last_active_column.py"
Cohesion: 0.31
Nodes (10): _make_board(), test_add_task_sets_last_active_column(), test_column_background_click_sets_last_active_column(), test_column_widget_mouse_press_emits_column_activated(), test_quick_add_task_falls_back_to_first_column_when_nothing_active(), test_quick_add_task_falls_back_when_last_active_column_belongs_to_another_board(), test_quick_add_task_falls_back_when_last_active_column_was_deleted(), test_quick_add_task_noop_with_no_board_selected() (+2 more)

### Community 139 - "LandingTourDialog"
Cohesion: 0.17
Nodes (8): LandingTourDialog, QDialog, QWidget, Diálogo modal interactivo para guiar al usuario en las capacidades clave de…, Verifica la navegación paso a paso y la persistencia de LandingTourDialog., Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el…, test_landing_tour_dialog_dont_show_checkbox(), test_landing_tour_dialog_navigation_and_persistence()

### Community 140 - ".handle_task_drop"
Cohesion: 0.20
Nodes (5): Maneja la recolocación en lote de múltiples tareas tras arrastrarlas., Soltar un lote de tarjetas sobre una columna plegada: la despliega y coloca las…, Registra una acción deshacer/rehacer para el movimiento (individual o en lote)…, Maneja la lógica de recolocación de tareas (individual o por lote) tras…, Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…

### Community 141 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 142 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 143 - "ensure_mcp_registered"
Cohesion: 0.29
Nodes (6): ensure_mcp_registered(), Registra el servidor MCP del tablero en la CLI si aún no lo está. Devuelve (ok,…, subprocess.run simulado: devuelve el resultado indicado según el subcomando., _Runs, test_agy_mcp_uses_the_http_rpc_endpoint(), test_claude_mcp_is_added_in_the_repo_scope_only_when_missing()

### Community 145 - "_ClickOutsideFilter"
Cohesion: 0.25
Nodes (5): _ClickOutsideFilter, QObject, Mueve la barra de desplazamiento del diario hasta abajo., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo…, Filtro de eventos que detecta clics fuera del diálogo dentro de la ventana…

### Community 171 - "BoardSyncWorker"
Cohesion: 0.29
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 181 - "TableInsertDialog"
Cohesion: 0.25
Nodes (5): Diálogo modal para configurar e insertar una tabla con número inicial de filas…, TableInsertDialog, Pide filas y columnas mediante un diálogo unificado e inserta la tabla…, Verifica que TableInsertDialog admita dimensiones personalizadas y que su botón…, test_table_dialog_insert_dimensions()

### Community 185 - ".reload_logs"
Cohesion: 0.20
Nodes (5): Carga el siguiente lote de entradas anteriores del diario preservando la…, Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Crea una nueva entrada de diario con el texto del input., Elimina una entrada de diario tras confirmación., Limpia y vuelve a cargar los logs/entradas del diario con carga diferida (lazy…

### Community 186 - "ImagePreviewDialog"
Cohesion: 0.12
Nodes (14): ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, QWidget, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/…, Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña… (+6 more)

### Community 188 - "mcp_server.py"
Cohesion: 0.14
Nodes (11): Exception, _DummySignal, _masked(), McpEventBus, McpPermissionDenied, QObject, Servidor MCP (Model Context Protocol) para Ekin Kanban. Permite a agentes de IA…, Texto con los datos sensibles enmascarados (Privacy Shield) si se pide. (+3 more)

### Community 192 - "_column_with_cards"
Cohesion: 0.29
Nodes (8): _assert_cards_fit_the_column(), _column_with_cards(), #132: la columna alineaba sus tarjetas arriba (AlignTop) y, con esa alineación,…, #132: la fila de fecha + hora + temporizador + tablero enlazado no podía…, #132: una palabra sin espacios (ruta, snake_case) no tenía dónde partirse:…, test_task_card_title_breaks_long_paths_and_identifiers(), test_task_card_titles_get_the_height_they_need_in_a_column(), test_task_cards_fit_the_column_width()

### Community 193 - "WeeklyDigestDialog"
Cohesion: 0.32
Nodes (4): QDialog, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, _swatch_icon(), WeeklyDigestDialog

### Community 194 - "._update_local_dir_buttons"
Cohesion: 0.33
Nodes (3): Tras cambiar el directorio local desde fuera (p. ej. Ajustes), repinta Diario y…, Diario solo si el directorio local tiene algún .md / .txt; Work siempre, con un…, WORK: MCP en marcha, CLI actualizada y abierta en el repo con el INTRO. Si el…

### Community 195 - "hex_to_rgb"
Cohesion: 0.50
Nodes (4): contrast_text(), hex_to_rgb(), Tinta (#201e1d) sobre fondos claros, crema (#f5ead8) sobre fondos oscuros —…, Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b).

### Community 196 - "_editor_with_all_selected"
Cohesion: 0.33
Nodes (6): _editor_with_all_selected(), #68: subrayado desde el botón «U» y con Ctrl+U / Ctrl+S (Subrayado en Word en…, #62: el botón «1.» convierte las líneas seleccionadas en una lista numerada., test_ctrl_shift_u_still_uppercases_not_underlines(), test_numbering_button_turns_selected_lines_into_numbered_list(), test_underline_button_and_shortcuts_toggle_underline()

### Community 197 - "SidebarWidget"
Cohesion: 0.09
Nodes (23): QFrame, Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…, Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos…, Persiste el nuevo orden y recoloca los botones sin recargar el tablero activo., SidebarWidget, _board_drop_event() (+15 more)

### Community 198 - "set_language"
Cohesion: 0.25
Nodes (9): get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), test_i18n_strings_catalog_and_fallback(), test_settings_dialog_constructs_with_saved_language() (+1 more)

### Community 199 - "test_local_ai_rdi.py"
Cohesion: 0.21
Nodes (12): format_daily_standup_markdown(), generate_daily_standup_data(), Formatea la estructura de standup_data en un reporte Markdown elegante., Extrae métricas y estado del flujo del tablero para generar el informe Daily…, _active(), _agile_board(), Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi: - Fase 1:…, #84: la tarea activa se resuelve en el servidor (In Progress → Review → Ready)… (+4 more)

### Community 200 - "McpHttpServer"
Cohesion: 0.11
Nodes (9): McpHttpServer, Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies., Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria., _SseClientSession, Verifica que el recolector de sesiones SSE elimine sesiones inactivas o…, Verifica el control de contrapresión y límite de cola en sesiones SSE., test_mcp_sse_send_to_session_queue_limit(), test_mcp_sse_session_scavenger() (+1 more)

### Community 201 - "TaskTimerMixin"
Cohesion: 0.32
Nodes (5): Manejo de estado y UI del temporizador de tareas para TaskDetailDialog., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Actualiza el botón y la etiqueta de tiempo transcurrido según…, TaskTimerMixin

### Community 205 - "mcp_board"
Cohesion: 0.67
Nodes (3): mcp_board(), fixture, Crea un tablero de prueba con MCP activado y columnas.

### Community 208 - "NotificationsPopup"
Cohesion: 0.18
Nodes (7): NotificationsPopup, Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana., test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 209 - "_shown_expanded_column"
Cohesion: 0.50
Nodes (4): #59: un nombre largo no debe cortarse a mitad de carácter ni empujar los…, _shown_expanded_column(), test_column_title_elides_long_name_to_fit_header(), test_column_title_short_name_is_not_elided()

### Community 219 - ".check_for_updates"
Cohesion: 0.25
Nodes (4): Arranca la versión nueva como proceso aparte y cierra esta de forma ordenada…, Verifica de forma silenciosa (o con feedback si manual=True) si hay…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica si hay actualizaciones en el repo de GitHub (modo git dev).

### Community 225 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 230 - "sync_test_db"
Cohesion: 0.67
Nodes (3): fixture, Crea una base de datos temporal para pruebas de sincronización., sync_test_db()

### Community 244 - "QLabel"
Cohesion: 0.15
Nodes (11): CodeBlockDialog, LinkDialog, QDialog, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para insertar un enlace (URL)., QLabel, QDialog, ShortcutsDialog (+3 more)

## Knowledge Gaps
- **152 isolated node(s):** `CliTool`, `1. Overview`, `2. Implementation Tasks`, `3. Acceptance Criteria`, `QA Report` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **62 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `test_main_window.py`, `DayCell`, `.__init__`, `MyWorkWidget`, `MarkdownTextEdit`, `DashboardWidget`, `DiaryViewerDialog`, `.handle_task_drop`, `LandingTourDialog`, `TagManagerDialog`, `SettingsDialog`, `prompt_packs.py`, `TagPickerDialog`, `CommandPalette`, `LogEntryWidget`, `sync_board_with_file`, `._rebuild_single_column`, `TaskDetailDialog`, `.reload_boards`, `RichTextToolbar`, `strings.py`, `BoardSyncUiMixin`, `CalendarViewWidget`, `.show_command_palette`, `ColorCirclesPicker`, `templates.py`, `format_code_block_html`, `lucide_icon`, `test_mcp.py`, `CalendarSettingsDialog`, `.contextMenuEvent`, `SearchDialog`, `.load_task_data`, `summarize_diary_offline`, `PromptClipboardDialog`, `BulkAddTaskDialog`, `markdown_edit.py`, `.reload_logs`, `ImagePreviewDialog`, `InteractiveTourBanner`, `._build_language_segment`, `TemplateCardWidget`, `WeeklyDigestDialog`, `._update_local_dir_buttons`, `export_dialog.py`, `SidebarWidget`, `test_start_working.py`, `.__init__`, `BoardMcpUiMixin`, `TaskTimerMixin`, `BoardButton`, `set_language`, `quota_popup.py`, `.__init__`, `local_ai.py`, `BoardViewWidget`, `NotificationsPopup`, `test_widgets_headless.py`, `BoardEditDialog`, `.render_tags`, `BoardConfigDialog`, `ColumnWidget`, `TaskCard`, `.check_for_updates`, `start_working.py`, `.load_board`, `QuotaPopup`, `CreateBoardDialog`, `task_mixins.py`, `BoardSelectionMixin`, `.mouseReleaseEvent`, `create_getting_started_board`, `QLabel`, `format_sync_summary`, `.notify_due_today`?**
  _High betweenness centrality (0.294) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `copy_board`, `connection.py`, `test_local_dir.py`, `export_dialog.py`, `tasks.py`, `logs.py`, `sync.py`, `snapshots.py`, `get_task_tags_bulk`, `tags.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `MarkdownTextEdit` connect `MarkdownTextEdit` to `.insertFromMimeData`, `format_code_block_html`, `lucide_icon`, `_editor_with_all_selected`, `.contextMenuEvent`, `test_ux_enhancements.py`, `.mouseReleaseEvent`, `pixmap_from_data_uri`, `_ClickOutsideFilter`, `LogEntryWidget`, `test_widgets_headless.py`, `TableInsertDialog`, `TaskDetailDialog`, `markdown_edit.py`, `RichTextToolbar`, `FlowLayout`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `BoardViewWidget` (e.g. with `DiaryViewerDialog` and `InstallerDownloadThread`) actually correct?**
  _`BoardViewWidget` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `TaskDetailDialog` (e.g. with `.open_task_details()` and `MarkdownTextEdit`) actually correct?**
  _`TaskDetailDialog` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `MarkdownTextEdit` (e.g. with `LogEntryWidget` and `FlowLayout`) actually correct?**
  _`MarkdownTextEdit` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CliTool`, `1. Overview`, `2. Implementation Tasks` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._