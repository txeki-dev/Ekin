# 🗂️ Ekin Kanban — Backlog

Living planning doc: forensic findings (tech debt) + ideas for future releases.
Ordered roughly by value/effort. Checkboxes track what's done.

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
- [x] **Attachments / links** on cards *(Done in v0.6.0 — `task_links` table)*.
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
  been scattered across tooltips/README with no in-app place to see them all. Also fixed a latent
  guard bug in `board_view.add_column` (`board_id == -1` wasn't rejected, since `not -1` is
  `False` in Python) surfaced by exposing it to a global shortcut with no UI-visibility gate.
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
  drop before the timer fires still falls to the end (unchanged). If the drag ends without
  dropping inside that column, it folds itself back up — temporary, not equivalent to manually
  clicking unfold.

### Data & safety
- [x] **Automatic DB backups** *(Done in v0.4.0)* — `backups.py` writes a consistent SQLite snapshot
  to `backups/` on startup and keeps the 5 most recent.
- [x] **Export/report** — dump boards to JSON/CSV or a Markdown project report *(Done in v0.6.0 —
  `exporter.py`)*.
- [x] **Board archiving** (hide without deleting) *(Done in v0.6.0)*.

### UX & platform
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

### 🎯 Theme D — Distribution (parked)
**PyInstaller** standalone build + **update-from-Releases** (replaces the `git pull` auto-updater).
Parked per the user's direction: the project stays dev-mode (run from source) until there's a
reason to distribute it to non-developers.

### 🔧 Ongoing tech debt (fold into any wave)
Full i18n (an actual English translation + a language switcher in Settings — today's pass was
extraction-only, Spanish stays the only active language); remaining inline QSS beyond
QMenu/swatch/tag-pill (misc one-off buttons, not actually duplicated so lower value); auto-updater
still uses `git pull` (tied to Theme D).
