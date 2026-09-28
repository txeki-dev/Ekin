# Graph Report - Ekin  (2026-09-28)

## Corpus Check
- 142 files · ~187,245 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2592 nodes · 4621 edges · 206 communities (149 shown, 57 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 175 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `45c232cc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- exporter.py
- test_main_window.py
- test_ics_export.py
- QDialog
- test_widgets_headless.py
- sync_board_with_file
- MarkdownTextEdit
- tasks.py
- get_connection
- DashboardWidget
- t
- ._handle_key_press
- BoardSyncController
- local_ai.py
- SettingsDialog
- test_mcp.py
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
- hex_to_rgb
- ClickableTagPill
- detect_available_llm
- MainWindow
- templates.py
- SyncResult
- McpSyncDialog
- boards.py
- McpProtocolHandler
- main
- DraggableColumnTitle
- CalendarSettingsDialog
- .contextMenuEvent
- SearchDialog
- TagManagerDialog
- InteractiveTourBanner
- Any
- McpManager
- CreateBoardDialog
- sync.py
- summarize_diary_offline
- .reload_logs
- BoardSelectionMixin
- snapshots.py
- test_templates.py
- MyWorkWidget
- test_hover_expand.py
- UndoManager
- Part B: Semantic Extraction (Subagents)
- ColorCirclesPicker
- FlowLayout
- test_reminders.py
- format_elapsed_time
- SaveAsTemplateDialog
- backup_database
- Release v0.6.0
- 2. Implementation Tasks
- ics_export.py
- CI Workflow (ruff + pytest)
- strings.py
- DayCell
- .show_command_palette
- BoardButton
- LocalAiCircuitBreaker
- test_incremental_rendering.py
- .__init__
- test_local_ai.py
- .__init__
- .handle_task_drop
- test_local_ai_rdi.py
- BoardViewWidget
- compute_drop_index
- export_dialog.py
- .sync_ics
- .open_board_config
- TaskDetailDialog
- lucide_icon
- ColumnWidget
- security_utils.py
- test_timer_board_view.py
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- TECHNICAL DESIGN DOCUMENT
- McpHttpHandler
- board_ops.py
- ics_sync.py
- task_detail_dialog.py
- .insertFromMimeData
- BoardMcpUiMixin
- McpHttpServer
- set_language
- BoardSyncWorker
- connect_shared_board_from_file
- ._change_list_indent
- ShortcutsDialog
- NotificationsPopup
- .delete_board
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
- ._update_mention_popup
- test_ux_enhancements.py
- create_getting_started_board
- build_qss
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- _is_unc_path
- .apply_theme
- Calendar Drag-to-Reschedule
- Cross-Repo Graph Merge
- _collapsed_column_widget
- QFrame
- .load_board
- TableInsertDialog
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
- .select_board
- create_log() Atomicity Fix (Fix 6)
- Dead app.setStyleSheet() Removal (Fix 8)
- Stale Shortcuts Help Text Fix (Fix 3)
- timer_alert_hours N+1 Read Fix (Fix 7)
- open_shortcuts_requested Signal
- add_column() board_id==-1 Guard Fix
- backlog.md — Ekin Kanban Backlog
- Token Reduction Benchmark
- transcribe_all() Video/Audio Transcription
- .get_pending_notifications
- Ekin App Icon
- ekin-kanban
- _editor_with_all_selected
- QDialog
- QTextEdit
- QWidget
- BulkAddTaskDialog
- BoardConfigDialog
- _shown_expanded_column
- QFrame
- QThread
- TagPickerDialog
- McpEventBus
- fixture
- ._check_external_mcp_mutations
- .init_ui
- CloudSyncInfoDialog
- TaskAiMixin
- Any
- QDialog
- QFrame
- QObject

## God Nodes (most connected - your core abstractions)
1. `t()` - 237 edges
2. `get_connection()` - 99 edges
3. `BoardViewWidget` - 96 edges
4. `TaskDetailDialog` - 88 edges
5. `MarkdownTextEdit` - 85 edges
6. `MainWindow` - 52 edges
7. `lucide_icon()` - 42 edges
8. `SidebarWidget` - 40 edges
9. `SettingsDialog` - 33 edges
10. `BoardSyncController` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_is_local_link_classifies_urls_vs_paths()` --calls--> `_is_local_link()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `test_add_link_with_local_path_renders_with_attachment_icon()` --calls--> `TaskDetailDialog`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/task_detail_dialog.py
- `test_add_link_with_web_url_renders_with_link_icon()` --calls--> `TaskDetailDialog`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/task_detail_dialog.py
- `test_browse_local_file_does_not_overwrite_existing_label()` --calls--> `TaskDetailDialog`  [INFERRED]
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

## Communities (206 total, 57 thin omitted)

### Community 1 - "exporter.py"
Cohesion: 0.10
Nodes (29): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas., Convierte HTML (descripción/nota) en texto plano limpio para exportar., Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags,…, Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como… (+21 more)

### Community 2 - "test_main_window.py"
Cohesion: 0.08
Nodes (39): get_default_db_path(), InstallerDownloadThread, parse_version_tuple(), Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, Muestra confirmación al usuario y descarga el instalador si acepta., ReleaseCheckThread, QThread, _close_window() (+31 more)

### Community 3 - "test_ics_export.py"
Cohesion: 0.14
Nodes (23): build_ics(), _escape(), _fold_line(), Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Deriva (SEQUENCE, LAST-MODIFIED) del `updated_at` de la tarea. SEQUENCE debe…, Pliega líneas a 75 octetos con continuación por espacio (RFC 5545 §3.1). La…, Construye el contenido .ics (texto) con las tareas que tienen due_date. Con…, _sequence_and_modified() (+15 more)

### Community 5 - "test_widgets_headless.py"
Cohesion: 0.08
Nodes (49): _card_with_timer(), _cleanup_dialog(), _make_task(), _mention_editor(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, Verifica que CloudSyncInfoDialog se construye con las instrucciones de los…, #61: archivos insertados en la Descripción o al editar una entrada ya publicada…, #63: «@» muestra los Enlaces / Adjuntos de la tarea y filtra con lo que se… (+41 more)

### Community 6 - "sync_board_with_file"
Cohesion: 0.07
Nodes (39): Ejecuta el ciclo completo de sincronización y fusión diferencial para un…, sync_board_with_file(), fixture, Verifica que cambios en el archivo remoto sin cambios locales se importan…, Crea una base de datos temporal para pruebas de sincronización., Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que desvincular un tablero borra sync_path y lo deja offline., Verifica que si local y remoto añaden tareas diferentes simultáneamente, la… (+31 more)

### Community 7 - "MarkdownTextEdit"
Cohesion: 0.05
Nodes (33): MarkdownTextEdit, Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Aplica interlineado proporcional (por defecto 135%) a todos los bloques del…, QTextEdit, Pegar una URL envuelve el texto seleccionado en un enlace <a href>, o inserta…, Hacer clic en un enlace web dentro del editor abre el navegador mediante…, Verifica que insert_table genera tablas estilo Word con celdas centradas. (+25 more)

### Community 8 - "tasks.py"
Cohesion: 0.07
Nodes (34): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), advance_overdue_recurring() (+26 more)

### Community 9 - "get_connection"
Cohesion: 0.16
Nodes (18): create_column(), delete_column(), get_column(), get_columns(), Pliega (collapsed=1) o despliega (0) una columna del tablero., Actualiza las posiciones de múltiples columnas. column_positions debe ser una…, set_column_collapsed(), update_column() (+10 more)

### Community 10 - "DashboardWidget"
Cohesion: 0.10
Nodes (20): _esc(), export_report_pdf(), gather_stats(), Métricas de tableros para el panel de Analíticas y la exportación a PDF.…, Recopila métricas transversales (todos los tableros activos)., Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)., Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)., render_report_html() (+12 more)

### Community 11 - "t"
Cohesion: 0.15
Nodes (10): PriorityManagerDialog, QDialog, Modal propio e independiente para gestionar los niveles y colores de Prioridad.…, Carga los datos iniciales de la tarea y sus logs desde la base de datos., Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Guarda el título, descripción, etiquetas y fecha de vencimiento., Formatea y muestra la fecha y hora de última edición en la cabecera de NOTES., QLabel (+2 more)

### Community 12 - "._handle_key_press"
Cohesion: 0.09
Nodes (11): Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Alinea el bloque de texto actual o selección a la izquierda., Centra el bloque de texto actual o selección., Alinea el bloque de texto actual o selección a la derecha., Justifica el bloque de texto actual o selección., Convierte el texto seleccionado (o la palabra bajo el cursor) a MAYÚSCULAS., Convierte el texto seleccionado (o la palabra bajo el cursor) a minúsculas. (+3 more)

### Community 13 - "BoardSyncController"
Cohesion: 0.09
Nodes (17): BoardSyncController, QObject, board_sync_controller.py - Controlador de sincronización desacoplado de…, Configura el watcher para detectar reactivamente cambios externos., Disparado por el sistema de archivos ante modificaciones externas., Desvincula el tablero actual de su archivo compartido., Espera a que termine cualquier hilo de sincronización en ejecución., Devuelve True si hay una sincronización en segundo plano activa. (+9 more)

### Community 14 - "local_ai.py"
Cohesion: 0.13
Nodes (22): compute_fallback_embedding(), cosine_similarity(), find_duplicate_tasks(), get_llm_circuit_breaker(), get_local_embedding(), index_task_embedding(), is_ollama_available(), Módulo de IA Local de Ekin. Tras #60 su alcance queda acotado a: 1. Detección… (+14 more)

### Community 15 - "SettingsDialog"
Cohesion: 0.08
Nodes (21): QCheckBox, QFrame, QDialog, Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Segmentado English / Español que maneja el lang_combo de respaldo., Segmentado Light / Dark que maneja el theme_combo de respaldo., Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de… (+13 more)

### Community 16 - "test_mcp.py"
Cohesion: 0.10
Nodes (23): main(), Punto de entrada de línea de comandos (CLI) para MCP vía transporte STDIO.…, Exception, authenticate_and_get_board(), get_mcp_manager(), McpPermissionDenied, McpSecurityError, Servidor MCP (Model Context Protocol) para Ekin Kanban. Permite a agentes de IA… (+15 more)

### Community 18 - "CommandPalette"
Cohesion: 0.14
Nodes (12): CommandPalette, QDialog, _swatch_icon(), Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, Verifica que CommandPalette no tenga WA_DeleteOnClose activo y no sufra…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query() (+4 more)

### Community 19 - "LogEntryWidget"
Cohesion: 0.07
Nodes (30): fit_html_images(), linkify_urls(), Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no…, Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,…, sanitize_chat_html(), LogEntryWidget, Actualiza el ancho de las imágenes y tablas del comentario para ajustarse al… (+22 more)

### Community 20 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 21 - "board_sync.py"
Cohesion: 0.12
Nodes (23): _apply_remote_board_clean(), calculate_file_hash(), create_premerge_backup(), _execute_two_way_merge(), export_board_to_sync_dict(), _merge_task_sub_entities(), now_utc_iso(), _prune_premerge_backups() (+15 more)

### Community 22 - "._rebuild_single_column"
Cohesion: 0.09
Nodes (12): Maneja las acciones interactivas directas asociadas a cada paso del tour., Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.… (+4 more)

### Community 23 - "SidebarWidget"
Cohesion: 0.13
Nodes (16): Persiste el nuevo orden y recoloca los botones sin recargar el tablero activo., SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir…, El fix del guard no debe bloquear el caso normal: con un tablero real…, test_add_column_shortcut_noop_when_no_board_selected() (+8 more)

### Community 24 - ".reload_boards"
Cohesion: 0.18
Nodes (6): Abre el diálogo para crear un nuevo tablero a partir de una plantilla o en…, Re-aplica los colores dependientes del tema en los widgets de la barra lateral…, Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Permite al usuario seleccionar un archivo .ekboard compartido existente y…, Gestiona las acciones de sincronización solicitadas desde el menú contextual de…, Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…

### Community 25 - "connection.py"
Cohesion: 0.12
Nodes (17): Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, init_db(), Crea las tablas necesarias si no existen., get_active_timer_tasks(), get_scheduled_tasks(), get_task_board_id(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve el board_id al que pertenece una tarea (o None si no existe). (+9 more)

### Community 26 - "RichTextToolbar"
Cohesion: 0.08
Nodes (15): _align_icon(), _color_icon(), Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar, apply_text_color aplica el color especificado al texto seleccionado. (+7 more)

### Community 27 - "TaskCard"
Cohesion: 0.11
Nodes (10): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, test_task_card_ctrl_click_and_selection_state(), Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la…, Activa o desactiva el estado visual de selección múltiple., Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Umbral (en horas) a partir del cual la insignia del temporizador se resalta en…, Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo…, Limpia y dibuja las etiquetas actuales y la fecha de vencimiento. (+2 more)

### Community 28 - "BoardSyncUiMixin"
Cohesion: 0.09
Nodes (13): BoardSyncUiMixin, Maneja el clic en el botón de sincronización de la cabecera., Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para…, Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Compatibilidad hacia atrás: actualiza el controlador de sincronización. (+5 more)

### Community 29 - "CalendarViewWidget"
Cohesion: 0.12
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 30 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 31 - "hex_to_rgb"
Cohesion: 0.50
Nodes (4): contrast_text(), hex_to_rgb(), Tinta (#201e1d) sobre fondos claros, crema (#f5ead8) sobre fondos oscuros —…, Convierte un color hexadecimal en formato string a una tupla RGB (r, g, b).

### Community 32 - "ClickableTagPill"
Cohesion: 0.50
Nodes (3): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…

### Community 33 - "detect_available_llm"
Cohesion: 0.16
Nodes (14): check_http_endpoint(), detect_available_llm(), get_ollama_models(), is_model_downloaded(), is_runner_installed(), Detecta qué servicio de LLM local está disponible en el equipo., Inicia en segundo plano el ejecutable portable llama-server con el modelo Qwen…, Verifica si el modelo Qwen 2.5 Coder existe localmente y no está vacío. (+6 more)

### Community 34 - "MainWindow"
Cohesion: 0.08
Nodes (12): MainWindow, Manejador si el tablero actual cambió en el sidebar., Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Sincroniza inmediatamente el tablero activo con su archivo en la nube., Abre el diálogo para vincular el tablero activo a un nuevo archivo .ekboard., Abre la carpeta de logs de diagnóstico en el explorador de archivos., Una vez por semana ISO (si está activado), muestra el resumen semanal:… (+4 more)

### Community 35 - "templates.py"
Cohesion: 0.16
Nodes (19): apply_template_to_board(), BoardTemplate, ColumnTemplate, export_board_to_template(), get_all_templates(), get_builtin_templates(), get_template_by_id(), Any (+11 more)

### Community 36 - "SyncResult"
Cohesion: 0.14
Nodes (14): format_sync_summary(), Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Genera un resumen conciso de un SyncResult para mostrar en la interfaz., Exporta automáticamente los cambios locales si el tablero está vinculado., Resultado de una operación de sincronización. (+6 more)

### Community 37 - "McpSyncDialog"
Cohesion: 0.21
Nodes (7): McpSyncDialog, QDialog, QPushButton, QTextEdit, Diálogo modal para configurar la sincronización de un tablero con agentes de IA…, Prueba el diálogo modal de configuración McpSyncDialog., test_mcp_sync_dialog_headless()

### Community 38 - "boards.py"
Cohesion: 0.11
Nodes (18): create_board(), delete_board(), get_board(), get_board_by_uuid(), get_board_mutation_fingerprint(), get_boards(), move_board(), Recuerda el pack del AI Prompt Clipboard elegido para el tablero. (+10 more)

### Community 39 - "McpProtocolHandler"
Cohesion: 0.10
Nodes (19): get_mcp_tools_schema(), McpProtocolHandler, Retorna la especificación JSON-Schema de las herramientas expuestas por Ekin…, Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol., list_tasks no debe filtrar al agente el HTML/CSS de Qt (DOCTYPE, <style>, etc.)., list_tasks tenía un primer bucle muerto que repetía las consultas de cada…, Verifica que el prompt contextual del tablero (Scrum Master / Opositor) se…, Prueba la búsqueda semántica basada en embeddings a través de la herramienta… (+11 more)

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
Cohesion: 0.12
Nodes (10): format_single_cell(), format_table_all_cells(), Utilidades compartidas para procesamiento y saneamiento de HTML en…, Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen. (+2 more)

### Community 44 - "SearchDialog"
Cohesion: 0.19
Nodes (8): Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon(), Verifica que SearchDialog liste tareas, filtre por texto/tablero y emita…, test_search_dialog_filters_and_activation()

### Community 45 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 46 - "InteractiveTourBanner"
Cohesion: 0.19
Nodes (7): InteractiveTourBanner, Barra superior interactiva in-situ para guiar al usuario a través del tablero…, Aplica colores y refresca los textos según el idioma y tema actuales., Verifica la navegación paso a paso, emisión de señales y finalización de…, Verifica que el botón cerrar descarte el tour y persista…, test_interactive_tour_banner_dismiss(), test_interactive_tour_banner_navigation_and_actions()

### Community 47 - "Any"
Cohesion: 0.21
Nodes (4): Any, get_mcp_event_bus(), McpToolExecutor, Ejecuta herramientas MCP garantizando que no se sobrepasen los límites del…

### Community 48 - "McpManager"
Cohesion: 0.24
Nodes (4): McpManager, Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban., Prueba el servidor HTTP embebido realizando peticiones directas., test_mcp_http_server_live()

### Community 49 - "CreateBoardDialog"
Cohesion: 0.20
Nodes (4): CreateBoardDialog, QFrame, Diálogo visual moderno para crear un nuevo tablero a partir de una plantilla o…, test_create_board_dialog_headless()

### Community 50 - "sync.py"
Cohesion: 0.13
Nodes (14): get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero., Actualiza la marca de tiempo de sincronización y el hash del archivo., Desvincula un tablero de su archivo compartido, volviéndolo 100% local/offline. (+6 more)

### Community 51 - "summarize_diary_offline"
Cohesion: 0.40
Nodes (5): Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas)…, summarize_diary_offline(), Pruebas del resumen determinista del diario (local_ai.summarize_diary_offline),…, test_summarize_diary_offline_builds_two_sections(), test_summarize_diary_offline_empty()

### Community 52 - ".reload_logs"
Cohesion: 0.10
Nodes (11): _ClickOutsideFilter, QObject, Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Crea una nueva entrada de diario con el texto del input., Elimina una entrada de diario tras confirmación., Refresca los datos y el diario en vivo si un agente de IA modifica la tarea vía…, Mueve la barra de desplazamiento del diario hasta abajo., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo… (+3 more)

### Community 53 - "BoardSelectionMixin"
Cohesion: 0.21
Nodes (7): BoardSelectionMixin, Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej.…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero., Escape deselecciona tarjetas múltiples.

### Community 54 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 55 - "test_templates.py"
Cohesion: 0.17
Nodes (18): create_board_from_template(), delete_custom_template(), get_custom_templates(), get_templates_dir(), Devuelve la ruta al directorio donde se guardan las plantillas personalizadas…, Carga todas las plantillas de usuario personalizadas desde archivos JSON., Guarda una plantilla personalizada como archivo JSON en el directorio de…, Elimina una plantilla personalizada de disco si existe, con validación anti… (+10 more)

### Community 56 - "MyWorkWidget"
Cohesion: 0.16
Nodes (17): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon() (+9 more)

### Community 57 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 58 - "UndoManager"
Cohesion: 0.18
Nodes (9): Pruebas unitarias para UndoManager y UndoAction., test_undo_manager_initial_state(), test_undo_manager_max_depth(), test_undo_manager_push_clears_redo(), test_undo_manager_push_enables_can_undo(), test_undo_manager_undo_and_redo_lifecycle(), Pila simple de deshacer/rehacer para acciones destructivas (borrar…, UndoAction (+1 more)

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
Cohesion: 0.14
Nodes (20): current_week_key(), QDialog, Recordatorios anticipados y resumen semanal (weekly review). La decisión de…, Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, should_show_weekly_digest() (+12 more)

### Community 63 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 64 - "SaveAsTemplateDialog"
Cohesion: 0.20
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

### Community 68 - "ics_export.py"
Cohesion: 0.24
Nodes (8): clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, export_ics(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar., _strip_html()

### Community 69 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 70 - "strings.py"
Cohesion: 0.08
Nodes (25): Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, board_mixins.py - Mixins modulares para BoardViewWidget. Separa la gestión de…, Diálogos para la selección, creación y gestión de plantillas de tableros en…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando… (+17 more)

### Community 71 - "DayCell"
Cohesion: 0.20
Nodes (5): DayCell, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon(), Verifica que _on_task_rescheduled actualice la fecha en la BD y emita…, test_calendar_view_on_task_rescheduled_and_drag_drop()

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

### Community 76 - ".__init__"
Cohesion: 0.20
Nodes (5): CalendarChip, QFrame, QPushButton, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes).

### Community 77 - "test_local_ai.py"
Cohesion: 0.15
Nodes (16): download_and_extract_runner(), get_runner_download_url(), Devuelve la URL oficial de descarga del binario portable de llama-server según…, Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens…, Descarga y extrae el ejecutable portable de llama-server en runner_dir., stream_openai_chat_completion(), Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py)., Verifica que get_runner_download_url retorna una URL válida con terminación… (+8 more)

### Community 78 - ".__init__"
Cohesion: 0.17
Nodes (6): app_icon(), Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo…, QWidget

### Community 79 - ".handle_task_drop"
Cohesion: 0.20
Nodes (5): Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta…, Maneja la recolocación en lote de múltiples tareas tras arrastrarlas., Soltar un lote de tarjetas sobre una columna plegada: la despliega y coloca las…, Registra una acción deshacer/rehacer para el movimiento (individual o en lote)…, Maneja la lógica de recolocación de tareas (individual o por lote) tras…

### Community 80 - "test_local_ai_rdi.py"
Cohesion: 0.20
Nodes (7): format_daily_standup_markdown(), generate_daily_standup_data(), Extrae métricas y estado del flujo del tablero para generar el informe Daily…, Formatea la estructura de standup_data en un reporte Markdown elegante., Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi: - Fase 1:…, test_generate_daily_standup_data_and_markdown(), test_mcp_new_tools_and_mask_sensitive()

### Community 81 - "BoardViewWidget"
Cohesion: 0.08
Nodes (25): BoardViewWidget, Muestra la barra del tour interactivo in-situ y navega al paso especificado., Oculta la barra del tour interactivo in-situ., Muestra celebración tras completar los 4 pasos del tour interactivo., Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Espera a que termine cualquier hilo de sincronización activo antes de destruir…, BoardMcpUiMixin, BoardSelectionMixin (+17 more)

### Community 82 - "compute_drop_index"
Cohesion: 0.33
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una o varias tarjetas soltadas en `drop_y`.…

### Community 83 - "export_dialog.py"
Cohesion: 0.12
Nodes (12): ExportDialog, ImportConfirmationDialog, QDialog, Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Diálogo modal para confirmar la importación de tableros desde JSON., Genera una cadena amigable para nombres de archivo., Diálogo modal para configurar y ejecutar la exportación de tableros., _slugify() (+4 more)

### Community 84 - ".sync_ics"
Cohesion: 0.22
Nodes (3): Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde el calendario: abrir el detalle y quedarnos en el calendario., Reescribe cada feed .ics con auto-sync configurado (el global de todos los…

### Community 85 - ".open_board_config"
Cohesion: 0.12
Nodes (7): BoardEditDialog, Abre el diálogo para editar el nombre y color del tablero activo., Abre el diálogo para copiar el tablero activo con un nuevo nombre., Diálogo personalizado para crear o editar un tablero (nombre y color de fondo)., Archiva/desarchiva un tablero y recarga la lista., Abre el modal de opciones del tablero activo y ejecuta la acción elegida., Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo).

### Community 86 - "TaskDetailDialog"
Cohesion: 0.04
Nodes (32): QDialog, Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la…, Ancho máximo (px) para imágenes en las notas (panel izquierdo ancho)., Al pegar un enlace o archivo local en Notas o Diario, se añade automáticamente…, Enlaces / Adjuntos actuales de la tarea que se ofrecen al escribir «@»., Habilita/inhabilita fecha y hora según los checks., Dibuja las etiquetas asignadas como pastillas (excluyendo Prioridad, que tiene… (+24 more)

### Community 87 - "lucide_icon"
Cohesion: 0.16
Nodes (10): Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)., lucide_icon(), QIcon del icono Lucide `name` trazado en `color`., LandingTourDialog, QDialog, Diálogo modal interactivo para guiar al usuario en las capacidades clave de…, Verifica la navegación paso a paso y la persistencia de LandingTourDialog., Verifica que el checkbox 'No volver a mostrar' persista inmediatamente el… (+2 more)

### Community 88 - "ColumnWidget"
Cohesion: 0.15
Nodes (8): test_column_widget_mouse_press_emits_column_activated(), ColumnWidget, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada)., Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…

### Community 89 - "security_utils.py"
Cohesion: 0.29
Nodes (9): confirm_open_untrusted_link(), _get_target_extension(), _is_local_link(), open_link_safely(), Utilidades de seguridad para la validación y apertura segura de hipervínculos y…, Abre de forma segura una URL o ruta local tras verificar su nivel de confianza.…, True si la cadena representa una ruta de archivo local o de red (UNC / relativa…, Extracts the lowercased file extension from a local path or file URL. (+1 more)

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

### Community 96 - "McpHttpHandler"
Cohesion: 0.27
Nodes (5): BaseHTTPRequestHandler, McpHttpHandler, Manejador HTTP para Server-Sent Events (SSE) y llamadas JSON-RPC directas., Envía cabeceras CORS restrictivas para evitar que sitios web maliciosos lean…, Maneja peticiones preflight CORS de clientes web o navegadores.

### Community 97 - "board_ops.py"
Cohesion: 0.28
Nodes (8): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), move_column_to_board(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…, Mueve una columna a otro tablero y la coloca al final de su lista de columnas.

### Community 98 - "ics_sync.py"
Cohesion: 0.22
Nodes (8): delete_board_ics_sync_path(), get_all_board_ics_sync_paths(), get_board_ics_sync_path(), Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene., Crea o actualiza la ruta de auto-sync de un tablero., Desactiva la sincronización automática de un tablero., Devuelve {board_id: path} para todos los tableros con auto-sync configurado., set_board_ics_sync_path()

### Community 99 - "task_detail_dialog.py"
Cohesion: 0.14
Nodes (13): ensure_priority_category(), Garantiza la existencia de la categoría 'Priority' y sus valores iniciales si…, color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas)., Devuelve el id de la etiqueta permanente «Prioridad»., Abre el modal propio e independiente de Prioridades., Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Pruebas unitarias para la independización de la categoría 'Priority' y su modal… (+5 more)

### Community 100 - ".insertFromMimeData"
Cohesion: 0.14
Nodes (8): apply_word_style_to_qt_table(), Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Al pegar: archivos locales se insertan como enlaces y se emite señal para…, Inserta cada archivo local como enlace «📄 nombre» y emite local_link_pasted…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor con diseño estilo…, Codifica un QImage como data URI PNG en base64., Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se…

### Community 101 - "BoardMcpUiMixin"
Cohesion: 0.29
Nodes (5): BoardMcpUiMixin, Manejo de la interfaz del botón de integración MCP en la cabecera del tablero., Actualiza el estado visual del botón MCP en la cabecera del tablero., Abre el diálogo modal de configuración MCP para el tablero actual., Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el…

### Community 102 - "McpHttpServer"
Cohesion: 0.18
Nodes (4): McpHttpServer, Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies., Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria., ThreadingHTTPServer

### Community 103 - "set_language"
Cohesion: 0.20
Nodes (11): get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), Verifica que CalendarViewWidget obtenga nombres de meses y días de la semana…, test_calendar_view_weekdays_and_months_localization() (+3 more)

### Community 104 - "BoardSyncWorker"
Cohesion: 0.25
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 105 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, Carga y conecta a la base de datos local un tablero sincronizado existente…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 107 - "ShortcutsDialog"
Cohesion: 0.24
Nodes (6): Abre la ventana de referencia de atajos de teclado (Ctrl+/)., QDialog, ShortcutsDialog, Verifica que ShortcutsDialog carga y contiene los nuevos atajos de edición., test_shortcuts_dialog_constructs_with_both_sections(), test_shortcuts_dialog_includes_new_editor_shortcuts()

### Community 108 - "NotificationsPopup"
Cohesion: 0.28
Nodes (6): NotificationsPopup, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, _swatch_icon(), test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 110 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 111 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 112 - "ImagePreviewDialog"
Cohesion: 0.08
Nodes (19): ImagePreviewDialog, pixmap_from_data_uri(), QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Sustituye el contenido por un editor en línea con Guardar/Cancelar y soporte de… (+11 more)

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
Cohesion: 0.20
Nodes (9): format_code_block_html(), _get_warm_pygments_style(), Abre el diálogo para insertar un bloque de código formateado., Inserta un bloque de código formateado con resaltado de sintaxis., Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting() (+1 more)

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

### Community 127 - "._update_mention_popup"
Cohesion: 0.25
Nodes (3): Texto escrito tras un «@» que abre una mención (a inicio de línea o tras un…, Muestra, filtra u oculta el desplegable de menciones según el texto tras «@»., Sustituye «@texto» por un enlace al adjunto elegido («📄 nombre» o «🔗 nombre»).

### Community 128 - "test_ux_enhancements.py"
Cohesion: 0.11
Nodes (17): Pruebas exhaustivas para las 4 mejoras de UX: 1. Tablas interactivas y formato…, Verifica las proporciones, márgenes simétricos, scroll fluido y edición in-…, Verifica inserción inicial de tabla y manipulación mediante acciones de…, Verifica la eliminación total de CSS (<style>) residual de Qt., Verifica que los metadatos se organicen en 4 filas dentro del panel izquierdo,…, Verifica que TaskDetailDialog cargue de forma diferida (windowed) las entradas…, Verifica que pixmap_from_data_uri utilice QPixmapCache para data URIs base64., Verifica que escribir en una cita con placeholder borra el placeholder… (+9 more)

### Community 129 - "create_getting_started_board"
Cohesion: 0.50
Nodes (4): create_getting_started_board(), Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su…, Verifica que BoardViewWidget muestre y oculte el banner del tour según el…, test_board_view_interactive_tour_lifecycle()

### Community 130 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 131 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 132 - "_is_unc_path"
Cohesion: 0.67
Nodes (3): _is_unc_path(), r"""True if url targets a network share (UNC path, e.g. \\server\share or…, test_is_unc_path_detection()

### Community 133 - ".apply_theme"
Cohesion: 0.18
Nodes (5): Aplica el tema (oscuro/claro) al vuelo. `reload` recarga el tablero para que…, Abre la pantalla de Ajustes (tema, notificaciones, idioma, updates, tour)., Verifica de forma silenciosa (o con feedback si manual=True) si hay…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica si hay actualizaciones en el repo de GitHub (modo git dev).

### Community 134 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 135 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 136 - "_collapsed_column_widget"
Cohesion: 0.36
Nodes (8): _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _task_drag_mime(), test_hover_timeout_emits_signal_only_while_collapsed(), test_hover_timer_starts_on_drag_enter(), test_hover_timer_stops_on_drag_leave(), test_hover_timer_stops_on_drop_before_timeout()

### Community 138 - ".load_board"
Cohesion: 0.09
Nodes (10): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Ejecuta una recarga suave y segura del tablero cuando el agente de IA realiza…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Abre el diálogo para crear una columna., Confirma y borra una columna., Reordena las columnas del tablero actual tras arrastrar una por su título. (+2 more)

### Community 139 - "TableInsertDialog"
Cohesion: 0.12
Nodes (11): CodeBlockDialog, LinkDialog, QDialog, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para configurar e insertar una tabla con número inicial de filas…, Diálogo modal para insertar un enlace (URL)., TableInsertDialog, Abre el diálogo para insertar o editar un enlace web. (+3 more)

### Community 140 - "test_prompt_clipboard.py"
Cohesion: 0.05
Nodes (48): Abre el AI Prompt Clipboard con el pack de prompts del tablero activo., fixture, claude_code_server_name(), Nombre del servidor MCP del tablero en el comando `claude mcp add` (p. ej.…, parametrize, ask_variable_values(), PromptClipboardDialog, Copia el prompt seleccionado con las variables del tablero; pide las que falten. (+40 more)

### Community 141 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 142 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 171 - ".select_board"
Cohesion: 0.33
Nodes (3): Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…, Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…

### Community 181 - ".get_pending_notifications"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

### Community 185 - "_editor_with_all_selected"
Cohesion: 0.33
Nodes (6): _editor_with_all_selected(), #68: subrayado desde el botón «U» y con Ctrl+U / Ctrl+S (Subrayado en Word en…, #62: el botón «1.» convierte las líneas seleccionadas en una lista numerada., test_ctrl_shift_u_still_uppercases_not_underlines(), test_numbering_button_turns_selected_lines_into_numbered_list(), test_underline_button_and_shortcuts_toggle_underline()

### Community 190 - "BulkAddTaskDialog"
Cohesion: 0.17
Nodes (8): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., Verifica que BulkAddTaskDialog crea múltiples tareas en las columnas…, Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, test_bulk_add_task_dialog(), test_secondary_dialogs_schedule_delete_later_on_finished()

### Community 191 - "BoardConfigDialog"
Cohesion: 0.22
Nodes (4): BoardConfigDialog, Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…, Verifica que BoardConfigDialog muestre las opciones adecuadas según si el…, test_board_config_dialog_cloud_options()

### Community 192 - "_shown_expanded_column"
Cohesion: 0.50
Nodes (4): #59: un nombre largo no debe cortarse a mitad de carácter ni empujar los…, _shown_expanded_column(), test_column_title_elides_long_name_to_fit_header(), test_column_title_short_name_is_not_elided()

### Community 195 - "TagPickerDialog"
Cohesion: 0.29
Nodes (4): QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog

### Community 196 - "McpEventBus"
Cohesion: 0.25
Nodes (5): _DummySignal, McpEventBus, QObject, Emite señales Qt cuando el agente IA modifica datos a través de MCP., Fallback sin interfaz gráfica Qt cuando se ejecuta en entornos headless puros.

### Community 199 - ".init_ui"
Cohesion: 0.40
Nodes (3): lucide_pixmap(), QPixmap cuadrado (size x size) del icono Lucide `name`, trazado en `color`., _svg_data()

### Community 200 - "CloudSyncInfoDialog"
Cohesion: 0.50
Nodes (3): CloudSyncInfoDialog, QDialog, Diálogo modal explicativo previo a seleccionar la ruta de sincronización en la…

### Community 201 - "TaskAiMixin"
Cohesion: 0.50
Nodes (3): IA local por tarea para TaskDetailDialog: detección de tareas duplicadas en el…, Comprueba si existen tareas similares o duplicadas en este tablero., TaskAiMixin

## Knowledge Gaps
- **132 isolated node(s):** `ekin-kanban`, `1. Overview`, `2. Implementation Tasks`, `3. Acceptance Criteria`, `QA Report` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **57 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `create_getting_started_board`, `test_main_window.py`, `.apply_theme`, `test_widgets_headless.py`, `.load_board`, `DashboardWidget`, `._handle_key_press`, `BoardSyncController`, `local_ai.py`, `test_prompt_clipboard.py`, `test_mcp.py`, `SettingsDialog`, `CommandPalette`, `LogEntryWidget`, `._rebuild_single_column`, `SidebarWidget`, `.reload_boards`, `RichTextToolbar`, `TaskCard`, `BoardSyncUiMixin`, `CalendarViewWidget`, `templates.py`, `SyncResult`, `McpSyncDialog`, `CalendarSettingsDialog`, `.contextMenuEvent`, `SearchDialog`, `TagManagerDialog`, `InteractiveTourBanner`, `CreateBoardDialog`, `summarize_diary_offline`, `.reload_logs`, `BoardSelectionMixin`, `MyWorkWidget`, `ColorCirclesPicker`, `BulkAddTaskDialog`, `test_reminders.py`, `SaveAsTemplateDialog`, `BoardConfigDialog`, `TagPickerDialog`, `strings.py`, `.init_ui`, `DayCell`, `CloudSyncInfoDialog`, `TaskAiMixin`, `.show_command_palette`, `.__init__`, `BoardButton`, `.__init__`, `.handle_task_drop`, `BoardViewWidget`, `export_dialog.py`, `.open_board_config`, `TaskDetailDialog`, `lucide_icon`, `ColumnWidget`, `security_utils.py`, `task_detail_dialog.py`, `BoardMcpUiMixin`, `set_language`, `ShortcutsDialog`, `NotificationsPopup`, `.delete_board`, `.mouseReleaseEvent`, `ImagePreviewDialog`, `TaskTimerMixin`, `format_code_block_html`, `.notify_due_today`?**
  _High betweenness centrality (0.372) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `board_ops.py`, `ics_sync.py`, `exporter.py`, `boards.py`, `tasks.py`, `sync.py`, `export_dialog.py`, `snapshots.py`, `connection.py`, `tags.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `BoardViewWidget` to `create_getting_started_board`, `._check_external_mcp_mutations`, `strings.py`, `.init_ui`, `.load_board`, `test_incremental_rendering.py`, `test_prompt_clipboard.py`, `.__init__`, `.handle_task_drop`, `SettingsDialog`, `SidebarWidget`, `._rebuild_single_column`, `lucide_icon`, `test_wip_limit.py`, `test_hover_expand.py`, `test_timer_board_view.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `BoardViewWidget` (e.g. with `PromptClipboardDialog` and `test_board_view_mcp_btn_states()`) actually correct?**
  _`BoardViewWidget` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `TaskDetailDialog` (e.g. with `.open_task_details()` and `LogEntryWidget`) actually correct?**
  _`TaskDetailDialog` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `MarkdownTextEdit` (e.g. with `test_markdown_edit_case_conversions()` and `test_markdown_edit_image_resize_methods()`) actually correct?**
  _`MarkdownTextEdit` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ekin-kanban`, `1. Overview`, `2. Implementation Tasks` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._