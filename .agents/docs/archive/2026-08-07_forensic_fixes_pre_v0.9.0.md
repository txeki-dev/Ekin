# TECHNICAL DESIGN DOCUMENT

## 1. Overview

A forensic bug-hunt pass across the whole codebase, run ahead of cutting v0.9.0, using two
independent audit agents (data/logic layer, UI layer) whose findings were each individually
verified against the actual current code before being accepted here. Nine fixes, ranked by
severity: two critical (an unbounded resource leak in the most common user interaction, and an
uncaught-exception crash risk on Ctrl+Z), four correctness bugs (one stale help-text, one stale
board card, one silent data-loss on column/board copy, one atomicity gap), and three low-risk
efficiency/cleanup items. Everything here was chosen for being real, verified, and low-risk to fix
right now — a matching "explicitly out of scope" list (systemic double-commit pattern,
`get_task()`/`get_tasks()` shape inconsistency, an unreachable `backups` edge case, minor link-order
loss on restore, calendar refresh-while-hidden) is deliberately **not** touched in this wave; note
these in `backlog.md` as tech debt during the Backlog phase, don't act on them now.

Once all 9 are implemented and QA passes, this wave concludes with cutting the release: bump
`version.py` to `0.9.0` and move `CHANGELOG.md`'s `[Unreleased]` section under a new
`## [0.9.0] - <today's date>` heading, exactly like the 0.8.0 cut — that step belongs to the
Release Engineer at the end of the pipeline, not the Coder.

## 2. Implementation Tasks

### Fix 1 (CRITICAL) — `TaskDetailDialog` never gets destroyed: leaked dialog + a `QTimer` that runs forever

- [x] `detail_dialog/task_detail_dialog.py` — `__init__` (~L39-42, right after
  `self._timer_refresh_timer.start(30_000)`): add
  ```python
  # El diálogo se parenta a MainWindow/BoardViewWidget (viven toda la sesión), así que
  # nada lo destruye por sí solo cuando se cierra -- sin esto, cada tarea abierta deja un
  # TaskDetailDialog zombi con su _timer_refresh_timer disparando para siempre.
  self.finished.connect(self.deleteLater)
  ```
  `QDialog.finished` fires on both `accept()` and `reject()` (including the default Esc/close-button
  path), and `deleteLater()` doesn't destroy the object until the next event-loop turn, so callers
  reading `dialog.modified`/`dialog.task_deleted`/`dialog.deleted_snapshot` immediately after
  `.exec()` returns (`main.py`'s `_open_task_detail`, `board_view.py`'s same-named method) remain
  completely safe.

### Fix 2 (CRITICAL) — Ctrl+Z can raise an uncaught `sqlite3.IntegrityError` and destroy the undo action itself

- [x] `database/snapshots.py` — imports (~L1-6): add `from .tags import get_tag_value` to the
  existing import block.

- [x] `database/snapshots.py` — `restore_task` (~L34-41): right after the existing
  `linked_board_id` guard, add the equivalent guard for tags, computed *before* opening
  `get_connection` (same pattern as `linked_board_id`):
  ```python
  def restore_task(snap, column_id=None, db_path=None):
      """Recrea una tarea a partir de un snapshot. Devuelve el nuevo id."""
      column_id = column_id if column_id is not None else snap["column_id"]
      # Si el tablero enlazado ya no existe (se borró mientras tanto), no lo restauramos:
      # violaría la clave foránea en vez de simplemente perder el vínculo.
      linked_board_id = snap.get("linked_board_id")
      if linked_board_id is not None and get_board(linked_board_id, db_path) is None:
          linked_board_id = None
      # Mismo razonamiento para las etiquetas: si una tag_value del catálogo se borró
      # mientras tanto, insertar su id violaría la FK de task_tags (ON DELETE CASCADE,
      # PRAGMA foreign_keys = ON) y abortaría la restauración entera con una excepción
      # sin capturar que además destruye la propia acción de deshacer (ver UndoManager.undo()).
      tag_value_ids = [
          tvid for tvid in snap.get("tag_value_ids", [])
          if get_tag_value(tvid, db_path) is not None
      ]
      with get_connection(db_path) as conn:
  ```
  and change the existing tag-restoration loop (currently
  `for tvid in snap.get("tag_value_ids", []):`) to iterate the new filtered `tag_value_ids` list
  instead:
  ```python
  for tvid in tag_value_ids:
      cursor.execute(
          "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
          (new_id, tvid))
  ```

### Fix 3 — the Shortcuts dialog describes a `Ctrl+N` behavior that no longer exists

- [x] `strings.py` — key `"shortcuts.item_new_task"`: replace its value with
  ```python
  "shortcuts.item_new_task": (
      "Ctrl+N — Nueva tarea en la última columna con la que interactuaste (si no hay "
      "ninguna, la primera del tablero activo)"
  ),
  ```

### Fix 4 — editing a task from the Calendar leaves the board-view card stale

- [x] `main.py` — `on_calendar_task` (~L304-309): replace with (**note for Tester**: the TDD's
  literal snippet below omits a pre-existing `self.sync_ics()` call that the Architect's read of
  the file missed — the actual current code already had `self.sync_ics()` as the third line of the
  `if changed:` block. The Coder kept that pre-existing call rather than deleting it (deleting it
  would have been a real regression: it's the *only* thing keeping the `.ics` feed in sync when the
  edited task's board differs from the sidebar's active one, since in that case the new conditional
  `load_board()` call below never runs). The new `load_board()` call was added with `notify=False`
  precisely because `sync_ics()`/`refresh_notifications()`/`calendar_view.refresh()` are already
  called explicitly right above it — using the default `notify=True` would have fired all three
  again redundantly via the `data_changed` signal chain. See the actual diff, not this snippet, for
  ground truth.)
  ```python
  def on_calendar_task(self, task_id, board_id):
      """Desde el calendario: abrir el detalle y quedarnos en el calendario."""
      changed = self._open_task_detail(task_id)
      if changed:
          self.calendar_view.refresh()
          self.sidebar.refresh_notifications()
          # Solo recargamos board_view si la tarea editada pertenece al tablero que
          # tiene activo la sidebar -- si no, board_view.load_board() desincronizaría
          # qué tablero muestra cargado respecto al que la sidebar resalta.
          if board_id == self.sidebar.active_board_id:
              self.board_view.load_board(board_id)
  ```
  Do not add an explicit `sync_ics()` call — `load_board()`'s default `notify=True` already emits
  `data_changed`, already connected to `self.sync_ics` in `init_ui()`, exactly like the sibling
  `on_notification_task` relies on the same indirect path.

### Fix 5 — copying a column/board silently drops due-time, recurrence, linked board, timer, and links

- [x] `database/board_ops.py` — add a new private helper, placed immediately before
  `copy_column_to_board`:
  ```python
  def _duplicate_task_into_column(cursor, task_row, new_column_id):
      """Duplica una fila de `tasks` (con sus etiquetas, diario y enlaces) en
      new_column_id. Usado tanto por copy_column_to_board como por copy_board para no
      duplicar esta lógica dos veces. `task_row` debe incluir title, description,
      tag_text, tag_color, position, due_date, due_time, recurrence, linked_board_id,
      timer_started_at, e id (de la tarea origen)."""
      cursor.execute(
          """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position,
                                 due_date, due_time, recurrence, linked_board_id, timer_started_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
          (new_column_id, task_row["title"], task_row["description"], task_row["tag_text"],
           task_row["tag_color"], task_row["position"], task_row["due_date"], task_row["due_time"],
           task_row["recurrence"], task_row["linked_board_id"], task_row["timer_started_at"])
      )
      new_task_id = cursor.lastrowid
      old_task_id = task_row["id"]

      cursor.execute(
          "SELECT tag_value_id FROM task_tags WHERE task_id = ? AND tag_value_id IS NOT NULL",
          (old_task_id,)
      )
      for row in cursor.fetchall():
          cursor.execute(
              "INSERT INTO task_tags (task_id, tag_value_id, text, color) VALUES (?, ?, '', '#6b7280')",
              (new_task_id, row["tag_value_id"])
          )

      cursor.execute(
          "SELECT content, created_at FROM task_logs WHERE task_id = ? ORDER BY id ASC",
          (old_task_id,)
      )
      for row in cursor.fetchall():
          cursor.execute(
              "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
              (new_task_id, row["content"], row["created_at"])
          )

      cursor.execute(
          "SELECT url, label, position FROM task_links WHERE task_id = ? ORDER BY position ASC",
          (old_task_id,)
      )
      for row in cursor.fetchall():
          cursor.execute(
              "INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
              (new_task_id, row["url"], row["label"], row["position"])
          )

      return new_task_id
  ```

- [x] `database/board_ops.py` — `copy_column_to_board` (~L47-51, the task `SELECT`): replace with
  ```python
  cursor.execute(
      """SELECT id, title, description, tag_text, tag_color, position, due_date,
                due_time, recurrence, linked_board_id, timer_started_at
         FROM tasks WHERE column_id = ? ORDER BY position ASC""",
      (column_id,)
  )
  ```
  and replace the entire `for task in tasks:` block that follows (from the task-INSERT through the
  end of the logs-duplication loop, ~L56-90) with:
  ```python
  for task in tasks:
      _duplicate_task_into_column(cursor, task, new_column_id)
  ```

- [x] `database/board_ops.py` — `copy_board` (~L119-123, the task `SELECT` inside the column loop):
  apply the identical `SELECT` column-list change, and replace its `for task in tasks:` block
  (~L126-160) with:
  ```python
  for task in tasks:
      _duplicate_task_into_column(cursor, task, new_col_id)
  ```
  (`new_col_id` — matches this function's existing variable name for the newly-created column, as
  opposed to `copy_column_to_board`'s `new_column_id`.)

### Fix 6 — `create_log()` breaks atomicity with a mid-function commit

- [x] `database/logs.py` — `create_log` (~L7-22): remove the first `conn.commit()` call (the one
  immediately after the `INSERT INTO task_logs`). Result:
  ```python
  def create_log(task_id, content, db_path=None):
      with get_connection(db_path) as conn:
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO task_logs (task_id, content) VALUES (?, ?)",
              (task_id, content)
          )

          # También actualizamos la fecha de modificación de la tarea madre
          conn.execute(
              "UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
              (task_id,)
          )
          conn.commit()
          return cursor.lastrowid
  ```

### Fix 7 — `timer_alert_hours` re-read from the DB once per column on every board load

- [x] `board_view.py` — `load_board` (~L449-451, right before `for col_data in columns:`): add
  ```python
  timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))
  ```

- [x] `board_view.py` — `_build_column_widget` (~L332): change the signature to
  ```python
  def _build_column_widget(self, col_data, tasks, board_info, timer_alert_hours):
  ```
  and remove the line `timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))`
  from inside the `if not col_data.get("collapsed"):` block — the value now arrives as a parameter,
  used exactly as before (`card.set_timer_alert_hours(timer_alert_hours)`).

- [x] `board_view.py` — `load_board`'s call site (~L457): change
  `col_widget = self._build_column_widget(col_data, tasks, board_info)` to
  `col_widget = self._build_column_widget(col_data, tasks, board_info, timer_alert_hours)`.

- [x] `board_view.py` — `_rebuild_single_column` (~L386-390, right before
  `new_widget = self._build_column_widget(col_data, tasks, board_info)`): add
  `timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))` and
  change that call site to
  `new_widget = self._build_column_widget(col_data, tasks, board_info, timer_alert_hours)`.

### Fix 8 — dead `app.setStyleSheet(styles.QSS)` in `main()`

- [x] `main.py` — `main()` (~L506-507): delete both the comment
  `# Aplicar hoja de estilos QSS global` and the line `app.setStyleSheet(styles.QSS)`.
  `MainWindow.__init__` always immediately re-applies the real saved theme via
  `self.apply_theme(database.get_setting("theme", "dark"), reload=False)` before any widget is
  shown, so this line has no observable effect. Leave `styles.QSS` itself defined in `styles.py` —
  removing the module-level constant is out of scope for this fix (check first whether anything
  else references it before ever considering that separately; this task is just about the dead call
  site in `main()`).

### Fix 9 — N+1 query pattern in export: one log fetch per task instead of one batched query

- [x] `database/logs.py` — add a new function, placed right after `get_logs`:
  ```python
  def get_logs_bulk(task_ids, db_path=None):
      """{task_id: [entradas de diario]} para varias tareas en UNA sola consulta (evita
      el patrón N+1 al exportar). Cada entrada tiene la misma forma que en get_logs."""
      result = {tid: [] for tid in task_ids}
      if not task_ids:
          return result
      placeholders = ",".join("?" * len(task_ids))
      with get_connection(db_path) as conn:
          cursor = conn.cursor()
          cursor.execute(
              f"SELECT id, task_id, content, created_at FROM task_logs "
              f"WHERE task_id IN ({placeholders}) ORDER BY task_id ASC, id ASC",
              list(task_ids)
          )
          for row in cursor.fetchall():
              data = dict(row)
              task_id = data.pop("task_id")
              result.setdefault(task_id, []).append(data)
      return result
  ```
  and add `"get_logs_bulk"` to `__all__` in the same file (already re-exported automatically via
  `from .logs import *` in `database/__init__.py`, no change needed there).

- [x] `exporter.py` — `_gather` (the column loop, currently
  `for task in database.get_tasks(col["id"], db_path):`): capture the tasks list, fetch logs in
  bulk once per column, and look them up per task instead of querying per task:
  ```python
  for col in database.get_columns(board["id"], db_path):
      c = {"id": col["id"], "name": col["name"], "color": col["color"], "tasks": []}
      tasks = database.get_tasks(col["id"], db_path)
      logs_by_task = database.get_logs_bulk([t["id"] for t in tasks], db_path)
      for task in tasks:
          c["tasks"].append({
              "id": task["id"], "title": task["title"],
              "description": _plain(task.get("description")),
              "due_date": task.get("due_date"), "due_time": task.get("due_time"),
              "recurrence": task.get("recurrence", "none"),
              "tags": [{"category": t["category"], "value": t["value"]} for t in task.get("tags", [])],
              "logs": [
                  {"created_at": lg["created_at"], "content": _plain(lg["content"])}
                  for lg in logs_by_task.get(task["id"], [])
              ],
          })
      b["columns"].append(c)
  ```

## 3. Acceptance Criteria

- **Fix 1:** opening a `TaskDetailDialog` via the real app (`main.py`/`board_view.py` call sites,
  i.e. constructed *with* a parent) and closing it (Guardar Cambios, Cerrar, or Esc) results in the
  dialog and its `_timer_refresh_timer` being destroyed — verifiable via a `shiboken6`/weakref-style
  liveness check, or at minimum by confirming `self.finished` is connected to `self.deleteLater`
  and that a `QTimer.singleShot` pump after `.close()`/`.accept()` lets `deleteLater` run and the
  Python-side object become invalid to touch. Existing headless tests that construct the dialog
  *without* a parent (`tests/test_widgets_headless.py`) must keep passing unmodified (parentless
  construction already worked fine before this fix; this fix doesn't change that path).
- **Fix 2 — the critical regression test:** construct a snapshot of a task carrying a
  `tag_value_id` that has since been deleted from the tag catalog, then call `restore_task`.
  Empirically confirm (same method already used earlier this session for the hover-expand crash
  fix: temporarily `git stash` just the fix in `database/snapshots.py`, keep the new test, run it,
  confirm it fails with `sqlite3.IntegrityError`, then `git stash pop` and confirm it passes) that
  the fix resolves it. After the fix: `restore_task` must succeed, the restored task must exist,
  and it must simply have fewer tags (the deleted one dropped) rather than raising. A second test:
  restoring a task whose tags *are* all still valid must keep every one of them (no
  over-filtering).
- **Fix 3:** `t("shortcuts.item_new_task")` reflects the last-active-column behavior, not "primera
  columna".
- **Fix 4:** editing a task through the calendar while its board is the sidebar's active board
  updates the corresponding card the next time the board view is shown (verified by calling
  `on_calendar_task` directly and checking `board_view.board_id`/a reloaded card's data — or, since
  a real click can't be simulated headless, by monkeypatching `_open_task_detail` to return `True`
  and asserting `board_view.load_board` was called with the right `board_id` only when it matches
  the active board, and *not* called when it doesn't).
- **Fix 5:** copying a column or a whole board preserves `due_time`, `recurrence`,
  `linked_board_id` (unless the linked board is the one being copied *out of* in a way that would
  dangle — existing `copy_column_to_board`/`copy_board` semantics for cross-board FK validity
  should be preserved; if unsure, mirror whatever `restore_task` already does for a stale
  `linked_board_id`), `timer_started_at`, and every `task_links` row (url, label, and relative
  `position` all preserved) — for both `copy_column_to_board` and `copy_board`. Existing tests
  `test_copy_column_to_board_duplicates_tasks_tags_and_logs` and
  `test_copy_board_duplicates_full_hierarchy` must keep passing; extend them (or add siblings) to
  assert on the previously-dropped fields and on `task_links`.
- **Fix 6:** `create_log` still returns the same `lastrowid` and still updates `updated_at` — a
  test should confirm both effects happen together in a single call, and (if practical) that only
  one `conn.commit()` remains in the function body (a `grep`-style assertion via reading the
  source, or simply code review, is acceptable if a runtime test for "only committed once" isn't
  straightforward).
- **Fix 7:** `_build_column_widget` and `_rebuild_single_column` no longer call
  `database.get_setting("timer_alert_hours", ...)` internally — the value arrives as a parameter.
  `load_board` calls `database.get_setting` exactly once per invocation regardless of column count
  (a test can monkeypatch/spy `database.get_setting` and assert call count, or simply verify the
  refactored signature is used correctly end-to-end — cards still get the right threshold applied,
  matching the existing `tests/test_timer_board_view.py` assertions, which must keep passing
  unmodified).
- **Fix 8:** `app.setStyleSheet(styles.QSS)` no longer appears in `main.py`; the app still launches
  with the correct theme (already covered by existing smoke-test conventions — no new test
  strictly required for a dead-code removal, but the full-app smoke check at the end of QA must
  still show the app launching and rendering normally).
- **Fix 9:** `get_logs_bulk` returns the same shape/content as calling `get_logs` per task
  (including for an empty `task_ids` list, and for task ids with zero log entries returning `[]`
  rather than being omitted from the result dict). `exporter.boards_to_json`/`_gather`'s exported
  log content is byte-for-byte identical before and after this change for the same DB state —
  existing exporter tests must keep passing unmodified.
- **General:** full existing test suite (145 tests before this wave) + ruff stay green. A full-app
  smoke check (per this project's convention) against a real `MainWindow` + scratch DB: open and
  close several tasks and confirm no error; trigger the Ctrl+Z scenario from Fix 2 end-to-end
  (delete a tagged task, delete the tag from the catalog, undo) and confirm no crash and the task
  reappears; copy a column containing a task with a due-time/recurrence/link and confirm the copy
  keeps them; edit a task from the calendar and confirm the board card refreshes.
- **Final step (Release Engineer, after QA passes, not part of the Coder's/Tester's checklist):**
  bump `version.py` to `0.9.0`, move `CHANGELOG.md`'s `[Unreleased]` section under a new
  `## [0.9.0] - <today>` heading leaving a fresh empty `[Unreleased]`, re-run the full suite one
  more time after the bump, then commit and push to `main` (the push auto-tags `v0.9.0` per
  `.github/workflows/release.yml`, same as every prior version cut).

## QA Report

**Code review:** every `[x]` task in §2 traced against the actual current contents of
`detail_dialog/task_detail_dialog.py`, `database/snapshots.py`, `strings.py`, `main.py`,
`database/board_ops.py`, `database/logs.py`, `exporter.py`, `board_view.py` — all 9 fixes match
this TDD's intent. One deliberate deviation from the Architect's literal Fix 4 snippet, called out
here explicitly: the TDD's snippet for `on_calendar_task` assumed no pre-existing `sync_ics()` call
and relied on `load_board()`'s default `notify=True` to trigger it indirectly via the `data_changed`
signal. Reading the *current* `main.py` (the Architect's file-read had cut off right before it)
showed `on_calendar_task` already calls `self.sync_ics()` directly, one line before where the new
`board_view.load_board()` call would go. Applying the TDD's snippet verbatim would have kept that
still working (redundant `sync_ics()`, harmless) — but adding a second, indirect trigger of the same
sync via `data_changed` on top of the direct call is pure duplication for no benefit, so the actual
implementation calls `self.sync_ics()` explicitly (preserving the pre-existing line) and passes
`notify=False` to the new `load_board()` call to suppress the redundant signal path. Net effect is
identical to the TDD's intent (calendar edits sync `.ics` and refresh the board card when it's the
active board) with no duplicate work. Verified correct by both the new `test_main_window.py` tests
and the smoke script.

**Empirical regression verification (git stash method, as used earlier this session for the
hover-expand crash):**
- Fix 1 (`test_task_detail_dialog_is_destroyed_after_closing_when_parented`): stashed the one-line
  `self.finished.connect(self.deleteLater)` addition in `task_detail_dialog.py`, re-ran the test —
  failed with `Failed: DID NOT RAISE <class 'RuntimeError'>` (the dialog was still alive after
  `reject()` + `sendPostedEvents`). Popped the stash — test passes.
- Fix 2 (`test_restore_task_drops_deleted_tag_instead_of_raising`): stashed the `tag_value_ids`
  filter in `database/snapshots.py`, re-ran — failed with
  `sqlite3.IntegrityError: FOREIGN KEY constraint failed`, exactly the crash path described in the
  TDD. Popped the stash — test passes, and the sibling
  `test_restore_task_keeps_tags_that_still_exist` confirms surviving tags are *not* dropped
  needlessly.
- Fix 4 (`test_on_calendar_task_reloads_board_view_when_editing_the_active_board`): stashed the
  rewritten `on_calendar_task` in `main.py`, re-ran — failed with
  `AssertionError: assert [] == [((1,), {'notify': False})]` (old code never called
  `board_view.load_board` at all). Popped the stash — test passes; the two negative-case siblings
  (different board, no-op dialog) also pass and were checked to still pass against the *old* code
  too (they assert `calls == []`, which old code also satisfies — confirming they test the guard
  condition, not just "anything changed").

**Test-writing detours, both resolved and documented so they aren't repeated:**
- First attempt at a Fix 6 regression test used
  `monkeypatch.setattr(sqlite3.Connection, "commit", counting_commit)`, which raised
  `TypeError: cannot set 'commit' attribute of immutable type 'sqlite3.Connection'` — `Connection`
  is an immutable C type, not patchable at runtime. Replaced with the TDD's pre-approved fallback:
  `test_create_log_has_a_single_commit_call` asserts
  `inspect.getsource(database.create_log).count(".commit()") == 1`, which does correctly fail
  against the old two-commit body and pass against the fix.
- First attempt at the Fix 1 test called `.close()` on a dialog that was never `.show()`n; `finished`
  never fired (confirmed via an isolated diagnostic script printing `finished emitted: []`).
  Switched to calling `.reject()` directly, matching how the dialog's real Cerrar/Esc path actually
  terminates it.
- Running the full suite after adding the new tests crashed with
  `Windows fatal exception: access violation`, but only when run as part of the *full* suite, not in
  isolation. Root-caused to `qapp.sendPostedEvents(None, QEvent.Type.DeferredDelete)` in the two new
  Fix-1 tests: `receiver=None` processes every pending `DeferredDelete` across the whole
  session-scoped `QApplication`, including orphaned `MainWindow` instances left behind by the new
  `tests/test_main_window.py` (which never explicitly closes the windows it constructs) — a native
  crash resulted from touching those half-alive objects from an unrelated test. Fixed by scoping
  both calls to `receiver=dlg` (the specific dialog under test) instead of `None`. Full suite re-run
  clean afterward, 5 consecutive times with no flake.

**Tests added (14 new, 159 total):**
- `tests/test_database.py` (+6): Fix 2's two regression tests (drop-deleted-tag,
  keep-existing-tags); Fix 5's two copy-preservation tests (`copy_column_to_board`, `copy_board`,
  covering `due_time`/`recurrence`/`linked_board_id`/`timer_started_at`/`task_links`); Fix 6's
  source-inspection commit-count test; Fix 9's two `get_logs_bulk` tests (matches per-task
  `get_logs` output including tasks with zero logs, empty-input returns `{}` not an error).
- `tests/test_widgets_headless.py` (+3): Fix 1's destruction-after-close test (parented case) and
  its sibling confirming the unparented case still behaves as before (already GC'd, no regression
  there); Fix 3's shortcuts-string content test.
- `tests/test_main_window.py` (+3, new file): Fix 4's three `on_calendar_task` scenarios (reloads
  active board, skips a different board, skips a no-op dialog result).
- `tests/test_timer_board_view.py` (+1): Fix 7's call-count test confirming `get_setting` is read
  exactly once per `load_board()` regardless of column count (4 columns, 1 call).
- Fix 8 (dead-code removal) has no dedicated test per the TDD's own note — covered by the full-app
  smoke check confirming the app still launches and themes correctly.

**Full-app smoke script** (`smoke_forensic_fixes.py`, real `MainWindow` against a scratch DB, all 4
non-trivial-to-unit-test scenarios chained end-to-end):
```
OK: 10 dialogos abiertos y cerrados, ninguno queda vivo (sin fuga).
OK: Ctrl+Z tras borrar la etiqueta de una tarea borrada no revienta la app.
OK: copiar una columna conserva hora, recurrencia y enlaces.
OK: editar una tarea desde el Calendario refresca la tarjeta del tablero activo.
SMOKE OK: las 4 correcciones criticas/importantes funcionan de punta a punta en la app real.
```

**Suite results:** `pytest -q` (offscreen, whole suite): **159 passed** (was 145; +14 from this
wave). `ruff check .`: **all checks passed**.

**Acceptance criteria (§3) — verified:**
- ✅ Fix 1: dialog is destroyed after both `accept()`/`reject()` paths; `dialog.modified`/
  `task_deleted`/`deleted_snapshot` remain readable immediately after `.exec()` returns (unchanged
  call sites in `main.py`/`board_view.py`, no regression — full suite + smoke confirm).
- ✅ Fix 2: stale `tag_value_id`s are silently dropped instead of raising; surviving tags are kept;
  empirically confirmed to reproduce the exact `IntegrityError` against pre-fix code.
- ✅ Fix 3: shortcuts help text now describes "last active column" behavior, matching
  `board_view.py`'s actual `quick_add_task` logic.
- ✅ Fix 4: board card refreshes when the edited task belongs to the sidebar's active board, and
  does *not* reload when it belongs to a different board (both directions tested); `sync_ics()`
  still fires exactly once (documented deviation above).
- ✅ Fix 5: `due_time`, `recurrence`, `linked_board_id`, `timer_started_at`, and every `task_links`
  row survive both `copy_column_to_board` and `copy_board`; pre-existing
  `test_copy_column_to_board_duplicates_tasks_tags_and_logs` /
  `test_copy_board_duplicates_full_hierarchy` still pass unmodified; shared `_duplicate_task_into_column`
  helper eliminates the ~35-line duplication called out in the TDD.
- ✅ Fix 6: `create_log` still returns `lastrowid` and updates `updated_at`; source-inspection
  confirms exactly one `.commit()` remains.
- ✅ Fix 7: `_build_column_widget`/`_rebuild_single_column` take `timer_alert_hours` as a parameter;
  `load_board` reads the setting exactly once regardless of column count (tested with 4 columns);
  existing `test_timer_board_view.py` assertions on threshold behavior pass unmodified.
- ✅ Fix 8: `app.setStyleSheet(styles.QSS)` removed; app still launches and themes correctly
  (confirmed by smoke script + full suite, which constructs real `MainWindow`/`BoardViewWidget`
  instances throughout).
- ✅ Fix 9: `get_logs_bulk` matches `get_logs` per task byte-for-byte, including empty-list and
  zero-log-entry edge cases; `exporter.py`'s `_gather()` uses it instead of the N+1 pattern;
  existing exporter tests pass unmodified.
- ✅ General: full suite green (159/159, was 145), ruff clean, full-app smoke covers all 4 described
  scenarios end-to-end.

**STATUS: QA PASSED**

## Post-QA Addendum (Release Engineer, discovered during final pre-push suite run)

**10th finding — CRITICAL, test-harness-only: the entire test suite crashed with
`STATUS_HEAP_CORRUPTION` (`0xC0000374`) at interpreter shutdown, after every individual test had
already reported `PASSED`.** This was invisible in every prior "suite is green" claim this
session (including this wave's own QA Report above) because the crash happens *after* pytest's
final summary line would normally print, and nothing in this session's workflow had checked the
actual process exit code — piping through tools like `tail` or reading truncated output made
100%-progress dots look indistinguishable from a clean pass. Verified this was **pre-existing, not
a regression from this wave**: `git stash`-ing every one of this wave's changes (all 9 fixes, the
5 new/modified test files, version.py) and running the *pristine* 145-test suite from before this
wave reproduced the identical crash, consistently, 100% of 3 consecutive runs.

**Root cause:** `tests/conftest.py`'s session-scoped `qapp` fixture created the `QApplication` and
`yield`ed it with no teardown at all. Across an entire test session, hundreds of `QWidget`s (many
deliberately unparented, e.g. to test Python-GC-driven cleanup) accumulate; with no explicit
cleanup, their destruction gets deferred to CPython's own interpreter-shutdown sequence, where the
order between Python's garbage collector tearing down lingering `QObject` wrappers and Shiboken/Qt
tearing down the `QApplication` singleton itself is undefined. Native Qt widget destructors running
after (or interleaved with) `QApplication` teardown is a known class of PySide6/Shiboken heap
corruption on Windows.

**Fix:** `tests/conftest.py` — added an explicit teardown after `yield app`:
```python
app.closeAllWindows()
app.processEvents()
gc.collect()
app.processEvents()
```
This forces every remaining top-level widget to close and every now-unreferenced `QObject` to be
collected *while the `QApplication` is still fully alive*, before interpreter shutdown ever begins.

**Verification:** confirmed via explicit exit-code checks (not just reading dot-progress output),
using PowerShell's `$LASTEXITCODE` since MSYS/bash's `$?` translation of a Windows native crash
exit code is unreliable:
- Pristine pre-wave code + old conftest.py: `EXITCODE=-1073740940` (`0xC0000374`), 3/3 runs.
- Pristine pre-wave code + fixed conftest.py: `145 passed in 6.02s`, `EXITCODE=0`.
- Full forensic-wave code (all 9 fixes + 14 new tests) + fixed conftest.py:
  `159 passed in 10.24s`, `EXITCODE=0`, confirmed clean across 4 consecutive runs (1 initial + 3
  repeats).
- `ruff check .`: all checks passed.

**Scope note:** this is a test-harness-only defect — it never affected the shipped application
(the real `main.py` entry point calls `sys.exit(app.exec())` and lets the OS reclaim resources on
normal process exit; it never relies on Python's GC to destroy Qt widgets in a specific order
before an already-running event loop's `QApplication` is torn down the way a session-scoped pytest
fixture does). No `CHANGELOG.md` entry needed since it's invisible to end users; recorded here and
in `context.md` for engineering record, since it silently invalidated the exit-code guarantee of
every "suite is green" claim made this session prior to this fix.

**STATUS: QA PASSED (post-addendum, re-confirmed)**
