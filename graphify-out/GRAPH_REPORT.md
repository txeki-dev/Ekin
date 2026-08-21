# Graph Report - Ekin  (2026-08-21)

## Corpus Check
- 83 files · ~102,381 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1269 nodes · 2229 edges · 124 communities (85 shown, 39 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f8f21961`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CalendarViewWidget
- MarkdownTextEdit
- CalendarSettingsDialog
- test_ics_export.py
- tasks.py
- /graphify Pipeline
- test_widgets_headless.py
- snapshots.py
- 2. Implementation Tasks
- tags.py
- ColumnEditDialog
- exporter.py
- ._collapse_hover_expanded_column
- get_connection
- main.py
- SidebarWidget
- _ClickOutsideFilter
- .load_board
- test_hover_expand.py
- Part B: Semantic Extraction (Subagents)
- FlowLayout
- t
- ColumnWidget
- BoardViewWidget
- MainWindow
- Release v0.6.0
- CI Workflow (ruff + pytest)
- .add_task
- database/__init__.py
- format_elapsed_time
- .handle_task_drop
- .__init__
- backup_database
- LogEntryWidget
- .__init__
- BoardButton
- test_main_window.py
- ExportDialog
- RichTextToolbar
- TECHNICAL DESIGN DOCUMENT
- BoardEditDialog
- QPushButton
- test_timer_board_view.py
- boards.py
- Release v0.4.0
- Hover-to-Expand Collapsed Column
- Global Search & Filter Feature
- Git-Stash Empirical Regression Verification
- board_ops.py
- ics_sync.py
- ImagePreviewDialog
- task_detail_dialog.py
- .reload_boards
- QLabel
- CLAUDE.md
- TaskDetailDialog
- fixture
- TECHNICAL DESIGN DOCUMENT
- TECHNICAL DESIGN DOCUMENT
- TagPickerDialog
- TaskCard
- Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)
- UndoManager
- links.py
- .get_pending_notifications
- .init_ui
- TECHNICAL DESIGN DOCUMENT
- ._open_task_detail
- Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave
- TECHNICAL DESIGN DOCUMENT
- settings.py
- Calendar Drag-to-Reschedule
- ._build_column_widget
- ._build_utility_bar
- Cross-Repo Graph Merge
- .render_tags
- BoardColumnsArea
- .notify_due_today
- sidebar.py
- get_subtasks_progress_bulk() Function
- v0.9.1: Local File Attachments on Task Links
- .reload_logs
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
- NotificationsPopup
- compute_drop_index
- TECHNICAL DESIGN DOCUMENT
- show_image_preview
- test_create_log_has_no_intermediate_commit_call
- test_db_name_is_resolved_at_call_time
- test_restore_task_returns_none_if_column_was_deleted_in_the_meantime
- test_restore_column_returns_none_if_board_was_deleted_in_the_meantime
- test_snapshot_and_restore_task_preserves_link_order
- VerticalLabel
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
- ._build_link_row
- DraggableColumnTitle
- .apply_theme

## God Nodes (most connected - your core abstractions)
1. `t()` - 123 edges
2. `get_connection()` - 83 edges
3. `TaskDetailDialog` - 69 edges
4. `BoardViewWidget` - 63 edges
5. `MainWindow` - 39 edges
6. `SidebarWidget` - 36 edges
7. `MarkdownTextEdit` - 29 edges
8. `ColumnWidget` - 27 edges
9. `CalendarViewWidget` - 26 edges
10. `TagManagerDialog` - 25 edges

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
- **Git-Stash Crash-Fix Verification Method** — _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_git_stash_verification_method, _agents_docs_archive_2026_08_07_forensic_fixes_pre_v0_9_0_ctrl_z_fk_crash_fix, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug [EXTRACTED 0.90]
- **Ekin CI + Version-Bump Release Pipeline** — github_workflows_ci_document, github_workflows_release_version_read, github_workflows_release_create_release, changelog_document, readme_ci_badge, readme_release_badge [EXTRACTED 1.00]
- **graphify Skill Pipeline + Its Loaded Reference Docs** — claude_skills_graphify_skill_graphify_pipeline, claude_skills_graphify_references_add_watch_add_url_ingest, claude_skills_graphify_references_exports_wiki_export, claude_skills_graphify_references_extraction_spec_subagent_prompt, claude_skills_graphify_references_github_and_merge_clone_merge_cross_repo, claude_skills_graphify_references_hooks_post_commit_hook, claude_skills_graphify_references_query_vocab_expansion, claude_skills_graphify_references_transcribe_whisper_prompt_generation, claude_skills_graphify_references_update_incremental_update [EXTRACTED 1.00]
- **Hover-Expand Feature and Its Mid-Drag Crash Fix** — _agents_docs_archive_2026_08_06_hover_expand_collapsed_columns_hover_to_expand_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_load_board_mid_drag_crash_bug, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_rebuild_single_column_method [EXTRACTED 1.00]
- **Recurring QDialog-Never-Destroyed Leak Pattern** — changelog_v0_9_0_taskdetaildialog_leak_fix, changelog_unreleased_imagepreview_leak_fix, backlog_pre_v0_9_0_forensic_pass_taskdetaildialog_leak_item, backlog_imagepreview_leak_item [EXTRACTED 1.00]
- **Evolving Keyboard-Shortcuts Discoverability** — _agents_docs_archive_2026_08_01_v0_6_0_keyboard_shortcuts_v1, _agents_docs_archive_2026_08_07_keyboard_shortcuts_and_dialog_keyboard_shortcuts_feature, _agents_docs_archive_2026_08_07_hover_expand_crash_fix_and_shortcuts_button_shortcuts_button_feature [INFERRED 0.75]

## Communities (124 total, 39 thin omitted)

### Community 0 - "CalendarViewWidget"
Cohesion: 0.12
Nodes (12): CalendarViewWidget, _group_by_day(), QWidget, Vista de calendario (mes / semana / día) con filtro por tablero y leyenda., Reconstruye la rejilla de celdas según el modo de vista., Recarga filtro/leyenda y pinta el periodo actual según el modo., Cambia la fecha de vencimiento de una tarea arrastrada a otro día., CalendarViewWidget.refresh() omite consultas costosas cuando el widget está… (+4 more)

### Community 2 - "MarkdownTextEdit"
Cohesion: 0.08
Nodes (20): MarkdownTextEdit, QTextEdit con atajos tipo Markdown para crear listas al vuelo. - `* `, `- `, `+…, Al pegar: las imágenes se insertan como imagen; una tabla (de Excel/Sheets/Word…, Si el texto plano pegado tiene pinta de tabla (varias líneas con tabuladores,…, Inserta una tabla `rows`x`cols` en la posición del cursor, con el estilo del…, Codifica un QImage como data URI PNG en base64., Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se…, Elimina el marcador escrito y convierte la línea actual en una lista. (+12 more)

### Community 3 - "CalendarSettingsDialog"
Cohesion: 0.15
Nodes (9): CalendarSettingsDialog, QDialog, Ajustes del calendario: sincronización iCalendar (.ics) para…, None = feed global (todos los tableros); si no, el id del tablero elegido., Valida y persiste la URL pública. Devuelve la URL, o None si está vacía., Guarda la URL, la copia al portapapeles y abre 'Añadir por URL' de Google., Guarda la URL, la copia y abre «Suscribirse desde la web» de Outlook.com., Copia la URL como enlace webcal:// para pegar en iPhone/iPad/Mac (iCloud). (+1 more)

### Community 4 - "test_ics_export.py"
Cohesion: 0.11
Nodes (26): build_ics(), _escape(), export_ics(), _fold_line(), Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)., Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados., Convierte la descripción HTML de una tarea en texto plano razonable., Deriva (SEQUENCE, LAST-MODIFIED) del `updated_at` de la tarea. SEQUENCE debe… (+18 more)

### Community 5 - "tasks.py"
Cohesion: 0.09
Nodes (25): get_task_links_bulk(), {task_id: [enlaces]} para varias tareas en una consulta (evita N+1 al pintar el…, advance_overdue_recurring(), advance_recurrence(), create_task(), delete_task(), get_tasks(), next_occurrence() (+17 more)

### Community 6 - "/graphify Pipeline"
Cohesion: 0.09
Nodes (24): Backlog Item: restore_task/restore_column FK Crash on Ctrl+Z, Backlog Item: ImagePreviewDialog Never Destroyed, Backlog Step 21: Third Forensic Bug-Hunt Pass Summary, Tech Debt: restore_column/restore_board Not Atomic Across Children, Unreleased Fix: Ctrl+Z FK Crash on Undoing a Deleted Task/Column, Unreleased Fix: ImagePreviewDialog Never Destroyed, /graphify add URL Ingestion, --watch Background Watcher (+16 more)

### Community 7 - "test_widgets_headless.py"
Cohesion: 0.08
Nodes (36): QDialog, SettingsDialog, _card_with_timer(), _collapsed_column_widget(), _drag_enter_event(), _drop_event(), Pruebas de humo (smoke tests) headless para widgets de Qt: construcción y unas…, Regresión: el texto describía el comportamiento antiguo de Ctrl+N (siempre la… (+28 more)

### Community 8 - "snapshots.py"
Cohesion: 0.21
Nodes (16): get_board(), get_columns(), get_task_links(), Captura todo el contenido de una tarea para poder recrearla (deshacer)., Recrea una tarea a partir de un snapshot. Devuelve el nuevo id., restore_board(), _restore_board_in_conn(), restore_column() (+8 more)

### Community 9 - "2. Implementation Tasks"
Cohesion: 0.15
Nodes (12): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, `board_view.py` — wiring + periodic badge refresh, Database layer, `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions, QA Report, `settings_dialog.py` — configurable threshold (+4 more)

### Community 10 - "tags.py"
Cohesion: 0.10
Nodes (20): create_tag_category(), create_tag_value(), delete_tag_category(), delete_tag_value(), get_or_create_tag_value(), get_tag_categories(), get_tag_value(), get_tag_values() (+12 more)

### Community 11 - "ColumnEditDialog"
Cohesion: 0.20
Nodes (5): BoardSelectionDialog, ColumnEditDialog, QDialog, Diálogo para seleccionar un tablero de destino para mover o copiar una columna., Diálogo para crear o editar una columna (nombre y color).

### Community 12 - "exporter.py"
Cohesion: 0.11
Nodes (28): boards_to_json(), _gather(), _plain(), Exportación de los tableros de Ekin a JSON, CSV o un informe Markdown.…, Informe de proyecto en Markdown: por tablero, sus columnas y tareas., Convierte HTML (descripción/nota) en texto plano razonable para exportar., Estructura anidada de contenido: tableros -> columnas -> tareas (+logs, tags,…, Volcado completo (tableros, columnas, tareas, etiquetas, enlaces y diario) como… (+20 more)

### Community 13 - "._collapse_hover_expanded_column"
Cohesion: 0.29
Nodes (4): Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la BD)…, Expansión temporal (por hover durante un arrastre) de una columna plegada:…, Repliega (BD + widget) la columna actualmente expandida por hover, si la hay.…, Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier arrastre de…

### Community 14 - "get_connection"
Cohesion: 0.17
Nodes (17): create_column(), delete_column(), get_column(), Pliega (collapsed=1) o despliega (0) una columna del tablero., Actualiza las posiciones de múltiples columnas. column_positions debe ser una…, set_column_collapsed(), update_column(), update_column_positions() (+9 more)

### Community 15 - "main.py"
Cohesion: 0.10
Nodes (18): Vista de calendario mensual para Ekin: muestra las tareas por su fecha de…, Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).…, Diálogo de búsqueda global de tareas. Filtra por texto (título/descripción),…, Pantalla de Ajustes de la aplicación: tema, notificaciones y persistencia.…, Diálogo "Atajos de teclado" (Ctrl+/): referencia estática de todos los atajos…, build_qss(), color_swatch_css(), hex_to_rgb() (+10 more)

### Community 16 - "SidebarWidget"
Cohesion: 0.13
Nodes (16): Cambia el tablero activo, actualiza los estilos visuales de los botones y emite…, Selecciona el tablero anterior (-1) o siguiente (+1) al activo, en el orden en…, Selecciona el tablero en la posición `index` (0-based, mismo orden visual que…, SidebarWidget, La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder ni…, El reloj debe estar en una fila propia (fila 0 del layout exterior), separada…, Regresión específica contra el bug de captura tardía de variable de bucle: las…, Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir… (+8 more)

### Community 17 - "_ClickOutsideFilter"
Cohesion: 0.12
Nodes (8): _ClickOutsideFilter, Filtro de eventos que detecta clics fuera del diálogo dentro de la ventana…, Carga los datos iniciales de la tarea y sus logs desde la base de datos., Devuelve el id de la etiqueta permanente «Prioridad», asegurando que existan…, Rellena el selector rápido de Prioridad con los valores actuales del catálogo…, Rellena el selector de Tablero vinculado con el resto de tableros (excluyendo…, Actualiza el botón y la etiqueta de tiempo transcurrido según…, QObject

### Community 18 - ".load_board"
Cohesion: 0.12
Nodes (8): QFrame, Carga las columnas y tareas de un tablero específico. `notify=False` evita…, Limpia todos los widgets del layout de columnas., Abre el diálogo para crear una columna., Abre el diálogo para editar nombre y color de una columna., Pliega o despliega una columna (persiste el estado) y recarga el tablero., Reordena las columnas del tablero actual tras arrastrar una por su título., Crea una copia de la columna en otro tablero seleccionado.

### Community 19 - "test_hover_expand.py"
Cohesion: 0.25
Nodes (15): _collapsed_state(), _make_board_with_columns(), Si el drop real aterriza en OTRA columna (no en la expandida por hover),…, Regresión del crash real reportado en producción: al soltar una tarjeta tras un…, La columna B reconstruida debe ocupar exactamente el mismo índice que tenía en…, Por petición del usuario: incluso si el drop aterriza DENTRO de la columna…, test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize(), test_finalize_is_noop_when_nothing_pending() (+7 more)

### Community 20 - "Part B: Semantic Extraction (Subagents)"
Cohesion: 0.14
Nodes (15): Confidence Scoring Rubric, Node ID Format Rule, Extraction Subagent Prompt Template, --cluster-only Re-clustering, Code-Only Change Fast Path (Skip Semantic), No API Key Required Rule, graph.json Shrink Guard (#479), Part A: Structural (AST) Extraction (+7 more)

### Community 21 - "FlowLayout"
Cohesion: 0.18
Nodes (3): QLayout, FlowLayout, Layout que distribuye los widgets de izquierda a derecha y salta de línea si no…

### Community 22 - "t"
Cohesion: 0.28
Nodes (5): QDialog, Gestor del catálogo de etiquetas permanentes. Panel izquierdo: las etiquetas…, TagManagerDialog, Devuelve la cadena asociada a `key`, interpolando **kwargs si se pasan., t()

### Community 23 - "ColumnWidget"
Cohesion: 0.14
Nodes (8): ColumnWidget, Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo suficiente:…, Pequeño botón cuadrado con un icono PINTADO (left/right/pencil) a juego con el…, Columna plegada: tira estrecha con botón de desplegar, contador y nombre…, Establece el diseño de la columna (borde y fondo) basado en su color., Muestra el menú contextual de la columna para editarla, moverla, copiarla o…, Elimina todos los widgets de tarea de la columna., Añade una tarjeta de tarea a la columna (no-op si está plegada).

### Community 24 - "BoardViewWidget"
Cohesion: 0.25
Nodes (13): BoardViewWidget, Refresca la insignia de tiempo transcurrido en todas las tarjetas con un…, Alterna la barra lateral y actualiza el icono: ◀ (plegar) / ▶ (desplegar)., _make_board(), test_add_task_sets_last_active_column(), test_column_background_click_sets_last_active_column(), test_column_widget_mouse_press_emits_column_activated(), test_quick_add_task_falls_back_to_first_column_when_nothing_active() (+5 more)

### Community 25 - "MainWindow"
Cohesion: 0.11
Nodes (8): MainWindow, Manejador si el tablero actual cambió en el sidebar., Abre el diálogo de búsqueda global; al elegir un resultado salta a su tarjeta., Abre la ventana de referencia de atajos de teclado (Ctrl+/)., Reescribe cada feed .ics con auto-sync configurado (el global de todos los…, Muestra u oculta la barra lateral., Verifica de forma silenciosa si hay actualizaciones en el repo de GitHub., QMainWindow

### Community 26 - "Release v0.6.0"
Cohesion: 0.18
Nodes (13): Board Archiving Feature, Calendar Board Filter + Legend, Export / Report Module (exporter.py), Keyboard Shortcuts (v0.6.0 Initial Set), Light Theme + Toggle, Per-Board .ics Feeds, Recurring Tasks Feature, Release v0.6.0 (+5 more)

### Community 27 - "CI Workflow (ruff + pytest)"
Cohesion: 0.18
Nodes (12): Backlog Item: CI Workflow Running pytest on Push/PR, v0.5.0: CI Workflow + ruff Added, CI Workflow (ruff + pytest), CI Lint Job (ruff), CI Test Job (pytest matrix py3.10-3.12), Create Git Tag + GitHub Release, extract_release_notes.py Script, Build Release Notes from CHANGELOG (+4 more)

### Community 29 - "database/__init__.py"
Cohesion: 0.19
Nodes (10): init_db(), Crea las tablas necesarias si no existen., get_scheduled_tasks(), get_task_board_id(), Devuelve el board_id al que pertenece una tarea (o None si no existe)., Devuelve las tareas con fecha de vencimiento (due_date) junto con su tablero.…, Busca tareas en todos los tableros (o en uno) con filtros opcionales. - text:…, search_tasks() (+2 more)

### Community 30 - "format_elapsed_time"
Cohesion: 0.24
Nodes (14): format_elapsed_time(), Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'., Pruebas de lógica pura para styles.format_elapsed_time: no requieren Qt., test_accepts_float_seconds(), test_exactly_one_day(), test_exactly_one_hour(), test_exactly_one_minute(), test_hours_and_minutes_under_a_day() (+6 more)

### Community 32 - ".__init__"
Cohesion: 0.14
Nodes (6): CalendarChip, DayCell, QFrame, Chip de tarea en el calendario. Se puede pulsar (abrir) o arrastrar a otro día…, Celda de un día del calendario: número + chips de tareas que vencen ese día.…, _swatch_icon()

### Community 33 - "backup_database"
Cohesion: 0.23
Nodes (11): backup_database(), _prune_backups(), Copias de seguridad automáticas de la base de datos de Ekin. En cada arranque…, Crea una copia de seguridad de `db_path` y conserva las `keep` más recientes.…, Deja solo las `keep` copias más recientes de `base` en `backup_dir`., Pruebas de las copias de seguridad automáticas de la base de datos., test_backup_creates_valid_copy(), test_backup_default_dir_is_sibling_backups_folder() (+3 more)

### Community 34 - "LogEntryWidget"
Cohesion: 0.16
Nodes (10): LogEntryWidget, QFrame, Actualiza el ancho de las imágenes y tablas del comentario para ajustarse al…, Una entrada del diario/chat, con botones (pintados) de editar y eliminar y…, Regresión: setTextInteractionFlags(Qt.TextSelectableByMouse) A SOLAS anulaba…, Verifica que un comentario multilínea tiene tamaño vertical y no se colapsa., test_log_entry_widget_multiline_text_vertical_sizing(), test_log_entry_widget_plain_text_keeps_default_cursor() (+2 more)

### Community 35 - ".__init__"
Cohesion: 0.18
Nodes (7): app_icon(), apply_win32_icon(), main(), Crea el icono de bandeja (habilita toasts nativos de Windows)., Icono de la app. Prefiere el .ico multi-resolución (mejor para la barra de…, Verifica si es la primera vez que se abre la app y crea datos de ejemplo., Fuerza los iconos nativos de Win32 (WM_SETICON) directamente en el HWND de…

### Community 37 - "test_main_window.py"
Cohesion: 0.26
Nodes (13): _close_window(), _make_task_on_board(), _make_window(), Pruebas headless para MainWindow (main.py): comportamientos que solo existen a…, Verifica que el título de la ventana principal es 'Ekin vX.X.X'., Construye una MainWindow apta para tests: __init__ agenda dos QTimer.singleShot…, Cierra y destruye la ventana de verdad (deleteLater + procesar el evento…, Regresión: editar una tarea desde el Calendario dejaba la tarjeta del tablero… (+5 more)

### Community 38 - "ExportDialog"
Cohesion: 0.15
Nodes (9): ExportDialog, ImportConfirmationDialog, QDialog, Diálogo modal para confirmar la importación de tableros desde JSON., Diálogo modal para configurar y ejecutar la exportación de tableros., Abre el diálogo modal de exportación (JSON/CSV/MD, todo o tablero activo)., Abre el selector de archivo JSON y el diálogo de confirmación de importación., test_export_dialog_initial_state_and_toggles() (+1 more)

### Community 39 - "RichTextToolbar"
Cohesion: 0.13
Nodes (5): Sustituye el contenido por un editor en línea con Guardar/Cancelar., QWidget, Barra de formato básica (negrita, cursiva, tachado, viñetas, tablas) para un…, Pide filas y columnas y crea una tabla vacía en la posición del cursor., RichTextToolbar

### Community 40 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.22
Nodes (8): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, Item 1 — Ctrl+N targets the last-interacted-with column, Item 2 — Two-row utility bar, Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 41 - "BoardEditDialog"
Cohesion: 0.22
Nodes (4): BoardEditDialog, Diálogo personalizado para crear o editar un tablero (nombre y color de fondo)., Abre el diálogo para crear un nuevo tablero con nombre y color., Abre el diálogo para copiar el tablero activo con un nuevo nombre.

### Community 42 - "QPushButton"
Cohesion: 0.29
Nodes (6): QPushButton, QDialog, Reejecuta la búsqueda con los filtros actuales y repinta la lista., Búsqueda global de tareas con filtros por tablero, etiqueta y vencimiento., SearchDialog, _swatch_icon()

### Community 43 - "test_timer_board_view.py"
Cohesion: 0.38
Nodes (9): _card_for(), _make_board_with_task(), Antes del fix, _build_column_widget releía el ajuste una vez POR COLUMNA…, test_build_column_widget_applies_configured_threshold(), test_build_column_widget_defaults_threshold_when_unset(), test_load_board_reads_timer_alert_hours_once_regardless_of_column_count(), test_refresh_timer_badges_noop_on_board_with_no_timers(), test_refresh_timer_badges_noop_on_welcome_screen() (+1 more)

### Community 44 - "boards.py"
Cohesion: 0.25
Nodes (7): create_board(), delete_board(), get_boards(), Devuelve los tableros. Por defecto excluye los archivados., Archiva (1) o desarchiva (0) un tablero. Los archivados se ocultan de la barra…, set_board_archived(), update_board()

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

### Community 51 - "ImagePreviewDialog"
Cohesion: 0.20
Nodes (7): ImagePreviewDialog, QDialog, Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra…, Regresión: antes solo se escalaba hacia abajo, así que una imagen ya pequeña…, Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog…, test_image_preview_dialog_is_destroyed_after_closing_when_parented(), test_image_preview_dialog_upscales_small_pixmap()

### Community 52 - "task_detail_dialog.py"
Cohesion: 0.31
Nodes (5): fit_html_images(), Ajusta o añade el atributo width a las etiquetas <img> y <table> para que nunca…, color_icon(), Genera un pequeño icono cuadrado del color indicado (para combos y listas)., Cadenas de la interfaz, centralizadas para facilitar una futura traducción.…

### Community 53 - ".reload_boards"
Cohesion: 0.22
Nodes (4): Vuelve a cargar la lista de tableros como widgets personalizados desde la base…, Archiva/desarchiva un tablero y recarga la lista., Mueve una columna arrastrada desde el tablero activo hasta el botón de otro…, Abre el diálogo para editar el nombre y color del tablero activo.

### Community 54 - "QLabel"
Cohesion: 0.48
Nodes (4): QLabel, QDialog, ShortcutsDialog, test_shortcuts_dialog_constructs_with_both_sections()

### Community 55 - "CLAUDE.md"
Cohesion: 0.29
Nodes (5): 1. Think Before Coding, 2. Simplicity First, 3. Surgical Changes, 4. Goal-Driven Execution, graphify

### Community 56 - "TaskDetailDialog"
Cohesion: 0.07
Nodes (26): QDialog, Habilita/inhabilita fecha y hora según los checks., Guarda el título, descripción, etiquetas y fecha de vencimiento., Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción…, Detiene y borra el temporizador: deja de contar y quita la insignia de la…, Borra definitivamente la tarea actual de la base de datos., Ajusta dinámicamente las imágenes y tablas de todos los comentarios cargados al…, Ancho máximo (px) para imágenes y tablas en el chat: reservando márgenes y la… (+18 more)

### Community 57 - "fixture"
Cohesion: 0.32
Nodes (7): fixture, _close_top_level_widgets_after_each_test(), db_path(), qapp(), QApplication compartida para toda la sesión de tests: cualquier test que…, Cierra y destruye (deleteLater) cualquier widget de nivel superior que un test…, Ruta a una base de datos SQLite temporal, inicializada con el esquema de Ekin.

### Community 58 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 59 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 60 - "TagPickerDialog"
Cohesion: 0.29
Nodes (4): QDialog, Selecciona una etiqueta del catálogo para una tarea. - Modo asignar…, Devuelve (tag_value_id | None, is_none). is_none indica que se eligió «Ninguno»., TagPickerDialog

### Community 61 - "TaskCard"
Cohesion: 0.20
Nodes (5): QFrame, Aplica dinámicamente el estilo a la tarjeta basándose en el color de fondo del…, Umbral (en horas) a partir del cual la insignia del temporizador se resalta en…, Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo…, TaskCard

### Community 62 - "Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//)"
Cohesion: 0.29
Nodes (7): Sidebar Shortcuts (❔) Button, i18n Pass Loop-Variable Shadowing Bugs (Prior Incident), Keyboard Shortcuts Wave (Ctrl+Shift+N/1-9/,/Shift+C//), Loop-Variable Late-Binding Avoidance Pattern, shortcuts_dialog.py Missing from py-modules Bug, select_board_by_index() Method, ShortcutsDialog Class

### Community 64 - "links.py"
Cohesion: 0.50
Nodes (3): add_task_link(), delete_task_link(), Añade un enlace/adjunto (URL o ruta) a una tarea. Devuelve su id.

### Community 65 - ".get_pending_notifications"
Cohesion: 0.33
Nodes (3): Tareas de todos los tableros que están atrasadas o vencen hoy o mañana.…, Actualiza el badge de la campana según atrasadas + vencimientos hoy/mañana., Muestra el popup de vencimientos anclado bajo la campana.

### Community 66 - ".init_ui"
Cohesion: 0.18
Nodes (4): QWidget, Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay., Limpia y dibuja las etiquetas actuales y la fecha de vencimiento., TaskListArea

### Community 67 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 68 - "._open_task_detail"
Cohesion: 0.22
Nodes (4): Abre el diálogo de detalle de una tarea. Devuelve True si el diálogo modificó o…, Desde la campana: ir al tablero de la tarea, mostrarlo y abrir su detalle., Desde la pastilla de tablero enlazado de una tarjeta: saltar a ese tablero., Desde el calendario: abrir el detalle y quedarnos en el calendario.

### Community 69 - "Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave"
Cohesion: 0.40
Nodes (5): Backlog Step 18: Click-to-Enlarge + Icon Cache/Redesign Wave, Backlog Step 19: v0.9.2 Same-Day Fixes, v0.9.2: Click-to-Enlarge Fix on Already-Posted Entries, v0.9.2: App Icon Transparency Retuned, README Feature: Click-to-Enlarge Pasted Images

### Community 70 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 71 - "settings.py"
Cohesion: 0.40
Nodes (4): get_setting(), Crea o actualiza un ajuste de la aplicación., Devuelve el valor de un ajuste, o `default` si no está definido., set_setting()

### Community 72 - "Calendar Drag-to-Reschedule"
Cohesion: 0.50
Nodes (4): Calendar Drag-to-Reschedule, CalendarViewWidget Class, data_changed Signal, update_task_due_date() Function

### Community 73 - "._build_column_widget"
Cohesion: 0.20
Nodes (4): Registra una acción deshacer/rehacer para un borrado (restaurar desde snapshot)., Construye un ColumnWidget completo (señales conectadas y, si está desplegada,…, Confirma y borra una columna., Abre el diálogo de detalle/chat de una tarea.

### Community 75 - "Cross-Repo Graph Merge"
Cohesion: 0.50
Nodes (4): Cross-Repo Graph Merge, Clone Single GitHub Repo, Monorepo Multi-Subfolder Merge, Step 0: GitHub Clone & Multi-Path Merge

### Community 76 - ".render_tags"
Cohesion: 0.10
Nodes (11): ClickableTagPill, QFrame, Pastilla de etiqueta cuyo cuerpo emite `clicked` (para editar el valor). El…, Dibuja las etiquetas asignadas como pastillas. Clic en la pastilla = editar el…, Ajusta la selección del combo de Prioridad a lo que haya en current_tags, sin…, Asigna (o reemplaza) el valor de una etiqueta permanente, garantizando un único…, Retira una etiqueta de la tarea (localmente) y re-renderiza., Edita el valor de una etiqueta ya asignada: cambiarlo o poner «Ninguno»… (+3 more)

### Community 77 - "BoardColumnsArea"
Cohesion: 0.27
Nodes (3): BoardColumnsArea, QWidget, Contenedor horizontal de columnas que acepta soltar una columna arrastrada para…

### Community 79 - "sidebar.py"
Cohesion: 0.14
Nodes (8): Diálogos para Exportación e Importación avanzada de tableros en Ekin.…, Genera una cadena amigable para nombres de archivo., _slugify(), Importación de tableros, columnas y tareas a Ekin desde archivos JSON.…, Confirma y elimina el tablero activo., Registra deshacer/rehacer del borrado de un tablero (restaurar desde snapshot)., Pila simple de deshacer/rehacer para acciones destructivas (borrar…, UndoAction

### Community 80 - "get_subtasks_progress_bulk() Function"
Cohesion: 0.67
Nodes (3): get_subtasks_progress_bulk() Function, get_task_tags_bulk() Function, TaskCard Subtask Progress Badge

### Community 81 - "v0.9.1: Local File Attachments on Task Links"
Cohesion: 0.67
Nodes (3): Backlog Item: Local File Attachments on Task Links, v0.9.1: Local File Attachments on Task Links, README Feature: Local File Attachments

### Community 82 - ".reload_logs"
Cohesion: 0.20
Nodes (5): Limpia y vuelve a cargar todos los logs/entradas del diario., Guarda la edición de un comentario (o cancela si new_html es None) y recarga., Crea una nueva entrada de diario con el texto del input., Abre el diálogo de forma síncrona sin bloquear la ventana padre, permitiendo…, Mueve la barra de desplazamiento del diario hasta abajo.

### Community 98 - "NotificationsPopup"
Cohesion: 0.24
Nodes (7): NotificationsPopup, QDialog, Pequeño icono cuadrado del color indicado (para listar tareas por tablero)., Popup emergente con las tareas atrasadas o que vencen hoy o mañana, agrupadas.…, _swatch_icon(), test_notifications_popup_empty(), test_notifications_popup_with_tasks()

### Community 99 - "compute_drop_index"
Cohesion: 0.29
Nodes (8): Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt: el…, Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el…, test_dragging_card_excludes_itself_from_count(), test_dragging_first_card_down_is_not_off_by_one(), test_drop_above_first_card_inserts_at_zero(), test_drop_at_end_inserts_after_last(), compute_drop_index(), Índice de inserción para una tarjeta soltada en `drop_y`. `cards_geom` es una…

### Community 100 - "TECHNICAL DESIGN DOCUMENT"
Cohesion: 0.33
Nodes (5): 1. Overview, 2. Implementation Tasks, 3. Acceptance Criteria, QA Report, TECHNICAL DESIGN DOCUMENT

### Community 101 - "show_image_preview"
Cohesion: 0.17
Nodes (11): pixmap_from_data_uri(), Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo…, Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una…, show_image_preview(), Maneja los enlaces clicados dentro de una entrada ya enviada. Hoy el único tipo…, Regresión: antes href y src eran el MISMO data URI (la miniatura ya reducida al…, test_markdown_text_edit_stores_higher_res_copy_for_preview(), test_pixmap_from_data_uri_decodes_valid_png() (+3 more)

### Community 121 - "._build_link_row"
Cohesion: 0.29
Nodes (3): _is_local_link(), True a menos que la cadena empiece por un esquema web reconocido (case-…, test_is_local_link_classifies_urls_vs_paths()

### Community 122 - "DraggableColumnTitle"
Cohesion: 0.25
Nodes (3): DraggableColumnTitle, QLabel del título de columna que permite iniciar un arrastre para reordenarla o…, Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta hijo…

## Knowledge Gaps
- **132 isolated node(s):** `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column`, `Item 2 — Two-row utility bar`, `Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it` (+127 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `t()` connect `t` to `CalendarViewWidget`, `CalendarSettingsDialog`, `test_widgets_headless.py`, `ColumnEditDialog`, `main.py`, `SidebarWidget`, `_ClickOutsideFilter`, `.load_board`, `ColumnWidget`, `MainWindow`, `.add_task`, `.__init__`, `LogEntryWidget`, `.__init__`, `BoardButton`, `ExportDialog`, `RichTextToolbar`, `BoardEditDialog`, `QPushButton`, `ImagePreviewDialog`, `task_detail_dialog.py`, `.reload_boards`, `QLabel`, `TaskDetailDialog`, `TagPickerDialog`, `.init_ui`, `._build_column_widget`, `._build_utility_bar`, `.render_tags`, `BoardColumnsArea`, `.notify_due_today`, `sidebar.py`, `NotificationsPopup`, `._build_link_row`?**
  _High betweenness centrality (0.168) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `get_connection` to `links.py`, `tasks.py`, `settings.py`, `snapshots.py`, `tags.py`, `boards.py`, `exporter.py`, `sidebar.py`, `board_ops.py`, `ics_sync.py`, `database/__init__.py`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `TaskDetailDialog` connect `TaskDetailDialog` to `LogEntryWidget`, `MarkdownTextEdit`, `._open_task_detail`, `RichTextToolbar`, `test_widgets_headless.py`, `._build_column_widget`, `.render_tags`, `main.py`, `_ClickOutsideFilter`, `.reload_logs`, `task_detail_dialog.py`, `t`, `._build_link_row`, `TagPickerDialog`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `TaskDetailDialog` (e.g. with `LogEntryWidget` and `MarkdownTextEdit`) actually correct?**
  _`TaskDetailDialog` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `BoardViewWidget` (e.g. with `UndoAction` and `ColumnWidget`) actually correct?**
  _`BoardViewWidget` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `MainWindow` (e.g. with `BoardViewWidget` and `CalendarViewWidget`) actually correct?**
  _`MainWindow` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `ekin-kanban`, `1. Overview`, `Item 1 — Ctrl+N targets the last-interacted-with column` to the rest of the system?**
  _132 weakly-connected nodes found - possible documentation gaps or missing edges._