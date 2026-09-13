# Graph Report - Ekin  (2026-09-13)

## Corpus Check
- 110 files · ~148,403 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2008 nodes · 3726 edges · 175 communities (117 shown, 58 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 229 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e69d7d98`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CalendarViewWidget
- MarkdownTextEdit
- CalendarSettingsDialog
- DashboardWidget
- tasks.py
- /graphify Pipeline
- TaskDetailDialog
- snapshots.py
- 2. Implementation Tasks
- tags.py
- RunnerDownloadThread
- test_ics_export.py
- BoardViewWidget
- get_connection
- BulkAddTaskDialog
- local_ai.py
- AiSpecDialog
- test_local_ai.py
- test_hover_expand.py
- Part B: Semantic Extraction (Subagents)
- BoardConfigDialog
- .keyPressEvent
- ColumnWidget
- test_reminders.py
- MainWindow
- Release v0.6.0
- CI Workflow (ruff + pytest)
- markdown_edit.py
- connection.py
- format_elapsed_time
- sync_board_with_file
- ._insert_image
- backup_database
- main
- compute_drop_index
- BoardButton
- CommandPalette
- test_board_sync.py
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
- export_dialog.py
- CLAUDE.md
- .__init__
- conftest.py
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- NotificationsPopup
- TaskCard
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- .check_for_updates
- TagManagerDialog
- detect_available_llm
- ._update_cards_selection_ui
- TECHNICAL DESIGN DOCUMENT
- VerticalLabel
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- TECHNICAL DESIGN DOCUMENT
- create_premerge_backup
- Calendar Drag-to-Reschedule
- .__init__
- .init_ui
- Cross-Repo Graph Merge
- sync.py
- .reload_boards
- test_widgets_headless.py
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
- .reload_logs
- TECHNICAL DESIGN DOCUMENT
- BoardColumnsArea
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
- ._collapse_hover_expanded_column
- main.py
- SettingsDialog
- MyWorkWidget
- connect_shared_board_from_file
- ._build_column_widget
- ._on_sync_finished
- QLabel
- SearchDialog
- show_image_preview
- ExportDialog
- .notify_due_today
- .load_board
- .open_code_dialog
- .handle_task_drop
- ._change_list_indent
- ._build_link_row
- download_and_extract_runner
- .render_tags
- BoardEditDialog
- PromptViewerDialog
- test_create_tasks_batch
- CloudSyncInfoDialog
- QPushButton
- _analyze_task_for_spec
- build_qss
- .mouseReleaseEvent
- ._open_task_detail
- .open_board_config
- set_language
- format_code_block_html
- bump_version.py
- .open_link_dialog
- .get_pending_notifications
- UndoAction
- .sync_ics
- .select_board
- .add_task
- .apply_theme
- ._prompt_custom_image_size
- style_menu
- ._grid_from_plain_text
- .on_board_changed
- color_swatch_css
- test_bulk_queries_chunking_handles_large_task_lists
- test_copy_operations_generate_uuids
- test_save_task_full_atomic_update
- test_snapshot_and_restore_board_single_connection
- test_table_dialog_insert_dimensions
- test_quote_placeholder_clearing_on_click
- test_markdown_edit_case_conversions
- test_markdown_edit_image_resize_methods
- test_markdown_text_edit_open_code_dialog_bool_safe

## God Nodes (most connected - your core abstractions)
1. `t()` - 192 edges
2. `get_connection()` - 98 edges
3. `BoardViewWidget` - 92 edges
4. `TaskDetailDialog` - 92 edges
5. `MarkdownTextEdit` - 79 edges
6. `MainWindow` - 53 edges
7. `SidebarWidget` - 46 edges
8. `lucide_icon()` - 35 edges
9. `AiSpecDialog` - 34 edges
10. `SettingsDialog` - 29 edges

## Surprising Connections (you probably didn't know these)
- `test_is_local_link_classifies_urls_vs_paths()` --calls--> `_is_local_link()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `test_is_unc_path_detection()` --calls--> `_is_unc_path()`  [INFERRED]
  tests/test_widgets_headless.py → detail_dialog/security_utils.py
- `Semantic Manifest Stamping Gate (#2015/#1948)` --semantically_similar_to--> `Tech Debt: restore_column/restore_board Not Atomic Across Children`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/update.md → backlog.md
- `_ClickOutsideFilter` --uses--> `AiAssistDialog`  [INFERRED]
  detail_dialog/task_detail_dialog.py → ai_assist_dialog.py
- `TaskDetailDialog` --uses--> `AiAssistDialog`  [INFERRED]
  detail_dialog/task_detail_dialog.py → ai_assist_dialog.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (175 total, 58 thin omitted)

### Community 0 - "CalendarViewWidget"
Cohesion: 0.12
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 2 - "MarkdownTextEdit"
Cohesion: 0.06
Nodes (28): MarkdownTextEdit, Inserta una línea separadora horizontal en la posición del cursor., QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, QTextEdit, Verifica que escribir en una cita con placeholder borra el placeholder…, test_quote_placeholder_clearing_on_typing(), Verifica que insert_table genera tablas estilo Word con celdas centradas., Verifica la inserción de citas estructuradas y la emisión de señal para enlaces… (+20 more)

### Community 3 - "CalendarSettingsDialog"
Cohesion: 0.15
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 4 - "DashboardWidget"
Cohesion: 0.10
Nodes (20): _esc(), export_report_pdf(), gather_stats(), Métricas de tableros para el panel de Analíticas y la exportación a PDF.…, Recopila métricas transversales (todos los tableros activos)., Construye un informe HTML simple a partir de `stats`. Puro (sin Qt)., Renderiza el informe HTML a un PDF en `path`. Usa QPdfWriter (sin deps nuevas)., render_report_html() (+12 more)

### Community 5 - "tasks.py"
Cohesion: 0.06
Nodes (35): add_task_link(), delete_task_link(), get_task_links(), get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en lotes paginados (evita N+1 y el…, Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id., get_task_tags(), advance_overdue_recurring() (+27 more)

### Community 6 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 7 - "TaskDetailDialog"
Cohesion: 0.06
Nodes (38): QDialog, Elimina una entrada de diario tras confirmación., Habilita/inhabilita fecha y hora según los checks., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Borra definitivamente la tarea actual de la base de datos., Verifies if the target is a UNC share, executable/script, or unsafe scheme, and…, Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al… (+30 more)

### Community 8 - "snapshots.py"
Cohesion: 0.21
Nodes (15): Módulo de snapshots y restauración para acciones Deshacer / Rehacer…, Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., Captura todo el contenido de una tarea para poder recrearla (deshacer),…, restore_board(), _restore_board_in_conn(), restore_column(), _restore_column_in_conn(), restore_task() (+7 more)

### Community 9 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 10 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 11 - "RunnerDownloadThread"
Cohesion: 0.17
Nodes (9): QThread, Hilo para descargar y extraer en segundo plano el ejecutable portable de llama-…, Hilo para ejecutar la inferencia de la SPEC en segundo plano con soporte de…, RunnerDownloadThread, SpecGenerationThread, Verifica que un fallo a mitad de streaming emita error_occurred sin corromper…, Verifica que RunnerDownloadThread emite las señales de progreso y finalización., test_runner_download_thread() (+1 more)

### Community 12 - "test_ics_export.py"
Cohesion: 0.05
Nodes (60): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas., Convierte HTML (descripción/nota) en texto plano limpio para exportar., Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags,…, Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como… (+52 more)

### Community 13 - "BoardViewWidget"
Cohesion: 0.12
Nodes (20): BoardViewWidget, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Configura el watcher para detectar reactivamente cambios externos en el archivo…, Evento de cambio detectado por el sistema de archivos (OneDrive)., Espera a que termine cualquier hilo de sincronización activo antes de destruir…, Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)., _make_board(), test_add_task_sets_last_active_column() (+12 more)

### Community 14 - "get_connection"
Cohesion: 0.11
Nodes (26): create_board(), delete_board(), get_board(), get_boards(), Devuelve los tableros. Por defecto excluye los archivados., Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra…, set_board_archived(), update_board() (+18 more)

### Community 15 - "BulkAddTaskDialog"
Cohesion: 0.07
Nodes (18): BoardSelectionDialog, ColumnEditDialog, QDialog, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Diálogo para crear o editar una columna (nombre y color)., BulkAddTaskDialog, QDialog, Diálogo modal con tabla para crear múltiples tareas simultáneamente. (+10 more)

### Community 16 - "local_ai.py"
Cohesion: 0.09
Nodes (24): AiAssistDialog, QDialog, Diálogo genérico de asistencia por IA (offline) para una tarea concreta.…, Abre el asistente que desglosa esta tarea en subtareas (tareas hermanas en la…, Abre el asistente que resume el diario de esta tarea (offline)., parse_subtask_lines(), Módulo de IA Local Autónoma para Ekin (Vía B). Permite seleccionar múltiples…, Detiene el runner autónomo gestionado si está en ejecución. (+16 more)

### Community 17 - "AiSpecDialog"
Cohesion: 0.08
Nodes (13): AiSpecDialog, Diálogo modal interactivo para generar especificaciones técnicas con IA local., Carga la metadata completa de las tareas seleccionadas (incluyendo enlaces y…, Muestra qué motor de IA atenderá la generación y puebla el selector de modelos…, Inicia el proceso de generación de SPEC en segundo plano con streaming., Copia la SPEC generada al portapapeles del sistema., Guarda la especificación en un archivo Markdown., Crea una nueva tarjeta en la primera columna del tablero actual con la SPEC. (+5 more)

### Community 18 - "test_local_ai.py"
Cohesion: 0.19
Nodes (13): build_spec_prompts(), format_tasks_for_prompt(), Prepara un JSON estructurado con las tareas seleccionadas conteniendo…, Genera el system prompt y user prompt según el objetivo y plantilla…, Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py)., Verifica que el selector de modelos de Ollama SIEMPRE esté visible y editable…, test_build_spec_prompts_coding_agent(), test_build_spec_prompts_qa_tests() (+5 more)

### Community 19 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 20 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 21 - "BoardConfigDialog"
Cohesion: 0.40
Nodes (3): BoardConfigDialog, QDialog, Modal de opciones del tablero activo: Edit, Copy, Archive, Import, Export,…

### Community 22 - ".keyPressEvent"
Cohesion: 0.09
Nodes (11): Elimina el marcador escrito y convierte la línea actual en una lista., Saca el bloque actual de la lista, dejando un párrafo normal., Alinea el bloque de texto actual o selección a la izquierda., Centra el bloque de texto actual o selección., Alinea el bloque de texto actual o selección a la derecha., Justifica el bloque de texto actual o selección., Convierte el texto seleccionado (o la palabra bajo el cursor) a MAYÚSCULAS., Convierte el texto seleccionado (o la palabra bajo el cursor) a minúsculas. (+3 more)

### Community 23 - "ColumnWidget"
Cohesion: 0.16
Nodes (7): ColumnWidget, Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…, La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de…, Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Añade una tarjeta de tarea a la columna (no-op si está plegada).

### Community 24 - "test_reminders.py"
Cohesion: 0.14
Nodes (20): current_week_key(), QDialog, Recordatorios anticipados y resumen semanal (weekly review). La decisión de…, Clave ISO de la semana ('YYYY-Www'), estable para comparar semanas., True si el resumen está activado y aún no se ha mostrado esta semana ISO., Separa tareas con due_date en 'overdue' (antes de hoy) y 'this_week' (hoy en…, Resumen semanal: atrasadas + lo que vence esta semana, agrupado. Al pulsar una…, should_show_weekly_digest() (+12 more)

### Community 25 - "MainWindow"
Cohesion: 0.11
Nodes (8): MainWindow, Muestra el panel transversal "Mi trabajo" (todo lo que vence / está en curso)., Muestra el panel de Analíticas (métricas transversales + exportar PDF)., Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., Abre la ventana de referencia de atajos de teclado (Ctrl+/)., Una vez por semana ISO (si está activado), muestra el resumen semanal:…, Muestra u oculta la barra lateral., QMainWindow

### Community 26 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 27 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 28 - "markdown_edit.py"
Cohesion: 0.13
Nodes (16): apply_word_style_to_qt_table(), fit_html_images(), linkify_urls(), Utilidades compartidas para procesamiento y saneamiento de HTML en…, Elimina cabeceras DOCTYPE de Qt y cualquier residuo corrupto de DTD para que no…, Aplica formato estilo Microsoft Word a un QTextTable de Qt: padding…, Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, Convierte URLs en texto plano dentro de html_text en enlaces <a href="...">,… (+8 more)

### Community 29 - "connection.py"
Cohesion: 0.12
Nodes (17): Gestor de conexión y configuración global de base de datos SQLite para Ekin.…, init_db(), Crea las tablas necesarias si no existen., get_active_timer_tasks(), get_scheduled_tasks(), get_task_board_id(), Devuelve las tareas con el temporizador en marcha (timer_started_at no nulo),…, Devuelve el board_id al que pertenece una tarea (o None si no existe). (+9 more)

### Community 30 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 31 - "sync_board_with_file"
Cohesion: 0.12
Nodes (16): Ejecuta el ciclo completo de sincronización y fusión diferencial para un…, Resultado de una operación de sincronización., sync_board_with_file(), SyncResult, Verifica que ante una edición concurrente en la misma tarea, no se pierde…, Verifica que un archivo .ekboard corrupto no rompe la aplicación ni corrompe la…, Verifica que se genera una instantánea de respaldo en backups/ al detectar…, Verifica que si la copia de seguridad pre-fusión falla (ej. disco lleno), la… (+8 more)

### Community 33 - "backup_database"
Cohesion: 0.23
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., Pruebas de las copias de seguridad automáticas de la base de datos., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder() (+3 more)

### Community 34 - "main"
Cohesion: 0.40
Nodes (5): apply_win32_icon(), main(), Registra las tipografías empaquetadas (Caprasimo display + Figtree body) para…, Fuerza los iconos nativos de Win32 (WM_SETICON) directamente en el HWND de…, register_fonts()

### Community 35 - "compute_drop_index"
Cohesion: 0.33
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una tarjeta soltada en `drop_y`. `cards_geom` es una…

### Community 36 - "BoardButton"
Cohesion: 0.24
Nodes (4): BoardButton, Widget personalizado para representar un botón de tablero en la barra lateral., Verifica que los tableros vinculados muestran el icono ☁️ en la barra lateral., test_sidebar_board_button_cloud_badge()

### Community 37 - "CommandPalette"
Cohesion: 0.06
Nodes (41): CommandPalette, QDialog, _swatch_icon(), get_default_db_path(), InstallerDownloadThread, parse_version_tuple(), QThread, Abre la paleta de comandos (Ctrl+K): buscar tareas, ejecutar acciones o… (+33 more)

### Community 38 - "test_board_sync.py"
Cohesion: 0.10
Nodes (19): fixture, Verifica que cambios en el archivo remoto sin cambios locales se importan…, Crea una base de datos temporal para pruebas de sincronización., Verifica que desvincular un tablero borra sync_path y lo deja offline., Verifica que si local y remoto añaden tareas diferentes simultáneamente, la…, Verifica que si un colaborador elimina una tarea en OneDrive, no se resucita al…, Verifica que en una fusión bidireccional concurrente, las etiquetas de ambas…, Verifica que la primera sincronización exporta el tablero al archivo .ekboard. (+11 more)

### Community 39 - "RichTextToolbar"
Cohesion: 0.10
Nodes (13): _color_icon(), QWidget, Barra de formato (negrita, cursiva, tachado, color, alineaciones,…, Pide filas y columnas mediante un diálogo unificado e inserta la tabla…, Despliega un menú emergente con una paleta de colores y opción personalizada., Aplica el color seleccionado al texto seleccionado o al texto que se escriba., RichTextToolbar, Verifica alineaciones de texto (izq, centro, der, justificado) y sincronización… (+5 more)

### Community 40 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.22
Nodes (8): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, Item 1 — Ctrl+N targets the last-interacted-with column, Item 2 — Two-row utility bar, Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 41 - "board_sync.py"
Cohesion: 0.21
Nodes (13): _apply_remote_board_clean(), calculate_file_hash(), _execute_two_way_merge(), _merge_task_sub_entities(), now_utc_iso(), board_sync.py - Motor de sincronización asíncrona y fusión (Merge Engine) de…, Escribe el archivo .ekboard de forma atómica usando un archivo temporal para…, Aplica limpiamente los datos remotos cuando no hay modificaciones locales. (+5 more)

### Community 42 - ".contextMenuEvent"
Cohesion: 0.15
Nodes (9): format_single_cell(), format_table_all_cells(), Aplica el estilo estándar de celda (padding, centrado y opcionalmente estilo…, Reaplica el formato de bordes, padding y cabecera a todas las celdas de una…, Devuelve un QTextCursor posicionado en la imagen bajo `pos`, o None si no hay…, Identifica si una tabla corresponde a un bloque de código., Menú contextual estándar ampliado con opciones de mayúsculas/minúsculas, borrar…, Verifica inserción inicial de tabla y manipulación mediante acciones de… (+1 more)

### Community 43 - "test_timer_board_view.py"
Cohesion: 0.38
Nodes (9): _card_for(), _make_board_with_task(), Antes del fix, _build_column_widget releía el ajuste una vez POR COLUMNA…, test_build_column_widget_applies_configured_threshold(), test_build_column_widget_defaults_threshold_when_unset(), test_load_board_reads_timer_alert_hours_once_regardless_of_column_count(), test_refresh_timer_badges_noop_on_board_with_no_timers(), test_refresh_timer_badges_noop_on_welcome_screen() (+1 more)

### Community 44 - "t"
Cohesion: 0.12
Nodes (10): Actualiza el botón y estado de sincronización con OneDrive., Carga los datos iniciales de la tarea y sus logs desde la base de datos., Devuelve el id de la etiqueta permanente «Prioridad», asegurando que existan…, Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Guarda el título, descripción, etiquetas y fecha de vencimiento., Formatea y muestra la fecha y hora de última edición en la cabecera de NOTES., Actualiza el botón y la etiqueta de tiempo transcurrido según… (+2 more)

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
Cohesion: 0.12
Nodes (17): QFrame, Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos…, SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir…, El fix del guard no debe bloquear el caso normal: con un tablero real… (+9 more)

### Community 54 - "export_dialog.py"
Cohesion: 0.29
Nodes (4): Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Genera una cadena amigable para nombres de archivo., _slugify(), Importación de tableros, columnas y tareas a Ekin desde archivos JSON.…

### Community 55 - "CLAUDE.md"
Cohesion: 0.29
Nodes (5): 1. Think Before Coding, 2. Simplicity First, 3. Surgical Changes, 4. Goal-Driven Execution, graphify

### Community 56 - ".__init__"
Cohesion: 0.14
Nodes (6): CalendarChip, DayCell, QFrame, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon()

### Community 57 - "conftest.py"
Cohesion: 0.32
Nodes (7): _close_top_level_widgets_after_each_test(), db_path(), fixture, qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 58 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 59 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 60 - "NotificationsPopup"
Cohesion: 0.28
Nodes (6): NotificationsPopup, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, _swatch_icon(), test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 61 - "TaskCard"
Cohesion: 0.13
Nodes (8): Verifica que Ctrl+Clic emite ctrl_clicked y set_selected actualiza el aspecto…, test_task_card_ctrl_click_and_selection_state(), QFrame, Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la…, Activa o desactiva el estado visual de selección múltiple., Umbral (en horas) a partir del cual la insignia del temporizador se resalta en…, Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo…, TaskCard

### Community 62 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 63 - ".check_for_updates"
Cohesion: 0.33
Nodes (3): Verifica de forma silenciosa si hay actualizaciones. - En modo…, Inicia comprobación asíncrona de releases públicas en GitHub., Verifica de forma silenciosa si hay actualizaciones en el repo de GitHub (modo…

### Community 64 - "TagManagerDialog"
Cohesion: 0.12
Nodes (10): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog, QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog, _ClickOutsideFilter (+2 more)

### Community 65 - "detect_available_llm"
Cohesion: 0.14
Nodes (16): check_http_endpoint(), detect_available_llm(), get_ollama_models(), is_model_downloaded(), is_runner_installed(), Detecta qué servicio de LLM local está disponible en el equipo., Inicia en segundo plano el ejecutable portable llama-server con el modelo Qwen…, Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens… (+8 more)

### Community 66 - "._update_cards_selection_ui"
Cohesion: 0.25
Nodes (4): Actualiza el estado visual de selección en todas las tarjetas y la barra…, Deselecciona todas las tareas activas., Abre el generador modal de especificaciones para agentes de IA., Escape deselecciona tarjetas múltiples.

### Community 67 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 69 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 70 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 71 - "create_premerge_backup"
Cohesion: 0.20
Nodes (10): create_premerge_backup(), export_board_to_sync_dict(), _prune_premerge_backups(), Serializa un tablero completo con sus columnas, tareas, etiquetas, enlaces y…, Conserva únicamente las `keep` copias de seguridad más recientes de sync para…, Crea una instantánea local automática del tablero antes de fusionar cambios,…, Verifica que create_premerge_backup usa el directorio canónico de la BD y poda…, Verifica que export_board_to_sync_dict serializa correctamente todos los campos… (+2 more)

### Community 72 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 73 - ".__init__"
Cohesion: 0.18
Nodes (5): app_icon(), Aplica el cambio de idioma a toda la interfaz y sus elementos persistentes., Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Crea el icono de bandeja (habilita toasts nativos de Windows)., Verifica si es la primera vez que se abre la app y crea datos de ejemplo.

### Community 74 - ".init_ui"
Cohesion: 0.18
Nodes (4): QWidget, Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Limpia y dibuja las etiquetas actuales y la fecha de vencimiento., TaskListArea

### Community 75 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 76 - "sync.py"
Cohesion: 0.12
Nodes (16): get_board_by_uuid(), get_board_last_local_modified(), get_board_sync_info(), get_synced_boards(), mark_board_tasks_synced(), Marca todas las tareas del tablero como sincronizadas con el archivo…, Vincula un tablero a una ruta de archivo .ekboard externa (OneDrive/carpeta…, Devuelve la información de sincronización de un tablero. (+8 more)

### Community 77 - ".reload_boards"
Cohesion: 0.18
Nodes (6): Re-aplica los colores dependientes del tema en los widgets de la barra lateral…, Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Permite al usuario seleccionar un archivo .ekboard compartido existente y…, Gestiona las acciones de sincronización solicitadas desde el menú contextual de…, Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para crear un nuevo tablero con nombre y color.

### Community 78 - "test_widgets_headless.py"
Cohesion: 0.09
Nodes (33): _card_with_timer(), _collapsed_column_widget(), _drag_enter_event(), _drop_event(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, Al hacer clic fuera de TaskDetailDialog en la ventana principal, se guardan…, Clics dentro de los controles de TaskDetailDialog no deben disparar el…, fit_html_images ajusta o añade width para evitar desbordamiento horizontal. (+25 more)

### Community 80 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 81 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 98 - "task_detail_dialog.py"
Cohesion: 0.22
Nodes (11): confirm_open_untrusted_link(), _get_target_extension(), _is_local_link(), _is_unc_path(), Utilidades de seguridad para la validación y apertura segura de hipervínculos y…, True a menos que la cadena empiece por un esquema web reconocido (case-…, r"""True if url targets a network share (UNC path, e.g. \\server\share or…, Extracts the lowercased file extension from a local path or file URL. (+3 more)

### Community 99 - ".reload_logs"
Cohesion: 0.25
Nodes (4): Crea una nueva entrada de diario con el texto del input., Mueve la barra de desplazamiento del diario hasta abajo., Limpia y vuelve a cargar todos los logs/entradas del diario., Guarda la edición de un comentario (o cancela si new_html es None) in-place sin…

### Community 100 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 101 - "BoardColumnsArea"
Cohesion: 0.24
Nodes (4): BoardColumnsArea, QFrame, QWidget, Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…

### Community 107 - "DraggableColumnTitle"
Cohesion: 0.25
Nodes (3): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…

### Community 121 - "BoardSyncWorker"
Cohesion: 0.33
Nodes (5): BoardSyncWorker, QThread, Hilo para ejecutar la sincronización de tableros en segundo plano sin bloquear…, Verifica que BoardSyncWorker ejecuta la sincronización en segundo plano y emite…, test_board_sync_worker()

### Community 122 - "._collapse_hover_expanded_column"
Cohesion: 0.29
Nodes (4): Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de…, Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…

### Community 123 - "main.py"
Cohesion: 0.10
Nodes (22): Diálogo de interfaz gráfica para la generación de especificaciones (SPEC) para…, Diálogo para la creación masiva de tareas (Bulk Add Tasks) en una tabla.…, Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Diálogo informativo para vincular tableros con proveedores Cloud (Google Drive,…, Selector de color por círculos preseleccionados (New board / Edit column). Seis…, Paleta de comandos (Ctrl+K): un único campo que busca tareas (reutilizando…, Panel de Analíticas: métricas transversales (todos los tableros) con tarjetas…, lucide_icon() (+14 more)

### Community 124 - "SettingsDialog"
Cohesion: 0.10
Nodes (15): QCheckBox, QDialog, Fila de ajuste: etiqueta (600) + descripción (muted) a la izquierda, control a…, Segmentado English / Español que maneja el lang_combo de respaldo., Segmentado Light / Dark que maneja el theme_combo de respaldo., Interruptor 46×26: pista redondeada + perilla; acento cuando está activo., Stepper −/+ con el valor en medio (tipo Caprasimo), que maneja el spin de…, Stepper −/+ genérico ligado a un QSpinBox de respaldo; muestra `valor suffix`. (+7 more)

### Community 125 - "MyWorkWidget"
Cohesion: 0.16
Nodes (17): bucket_scheduled_tasks(), MyWorkWidget, QWidget, Recarga los grupos desde la base de datos (todos los tableros)., Reparte tareas con due_date en cubos: overdue / today / tomorrow / upcoming.…, Pequeño icono cuadrado del color del tablero (para listar tareas por tablero)., Panel "Mi trabajo": agrega, de todos los tableros, las tareas con temporizador…, _swatch_icon() (+9 more)

### Community 126 - "connect_shared_board_from_file"
Cohesion: 0.25
Nodes (8): connect_shared_board_from_file(), Lee y deserializa un archivo .ekboard con reintentos para mitigar bloqueos…, Carga y conecta a la base de datos local un tablero sincronizado existente…, read_sync_file_with_retry(), Verifica que un segundo usuario puede conectar un archivo .ekboard compartido…, Verifica que read_sync_file_with_retry reintenta ante errores de bloqueo…, test_connect_shared_board_from_file(), test_read_sync_file_with_retry_and_lock_handling()

### Community 127 - "._build_column_widget"
Cohesion: 0.18
Nodes (5): Abre el diálogo de detalle/chat de una tarea., Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic., Confirma y borra una columna.

### Community 128 - "._on_sync_finished"
Cohesion: 0.20
Nodes (5): Asegura que el archivo sincronizado esté registrado en QFileSystemWatcher tras…, Ejecuta la sincronización en un hilo secundario sin congelar la UI., Ejecuta la sincronización en diferido cuando OneDrive termina de escribir., Exporta cambios locales en segundo plano si el tablero está vinculado., Sincroniza el tablero actual inmediatamente y notifica si hubo fusión.

### Community 129 - "QLabel"
Cohesion: 0.33
Nodes (6): QLabel, QDialog, ShortcutsDialog, Verifica que ShortcutsDialog carga y contiene los nuevos atajos de edición., test_shortcuts_dialog_constructs_with_both_sections(), test_shortcuts_dialog_includes_new_editor_shortcuts()

### Community 130 - "SearchDialog"
Cohesion: 0.31
Nodes (5): QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon()

### Community 131 - "show_image_preview"
Cohesion: 0.10
Nodes (17): ImagePreviewDialog, pixmap_from_data_uri(), QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña… (+9 more)

### Community 132 - "ExportDialog"
Cohesion: 0.21
Nodes (7): ExportDialog, ImportConfirmationDialog, QDialog, Diálogo modal para confirmar la importación de tableros desde JSON., Diálogo modal para configurar y ejecutar la exportación de tableros., test_export_dialog_initial_state_and_toggles(), test_import_confirmation_dialog_initial_state()

### Community 134 - ".load_board"
Cohesion: 0.09
Nodes (12): Reordena las columnas del tablero actual tras arrastrar una por su título., Crea una copia de la columna en otro tablero seleccionado., Crea una tarea con `title` en la última columna activa (o la primera) del…, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Maneja el clic en el botón de sincronización de la cabecera., Crea un nuevo archivo .ekboard compartido para el tablero actual., Conecta un archivo .ekboard existente y cambia la vista a dicho tablero., Abre el diálogo para crear múltiples tareas en una tabla. (+4 more)

### Community 139 - "download_and_extract_runner"
Cohesion: 0.15
Nodes (12): download_and_extract_runner(), ensure_directories(), get_runner_download_url(), Devuelve la URL oficial de descarga del binario portable de llama-server según…, Asegura que los directorios ~/.ekin/models y ~/.ekin/bin existan., Descarga y extrae el ejecutable portable de llama-server en runner_dir., Verifica que get_runner_download_url retorna una URL válida con terminación…, Verifica la descarga, descompresión del ZIP en el directorio destino y limpieza… (+4 more)

### Community 140 - ".render_tags"
Cohesion: 0.10
Nodes (11): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza., Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno»… (+3 more)

### Community 141 - "BoardEditDialog"
Cohesion: 0.20
Nodes (4): BoardEditDialog, Diálogo personalizado para crear o editar un tablero (nombre y color de fondo)., Abre el diálogo para editar el nombre y color del tablero activo., Abre el diálogo para copiar el tablero activo con un nuevo nombre.

### Community 142 - "PromptViewerDialog"
Cohesion: 0.22
Nodes (6): PromptViewerDialog, QDialog, Diálogo modal para inspeccionar el prompt maestro ensamblado antes de enviarlo…, Ensambla el prompt maestro completo listo para usar en cloud LLMs o inspección., Abre el diálogo para visualizar el prompt maestro ensamblado., Copia el prompt maestro ensamblado directamente al portapapeles.

### Community 144 - "CloudSyncInfoDialog"
Cohesion: 0.25
Nodes (7): CloudSyncInfoDialog, QDialog, Diálogo modal explicativo previo a seleccionar la ruta de sincronización en la…, Verifica que CloudSyncInfoDialog se construye con las instrucciones de los…, Verifica que los diálogos secundarios conectan deleteLater al emitir finished…, test_cloud_sync_info_dialog_constructs_and_accepts(), test_secondary_dialogs_schedule_delete_later_on_finished()

### Community 145 - "QPushButton"
Cohesion: 0.13
Nodes (10): _align_icon(), CodeBlockDialog, LinkDialog, QDialog, Dibuja un icono vectorial nítido para alineación de texto (left, center, right,…, Diálogo modal para insertar un bloque de código formateado., Diálogo modal para insertar un enlace (URL)., Diálogo modal para configurar e insertar una tabla con número inicial de filas… (+2 more)

### Community 146 - "_analyze_task_for_spec"
Cohesion: 0.33
Nodes (7): _analyze_task_for_spec(), generate_structural_spec(), Realiza un análisis heurístico de la tarea para deducir el dominio…, Generador offline instantáneo que sintetiza una SPEC estructurada sin necesidad…, test_generate_structural_spec_offline(), Verifica la eliminación total de CSS (<style>) residual de Qt y el análisis de…, test_html_description_clean_and_domain_analysis()

### Community 147 - "build_qss"
Cohesion: 0.33
Nodes (6): build_qss(), Cambia la paleta activa (COLORS) in-place y devuelve el QSS correspondiente., set_theme(), Verifica que los estilos QSS no contienen tamaños de fuente fraccionales…, test_qss_font_sizes_valid_integers(), test_styles_qcalendarwidget_rules()

### Community 148 - ".mouseReleaseEvent"
Cohesion: 0.25
Nodes (4): Un clic (no un arrastre de selección) sobre una imagen pegada la abre en…, Elimina la tabla/bloque de código donde se pulsó 'Borrar' o donde se encuentra…, Identifica si una tabla corresponde a un bloque de cita (1 fila, 2 columnas,…, Comprueba si el texto coincide con alguno de los placeholders conocidos de…

### Community 149 - "._open_task_detail"
Cohesion: 0.22
Nodes (4): Crea una tarea con `title` en el tablero activo (captura rápida de la paleta)., Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero.

### Community 150 - ".open_board_config"
Cohesion: 0.25
Nodes (4): Archiva/desarchiva un tablero y recarga la lista., Abre el modal de opciones del tablero activo y ejecuta la acción elegida., Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo)., Abre el selector de archivo JSON y el diálogo de confirmación de importación.

### Community 151 - "set_language"
Cohesion: 0.25
Nodes (9): get_available_languages(), get_language(), Returns the active language code ('en' | 'es')., Returns mapping of available language codes to human-readable names., Sets the active language and updates STRINGS in-place., set_language(), test_i18n_strings_catalog_and_fallback(), test_settings_dialog_constructs_with_saved_language() (+1 more)

### Community 152 - "format_code_block_html"
Cohesion: 0.33
Nodes (7): format_code_block_html(), _get_warm_pygments_style(), Devuelve la clase de estilo Pygments ajustada a la paleta Warm Shell / Night…, Formatea código con resaltado de sintaxis (pygments) dentro de un bloque visual…, format_code_block_html() aplica pygments y insert_code_block() lo embebe en el…, test_markdown_text_edit_code_block_formatting(), test_warm_syntax_highlighting_style()

### Community 153 - "bump_version.py"
Cohesion: 0.52
Nodes (6): calculate_next_version(), get_current_version(), main(), update_changelog(), update_installer_iss(), update_version_py()

### Community 155 - ".get_pending_notifications"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

### Community 156 - "UndoAction"
Cohesion: 0.25
Nodes (4): Confirma y elimina el tablero activo., Registra deshacer/rehacer del borrado de un tablero (restaurar desde snapshot)., Pila simple de deshacer/rehacer para acciones destructivas (borrar…, UndoAction

### Community 158 - ".select_board"
Cohesion: 0.33
Nodes (3): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…

### Community 162 - "style_menu"
Cohesion: 0.33
Nodes (4): CSS base para una pastilla de etiqueta coloreada (fondo + esquinas…, Aplica el tema oscuro estándar (fondo/borde/item/selección) a un QMenu., style_menu(), tag_pill_css()

## Knowledge Gaps
- **132 isolated node(s):** `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column`, `Item 2 — Two-row utility bar`, `Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `._on_sync_finished`, `CalendarViewWidget`, `SearchDialog`, `CalendarSettingsDialog`, `DashboardWidget`, `show_image_preview`, `.load_board`, `TaskDetailDialog`, `ExportDialog`, `.notify_due_today`, `._build_link_row`, `QLabel`, `.render_tags`, `BoardEditDialog`, `PromptViewerDialog`, `BulkAddTaskDialog`, `local_ai.py`, `AiSpecDialog`, `CloudSyncInfoDialog`, `QPushButton`, `.mouseReleaseEvent`, `BoardConfigDialog`, `.keyPressEvent`, `.open_board_config`, `format_code_block_html`, `test_reminders.py`, `set_language`, `ColumnWidget`, `markdown_edit.py`, `UndoAction`, `.add_task`, `._prompt_custom_image_size`, `BoardButton`, `CommandPalette`, `RichTextToolbar`, `.contextMenuEvent`, `LogEntryWidget`, `SidebarWidget`, `export_dialog.py`, `.__init__`, `NotificationsPopup`, `.check_for_updates`, `TagManagerDialog`, `._update_cards_selection_ui`, `.__init__`, `.init_ui`, `.reload_boards`, `test_widgets_headless.py`, `task_detail_dialog.py`, `.reload_logs`, `BoardColumnsArea`, `main.py`, `SettingsDialog`, `MyWorkWidget`, `._build_column_widget`?**
  _High betweenness centrality (0.208) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `tasks.py`, `snapshots.py`, `tags.py`, `sync.py`, `test_ics_export.py`, `board_ops.py`, `ics_sync.py`, `export_dialog.py`, `connection.py`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `TaskDetailDialog` connect `TaskDetailDialog` to `TagManagerDialog`, `task_detail_dialog.py`, `MarkdownTextEdit`, `.reload_logs`, `DashboardWidget`, `RichTextToolbar`, `._build_link_row`, `.render_tags`, `t`, `test_widgets_headless.py`, `local_ai.py`, `AiSpecDialog`, `LogEntryWidget`, `._open_task_detail`, `main.py`, `markdown_edit.py`, `._build_column_widget`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `BoardViewWidget` (e.g. with `AiSpecDialog` and `BulkAddTaskDialog`) actually correct?**
  _`BoardViewWidget` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `TaskDetailDialog` (e.g. with `AiAssistDialog` and `LogEntryWidget`) actually correct?**
  _`TaskDetailDialog` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MarkdownTextEdit` (e.g. with `LogEntryWidget` and `FlowLayout`) actually correct?**
  _`MarkdownTextEdit` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._