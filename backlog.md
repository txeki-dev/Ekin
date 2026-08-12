# 🗂️ Ekin Kanban — Backlog

Living planning doc: forensic findings (tech debt) + ideas for future releases.
Ordered roughly by value/effort. Checkboxes track what's done.

---

## ✅ Fixed in the forensic pass (2026-08-10, v0.9.1)

Same two-independent-agent format as the 2026-08-07 pass (data/logic layer, UI layer + a dedicated
CI-flakiness investigation), every finding re-verified against actual source before acceptance.
Triggered by CI intermittently failing since the 2026-08-07 task-timer commit — pinpointed via the
GitHub Actions check-runs API (no `gh` CLI / log access available) to a different single
Python-version job failing on different runs, which pointed at a race/leak rather than a
deterministic cross-platform bug.

- [x] **CI crash root cause found and fixed: a stray, unparented `QTimer.singleShot` could fire
  against an already-destroyed widget.** `detail_dialog/task_detail_dialog.py`'s
  `scroll_to_bottom()` (called on every dialog open and every diary edit) scheduled a bare
  `QTimer.singleShot(50, lambda: scrollbar.setValue(...))` holding a closure over a child
  scrollbar. If the dialog was destroyed before the 50ms elapsed — which never happens during
  normal use, but routinely happens across a 166-test session where the event loop is only pumped
  once, at the very end — the timer fires later against a deleted C++ object. Reproduced directly
  (including the actual `STATUS_HEAP_CORRUPTION`/`0xC0000374` crash) against a realistic population
  of leftover dialogs. Fixed by parenting the timer to the dialog (`QTimer(self)`), so Qt cancels
  it automatically when the dialog is destroyed instead of leaving it dangling.
- [x] **Contributing hazard: `tests/test_main_window.py` left 3 `MainWindow()` instances alive with
  two more real, unparented timers pending** — one of which (`check_for_updates`) runs live `git
  fetch`/`git status` subprocess calls. Fixed by monkeypatching both to no-ops before construction
  and explicitly closing/deleting each window after its test.
- [x] **`restore_task()` (Ctrl+Z) loses `task_links` ordering** — was hardcoding every restored
  link's `position` to `0`; now the original position is captured in the snapshot and restored.
  Closes the item of the same name below. New regression test:
  `test_snapshot_and_restore_task_preserves_link_order`.
- [x] **Systemic double-commit pattern, audited and ruled out** — the dedicated audit this backlog
  asked for (below) happened as a side effect of removing ~40 redundant trailing `conn.commit()`
  calls across the whole `database/` package: every one of them was individually verified to be
  the *last* statement before its function returns (the connection context manager already commits
  on clean exit), never a *premature* mid-transaction commit like the original `create_log` bug.
  No other atomicity-breaking commits found.
- [x] **Dead code**: unused `styles.QSS` module-level constant (nothing has read it since
  `set_theme()` took over in the previous forensic pass) and an unreachable `sys.exit(0)` after
  `os.execv()` in `main.check_for_updates`.
- [x] **CI still red after the fix above (py3.10 only) — the broader "no shared cleanup" pattern
  really was load-bearing, not just theoretical.** The first push (timer fix + `MainWindow` cleanup)
  flipped CI from "all 3 Python versions fail" to "2 of 3 pass," confirming the mechanism but
  exposing that it wasn't the *only* source: dozens of other tests construct a
  `BoardViewWidget`/`TaskDetailDialog` and never close it, so hundreds of orphaned widgets still
  converged on one final teardown burst. Fixed with a `tests/conftest.py` autouse fixture that
  closes every top-level widget after *each* test instead of letting them all accumulate to
  session end — the fix originally logged below as "deferred, provably safe today" turned out not
  to be safe enough; it's done now, verified by re-polling GitHub Actions after the follow-up push
  (all 3 Python versions + lint + release green).

**New tech debt found this pass, deferred on purpose (see "Code quality & tech debt" below):**
`restore_column`/`restore_board` aren't atomic across their children (each nested
`restore_task`/`restore_column` call opens its own connection/transaction) — low practical impact,
not acted on.

---

## ✅ Fixed in the forensic pass (2026-08-07, pre-v0.9.0)

Two independent audit agents (data/logic layer, UI layer), every finding individually re-verified
against actual source before acceptance. Full writeup: `.agents/docs/archive/2026-08-07_forensic_fixes_pre_v0.9.0.md`.

- [x] **Critical: `TaskDetailDialog` leaked forever** — every task opened from the board or
  calendar left the dialog alive in the background with its 30s refresh `QTimer` still running,
  because nothing destroyed it after closing. Fixed with `self.finished.connect(self.deleteLater)`.
- [x] **Critical: `Ctrl+Z` could crash the app** — restoring a deleted task's tags during undo
  assumed every tag it had still existed in the catalog; a tag deleted in between raised an
  uncaught `sqlite3.IntegrityError` that escaped a Qt slot and terminated the process. Fixed by
  filtering stale `tag_value_id`s before restoring, mirroring the existing `linked_board_id` guard.
- [x] **Stale shortcuts help text** — `Ctrl+/`'s dialog still described `Ctrl+N`'s pre-"last active
  column" behavior.
- [x] **Calendar edits left the board card stale** — `on_calendar_task` never reloaded `board_view`
  (only its sibling `on_notification_task` did); fixed, scoped to only reload when the edited
  task's board matches the sidebar's active board.
- [x] **Copying a column/board silently dropped due time, recurrence, linked board, timer, and
  links** — `copy_column_to_board`/`copy_board` only ever carried title/description/tags/logs.
  Fixed via a shared `_duplicate_task_into_column` helper (also removed ~35 lines of duplicated
  logic between the two callers).
- [x] **`create_log` broke transaction atomicity** with a premature `commit()` between the diary
  insert and the parent task's `updated_at` update.
- [x] **Efficiency: `timer_alert_hours` re-read once per column** on every `load_board()` — now
  read once and passed down.
- [x] **Efficiency: N+1 diary export** — added `database.get_logs_bulk()`, wired into
  `exporter._gather()`.
- [x] **Dead code**: `app.setStyleSheet(styles.QSS)` in `main()`, unreachable since
  `apply_theme()` always overwrites it before any widget renders.
- [x] **Test-harness only: `pytest` crashed with `STATUS_HEAP_CORRUPTION` at interpreter shutdown**,
  after every test already reported `PASSED` — invisible until process exit codes were checked
  directly. Confirmed pre-existing (not a regression from this wave) via `git stash` against
  pristine pre-wave code. Root cause: the session-scoped `qapp` fixture never tore down
  accumulated Qt widgets before `QApplication` teardown, racing against CPython's own interpreter
  shutdown. Fixed with an explicit `qapp` fixture teardown in `tests/conftest.py`. Never affected
  the shipped app (which exits via `sys.exit(app.exec())`, not a pytest fixture).

**Explicitly deferred (documented, not acted on this wave — see "Code quality & tech debt" below):**
systemic double-commit pattern beyond `create_log`, `get_task()`/`get_tasks()` shape inconsistency,
an unreachable `backups._prune_backups(keep=0)` edge case, minor task-link ordering loss on
`restore_task()` (Ctrl+Z), `CalendarViewWidget.refresh()` running while hidden.

---

## ✅ Fixed in the forensic pass (2026-07-16)

- [x] **Board header showed a static "Mi Tablero"** — `load_board` never updated the title label; it
  now shows the selected board's real name. *(bug)*
- [x] **N+1 tag queries** — `get_tasks` / `get_scheduled_tasks` opened one connection per task to load
  tags. Added `get_task_tags_bulk()` (single query, grouped) and wired both to it. *(efficiency)*
- [x] **Stale test suite** — 3 `database` tests asserted the pre-`category_id` tag shape and were
  silently not running (pytest not installed). Aligned them and added tests for the new helpers
  (`get_scheduled_tasks`, `get_task_board_id`, `get_setting/set_setting`, `get_task_tags_bulk`).

---

## 🧹 Code quality & tech debt (found, not yet fixed)

- [x] **`db_path=DB_NAME` default binding is frozen at import.** *(Done in v0.4.0.)* All 38
  `database.py` functions now use `db_path=None` → `db_path or DB_NAME`, resolving at call time.
  Reassigning `database.DB_NAME` is honored everywhere; proven by `test_db_name_is_resolved_at_call_time`.
  **(P1 — consistency)**
- [x] **`TaskListArea.layout` shadows `QWidget.layout()`** (`widgets.py`). *(Done in v0.4.0.)* Renamed
  to `list_layout`. **(P2)**
- [x] **Connections are never explicitly closed.** *(Done in the post-0.6.0 readability pass.)*
  `get_connection` is now a real `contextlib.contextmanager` that closes in a `finally` block
  (commit on success, rollback on exception); all 58 call sites unchanged. **(P2 — perf)**
- [x] **`data_changed` fires on plain navigation, not just mutations.** *(Done in the post-0.6.0
  readability pass.)* `board_view.load_board(board_id, notify=True)` now skips the emit for
  pure-navigation callers (board switch, startup, theme reload); `TaskDetailDialog` tracks
  `self.modified` so opening a task to just look no longer triggers a bell/calendar/`.ics`
  refresh. **(P2 — perf)**
- [x] **Duplicated inline stylesheets.** *(Done in the post-0.6.0 readability pass — QMenu/swatch;
  extended 2026-08-03 with tag pills.)* `styles.style_menu()` / `styles.color_swatch_css()` /
  `styles.tag_pill_css()` cover QMenu, color-swatch and tag-pill duplicates across
  `widgets.py`/`sidebar.py`/`board_view.py`/`detail_dialog/*`, plus the tray menu. Other ad-hoc
  one-off inline styles (not actually duplicated elsewhere) intentionally left alone. **(P3)**
- [x] **Dead `#TaskCardDueDate` object name** *(Done in v0.4.0.)* — dropped the unused name (label is
  styled inline). **(P3)**
- [x] **iCalendar line folding** *(Done in v0.4.0.)* — continuations now cap at 74 content octets so
  the folded line (incl. the leading space) stays ≤75; unit-tested. **(P3)**
- [x] **Same-column drag reorder off-by-one** *(Done in v0.4.0.)* — the dragged card is excluded from
  the drop-index calc (`widgets.compute_drop_index`), with a regression test. **(P2 — bug)**
- [ ] **Auto-updater uses `git pull`** (`main.py`) — requires git + a clean tree on the user's machine.
  Consider updating from GitHub Release assets (ties into packaging, below). **(P2)**
- [x] **Systemic double-commit pattern beyond `create_log`** *(Audited and ruled out 2026-08-10 —
  see the forensic-pass section above.)* Found during the 2026-08-07 forensic pass while fixing
  `create_log`'s premature commit; the dedicated audit this item asked for happened as a side
  effect of removing ~40 redundant *trailing* commits — none were premature/mid-transaction.
  **(P2 — correctness/atomicity)**
- [ ] **`get_task()` / `get_tasks()` return shape inconsistency** — flagged during the 2026-08-07
  forensic pass as out of scope for that wave; the two functions don't expose task fields
  identically, which is a trap for future code that assumes parity between them. **(P2 — consistency)**
- [ ] **`backups._prune_backups(keep=0)` edge case** — currently unreachable (no UI path sets `keep`
  to `0`), but the function doesn't guard against it explicitly. Low priority since it can't be hit
  today. **(P3)**
- [x] **`restore_task()` loses `task_links` ordering on Ctrl+Z** *(Done 2026-08-10 — see the
  forensic-pass section above.)* Links are now captured and restored with their real `position`.
- [ ] **`CalendarViewWidget.refresh()` runs even while the calendar isn't visible** — wasteful but
  harmless (no wrong output, just an avoidable recompute). **(P3 — efficiency)**
- [ ] **Missing-file link rendering has no automated regression test** — flagged during QA on the
  2026-08-10 local-file-attachments wave: `_build_link_row`'s red/tooltip path for a local
  attachment whose file no longer exists on disk was verified manually (real dialog against a temp
  DB) but the Architect's own test list for that wave didn't include a dedicated `pytest` case for
  it. Low risk (simple, already-verified logic) but worth locking in next time this file is
  touched. **(P3 — test coverage)**
- [ ] **`restore_column`/`restore_board` aren't atomic across their children** — found during the
  2026-08-10 forensic pass: each nested `restore_task`/`restore_column` call opens its own
  connection/transaction, so a failure partway through an undo of a multi-task column/board leaves
  a partially-restored result instead of all-or-nothing. Low practical impact (would need a
  mid-restore failure, e.g. disk full) — not acted on this pass. **(P3 — atomicity)**
- [x] **No shared cleanup fixture for widget-constructing tests** *(Done 2026-08-10 — see the
  forensic-pass section above.)* Found during the CI-flakiness investigation: dozens of tests
  construct a `BoardViewWidget`/`TaskDetailDialog` without ever closing/deleting it, relying
  entirely on the session-end `qapp` teardown — turned out to still be a live CI-flakiness source
  (py3.10 kept failing even after the first fix), not just a theoretical one. Fixed with an
  autouse `tests/conftest.py` fixture that closes every top-level widget after each test.

---

## 🧪 Testing & tooling

- [x] Tests for `ics_export` (escaping, folding, `SEQUENCE`/`LAST-MODIFIED`, all-day `DTSTART/DTEND`).
  *(Done in v0.4.0 — `tests/test_ics_export.py`.)*
- [x] Headless (offscreen) smoke tests for the Qt widgets (calendar grid, bell popup, settings dialog).
  *(Done 2026-08-03 — `tests/test_widgets_headless.py` + a session-scoped `qapp` fixture in
  `conftest.py`; passes with `QT_QPA_PLATFORM=offscreen`, matching CI.)*
- [x] CI workflow running `pytest` on push/PR *(Done — `.github/workflows/ci.yml`, matrix py3.10–3.12
  with the Qt system libs; `test` job).*
- [x] `ruff` lint check in CI *(Done — `lint` job; ruleset `E4/E7/E9/F` in `[tool.ruff.lint]`, baseline
  clean).*

---

## 🚀 Feature backlog for new releases

### Reminders & calendar (build on 0.3.x)
- [x] **Overdue in the bell** *(Done in v0.4.0)* — past-due tasks now surface in their own "ATRASADAS"
  group above today/tomorrow, included in the badge count.
- [x] **Time-of-day due + `VALARM`** *(Done in v0.6.0)* — optional time on due dates, and reminder
  alarms in the `.ics`.
- [x] **Calendar: drag a task to change its due date** *(Done in v0.4.0)*, plus **Month/Week/Day
  views** *(Done in v0.6.0)*.
- [x] **Calendar: filter by board** + a board color legend *(Done in v0.6.0)*.
- [x] **"Subscribe in Google" helper** in Ajustes *(Done in v0.4.0)* — stores the public feed URL
  (`ics_public_url`) and a button that copies it and opens Google's *add-by-URL* page.
- [x] **Per-board `.ics` feeds** so each board can be a separate subscribable calendar. One-off
  **export** was per-board since v0.6.0; **auto-sync** (the always-up-to-date subscribable feed)
  became per-board too on 2026-08-03 — `board_ics_sync` table + `database/ics_sync.py`, a board
  picker in `CalendarSettingsDialog`'s auto-sync section (mirrors the export picker), and
  `main.py`'s `sync_ics()` now rewrites the global feed plus every configured per-board feed.

### Task power features
- [x] **Global search & filter** (by title, tag, due, board) *(Done in v0.5.0 — 🔍 sidebar button + Ctrl+F)*.
- [~] **Subtasks / checklists** inside a card — shipped in **v0.5.0** but **removed in v0.5.1** (product
  decision; the nested-checklist approach wasn't a fit). Could be revisited later with a different UX.
- [x] **Recurring tasks** (daily/weekly/monthly) *(Done in v0.6.0)*.
- [x] **Attachments / links** on cards *(Done in v0.6.0 — `task_links` table)*. **Extended
  2026-08-10** (user-requested): a **📁** browse button next to the existing URL/label inputs opens
  the native OS file picker to attach a local file instead of only pasting a URL (label auto-fills
  from the file name if left blank). Link rows now render **📎** for local attachments vs **🔗** for
  web links, and flag a local attachment in red with a tooltip if its file has since been moved or
  deleted (`os.path.exists` check at render time). Also fixed a latent bug where opening a local
  path silently did nothing — `QDesktopServices.openUrl(QUrl(raw_path))` is malformed for a bare
  Windows path; local links now go through `QUrl.fromLocalFile(...)`, and any link that still fails
  to open shows a warning dialog. No DB schema change (`task_links.url` already held either kind);
  classification is a scheme heuristic (`_is_local_link`) at render/open time.
- [x] **Undo/redo** for destructive actions (delete task/column/board) *(Done in v0.6.0 — snapshot/restore + `undo.py`)*.
- [x] **Keyboard shortcuts** — ~~`Ctrl+N` new task~~, ~~`Ctrl+F` search~~, ~~`Ctrl+Z`/`Ctrl+Y`
  undo/redo~~ all done earlier. `Esc` to close dialogs was already free (Qt's default `QDialog`
  behavior — verified empirically with a headless `QTest.keyClick` sweep across all 9 dialogs, no
  code needed). Arrow-key board navigation added 2026-08-03: **Alt+Up/Alt+Down** cycle boards
  (`SidebarWidget.select_adjacent_board`) — bare arrows were unavailable, already claimed by every
  text field and list widget in the app. **Extended 2026-08-07**: `Ctrl+Shift+N` (new column),
  `Ctrl+1`..`Ctrl+9` (jump to the Nth sidebar board via the new
  `SidebarWidget.select_board_by_index`), `Ctrl+,` (Ajustes), `Ctrl+Shift+C` (Calendar) — plus
  **Ctrl+/** opening a new `ShortcutsDialog` reference window that lists every shortcut in the
  app (new, pre-existing global, and rich-text-editor-local) grouped by category, since they'd
  been scattered across tooltips/README with no in-app place to see them all. **`Ctrl+N`
  refined 2026-08-07** (user-requested): now targets `BoardViewWidget._last_active_column_id`
  (the last column a card/`+ Añadir Tarea`/click touched, tracked via a new
  `ColumnWidget.column_activated` signal + task-card click wrapper), re-validated against the
  active board on every use so a stale or cross-board id safely falls back to the first column —
  instead of always adding to the first column regardless of context. Also fixed a latent
  guard bug in `board_view.add_column` (`board_id == -1` wasn't rejected, since `not -1` is
  `False` in Python) surfaced by exposing it to a global shortcut with no UI-visibility gate.
  **2026-08-07:** added a visible **❔** button to the sidebar utility bar (next to 🔍/📅/⚙) that
  opens the same shortcuts dialog — `Ctrl+/` alone had no UI entry point, and reads as
  `Ctrl+Shift+/` on a Spanish keyboard layout since `/` requires Shift there.
- [x] **Rich-text tables + strikethrough** in the description/diary editors *(Done post-0.6.0,
  2026-08-03)*. Pasting a table (Excel/Sheets/Word, or tab-separated text) inserts a real table
  instead of flattening it to text; the toolbar's **▦** button inserts an empty one. Strikethrough
  via Ctrl+Shift+X or a toolbar button, alongside the existing bold/italic/bullets.
- [x] **Arrows in rich text** *(Done 2026-08-05)*. Typing `-->` in the description or diary/chat
  editor auto-converts it to `→`; a toolbar button (next to bullets) inserts one too.
- [x] **Priority quick-selector** *(Done 2026-08-05)*. A **🚩 Prioridad** dropdown next to
  Etiquetas in the task detail dialog (Baja/Media/Alta by default, seeded on first use and merged
  with the pre-existing onboarding "Prioridad: Alta" demo tag rather than duplicating it). It's a
  fast UI shortcut over the same tag system — no new DB schema — so the chosen priority shows up
  as a pill on the board card automatically, through the existing tag-pill rendering.
- [x] **Board links on task cards** *(Done 2026-08-05)*. A task can point at a *different* board
  (e.g. a summary task in "Tareas" linking to the dedicated "SW X" board tracking that work in
  detail) via a new **🔗 Tablero vinculado** selector next to Etiquetas/Prioridad. The card then
  shows a colored, clickable **🔗 <board>** pill that jumps to that board instead of opening the
  task's own detail. New nullable `tasks.linked_board_id` column (`ON DELETE SET NULL`, so
  deleting the target board just clears the link); included in the task snapshot/restore
  (Ctrl+Z) round-trip.
- [x] **Hover-to-expand on collapsed columns** *(Done 2026-08-06)*. Extends the 0.5.1
  "drop-to-expand" behavior (which always dropped the card at the end): holding a dragged card
  over a collapsed column for ~650ms now unfolds it automatically so a real drop position can be
  chosen, via the same `compute_drop_index` mechanism already used by expanded columns. A quick
  drop before the timer fires still falls to the end (unchanged). **Critical crash fixed
  2026-08-07** (user-reported, real production drag): the initial implementation reloaded the
  *entire* board on hover-expand, which destroyed and rebuilt every column — including the one the
  dragged card was still being dragged out of; dropping the card afterward could crash the app.
  Fixed with a surgical `BoardViewWidget._rebuild_single_column(column_id)` that only ever touches
  the one column whose state actually changed, never the drag's source column. **Behavior
  finalized 2026-08-07** (same day, user-requested): the column now *always* folds back up once
  the drag ends, whether the card was dropped inside it, elsewhere, or the drag was cancelled — it
  no longer stays permanently unfolded just because the drop happened to land there. It's purely a
  temporary peek, never equivalent to manually clicking unfold.
- [x] **Task timer with a board-card badge + configurable alert threshold** *(Done 2026-08-07,
  user-requested)*. New **⏱ Temporizador** control in the task detail: **▶ Iniciar** records the
  start time (`tasks.timer_started_at`, nullable ISO timestamp) and shows a live elapsed-time
  counter; **↺ Reiniciar** resets it to now; **✕ Detener** clears it. All three are instant-persist
  (write to the DB immediately, like a diary entry or a link) rather than deferred to "Guardar
  Cambios". The same elapsed time shows as a badge directly on the board-view card — not just in
  the dialog — so tasks running too long are visible without opening each one; the badge turns red
  once it crosses `app_settings.timer_alert_hours` (a `QSpinBox` in Ajustes, default 24h, global
  for the whole app). `BoardViewWidget.refresh_timer_badges()` (a 60s `QTimer`) keeps visible
  badges' elapsed text current without any DB query or widget reconstruction. Carried through
  `snapshot_task`/`restore_task` for Ctrl+Z undo, same as `linked_board_id`.
- [x] **Click-to-enlarge pasted images** *(Done 2026-08-12, user-requested)*. An image pasted
  into the task description or diary/chat now opens in a larger centered view when clicked —
  while composing, while editing an existing entry, or once it's already been posted.
  `MarkdownTextEdit._insert_image` wraps the pasted image's data URI in a same-URI `<a href>`
  at insertion time, clickable via `QTextEdit.anchorAt()` (the three editable surfaces, all
  sharing `MarkdownTextEdit`) or `QLabel.linkActivated` (an already-posted entry's read-only
  `content_label`). New `detail_dialog/image_preview_dialog.py::ImagePreviewDialog` scales to
  90% of screen size and closes on click/Esc/close button. A press/release position-delta
  check keeps normal text-selection drags from being hijacked into opening the preview.
  **Fixed in v0.9.2** (same-day user feedback): a real bug — `content_label`'s
  `setTextInteractionFlags(Qt.TextSelectableByMouse)` was *replacing* the flag set instead of
  adding to it, silently stripping `LinksAccessibleByMouse`, so the preview silently did
  nothing on an already-posted entry despite working fine while composing (closed with a test
  that fires a real click, verified via `git stash` to fail against the pre-fix code — the
  original test only called the handler directly, missing this entirely). Also: the preview
  now always scales small images *up* instead of only ever scaling large ones down; and
  description-pasted images default to the same width as chat images
  (`desc_input.image_width_provider = self._chat_image_width`) instead of risking overflow on
  dialog resize. **Fixed same day, follow-up**: the preview still looked blurry — v0.9.2's
  "always scale up-or-down" fix addressed the dialog's scaling logic correctly, but `<a href>`
  and `<img src>` were still the *same* small, already-downscaled data URI, so enlarging meant
  interpolating detail an earlier downscale had already thrown away. `_insert_image` now stores
  a second, separately-scaled copy (capped at 1920px) specifically for the `href`, so the
  dialog scales down from real detail instead of up from a thumbnail. Manually verified: a
  3000×2000 paste now yields a 1920×1280 preview vs. a 614×409 inline thumbnail.

### Data & safety
- [x] **Automatic DB backups** *(Done in v0.4.0)* — `backups.py` writes a consistent SQLite snapshot
  to `backups/` on startup and keeps the 5 most recent.
- [x] **Export/report** — dump boards to JSON/CSV or a Markdown project report *(Done in v0.6.0 —
  `exporter.py`)*.
- [x] **Board archiving** (hide without deleting) *(Done in v0.6.0)*.

### UX & platform
- [x] **Two-row sidebar utility bar** *(Done 2026-08-07, user-requested)*. `SidebarWidget.
  _build_utility_bar()`'s clock + 5 icon buttons (🔔🔍📅⚙❔) were cramped into a single row that
  didn't fit comfortably in the ~220px sidebar; now the clock sits on its own centered row above a
  second, centered row of icon buttons. Purely a layout change (`QHBoxLayout` → `QVBoxLayout` +
  a nested row) — no button's behavior, size, tooltip, or object name changed.
- [x] **Settings screen** — persist window size/position, theme, notification prefs, sync path *(Done
  in v0.6.0 — `settings_dialog.py`; sync path already lived in `app_settings` since 0.4.0)*.
- [x] **Light theme** + theme toggle *(Done in v0.6.0 — QSS was already centralized)*.
- [x] **Internationalization (i18n)** — infrastructure done 2026-08-03: every user-facing string
  (~280) moved into `strings.py` (a flat `STRINGS` dict + `t(key, **kwargs)`), covering the whole
  app — `main.py`, `board_view.py`, `widgets.py`, `sidebar.py`, `calendar_view.py`,
  `search_dialog.py`, `settings_dialog.py`, `detail_dialog/*`. Spanish is still the only *active*
  language (no `.ts`/`.qm`/translator tooling, no language switcher yet — deliberately scoped to
  extraction-only per the user's direction) but adding a second language now only touches `strings.py`.
- [x] **Cross-platform notifications** — audited 2026-08-03 (code review, not live macOS/Linux
  testing — no such machine available here). Already portable: the only two OS-specific call sites
  (`subprocess.STARTUPINFO`, `ctypes.windll` AppUserModelID) are correctly guarded behind
  `os.name == 'nt'`, and `QSystemTrayIcon` usage already checks `isSystemTrayAvailable()`. One
  documented, unfixable-from-here limitation: `QSystemTrayIcon.showMessage()` has weak Notification
  Center integration on macOS (a Qt/OS gap — would need a native bridge like PyObjC).
- [x] **Taskbar icon showing as the generic Python icon on a second PC** *(Done 2026-08-12,
  user-reported)*. The code (absolute icon paths, an explicit AppUserModelID) was already
  correct as of 2026-07-29 — likely explanation is Windows caching the wrong icon on that PC
  under the *old* AppUserModelID from before that fix, a cache nothing since had invalidated.
  Versioned the AppUserModelID (`"EkinKanban.TrelloLite.2"`, `main.py`) so Windows treats it
  as a fresh identity. **Not fully verifiable from here** — the affected PC needs a `git pull`
  + relaunch; if the icon still doesn't refresh, the user needs to unpin/re-pin the taskbar
  icon or reboot, since no app-level code can force-clear another machine's OS icon cache.
- [x] **App icon redesigned with a transparent background** *(Done 2026-08-12,
  user-requested)*. `ekin_icon.png`/`.ico` no longer carry a baked-in white background/drop
  shadow — regenerated via a one-off Pillow script (per-pixel whiteness threshold, not a new
  runtime dependency) at all 7 `.ico` resolutions. **Retuned same day (v0.9.2)**: the first
  threshold (170–225) still left a visible grayish halo — most background pixels actually sit
  in 195–225 per a finer histogram of the true original (re-pulled from git history, since the
  file had already been overwritten once). Tightened to 140–165; outer-edge alpha is now
  uniformly `0` (was `0`–`97`). An opacity-mask visualization clarified along the way that what
  looked like a stray white shape was actually the badge's own intentional torn-corner design,
  correctly kept opaque — not something to remove.

### Packaging & distribution
- [ ] **Standalone executable** (PyInstaller) so non-developers don't need Python/git.
- [ ] **Update from Releases** instead of `git pull` (download the latest release asset).

---

## 🗺️ Suggested next steps
1. ~~**0.3.2 (patch)** — ship the forensic fixes.~~ ✅ Released.
2. ~~**0.4.0** — reminders polish + automatic DB backups + P1 `db_path` normalization.~~ ✅ 2026-07-22.
3. ~~**0.5.0** — global search + subtasks/checklists.~~ ✅ 2026-07-29 *(subtasks later removed in 0.5.1)*.
4. ~~**0.5.1** — UX refinements: collapsible columns (+ drop-to-expand), plain/image paste, comment
   edit/delete, painted icons, Ctrl+B/N & Ctrl+K/I formatting, Outlook/iCloud sync docs, taskbar icon.~~
   ✅ 2026-07-30.
5. ~~**0.6.0** — calendar depth (Mes/Semana/Día + filter + VALARM + per-board feeds); recurring
   tasks; undo/redo; attachments/links; board archiving; export (JSON/CSV/MD); dark/light theme +
   Settings screen.~~ ✅ 2026-08-03.
6. ~~**Post-0.6.0 readability pass** — connection leak fix; `data_changed` over-firing fix;
   centralize QMenu/swatch QSS; split `detail_dialog.py` → `detail_dialog/` package (7 classes,
   one per file); split `database.py` → `database/` package (~60 functions across 11 domain
   modules, `DB_NAME`/`get_connection` kept together in `__init__.py` to preserve call-time
   resolution).~~ ✅ 2026-08-03.
7. ~~**0.7.0** — table paste/insert (Excel/Sheets/Word or tab-separated text; **▦** toolbar button
   for an empty table) + strikethrough (Ctrl+Shift+X) in the description/diary editors, released
   together with the readability-pass fixes above.~~ ✅ 2026-08-03.
8. ~~**Small-wins + medium batch** — `Esc`-closes-dialogs (verified, already free) + Alt+Up/Down
   board nav; tag-pill QSS centralization; light-theme hardcoded-color fixes (+ an `apply_theme`
   ordering bug so the fix actually takes effect on startup); per-board auto-sync `.ics` feeds;
   i18n string-extraction infrastructure (`strings.py`, ~280 strings); cross-platform notification
   audit (already portable, one documented macOS limitation); headless Qt widget smoke tests.~~
   ✅ 2026-08-03.
9. ~~**Arrows + Priority selector** — `-->` auto-converts to `→` in rich text (+ toolbar button);
   a **🚩 Prioridad** quick-selector in the task detail dialog, next to Etiquetas, that reuses the
   tag system so it shows on board cards for free.~~ ✅ 2026-08-05.
10. ~~**Board links on task cards** — a **🔗 Tablero vinculado** selector in the task detail dialog
   links a task to a different board; the card shows a clickable pill that jumps straight there.~~
   ✅ 2026-08-05.
11. ~~**Hover-to-expand on collapsed columns** — holding a dragged card over a collapsed column
   unfolds it temporarily so a drop position can be chosen, instead of always landing at the end;
   folds back up if the drag ends without dropping there.~~ ✅ 2026-08-06.
12. ~~**More keyboard shortcuts + a shortcuts dialog** — `Ctrl+Shift+N` new column, `Ctrl+1..9`
   jump to a sidebar board, `Ctrl+,` Ajustes, `Ctrl+Shift+C` Calendar, and **Ctrl+/** opens a
   reference dialog listing every shortcut in the app.~~ ✅ 2026-08-07.
13. ~~**Ctrl+N last-active column, two-row utility bar, hover-expand always re-collapses** —
   three independent refinements: `Ctrl+N` targets the last column interacted with instead of
   always the first; the sidebar utility bar spans two rows instead of one cramped one; a
   hover-expanded column now always folds back up when the drag ends, even if the card was
   dropped inside it.~~ ✅ 2026-08-07.
14. ~~**Task timer + board-card badge** — a **⏱ Temporizador** in the task detail (Iniciar/
   Reiniciar/Detener, instant-persist) shows the same elapsed time as a badge on the board card,
   turning red past a configurable Ajustes threshold — so stale tasks are visible without opening
   each one.~~ ✅ 2026-08-07.
15. ~~**v0.9.0 — forensic bug-hunt pass** — 2 critical fixes (leaked `TaskDetailDialog`+`QTimer`;
   uncaught `IntegrityError` crash on Ctrl+Z), 4 correctness fixes (stale shortcuts text, stale
   calendar-edited board card, silent data loss on column/board copy, `create_log` atomicity), 3
   efficiency/cleanup items, plus a pre-existing test-harness crash (`STATUS_HEAP_CORRUPTION` at
   pytest shutdown) found and fixed along the way. 159/159 tests passing, clean exit code.~~
   ✅ 2026-08-07.
16. ~~**Local file attachments on task links** — a **📁** browse button next to the existing
   enlaces/adjuntos inputs opens the native OS file picker to attach a local file instead of only
   pasting a URL; link rows render 📎 for local attachments vs 🔗 for web links, flag a missing
   local file in red, and fixed a latent bug where local paths never actually opened
   (`QUrl.fromLocalFile` instead of a malformed raw-path `QUrl`). No DB schema change. 166/166
   tests passing (7 new).~~ ✅ 2026-08-10.
17. ~~**v0.9.1 — forensic bug-hunt pass + CI fix** — found and fixed the root cause of CI
   intermittently failing since 2026-08-07 (a stray, unparented `QTimer.singleShot` that could fire
   against an already-destroyed widget, reproduced down to the actual native crash); a first push
   fixed that plus `tests/test_main_window.py` leaking real timers (incl. live `git` subprocess
   calls), which flipped CI from "all 3 Python versions fail" to "2 of 3 pass" — confirming the
   mechanism but exposing a second, broader source (dozens of tests never closing the widgets they
   construct), fixed with a follow-up push adding an autouse test-cleanup fixture, landing CI fully
   green (3 Python versions + lint + release), verified via the GitHub Actions API after each push.
   Also fixed `restore_task()` losing link order on Ctrl+Z; removed ~40 redundant `conn.commit()`
   calls across `database/` (doubling as the dedicated double-commit audit an earlier item asked
   for) plus two confirmed dead-code spots. 167/167 tests passing, ruff clean.~~ ✅ 2026-08-10.
18. ~~**Click-to-enlarge pasted images, taskbar icon cache fix, transparent icon redesign** —
   pasted images in the description/diary now open larger on click (new
   `ImagePreviewDialog`); the taskbar showing Ekin as a generic Python icon on a second PC
   traced to Windows caching an icon under a since-fixed AppUserModelID, addressed by
   versioning the identifier; `ekin_icon.png`/`.ico` regenerated with a real transparent
   background instead of a baked-in white one. 176/176 tests passing (9 new), ruff clean.~~
   ✅ 2026-08-12.
19. ~~**v0.9.2 — same-day fixes to the wave above, from direct user feedback** — a real bug
   (a `QLabel` interaction-flag call silently stripping `LinksAccessibleByMouse`) meant
   click-to-enlarge did nothing on an already-posted diary entry, fixed and locked in with a
   test proven via `git stash` to fail against the pre-fix code; the preview now upscales
   small images instead of only ever scaling large ones down; description-pasted images
   default to the same width as chat images; the icon's transparency threshold retuned
   (140–165, was 170–225) for a genuinely crisp, halo-free background. 178/178 tests passing
   (2 new), ruff clean. Cut as **v0.9.2**, tag + GitHub Release confirmed published.~~
   ✅ 2026-08-12.
20. ~~**Image preview resolution fix — same-day follow-up on v0.9.2** — the enlarged preview
   still looked blurry because `<a href>`/`<img src>` shared the same already-downscaled data
   URI; `_insert_image` now stores a separate, higher-resolution copy (capped at 1920px) just
   for the preview, so `ImagePreviewDialog` scales down from real detail instead of up from a
   thumbnail. Manually verified end-to-end (3000×2000 → 1920×1280 preview vs. 614×409 inline).
   180/180 tests passing (2 new), ruff clean. Cut as **v0.9.3**, tag + GitHub Release confirmed
   published.~~ ✅ 2026-08-12.

### 🎯 Theme D — Distribution (parked)
**PyInstaller** standalone build + **update-from-Releases** (replaces the `git pull` auto-updater).
Parked per the user's direction: the project stays dev-mode (run from source) until there's a
reason to distribute it to non-developers.

### 🔧 Ongoing tech debt (fold into any wave)
Full i18n (an actual English translation + a language switcher in Settings — today's pass was
extraction-only, Spanish stays the only active language); remaining inline QSS beyond
QMenu/swatch/tag-pill (misc one-off buttons, not actually duplicated so lower value); auto-updater
still uses `git pull` (tied to Theme D).
