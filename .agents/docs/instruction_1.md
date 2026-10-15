# TECHNICAL DESIGN DOCUMENT — Backlog "SW - Ekin" (sesión 2026-10-14)

## 0. Estado (2026-10-15, tras el OUTRO b063add)

| Oleada | Resultado |
|---|---|
| 1 | ✅ #83, #98, #99, #84, #82 en Done. #97: el cambio de `version` está integrado, pero la tarjeta está **aparcada en el Backlog** para replantear una fusión por campos en la sync `.ekboard`. |
| 2 | ✅ #85, #86, #87, #88 en Done. Mejora posterior pedida por el usuario: #104 (pie de página de estado, botón **Work** en lugar de «Start working», pestaña **Directorios locales** en Ajustes). El semáforo de #88 quedó en la barra lateral, como pedía la tarjeta. |
| 3 | ✅ #101, #102, #103 (edición concurrente, validada a mano; destapó el cierre nativo 0xc0000005 y la foto previa a la hoja de estilos, c8e1af6) y #74 **solo parte A**; las partes B y C se descartaron. |
| 4 | ⏳ #81: pendiente la fase 81.0 (ADR + sub-tarjetas), sin código hasta que el usuario apruebe el ADR. |

Nuevo hallazgo pendiente: #106 (cierre nativo en `pyside6.abi3.dll` al reiniciar tras la auto-actualización por `os.execv`).
Las casillas de las secciones de abajo reflejan lo implementado; las de las partes descartadas de #74 quedan sin marcar.

## 1. Overview

Plan de implementación de las 12 tarjetas de `📥 Backlog & Triage`: las 9 originales (#74,
#81–#88) y tres bugs que salieron de esta auditoría y se añadieron como tarjetas (#97, #98, #99). Basado en
auditoría del código actual (`mcp_server.py`, `local_ai.py`, `prompt_packs.py`,
`assets/prompt_packs/*.json`, `detail_dialog/markdown_edit.py`, `database/`, `sidebar.py`,
`board_view.py`) y de las CLIs instaladas en este PC (`claude` 2.1.299 vía npm `.cmd`,
`agy` 1.3.5 `.exe` nativo, `gemini` vía npm `.cmd`, `wt` disponible).

### Hallazgos que condicionan el plan

1. **El INTRO no puede funcionar tal y como está escrito.** `get_board_executive_summary`
   (`local_ai.generate_daily_standup_data`) solo clasifica columnas *done* e *in-progress* por
   palabras clave; **Ready, Review y Backlog son invisibles**. El INTRO pide "si In Progress está
   vacío, la primera de Ready" pero prohíbe `list_tasks` → el agente no tiene forma de verla
   (pasó en esta misma sesión). Raíz de #84.
2. **No existe el concepto de "rol de columna"**: cada prompt y el resumen adivinan por nombre o
   posición ("the column right after in-progress", "last (done) column"). #83 y #84 necesitan
   el mismo clasificador → se crea una sola vez (`column_roles.py`).
3. `list_task_comments` y `get_task` devuelven **HTML crudo de Qt** (DOCTYPE + `<style>`): el
   fix c778fcf solo cubrió `list_tasks`. Gasta tokens y ensucia el "latest handoff comment".
4. `get_board_by_uuid` (la ruta del MCP) devuelve un subconjunto de campos: `local_dir` (#85)
   hay que añadirlo explícitamente o el MCP no lo verá.
5. El arrastre de archivos (#82) ya tiene media tubería: `insertFromMimeData` trata `hasUrls()`
   y `canInsertFromMimeData` acepta URLs de archivo (verificado headless). Falta probar y
   blindar el camino real de *drop*.
6. Claude Code expone la cuota **de forma documentada** en el JSON de la status line
   (`rate_limits.five_hour|seven_day.used_percentage` + `resets_at`, solo Pro/Max y tras la
   primera respuesta de la sesión). `agy` no expone cuota (sin subcomando usage/quota).
7. `claude.cmd`/`gemini.cmd` son *shims* npm: un prompt multilínea con `< > ; "` **no puede
   pasarse como argumento a través de cmd.exe** de forma segura. `agy.exe` sí (`-i "<prompt>"`).
8. PatrimonIA ya resolvió el patrón Terminal↔PWA por Wi-Fi (`patrimonia/lan.py`,
   `mobile/{index.html,core.mjs,sw.js}`): escucha LAN a demanda + TLS con mkcert (requisito del
   service worker) + mDNS + QR de emparejamiento + cola de eventos idempotente. #81 debe
   reutilizarlo, no reinventarlo.

9. **Mover entre columnas no incrementa `tasks.version`** — ni el arrastre
   (`database.update_task_positions`, usado también por deshacer/rehacer) ni MCP `move_task`.
   En `board_sync` (~L627-664), si un colaborador editó la misma tarea, la sync adopta la columna
   remota y **se pierde el movimiento local**; si no la tocó, la red `differs` genera un
   conflicto falso. → tarjeta **#97**.
10. **MCP `update_task` es el único llamador de producción del `database.update_task` legado**
    (los tests también lo usan como helper): pisa `tag_text`/`tag_color`, no admite `due_time`,
    guarda `""` en vez de NULL al quitar la fecha y no es atómico. → tarjeta **#98**.
11. **El Markdown que envían los agentes se guarda sin convertir** (`create_task`,
    `create_tasks_batch`, `update_task`, `add_task_comment`), pero la app lo pinta como HTML
    (`desc_input.setHtml`, `QLabel` rich text en el Journal): los saltos de línea desaparecen y
    todo sale en un párrafo (p. ej. #74). `QTextDocument.setMarkdown()` + `toHtml()` funciona
    sin `QApplication` y en hilos secundarios (verificado). → tarjeta **#99**.

### Orden de ejecución (por dependencias y riesgo)

| Oleada | # | Tarjeta | Esfuerzo | Depende de |
|---|---|---|---|---|
| 1 | 97 | BUG: mover entre columnas no sube `version` (sync) | S | — |
| 1 | 83 | BUG: agente pasa a Done → quitar fecha | S | 97 (mismo UPDATE de `move_task`) |
| 1 | 98 | BUG: MCP `update_task` por la ruta legada | S | — |
| 1 | 99 | BUG: Markdown de agentes → un único párrafo | S | 98 (mismo `update_task`) |
| 1 | 84 | Revisión AI PROMPTS + resumen con flujo por columnas | M | 83 (`column_roles`) |
| 1 | 82 | Drag&Drop de archivos | S | — |
| 2 | 85 | Asociar directorio local con tablero | M | — |
| 2 | 86 | Visor `diary.md` / `diary_archive.md` | S | 85 |
| 2 | 87 | START WORKING (lanzar CLI) | M | 85, 84 |
| 2 | 88 | Semáforo de cuota de CLIs | M | 87 (paso de init opcional) |
| 3 | 101 | BUG: el servidor MCP no arranca al abrir Ekin | S | — |
| 3 | 102 | BUG: «TaskCard already deleted» al cerrar el detalle | S | — |
| 3 | 103 | BUG: edición concurrente (cambios perdidos al cerrar el detalle) | S | — |
| 3 | 74 | Respuestas MCP en inglés (**solo A**; B y C descartadas) | S | 84 (mismos tools) |
| 4 | 81 | PWA Ekin Móvil | XL (épica) | ADR aprobado |

### Flujo de trabajo por tarjeta

`move_task` → ⚡ In Progress · test rojo · implementación · `pytest` completo + `ruff` verdes ·
CHANGELOG `[Unreleased]` + `backlog.md` + `diary.md` · commit Conventional `(#id)` ·
comentario DONE + `move_task` → 🔍 Code Review & QA. Push a `main` tras tests verdes; OUTRO al
final mueve a 🚀 Done con hash. `graphify update .` tras cambios de código.

---

## 2. Implementation Tasks

### #97 — BUG: mover entre columnas no incrementa `tasks.version`  `[S]`

- [x] Test rojo en `tests/test_board_sync.py` (con los helpers del archivo): tablero sincronizado
  → mover la tarea de columna en local (`update_task_positions`) + editar su título en el
  `.ekboard` remoto subiendo `version` → `sync_board_with_file` → la tarea conserva la
  columna local **y** el título remoto. Segundo test: mover sin cambios remotos →
  `SyncResult.conflicts == 0`.
- [x] `database/tasks.py::update_task_positions`: por cada tupla,
  `version = version + CASE WHEN column_id != ? THEN 1 ELSE 0 END` (se compara con la columna
  nueva antes de sobrescribirla; el `SET` de SQLite evalúa con los valores previos de la fila).
  Reordenar dentro de la misma columna no sube `version`.
- [x] `mcp_server._tool_move_task`: el mismo `CASE` en su UPDATE.
- [x] Tests: reordenar en la misma columna no cambia `version`; arrastre, deshacer y MCP
  `move_task` suben exactamente 1; `tests/test_batch_drag_drop.py` y
  `tests/test_incremental_rendering.py` siguen verdes.

### #83 — BUG: agente IA pasa una tarjeta a Done → quitar fecha  `[S]`

Decisión D1 (usuario, 2026-10-14): movimientos **vía MCP** a la columna con rol `done`, en
**cualquier tablero** (SW, GTD, Opositor…). Los arrastres manuales no cambian. La fecha retirada
queda registrada en el diario.

- [x] `column_roles.py` (nuevo, puro, sin Qt): constantes `BACKLOG, READY, IN_PROGRESS, REVIEW,
  DONE, OTHER`; `classify_column(name: str) -> str` (minúsculas + sin acentos vía
  `unicodedata`; precedencia done > review > in_progress > ready > backlog). Palabras clave:
  done = `done, hecho, shipped, completad, terminad, cerrad, resuelto, finaliz, dominad`;
  review = `review, revision, qa, test, validac, verificac`; in_progress = las actuales de
  `local_ai` (`progress, curso, doing, haciendo, wip, activo, desarrollo`); ready = `ready,
  listo, next, proxim, to code, selected`; backlog = `backlog, triage, inbox, bandeja,
  pendiente, todo, to do, por hacer`. `column_roles(columns) -> dict[int, str]`: aplica
  `classify_column` y, si ninguna es backlog/done, asigna backlog a la primera `other` y done a
  la última `other` por `position`.
- [x] `local_ai.generate_daily_standup_data`: sustituir las tuplas inline de `is_done` /
  `is_in_progress` por `column_roles(columns)` (comportamiento idéntico para los nombres actuales).
- [x] `mcp_server.McpToolExecutor._tool_move_task`: si el rol destino es `done` y la tarea tiene
  `due_date`: en el **mismo UPDATE** de #97, `due_date = NULL, due_time = NULL` (como un
  movimiento a Done siempre cambia de columna, `version` sube exactamente una vez). Añadir al audit
  "Fecha de vencimiento retirada (era YYYY-MM-DD[ HH:MM]) al pasar a '<columna>'." y
  `"due_date_cleared": true` a la respuesta.
- [x] Tests: `tests/test_column_roles.py` (tabla con las columnas de las plantillas
  `software_agile`, `gtd_personal`, `opositor_study`, `getting_started` + fallbacks);
  `tests/test_mcp.py`: done limpia fecha/hora, sube `version` y lo registra (en un tablero SW
  y en uno de plantilla GTD); columna no-done la conserva; tarea sin fecha → sin audit extra;
  `tests/test_local_ai_rdi.py` sigue verde.

### #98 — BUG: MCP `update_task` por la ruta legada  `[S]`

- [x] Test rojo en `tests/test_mcp.py`: tarea con `tag_text`/`tag_color`, `recurrence`,
  `linked_board_id` y `due_time` → MCP `update_task` (solo `title`) → se conservan todos;
  `due_time` nuevo se guarda; `due_date: ""` deja `due_date` y `due_time` a NULL; `version` sube
  exactamente 1.
- [x] `mcp_server._tool_update_task`: leer la tarea completa y llamar a
  `database.save_task_full(...)` con los valores actuales para lo que no venga en `args`
  (`recurrence`, `linked_board_id`, `tag_text`, `tag_color`, `due_time`); `due_date`/`due_time`
  vacíos → `None`; si `due_date` queda a `None`, `due_time` también. Etiquetas y prioridad:
  calcular `tag_value_ids` con la lógica actual y pasarlos en la misma llamada (`None` si no se
  tocan, así `save_task_full` no borra las etiquetas). El audit del diario va después.
- [x] `get_mcp_tools_schema`: `update_task` acepta `due_time` (`HH:MM`).
- [x] `database.update_task` **se mantiene**: aunque deja de tener llamadores en producción,
  5 tests lo usan como helper (`test_board_sync.py`, `test_database.py`).

### #99 — BUG: el Markdown de los agentes MCP se ve como un único párrafo  `[S]`

- [x] `html_utils.py` (raíz, ya compartido por el MCP): `markdown_to_qt_html(text: str) -> str`.
  Vacío → `""`; si `Qt.mightBeRichText(text)` → se devuelve tal cual; si no →
  `QTextDocument.setMarkdown(text, MarkdownDialectGitHub | MarkdownNoHTML)` + `toHtml()` (sin
  dependencias nuevas). Verificar al implementar que `MarkdownNoHTML` convierte las etiquetas en
  texto; si no, escapar `<`/`>` antes.
- [x] `mcp_server`: aplicarlo a `description` en `_tool_create_task`, `_tool_create_tasks_batch`
  y `_tool_update_task` (sobre la ruta de #98), y al comentario en `_tool_add_task_comment`
  (sustituye a `html.escape`); el prefijo de autoría se escapa como `\[cliente\]:` para que
  CommonMark no lo trate como definición de enlace. El embedding semántico se sigue indexando
  con el texto original.
- [x] `database/__init__.py`: migración única (bandera `md_content_migrated` en `app_settings`)
  que convierte las `tasks.description` y `task_logs.content` que no son rich text y contienen
  `\n`. Los backups de arranque (`backups.py`) ya cubren el rollback.
- [x] Tests (`tests/test_mcp.py`, `tests/test_database.py`): encabezados, listas, task lists,
  negrita y `code` → HTML de Qt; el HTML de entrada no se toca; `<script>`/`<img>` en Markdown
  salen como texto; el prefijo `[cliente]:` sigue visible; `list_tasks` y
  `get_task_condensed_context` devuelven texto limpio con viñetas; la migración convierte solo
  los registros afectados y es idempotente.
- [x] Verificación manual en la app real: una tarjeta y un comentario creados por MCP con
  Markdown se ven con formato.

### #84 — Revisión de AI PROMPTS y arquitectura de columnas  `[M]`

- [x] `local_ai.generate_daily_standup_data`: añadir
  `columns_flow: [{id, name, role, count, wip_limit, top_tasks: [{id, title}] (≤3; vacío en done)}]`
  y `active_task: {id, title, column_name, role} | None`, resuelta como primera tarjeta de
  **in_progress → review → ready** (orden de columnas; dentro, `position`).
- [x] `local_ai.format_daily_standup_markdown`: secciones nuevas "🎯 Tarea activa" y
  "🧭 Flujo por columnas" (`nombre [rol] n/límite: #id título, …`), y top 5 del backlog.
- [x] `mcp_server`: `_tool_get_board_executive_summary` devuelve `active_task` y `columns_flow`
  (títulos saneados si `mask_sensitive`); `_tool_list_columns` y `_tool_get_board_info` añaden
  `role`; `_build_instructions` lista columnas con su rol.
- [x] `mcp_server._tool_list_task_comments`: `content` pasa por `clean_html_description` y acepta
  `mask_sensitive` (actualizar el esquema en `get_mcp_tools_schema`); `_tool_get_task`: limpiar
  `description` y `logs[].content` igual que `list_tasks`.
- [x] `mcp_server._tool_get_task_condensed_context`: añadir `latest_comment` (última entrada
  limpia y enmascarada) — es lo que el INTRO llama "latest handoff comment".
- [x] `assets/prompt_packs/dev.json`, reescribir con roles explícitos:
  - **INTRO**: Active Task = `active_task` del resumen (el servidor ya aplica
    In Progress → Review/QA → Ready). Si es `null`, proponer las primeras tarjetas del Backlog
    (de `columns_flow`) para triage. La salida añade una línea "Pending: n Ready · n Review ·
    n Backlog". Se mantiene la prohibición de `list_tasks`/`get_task` (ya no hace falta).
  - **FEATURE_PLAN / FEATURE_BUILD / OUTRO / REMEDIATE / AUDIT / INITIAL / MIGRATE / RECOVER**:
    "first (backlog) column", "in-progress column", "column right after in-progress", "last (done)
    column" → "la columna con `role` backlog / in_progress / review / done de `list_columns`".
    OUTRO: tarjetas terminadas = las de `review` (y `in_progress` cerradas hoy) → `done`; Next
    Step sobre el `active_task` de un resumen recién pedido.
- [x] `assets/prompt_packs/gtd.json` y `opositor.json`: revisar cada prompt contra las columnas
  de su plantilla (`templates.py`) y corregir referencias inexistentes o ambiguas.
- [x] `templates.py`: revisar el `ai_system_prompt` de las tres plantillas por la misma razón.
- [x] Tests: `tests/test_local_ai_rdi.py` (precedencia de `active_task`; `None` si todo vacío;
  `columns_flow` con roles); `tests/test_mcp.py` (`list_task_comments`/`get_task` sin
  `<!DOCTYPE`/`<style>`; `role` en `list_columns`; `latest_comment`);
  `tests/test_prompt_clipboard.py` (los packs de fábrica cargan, sus `{{variables}}` son de
  `board_variables` y el INTRO de DEV usa `active_task`).

### #82 — Drag&Drop de archivos en Description y Journal  `[S]`

- [x] Test rojo en `tests/test_widgets_headless.py`: simular
  `QDragEnterEvent`/`QDragMoveEvent`/`QDropEvent` con `QMimeData.setUrls([file://…])` (uno y
  varios archivos) sobre el `viewport()` de `desc_input`, `log_input` y del editor de un
  `LogEntryWidget` en edición. Esperado: enlace "📄 nombre" en el punto de drop, una emisión de
  `local_link_pasted` por archivo, el archivo en Enlaces/Adjuntos (sin duplicados) y visible
  en el popup `@`.
- [x] Si falla, `detail_dialog/markdown_edit.py::MarkdownTextEdit`: sobrescribir
  `dragEnterEvent`/`dragMoveEvent`/`dropEvent` para mime con URLs locales:
  `setDropAction(Qt.CopyAction)` (el Explorador propone *Move*), colocar el cursor con
  `cursorForPosition(event.position().toPoint())`, llamar a `insert_local_files(paths)` y
  `acceptProposedAction()`. Cualquier otro mime → `super()`.
- [x] Verificación manual en la app real: Explorador → Description, Journal (nueva entrada y
  edición de una publicada), varios archivos y una carpeta.

### #85 — Asociar un directorio local con el tablero  `[M]`

- [x] `database/__init__.py`: migración aditiva `boards.local_dir TEXT DEFAULT NULL` (patrón
  `PRAGMA table_info`). `database/boards.py`: `set_board_local_dir(board_id, path|None)` (en
  `__all__`), y `local_dir` en `get_board`, `get_board_by_uuid` y `get_boards`.
- [x] Es un dato de máquina: **no** se escribe en `.ekboard` (`board_sync.export_board_to_sync_dict`),
  ni en exportaciones JSON (`exporter`), ni en plantillas (`templates.export_board_to_template`),
  ni se copia con `copy_board`.
- [x] `sidebar.py::BoardEditDialog(..., local_dir=None)`: fila "Directorio local (repo)" con
  `QLineEdit` de solo lectura + "Examinar…" (`QFileDialog.getExistingDirectory`) + "Quitar";
  atributo `self.local_dir`; `get_data()` sin cambios (contrato intacto). El flujo de editar
  tablero (`sidebar.py` ~1031/1050) persiste con `set_board_local_dir`. Textos EN/ES en
  `strings.py`.
- [x] MCP: `get_board_info` añade `local_directory`; `_build_instructions` añade
  "Directorio local del repositorio (CWD esperado): <ruta>" si está definido.
  `prompt_packs.board_variables` añade `repo_path` cuando exista.
- [x] `detail_dialog/repo_files.py` (nuevo, puro): `list_repo_files(root, limit=5000) -> list[str]`
  (rutas relativas): `git -C root ls-files --cached --others --exclude-standard` (timeout 3 s,
  `CREATE_NO_WINDOW`); si falla, `os.walk` saltando `.git, venv, .venv, node_modules,
  __pycache__, dist, build, .pytest_cache`.
- [x] `TaskDetailDialog._task_links_for_mentions`: enlaces de la tarea primero y después los
  archivos del repo (`{"url": ruta_absoluta, "label": ruta_relativa, "source": "repo"}`), con la
  lista calculada de forma perezosa al primer `@` y cacheada por diálogo.
  `MarkdownTextEdit._insert_mention`: para elementos locales emite `local_link_pasted(url, label)`
  (el diálogo ya deduplica) → el archivo entra en Enlaces/Adjuntos. Icono distinto para archivos
  del repo (`lucide_icon` existente).
- [x] Tests: migración + set/get; exportaciones sin `local_dir`; `list_repo_files` con
  `.gitignore` (repo git temporal) y con fallback; el proveedor `@` incluye archivos solo si el
  tablero tiene `local_dir`; elegir un archivo del repo lo añade a los enlaces.

### #86 — Visor de `diary.md` / `diary_archive.md`  `[S]`

- [x] `diary_viewer_dialog.py` (nuevo): `DiaryViewerDialog(board_id, db_path, parent)` con
  `QTabWidget`, una pestaña por archivo existente de (`diary.md`, `diary_archive.md`) en
  `local_dir`; cada una con un `QTextBrowser.setMarkdown(texto)` (UTF-8, `errors="replace"`) y
  `setOpenExternalLinks(True)`; botones "Recargar" (conserva el scroll) y "Abrir en editor"
  (`QDesktopServices.openUrl`). `self.finished.connect(self.deleteLater)` (patrón anti-fuga).
- [x] `board_view.py`: botón de cabecera `diary_btn` (lucide `book-open`), visible solo si el
  tablero tiene `local_dir` y existe al menos un archivo; se reevalúa en `load_board`.
- [x] Tests: pestañas solo para archivos existentes; el Markdown se renderiza (texto del
  encabezado sin `#`); visibilidad del botón según `local_dir`.

### #87 — START WORKING: lanzar la CLI desde el tablero  `[M]`

Decisión D2 (usuario, 2026-10-14): **consola externa**. Una terminal embebida exige ConPTY + emulador
ANSI (p. ej. `pywinpty` + widget propio): mucho riesgo para poco valor. En Windows 11,
`CREATE_NEW_CONSOLE` ya abre en Windows Terminal si es la consola por defecto.

- [x] `cli_tools.py` (nuevo): registro `CliTool(id, name, exe, update_args, prompt_args)`:
  `claude` (update `["update"]`, prompt `[p]`), `agy` (update `["update"]`, prompt `["-i", p]`),
  `gemini` (sin update, prompt `["-i", p]`). `detect_installed()` vía `shutil.which`.
  `build_launch(tool, prompt) -> (argv, via_clipboard)`: si el ejecutable resuelto es
  `.cmd`/`.bat` → argv sin prompt y `via_clipboard=True` (hallazgo 7); si es `.exe` → prompt
  como argumento.
- [x] Registro del MCP: `claude` → `claude mcp get <name>`; si no existe,
  `claude mcp add --transport sse <name> <url>` con `cwd=local_dir`. `agy` → determinar la
  sintaxis con `agy mcp add --help` al implementar; si no es automatizable, avisar y copiar la
  config.
- [x] `start_working.py` (nuevo): `StartWorkingWorker(QThread)` con señal de progreso por paso:
  (1) MCP del tablero activo (`mcp_enabled`) y `get_mcp_manager().start()`; si el MCP del
  tablero está desactivado → abrir `McpSyncDialog` y abortar; (2) `<cli> update` (timeout 120 s,
  fallo no bloqueante); (3) registro del MCP; (4) lanzamiento con
  `subprocess.Popen(argv, cwd=local_dir, creationflags=CREATE_NEW_CONSOLE)`.
- [x] Prompt: prompt `intro` del pack del tablero (`load_pack(resolve_pack_id(...))`; si no hay
  `intro`, el primero) con `fill_variables(..., board_variables(board))`; las variables sin
  resolver se piden con `prompt_clipboard_dialog.ask_variable_values`. Con `via_clipboard`
  → se copia el prompt y se muestra el aviso "INTRO copiado: pégalo con Ctrl+V".
- [x] Selección: con más de una CLI detectada, modal de elección (lista + Aceptar) y el proceso
  continúa; con ninguna, mensaje con las CLIs soportadas.
- [x] `board_view.py`: botón de cabecera "Start working" (lucide `play`) visible solo con
  `local_dir`; diálogo de progreso con los 4 pasos.
- [x] Tests (sin procesos reales: `subprocess` y `shutil.which` simulados): detección;
  `build_launch` para `.exe` y `.cmd`; secuencia y abortos del worker; visibilidad del botón.

### #88 — Semáforo de cuota restante de las CLIs  `[M]`

- [x] `scripts/ekin_statusline.py` → se instala en `~/.ekin/bin/`: lee el JSON de stdin, escribe
  `~/.ekin/cli_quota/claude.json` (`rate_limits` + `captured_at`), y si había una status line
  previa (guardada en `~/.ekin/cli_quota/claude_prev_statusline.json`) le reenvía el mismo stdin
  e imprime su salida; si no, imprime una línea mínima (`5h 23% · 7d 41%`).
- [x] `cli_quota.py` (nuevo): `install_claude_statusline()` / `uninstall_claude_statusline()`
  sobre `~/.claude/settings.json` — **solo tras pulsar un botón explícito**, con copia de
  seguridad, conservando el resto de claves y restaurando la status line previa al
  desinstalar. Usa el `python.exe` de Ekin (`sys.executable`; no `pythonw`, la status line
  necesita stdout). `read_quota(tool_id) -> QuotaSnapshot | None` (ventanas con `resets_at`
  vencido = sin dato). `quota_state(snapshot) -> green|amber|red|grey` sobre el mayor uso de
  5h/7d (verde < 70 %, ámbar 70–90 %, rojo ≥ 90 %, gris = sin datos o caducado).
- [x] `agy` / `gemini`: sin fuente documentada → "Sin datos (la CLI no expone la cuota)".
  Volver a revisar `agy help` al implementar.
- [x] `sidebar.py` (barra de utilidades, junto a calendario y ajustes, como pide la tarjeta): botón semáforo (punto pintado con el color de
  estado) → popover por CLI detectada: "Sesión (5 h): 77 % restante — se reinicia 15:00",
  "Semanal (7 d): 59 % restante — lun 10:00", "Datos de hh:mm (se actualizan mientras hay una
  sesión de Claude Code abierta)", y botón Activar/Desactivar lectura. Refresco con
  `QFileSystemWatcher` sobre `claude.json`.
- [x] Integración con #87: el diálogo de progreso muestra la cuota de la CLI elegida y avisa si
  está en rojo antes de lanzar.
- [x] Tests: parseo y estados; caducidad por `resets_at`; el script escribe el snapshot y
  encadena la status line previa (subproceso real con un one-liner de Python); instalar y
  desinstalar sobre un HOME temporal conservando claves y creando la copia de seguridad.

### #101 — BUG: el servidor MCP no arranca al abrir Ekin  `[S]`

Hallazgo de la Oleada 2: `McpManager.start()` solo se llama al guardar el diálogo MCP
(`mcp_sync_dialog.py:373`), así que tras cada reinicio (incluida la auto-actualización) el MCP
queda caído hasta abrir ese diálogo.

- [x] Test rojo: `MainWindow` con un tablero `mcp_enabled = 1` llama a `get_mcp_manager().start()`;
  sin tableros con MCP, no lo llama.
- [x] `main.py` (`MainWindow.__init__`, tras `init_db` y la migración): si
  `any(b["mcp_enabled"] for b in database.get_boards(include_archived=True))` →
  `get_mcp_manager(database.DB_NAME).start()`; un `False` (puerto ocupado) solo se registra en el log.
- [x] `tests/test_main_window.py` ya neutraliza timers y llamadas externas al construir
  `MainWindow`: simular `get_mcp_manager` igual, para que ningún test abra el puerto 8765 real.

### #102 — BUG: «TaskCard already deleted» al cerrar el detalle  `[S]`

- [x] Test rojo en `tests/test_widgets_headless.py`: `TaskCard` con un manejador de `clicked` que
  destruye la tarjeta (como la recarga por MCP durante el `exec()` del detalle) → el
  `mouseReleaseEvent` no lanza `RuntimeError`.
- [x] `widgets.py::TaskCard.mouseReleaseEvent`: llamar a `super().mouseReleaseEvent(event)` antes de
  emitir `clicked` / `ctrl_clicked` (no tocar `self` tras el bucle anidado).

### #74 — Respuestas MCP en inglés para ahorrar tokens  `[A: S · B: S · C: M]`

Decisión D4 (usuario, 2026-10-14): A ya; B como puerta go/no-go; C solo si B lo justifica.
**Cierre (usuario, 2026-10-15): #74 se cierra solo con la parte A; B y C se descartan.**

- [x] **A. Texto del servidor en inglés (sin LLM, coste cero):** descripciones de
  `get_mcp_tools_schema`, `_build_instructions`, mensajes de error del ejecutor y
  `format_daily_standup_markdown` (solo lo usa el MCP — verificado). Los audits del diario
  siguen en el idioma de la UI (los ve el usuario). Ajustar los tests que comparan cadenas.
- [ ] ~~**B. Medición (spike):**~~ **DESCARTADA (2026-10-15).** `scripts/measure_mcp_tokens.py` vuelca las respuestas reales **BLOQUEADO (2026-10-14)**: sin LLM local ni credenciales de Anthropic en este PC; pendiente de decisión del usuario.
  (`list_tasks`, resumen ejecutivo, `get_task_condensed_context` de 5 tarjetas) en ES y su
  traducción EN con el modelo candidato, y mide tokens (endpoint `count_tokens` de Anthropic
  si hay `ANTHROPIC_API_KEY`; si no, aproximado y marcado como tal) y latencia por tarjeta.
  Candidatos: el Qwen2.5-Coder-1.5B actual frente a un instruct generalista ~3B Q4 vía
  `llama-server`. **Puerta:** seguir con C solo si ahorro ≥ 20 % en contenido de usuario y
  p95 < 3 s por tarjeta en este PC; si no, cerrar C como won't-do y documentarlo.
- [ ] ~~**C. Traducción LLM opt-in (si B pasa):**~~ **DESCARTADA (2026-10-15).** `mcp_translation.py` con
  `translate_response(data)` que recorre las claves `title, description, content,
  journal_summary, latest_comment, executive_markdown`; caché en la tabla nueva
  `translations(src_hash TEXT PRIMARY KEY, lang TEXT, text TEXT, created_at TEXT)`. Acierto →
  inglés; fallo → original + encolar en un `TranslationWorker` (hilo daemon, cola única,
  `local_ai.stream_openai_chat_completion` + circuit breaker). Sin LLM → original y nada en
  cola. Activación por tablero `boards.mcp_translate_en INTEGER DEFAULT 0` en `McpSyncDialog`
  con estado del motor y "Descargar modelo" (reutiliza las funciones del runner de
  `local_ai`). Gancho en `McpToolExecutor.execute` tras el handler.
- [ ] Tests C: desactivado → salida idéntica y cero llamadas al LLM; acierto de caché →
  inglés; fallo → original + encolado; sin LLM → original y nada en cola; un worker simulado
  rellena la caché.

### #81 — PWA Ekin Móvil  `[XL — épica]`

Decisión D3 (usuario, 2026-10-14): **PWA, LAN primero, reutilizando el patrón de PatrimonIA**.
Frente a una app nativa: coste 0 (frente a 99 USD/año de Apple + 25 USD de Google Play, dos
bases de código y revisiones de tienda) y cubre el alcance pedido (CRUD de tarjetas, fechas,
etiquetas, mover entre columnas, Description/Journal). Límites de iOS: sin sincronización en
segundo plano y almacenamiento desalojable — aceptable con el escritorio como fuente de verdad.
El acceso fuera de la Wi-Fi ("cloud") se aplaza a una fase posterior vía Tailscale (HTTPS sin
backend propio), sin sincronizar la app entera por la nube.

En esta sesión solo se hace la fase 0; el resto entra como sub-tarjetas en el Backlog:

- [ ] **81.0 ADR + contrato API** (`.agents/docs/adr/0001-ekin-mobile-pwa.md`): topología,
  seguridad (escucha a demanda atada a la IP de LAN, TLS con mkcert, token por dispositivo con
  revocación, sin columnas ni tableros editables), endpoints `GET /m/snapshot` y
  `POST /m/events` (cola idempotente por `client_uuid`: `create_task, update_task, move_task,
  add_log, add_link`), conflictos por `tasks.version` (el perdedor se archiva en el diario, como
  `board_sync`) y edición del HTML de Qt (sanear en el escritorio).
- [ ] 81.1 Escucha LAN + TLS + mDNS `ekin.local` + emparejamiento QR (deps `zeroconf`, `qrcode`).
- [ ] 81.2 PWA de solo lectura offline (tableros → columnas → tarjetas → detalle), JS sin
  framework como `PatrimonIA/mobile/`, con `sw.js`.
- [ ] 81.3 Escrituras por cola: crear, mover, fecha y etiquetas.
- [ ] 81.4 Edición de Description y nueva entrada de Journal.
- [ ] 81.5 Evaluar el acceso remoto con Tailscale.

---

## 3. Acceptance Criteria

- **Global:** `pytest` 100 % verde y `ruff` limpio tras cada tarjeta; un commit por tarjeta;
  CHANGELOG `[Unreleased]`, `backlog.md` y `diary.md` al día; sin cambios en el
  comportamiento de los tableros que no usan la funcionalidad nueva.
- **#97:** en un tablero compartido, un movimiento local sobrevive a una edición remota de la
  misma tarea; mover sin cambios remotos da 0 conflictos; reordenar en la misma columna no
  cambia `version`.
- **#98:** MCP `update_task` no pisa campos que no recibe, admite `due_time`, al quitar la fecha
  deja fecha y hora a NULL y sube `version` una sola vez.
- **#99:** las descripciones y comentarios en Markdown enviados por MCP se ven con formato en la
  ficha y en el Journal; los datos antiguos afectados se reparan una sola vez; ningún HTML
  enviado por el agente se interpreta.
- **#83:** mover vía MCP a la columna `done` de cualquier tablero deja `due_date`/`due_time` a
  NULL, sube `version`, registra la fecha antigua en el diario, y la tarea desaparece del
  Calendario, de Mi trabajo y de las notificaciones. Los movimientos a otras columnas y los
  arrastres manuales no cambian.
- **#84:** con In Progress vacío y Ready con tarjetas, el INTRO devuelve la primera de Ready
  **sin** `list_tasks`; con ambas vacías y Review con tarjetas, la de Review; con todo vacío,
  propone las de Backlog. Ninguna respuesta MCP contiene `<!DOCTYPE` ni `<style>`. Los tres
  packs solo referencian roles o columnas que existen en su plantilla.
- **#82:** arrastrar 1..N archivos (o una carpeta) desde el Explorador a Description, a una
  nueva entrada del Journal o a una entrada en edición inserta los enlaces en el punto de
  drop, los añade una sola vez a Enlaces/Adjuntos y aparecen al escribir `@`.
- **#85:** el directorio se puede fijar, cambiar y quitar desde Editar tablero; persiste;
  nunca sale de la máquina (.ekboard, exportación, plantillas); el MCP lo expone; `@` lista
  los archivos del repo respetando `.gitignore` y elegir uno lo adjunta.
- **#86:** con `local_dir` y algún diario presente, el botón abre el visor con Markdown
  renderizado; sin ellos, el botón no aparece.
- **#87:** un clic abre una consola externa en `local_dir` con la CLI elegida, el MCP del
  tablero registrado y el INTRO cargado (como argumento en `.exe`, por portapapeles con aviso
  en `.cmd`); con varias CLIs pide elegir; un fallo del update no bloquea; con el MCP del
  tablero desactivado, no lanza y abre la configuración.
- **#88:** con la lectura activada y una sesión de Claude Code reciente, el semáforo muestra el
  % restante de 5 h y 7 d y la hora de reinicio; los datos caducados salen en gris; activar y
  desactivar conserva el resto de `~/.claude/settings.json` (y la status line previa); las
  CLIs sin fuente muestran "Sin datos".
- **#101:** tras abrir la app (o reiniciarse al actualizarse) el MCP responde sin tocar el diálogo,
  siempre que algún tablero lo tenga activado.
- **#102:** cerrar el detalle de una tarjeta tras una recarga del tablero no lanza excepciones.
- **#74:** A: tools, instrucciones y resumen ejecutivo en inglés. B: informe de ahorro y latencia
  con decisión go/no-go en la tarjeta. C (si go): con el toggle desactivado, salida idéntica
  byte a byte; activado, nunca añade latencia (fallo de caché → original).
- **#81:** ADR aprobado por el usuario y sub-tarjetas 81.1–81.5 creadas en el Backlog con su
  DoD; nada de código de la PWA hasta la aprobación.
