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
- [ ] **Connections are never explicitly closed.** `with get_connection() as conn:` only manages the
  transaction, not closing; CPython refcounting closes them promptly so it's not a real leak, but a
  closing context manager (or a shared connection) would be more robust and faster. **(P2 — perf)**
- [ ] **`data_changed` fires on plain navigation, not just mutations.** Switching boards re-runs the
  calendar refresh, the bell query and (if configured) the full `.ics` build. Introduce a dedicated
  "data mutated" signal, or only refresh the calendar when it becomes visible. **(P2 — perf)**
- [ ] **Duplicated inline stylesheets.** The dark `QMenu` theme, colored swatch buttons and several
  ad-hoc styles are repeated across `widgets.py`/`board_view.py`/`detail_dialog.py`. Centralize in
  `styles.py` via object names. **(P3)**
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
- [ ] Headless (offscreen) smoke tests for the Qt widgets (calendar grid, bell popup, settings dialog).
- [x] CI workflow running `pytest` on push/PR *(Done — `.github/workflows/ci.yml`, matrix py3.10–3.12
  with the Qt system libs; `test` job).*
- [x] `ruff` lint check in CI *(Done — `lint` job; ruleset `E4/E7/E9/F` in `[tool.ruff.lint]`, baseline
  clean).*

---

## 🚀 Feature backlog for new releases

### Reminders & calendar (build on 0.3.x)
- [x] **Overdue in the bell** *(Done in v0.4.0)* — past-due tasks now surface in their own "ATRASADAS"
  group above today/tomorrow, included in the badge count.
- [ ] **Time-of-day due + `VALARM`** — optional time on due dates, and reminder alarms in the `.ics`.
- [x] **Calendar: drag a task to change its due date** *(Done in v0.4.0)*. — a **week/day view** is
  still pending.
- [ ] **Calendar: filter by board** + a board color legend.
- [x] **"Subscribe in Google" helper** in Ajustes *(Done in v0.4.0)* — stores the public feed URL
  (`ics_public_url`) and a button that copies it and opens Google's *add-by-URL* page.
- [ ] **Per-board `.ics` feeds** so each board can be a separate subscribable calendar.

### Task power features
- [ ] **Global search & filter** (by title, tag, due, board).
- [ ] **Subtasks / checklists** inside a card.
- [ ] **Recurring tasks** (daily/weekly/monthly).
- [ ] **Attachments / links** on cards.
- [ ] **Undo/redo** for destructive actions (delete task/column/board).
- [ ] **Keyboard shortcuts** — `Esc` to close dialogs, `Ctrl+N` new task, `Ctrl+F` search, arrow nav.

### Data & safety
- [x] **Automatic DB backups** *(Done in v0.4.0)* — `backups.py` writes a consistent SQLite snapshot
  to `backups/` on startup and keeps the 5 most recent.
- [ ] **Export/report** — dump boards to JSON/CSV or a Markdown project report.
- [ ] **Board archiving** (hide without deleting).

### UX & platform
- [ ] **Settings screen** — persist window size/position, theme, notification prefs, sync path (some
  of this already lives in `app_settings`).
- [ ] **Light theme** + theme toggle (QSS is already centralized).
- [ ] **Internationalization (i18n)** — strings are hardcoded Spanish; extract to enable EN/others.
- [ ] **Cross-platform notifications** verified on macOS/Linux (Qt tray already portable).

### Packaging & distribution
- [ ] **Standalone executable** (PyInstaller) so non-developers don't need Python/git.
- [ ] **Update from Releases** instead of `git pull` (download the latest release asset).

---

## 🗺️ Suggested next steps
1. ~~**0.3.2 (patch)** — ship the forensic fixes above.~~ ✅ Released.
2. ~~**0.4.0** — reminders polish: overdue-in-bell + calendar drag-to-reschedule + "Subscribe in
   Google" helper; plus automatic DB backups; plus the P1 `db_path` normalization.~~ ✅ Released 2026-07-22.
3. **0.5.0 (next)** — global search + subtasks/checklists.
4. **Ongoing tech debt** — CI `pytest`/lint workflow; connection-closing context manager;
   `data_changed` only on real mutations; centralize duplicated stylesheets.
