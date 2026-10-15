# Graph Report - Ekin  (2026-10-15)

## Corpus Check
- 159 files · ~208,082 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2911 nodes · 5249 edges · 232 communities (165 shown, 67 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 191 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `227a8d51`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_local_dir.py
- test_main_window.py
- test_ics_export.py
- QDialog
- test_widgets_headless.py
- sync_board_with_file
- MarkdownTextEdit
- tasks.py
- get_connection
- DashboardWidget
- PromptClipboardDialog
- ._handle_key_press
- BoardSyncController
- clean_html_description
- SettingsDialog
- lucide_icon
- TaskListArea
- CommandPalette
- LogEntryWidget
- /graphify Pipeline
- board_sync.py
- ._rebuild_single_column
- test_diary_viewer.py
- .reload_boards
- connection.py
- RichTextToolbar
- TaskCard
- BoardSyncUiMixin
- CalendarViewWidget
- tags.py
- QFrame
- .show_command_palette
- links.py
- MainWindow
- templates.py
- test_my_work_view.py
- McpSyncDialog
- boards.py
- test_mcp.py
- main
- DraggableColumnTitle
- CalendarSettingsDialog
- .contextMenuEvent
- SearchDialog
- .__init__
- SaveAsTemplateDialog
- Any
- McpManager
- export_dialog.py
- sync.py
- summarize_diary_offline
- test_templates.py
- BoardSelectionMixin
- snapshots.py
- BulkAddTaskDialog
- markdown_edit.py
- test_hover_expand.py
- UndoManager
- Part B: Semantic Extraction (Subagents)
- QLabel
- FlowLayout
- test_reminders.py
- format_elapsed_time
- CreateBoardDialog
- backup_database
- Release v0.6.0
- 2. Implementation Tasks
- detect_available_llm
- CI Workflow (ruff + pytest)
- test_start_working.py
- .__init__
- .open_board_config
- BoardButton
- LocalAiCircuitBreaker
- test_incremental_rendering.py
- test_prompt_clipboard.py
- test_local_ai.py
- .__init__
- .handle_task_drop
- local_ai.py
- BoardViewWidget
- PriorityManagerDialog
- t
- test_column_roles.py
- BoardEditDialog
- .render_tags
- LandingTourDialog
- ColumnWidget
- ColorCirclesPicker
- test_timer_board_view.py
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- TECHNICAL DESIGN DOCUMENT
- authenticate_and_get_board
- board_ops.py
- ics_sync.py
- cli_tools.py
- .insertFromMimeData
- ImagePreviewDialog
- TagManagerDialog
- set_language
- BoardSyncWorker
- connect_shared_board_from_file
- SyncResult
- .select_board
- compute_drop_index
- NotificationsPopup
- .mouseReleaseEvent
- conftest.py
- show_image_preview
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- test_board_reorder.py
- TaskTimerMixin
- .get_pending_notifications
- QThread
- .notify_due_today
- bump_version.py
- test_wip_limit.py
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- CLAUDE.md
- cli_quota.py
- 2. Implementation Tasks
- create_getting_started_board
- build_qss
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- DayCell
- .apply_theme
- Calendar Drag-to-Reschedule
- Cross-Repo Graph Merge
- TaskDetailDialog
- QFrame
- .load_board
- TableInsertDialog
- prompt_packs.py
- get_subtasks_progress_bulk() Function
- v0.9.1: Local File Attachments on Task Links
- QFrame
- extract_release_notes.py
- QWidget
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
- QWidget
- create_log() Atomicity Fix (Fix 6)
- Dead app.setStyleSheet() Removal (Fix 8)
- Stale Shortcuts Help Text Fix (Fix 3)
- timer_alert_hours N+1 Read Fix (Fix 7)
- open_shortcuts_requested Signal
- add_column() board_id==-1 Guard Fix
- backlog.md — Ekin Kanban Backlog
- Token Reduction Benchmark
- transcribe_all() Video/Audio Transcription
- strings.py
- Ekin App Icon
- ekin-kanban
- _ClickOutsideFilter
- QDialog
- QTextEdit
- QWidget
- .delete_board
- start_working.py
- format_code_block_html
- QFrame
- QThread
- test_priority_manager.py
- mcp_server.py
- SidebarWidget
- TagPickerDialog
- test_local_ai_rdi.py
- _SseClientSession
- task_mixins.py
- Any
- QObject
- QFrame
- fixture
- ._update_mention_popup
- _collapsed_column_widget
- quota_popup.py
- _mention_editor
- parametrize
- _editor_with_all_selected
- test_database_sync_helpers_lifecycle
- test_connection_pooling_and_lifecycle
- test_fts5_search_and_triggers
- test_fts5_search_fallback_on_error
- test_update_task_positions_bumps_version_only_on_column_change
- test_concurrent_edit.py
- test_cli_quota.py
- test_last_active_column.py
- hex_to_rgb
- ._change_list_indent
- WeeklyDigestDialog
- _shown_expanded_column
- claude_statusline.py
- fixture
- fixture
- test_shortcuts_item_new_task_describes_last_active_column_behavior
- sync_test_db
- QDialog
- QDialog
- QObject

## God Nodes (most connected - your core abstractions)
1. `t()` - 249 edges
2. `BoardViewWidget` - 110 edges
3. `TaskDetailDialog` - 105 edges
4. `get_connection()` - 99 edges
5. `MarkdownTextEdit` - 85 edges
6. `MainWindow` - 52 edges
7. `SidebarWidget` - 45 edges
8. `lucide_icon()` - 42 edges
9. `SettingsDialog` - 31 edges
10. `McpProtocolHandler` - 31 edges

## Surprising Connections (you probably didn't know these)
- `test_is_local_link_classifies_urls_vs_paths()` --calls--> `_is_local_link()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `test_installer_download_thread()` --indirect_call--> `t()`  [INFERRED]
  tests/test_main_window.py → strings.py
- `BoardSyncWorker` --uses--> `BoardSyncController`  [INFERRED]
  board_sync.py → board_sync_controller.py
- `SyncResult` --uses--> `BoardSyncController`  [INFERRED]
  board_sync.py → board_sync_controller.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (232 total, 67 thin omitted)

### Community 1 - "test_local_dir.py"
Cohesion: 0.07
Nodes (43): list_repo_files(), Archivos del directorio local (repo) asociado a un tablero, para ofrecerlos en…, Rutas relativas (con «/») de los archivos de `root`, como mucho `limit`., boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas. (+35 more)

### Community 2 - "test_main_window.py"
Cohesion: 0.07
Nodes (47): get_default_db_path(), InstallerDownloadThread, parse_version_tuple(), Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, ReleaseCheckThread, _close_window(), _FakeMcpManager, _make_task_on_board() (+39 more)

### Community 3 - "test_ics_export.py"
Cohesion: 0.11
Nodes (28): build_ics(), _escape(), export_ics(), _fold_line(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar. (+20 more)

### Community 5 - "test_widgets_headless.py"
Cohesion: 0.09
Nodes (44): _card_with_timer(), _cleanup_dialog(), _drop_files(), _make_task(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, #61: archivos insertados en la Descripción o al editar una entrada ya publicada…, Con los botones de subrayado, numeración y adjuntar, la barra del Diario partía…, El editor en línea de una entrada ya publicada debe escalar las imágenes… (+36 more)

### Community 6 - "sync_board_with_file"
Cohesion: 0.07
Nodes (41): Ejecuta el ciclo completo de sincronización y fusión diferencial para un…, sync_board_with_file(), Verifica que cambios en el archivo remoto sin cambios locales se importan…, Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que desvincular un tablero borra sync_path y lo deja offline., Verifica que si local y remoto añaden tareas diferentes simultáneamente, la…, Verifica que un archivo .ekboard corrupto no rompe la aplicación ni corrompe la…, Verifica que se genera una instantánea de respaldo en backups/ al detectar… (+33 more)

### Community 7 - "MarkdownTextEdit"
Cohesion: 0.05
Nodes (37): MarkdownTextEdit, Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Aplica interlineado proporcional (por defecto 135%) a todos los bloques del…, QTextEdit, Verifica que escribir en una cita con placeholder borra el placeholder…, Verifica que hacer clic en una cita con placeholder borra el texto predefinido., test_quote_placeholder_clearing_on_click() (+29 more)

### Community 8 - "tasks.py"
Cohesion: 0.08
Nodes (25): advance_overdue_recurring(), advance_recurrence(), create_task(), create_tasks_batch(), delete_task(), next_occurrence(), Vincula una tarea con otro tablero (o None para quitar el vínculo)., Inicia (started_at = timestamp ISO de datetime.now()) o borra (started_at =… (+17 more)

### Community 9 - "get_connection"
Cohesion: 0.16
Nodes (18): create_column(), delete_column(), get_column(), get_columns(), Pliega (collapsed=1) o despliega (0) una columna del tablero., Actualiza las posiciones de múltiples columnas. column_positions debe ser una…, set_column_collapsed(), update_column() (+10 more)

### Community 10 - "DashboardWidget"
Cohesion: 0.10
Nodes (20): _esc(), export_report_pdf(), gather_stats(), Métricas de tableros para el panel de Analíticas y la exportación a PDF.…, Recopila métricas transversales (todos los tableros activos)., Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)., Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)., render_report_html() (+12 more)

### Community 11 - "PromptClipboardDialog"
Cohesion: 0.16
Nodes (9): Abre el AI Prompt Clipboard con el pack de prompts del tablero activo., ask_variable_values(), PromptClipboardDialog, AI Prompt Clipboard del tablero: los prompts del pack del tablero (DEV,…, Copia el prompt seleccionado con las variables del tablero; pide las que falten., Pide el valor de cada variable {{...}} pendiente. Devuelve {nombre: valor}, o…, Modal con el pack de prompts del tablero: filtro por categoría, búsqueda, vista…, _swatch_icon() (+1 more)

### Community 12 - "._handle_key_press"
Cohesion: 0.09
Nodes (11): Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Alinea el bloque de texto actual o selección a la izquierda., Centra el bloque de texto actual o selección., Alinea el bloque de texto actual o selección a la derecha., Justifica el bloque de texto actual o selección., Convierte el texto seleccionado (o la palabra bajo el cursor) a MAYÚSCULAS., Convierte el texto seleccionado (o la palabra bajo el cursor) a minúsculas. (+3 more)

### Community 13 - "BoardSyncController"
Cohesion: 0.09
Nodes (17): BoardSyncController, QObject, board_sync_controller.py - Controlador de sincronización desacoplado de…, Configura el watcher para detectar reactivamente cambios externos., Disparado por el sistema de archivos ante modificaciones externas., Desvincula el tablero actual de su archivo compartido., Espera a que termine cualquier hilo de sincronización en ejecución., Devuelve True si hay una sincronización en segundo plano activa. (+9 more)

### Community 14 - "clean_html_description"
Cohesion: 0.15
Nodes (20): clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, author_entry_html(), markdown_to_qt_html(), migrate_plain_text_content(), Conversión a HTML de Qt del Markdown / texto plano que envían los agentes por…, Fragmento HTML de Qt para `text`. Lo que ya es HTML se devuelve tal cual; el… (+12 more)

### Community 15 - "SettingsDialog"
Cohesion: 0.10
Nodes (14): Pestaña Directorios locales: cada tablero con su carpeta (repo), con Examinar y…, Segmentado English / Español que maneja el lang_combo de respaldo., Segmentado Light / Dark que maneja el theme_combo de respaldo., SettingsDialog, test_settings_persists_reminder_and_digest(), Verifica que el botón 'Buscar ahora' en ajustes emita check_updates_requested., Verifica que el botón de Tour Interactivo en Ajustes emita…, test_settings_dialog_check_updates_button_emits_signal() (+6 more)

### Community 16 - "lucide_icon"
Cohesion: 0.10
Nodes (14): BoardMcpUiMixin, Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Manejo de la interfaz del botón de integración MCP en la cabecera del tablero., Actualiza el estado visual del botón MCP en la cabecera del tablero., Abre el diálogo modal de configuración MCP para el tablero actual., Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el…, _align_icon(), Dibuja un icono vectorial nítido para alineación de texto (left, center, right,… (+6 more)

### Community 18 - "CommandPalette"
Cohesion: 0.14
Nodes (12): CommandPalette, QDialog, _swatch_icon(), Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, Verifica que CommandPalette no tenga WA_DeleteOnClose activo y no sufra…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query() (+4 more)

### Community 19 - "LogEntryWidget"
Cohesion: 0.06
Nodes (32): fit_html_images(), linkify_urls(), Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no…, Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,…, sanitize_chat_html(), LogEntryWidget, Actualiza el ancho de las imágenes y tablas del comentario para ajustarse al… (+24 more)

### Community 20 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 21 - "board_sync.py"
Cohesion: 0.12
Nodes (23): _apply_remote_board_clean(), calculate_file_hash(), create_premerge_backup(), _execute_two_way_merge(), export_board_to_sync_dict(), _merge_task_sub_entities(), now_utc_iso(), _prune_premerge_backups() (+15 more)

### Community 22 - "._rebuild_single_column"
Cohesion: 0.10
Nodes (11): Maneja las acciones interactivas directas asociadas a cada paso del tour., Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de… (+3 more)

### Community 23 - "test_diary_viewer.py"
Cohesion: 0.12
Nodes (13): Abre los diarios de desarrollo (diary.md / diary_archive.md) del directorio…, Tras cambiar el directorio local desde fuera (p. ej. Ajustes), repinta Diario y…, Diario solo con diarios en el directorio local; Work siempre, con un tooltip…, WORK: MCP en marcha, CLI actualizada y abierta en el repo con el INTRO. Si el…, diary_files(), DiaryViewerDialog, Rutas de los diarios que existen en `local_dir` (en el orden de DIARY_FILES)., Una pestaña por diario existente, renderizado como Markdown; Recargar conserva… (+5 more)

### Community 24 - ".reload_boards"
Cohesion: 0.22
Nodes (5): Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero a partir de una plantilla o en…, Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Permite al usuario seleccionar un archivo .ekboard compartido existente y…, Gestiona las acciones de sincronización solicitadas desde el menú contextual de…

### Community 25 - "connection.py"
Cohesion: 0.12
Nodes (17): Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, init_db(), Crea las tablas necesarias si no existen., get_active_timer_tasks(), get_scheduled_tasks(), get_task_board_id(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve el board_id al que pertenece una tarea (o None si no existe). (+9 more)

### Community 26 - "RichTextToolbar"
Cohesion: 0.09
Nodes (13): _color_icon(), Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar, apply_text_color aplica el color especificado al texto seleccionado., Verifica que la barra de formato contiene todos los botones requeridos., Verifica alineaciones de texto (izq, centro, der, justificado) y sincronización… (+5 more)

### Community 27 - "TaskCard"
Cohesion: 0.10
Nodes (12): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, #102: `clicked` abre el detalle con exec() (bucle anidado); si mientras tanto…, test_task_card_click_handler_may_destroy_the_card(), test_task_card_ctrl_click_and_selection_state(), Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la…, Activa o desactiva el estado visual de selección múltiple., Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Umbral (en horas) a partir del cual la insignia del temporizador se resalta en… (+4 more)

### Community 28 - "BoardSyncUiMixin"
Cohesion: 0.08
Nodes (17): BoardSyncUiMixin, Maneja el clic en el botón de sincronización de la cabecera., Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para…, Compatibilidad hacia atrás: actualiza el controlador de sincronización., Compatibilidad hacia atrás: delega en sync_controller. (+9 more)

### Community 29 - "CalendarViewWidget"
Cohesion: 0.12
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 30 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 31 - "QFrame"
Cohesion: 0.18
Nodes (8): InteractiveTourBanner, Barra superior interactiva in-situ para guiar al usuario a través del tablero…, Aplica colores y refresca los textos según el idioma y tema actuales., QFrame, Verifica la navegación paso a paso, emisión de señales y finalización de…, Verifica que el botón cerrar descarte el tour y persista…, test_interactive_tour_banner_dismiss(), test_interactive_tour_banner_navigation_and_actions()

### Community 32 - ".show_command_palette"
Cohesion: 0.13
Nodes (7): Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o…, Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Inicia o reanuda el tour interactivo in-situ en el tablero demo '🚀 Primeros…, Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero., Desde el calendario: abrir el detalle y quedarnos en el calendario.

### Community 33 - "links.py"
Cohesion: 0.20
Nodes (9): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), get_task() (+1 more)

### Community 34 - "MainWindow"
Cohesion: 0.07
Nodes (14): MainWindow, Muestra el tour interactivo in-situ en el primer inicio si no se ha descartado., Manejador si el tablero actual cambió en el sidebar., Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Sincroniza inmediatamente el tablero activo con su archivo en la nube., Abre el diálogo para vincular el tablero activo a un nuevo archivo .ekboard., Abre la carpeta de logs de diagnóstico en el explorador de archivos. (+6 more)

### Community 35 - "templates.py"
Cohesion: 0.18
Nodes (15): apply_template_to_board(), BoardTemplate, ColumnTemplate, export_board_to_template(), get_builtin_templates(), Any, Motor de Plantillas de Tableros (Board Templates Engine) para Ekin Kanban.…, Retorna una lista de copias de las plantillas predefinidas de fábrica. (+7 more)

### Community 36 - "test_my_work_view.py"
Cohesion: 0.30
Nodes (11): bucket_scheduled_tasks(), Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, _iso(), _item_texts(), Pruebas de la vista "Mi trabajo" (my_work_view): - bucket_scheduled_tasks:…, _seed(), test_bucket_scheduled_tasks_groups_by_due(), test_bucket_scheduled_tasks_ignores_missing_due() (+3 more)

### Community 37 - "McpSyncDialog"
Cohesion: 0.19
Nodes (8): get_mcp_manager(), McpSyncDialog, QDialog, QPushButton, QTextEdit, Diálogo modal para configurar la sincronización de un tablero con agentes de IA…, Prueba el diálogo modal de configuración McpSyncDialog., test_mcp_sync_dialog_headless()

### Community 38 - "boards.py"
Cohesion: 0.10
Nodes (20): create_board(), delete_board(), get_board(), get_board_by_uuid(), get_board_mutation_fingerprint(), get_boards(), move_board(), Recuerda el pack del AI Prompt Clipboard elegido para el tablero. (+12 more)

### Community 39 - "test_mcp.py"
Cohesion: 0.07
Nodes (45): main(), Punto de entrada de línea de comandos (CLI) para MCP vía transporte STDIO.…, McpProtocolHandler, Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol., _done_and_other_columns(), Pruebas automatizadas para el Servidor MCP (Model Context Protocol), seguridad…, list_tasks no debe filtrar al agente el HTML/CSS de Qt (DOCTYPE, <style>, etc.)., list_tasks tenía un primer bucle muerto que repetía las consultas de cada… (+37 more)

### Community 40 - "main"
Cohesion: 0.13
Nodes (18): get_log_dir(), install_excepthook(), install_qt_message_handler(), Registro de diagnóstico y captura global de errores para Ekin. Escribe un log…, Directorio de logs (se crea si no existe): ~/.ekin/logs., Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del…, Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)., Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin. (+10 more)

### Community 41 - "DraggableColumnTitle"
Cohesion: 0.12
Nodes (5): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Etiqueta con el texto girado 90° (nombre de una columna plegada)., Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…, VerticalLabel

### Community 42 - "CalendarSettingsDialog"
Cohesion: 0.15
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 43 - ".contextMenuEvent"
Cohesion: 0.12
Nodes (11): format_single_cell(), format_table_all_cells(), Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen., Identifica si una tabla corresponde a un bloque de código. (+3 more)

### Community 44 - "SearchDialog"
Cohesion: 0.19
Nodes (8): Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon(), Verifica que SearchDialog liste tareas, filtre por texto/tablero y emita…, test_search_dialog_filters_and_activation()

### Community 45 - ".__init__"
Cohesion: 0.18
Nodes (6): QCheckBox, Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de…, Stepper −/+ genérico ligado a un QSpinBox de respaldo; muestra `valor suffix`., ToggleSwitch

### Community 46 - "SaveAsTemplateDialog"
Cohesion: 0.20
Nodes (6): QDialog, QFrame, Tarjeta interactiva para visualizar y seleccionar una plantilla de tablero., Diálogo modal para guardar el tablero actual como plantilla personalizada de…, SaveAsTemplateDialog, TemplateCardWidget

### Community 47 - "Any"
Cohesion: 0.17
Nodes (8): Any, _clean_text(), get_mcp_event_bus(), McpSecurityError, McpToolExecutor, Texto plano de un HTML de Qt (sin DOCTYPE/<style>), enmascarado si se pide., Ejecuta herramientas MCP garantizando que no se sobrepasen los límites del…, Excepción para violaciones de acceso, tokens inválidos o intentos fuera de…

### Community 48 - "McpManager"
Cohesion: 0.11
Nodes (8): McpHttpServer, McpManager, Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies., Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria., Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban., Prueba el servidor HTTP embebido realizando peticiones directas., test_mcp_http_server_live(), ThreadingHTTPServer

### Community 49 - "export_dialog.py"
Cohesion: 0.14
Nodes (11): ExportDialog, ImportConfirmationDialog, QDialog, Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Diálogo modal para confirmar la importación de tableros desde JSON., Genera una cadena amigable para nombres de archivo., Diálogo modal para configurar y ejecutar la exportación de tableros., _slugify() (+3 more)

### Community 50 - "sync.py"
Cohesion: 0.13
Nodes (14): get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero., Actualiza la marca de tiempo de sincronización y el hash del archivo., Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline. (+6 more)

### Community 51 - "summarize_diary_offline"
Cohesion: 0.40
Nodes (5): Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas)…, summarize_diary_offline(), Pruebas del resumen determinista del diario (local_ai.summarize_diary_offline),…, test_summarize_diary_offline_builds_two_sections(), test_summarize_diary_offline_empty()

### Community 52 - "test_templates.py"
Cohesion: 0.15
Nodes (22): create_board_from_template(), delete_custom_template(), get_all_templates(), get_custom_templates(), get_template_by_id(), get_templates_dir(), Devuelve la ruta al directorio donde se guardan las plantillas personalizadas…, Carga todas las plantillas de usuario personalizadas desde archivos JSON. (+14 more)

### Community 53 - "BoardSelectionMixin"
Cohesion: 0.21
Nodes (7): BoardSelectionMixin, Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej.…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero., Escape deselecciona tarjetas múltiples.

### Community 54 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 55 - "BulkAddTaskDialog"
Cohesion: 0.21
Nodes (6): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas…, test_bulk_add_task_dialog()

### Community 56 - "markdown_edit.py"
Cohesion: 0.09
Nodes (19): Utilidades compartidas para procesamiento y saneamiento de HTML en…, Diálogos modales para el editor enriquecido (bloques de código, enlaces,…, confirm_open_untrusted_link(), _get_target_extension(), _is_local_link(), _is_unc_path(), open_link_safely(), Utilidades de seguridad para la validación y apertura segura de hipervínculos y… (+11 more)

### Community 57 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 58 - "UndoManager"
Cohesion: 0.18
Nodes (9): Pruebas unitarias para UndoManager y UndoAction., test_undo_manager_initial_state(), test_undo_manager_max_depth(), test_undo_manager_push_clears_redo(), test_undo_manager_push_enables_can_undo(), test_undo_manager_undo_and_redo_lifecycle(), Pila simple de deshacer/rehacer para acciones destructivas (borrar…, UndoAction (+1 more)

### Community 59 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 60 - "QLabel"
Cohesion: 0.23
Nodes (7): MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon(), QLabel

### Community 61 - "FlowLayout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 62 - "test_reminders.py"
Cohesion: 0.23
Nodes (14): current_week_key(), Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, should_show_weekly_digest(), split_digest_tasks(), _iso(), Pruebas de recordatorios anticipados y resumen semanal (reminders.py): - lógica… (+6 more)

### Community 63 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 64 - "CreateBoardDialog"
Cohesion: 0.23
Nodes (3): CreateBoardDialog, Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o…, test_create_board_dialog_headless()

### Community 65 - "backup_database"
Cohesion: 0.24
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder(), test_backup_rapid_calls_never_collide() (+3 more)

### Community 66 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 67 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 68 - "detect_available_llm"
Cohesion: 0.16
Nodes (14): check_http_endpoint(), detect_available_llm(), get_ollama_models(), is_model_downloaded(), is_runner_installed(), Detecta qué servicio de LLM local está disponible en el equipo., Inicia en segundo plano el ejecutable portable llama-server con el modelo Qwen…, Verifica si el modelo Qwen 2.5 Coder existe localmente y no está vacío. (+6 more)

### Community 69 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 70 - "test_start_working.py"
Cohesion: 0.18
Nodes (18): build_launch(), (argv, prompt_por_portapapeles). Un shim .cmd/.bat (instalación npm) pasa por…, Ejecuta START WORKING para el tablero. Devuelve el id de la CLI abierta, o None…, start_working(), #87: START WORKING abre la CLI del agente en el directorio local del tablero,…, Enlazar el directorio cuesta un clic: Work lo pide si falta y sigue con START…, La cabecera se recortaba: el recuento, el MCP y la sync viven ahora en el pie…, _sw_board() (+10 more)

### Community 71 - ".__init__"
Cohesion: 0.20
Nodes (5): CalendarChip, QFrame, QPushButton, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes).

### Community 72 - ".open_board_config"
Cohesion: 0.17
Nodes (6): Abre el selector de archivo JSON y el diálogo de confirmación de importación., Abre el diálogo para editar el nombre y color del tablero activo., Abre el diálogo para copiar el tablero activo con un nuevo nombre., Archiva/desarchiva un tablero y recarga la lista., Abre el modal de opciones del tablero activo y ejecuta la acción elegida., Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo).

### Community 73 - "BoardButton"
Cohesion: 0.18
Nodes (6): BoardButton, Widget personalizado para representar un botón de tablero en la barra lateral., Arrastrar el tablero por la barra lateral para cambiar su orden., Línea de acento en el borde (superior o inferior) donde caerá el tablero., Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral., test_sidebar_board_button_cloud_badge()

### Community 74 - "LocalAiCircuitBreaker"
Cohesion: 0.15
Nodes (7): LocalAiCircuitBreaker, Disyuntor (Circuit Breaker) para el servicio local de inferencia y embeddings.…, Determina si se debe permitir el intento de llamada al servicio local de IA., Registra una respuesta satisfactoria del servicio local, cerrando el circuito., Registra un fallo o timeout del servicio local. Si supera el umbral, abre el…, Restablece manualmente el disyuntor al estado inicial CLOSED., test_local_ai_circuit_breaker_lifecycle()

### Community 75 - "test_incremental_rendering.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el renderizado incremental del tablero (mutaciones de…, Mover una tarea dentro de la misma columna solo debe reconstruir esa columna., Mover una tarea entre dos columnas solo debe reconstruir origen y destino,…, Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del…, create_quick_task solo debe reconstruir la columna de destino, preservando las…, add_task debe reconstruir solo la columna destino y actualizar el chip de…, test_add_task_incremental(), test_create_quick_task_incremental_rendering() (+3 more)

### Community 76 - "test_prompt_clipboard.py"
Cohesion: 0.20
Nodes (14): _dialog(), fixture, parametrize, #67: AI Prompt Clipboard por tablero (packs DEV / Opositor / GTD con el esquema…, test_boards_created_from_templates_get_their_prompt_pack(), test_builtin_packs_are_valid_and_target_the_board_mcp(), test_changing_pack_is_remembered_for_the_board(), test_copy_fills_board_vars_and_asks_for_the_rest() (+6 more)

### Community 77 - "test_local_ai.py"
Cohesion: 0.15
Nodes (16): download_and_extract_runner(), get_runner_download_url(), Devuelve la URL oficial de descarga del binario portable de llama-server según…, Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens…, Descarga y extrae el ejecutable portable de llama-server en runner_dir., stream_openai_chat_completion(), Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py)., Verifica que get_runner_download_url retorna una URL válida con terminación… (+8 more)

### Community 78 - ".__init__"
Cohesion: 0.17
Nodes (6): app_icon(), Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Arranca el servidor MCP; si el puerto sigue ocupado (p. ej. por la instancia…, Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo…

### Community 79 - ".handle_task_drop"
Cohesion: 0.20
Nodes (5): Maneja la recolocación en lote de múltiples tareas tras arrastrarlas., Soltar un lote de tarjetas sobre una columna plegada: la despliega y coloca las…, Registra una acción deshacer/rehacer para el movimiento (individual o en lote)…, Maneja la lógica de recolocación de tareas (individual o por lote) tras…, Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…

### Community 80 - "local_ai.py"
Cohesion: 0.13
Nodes (22): compute_fallback_embedding(), cosine_similarity(), find_duplicate_tasks(), get_llm_circuit_breaker(), get_local_embedding(), index_task_embedding(), is_ollama_available(), Módulo de IA Local de Ekin. Tras #60 su alcance queda acotado a: 1. Detección… (+14 more)

### Community 81 - "BoardViewWidget"
Cohesion: 0.07
Nodes (17): BoardViewWidget, Muestra la barra del tour interactivo in-situ y navega al paso especificado., Oculta la barra del tour interactivo in-situ., Muestra celebración tras completar los 4 pasos del tour interactivo., Monitorea mutaciones en la base de datos realizadas por agentes de IA vía MCP…, Inicia o reinicia el temporizador de debounce para recargar el tablero de forma…, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Espera a que termine cualquier hilo de sincronización activo antes de destruir… (+9 more)

### Community 82 - "PriorityManagerDialog"
Cohesion: 0.33
Nodes (3): PriorityManagerDialog, QDialog, Modal propio e independiente para gestionar los niveles y colores de Prioridad.…

### Community 83 - "t"
Cohesion: 0.10
Nodes (14): Refresca en vivo la tarea si otro (agente vía MCP, otro proceso, sync) la…, Elimina una entrada de diario tras confirmación., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Kicker de cabecera: TABLERO · COLUMNA (en mayúsculas). Se repinta en vivo si…, Vuelca en el formulario los campos editables de `task` y toma la foto con la…, Campos editables tal y como están ahora en el formulario., La tarea se borró fuera de este diálogo (agente, otro proceso, sync): avisar y…, Rellena el selector rápido de Prioridad con los valores actuales del catálogo… (+6 more)

### Community 84 - "test_column_roles.py"
Cohesion: 0.18
Nodes (16): classify_column(), column_roles(), Rol de cada columna en el flujo del tablero (backlog, ready, in_progress,…, Rol de una columna según su nombre; OTHER si ninguna palabra clave encaja., {column_id: rol} para las columnas de un tablero (en orden de `position`). Si…, _words(), parametrize, Pruebas del clasificador de roles de columna (column_roles.py) sobre las… (+8 more)

### Community 85 - "BoardEditDialog"
Cohesion: 0.24
Nodes (3): BoardEditDialog, Diálogo personalizado para crear o editar un tablero (nombre, color y, al…, test_board_edit_dialog_local_dir_row()

### Community 86 - ".render_tags"
Cohesion: 0.09
Nodes (12): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas (excluyendo Prioridad, que tiene…, Abre el modal propio e independiente de Prioridades., Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza. (+4 more)

### Community 87 - "LandingTourDialog"
Cohesion: 0.16
Nodes (8): Abre la guía de bienvenida y recorrido inicial de Ekin (modal de diapositivas)., LandingTourDialog, QDialog, Diálogo modal interactivo para guiar al usuario en las capacidades clave de…, Verifica la navegación paso a paso y la persistencia de LandingTourDialog., Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el…, test_landing_tour_dialog_dont_show_checkbox(), test_landing_tour_dialog_navigation_and_persistence()

### Community 88 - "ColumnWidget"
Cohesion: 0.16
Nodes (7): ColumnWidget, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada)., Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…

### Community 89 - "ColorCirclesPicker"
Cohesion: 0.06
Nodes (20): BoardColumnsArea, BoardSelectionDialog, ColumnEditDialog, QDialog, QWidget, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…, Diálogo para crear o editar una columna (nombre y color). (+12 more)

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
Cohesion: 0.21
Nodes (8): BaseHTTPRequestHandler, authenticate_and_get_board(), McpHttpHandler, Manejador HTTP para Server-Sent Events (SSE) y llamadas JSON-RPC directas., Envía cabeceras CORS restrictivas para evitar que sitios web maliciosos lean…, Maneja peticiones preflight CORS de clientes web o navegadores., Valida que el tablero exista, tenga MCP activado y que el token coincida si…, test_mcp_authentication_and_sandboxing()

### Community 97 - "board_ops.py"
Cohesion: 0.28
Nodes (8): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), move_column_to_board(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…, Mueve una columna a otro tablero y la coloca al final de su lista de columnas.

### Community 98 - "ics_sync.py"
Cohesion: 0.22
Nodes (8): delete_board_ics_sync_path(), get_all_board_ics_sync_paths(), get_board_ics_sync_path(), Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene., Crea o actualiza la ruta de auto-sync de un tablero., Desactiva la sincronización automática de un tablero., Devuelve {board_id: path} para todos los tableros con auto-sync configurado., set_board_ics_sync_path()

### Community 99 - "cli_tools.py"
Cohesion: 0.14
Nodes (14): CliTool, ensure_mcp_registered(), launch(), CLIs de agentes de IA que Ekin sabe lanzar desde un tablero (START WORKING):…, Actualiza la CLI. Devuelve (ok, mensaje). Nunca lanza: un fallo no debe…, Registra el servidor MCP del tablero en la CLI si aún no lo está. Devuelve (ok,…, Abre la CLI en una consola nueva (Windows Terminal si es la consola por…, _run() (+6 more)

### Community 100 - ".insertFromMimeData"
Cohesion: 0.14
Nodes (8): apply_word_style_to_qt_table(), Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Al pegar: archivos locales se insertan como enlaces y se emite señal para…, Inserta cada archivo local como enlace «📄 nombre» y emite local_link_pasted…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor con diseño estilo…, Codifica un QImage como data URI PNG en base64., Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se…

### Community 101 - "ImagePreviewDialog"
Cohesion: 0.18
Nodes (8): ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, QPixmap, Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog…, test_image_preview_dialog_is_destroyed_after_closing_when_parented(), test_image_preview_dialog_upscales_small_pixmap()

### Community 102 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 103 - "set_language"
Cohesion: 0.20
Nodes (11): get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), Verifica que CalendarViewWidget obtenga nombres de meses y días de la semana…, test_calendar_view_weekdays_and_months_localization() (+3 more)

### Community 104 - "BoardSyncWorker"
Cohesion: 0.25
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 105 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, Carga y conecta a la base de datos local un tablero sincronizado existente…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 106 - "SyncResult"
Cohesion: 0.14
Nodes (14): format_sync_summary(), Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Genera un resumen conciso de un SyncResult para mostrar en la interfaz., Exporta automáticamente los cambios locales si el tablero está vinculado., Resultado de una operación de sincronización. (+6 more)

### Community 107 - ".select_board"
Cohesion: 0.33
Nodes (3): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…

### Community 108 - "compute_drop_index"
Cohesion: 0.33
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una o varias tarjetas soltadas en `drop_y`.…

### Community 109 - "NotificationsPopup"
Cohesion: 0.11
Nodes (12): BoardConfigDialog, NotificationsPopup, QDialog, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…, Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos…, _swatch_icon() (+4 more)

### Community 110 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 111 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 112 - "show_image_preview"
Cohesion: 0.17
Nodes (12): pixmap_from_data_uri(), Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Verifica que pixmap_from_data_uri utilice QPixmapCache para data URIs base64., test_pixmap_from_data_uri_cache(), Regresión: antes href y src eran el MISMO data URI (la miniatura ya reducida al…, test_markdown_text_edit_stores_higher_res_copy_for_preview() (+4 more)

### Community 113 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 114 - "test_board_reorder.py"
Cohesion: 0.39
Nodes (8): _board_drop_event(), _names(), #58: reordenar tableros arrastrándolos en la barra lateral (persistido en…, test_board_button_ignores_drag_of_itself(), test_boards_created_after_a_reorder_go_last(), test_dropping_a_board_on_another_reorders_sidebar_and_db(), test_move_board_before_and_after_target_persists_order(), test_reorder_keeps_archived_boards_in_place()

### Community 115 - "TaskTimerMixin"
Cohesion: 0.32
Nodes (5): Manejo de estado y UI del temporizador de tareas para TaskDetailDialog., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Actualiza el botón y la etiqueta de tiempo transcurrido según…, TaskTimerMixin

### Community 116 - ".get_pending_notifications"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

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

### Community 127 - "cli_quota.py"
Cohesion: 0.22
Nodes (15): _command(), install_claude_statusline(), is_installed(), _load_settings(), _python_for_scripts(), quota_state(), Cuota restante de las CLIs de IA (#88). Claude Code la expone de forma…, Quita la status line de Ekin y restaura la que hubiera antes. (+7 more)

### Community 128 - "2. Implementation Tasks"
Cohesion: 0.09
Nodes (22): 0. Estado (2026-10-15, tras el OUTRO b063add), #101 — BUG: el servidor MCP no arranca al abrir Ekin  `[S]`, #102 — BUG: «TaskCard already deleted» al cerrar el detalle  `[S]`, 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, #74 — Respuestas MCP en inglés para ahorrar tokens  `[A: S · B: S · C: M]`, #81 — PWA Ekin Móvil  `[XL — épica]` (+14 more)

### Community 129 - "create_getting_started_board"
Cohesion: 0.50
Nodes (4): create_getting_started_board(), Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su…, Verifica que BoardViewWidget muestre y oculte el banner del tour según el…, test_board_view_interactive_tour_lifecycle()

### Community 130 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 131 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 132 - "DayCell"
Cohesion: 0.20
Nodes (5): DayCell, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon(), Verifica que _on_task_rescheduled actualice la fecha en la BD y emita…, test_calendar_view_on_task_rescheduled_and_drag_drop()

### Community 133 - ".apply_theme"
Cohesion: 0.15
Nodes (6): Aplica el tema (oscuro/claro) al vuelo. `reload` recarga el tablero para que…, Abre la pantalla de Ajustes (tema, notificaciones, idioma, updates, tour)., Arranca la versión nueva como proceso aparte y cierra esta de forma ordenada…, Verifica de forma silenciosa (o con feedback si manual=True) si hay…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica si hay actualizaciones en el repo de GitHub (modo git dev).

### Community 134 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 135 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 136 - "TaskDetailDialog"
Cohesion: 0.04
Nodes (31): Carga el siguiente lote de entradas anteriores del diario preservando la…, Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la…, Ancho máximo (px) para imágenes en las notas (panel izquierdo ancho)., Al pegar un enlace o archivo local en Notas o Diario, se añade automáticamente…, Lo que se ofrece al escribir «@»: los Enlaces / Adjuntos actuales de la tarea…, Crea una nueva entrada de diario con el texto del input. (+23 more)

### Community 138 - ".load_board"
Cohesion: 0.08
Nodes (11): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Ejecuta una recarga suave y segura del tablero cuando el agente de IA realiza…, Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Abre el diálogo para crear una columna., Confirma y borra una columna. (+3 more)

### Community 139 - "TableInsertDialog"
Cohesion: 0.12
Nodes (11): CodeBlockDialog, LinkDialog, QDialog, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para configurar e insertar una tabla con número inicial de filas…, Diálogo modal para insertar un enlace (URL)., TableInsertDialog, Abre el diálogo para insertar o editar un enlace web. (+3 more)

### Community 140 - "prompt_packs.py"
Cohesion: 0.10
Nodes (29): claude_code_server_name(), Nombre del servidor MCP del tablero en el comando `claude mcp add` (p. ej.…, board_variables(), fill_variables(), find_variables(), import_pack(), list_packs(), load_pack() (+21 more)

### Community 141 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 142 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 171 - "QWidget"
Cohesion: 0.16
Nodes (12): QWidget, QDialog, ShortcutsDialog, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Verifica que ShortcutsDialog carga y contiene los nuevos atajos de edición., Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/…, test_secondary_dialogs_schedule_delete_later_on_finished() (+4 more)

### Community 181 - "strings.py"
Cohesion: 0.08
Nodes (25): Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, board_mixins.py - Mixins modulares para BoardViewWidget. Separa la gestión de…, Diálogos para la selección, creación y gestión de plantillas de tableros en…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando… (+17 more)

### Community 185 - "_ClickOutsideFilter"
Cohesion: 0.25
Nodes (4): _ClickOutsideFilter, Mueve la barra de desplazamiento del diario hasta abajo., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo…, Filtro de eventos que detecta clics fuera del diálogo dentro de la ventana…

### Community 191 - "start_working.py"
Cohesion: 0.18
Nodes (8): detect_installed(), [(CliTool, ruta del ejecutable)] de las CLIs conocidas que están en el PATH., QThread, _pick_cli(), START WORKING (#87): desde un tablero con directorio local, arranca el servidor…, Los pasos lentos (update de la CLI y registro del MCP) fuera del hilo de la…, StartWorkingWorker, test_detect_installed_uses_the_path()

### Community 192 - "format_code_block_html"
Cohesion: 0.20
Nodes (9): format_code_block_html(), _get_warm_pygments_style(), Abre el diálogo para insertar un bloque de código formateado., Inserta un bloque de código formateado con resaltado de sintaxis., Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting() (+1 more)

### Community 195 - "test_priority_manager.py"
Cohesion: 0.27
Nodes (9): ensure_priority_category(), Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si…, Devuelve el id de la etiqueta permanente «Prioridad»., Pruebas unitarias para la independización de la categoría 'Priority' y su modal…, test_ensure_priority_category_creates_defaults(), test_priority_manager_dialog_crud(), test_tag_manager_dialog_excludes_priority(), test_tag_picker_dialog_excludes_priority() (+1 more)

### Community 196 - "mcp_server.py"
Cohesion: 0.11
Nodes (13): Exception, _DummySignal, get_mcp_tools_schema(), _masked(), McpEventBus, McpPermissionDenied, Servidor MCP (Model Context Protocol) para Ekin Kanban. Permite a agentes de IA…, Retorna la especificación JSON-Schema de las herramientas expuestas por Ekin… (+5 more)

### Community 197 - "SidebarWidget"
Cohesion: 0.13
Nodes (16): Persiste el nuevo orden y recoloca los botones sin recargar el tablero activo., SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir…, El fix del guard no debe bloquear el caso normal: con un tablero real…, test_add_column_shortcut_noop_when_no_board_selected() (+8 more)

### Community 198 - "TagPickerDialog"
Cohesion: 0.29
Nodes (4): QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog

### Community 199 - "test_local_ai_rdi.py"
Cohesion: 0.19
Nodes (12): format_daily_standup_markdown(), generate_daily_standup_data(), Extrae métricas y estado del flujo del tablero para generar el informe Daily…, Formatea la estructura de standup_data en un reporte Markdown elegante., _active(), _agile_board(), Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi: - Fase 1:…, #84: la tarea activa se resuelve en el servidor (In Progress → Review → Ready)… (+4 more)

### Community 200 - "_SseClientSession"
Cohesion: 0.29
Nodes (5): _SseClientSession, Verifica que el recolector de sesiones SSE elimine sesiones inactivas o…, Verifica el control de contrapresión y límite de cola en sesiones SSE., test_mcp_sse_send_to_session_queue_limit(), test_mcp_sse_session_scavenger()

### Community 201 - "task_mixins.py"
Cohesion: 0.33
Nodes (4): Mixins de funcionalidad modular para TaskDetailDialog (temporizadores,…, IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el…, Comprueba si existen tareas similares o duplicadas en este tablero., TaskAiMixin

### Community 206 - "._update_mention_popup"
Cohesion: 0.25
Nodes (3): Texto escrito tras un «@» que abre una mención (a inicio de línea o tras un…, Muestra, filtra u oculta el desplegable de menciones según el texto tras «@»., Sustituye «@texto» por un enlace al adjunto elegido («📄 nombre» o «🔗 nombre»);…

### Community 207 - "_collapsed_column_widget"
Cohesion: 0.36
Nodes (8): _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _task_drag_mime(), test_hover_timeout_emits_signal_only_while_collapsed(), test_hover_timer_starts_on_drag_enter(), test_hover_timer_stops_on_drag_leave(), test_hover_timer_stops_on_drop_before_timeout()

### Community 208 - "quota_popup.py"
Cohesion: 0.14
Nodes (13): QDialog, quota_dot_icon(), quota_lines(), QuotaPopup, Semáforo de cuota restante de las CLIs de IA (#88): el punto de color de la…, Icono del semáforo: un punto relleno del color del estado., Líneas legibles de la cuota restante de Claude Code (una por ventana vigente)., Detalle de la cuota por CLI instalada; permite activar o quitar la lectura de… (+5 more)

### Community 209 - "_mention_editor"
Cohesion: 0.40
Nodes (5): _mention_editor(), #63: «@» muestra los Enlaces / Adjuntos de la tarea y filtra con lo que se…, test_at_mention_ignores_emails_and_editors_without_provider(), test_at_mention_inserts_link_replacing_the_typed_mention(), test_at_mention_popup_filters_task_attachments()

### Community 211 - "_editor_with_all_selected"
Cohesion: 0.33
Nodes (6): _editor_with_all_selected(), #68: subrayado desde el botón «U» y con Ctrl+U / Ctrl+S (Subrayado en Word en…, #62: el botón «1.» convierte las líneas seleccionadas en una lista numerada., test_ctrl_shift_u_still_uppercases_not_underlines(), test_numbering_button_turns_selected_lines_into_numbered_list(), test_underline_button_and_shortcuts_toggle_underline()

### Community 217 - "test_concurrent_edit.py"
Cohesion: 0.18
Nodes (17): _card_of(), _close(), #103: edición concurrente de una tarjeta. Mientras el detalle está abierto, un…, Cierre nativo de la app (0xc0000005 en Qt6Widgets.dll, 2026-10-15): el detalle…, Escenario real del cierre: clic en la tarjeta → detalle abierto → un agente…, Prueba manual 2 de #103 (2026-10-15): con la hoja de estilos de la app, mostrar…, test_a_description_the_user_did_edit_still_wins(), test_click_outside_keeps_the_agents_changes() (+9 more)

### Community 218 - "test_cli_quota.py"
Cohesion: 0.20
Nodes (15): {"five_hour": {...}, "seven_day": {...}, "captured_at": ts} con las ventanas…, read_quota(), parametrize, home(), fixture, #88: semáforo de cuota restante de las CLIs de IA. Claude Code la expone en el…, _run_statusline(), test_quota_popup_offers_enabling_then_shows_the_quota() (+7 more)

### Community 219 - "test_last_active_column.py"
Cohesion: 0.31
Nodes (10): _make_board(), test_add_task_sets_last_active_column(), test_column_background_click_sets_last_active_column(), test_column_widget_mouse_press_emits_column_activated(), test_quick_add_task_falls_back_to_first_column_when_nothing_active(), test_quick_add_task_falls_back_when_last_active_column_belongs_to_another_board(), test_quick_add_task_falls_back_when_last_active_column_was_deleted(), test_quick_add_task_noop_with_no_board_selected() (+2 more)

### Community 220 - "hex_to_rgb"
Cohesion: 0.50
Nodes (4): contrast_text(), hex_to_rgb(), Tinta (#201e1d) sobre fondos claros, crema (#f5ead8) sobre fondos oscuros —…, Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b).

### Community 222 - "WeeklyDigestDialog"
Cohesion: 0.32
Nodes (4): QDialog, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, _swatch_icon(), WeeklyDigestDialog

### Community 223 - "_shown_expanded_column"
Cohesion: 0.50
Nodes (4): #59: un nombre largo no debe cortarse a mitad de carácter ni empujar los…, _shown_expanded_column(), test_column_title_elides_long_name_to_fit_header(), test_column_title_short_name_is_not_elided()

### Community 225 - "fixture"
Cohesion: 0.22
Nodes (9): fixture, board(), repo(), mcp_board(), Crea un tablero de prueba con MCP activado y columnas., flow(), no_real_quota(), Simula todo lo externo y registra lo que haría START WORKING. (+1 more)

### Community 230 - "sync_test_db"
Cohesion: 0.67
Nodes (3): fixture, Crea una base de datos temporal para pruebas de sincronización., sync_test_db()

## Knowledge Gaps
- **152 isolated node(s):** `CliTool`, `1. Overview`, `2. Implementation Tasks`, `3. Acceptance Criteria`, `QA Report` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `create_getting_started_board`, `test_main_window.py`, `DayCell`, `.apply_theme`, `test_widgets_headless.py`, `TaskDetailDialog`, `.load_board`, `DashboardWidget`, `._handle_key_press`, `BoardSyncController`, `PromptClipboardDialog`, `prompt_packs.py`, `lucide_icon`, `SettingsDialog`, `CommandPalette`, `LogEntryWidget`, `._rebuild_single_column`, `test_diary_viewer.py`, `.reload_boards`, `RichTextToolbar`, `TaskCard`, `BoardSyncUiMixin`, `CalendarViewWidget`, `QFrame`, `.show_command_palette`, `MainWindow`, `templates.py`, `McpSyncDialog`, `test_mcp.py`, `CalendarSettingsDialog`, `.contextMenuEvent`, `SearchDialog`, `.__init__`, `SaveAsTemplateDialog`, `QWidget`, `export_dialog.py`, `summarize_diary_offline`, `BoardSelectionMixin`, `strings.py`, `BulkAddTaskDialog`, `markdown_edit.py`, `QLabel`, `.delete_board`, `start_working.py`, `CreateBoardDialog`, `format_code_block_html`, `test_priority_manager.py`, `SidebarWidget`, `TagPickerDialog`, `.__init__`, `.open_board_config`, `task_mixins.py`, `BoardButton`, `test_start_working.py`, `.__init__`, `.handle_task_drop`, `quota_popup.py`, `BoardViewWidget`, `PriorityManagerDialog`, `BoardEditDialog`, `.render_tags`, `LandingTourDialog`, `ColumnWidget`, `ColorCirclesPicker`, `WeeklyDigestDialog`, `test_shortcuts_item_new_task_describes_last_active_column_behavior`, `ImagePreviewDialog`, `TagManagerDialog`, `set_language`, `SyncResult`, `NotificationsPopup`, `.mouseReleaseEvent`, `TaskTimerMixin`, `.notify_due_today`?**
  _High betweenness centrality (0.284) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `board_ops.py`, `ics_sync.py`, `links.py`, `test_local_dir.py`, `boards.py`, `tasks.py`, `export_dialog.py`, `sync.py`, `snapshots.py`, `connection.py`, `tags.py`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `BoardViewWidget` to `create_getting_started_board`, `.load_board`, `PromptClipboardDialog`, `._rebuild_single_column`, `test_diary_viewer.py`, `QFrame`, `test_mcp.py`, `strings.py`, `test_hover_expand.py`, `SidebarWidget`, `test_start_working.py`, `test_incremental_rendering.py`, `.__init__`, `.handle_task_drop`, `test_concurrent_edit.py`, `test_timer_board_view.py`, `test_last_active_column.py`, `cli_tools.py`, `test_wip_limit.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `t()` (e.g. with `test_installer_download_thread()` and `test_board_view_mcp_btn_states()`) actually correct?**
  _`t()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `BoardViewWidget` (e.g. with `test_board_view_mcp_btn_states()` and `_Runs`) actually correct?**
  _`BoardViewWidget` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `TaskDetailDialog` (e.g. with `.open_task_details()` and `._open_task_detail()`) actually correct?**
  _`TaskDetailDialog` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MarkdownTextEdit` (e.g. with `test_markdown_edit_case_conversions()` and `test_markdown_edit_image_resize_methods()`) actually correct?**
  _`MarkdownTextEdit` has 6 INFERRED edges - model-reasoned connections that need verification._