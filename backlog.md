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

- [ ] **`db_path=DB_NAME` default binding is frozen at import.** ~35 `database.py` functions bind the
  default at definition time, so reassigning `database.DB_NAME` is silently ignored (only the 4 newest
  helpers resolve it at call time). Make them all `db_path=None` → `db_path or DB_NAME`, **or** inject
  the DB path explicitly everywhere (e.g. a small `Database` object). Removes a latent footgun and
  makes the whole layer testable against temp DBs without monkeypatching. **(P1 — consistency)**
- [ ] **`TaskListArea.layout` shadows `QWidget.layout()`** (`widgets.py`). It works, but overriding a
  Qt method with an attribute is fragile. Rename to `list_layout`. **(P2)**
- [ ] **Connections are never explicitly closed.** `with get_connection() as conn:` only manages the
  transaction, not closing; CPython refcounting closes them promptly so it's not a real leak, but a
  closing context manager (or a shared connection) would be more robust and faster. **(P2 — perf)**
- [ ] **`data_changed` fires on plain navigation, not just mutations.** Switching boards re-runs the
  calendar refresh, the bell query and (if configured) the full `.ics` build. Introduce a dedicated
  "data mutated" signal, or only refresh the calendar when it becomes visible. **(P2 — perf)**
- [ ] **Duplicated inline stylesheets.** The dark `QMenu` theme, colored swatch buttons and several
  ad-hoc styles are repeated across `widgets.py`/`board_view.py`/`detail_dialog.py`. Centralize in
  `styles.py` via object names. **(P3)**
- [ ] **Dead `#TaskCardDueDate` object name** — set on the due-date label but has no QSS rule (styled
  inline instead). Either add the rule or drop the name. **(P3)**
- [ ] **iCalendar line folding** — continuation lines can be 1 octet over the 75-octet limit (the
  leading space isn't counted). Harmless for real clients, but tighten for strict RFC 5545. **(P3)**
- [ ] **Same-column drag reorder** includes the hidden dragged card in the drop-index calc, which can
  produce an off-by-one when dropping below the original slot. Exclude the dragged card. **(P2 — bug)**
- [ ] **Auto-updater uses `git pull`** (`main.py`) — requires git + a clean tree on the user's machine.
  Consider updating from GitHub Release assets (ties into packaging, below). **(P2)**

---

## 🧪 Testing & tooling

- [ ] Tests for `ics_export` (escaping, folding, `SEQUENCE`/`LAST-MODIFIED`, all-day `DTSTART/DTEND`).
- [ ] Headless (offscreen) smoke tests for the Qt widgets (calendar grid, bell popup, settings dialog).
- [ ] CI workflow running `pytest` on push/PR (currently only the release workflow exists).
- [ ] `ruff`/`flake8` lint + formatting check in CI.

---

## 🚀 Feature backlog for new releases

### Reminders & calendar (build on 0.3.x)
- [ ] **Overdue in the bell** — surface past-due tasks (own "Atrasadas" group), not just today/tomorrow.
- [ ] **Time-of-day due + `VALARM`** — optional time on due dates, and reminder alarms in the `.ics`.
- [ ] **Calendar: drag a task to change its due date**, and a **week/day view**.
- [ ] **Calendar: filter by board** + a board color legend.
- [ ] **"Subscribe in Google" helper** in Ajustes — store the public feed URL and a button that opens
  Google's *add-by-URL* page and copies the URL (the manual step users trip on).
- [ ] **Per-board `.ics` feeds** so each board can be a separate subscribable calendar.

### Task power features
- [ ] **Global search & filter** (by title, tag, due, board).
- [ ] **Subtasks / checklists** inside a card.
- [ ] **Recurring tasks** (daily/weekly/monthly).
- [ ] **Attachments / links** on cards.
- [ ] **Undo/redo** for destructive actions (delete task/column/board).
- [ ] **Keyboard shortcuts** — `Esc` to close dialogs, `Ctrl+N` new task, `Ctrl+F` search, arrow nav.

### Data & safety
- [ ] **Automatic DB backups** — copy `ekin_board.db` → `.bak` on startup (rotate a few).
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
2. **0.4.0** — reminders polish: overdue-in-bell + calendar drag-to-reschedule + "Subscribe in Google"
   helper; plus automatic DB backups (high value, low effort).
3. **0.5.0** — global search + subtasks/checklists.
4. **Ongoing tech debt** — normalize `db_path` handling and add the CI/lint workflow.
