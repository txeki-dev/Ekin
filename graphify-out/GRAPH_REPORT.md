# Graph Report - Ekin  (2026-09-13)

## Corpus Check
- 118 files · ~152,417 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2114 nodes · 3918 edges · 169 communities (110 shown, 59 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 223 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `97be14a8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CalendarViewWidget
- MarkdownTextEdit
- CalendarSettingsDialog
- DashboardWidget
- tasks.py
- /graphify Pipeline
- test_widgets_headless.py
- snapshots.py
- 2. Implementation Tasks
- tags.py
- SpecGenerationThread
- exporter.py
- BoardViewWidget
- get_connection
- ColorCirclesPicker
- generate_structural_spec
- AiSpecDialog
- test_local_ai.py
- test_hover_expand.py
- Part B: Semantic Extraction (Subagents)
- sidebar.py
- .mouseReleaseEvent
- ColumnWidget
- test_reminders.py
- MainWindow
- Release v0.6.0
- CI Workflow (ruff + pytest)
- markdown_edit.py
- connection.py
- format_elapsed_time
- SyncResult
- ._insert_image
- backup_database
- main
- compute_drop_index
- BoardButton
- test_main_window.py
- sync_board_with_file
- RichTextToolbar
- TECHNICAL DESIGN DOCUMENT
- board_sync.py
- .contextMenuEvent
- test_timer_board_view.py
- t
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- board_ops.py
- ics_sync.py
- FlowLayout
- LogEntryWidget
- SidebarWidget
- BoardSyncController
- CLAUDE.md
- .__init__
- conftest.py
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- CommandPalette
- TaskCard
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- .check_for_updates
- TagManagerDialog
- local_ai.py
- ._build_column_widget
- TECHNICAL DESIGN DOCUMENT
- VerticalLabel
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- TECHNICAL DESIGN DOCUMENT
- test_ics_export.py
- Calendar Drag-to-Reschedule
- .__init__
- TaskListArea
- Cross-Repo Graph Merge
- sync.py
- ColumnEditDialog
- .reload_logs
- test_snapshot_and_restore_preserves_uuids
- get_subtasks_progress_bulk() Function
- v0.9.1: Local File Attachments on Task Links
- UndoManager
- extract_release_notes.py
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
- task_detail_dialog.py
- BoardColumnsArea
- TECHNICAL DESIGN DOCUMENT
- ._build_link_row
- test_create_log_has_no_intermediate_commit_call
- test_db_name_is_resolved_at_call_time
- test_restore_task_returns_none_if_column_was_deleted_in_the_meantime
- test_restore_column_returns_none_if_board_was_deleted_in_the_meantime
- test_snapshot_and_restore_task_preserves_link_order
- DraggableColumnTitle
- create_log() Atomicity Fix (Fix 6)
- Dead app.setStyleSheet() Removal (Fix 8)
- Stale Shortcuts Help Text Fix (Fix 3)
- timer_alert_hours N+1 Read Fix (Fix 7)
- open_shortcuts_requested Signal
- add_column() board_id==-1 Guard Fix
- backlog.md — Ekin Kanban Backlog
- Token Reduction Benchmark
- transcribe_all() Video/Audio Transcription
- Ekin App Icon
- ekin-kanban
- BoardSyncWorker
- ._rebuild_single_column
- main.py
- SettingsDialog
- MyWorkWidget
- connect_shared_board_from_file
- InstallerDownloadThread
- test_ai_assist.py
- _card_with_timer
- SearchDialog
- ImagePreviewDialog
- BoardEditDialog
- .notify_due_today
- .load_board
- ._adjust_logs_width
- test_incremental_rendering.py
- .set_card_style
- .load_task_data
- download_and_extract_runner
- .render_tags
- .update_timer_badge
- .delete_log_entry
- test_create_tasks_batch
- TagPickerDialog
- CodeBlockDialog
- .delete_task
- build_qss
- clean_html_description
- ._confirm_open_untrusted_link
- _collapsed_column_widget
- ._chat_image_width
- format_code_block_html
- bump_version.py
- test_wip_limit.py
- ._notes_image_width
- test_sidebar_board_button_cloud_badge
- ._refresh_priority_combo
- test_cloud_sync_info_dialog_constructs_and_accepts
- test_board_view_sync_btn_states
- .apply_theme
- test_bulk_queries_chunking_handles_large_task_lists
- test_copy_operations_generate_uuids
- test_save_task_full_atomic_update
- test_snapshot_and_restore_board_single_connection
- test_ux_enhancements.py
- test_board_view_multi_selection_bar_and_escape
- test_shortcuts_dialog_includes_new_editor_shortcuts
- test_shortcuts_item_new_task_describes_last_active_column_behavior

## God Nodes (most connected - your core abstractions)
1. `t()` - 202 edges
2. `BoardViewWidget` - 108 edges
3. `get_connection()` - 98 edges
4. `TaskDetailDialog` - 94 edges
5. `MarkdownTextEdit` - 79 edges
6. `MainWindow` - 54 edges
7. `SidebarWidget` - 46 edges
8. `lucide_icon()` - 35 edges
9. `AiSpecDialog` - 31 edges
10. `BoardSyncController` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `_ClickOutsideFilter` --uses--> `AiAssistDialog`  [INFERRED]
  detail_dialog/task_detail_dialog.py → ai_assist_dialog.py
- `TaskDetailDialog` --uses--> `AiAssistDialog`  [INFERRED]
  detail_dialog/task_detail_dialog.py → ai_assist_dialog.py
- `BoardViewWidget` --uses--> `AiSpecDialog`  [INFERRED]
  board_view.py → ai_spec_dialog.py
- `BoardColumnsArea` --uses--> `ColorCirclesPicker`  [INFERRED]
  board_dialogs.py → color_picker.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (169 total, 59 thin omitted)

### Community 0 - "CalendarViewWidget"
Cohesion: 0.13
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 2 - "MarkdownTextEdit"
Cohesion: 0.04
Nodes (47): MarkdownTextEdit, Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Elige el símbolo de viñeta según el nivel de anidamiento (las listas numeradas…, Aumenta (Tab) o reduce (Shift+Tab) el nivel de anidamiento de la viñeta actual., Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Alinea el bloque de texto actual o selección a la izquierda. (+39 more)

### Community 3 - "CalendarSettingsDialog"
Cohesion: 0.16
Nodes (8): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud).

### Community 4 - "DashboardWidget"
Cohesion: 0.10
Nodes (20): _esc(), export_report_pdf(), gather_stats(), Métricas de tableros para el panel de Analíticas y la exportación a PDF.…, Recopila métricas transversales (todos los tableros activos)., Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)., Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)., render_report_html() (+12 more)

### Community 5 - "tasks.py"
Cohesion: 0.06
Nodes (35): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), advance_overdue_recurring() (+27 more)

### Community 6 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 7 - "test_widgets_headless.py"
Cohesion: 0.11
Nodes (40): QDialog, TaskDetailDialog, _cleanup_dialog(), _make_task(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Clics dentro de los controles de TaskDetailDialog no deben disparar el…, Al abrir TaskDetailDialog con múltiples comentarios, el scroll muestra el… (+32 more)

### Community 8 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 9 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 10 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 11 - "SpecGenerationThread"
Cohesion: 0.29
Nodes (5): QThread, Hilo para ejecutar la inferencia de la SPEC en segundo plano con soporte de…, SpecGenerationThread, Verifica que un fallo a mitad de streaming emita error_occurred sin corromper…, test_spec_generation_thread_error_handling_and_cancellation()

### Community 12 - "exporter.py"
Cohesion: 0.10
Nodes (29): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas., Convierte HTML (descripción/nota) en texto plano limpio para exportar., Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags,…, Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como… (+21 more)

### Community 13 - "BoardViewWidget"
Cohesion: 0.09
Nodes (20): BoardViewWidget, QFrame, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Compatibilidad hacia atrás: actualiza el controlador de sincronización., Compatibilidad hacia atrás: delega en sync_controller., Compatibilidad hacia atrás: delega en sync_controller., Ejecuta la sincronización en segundo plano delegando en el controlador., Gestiona el diálogo de resultado cuando la sincronización es manual. (+12 more)

### Community 14 - "get_connection"
Cohesion: 0.11
Nodes (26): create_board(), delete_board(), get_board(), get_boards(), Devuelve los tableros. Por defecto excluye los archivados., Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra…, set_board_archived(), update_board() (+18 more)

### Community 15 - "ColorCirclesPicker"
Cohesion: 0.15
Nodes (8): ColorCirclesPicker, _ColorDot, _CustomDot, QWidget, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, Círculo punteado con «+» que abre el selector de color libre., Fila de círculos de color con selección única y opción de color personalizado., QAbstractButton

### Community 16 - "generate_structural_spec"
Cohesion: 0.14
Nodes (16): _analyze_task_for_spec(), generate_structural_spec(), parse_subtask_lines(), Realiza un análisis heurístico de la tarea para deducir el dominio…, Generador offline instantáneo que sintetiza una SPEC estructurada sin necesidad…, Descompone una tarea en títulos de subtareas (tareas hermanas) de forma…, Convierte un texto (una tarea por línea) en títulos limpios: quita viñetas,…, suggest_subtasks_offline() (+8 more)

### Community 17 - "AiSpecDialog"
Cohesion: 0.07
Nodes (20): AiSpecDialog, PromptViewerDialog, QDialog, Diálogo modal interactivo para generar especificaciones técnicas con IA local., Carga la metadata completa de las tareas seleccionadas (incluyendo enlaces y…, Diálogo modal para inspeccionar el prompt maestro ensamblado antes de enviarlo…, Muestra qué motor de IA atenderá la generación y puebla el selector de modelos…, Inicia el proceso de generación de SPEC en segundo plano con streaming. (+12 more)

### Community 18 - "test_local_ai.py"
Cohesion: 0.14
Nodes (18): build_spec_prompts(), format_tasks_for_prompt(), Prepara un JSON estructurado con las tareas seleccionadas conteniendo…, Genera el system prompt y user prompt según el objetivo y plantilla…, Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens…, stream_openai_chat_completion(), test_build_spec_prompts_diary_summary_mode(), test_build_spec_prompts_task_breakdown_mode() (+10 more)

### Community 19 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 20 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 21 - "sidebar.py"
Cohesion: 0.10
Nodes (16): CloudSyncInfoDialog, QDialog, Diálogo modal explicativo previo a seleccionar la ruta de sincronización en la…, Importación de tableros, columnas y tareas a Ekin desde archivos JSON.…, BoardConfigDialog, NotificationsPopup, QDialog, Pequeño icono cuadrado del color indicado (para listar tareas por tablero). (+8 more)

### Community 22 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 23 - "ColumnWidget"
Cohesion: 0.16
Nodes (6): test_column_widget_mouse_press_emits_column_activated(), ColumnWidget, Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada).

### Community 24 - "test_reminders.py"
Cohesion: 0.14
Nodes (20): current_week_key(), QDialog, Recordatorios anticipados y resumen semanal (weekly review). La decisión de…, Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, should_show_weekly_digest() (+12 more)

### Community 25 - "MainWindow"
Cohesion: 0.06
Nodes (16): MainWindow, Manejador si el tablero actual cambió en el sidebar., Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., Abre la carpeta de logs de diagnóstico en el explorador de archivos., Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Abre la ventana de referencia de atajos de teclado (Ctrl+/). (+8 more)

### Community 26 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 27 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 28 - "markdown_edit.py"
Cohesion: 0.09
Nodes (24): apply_word_style_to_qt_table(), fit_html_images(), linkify_urls(), Utilidades compartidas para procesamiento y saneamiento de HTML en…, Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no…, Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,… (+16 more)

### Community 29 - "connection.py"
Cohesion: 0.12
Nodes (17): Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, init_db(), Crea las tablas necesarias si no existen., get_active_timer_tasks(), get_scheduled_tasks(), get_task_board_id(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve el board_id al que pertenece una tarea (o None si no existe). (+9 more)

### Community 30 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 31 - "SyncResult"
Cohesion: 0.14
Nodes (14): format_sync_summary(), Asegura que el archivo sincronizado siga registrado tras reemplazos atómicos., Ejecuta la sincronización en diferido cuando finalizan las escrituras., Inicia una sincronización del tablero activo. Si blocking=True, se ejecuta…, Procesa la finalización de una sincronización., Genera un resumen conciso de un SyncResult para mostrar en la interfaz., Exporta automáticamente los cambios locales si el tablero está vinculado., Resultado de una operación de sincronización. (+6 more)

### Community 33 - "backup_database"
Cohesion: 0.24
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder(), test_backup_rapid_calls_never_collide() (+3 more)

### Community 34 - "main"
Cohesion: 0.13
Nodes (18): get_log_dir(), install_excepthook(), install_qt_message_handler(), Registro de diagnóstico y captura global de errores para Ekin. Escribe un log…, Directorio de logs (se crea si no existe): ~/.ekin/logs., Configura (idempotente) un RotatingFileHandler en la raíz. Devuelve la ruta del…, Registra las excepciones no controladas y muestra un aviso no fatal (si hay UI)., Enruta los mensajes del propio Qt (warnings/critical) al log de Ekin. (+10 more)

### Community 35 - "compute_drop_index"
Cohesion: 0.33
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una tarjeta soltada en `drop_y`. `cards_geom` es una…

### Community 37 - "test_main_window.py"
Cohesion: 0.18
Nodes (19): get_default_db_path(), _close_window(), _make_task_on_board(), _make_window(), Pruebas headless para MainWindow (main.py): comportamientos que solo existen a…, Verifica que el título de la ventana principal es 'Ekin vX.X.X'., Verifica que archivos no rastreados (como .db-wal, .db-shm o temporales) no…, Verifica que modificaciones en archivos rastreados sí detienen la actualización… (+11 more)

### Community 38 - "sync_board_with_file"
Cohesion: 0.08
Nodes (35): Ejecuta el ciclo completo de sincronización y fusión diferencial para un…, sync_board_with_file(), fixture, Verifica que cambios en el archivo remoto sin cambios locales se importan…, Crea una base de datos temporal para pruebas de sincronización., Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que desvincular un tablero borra sync_path y lo deja offline., Verifica que si local y remoto añaden tareas diferentes simultáneamente, la… (+27 more)

### Community 39 - "RichTextToolbar"
Cohesion: 0.09
Nodes (14): _align_icon(), _color_icon(), QWidget, Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar (+6 more)

### Community 40 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.22
Nodes (8): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, Item 1 — Ctrl+N targets the last-interacted-with column, Item 2 — Two-row utility bar, Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 41 - "board_sync.py"
Cohesion: 0.12
Nodes (23): _apply_remote_board_clean(), calculate_file_hash(), create_premerge_backup(), _execute_two_way_merge(), export_board_to_sync_dict(), _merge_task_sub_entities(), now_utc_iso(), _prune_premerge_backups() (+15 more)

### Community 42 - ".contextMenuEvent"
Cohesion: 0.13
Nodes (9): format_single_cell(), format_table_all_cells(), Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Ajusta el ancho y alto (px) de la imagen indicada. Si new_width es <= 2.0…, Pide al usuario un ancho en píxeles y redimensiona la imagen., Identifica si una tabla corresponde a un bloque de código. (+1 more)

### Community 43 - "test_timer_board_view.py"
Cohesion: 0.38
Nodes (9): _card_for(), _make_board_with_task(), Antes del fix, _build_column_widget releía el ajuste una vez POR COLUMNA…, test_build_column_widget_applies_configured_threshold(), test_build_column_widget_defaults_threshold_when_unset(), test_load_board_reads_timer_alert_hours_once_regardless_of_column_count(), test_refresh_timer_badges_noop_on_board_with_no_timers(), test_refresh_timer_badges_noop_on_welcome_screen() (+1 more)

### Community 44 - "t"
Cohesion: 0.11
Nodes (11): QLabel, QPushButton, QDialog, ShortcutsDialog, Returns the localized string for `key`, falling back to English if missing., t(), test_shortcuts_dialog_constructs_with_both_sections(), QWidget (+3 more)

### Community 45 - "Release v0.4.0"
Cohesion: 0.22
Nodes (8): backup_database() Function, backups.py Module, db_path Normalization (P1), Dead #TaskCardDueDate Object Name, iCalendar Line-Folding Off-by-One, Overdue Tasks in Notification Bell, Release v0.4.0, Subscribe-in-Google Helper

### Community 46 - "Hover-to-Expand Collapsed Column"
Cohesion: 0.25
Nodes (9): compute_drop_index() Function, Same-Column Drag Off-by-One Bug, handle_hover_expand_requested() Method, BoardViewWidget._hover_expanded_column_id, Hover-to-Expand Collapsed Column, QDrag.exec() Return as Drag-End Checkpoint, _build_column_widget() Helper, load_board() Mid-Drag Crash Bug (+1 more)

### Community 47 - "Global Search & Filter Feature"
Cohesion: 0.22
Nodes (9): Ctrl+F Search Shortcut, Global Search & Filter Feature, Immediate-Persistence Pattern, on_notification_task Handler Reuse, Release v0.5.0, SearchDialog Class, search_tasks() Function, Subtask Checklist UI (Task Detail Dialog) (+1 more)

### Community 48 - "Git-Stash Empirical Regression Verification"
Cohesion: 0.22
Nodes (9): QMimeData GC Lifetime Bug (Test-Only), tests/test_hover_expand.py, Ctrl+Z FK IntegrityError Crash Fix (Fix 2), Git-Stash Empirical Regression Verification, STATUS_HEAP_CORRUPTION Test-Suite Crash, Stale Board Card on Calendar Edit Fix (Fix 4), conftest.py QApplication Teardown Fix, restore_task() Function (+1 more)

### Community 49 - "board_ops.py"
Cohesion: 0.28
Nodes (8): copy_board(), copy_column_to_board(), _duplicate_task_into_column(), move_column_to_board(), Crea una copia de un tablero entero, incluyendo sus columnas, tareas y logs., Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en…, Crea una copia de la columna en el tablero de destino, incluyendo todas sus…, Mueve una columna a otro tablero y la coloca al final de su lista de columnas.

### Community 50 - "ics_sync.py"
Cohesion: 0.22
Nodes (8): delete_board_ics_sync_path(), get_all_board_ics_sync_paths(), get_board_ics_sync_path(), Devuelve la ruta de auto-sync configurada para un tablero, o None si no tiene., Crea o actualiza la ruta de auto-sync de un tablero., Desactiva la sincronización automática de un tablero., Devuelve {board_id: path} para todos los tableros con auto-sync configurado., set_board_ics_sync_path()

### Community 51 - "FlowLayout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 52 - "LogEntryWidget"
Cohesion: 0.09
Nodes (19): LogEntryWidget, QFrame, Sustituye el contenido por un editor en línea con Guardar/Cancelar y soporte de…, Una entrada del diario/chat, con botones (pintados) de editar y eliminar y…, Cancela la edición volviendo al estado de lectura de forma instantánea y sin…, Guarda la edición del comentario invocando el callback., Limpia los widgets temporales de edición y reactiva la etiqueta de lectura., Maneja los enlaces clicados dentro de una entrada ya enviada (imágenes, URLs… (+11 more)

### Community 53 - "SidebarWidget"
Cohesion: 0.06
Nodes (31): QFrame, Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos…, Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana., Re-aplica los colores dependientes del tema en los widgets de la barra lateral…, Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Archiva/desarchiva un tablero y recarga la lista. (+23 more)

### Community 54 - "BoardSyncController"
Cohesion: 0.09
Nodes (17): BoardSyncController, QObject, board_sync_controller.py - Controlador de sincronización desacoplado de…, Configura el watcher para detectar reactivamente cambios externos., Disparado por el sistema de archivos ante modificaciones externas., Desvincula el tablero actual de su archivo compartido., Espera a que termine cualquier hilo de sincronización en ejecución., Devuelve True si hay una sincronización en segundo plano activa. (+9 more)

### Community 55 - "CLAUDE.md"
Cohesion: 0.29
Nodes (5): 1. Think Before Coding, 2. Simplicity First, 3. Surgical Changes, 4. Goal-Driven Execution, graphify

### Community 56 - ".__init__"
Cohesion: 0.12
Nodes (7): CalendarChip, DayCell, QFrame, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, Guía detallada de suscripción por proveedor (texto del diálogo de Ajustes)., _swatch_icon()

### Community 57 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 58 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 59 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 60 - "CommandPalette"
Cohesion: 0.14
Nodes (11): CommandPalette, QDialog, _swatch_icon(), Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o…, Pruebas headless de la paleta de comandos (command_palette.py): filtrado de…, _rows(), test_palette_command_click_emits_command_invoked(), test_palette_filters_commands_by_query() (+3 more)

### Community 61 - "TaskCard"
Cohesion: 0.20
Nodes (5): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, test_task_card_ctrl_click_and_selection_state(), QFrame, Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., TaskCard

### Community 62 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 63 - ".check_for_updates"
Cohesion: 0.33
Nodes (3): Verifica de forma silenciosa si hay actualizaciones. - En modo…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica de forma silenciosa si hay actualizaciones en el repo de GitHub (modo…

### Community 64 - "TagManagerDialog"
Cohesion: 0.27
Nodes (3): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog

### Community 65 - "local_ai.py"
Cohesion: 0.13
Nodes (19): check_http_endpoint(), detect_available_llm(), ensure_directories(), get_ollama_models(), is_model_downloaded(), is_runner_installed(), Módulo de IA Local Autónoma para Ekin (Vía B). Permite seleccionar múltiples…, Detecta qué servicio de LLM local está disponible en el equipo. (+11 more)

### Community 66 - "._build_column_widget"
Cohesion: 0.15
Nodes (6): Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Abre el generador modal de especificaciones para agentes de IA., Escape deselecciona tarjetas múltiples.

### Community 67 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 69 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 70 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 71 - "test_ics_export.py"
Cohesion: 0.14
Nodes (23): build_ics(), _escape(), _fold_line(), Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Deriva (SEQUENCE, LAST-MODIFIED) del `updated_at` de la tarea. SEQUENCE debe…, Pliega líneas a 75 octetos con continuación por espacio (RFC 5545 §3.1). La…, Construye el contenido .ics (texto) con las tareas que tienen due_date. Con…, _sequence_and_modified() (+15 more)

### Community 72 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 73 - ".__init__"
Cohesion: 0.18
Nodes (5): app_icon(), Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo.

### Community 75 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 76 - "sync.py"
Cohesion: 0.12
Nodes (16): get_board_by_uuid(), get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Marca todas las tareas del tablero como sincronizadas con el archivo…, Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero. (+8 more)

### Community 77 - "ColumnEditDialog"
Cohesion: 0.13
Nodes (9): BoardSelectionDialog, ColumnEditDialog, QDialog, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Diálogo para crear o editar una columna (nombre y color)., Abre el diálogo para crear una columna., Crea una copia de la columna en otro tablero seleccionado., test_board_selection_dialog_empty_and_selection() (+1 more)

### Community 78 - ".reload_logs"
Cohesion: 0.20
Nodes (5): Crea una nueva entrada de diario con el texto del input., Mueve la barra de desplazamiento del diario hasta abajo., Limpia y vuelve a cargar todos los logs/entradas del diario., Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…, Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo…

### Community 80 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 81 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 98 - "task_detail_dialog.py"
Cohesion: 0.11
Nodes (21): confirm_open_untrusted_link(), _get_target_extension(), _is_local_link(), _is_unc_path(), open_link_safely(), Utilidades de seguridad para la validación y apertura segura de hipervínculos y…, Abre de forma segura una URL o ruta local tras verificar su nivel de confianza.…, True si la cadena representa una ruta de archivo local o de red (UNC / relativa… (+13 more)

### Community 99 - "BoardColumnsArea"
Cohesion: 0.29
Nodes (3): BoardColumnsArea, QWidget, Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…

### Community 100 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 107 - "DraggableColumnTitle"
Cohesion: 0.25
Nodes (3): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…

### Community 121 - "BoardSyncWorker"
Cohesion: 0.33
Nodes (3): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…

### Community 122 - "._rebuild_single_column"
Cohesion: 0.08
Nodes (16): Maneja la lógica de recolocación de tareas tras arrastrarlas., Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Actualiza el chip de recuento de tareas y vencimientos de la semana sin…, Exporta cambios locales en segundo plano delegando en el controlador., Abre el diálogo para editar nombre y color de una columna., Confirma y borra una columna., Pliega o despliega una columna (persiste el estado) y recarga solo esa columna., Soltar una tarjeta sobre una columna plegada: la despliega y coloca la tarjeta… (+8 more)

### Community 123 - "main.py"
Cohesion: 0.08
Nodes (30): Diálogo de interfaz gráfica para la generación de especificaciones (SPEC) para…, Diálogos y componentes de interfaz auxiliares para la gestión de columnas y…, Actualiza el botón y estado de sincronización con OneDrive/archivo compartido., Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando…, Panel de Analíticas: métricas transversales (todos los tableros) con tarjetas… (+22 more)

### Community 124 - "SettingsDialog"
Cohesion: 0.05
Nodes (32): BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente., Valida e inserta las tareas definidas en la tabla., QCheckBox, QDialog, Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Segmentado English / Español que maneja el lang_combo de respaldo. (+24 more)

### Community 125 - "MyWorkWidget"
Cohesion: 0.16
Nodes (17): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon() (+9 more)

### Community 126 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, Carga y conecta a la base de datos local un tablero sincronizado existente…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 127 - "InstallerDownloadThread"
Cohesion: 0.13
Nodes (11): InstallerDownloadThread, parse_version_tuple(), QThread, Muestra confirmación al usuario y descarga el instalador si acepta., Convierte cadenas como '1.0.0' o 'v1.0.1' en tupla de enteros (1, 0, 1) para…, ReleaseCheckThread, test_installer_download_thread(), test_installer_download_thread_cancelled_removes_incomplete_file() (+3 more)

### Community 128 - "test_ai_assist.py"
Cohesion: 0.10
Nodes (15): AiAssistDialog, QDialog, Diálogo genérico de asistencia por IA para una tarea concreta. Muestra un…, Abre el asistente que desglosa esta tarea en subtareas (tareas hermanas en la…, Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas)…, summarize_diary_offline(), _make_task(), Pruebas de los asistentes de IA local offline (local_ai) y su integración: -… (+7 more)

### Community 129 - "_card_with_timer"
Cohesion: 0.33
Nodes (6): _card_with_timer(), test_timer_badge_hidden_when_no_timer(), test_timer_badge_hides_on_invalid_timestamp(), test_timer_badge_shown_danger_at_or_above_threshold(), test_timer_badge_shown_muted_under_threshold(), test_timer_badge_updates_when_threshold_changed()

### Community 130 - "SearchDialog"
Cohesion: 0.31
Nodes (5): QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon()

### Community 131 - "ImagePreviewDialog"
Cohesion: 0.20
Nodes (7): ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog…, test_image_preview_dialog_is_destroyed_after_closing_when_parented(), test_image_preview_dialog_upscales_small_pixmap()

### Community 132 - "BoardEditDialog"
Cohesion: 0.08
Nodes (16): ExportDialog, ImportConfirmationDialog, QDialog, Diálogo modal para confirmar la importación de tableros desde JSON., Genera una cadena amigable para nombres de archivo., Diálogo modal para configurar y ejecutar la exportación de tableros., _slugify(), BoardEditDialog (+8 more)

### Community 134 - ".load_board"
Cohesion: 0.13
Nodes (8): Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Maneja el clic en el botón de sincronización de la cabecera., Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión., Abre el diálogo para crear múltiples tareas en una tabla., Limpia todos los widgets del layout de columnas., Reordena las columnas del tablero actual tras arrastrar una por su título.

### Community 136 - "test_incremental_rendering.py"
Cohesion: 0.17
Nodes (11): Pruebas unitarias para el renderizado incremental del tablero (mutaciones de…, Mover una tarea dentro de la misma columna solo debe reconstruir esa columna., Mover una tarea entre dos columnas solo debe reconstruir origen y destino,…, Plegar una columna solo debe reconstruir esa columna, sin tocar el resto del…, create_quick_task solo debe reconstruir la columna de destino, preservando las…, add_task debe reconstruir solo la columna destino y actualizar el chip de…, test_add_task_incremental(), test_create_quick_task_incremental_rendering() (+3 more)

### Community 138 - ".load_task_data"
Cohesion: 0.12
Nodes (8): Habilita/inhabilita fecha y hora según los checks., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Guarda el título, descripción, etiquetas y fecha de vencimiento., Formatea y muestra la fecha y hora de última edición en la cabecera de NOTES., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Actualiza el botón y la etiqueta de tiempo transcurrido según…

### Community 139 - "download_and_extract_runner"
Cohesion: 0.20
Nodes (10): download_and_extract_runner(), get_runner_download_url(), Devuelve la URL oficial de descarga del binario portable de llama-server según…, Descarga y extrae el ejecutable portable de llama-server en runner_dir., Verifica que get_runner_download_url retorna una URL válida con terminación…, Verifica la descarga, descompresión del ZIP en el directorio destino y limpieza…, Verifica que si el ZIP contiene rutas maliciosas hacia directorios superiores…, test_download_and_extract_runner() (+2 more)

### Community 140 - ".render_tags"
Cohesion: 0.14
Nodes (7): Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza., Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno»…, Asigna una etiqueta permanente (categoría) con uno de sus valores a la tarea., Abre el gestor del catálogo de etiquetas y re-sincroniza las etiquetas…, Refresca los datos (valor/color) de las etiquetas asignadas y descarta las que…

### Community 144 - "TagPickerDialog"
Cohesion: 0.29
Nodes (4): QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog

### Community 145 - "CodeBlockDialog"
Cohesion: 0.13
Nodes (8): CodeBlockDialog, LinkDialog, QDialog, Abre el diálogo para insertar un bloque de código formateado., Inserta un bloque de código formateado con resaltado de sintaxis., Abre el diálogo para insertar o editar un enlace web., Diálogo modal para insertar un bloque de código formateado., Diálogo modal para insertar un enlace (URL).

### Community 147 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 148 - "clean_html_description"
Cohesion: 0.20
Nodes (9): Abre el asistente que resume el diario de esta tarea (offline)., clean_html_description(), Utilidades compartidas para procesamiento y saneamiento de HTML y texto plano.…, Limpia a fondo cualquier residuo HTML/CSS generado por editores enriquecidos o…, export_ics(), Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano limpio para iCalendar. (+1 more)

### Community 150 - "_collapsed_column_widget"
Cohesion: 0.36
Nodes (8): _collapsed_column_widget(), _drag_enter_event(), _drop_event(), _task_drag_mime(), test_hover_timeout_emits_signal_only_while_collapsed(), test_hover_timer_starts_on_drag_enter(), test_hover_timer_stops_on_drag_leave(), test_hover_timer_stops_on_drop_before_timeout()

### Community 152 - "format_code_block_html"
Cohesion: 0.33
Nodes (7): format_code_block_html(), _get_warm_pygments_style(), Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting(), test_warm_syntax_highlighting_style()

### Community 153 - "bump_version.py"
Cohesion: 0.52
Nodes (6): calculate_next_version(), get_current_version(), main(), update_changelog(), update_installer_iss(), update_version_py()

### Community 154 - "test_wip_limit.py"
Cohesion: 0.43
Nodes (5): _board_with(), Pruebas de los límites WIP por columna: persistencia y aviso visual en el…, test_column_widget_no_wip_label_when_unset(), test_column_widget_shows_wip_over_limit_in_danger(), test_column_widget_wip_under_limit_is_muted()

### Community 157 - "._refresh_priority_combo"
Cohesion: 0.33
Nodes (3): Devuelve el id de la etiqueta permanente «Prioridad», asegurando que existan…, Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…

### Community 170 - "test_ux_enhancements.py"
Cohesion: 0.11
Nodes (16): Pide filas y columnas mediante un diálogo unificado e inserta la tabla…, Diálogo modal para configurar e insertar una tabla con número inicial de filas…, TableInsertDialog, Pruebas exhaustivas para las 4 mejoras de UX: 1. Tablas interactivas y formato…, Verifica las proporciones, márgenes simétricos, scroll fluido y edición in-…, Verifica inserción inicial de tabla y manipulación mediante acciones de…, Verifica que TableInsertDialog admita dimensiones personalizadas y que su botón…, Verifica que los metadatos se organicen en 4 filas dentro del panel izquierdo,… (+8 more)

## Knowledge Gaps
- **132 isolated node(s):** `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column`, `Item 2 — Two-row utility bar`, `Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **59 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `test_ai_assist.py`, `CalendarViewWidget`, `MarkdownTextEdit`, `CalendarSettingsDialog`, `DashboardWidget`, `ImagePreviewDialog`, `.load_board`, `test_widgets_headless.py`, `BoardEditDialog`, `.notify_due_today`, `.load_task_data`, `SearchDialog`, `.render_tags`, `BoardViewWidget`, `.delete_log_entry`, `TagPickerDialog`, `AiSpecDialog`, `CodeBlockDialog`, `.delete_task`, `clean_html_description`, `generate_structural_spec`, `.mouseReleaseEvent`, `sidebar.py`, `format_code_block_html`, `test_reminders.py`, `ColumnWidget`, `markdown_edit.py`, `._refresh_priority_combo`, `SyncResult`, `BoardButton`, `RichTextToolbar`, `.contextMenuEvent`, `test_shortcuts_item_new_task_describes_last_active_column_behavior`, `LogEntryWidget`, `SidebarWidget`, `BoardSyncController`, `.__init__`, `CommandPalette`, `.check_for_updates`, `TagManagerDialog`, `local_ai.py`, `._build_column_widget`, `.__init__`, `ColumnEditDialog`, `.reload_logs`, `task_detail_dialog.py`, `._build_link_row`, `._rebuild_single_column`, `main.py`, `SettingsDialog`, `MyWorkWidget`, `InstallerDownloadThread`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `tasks.py`, `snapshots.py`, `tags.py`, `sync.py`, `exporter.py`, `board_ops.py`, `ics_sync.py`, `sidebar.py`, `connection.py`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `BoardViewWidget` connect `BoardViewWidget` to `.load_board`, `test_widgets_headless.py`, `test_incremental_rendering.py`, `AiSpecDialog`, `test_hover_expand.py`, `sidebar.py`, `ColumnWidget`, `MainWindow`, `test_wip_limit.py`, `test_board_view_sync_btn_states`, `test_timer_board_view.py`, `test_board_view_multi_selection_bar_and_escape`, `SidebarWidget`, `BoardSyncController`, `TaskCard`, `._build_column_widget`, `.__init__`, `ColumnEditDialog`, `BoardColumnsArea`, `._rebuild_single_column`, `main.py`, `SettingsDialog`, `InstallerDownloadThread`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `BoardViewWidget` (e.g. with `AiSpecDialog` and `BoardColumnsArea`) actually correct?**
  _`BoardViewWidget` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TaskDetailDialog` (e.g. with `AiAssistDialog` and `LogEntryWidget`) actually correct?**
  _`TaskDetailDialog` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MarkdownTextEdit` (e.g. with `LogEntryWidget` and `FlowLayout`) actually correct?**
  _`MarkdownTextEdit` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._