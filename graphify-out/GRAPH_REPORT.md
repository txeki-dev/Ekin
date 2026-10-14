# Graph Report - Ekin  (2026-10-14)

## Corpus Check
- 154 files · ~200,723 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2791 nodes · 4998 edges · 214 communities (151 shown, 63 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 182 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `23a2f63e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_local_dir.py
- test_main_window.py
- test_ics_export.py
- QDialog
- TaskDetailDialog
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
- t
- TaskListArea
- CommandPalette
- LogEntryWidget
- /graphify Pipeline
- board_sync.py
- ._rebuild_single_column
- SidebarWidget
- .reload_boards
- connection.py
- RichTextToolbar
- TaskCard
- BoardSyncUiMixin
- CalendarViewWidget
- tags.py
- InteractiveTourBanner
- MyWorkWidget
- links.py
- MainWindow
- templates.py
- test_ux_enhancements.py
- McpSyncDialog
- boards.py
- test_mcp.py
- main
- DraggableColumnTitle
- CalendarSettingsDialog
- .contextMenuEvent
- SearchDialog
- security_utils.py
- SaveAsTemplateDialog
- Any
- McpManager
- TagManagerDialog
- sync.py
- summarize_diary_offline
- test_templates.py
- BoardSelectionMixin
- snapshots.py
- BulkAddTaskDialog
- task_detail_dialog.py
- test_hover_expand.py
- UndoManager
- Part B: Semantic Extraction (Subagents)
- ColorCirclesPicker
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
- DayCell
- .show_command_palette
- BoardButton
- LocalAiCircuitBreaker
- test_incremental_rendering.py
- start_prompt
- test_local_ai.py
- .__init__
- .handle_task_drop
- local_ai.py
- BoardViewWidget
- compute_drop_index
- export_dialog.py
- test_column_roles.py
- BoardEditDialog
- .render_tags
- LandingTourDialog
- ColumnWidget
- .sync_ics
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
- lucide_icon
- strings.py
- set_language
- BoardSyncWorker
- connect_shared_board_from_file
- TagPickerDialog
- .load_task_data
- NotificationsPopup
- prompt_packs.py
- .mouseReleaseEvent
- conftest.py
- ImagePreviewDialog
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- test_board_reorder.py
- TaskTimerMixin
- format_code_block_html
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
- _Runs
- 2. Implementation Tasks
- create_getting_started_board
- build_qss
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- .reload_logs
- .check_for_updates
- Calendar Drag-to-Reschedule
- Cross-Repo Graph Merge
- test_widgets_headless.py
- QFrame
- .load_board
- QLabel
- test_prompt_clipboard.py
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
- .delete_board
- Ekin App Icon
- ekin-kanban
- hex_to_rgb
- QDialog
- QTextEdit
- QWidget
- BoardConfigDialog
- .set_board
- _SseClientSession
- QFrame
- QThread
- ._check_external_mcp_mutations
- mcp_server.py
- .__init__
- .open_code_dialog
- test_local_ai_rdi.py
- mcp_board
- task_mixins.py
- Any
- .delete_task
- QFrame
- .select_board
- .get_pending_notifications
- test_database_sync_helpers_lifecycle
- test_connection_pooling_and_lifecycle
- test_fts5_search_and_triggers
- test_fts5_search_fallback_on_error
- test_update_task_positions_bumps_version_only_on_column_change
- QObject
- parametrize

## God Nodes (most connected - your core abstractions)
1. `t()` - 240 edges
2. `BoardViewWidget` - 102 edges
3. `get_connection()` - 99 edges
4. `TaskDetailDialog` - 94 edges
5. `MarkdownTextEdit` - 89 edges
6. `MainWindow` - 50 edges
7. `lucide_icon()` - 42 edges
8. `SidebarWidget` - 41 edges
9. `McpProtocolHandler` - 30 edges
10. `sync_board_with_file()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `test_is_local_link_classifies_urls_vs_paths()` --calls--> `_is_local_link()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `test_board_view_mcp_btn_states()` --calls--> `BoardViewWidget`  [INFERRED]
  tests/test_mcp.py → board_view.py
- `_Runs` --uses--> `BoardViewWidget`  [INFERRED]
  tests/test_start_working.py → board_view.py
- `test_refresh_timer_badges_noop_on_welcome_screen()` --calls--> `BoardViewWidget`  [EXTRACTED]
  tests/test_timer_board_view.py → board_view.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (214 total, 63 thin omitted)

### Community 1 - "test_local_dir.py"
Cohesion: 0.06
Nodes (47): list_repo_files(), Archivos del directorio local (repo) asociado a un tablero, para ofrecerlos en…, Rutas relativas (con «/») de los archivos de `root`, como mucho `limit`., boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas. (+39 more)

### Community 2 - "test_main_window.py"
Cohesion: 0.07
Nodes (41): get_default_db_path(), InstallerDownloadThread, parse_version_tuple(), Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, Muestra confirmación al usuario y descarga el instalador si acepta., ReleaseCheckThread, QThread, Los pasos lentos (update de la CLI y registro del MCP) fuera del hilo de la… (+33 more)

### Community 3 - "test_ics_export.py"
Cohesion: 0.11
Nodes (28): build_ics(), _escape(), export_ics(), _fold_line(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar. (+20 more)

### Community 5 - "TaskDetailDialog"
Cohesion: 0.06
Nodes (45): QDialog, Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la…, Ancho máximo (px) para imágenes en las notas (panel izquierdo ancho)., Lo que se ofrece al escribir «@»: los Enlaces / Adjuntos actuales de la tarea…, Verifies if the target is a UNC share, executable/script, or unsafe scheme, and…, TaskDetailDialog, TaskAiMixin (+37 more)

### Community 6 - "sync_board_with_file"
Cohesion: 0.06
Nodes (44): Ejecuta el ciclo completo de sincronización y fusión diferencial para un…, sync_board_with_file(), fixture, Verifica que cambios en el archivo remoto sin cambios locales se importan…, Crea una base de datos temporal para pruebas de sincronización., Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que desvincular un tablero borra sync_path y lo deja offline., Verifica que si local y remoto añaden tareas diferentes simultáneamente, la… (+36 more)

### Community 7 - "MarkdownTextEdit"
Cohesion: 0.05
Nodes (36): MarkdownTextEdit, Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Aplica interlineado proporcional (por defecto 135%) a todos los bloques del…, Texto escrito tras un «@» que abre una mención (a inicio de línea o tras un…, Muestra, filtra u oculta el desplegable de menciones según el texto tras «@»., Sustituye «@texto» por un enlace al adjunto elegido («📄 nombre» o «🔗 nombre»);…, QTextEdit (+28 more)

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
Cohesion: 0.09
Nodes (18): Abre el AI Prompt Clipboard con el pack de prompts del tablero activo., Abre los diarios de desarrollo (diary.md / diary_archive.md) del directorio…, diary_files(), DiaryViewerDialog, Rutas de los diarios que existen en `local_dir` (en el orden de DIARY_FILES)., Una pestaña por diario existente, renderizado como Markdown; Recargar conserva…, ask_variable_values(), PromptClipboardDialog (+10 more)

### Community 12 - "._handle_key_press"
Cohesion: 0.07
Nodes (13): Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Elige el símbolo de viñeta según el nivel de anidamiento (las listas numeradas…, Aumenta (Tab) o reduce (Shift+Tab) el nivel de anidamiento de la viñeta actual., Alinea el bloque de texto actual o selección a la izquierda., Centra el bloque de texto actual o selección., Alinea el bloque de texto actual o selección a la derecha., Justifica el bloque de texto actual o selección. (+5 more)

### Community 13 - "BoardSyncController"
Cohesion: 0.08
Nodes (20): BoardSyncController, QObject, Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Disparado por el sistema de archivos ante modificaciones externas., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Exporta automáticamente los cambios locales si el tablero está vinculado. (+12 more)

### Community 14 - "clean_html_description"
Cohesion: 0.15
Nodes (20): clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, author_entry_html(), markdown_to_qt_html(), migrate_plain_text_content(), Conversión a HTML de Qt del Markdown / texto plano que envían los agentes por…, Fragmento HTML de Qt para `text`. Lo que ya es HTML se devuelve tal cual; el… (+12 more)

### Community 15 - "SettingsDialog"
Cohesion: 0.08
Nodes (20): QCheckBox, QFrame, QDialog, Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Segmentado English / Español que maneja el lang_combo de respaldo., Segmentado Light / Dark que maneja el theme_combo de respaldo., Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de… (+12 more)

### Community 16 - "t"
Cohesion: 0.17
Nodes (13): format_sync_summary(), board_sync_controller.py - Controlador de sincronización desacoplado de…, Genera un resumen conciso de un SyncResult para mostrar en la interfaz., PriorityManagerDialog, QDialog, Modal propio e independiente para gestionar los niveles y colores de Prioridad.…, Returns the localized string for `key`, falling back to English if missing., t() (+5 more)

### Community 18 - "CommandPalette"
Cohesion: 0.14
Nodes (12): CommandPalette, QDialog, _swatch_icon(), Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, Verifica que CommandPalette no tenga WA_DeleteOnClose activo y no sufra…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query() (+4 more)

### Community 19 - "LogEntryWidget"
Cohesion: 0.06
Nodes (35): fit_html_images(), format_single_cell(), linkify_urls(), Utilidades compartidas para procesamiento y saneamiento de HTML en…, Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no…, Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,… (+27 more)

### Community 20 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 21 - "board_sync.py"
Cohesion: 0.12
Nodes (23): _apply_remote_board_clean(), calculate_file_hash(), create_premerge_backup(), _execute_two_way_merge(), export_board_to_sync_dict(), _merge_task_sub_entities(), now_utc_iso(), _prune_premerge_backups() (+15 more)

### Community 22 - "._rebuild_single_column"
Cohesion: 0.10
Nodes (11): Maneja las acciones interactivas directas asociadas a cada paso del tour., Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de… (+3 more)

### Community 23 - "SidebarWidget"
Cohesion: 0.13
Nodes (16): Persiste el nuevo orden y recoloca los botones sin recargar el tablero activo., SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir…, El fix del guard no debe bloquear el caso normal: con un tablero real…, test_add_column_shortcut_noop_when_no_board_selected() (+8 more)

### Community 24 - ".reload_boards"
Cohesion: 0.12
Nodes (10): Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero a partir de una plantilla o en…, Abre el diálogo para copiar el tablero activo con un nuevo nombre., Re-aplica los colores dependientes del tema en los widgets de la barra lateral…, Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Archiva/desarchiva un tablero y recarga la lista., Abre el modal de opciones del tablero activo y ejecuta la acción elegida., Permite al usuario seleccionar un archivo .ekboard compartido existente y… (+2 more)

### Community 25 - "connection.py"
Cohesion: 0.12
Nodes (17): Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, init_db(), Crea las tablas necesarias si no existen., get_active_timer_tasks(), get_scheduled_tasks(), get_task_board_id(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve el board_id al que pertenece una tarea (o None si no existe). (+9 more)

### Community 26 - "RichTextToolbar"
Cohesion: 0.07
Nodes (16): _align_icon(), _color_icon(), Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, Pide filas y columnas mediante un diálogo unificado e inserta la tabla…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar (+8 more)

### Community 27 - "TaskCard"
Cohesion: 0.11
Nodes (10): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, test_task_card_ctrl_click_and_selection_state(), Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la…, Activa o desactiva el estado visual de selección múltiple., Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Umbral (en horas) a partir del cual la insignia del temporizador se resalta en…, Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo…, Limpia y dibuja las etiquetas actuales y la fecha de vencimiento. (+2 more)

### Community 28 - "BoardSyncUiMixin"
Cohesion: 0.07
Nodes (18): BoardSyncUiMixin, Maneja el clic en el botón de sincronización de la cabecera., Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para…, Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Compatibilidad hacia atrás: actualiza el controlador de sincronización. (+10 more)

### Community 29 - "CalendarViewWidget"
Cohesion: 0.12
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 30 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 31 - "InteractiveTourBanner"
Cohesion: 0.19
Nodes (7): InteractiveTourBanner, Barra superior interactiva in-situ para guiar al usuario a través del tablero…, Aplica colores y refresca los textos según el idioma y tema actuales., Verifica la navegación paso a paso, emisión de señales y finalización de…, Verifica que el botón cerrar descarte el tour y persista…, test_interactive_tour_banner_dismiss(), test_interactive_tour_banner_navigation_and_actions()

### Community 32 - "MyWorkWidget"
Cohesion: 0.16
Nodes (17): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon() (+9 more)

### Community 33 - "links.py"
Cohesion: 0.20
Nodes (9): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), get_task() (+1 more)

### Community 34 - "MainWindow"
Cohesion: 0.07
Nodes (13): MainWindow, Manejador si el tablero actual cambió en el sidebar., Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., Sincroniza inmediatamente el tablero activo con su archivo en la nube., Abre el diálogo para vincular el tablero activo a un nuevo archivo .ekboard., Abre la carpeta de logs de diagnóstico en el explorador de archivos. (+5 more)

### Community 35 - "templates.py"
Cohesion: 0.16
Nodes (19): apply_template_to_board(), BoardTemplate, ColumnTemplate, export_board_to_template(), get_all_templates(), get_builtin_templates(), get_template_by_id(), Any (+11 more)

### Community 36 - "test_ux_enhancements.py"
Cohesion: 0.10
Nodes (19): Pruebas exhaustivas para las 4 mejoras de UX: 1. Tablas interactivas y formato…, Verifica las proporciones, márgenes simétricos, scroll fluido y edición in-…, Verifica que TableInsertDialog admita dimensiones personalizadas y que su botón…, Verifica inserción inicial de tabla y manipulación mediante acciones de…, Verifica la eliminación total de CSS (<style>) residual de Qt., Verifica que los metadatos se organicen en 4 filas dentro del panel izquierdo,…, Verifica que TaskDetailDialog cargue de forma diferida (windowed) las entradas…, Verifica que pixmap_from_data_uri utilice QPixmapCache para data URIs base64. (+11 more)

### Community 37 - "McpSyncDialog"
Cohesion: 0.19
Nodes (8): get_mcp_manager(), McpSyncDialog, QDialog, QPushButton, QTextEdit, Diálogo modal para configurar la sincronización de un tablero con agentes de IA…, Prueba el diálogo modal de configuración McpSyncDialog., test_mcp_sync_dialog_headless()

### Community 38 - "boards.py"
Cohesion: 0.10
Nodes (20): create_board(), delete_board(), get_board(), get_board_by_uuid(), get_board_mutation_fingerprint(), get_boards(), move_board(), Recuerda el pack del AI Prompt Clipboard elegido para el tablero. (+12 more)

### Community 39 - "test_mcp.py"
Cohesion: 0.07
Nodes (44): McpProtocolHandler, Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol., _done_and_other_columns(), parametrize, Pruebas automatizadas para el Servidor MCP (Model Context Protocol), seguridad…, list_tasks no debe filtrar al agente el HTML/CSS de Qt (DOCTYPE, <style>, etc.)., list_tasks tenía un primer bucle muerto que repetía las consultas de cada…, Verifica que el prompt contextual del tablero (Scrum Master / Opositor) se… (+36 more)

### Community 40 - "main"
Cohesion: 0.13
Nodes (18): get_log_dir(), install_excepthook(), install_qt_message_handler(), Registro de diagnóstico y captura global de errores para Ekin. Escribe un log…, Directorio de logs (se crea si no existe): ~/.ekin/logs., Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del…, Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)., Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin. (+10 more)

### Community 41 - "DraggableColumnTitle"
Cohesion: 0.10
Nodes (6): QPixmap, DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Etiqueta con el texto girado 90° (nombre de una columna plegada)., Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…, VerticalLabel

### Community 42 - "CalendarSettingsDialog"
Cohesion: 0.15
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 43 - ".contextMenuEvent"
Cohesion: 0.15
Nodes (7): format_table_all_cells(), Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen., Identifica si una tabla corresponde a un bloque de código., Menú contextual estándar ampliado con opciones de mayúsculas/minúsculas, borrar…

### Community 44 - "SearchDialog"
Cohesion: 0.25
Nodes (6): QDialog, Diálogo de búsqueda global de tareas. Filtra por texto (título/descripción),…, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon()

### Community 45 - "security_utils.py"
Cohesion: 0.29
Nodes (9): confirm_open_untrusted_link(), _get_target_extension(), _is_local_link(), open_link_safely(), Utilidades de seguridad para la validación y apertura segura de hipervínculos y…, Abre de forma segura una URL o ruta local tras verificar su nivel de confianza.…, True si la cadena representa una ruta de archivo local o de red (UNC / relativa…, Extracts the lowercased file extension from a local path or file URL. (+1 more)

### Community 46 - "SaveAsTemplateDialog"
Cohesion: 0.20
Nodes (5): QDialog, Tarjeta interactiva para visualizar y seleccionar una plantilla de tablero., Diálogo modal para guardar el tablero actual como plantilla personalizada de…, SaveAsTemplateDialog, TemplateCardWidget

### Community 47 - "Any"
Cohesion: 0.19
Nodes (6): Any, _clean_text(), get_mcp_event_bus(), McpToolExecutor, Texto plano de un HTML de Qt (sin DOCTYPE/<style>), enmascarado si se pide., Ejecuta herramientas MCP garantizando que no se sobrepasen los límites del…

### Community 48 - "McpManager"
Cohesion: 0.10
Nodes (10): claude_code_server_name(), McpHttpServer, McpManager, Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies., Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria., Nombre del servidor MCP del tablero en el comando `claude mcp add` (p. ej.…, Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban., Prueba el servidor HTTP embebido realizando peticiones directas. (+2 more)

### Community 49 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 50 - "sync.py"
Cohesion: 0.13
Nodes (14): get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero., Actualiza la marca de tiempo de sincronización y el hash del archivo., Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline. (+6 more)

### Community 51 - "summarize_diary_offline"
Cohesion: 0.40
Nodes (5): Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas)…, summarize_diary_offline(), Pruebas del resumen determinista del diario (local_ai.summarize_diary_offline),…, test_summarize_diary_offline_builds_two_sections(), test_summarize_diary_offline_empty()

### Community 52 - "test_templates.py"
Cohesion: 0.17
Nodes (18): create_board_from_template(), delete_custom_template(), get_custom_templates(), get_templates_dir(), Devuelve la ruta al directorio donde se guardan las plantillas personalizadas…, Carga todas las plantillas de usuario personalizadas desde archivos JSON., Guarda una plantilla personalizada como archivo JSON en el directorio de…, Elimina una plantilla personalizada de disco si existe, con validación anti… (+10 more)

### Community 53 - "BoardSelectionMixin"
Cohesion: 0.21
Nodes (7): BoardSelectionMixin, Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej.…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero., Escape deselecciona tarjetas múltiples.

### Community 54 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 55 - "BulkAddTaskDialog"
Cohesion: 0.20
Nodes (6): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas…, test_bulk_add_task_dialog()

### Community 56 - "task_detail_dialog.py"
Cohesion: 0.18
Nodes (11): ensure_priority_category(), Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si…, color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas)., Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Pruebas unitarias para la independización de la categoría 'Priority' y su modal…, test_ensure_priority_category_creates_defaults(), test_priority_manager_dialog_crud() (+3 more)

### Community 57 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 58 - "UndoManager"
Cohesion: 0.20
Nodes (8): Pruebas unitarias para UndoManager y UndoAction., test_undo_manager_initial_state(), test_undo_manager_max_depth(), test_undo_manager_push_clears_redo(), test_undo_manager_push_enables_can_undo(), test_undo_manager_undo_and_redo_lifecycle(), UndoAction, UndoManager

### Community 59 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 60 - "ColorCirclesPicker"
Cohesion: 0.06
Nodes (20): BoardColumnsArea, BoardSelectionDialog, ColumnEditDialog, QDialog, QWidget, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…, Diálogo para crear o editar una columna (nombre y color). (+12 more)

### Community 61 - "FlowLayout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 62 - "test_reminders.py"
Cohesion: 0.13
Nodes (19): current_week_key(), QDialog, Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, should_show_weekly_digest(), split_digest_tasks() (+11 more)

### Community 63 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 64 - "CreateBoardDialog"
Cohesion: 0.20
Nodes (4): CreateBoardDialog, QFrame, Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o…, test_create_board_dialog_headless()

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
Cohesion: 0.21
Nodes (14): START WORKING: MCP en marcha, CLI actualizada y abierta en el repo con el INTRO., build_launch(), (argv, prompt_por_portapapeles). Un shim .cmd/.bat (instalación npm) pasa por…, Ejecuta START WORKING para el tablero. Devuelve el id de la CLI abierta, o None…, start_working(), #87: START WORKING abre la CLI del agente en el directorio local del tablero,…, _sw_board(), test_build_launch_passes_the_prompt_to_exes_and_uses_the_clipboard_for_npm_shims() (+6 more)

### Community 71 - "DayCell"
Cohesion: 0.11
Nodes (10): CalendarChip, DayCell, QFrame, QPushButton, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes)., _swatch_icon() (+2 more)

### Community 72 - ".show_command_palette"
Cohesion: 0.18
Nodes (5): Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o…, Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Inicia o reanuda el tour interactivo in-situ en el tablero demo '🚀 Primeros…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero.

### Community 73 - "BoardButton"
Cohesion: 0.18
Nodes (6): BoardButton, Widget personalizado para representar un botón de tablero en la barra lateral., Arrastrar el tablero por la barra lateral para cambiar su orden., Línea de acento en el borde (superior o inferior) donde caerá el tablero., Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral., test_sidebar_board_button_cloud_badge()

### Community 74 - "LocalAiCircuitBreaker"
Cohesion: 0.15
Nodes (7): LocalAiCircuitBreaker, Disyuntor (Circuit Breaker) para el servicio local de inferencia y embeddings.…, Determina si se debe permitir el intento de llamada al servicio local de IA., Registra una respuesta satisfactoria del servicio local, cerrando el circuito., Registra un fallo o timeout del servicio local. Si supera el umbral, abre el…, Restablece manualmente el disyuntor al estado inicial CLOSED., test_local_ai_circuit_breaker_lifecycle()

### Community 75 - "test_incremental_rendering.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el renderizado incremental del tablero (mutaciones de…, Mover una tarea dentro de la misma columna solo debe reconstruir esa columna., Mover una tarea entre dos columnas solo debe reconstruir origen y destino,…, Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del…, create_quick_task solo debe reconstruir la columna de destino, preservando las…, add_task debe reconstruir solo la columna destino y actualizar el chip de…, test_add_task_incremental(), test_create_quick_task_incremental_rendering() (+3 more)

### Community 76 - "start_prompt"
Cohesion: 0.15
Nodes (14): board_variables(), fill_variables(), find_variables(), Variables que se rellenan solas a partir del tablero., El pack guardado en el tablero, o el de por defecto si ya no existe (o no hay)., Nombres de las variables {{...}} del texto, en orden de aparición y sin repetir., Sustituye las variables con valor en `values`; deja intactas las demás., resolve_pack_id() (+6 more)

### Community 77 - "test_local_ai.py"
Cohesion: 0.15
Nodes (16): download_and_extract_runner(), get_runner_download_url(), Devuelve la URL oficial de descarga del binario portable de llama-server según…, Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens…, Descarga y extrae el ejecutable portable de llama-server en runner_dir., stream_openai_chat_completion(), Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py)., Verifica que get_runner_download_url retorna una URL válida con terminación… (+8 more)

### Community 78 - ".__init__"
Cohesion: 0.15
Nodes (6): app_icon(), Aplica el tema (oscuro/claro) al vuelo. `reload` recarga el tablero para que…, Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo…

### Community 79 - ".handle_task_drop"
Cohesion: 0.20
Nodes (5): Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…, Maneja la recolocación en lote de múltiples tareas tras arrastrarlas., Soltar un lote de tarjetas sobre una columna plegada: la despliega y coloca las…, Registra una acción deshacer/rehacer para el movimiento (individual o en lote)…, Maneja la lógica de recolocación de tareas (individual o por lote) tras…

### Community 80 - "local_ai.py"
Cohesion: 0.13
Nodes (22): compute_fallback_embedding(), cosine_similarity(), find_duplicate_tasks(), get_llm_circuit_breaker(), get_local_embedding(), index_task_embedding(), is_ollama_available(), Módulo de IA Local de Ekin. Tras #60 su alcance queda acotado a: 1. Detección… (+14 more)

### Community 81 - "BoardViewWidget"
Cohesion: 0.09
Nodes (23): BoardViewWidget, Muestra la barra del tour interactivo in-situ y navega al paso especificado., Oculta la barra del tour interactivo in-situ., Muestra celebración tras completar los 4 pasos del tour interactivo., Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Espera a que termine cualquier hilo de sincronización activo antes de destruir…, BoardMcpUiMixin, BoardSelectionMixin (+15 more)

### Community 82 - "compute_drop_index"
Cohesion: 0.33
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una o varias tarjetas soltadas en `drop_y`.…

### Community 83 - "export_dialog.py"
Cohesion: 0.12
Nodes (12): ExportDialog, ImportConfirmationDialog, QDialog, Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Diálogo modal para confirmar la importación de tableros desde JSON., Genera una cadena amigable para nombres de archivo., Diálogo modal para configurar y ejecutar la exportación de tableros., _slugify() (+4 more)

### Community 84 - "test_column_roles.py"
Cohesion: 0.18
Nodes (16): classify_column(), column_roles(), Rol de cada columna en el flujo del tablero (backlog, ready, in_progress,…, Rol de una columna según su nombre; OTHER si ninguna palabra clave encaja., {column_id: rol} para las columnas de un tablero (en orden de `position`). Si…, _words(), parametrize, Pruebas del clasificador de roles de columna (column_roles.py) sobre las… (+8 more)

### Community 85 - "BoardEditDialog"
Cohesion: 0.20
Nodes (4): BoardEditDialog, Abre el diálogo para editar el nombre y color del tablero activo., Diálogo personalizado para crear o editar un tablero (nombre, color y, al…, test_board_edit_dialog_local_dir_row()

### Community 86 - ".render_tags"
Cohesion: 0.08
Nodes (14): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas (excluyendo Prioridad, que tiene…, Devuelve el id de la etiqueta permanente «Prioridad»., Abre el modal propio e independiente de Prioridades., Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin… (+6 more)

### Community 87 - "LandingTourDialog"
Cohesion: 0.17
Nodes (8): Abre la guía de bienvenida y recorrido inicial de Ekin (modal de diapositivas)., LandingTourDialog, QDialog, Diálogo modal interactivo para guiar al usuario en las capacidades clave de…, Verifica la navegación paso a paso y la persistencia de LandingTourDialog., Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el…, test_landing_tour_dialog_dont_show_checkbox(), test_landing_tour_dialog_navigation_and_persistence()

### Community 88 - "ColumnWidget"
Cohesion: 0.15
Nodes (8): test_column_widget_mouse_press_emits_column_activated(), ColumnWidget, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada)., Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…

### Community 89 - ".sync_ics"
Cohesion: 0.22
Nodes (3): Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde el calendario: abrir el detalle y quedarnos en el calendario., Reescribe cada feed .ics con auto-sync configurado (el global de todos los…

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

### Community 97 - "board_ops.py"
Cohesion: 0.28
Nodes (8): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), move_column_to_board(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…, Mueve una columna a otro tablero y la coloca al final de su lista de columnas.

### Community 98 - "ics_sync.py"
Cohesion: 0.22
Nodes (8): delete_board_ics_sync_path(), get_all_board_ics_sync_paths(), get_board_ics_sync_path(), Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene., Crea o actualiza la ruta de auto-sync de un tablero., Desactiva la sincronización automática de un tablero., Devuelve {board_id: path} para todos los tableros con auto-sync configurado., set_board_ics_sync_path()

### Community 99 - "cli_tools.py"
Cohesion: 0.18
Nodes (11): CliTool, detect_installed(), launch(), CLIs de agentes de IA que Ekin sabe lanzar desde un tablero (START WORKING):…, [(CliTool, ruta del ejecutable)] de las CLIs conocidas que están en el PATH., Actualiza la CLI. Devuelve (ok, mensaje). Nunca lanza: un fallo no debe…, Abre la CLI en una consola nueva (Windows Terminal si es la consola por…, _run() (+3 more)

### Community 100 - ".insertFromMimeData"
Cohesion: 0.14
Nodes (8): apply_word_style_to_qt_table(), Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Al pegar: archivos locales se insertan como enlaces y se emite señal para…, Inserta cada archivo local como enlace «📄 nombre» y emite local_link_pasted…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor con diseño estilo…, Codifica un QImage como data URI PNG en base64., Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se…

### Community 101 - "lucide_icon"
Cohesion: 0.15
Nodes (11): BoardMcpUiMixin, Manejo de la interfaz del botón de integración MCP en la cabecera del tablero., Actualiza el estado visual del botón MCP en la cabecera del tablero., Abre el diálogo modal de configuración MCP para el tablero actual., Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el…, Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)., lucide_icon(), lucide_pixmap() (+3 more)

### Community 102 - "strings.py"
Cohesion: 0.08
Nodes (27): Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, board_mixins.py - Mixins modulares para BoardViewWidget. Separa la gestión de…, Diálogos para la selección, creación y gestión de plantillas de tableros en…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando… (+19 more)

### Community 103 - "set_language"
Cohesion: 0.20
Nodes (11): get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), Verifica que CalendarViewWidget obtenga nombres de meses y días de la semana…, test_calendar_view_weekdays_and_months_localization() (+3 more)

### Community 104 - "BoardSyncWorker"
Cohesion: 0.25
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 105 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, Carga y conecta a la base de datos local un tablero sincronizado existente…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 106 - "TagPickerDialog"
Cohesion: 0.29
Nodes (4): QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog

### Community 107 - ".load_task_data"
Cohesion: 0.11
Nodes (8): _is_unc_path(), r"""True if url targets a network share (UNC path, e.g. \\server\share or…, Al pegar un enlace o archivo local en Notas o Diario, se añade automáticamente…, Habilita/inhabilita fecha y hora según los checks., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Guarda el título, descripción, etiquetas y fecha de vencimiento., Formatea y muestra la fecha y hora de última edición en la cabecera de NOTES., test_is_unc_path_detection()

### Community 108 - "NotificationsPopup"
Cohesion: 0.28
Nodes (6): NotificationsPopup, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, _swatch_icon(), test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 109 - "prompt_packs.py"
Cohesion: 0.20
Nodes (10): import_pack(), list_packs(), Packs de prompts del AI Prompt Clipboard de cada tablero. Usan el mismo esquema…, [(pack_id, nombre visible)]: primero los de fábrica, luego los importados., Normaliza una lista de prompts; ValueError si no sigue el esquema del Clipboard., Valida un pack JSON (p. ej. exportado de AI-Dev-Prompt-Clipboard), lo guarda…, _validate(), _pick_cli() (+2 more)

### Community 110 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 111 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 112 - "ImagePreviewDialog"
Cohesion: 0.11
Nodes (15): ImagePreviewDialog, pixmap_from_data_uri(), QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña… (+7 more)

### Community 113 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 114 - "test_board_reorder.py"
Cohesion: 0.39
Nodes (8): _board_drop_event(), _names(), #58: reordenar tableros arrastrándolos en la barra lateral (persistido en…, test_board_button_ignores_drag_of_itself(), test_boards_created_after_a_reorder_go_last(), test_dropping_a_board_on_another_reorders_sidebar_and_db(), test_move_board_before_and_after_target_persists_order(), test_reorder_keeps_archived_boards_in_place()

### Community 115 - "TaskTimerMixin"
Cohesion: 0.32
Nodes (5): Manejo de estado y UI del temporizador de tareas para TaskDetailDialog., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Actualiza el botón y la etiqueta de tiempo transcurrido según…, TaskTimerMixin

### Community 116 - "format_code_block_html"
Cohesion: 0.33
Nodes (7): format_code_block_html(), _get_warm_pygments_style(), Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting(), test_warm_syntax_highlighting_style()

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

### Community 127 - "_Runs"
Cohesion: 0.29
Nodes (6): ensure_mcp_registered(), Registra el servidor MCP del tablero en la CLI si aún no lo está. Devuelve (ok,…, subprocess.run simulado: devuelve el resultado indicado según el subcomando., _Runs, test_agy_mcp_uses_the_http_rpc_endpoint(), test_claude_mcp_is_added_in_the_repo_scope_only_when_missing()

### Community 128 - "2. Implementation Tasks"
Cohesion: 0.10
Nodes (19): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, #74 — Respuestas MCP en inglés para ahorrar tokens  `[A: S · B: S · C: M]`, #81 — PWA Ekin Móvil  `[XL — épica]`, #82 — Drag&Drop de archivos en Description y Journal  `[S]`, #83 — BUG: agente IA pasa una tarjeta a Done → quitar fecha  `[S]`, #84 — Revisión de AI PROMPTS y arquitectura de columnas  `[M]` (+11 more)

### Community 129 - "create_getting_started_board"
Cohesion: 0.50
Nodes (4): create_getting_started_board(), Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su…, Verifica que BoardViewWidget muestre y oculte el banner del tour según el…, test_board_view_interactive_tour_lifecycle()

### Community 130 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 131 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 132 - ".reload_logs"
Cohesion: 0.10
Nodes (11): _ClickOutsideFilter, QObject, Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Crea una nueva entrada de diario con el texto del input., Elimina una entrada de diario tras confirmación., Refresca los datos y el diario en vivo si un agente de IA modifica la tarea vía…, Mueve la barra de desplazamiento del diario hasta abajo., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo… (+3 more)

### Community 133 - ".check_for_updates"
Cohesion: 0.25
Nodes (4): Abre la pantalla de Ajustes (tema, notificaciones, idioma, updates, tour)., Verifica de forma silenciosa (o con feedback si manual=True) si hay…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica si hay actualizaciones en el repo de GitHub (modo git dev).

### Community 134 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 135 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 136 - "test_widgets_headless.py"
Cohesion: 0.07
Nodes (45): _card_with_timer(), _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _editor_with_all_selected(), _mention_editor(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, #68: subrayado desde el botón «U» y con Ctrl+U / Ctrl+S (Subrayado en Word en… (+37 more)

### Community 138 - ".load_board"
Cohesion: 0.08
Nodes (11): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Ejecuta una recarga suave y segura del tablero cuando el agente de IA realiza…, Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Abre el diálogo para crear una columna., Confirma y borra una columna. (+3 more)

### Community 139 - "QLabel"
Cohesion: 0.15
Nodes (9): CodeBlockDialog, LinkDialog, QDialog, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para configurar e insertar una tabla con número inicial de filas…, Diálogo modal para insertar un enlace (URL)., TableInsertDialog, Abre el diálogo para insertar o editar un enlace web. (+1 more)

### Community 140 - "test_prompt_clipboard.py"
Cohesion: 0.16
Nodes (19): load_pack(), _pack_path(), _dialog(), fixture, parametrize, #67: AI Prompt Clipboard por tablero (packs DEV / Opositor / GTD con el esquema…, #84: los prompts DEV adivinaban columnas por posición ("the column right after…, test_boards_created_from_templates_get_their_prompt_pack() (+11 more)

### Community 141 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 142 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 171 - "QWidget"
Cohesion: 0.14
Nodes (14): QWidget, QDialog, ShortcutsDialog, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Verifica que ShortcutsDialog carga y contiene los nuevos atajos de edición., Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, Regresión de la fuga de memoria: el diálogo real (parentado a MainWindow/…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog… (+6 more)

### Community 185 - "hex_to_rgb"
Cohesion: 0.50
Nodes (4): contrast_text(), hex_to_rgb(), Tinta (#201e1d) sobre fondos claros, crema (#f5ead8) sobre fondos oscuros —…, Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b).

### Community 190 - "BoardConfigDialog"
Cohesion: 0.29
Nodes (5): BoardConfigDialog, QDialog, Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…, Verifica que BoardConfigDialog muestre las opciones adecuadas según si el…, test_board_config_dialog_cloud_options()

### Community 191 - ".set_board"
Cohesion: 0.33
Nodes (3): Configura el watcher para detectar reactivamente cambios externos., Desvincula el tablero actual de su archivo compartido., Asigna el tablero activo e inicializa su estado y su vigilante de archivos.

### Community 192 - "_SseClientSession"
Cohesion: 0.29
Nodes (5): _SseClientSession, Verifica que el recolector de sesiones SSE elimine sesiones inactivas o…, Verifica el control de contrapresión y límite de cola en sesiones SSE., test_mcp_sse_send_to_session_queue_limit(), test_mcp_sse_session_scavenger()

### Community 196 - "mcp_server.py"
Cohesion: 0.12
Nodes (15): Exception, _DummySignal, get_mcp_tools_schema(), _masked(), McpEventBus, McpPermissionDenied, McpSecurityError, QObject (+7 more)

### Community 199 - "test_local_ai_rdi.py"
Cohesion: 0.19
Nodes (12): format_daily_standup_markdown(), generate_daily_standup_data(), Extrae métricas y estado del flujo del tablero para generar el informe Daily…, Formatea la estructura de standup_data en un reporte Markdown elegante., _active(), _agile_board(), Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi: - Fase 1:…, #84: la tarea activa se resuelve en el servidor (In Progress → Review → Ready)… (+4 more)

### Community 200 - "mcp_board"
Cohesion: 0.67
Nodes (3): mcp_board(), fixture, Crea un tablero de prueba con MCP activado y columnas.

### Community 201 - "task_mixins.py"
Cohesion: 0.33
Nodes (4): Mixins de funcionalidad modular para TaskDetailDialog (temporizadores,…, IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el…, Comprueba si existen tareas similares o duplicadas en este tablero., TaskAiMixin

### Community 210 - ".select_board"
Cohesion: 0.33
Nodes (3): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…

### Community 211 - ".get_pending_notifications"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

## Knowledge Gaps
- **149 isolated node(s):** `CliTool`, `ekin-kanban`, `1. Overview`, `2. Implementation Tasks`, `3. Acceptance Criteria` (+144 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **63 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `create_getting_started_board`, `test_main_window.py`, `.reload_logs`, `TaskDetailDialog`, `.check_for_updates`, `test_widgets_headless.py`, `.load_board`, `DashboardWidget`, `QLabel`, `._handle_key_press`, `PromptClipboardDialog`, `SettingsDialog`, `CommandPalette`, `LogEntryWidget`, `._rebuild_single_column`, `SidebarWidget`, `.reload_boards`, `RichTextToolbar`, `TaskCard`, `BoardSyncUiMixin`, `CalendarViewWidget`, `InteractiveTourBanner`, `MyWorkWidget`, `templates.py`, `McpSyncDialog`, `test_mcp.py`, `CalendarSettingsDialog`, `.contextMenuEvent`, `SearchDialog`, `security_utils.py`, `SaveAsTemplateDialog`, `QWidget`, `TagManagerDialog`, `summarize_diary_offline`, `BoardSelectionMixin`, `.delete_board`, `BulkAddTaskDialog`, `task_detail_dialog.py`, `ColorCirclesPicker`, `test_reminders.py`, `BoardConfigDialog`, `CreateBoardDialog`, `.__init__`, `test_start_working.py`, `DayCell`, `.show_command_palette`, `task_mixins.py`, `BoardButton`, `.delete_task`, `.__init__`, `.handle_task_drop`, `BoardViewWidget`, `export_dialog.py`, `BoardEditDialog`, `.render_tags`, `LandingTourDialog`, `ColumnWidget`, `lucide_icon`, `strings.py`, `set_language`, `TagPickerDialog`, `.load_task_data`, `NotificationsPopup`, `prompt_packs.py`, `.mouseReleaseEvent`, `ImagePreviewDialog`, `TaskTimerMixin`, `format_code_block_html`, `.notify_due_today`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `board_ops.py`, `ics_sync.py`, `links.py`, `test_local_dir.py`, `boards.py`, `tasks.py`, `sync.py`, `export_dialog.py`, `snapshots.py`, `connection.py`, `tags.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `BoardViewWidget` to `create_getting_started_board`, `._check_external_mcp_mutations`, `lucide_icon`, `strings.py`, `test_start_working.py`, `test_mcp.py`, `.load_board`, `PromptClipboardDialog`, `test_incremental_rendering.py`, `.__init__`, `.handle_task_drop`, `SettingsDialog`, `._rebuild_single_column`, `SidebarWidget`, `test_wip_limit.py`, `test_hover_expand.py`, `test_timer_board_view.py`, `_Runs`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `t()` (e.g. with `test_installer_download_thread()` and `test_board_view_mcp_btn_states()`) actually correct?**
  _`t()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `BoardViewWidget` (e.g. with `test_board_view_mcp_btn_states()` and `_Runs`) actually correct?**
  _`BoardViewWidget` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `TaskDetailDialog` (e.g. with `.open_task_details()` and `MarkdownTextEdit`) actually correct?**
  _`TaskDetailDialog` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MarkdownTextEdit` (e.g. with `_ClickOutsideFilter` and `TaskDetailDialog`) actually correct?**
  _`MarkdownTextEdit` has 2 INFERRED edges - model-reasoned connections that need verification._