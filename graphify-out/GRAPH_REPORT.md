# Graph Report - Ekin  (2026-10-28)

## Corpus Check
- 163 files · ~232,780 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3135 nodes · 5892 edges · 243 communities (167 shown, 76 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 304 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e179a997`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- exporter.py
- _make_window
- test_ics_export.py
- MyWorkWidget
- TaskAiMixin
- test_board_sync.py
- MarkdownTextEdit
- tasks.py
- logs.py
- DashboardWidget
- DiaryViewerDialog
- McpHttpServer
- BoardSyncController
- TagManagerDialog
- SettingsDialog
- test_main_window.py
- TagPickerDialog
- CommandPalette
- LogEntryWidget
- /graphify Pipeline
- sync_board_with_file
- ._rebuild_single_column
- test_concurrent_edit.py
- .reload_boards
- get_task_tags_bulk
- RichTextToolbar
- ExportDialog
- BoardSyncUiMixin
- CalendarViewWidget
- tags.py
- lucide_icon
- .show_command_palette
- ColorCirclesPicker
- MainWindow
- get_builtin_templates
- ColumnEditDialog
- McpSyncDialog
- get_connection
- test_mcp.py
- main
- DraggableColumnTitle
- CalendarSettingsDialog
- .contextMenuEvent
- _remote_task
- clean_html_description
- test_prompt_clipboard.py
- Any
- McpManager
- .load_task_data
- sync.py
- mcp_server.py
- PromptClipboardDialog
- templates.py
- snapshots.py
- BulkAddTaskDialog
- styles.py
- test_hover_expand.py
- UndoAction
- Part B: Semantic Extraction (Subagents)
- InteractiveTourBanner
- FlowLayout
- test_reminders.py
- format_elapsed_time
- SaveAsTemplateDialog
- backup_database
- Release v0.6.0
- 2. Implementation Tasks
- _close_window
- CI Workflow (ruff + pytest)
- test_start_working.py
- ._handle_key_press
- SearchDialog
- BoardButton
- LocalAiCircuitBreaker
- test_incremental_rendering.py
- InstallerDownloadThread
- test_mcp_live_refresh.py
- test_local_dir.py
- SyncResult
- get_local_embedding
- BoardViewWidget
- t
- TaskDetailDialog
- test_column_roles.py
- privacy_shield.py
- .render_tags
- board_view.py
- ColumnWidget
- TaskCard
- test_timer_board_view.py
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- TECHNICAL DESIGN DOCUMENT
- _column_with_cards
- copy_board
- connection.py
- quota_popup.py
- ._insert_image
- prompt_packs.py
- .load_board
- BoardSyncWorker
- test_licensing.py
- connect_shared_board_from_file
- CreateBoardDialog
- build_qss
- TaskListArea
- ._rebuild_grid
- .init_ui
- WorkflowDialog
- QPixmap
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- test_batch_drag_drop.py
- test_release_notes.py
- test_board_reorder.py
- test_widgets_headless.py
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
- .__init__
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- DayCell
- .__init__
- Calendar Drag-to-Reschedule
- Cross-Repo Graph Merge
- ._update_local_dir_buttons
- _board_sync_lock
- create_getting_started_board
- strings.py
- .handle_task_drop
- get_subtasks_progress_bulk() Function
- v0.9.1: Local File Attachments on Task Links
- cli_tools.py
- extract_release_notes.py
- .reload_logs
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
- .__init__
- create_log() Atomicity Fix (Fix 6)
- Dead app.setStyleSheet() Removal (Fix 8)
- Stale Shortcuts Help Text Fix (Fix 3)
- timer_alert_hours N+1 Read Fix (Fix 7)
- open_shortcuts_requested Signal
- add_column() board_id==-1 Guard Fix
- backlog.md — Ekin Kanban Backlog
- Token Reduction Benchmark
- transcribe_all() Video/Audio Transcription
- CodeBlockDialog
- Ekin App Icon
- ekin-kanban
- board_variables
- Third-party notices
- BoardEditDialog
- QuotaPopup
- pixmap_from_data_uri
- TableInsertDialog
- .mouseReleaseEvent
- ._update_mention_popup
- .select_board
- test_unlink_board_sync
- test_sync_aborts_when_premerge_backup_fails
- SidebarWidget
- set_language
- test_local_ai_rdi.py
- NotificationsPopup
- TaskTimerMixin
- test_sync_initial_export_creates_file
- test_check_for_updates_ignores_untracked_files
- test_command_palette_cloud_and_calendar_dispatch
- test_downloaded_installer_runs_unattended_and_ekin_quits
- QThread
- LandingTourDialog
- WeeklyDigestDialog
- BoardConfigDialog
- _edit_remote_task
- .sync_ics
- test_database_sync_helpers_lifecycle
- test_connection_pooling_and_lifecycle
- test_fts5_search_and_triggers
- test_fts5_search_fallback_on_error
- test_update_task_positions_bumps_version_only_on_column_change
- ._check_external_mcp_mutations
- format_code_block_html
- .apply_theme
- ._change_list_indent
- is_ollama_available
- test_sync_imports_remote_changes_cleanly
- test_sync_collision_no_data_loss_preserves_in_journal
- claude_statusline.py
- conftest.py
- test_sync_concurrent_additions_both_preserved
- test_sync_corrupted_json_returns_error_safely
- test_premerge_backup_created_on_merge
- test_sync_remote_deletion_does_not_resurrect
- sync_test_db
- test_sync_exports_and_merges_structured_tags
- test_sync_board_with_file_catches_unresolved_lock
- test_get_board_by_uuid
- test_get_board_last_local_modified
- test_sync_up_to_date_when_no_changes
- test_sync_exports_local_changes_to_file
- user_packs_dir
- QDialog
- QObject
- parametrize
- QFrame
- QWidget

## God Nodes (most connected - your core abstractions)
1. `t()` - 273 edges
2. `BoardViewWidget` - 133 edges
3. `TaskDetailDialog` - 116 edges
4. `get_connection()` - 109 edges
5. `MarkdownTextEdit` - 94 edges
6. `MainWindow` - 55 edges
7. `SidebarWidget` - 53 edges
8. `lucide_icon()` - 53 edges
9. `TaskCard` - 40 edges
10. `McpProtocolHandler` - 39 edges

## Surprising Connections (you probably didn't know these)
- `test_is_local_link_classifies_urls_vs_paths()` --calls--> `_is_local_link()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `test_is_unc_path_detection()` --calls--> `_is_unc_path()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `test_task_detail_dialog_click_inside_does_not_close()` --calls--> `TaskDetailDialog`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/task_detail_dialog.py
- `test_task_detail_dialog_click_outside_auto_saves_and_closes()` --calls--> `TaskDetailDialog`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/task_detail_dialog.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (243 total, 76 thin omitted)

### Community 1 - "exporter.py"
Cohesion: 0.10
Nodes (31): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas., Convierte HTML (descripción/nota) en texto plano limpio para exportar., Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags,…, Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como… (+23 more)

### Community 2 - "_make_window"
Cohesion: 0.16
Nodes (18): _FakeMcpManager, _make_task_on_board(), _make_window(), Gestor MCP simulado: ningún test debe abrir el puerto 8765 real (#101)., Construye una MainWindow apta para tests: __init__ agenda dos QTimer.singleShot…, Regresión: editar una tarea desde el Calendario dejaba la tarjeta del tablero…, #101: el servidor MCP solo arrancaba al guardar el diálogo MCP; tras cada…, #106: al reiniciar tras actualizarse, la instancia anterior puede tener aún el… (+10 more)

### Community 3 - "test_ics_export.py"
Cohesion: 0.11
Nodes (28): build_ics(), _escape(), export_ics(), _fold_line(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar. (+20 more)

### Community 4 - "MyWorkWidget"
Cohesion: 0.19
Nodes (15): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _iso(), _item_texts() (+7 more)

### Community 5 - "TaskAiMixin"
Cohesion: 0.50
Nodes (3): IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el…, Comprueba si existen tareas similares o duplicadas en este tablero., TaskAiMixin

### Community 6 - "test_board_sync.py"
Cohesion: 0.24
Nodes (9): _all_titles(), Verifica que en una fusión bidireccional concurrente, las etiquetas de ambas…, Verifica que get_synced_boards refleja adecuadamente la vinculación y…, #123: tras escribir el archivo, la sync marcaba como sincronizadas TODAS las…, #123: la importación sin cambios locales decidía con una foto tomada antes y…, test_get_synced_boards_lifecycle(), test_local_changes_made_while_importing_are_not_overwritten_or_deleted(), test_sync_two_way_merge_combines_tags() (+1 more)

### Community 7 - "MarkdownTextEdit"
Cohesion: 0.04
Nodes (41): MarkdownTextEdit, QTextEdit, Inserta cada archivo local como enlace «📄 nombre» y emite local_link_pasted…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Aplica interlineado proporcional (por defecto 135%) a todos los bloques del…, Verifica que escribir en una cita con placeholder borra el placeholder… (+33 more)

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
Nodes (26): Abre los diarios de desarrollo y demás .md / .txt del directorio local., DiaryViewerDialog, doc_files(), has_doc_files(), _iter_doc_files(), QDialog, Visor de solo lectura de los diarios de desarrollo (`diary.md`,…, Índice de la pestaña de `rel_path`, que se crea (y se lee) si aún no estaba… (+18 more)

### Community 12 - "McpHttpServer"
Cohesion: 0.18
Nodes (4): McpHttpServer, Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies., Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria., ThreadingHTTPServer

### Community 13 - "BoardSyncController"
Cohesion: 0.09
Nodes (18): BoardSyncController, QObject, Configura el watcher para detectar reactivamente cambios externos., Disparado por el sistema de archivos ante modificaciones externas., Desvincula el tablero actual de su archivo compartido., Espera a que termine cualquier hilo de sincronización en ejecución., Devuelve True si hay una sincronización en segundo plano activa., Controlador de sincronización autónomo para un tablero Kanban. Emite señales de… (+10 more)

### Community 14 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 15 - "SettingsDialog"
Cohesion: 0.10
Nodes (14): QDialog, Pestaña Directorios locales: cada tablero con su carpeta (repo), con Examinar y…, Segmentado English / Español que maneja el lang_combo de respaldo., Segmentado Light / Dark que maneja el theme_combo de respaldo., SettingsDialog, Verifica que el botón 'Buscar ahora' en ajustes emita check_updates_requested., Verifica que el botón de Tour Interactivo en Ajustes emita…, test_settings_dialog_check_updates_button_emits_signal() (+6 more)

### Community 16 - "test_main_window.py"
Cohesion: 0.12
Nodes (19): parse_version_tuple(), Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, ReleaseCheckThread, QThread, Pruebas headless para MainWindow (main.py): comportamientos que solo existen a…, La v1.9.0 es el puente (#228): las copias instaladas buscan releases en Txek-…, Mientras el repo nuevo no tenga releases, la API responde 404: error, nunca una…, Verifica que ReleaseCheckThread emita no_update_available si está al día. (+11 more)

### Community 17 - "TagPickerDialog"
Cohesion: 0.12
Nodes (14): ensure_priority_category(), Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si…, QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog, Devuelve el id de la etiqueta permanente «Prioridad»., Rellena el selector rápido de Prioridad con los valores actuales del catálogo… (+6 more)

### Community 18 - "CommandPalette"
Cohesion: 0.16
Nodes (11): CommandPalette, QDialog, Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, Verifica que CommandPalette no tenga WA_DeleteOnClose activo y no sufra…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query(), test_palette_lists_all_commands_when_empty() (+3 more)

### Community 19 - "LogEntryWidget"
Cohesion: 0.12
Nodes (13): LogEntryWidget, QFrame, Sustituye el contenido por un editor en línea con Guardar/Cancelar y soporte de…, Una entrada del diario/chat, con botones (pintados) de editar y eliminar y…, Cancela la edición volviendo al estado de lectura de forma instantánea y sin…, Guarda la edición del comentario invocando el callback., Limpia los widgets temporales de edición y reactiva la etiqueta de lectura., Maneja los enlaces clicados dentro de una entrada ya enviada (imágenes, URLs… (+5 more)

### Community 20 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 21 - "sync_board_with_file"
Cohesion: 0.08
Nodes (32): _apply_remote_board_clean(), calculate_file_hash(), create_premerge_backup(), _execute_two_way_merge(), export_board_to_sync_dict(), _merge_fields(), _merge_task_fields(), _merge_task_sub_entities() (+24 more)

### Community 22 - "._rebuild_single_column"
Cohesion: 0.11
Nodes (10): Maneja las acciones interactivas directas asociadas a cada paso del tour., Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de…, Atajo Ctrl+N: añade una tarea a la última columna con la que se ha interactuado… (+2 more)

### Community 23 - "test_concurrent_edit.py"
Cohesion: 0.18
Nodes (17): _card_of(), _close(), #103: edición concurrente de una tarjeta. Mientras el detalle está abierto, un…, Cierre nativo de la app (0xc0000005 en Qt6Widgets.dll, 2026-10-15): el detalle…, Escenario real del cierre: clic en la tarjeta → detalle abierto → un agente…, Prueba manual 2 de #103 (2026-10-15): con la hoja de estilos de la app, mostrar…, test_a_description_the_user_did_edit_still_wins(), test_click_outside_keeps_the_agents_changes() (+9 more)

### Community 24 - ".reload_boards"
Cohesion: 0.10
Nodes (12): Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo)., Abre el selector de archivo JSON y el diálogo de confirmación de importación., Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero a partir de una plantilla o en…, Abre el diálogo para editar el nombre y color del tablero activo., Confirma y elimina el tablero activo., Registra deshacer/rehacer del borrado de un tablero (restaurar desde snapshot)., Vuelve a cargar la lista de tableros como widgets personalizados desde la base… (+4 more)

### Community 25 - "get_task_tags_bulk"
Cohesion: 0.18
Nodes (14): get_active_timer_tasks(), get_scheduled_tasks(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.…, Sanea el texto de búsqueda para FTS5 generando términos con comodín de prefijo., Búsqueda de texto completo de alto rendimiento con FTS5 y ordenación por…, Búsqueda tradicional mediante SQL LIKE utilizada cuando no hay texto o como…, Busca tareas en todos los tableros (o en uno) con filtros opcionales. Utiliza… (+6 more)

### Community 26 - "RichTextToolbar"
Cohesion: 0.09
Nodes (14): _color_icon(), QWidget, Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar, apply_text_color aplica el color especificado al texto seleccionado., Verifica que la barra de formato contiene todos los botones requeridos. (+6 more)

### Community 27 - "ExportDialog"
Cohesion: 0.21
Nodes (7): ExportDialog, ImportConfirmationDialog, QDialog, Diálogo modal para confirmar la importación de tableros desde JSON., Diálogo modal para configurar y ejecutar la exportación de tableros., test_export_dialog_initial_state_and_toggles(), test_import_confirmation_dialog_initial_state()

### Community 28 - "BoardSyncUiMixin"
Cohesion: 0.18
Nodes (8): BoardSyncUiMixin, Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para…, Gestiona el diálogo de resultado cuando la sincronización es manual., Exporta cambios locales en segundo plano delegando en el controlador., Maneja el clic en el botón de sincronización de la cabecera.

### Community 29 - "CalendarViewWidget"
Cohesion: 0.13
Nodes (12): CalendarViewWidget, _group_by_day(), Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Devuelve el nombre del mes (1..12) según el idioma activo., Devuelve el nombre del día de la semana (0..6) según el idioma activo., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 30 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 31 - "lucide_icon"
Cohesion: 0.10
Nodes (14): Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando…, lucide_icon(), lucide_pixmap(), Iconos Lucide coloreados por estado. Los SVG de Lucide usan… (+6 more)

### Community 32 - ".show_command_palette"
Cohesion: 0.13
Nodes (7): Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o…, Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Inicia o reanuda el tour interactivo in-situ en el tablero demo '🚀 Primeros…, Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero., Desde el calendario: abrir el detalle y quedarnos en el calendario.

### Community 33 - "ColorCirclesPicker"
Cohesion: 0.13
Nodes (10): ColorCirclesPicker, _ColorDot, _CustomDot, QWidget, Fija el color activo (añadiendo el círculo si no existía)., Círculo punteado con «+» que abre el selector de color libre., Fila de círculos de color con selección única y opción de color personalizado., QAbstractButton (+2 more)

### Community 34 - "MainWindow"
Cohesion: 0.07
Nodes (14): MainWindow, Muestra el tour interactivo in-situ en el primer inicio si no se ha descartado., Manejador si el tablero actual cambió en el sidebar., Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., Sincroniza inmediatamente el tablero activo con su archivo en la nube., Abre el diálogo para vincular el tablero activo a un nuevo archivo .ekboard. (+6 more)

### Community 35 - "get_builtin_templates"
Cohesion: 0.40
Nodes (5): get_builtin_templates(), Retorna una lista de copias de las plantillas predefinidas de fábrica., #136: SW → DEV, Opositor → Socrático (cualquier estudio), Personal/GTD → GTD.…, test_builtin_board_types_are_dev_socratic_and_gtd(), test_builtin_templates_exist()

### Community 36 - "ColumnEditDialog"
Cohesion: 0.09
Nodes (12): BoardColumnsArea, BoardSelectionDialog, ColumnEditDialog, QDialog, QWidget, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…, Diálogo para crear o editar una columna (nombre y color). (+4 more)

### Community 37 - "McpSyncDialog"
Cohesion: 0.18
Nodes (7): Actualiza el estado visual del botón MCP en la cabecera del tablero., Abre el diálogo modal de configuración MCP para el tablero actual., McpSyncDialog, QDialog, QPushButton, QTextEdit, Diálogo modal para configurar la sincronización de un tablero con agentes de IA…

### Community 38 - "get_connection"
Cohesion: 0.10
Nodes (31): create_board(), delete_board(), get_board(), get_board_by_uuid(), get_board_mutation_fingerprint(), get_boards(), move_board(), Recuerda el pack del AI Prompt Clipboard elegido para el tablero. (+23 more)

### Community 39 - "test_mcp.py"
Cohesion: 0.04
Nodes (70): get_mcp_tools_schema(), McpProtocolHandler, Retorna la especificación JSON-Schema de las herramientas expuestas por Ekin…, Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol., board(), fixture, _done_and_other_columns(), mcp_board() (+62 more)

### Community 40 - "main"
Cohesion: 0.13
Nodes (18): get_log_dir(), install_excepthook(), install_qt_message_handler(), Registro de diagnóstico y captura global de errores para Ekin. Escribe un log…, Directorio de logs (se crea si no existe): ~/.ekin/logs., Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del…, Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)., Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin. (+10 more)

### Community 41 - "DraggableColumnTitle"
Cohesion: 0.11
Nodes (5): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Etiqueta con el texto girado 90° (nombre de una columna plegada)., Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…, VerticalLabel

### Community 42 - "CalendarSettingsDialog"
Cohesion: 0.14
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 43 - ".contextMenuEvent"
Cohesion: 0.12
Nodes (11): format_single_cell(), format_table_all_cells(), Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen., Identifica si una tabla corresponde a un bloque de código. (+3 more)

### Community 44 - "_remote_task"
Cohesion: 0.22
Nodes (9): #97: mover una tarjeta de columna cuenta como cambio local. Antes no subía…, #97: un movimiento local sin cambios remotos se exporta sin contarse como…, #97: la fusión bidireccional comparaba el column_uuid remoto con uno local que…, #97: si en local se mueve la tarjeta y en remoto (más reciente) se edita su…, _remote_task(), test_field_merge_keeps_local_move_and_newer_remote_title(), test_sync_local_move_survives_older_remote_edit(), test_sync_local_move_without_remote_changes_is_not_a_conflict() (+1 more)

### Community 45 - "clean_html_description"
Cohesion: 0.14
Nodes (22): clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, author_entry_html(), markdown_to_qt_html(), migrate_plain_text_content(), Conversión a HTML de Qt del Markdown / texto plano que envían los agentes por…, Fragmento HTML de Qt para `text`. Lo que ya es HTML (empieza por una etiqueta)… (+14 more)

### Community 46 - "test_prompt_clipboard.py"
Cohesion: 0.16
Nodes (19): load_pack(), _dialog(), #67: AI Prompt Clipboard por tablero (packs DEV / Opositor / GTD con el esquema…, #84: los prompts DEV adivinaban columnas por posición ("the column right after…, #111: INITIAL y MIGRATE mandaban `graphify build` y `graphifyy claude`, que no…, #111: AUDIT guardaba todos los hallazgos para un único `create_tasks_batch`…, #136: el pack daba las respuestas (tests, esquemas, dudas) y era solo para…, test_audit_findings_reach_remediate_through_tagged_cards() (+11 more)

### Community 47 - "Any"
Cohesion: 0.13
Nodes (14): Exception, _check_due(), _clean_text(), get_mcp_event_bus(), McpPermissionDenied, McpSecurityError, McpToolExecutor, Any (+6 more)

### Community 48 - "McpManager"
Cohesion: 0.11
Nodes (15): McpManager, Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban., _free_port(), #115: sin timeout de socket, un cliente que anuncia un cuerpo y no lo envía…, Prueba el servidor HTTP embebido realizando peticiones directas., #107: en Windows, SO_REUSEADDR dejaba que un segundo Ekin se enlazara al 8765…, Lee eventos SSE (líneas `event:` / `data:`) hasta el primero de tipo `wanted`;…, #121: Claude Code se registra por SSE, pero solo /health y /rpc tenían tests.… (+7 more)

### Community 49 - ".load_task_data"
Cohesion: 0.09
Nodes (11): Refresca en vivo la tarea si otro (agente vía MCP, otro proceso, sync) la…, Al pegar un enlace o archivo local en Notas o Diario, se añade automáticamente…, Habilita/inhabilita fecha y hora según los checks., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Kicker de cabecera: TABLERO · COLUMNA (en mayúsculas). Se repinta en vivo si…, Vuelca en el formulario los campos editables de `task` y toma la foto con la…, Campos editables tal y como están ahora en el formulario., Los mismos campos que _form_state(), con los valores guardados en la base de… (+3 more)

### Community 50 - "sync.py"
Cohesion: 0.13
Nodes (14): get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero., Actualiza la marca de tiempo de sincronización y el hash del archivo., Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline. (+6 more)

### Community 51 - "mcp_server.py"
Cohesion: 0.07
Nodes (23): BaseHTTPRequestHandler, main(), Punto de entrada de línea de comandos (CLI) para MCP vía transporte STDIO.…, authenticate_and_get_board(), _DummySignal, _masked(), McpEventBus, McpHttpHandler (+15 more)

### Community 52 - "PromptClipboardDialog"
Cohesion: 0.16
Nodes (9): Abre el AI Prompt Clipboard con el pack de prompts del tablero activo., ask_variable_values(), PromptClipboardDialog, QDialog, AI Prompt Clipboard del tablero: los prompts del pack del tablero (DEV,…, Copia el prompt seleccionado con las variables del tablero; pide las que falten., Pide el valor de cada variable {{...}} pendiente. Devuelve {nombre: valor}, o…, Modal con el pack de prompts del tablero: filtro por categoría, búsqueda, vista… (+1 more)

### Community 53 - "templates.py"
Cohesion: 0.11
Nodes (34): apply_template_to_board(), BoardTemplate, ColumnTemplate, create_board_from_template(), delete_custom_template(), export_board_to_template(), get_all_templates(), get_custom_templates() (+26 more)

### Community 54 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 55 - "BulkAddTaskDialog"
Cohesion: 0.20
Nodes (6): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas…, test_bulk_add_task_dialog()

### Community 56 - "styles.py"
Cohesion: 0.05
Nodes (55): Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, Diálogos para la selección, creación y gestión de plantillas de tableros en…, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, apply_word_style_to_qt_table(), clear_fit_html_cache(), fit_html_images(), _is_network_target(), linkify_urls() (+47 more)

### Community 57 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 58 - "UndoAction"
Cohesion: 0.18
Nodes (9): Pruebas unitarias para UndoManager y UndoAction., test_undo_manager_initial_state(), test_undo_manager_max_depth(), test_undo_manager_push_clears_redo(), test_undo_manager_push_enables_can_undo(), test_undo_manager_undo_and_redo_lifecycle(), Pila simple de deshacer/rehacer para acciones destructivas (borrar…, UndoAction (+1 more)

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

### Community 64 - "SaveAsTemplateDialog"
Cohesion: 0.22
Nodes (5): QDialog, Tarjeta interactiva para visualizar y seleccionar una plantilla de tablero., Diálogo modal para guardar el tablero actual como plantilla personalizada de…, SaveAsTemplateDialog, TemplateCardWidget

### Community 65 - "backup_database"
Cohesion: 0.24
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder(), test_backup_rapid_calls_never_collide() (+3 more)

### Community 66 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 67 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 68 - "_close_window"
Cohesion: 0.12
Nodes (16): _close_window(), Verifica que el título de la ventana principal es 'Ekin vX.X.X'., Verifica que modificaciones en archivos rastreados sí detienen la actualización…, #228: hasta que el repo nuevo publique la v2.0.0 la API responde 404. La…, Cierra y destruye la ventana de verdad (deleteLater + procesar el evento…, Verifica que check_for_updates(manual=True) muestre diálogo informativo si ya…, Verifica que tanto Ctrl+0 como Ctrl+O estén registrados como atajos para abrir…, #137: el diagrama del flujo de trabajo con IA se abre desde la paleta de… (+8 more)

### Community 69 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 70 - "test_start_working.py"
Cohesion: 0.08
Nodes (34): build_launch(), detect_installed(), [(CliTool, ruta del ejecutable)] de las CLIs conocidas que están en el PATH., (argv, prompt_por_portapapeles). Un shim .cmd/.bat (instalación npm) pasa por…, get_mcp_manager(), _pick_cli(), QThread, START WORKING (#87): desde un tablero con directorio local, arranca el servidor… (+26 more)

### Community 71 - "._handle_key_press"
Cohesion: 0.09
Nodes (11): Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Alinea el bloque de texto actual o selección a la izquierda., Centra el bloque de texto actual o selección., Alinea el bloque de texto actual o selección a la derecha., Justifica el bloque de texto actual o selección., Convierte el texto seleccionado (o la palabra bajo el cursor) a MAYÚSCULAS., Convierte el texto seleccionado (o la palabra bajo el cursor) a minúsculas. (+3 more)

### Community 72 - "SearchDialog"
Cohesion: 0.25
Nodes (6): QDialog, Diálogo de búsqueda global de tareas. Filtra por texto (título/descripción),…, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon()

### Community 73 - "BoardButton"
Cohesion: 0.18
Nodes (6): BoardButton, Widget personalizado para representar un botón de tablero en la barra lateral., Arrastrar el tablero por la barra lateral para cambiar su orden., Línea de acento en el borde (superior o inferior) donde caerá el tablero., Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral., test_sidebar_board_button_cloud_badge()

### Community 74 - "LocalAiCircuitBreaker"
Cohesion: 0.15
Nodes (7): LocalAiCircuitBreaker, Disyuntor (Circuit Breaker) para el servicio local de inferencia y embeddings.…, Determina si se debe permitir el intento de llamada al servicio local de IA., Registra una respuesta satisfactoria del servicio local, cerrando el circuito., Registra un fallo o timeout del servicio local. Si supera el umbral, abre el…, Restablece manualmente el disyuntor al estado inicial CLOSED., test_local_ai_circuit_breaker_lifecycle()

### Community 75 - "test_incremental_rendering.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el renderizado incremental del tablero (mutaciones de…, Mover una tarea dentro de la misma columna solo debe reconstruir esa columna., Mover una tarea entre dos columnas solo debe reconstruir origen y destino,…, Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del…, create_quick_task solo debe reconstruir la columna de destino, preservando las…, add_task debe reconstruir solo la columna destino y actualizar el chip de…, test_add_task_incremental(), test_create_quick_task_incremental_rendering() (+3 more)

### Community 76 - "InstallerDownloadThread"
Cohesion: 0.15
Nodes (9): installer_sha256_from_notes(), InstallerDownloadThread, SHA-256 del instalador según la línea «SHA-256: <hash>» que el workflow de…, Muestra confirmación al usuario y descarga el instalador si acepta., #117: el actualizador buscaba cualquier hex de 64 en las notas, y la release no…, test_installer_download_thread(), test_installer_download_thread_cancelled_removes_incomplete_file(), test_installer_download_thread_sha256_verification() (+1 more)

### Community 77 - "test_mcp_live_refresh.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el refresco automático del tablero y diálogo de tareas…, Verifica que si TaskDetailDialog está abierto, se actualice en tiempo real…, Verifica que PRAGMA data_version y la huella digital del tablero detecten…, #125: la recarga tras un cambio del agente usaba notify=False, así que…, Verifica que BoardViewWidget detecte la escritura de un agente MCP externo y…, Verifica que emitir board_mutated en el bus de eventos desencadene la recarga…, test_board_view_auto_detects_external_mcp_mutation(), test_board_view_mcp_event_bus_trigger() (+3 more)

### Community 78 - "test_local_dir.py"
Cohesion: 0.18
Nodes (16): list_repo_files(), Archivos del directorio local (repo) asociado a un tablero, para ofrecerlos en…, Rutas relativas (con «/») de los archivos de `root`, como mucho `limit`., _board_with_task(), _cleanup(), fixture, #85: un tablero puede asociarse a un directorio local (repo): el agente de IA…, repo() (+8 more)

### Community 79 - "SyncResult"
Cohesion: 0.14
Nodes (14): format_sync_summary(), Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Genera un resumen conciso de un SyncResult para mostrar en la interfaz., Exporta automáticamente los cambios locales si el tablero está vinculado., Resultado de una operación de sincronización. (+6 more)

### Community 80 - "get_local_embedding"
Cohesion: 0.15
Nodes (17): compute_fallback_embedding(), cosine_similarity(), find_duplicate_tasks(), get_llm_circuit_breaker(), get_local_embedding(), index_task_embedding(), Obtiene la instancia global del Circuit Breaker para el servicio local de IA., Genera un vector denso determinista y normalizado a partir de n-gramas de… (+9 more)

### Community 81 - "BoardViewWidget"
Cohesion: 0.08
Nodes (22): BoardViewWidget, QFrame, Muestra la barra del tour interactivo in-situ y navega al paso especificado., Oculta la barra del tour interactivo in-situ., Muestra celebración tras completar los 4 pasos del tour interactivo., Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Espera a que termine cualquier hilo de sincronización activo antes de destruir…, Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar). (+14 more)

### Community 82 - "t"
Cohesion: 0.12
Nodes (16): PriorityManagerDialog, QDialog, Modal propio e independiente para gestionar los niveles y colores de Prioridad.…, QWidget, QLabel, QDialog, ShortcutsDialog, Returns the localized string for `key`, falling back to English if missing. (+8 more)

### Community 83 - "TaskDetailDialog"
Cohesion: 0.05
Nodes (54): Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la…, Ancho máximo (px) para imágenes en las notas (panel izquierdo ancho)., Lo que se ofrece al escribir «@»: los Enlaces / Adjuntos actuales de la tarea…, Borra definitivamente la tarea actual de la base de datos., TaskDetailDialog, TaskAiMixin, TaskTimerMixin (+46 more)

### Community 84 - "test_column_roles.py"
Cohesion: 0.16
Nodes (17): classify_column(), column_roles(), Rol de cada columna en el flujo del tablero (backlog, ready, in_progress,…, Rol de una columna según su nombre; OTHER si ninguna palabra clave encaja., {column_id: rol} para las columnas de un tablero (en orden de `position`). Si…, _words(), parametrize, Pruebas del clasificador de roles de columna (column_roles.py) sobre las… (+9 more)

### Community 85 - "privacy_shield.py"
Cohesion: 0.22
Nodes (9): has_sensitive_data(), Escudo de Privacidad Local para Ekin Kanban. Filtra, sanitiza y protege…, Sanitiza el texto eliminando tokens sensibles y credenciales. Devuelve…, Comprueba rápidamente si un texto contiene algún patrón confidencial., sanitize_text(), parametrize, #118: mask_sensitive dejaba pasar tokens fine-grained de GitHub, claves de…, test_privacy_shield_masks_more_secret_formats() (+1 more)

### Community 86 - ".render_tags"
Cohesion: 0.09
Nodes (12): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas (excluyendo Prioridad, que tiene…, Abre el modal propio e independiente de Prioridades., Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza. (+4 more)

### Community 87 - "board_view.py"
Cohesion: 0.10
Nodes (17): BoardMcpUiMixin, BoardSelectionMixin, board_mixins.py - Mixins modulares para BoardViewWidget. Separa la gestión de…, Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej.…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero. (+9 more)

### Community 88 - "ColumnWidget"
Cohesion: 0.15
Nodes (8): test_column_widget_mouse_press_emits_column_activated(), ColumnWidget, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada)., Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…

### Community 89 - "TaskCard"
Cohesion: 0.08
Nodes (17): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, #109: los agentes citan las tarjetas por su id (#108...); la tarjeta lo…, #102: `clicked` abre el detalle con exec() (bucle anidado); si mientras tanto…, test_task_card_click_handler_may_destroy_the_card(), test_task_card_ctrl_click_and_selection_state(), test_task_card_shows_its_id_next_to_the_title(), test_task_list_area_drop_indicator(), Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la… (+9 more)

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

### Community 96 - "_column_with_cards"
Cohesion: 0.29
Nodes (8): _assert_cards_fit_the_column(), _column_with_cards(), #132: la columna alineaba sus tarjetas arriba (AlignTop) y, con esa alineación,…, #132: la fila de fecha + hora + temporizador + tablero enlazado no podía…, #132: una palabra sin espacios (ruta, snake_case) no tenía dónde partirse:…, test_task_card_title_breaks_long_paths_and_identifiers(), test_task_card_titles_get_the_height_they_need_in_a_column(), test_task_cards_fit_the_column_width()

### Community 97 - "copy_board"
Cohesion: 0.33
Nodes (6): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…

### Community 98 - "connection.py"
Cohesion: 0.06
Nodes (33): move_column_to_board(), Mueve una columna a otro tablero y la coloca al final de su lista de columnas., close_cached_connections(), get_db_data_version(), get_default_db_path(), Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, Devuelve el contador interno PRAGMA data_version de SQLite. Permite detectar…, Cierra y purga las conexiones abiertas en el hilo actual para db_path (o todas). (+25 more)

### Community 99 - "quota_popup.py"
Cohesion: 0.21
Nodes (10): quota_dot_icon(), quota_lines(), Semáforo de cuota restante de las CLIs de IA (#88): el punto de color de la…, Icono del semáforo: un punto relleno del color del estado., Líneas legibles de la cuota restante de Claude Code (una por ventana vigente)., _reset_text(), state_color(), tooltip_text() (+2 more)

### Community 101 - "prompt_packs.py"
Cohesion: 0.16
Nodes (14): import_pack(), list_packs(), _pack_path(), Packs de prompts del AI Prompt Clipboard de cada tablero. Usan el mismo esquema…, [(pack_id, nombre visible)]: primero los de fábrica, luego los importados., El pack guardado en el tablero, o el de por defecto si ya no existe (o no hay)., Normaliza una lista de prompts; ValueError si no sigue el esquema del Clipboard., Valida un pack JSON (p. ej. exportado de AI-Dev-Prompt-Clipboard), lo guarda… (+6 more)

### Community 102 - ".load_board"
Cohesion: 0.08
Nodes (14): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Ejecuta una recarga suave y segura del tablero cuando el agente de IA realiza…, Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Confirma y borra una columna. (+6 more)

### Community 103 - "BoardSyncWorker"
Cohesion: 0.25
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 104 - "test_licensing.py"
Cohesion: 0.29
Nodes (5): LICENSE oficial de PolyForm Noncommercial y avisos de terceros que viajan con…, El LICENSE tenía 10 de las 15 secciones de PolyForm Noncommercial 1.0.0 y un…, El instalador no llevaba ni la licencia de Ekin ni las de lo que empaqueta…, test_installer_ships_license_and_third_party_notices(), test_license_is_the_official_polyform_noncommercial_text()

### Community 105 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Carga y conecta a la base de datos local un tablero sincronizado existente…, Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 106 - "CreateBoardDialog"
Cohesion: 0.20
Nodes (4): CreateBoardDialog, QFrame, Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o…, test_create_board_dialog_headless()

### Community 107 - "build_qss"
Cohesion: 0.25
Nodes (8): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, #133: el sizeHint de QDateEdit no cuenta el padding de la QSS de la app ni el…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules(), test_task_detail_due_date_field_fits_any_date()

### Community 110 - ".init_ui"
Cohesion: 0.14
Nodes (12): Ancho mínimo para que quepa cualquier fecha (#133): el sizeHint de QDateEdit no…, QDialog, QFrame, QWidget, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog… (+4 more)

### Community 111 - "WorkflowDialog"
Cohesion: 0.29
Nodes (4): Abre el diagrama del flujo de trabajo con un agente de IA (#137)., QDialog, Los pasos del flujo, unidos por flechas, y una nota sobre columnas y traspasos., WorkflowDialog

### Community 112 - "QPixmap"
Cohesion: 0.11
Nodes (13): _swatch_icon(), ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, _align_icon(), Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., _swatch_icon() (+5 more)

### Community 113 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 114 - "test_batch_drag_drop.py"
Cohesion: 0.14
Nodes (13): Pruebas unitarias para la funcionalidad de Multi-Card Batch Drag-and-Drop…, Verifica la recolocación en lote entre columnas: atomicidad DB y renderizado…, Verifica el reordenamiento en lote dentro de la misma columna., Verifica que el movimiento en lote registre acción deshacer/rehacer y restaure…, Soltar un lote sobre una columna plegada debe desplegarla y colocar todas las…, Verifica que _create_drag_pixmap genere una imagen con dimensiones válidas para…, Verifica que TaskListArea emita batch_tasks_dropped cuando se suelta un payload…, test_batch_move_undo_and_redo() (+5 more)

### Community 115 - "test_release_notes.py"
Cohesion: 0.47
Nodes (4): El workflow de release (windows-latest, pwsh) extrae las notas de CHANGELOG.md…, _run(), test_notes_on_stdout_are_utf8_whatever_the_console_encoding(), test_notes_with_emoji_are_written_as_utf8_to_the_output_file()

### Community 116 - "test_board_reorder.py"
Cohesion: 0.39
Nodes (8): _board_drop_event(), _names(), #58: reordenar tableros arrastrándolos en la barra lateral (persistido en…, test_board_button_ignores_drag_of_itself(), test_boards_created_after_a_reorder_go_last(), test_dropping_a_board_on_another_reorders_sidebar_and_db(), test_move_board_before_and_after_target_persists_order(), test_reorder_keeps_archived_boards_in_place()

### Community 117 - "test_widgets_headless.py"
Cohesion: 0.05
Nodes (58): _card_with_timer(), _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _editor_with_all_selected(), _mention_editor(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, LogEntryWidget convierte URLs sin enlace en hipervínculos clicables y los abre… (+50 more)

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
Cohesion: 0.11
Nodes (30): _command(), install_claude_statusline(), is_installed(), _load_settings(), _python_for_scripts(), quota_state(), Cuota restante de las CLIs de IA (#88). Claude Code la expone de forma…, Quita la status line de Ekin y restaura la que hubiera antes. (+22 more)

### Community 128 - "2. Implementation Tasks"
Cohesion: 0.09
Nodes (22): 0. Estado (2026-10-15, tras el OUTRO b063add), #101 — BUG: el servidor MCP no arranca al abrir Ekin  `[S]`, #102 — BUG: «TaskCard already deleted» al cerrar el detalle  `[S]`, 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, #74 — Respuestas MCP en inglés para ahorrar tokens  `[A: S · B: S · C: M]`, #81 — PWA Ekin Móvil  `[XL — épica]` (+14 more)

### Community 129 - "compute_drop_index"
Cohesion: 0.25
Nodes (10): Verifica que compute_drop_index excluya todas las tareas del lote para evitar…, test_compute_drop_index_multi_card(), Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last() (+2 more)

### Community 130 - ".__init__"
Cohesion: 0.18
Nodes (6): CalendarChip, QFrame, QPushButton, QWidget, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes).

### Community 131 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 132 - "DayCell"
Cohesion: 0.20
Nodes (5): DayCell, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon(), Verifica que _on_task_rescheduled actualice la fecha en la BD y emita…, test_calendar_view_on_task_rescheduled_and_drag_drop()

### Community 133 - ".__init__"
Cohesion: 0.17
Nodes (6): app_icon(), Verifica si es la primera vez que se abre la app y crea datos de ejemplo…, Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Arranca el servidor MCP; si el puerto sigue ocupado (p. ej. por la instancia…, Crea el icono de bandeja (habilita toasts nativos de Windows).

### Community 134 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 135 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 136 - "._update_local_dir_buttons"
Cohesion: 0.33
Nodes (3): Tras cambiar el directorio local desde fuera (p. ej. Ajustes), repinta Diario y…, Diario solo si el directorio local tiene algún .md / .txt; Work siempre, con un…, WORK: MCP en marcha, CLI actualizada y abierta en el repo con el INTRO. Si el…

### Community 137 - "_board_sync_lock"
Cohesion: 0.33
Nodes (6): _board_sync_lock(), Lock, #124: «Sincronizar ahora» mientras la sync automática del mismo tablero sigue…, test_sidebar_sync_now_on_a_busy_board_informs_instead_of_failing(), #124: la sync manual de la barra lateral llamaba a sync_board_with_file en…, test_sync_of_a_board_already_syncing_returns_busy_without_touching_anything()

### Community 138 - "create_getting_started_board"
Cohesion: 0.33
Nodes (6): create_getting_started_board(), Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su…, Verifica que la plantilla de Primeros Pasos instancie las 4 columnas…, test_create_getting_started_board(), Verifica que BoardViewWidget muestre y oculte el banner del tour según el…, test_board_view_interactive_tour_lifecycle()

### Community 139 - "strings.py"
Cohesion: 0.07
Nodes (20): Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Panel de Analíticas: métricas transversales (todos los tableros) con tarjetas…, color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas)., Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Mixins de funcionalidad modular para TaskDetailDialog (temporizadores,…, Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Genera una cadena amigable para nombres de archivo. (+12 more)

### Community 140 - ".handle_task_drop"
Cohesion: 0.20
Nodes (5): Maneja la recolocación en lote de múltiples tareas tras arrastrarlas., Soltar un lote de tarjetas sobre una columna plegada: la despliega y coloca las…, Registra una acción deshacer/rehacer para el movimiento (individual o en lote)…, Maneja la lógica de recolocación de tareas (individual o por lote) tras…, Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…

### Community 141 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 142 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 143 - "cli_tools.py"
Cohesion: 0.13
Nodes (16): CliTool, ensure_mcp_registered(), launch(), CLIs de agentes de IA que Ekin sabe lanzar desde un tablero (START WORKING):…, Actualiza la CLI. Devuelve (ok, mensaje). Nunca lanza: un fallo no debe…, Registra el servidor MCP del tablero en la CLI si aún no lo está. Devuelve (ok,…, Abre la CLI en una consola nueva (Windows Terminal si es la consola por…, _run() (+8 more)

### Community 145 - ".reload_logs"
Cohesion: 0.10
Nodes (10): _ClickOutsideFilter, Limpia y vuelve a cargar los logs/entradas del diario con carga diferida (lazy…, Carga el siguiente lote de entradas anteriores del diario preservando la…, Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Crea una nueva entrada de diario con el texto del input., Elimina una entrada de diario tras confirmación., Mueve la barra de desplazamiento del diario hasta abajo., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo… (+2 more)

### Community 171 - ".__init__"
Cohesion: 0.18
Nodes (6): QCheckBox, Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de…, Stepper −/+ genérico ligado a un QSpinBox de respaldo; muestra `valor suffix`., ToggleSwitch

### Community 181 - "CodeBlockDialog"
Cohesion: 0.15
Nodes (8): CodeBlockDialog, LinkDialog, QDialog, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para insertar un enlace (URL)., Abre el diálogo para insertar un bloque de código formateado., Inserta un bloque de código formateado con resaltado de sintaxis., Abre el diálogo para insertar o editar un enlace web.

### Community 185 - "board_variables"
Cohesion: 0.17
Nodes (12): board_variables(), fill_variables(), find_variables(), Variables que se rellenan solas a partir del tablero., Nombres de las variables {{...}} del texto, en orden de aparición y sin repetir., Sustituye las variables con valor en `values`; deja intactas las demás., parametrize, test_board_variables_use_the_claude_code_server_name() (+4 more)

### Community 188 - "BoardEditDialog"
Cohesion: 0.20
Nodes (4): BoardEditDialog, Abre el diálogo para copiar el tablero activo con un nuevo nombre., Diálogo personalizado para crear o editar un tablero (nombre, color y, al…, test_board_edit_dialog_local_dir_row()

### Community 189 - "QuotaPopup"
Cohesion: 0.25
Nodes (4): QDialog, QuotaPopup, Detalle de la cuota por CLI instalada; permite activar o quitar la lectura de…, Muestra el detalle de la cuota por CLI anclado bajo el semáforo.

### Community 190 - "pixmap_from_data_uri"
Cohesion: 0.25
Nodes (8): pixmap_from_data_uri(), Decodifica 'data:image/xxx;base64,....' a un QPixmap con caché en memoria…, Verifica que pixmap_from_data_uri utilice QPixmapCache para data URIs base64., test_pixmap_from_data_uri_cache(), Regresión: antes href y src eran el MISMO data URI (la miniatura ya reducida al…, test_markdown_text_edit_stores_higher_res_copy_for_preview(), test_pixmap_from_data_uri_decodes_valid_png(), test_pixmap_from_data_uri_returns_null_for_garbage()

### Community 191 - "TableInsertDialog"
Cohesion: 0.25
Nodes (5): Diálogo modal para configurar e insertar una tabla con número inicial de filas…, TableInsertDialog, Pide filas y columnas mediante un diálogo unificado e inserta la tabla…, Verifica que TableInsertDialog admita dimensiones personalizadas y que su botón…, test_table_dialog_insert_dimensions()

### Community 192 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 193 - "._update_mention_popup"
Cohesion: 0.25
Nodes (3): Texto escrito tras un «@» que abre una mención (a inicio de línea o tras un…, Muestra, filtra u oculta el desplegable de menciones según el texto tras «@»., Sustituye «@texto» por un enlace al adjunto elegido («📄 nombre» o «🔗 nombre»);…

### Community 194 - ".select_board"
Cohesion: 0.33
Nodes (3): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…

### Community 197 - "SidebarWidget"
Cohesion: 0.11
Nodes (18): QFrame, Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos…, Persiste el nuevo orden y recoloca los botones sin recargar el tablero activo., SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir… (+10 more)

### Community 198 - "set_language"
Cohesion: 0.11
Nodes (21): parametrize, get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), _known_texts() (+13 more)

### Community 199 - "test_local_ai_rdi.py"
Cohesion: 0.21
Nodes (12): format_daily_standup_markdown(), generate_daily_standup_data(), Formatea la estructura de standup_data en un reporte Markdown elegante., Extrae métricas y estado del flujo del tablero para generar el informe Daily…, _active(), _agile_board(), Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi: - Fase 1:…, #84: la tarea activa se resuelve en el servidor (In Progress → Review → Ready)… (+4 more)

### Community 200 - "NotificationsPopup"
Cohesion: 0.18
Nodes (7): NotificationsPopup, Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana., test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 201 - "TaskTimerMixin"
Cohesion: 0.32
Nodes (5): Manejo de estado y UI del temporizador de tareas para TaskDetailDialog., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Actualiza el botón y la etiqueta de tiempo transcurrido según…, TaskTimerMixin

### Community 207 - "LandingTourDialog"
Cohesion: 0.16
Nodes (9): LandingTourDialog, QDialog, Diálogo modal interactivo para guiar al usuario en las capacidades clave de…, Verifica la navegación paso a paso y la persistencia de LandingTourDialog., Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el…, #137: el diagrama se abre desde la guía de bienvenida y desde Ajustes., test_landing_tour_and_settings_open_the_workflow_diagram(), test_landing_tour_dialog_dont_show_checkbox() (+1 more)

### Community 208 - "WeeklyDigestDialog"
Cohesion: 0.32
Nodes (4): QDialog, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, _swatch_icon(), WeeklyDigestDialog

### Community 209 - "BoardConfigDialog"
Cohesion: 0.29
Nodes (5): BoardConfigDialog, QDialog, Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…, Verifica que BoardConfigDialog muestre las opciones adecuadas según si el…, test_board_config_dialog_cloud_options()

### Community 210 - "_edit_remote_task"
Cohesion: 0.25
Nodes (8): _edit_remote_task(), Simula la edición de un compañero en el .ekboard, posterior a lo local: cambia…, #97: título cambiado en local y descripción en remoto no son una colisión: se…, #97: una tarea sin base de la última sincronización (sincronizada con una…, #97: la base se renueva al importar y al fusionar (no solo al exportar). Con…, test_field_merge_base_is_refreshed_after_every_sync(), test_field_merge_takes_each_side_changes_without_archiving(), test_field_merge_without_base_falls_back_to_newest_whole_task()

### Community 218 - "format_code_block_html"
Cohesion: 0.50
Nodes (5): format_code_block_html(), _get_warm_pygments_style(), Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, test_warm_syntax_highlighting_style()

### Community 219 - ".apply_theme"
Cohesion: 0.15
Nodes (6): Aplica el tema (oscuro/claro) al vuelo. `reload` recarga el tablero para que…, Abre la pantalla de Ajustes (tema, notificaciones, idioma, updates, tour)., Arranca la versión nueva como proceso aparte y cierra esta de forma ordenada…, Verifica de forma silenciosa (o con feedback si manual=True) si hay…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica si hay actualizaciones en el repo de GitHub (modo git dev).

### Community 221 - "is_ollama_available"
Cohesion: 0.50
Nodes (4): check_http_endpoint(), is_ollama_available(), Comprueba rápidamente si un endpoint HTTP local está respondiendo., Comprueba rápidamente si Ollama está respondiendo en localhost.

### Community 225 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 230 - "sync_test_db"
Cohesion: 0.67
Nodes (3): fixture, Crea una base de datos temporal para pruebas de sincronización., sync_test_db()

## Knowledge Gaps
- **153 isolated node(s):** `CliTool`, `1. Overview`, `2. Implementation Tasks`, `3. Acceptance Criteria`, `QA Report` (+148 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `.__init__`, `DayCell`, `TaskAiMixin`, `.__init__`, `MyWorkWidget`, `._update_local_dir_buttons`, `DashboardWidget`, `strings.py`, `.handle_task_drop`, `DiaryViewerDialog`, `TagManagerDialog`, `SettingsDialog`, `create_getting_started_board`, `TagPickerDialog`, `CommandPalette`, `LogEntryWidget`, `.reload_logs`, `sync_board_with_file`, `._rebuild_single_column`, `.reload_boards`, `RichTextToolbar`, `ExportDialog`, `BoardSyncUiMixin`, `CalendarViewWidget`, `lucide_icon`, `.show_command_palette`, `MainWindow`, `ColumnEditDialog`, `McpSyncDialog`, `test_mcp.py`, `CalendarSettingsDialog`, `.contextMenuEvent`, `.__init__`, `.load_task_data`, `PromptClipboardDialog`, `templates.py`, `BulkAddTaskDialog`, `styles.py`, `InteractiveTourBanner`, `QuotaPopup`, `BoardEditDialog`, `SaveAsTemplateDialog`, `.mouseReleaseEvent`, `SidebarWidget`, `test_start_working.py`, `._handle_key_press`, `SearchDialog`, `TaskTimerMixin`, `BoardButton`, `NotificationsPopup`, `InstallerDownloadThread`, `set_language`, `SyncResult`, `WeeklyDigestDialog`, `BoardViewWidget`, `BoardConfigDialog`, `TaskDetailDialog`, `LandingTourDialog`, `.render_tags`, `board_view.py`, `ColumnWidget`, `TaskCard`, `format_code_block_html`, `.apply_theme`, `quota_popup.py`, `prompt_packs.py`, `.load_board`, `CreateBoardDialog`, `._rebuild_grid`, `.init_ui`, `QPixmap`, `test_widgets_headless.py`, `.notify_due_today`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `copy_board`, `connection.py`, `exporter.py`, `tasks.py`, `logs.py`, `strings.py`, `sync.py`, `snapshots.py`, `get_task_tags_bulk`, `tags.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `BoardViewWidget` to `.__init__`, `._update_local_dir_buttons`, `create_getting_started_board`, `DiaryViewerDialog`, `.handle_task_drop`, `BoardSyncController`, `cli_tools.py`, `._rebuild_single_column`, `test_concurrent_edit.py`, `BoardSyncUiMixin`, `ColumnEditDialog`, `test_mcp.py`, `PromptClipboardDialog`, `BulkAddTaskDialog`, `test_hover_expand.py`, `UndoAction`, `InteractiveTourBanner`, `SidebarWidget`, `test_start_working.py`, `test_incremental_rendering.py`, `test_mcp_live_refresh.py`, `LandingTourDialog`, `board_view.py`, `ColumnWidget`, `TaskCard`, `._check_external_mcp_mutations`, `test_timer_board_view.py`, `.load_board`, `test_batch_drag_drop.py`, `test_wip_limit.py`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `BoardViewWidget` (e.g. with `BoardColumnsArea` and `BoardSelectionDialog`) actually correct?**
  _`BoardViewWidget` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `TaskDetailDialog` (e.g. with `._open_task_detail()` and `test_add_link_with_local_path_renders_with_attachment_icon()`) actually correct?**
  _`TaskDetailDialog` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `MarkdownTextEdit` (e.g. with `LogEntryWidget` and `CodeBlockDialog`) actually correct?**
  _`MarkdownTextEdit` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `CliTool`, `1. Overview`, `2. Implementation Tasks` to the rest of the system?**
  _153 weakly-connected nodes found - possible documentation gaps or missing edges._