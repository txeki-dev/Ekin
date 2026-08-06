# Changelog

All notable changes to Ekin Kanban are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- **Hover-to-expand on collapsed columns.** Dragging a task card and holding it over a collapsed
  column for about a second now unfolds it automatically so you can pick exactly where in the
  column to drop the card, instead of it always landing at the bottom. A quick drop (before the
  column has had time to unfold) still works exactly as before. If the drag ends without dropping
  inside that column — dropped elsewhere, or cancelled — the column folds itself back up.

## [0.8.0] - 2026-08-05

### Added
- **Board links on task cards.** A task can now link to a different board (e.g. a summary task
  "Desarrollo v2.0 SW X" living in a "Tareas" board that points at the dedicated "SW X" board
  where the detailed work is tracked). Pick the target board from the new **🔗 Tablero
  vinculado** selector in the task detail dialog, next to Etiquetas/Prioridad; the card then
  shows a colored, clickable **🔗 <board name>** pill that jumps straight to that board instead
  of opening the task's own detail. If the linked board is later deleted, the link is
  automatically cleared.
- **Arrows in rich text.** Typing `-->` in the task description or the diary/chat editor now
  auto-converts it to `→` as you type; a new toolbar button (next to the bullet-list button)
  inserts one on click.
- **Priority quick-selector.** The task detail dialog now has a small **🚩 Prioridad** selector
  next to Etiquetas (Baja/Media/Alta by default, customizable via **⚙ Gestionar**). It's backed
  by the same tag system as any other tag, so the chosen priority automatically shows up as a
  pill on the board-view card too.
- **Alt+Up / Alt+Down** cycles between boards in the sidebar.
- **Per-board auto-sync `.ics` feeds.** The always-up-to-date subscribable calendar feed
  (Calendario → ⚙ Ajustes → 📂 Elegir archivo…) can now be configured per board, not just
  globally, mirroring the existing per-board one-off export.
- Internationalization infrastructure: every user-facing string (~290) now lives in `strings.py`
  (a flat lookup + `t(key, **kwargs)`) instead of being hardcoded across the UI modules. Spanish
  is still the only active language — this is extraction only, no translation/switcher yet — but
  adding a second language now only touches one file.
- Headless Qt widget smoke tests (calendar grid, deadline-bell popup, settings dialog).

### Changed
- Light theme: fixed several spots that stayed hardcoded to the dark palette (board title,
  sidebar-toggle icon, task-card border, due-date badge), so switching to light theme no longer
  leaves near-invisible text/icons.
- Tag-pill styling centralized into `styles.tag_pill_css(color)` (previously duplicated between
  board cards and the task detail dialog).

### Fixed
- `apply_theme()` now runs before `init_ui()` on startup, so a saved light-theme preference is
  reflected immediately instead of only after the first manual theme toggle.

## [0.7.0] - 2026-08-03

### Added
- **Tables in the description and diary.** Paste a table (from Excel/Sheets/Word, or plain
  tab-separated text) and it becomes a real table instead of jumbled text; the new **▦** toolbar
  button inserts an empty table (prompts for rows/columns).
- **Strikethrough** formatting (Ctrl+Shift+X, plus a toolbar button) in the description and diary.

### Fixed
- Database connections are now closed after every use (previously left open until garbage-collected).
- The bell, calendar and `.ics` feed no longer refresh on plain navigation (switching boards,
  changing the theme) — only when a task, column or board actually changes.

## [0.6.0] - 2026-08-01

### Added — Calendar depth (A)
- **Time-of-day due + reminders.** A task can have an optional **time** (`due_time`); such tasks
  export as timed events with a **`VALARM`** (15-minute reminder) instead of all-day.
- **Week / Day views.** The calendar now toggles between **Mes / Semana / Día**.
- **Filter by board + legend.** A board filter and a colored board legend on the calendar.
- **Per-board `.ics` feeds.** `build_ics(board_id=…)` and a per-board picker in the export dialog.

### Added — Power features (B)
- **Recurring tasks** (daily / weekly / monthly): set in the task dialog; a **🔁** badge on the card;
  overdue recurring tasks **advance to the next occurrence on startup**.
- **Undo / redo** for destructive deletes (task, column, board) via **Ctrl+Z / Ctrl+Y** — restores
  the whole deleted subtree (tags, diary, links) from a snapshot.
- **Attachments / links** on a card: add URLs/paths (open, delete); **🔗** count on the card.
- **Keyboard shortcuts:** **Ctrl+N** new task, **Ctrl+F** search, **Esc** closes dialogs.

### Added — Polish & platform (C)
- **Board archiving:** right-click a board to archive/unarchive; a **🗄 Archivados** toggle hides them.
- **Export / report:** a sidebar **⬇ Exportar** menu → **JSON**, **CSV** (tasks) or a **Markdown**
  project report (`exporter.py`).
- **Settings screen** (⚙ in the sidebar): **theme** (dark / **light**, experimental), Windows
  **notifications** toggle, and the window **size/position is remembered**.

### Changed
- `database` gains `boards.archived`, `tasks.due_time`/`recurrence`, and a `task_links` table (all via
  additive migrations); `styles` is now `build_qss(palette)` + `set_theme()` with dark/light palettes.

### Added
- **Collapsible board columns.** A collapse button folds a column to a narrow strip (expand button,
  task count, vertical name) to save horizontal space; the collapsed state is saved per column
  (`columns.collapsed`). **Dragging a card onto a collapsed column expands it** and drops the card in.
- **Edit a diary/chat comment.** Each comment now has clear **edit** and **delete** icon buttons;
  editing opens an inline editor (new `database.update_log`).
- **Rich-text editor upgrades** (task description + diary): **Tab** nests a bullet into a sub‑bullet
  (**Shift+Tab** un‑nests; glyph varies by depth ● ○ ▪); external text now **pastes as plain text**
  (no foreign fonts/colors); and you can **paste images** directly (embedded inline in the note).
- **Calendar sync: Outlook & Apple/iCloud.** The Ajustes subscribe helper now has **Google / Outlook /
  Apple·iCloud** buttons (Apple copies a `webcal://` link) plus a detailed per‑provider guide; the
  README sync section documents all three in full.

### Changed
- Formatting shortcuts now accept both conventions: **bold = Ctrl+B or Ctrl+N**, **italic = Ctrl+K or
  Ctrl+I** (Spanish MS Word uses N/K). The italic toolbar button now shows **K** (an italic "I" reads
  like a "/").
- **Column, sidebar-toggle and comment icons are now painted** (pixmaps drawn at runtime) instead of
  Unicode/emoji glyphs, so they always render regardless of font. Collapse/expand shows ◀/▶ arrows and
  edit shows a pencil; the sidebar toggle now uses ◀/▶ too.
- **Bigger task-detail window** (more room for the description and diary), a roomier growable diary
  box (there was never a character limit — content is stored in full), and pasted **images scale to
  the text box width** — chat images use the (narrower) history width so there's no horizontal scroll
  and the entry's edit/delete buttons stay visible.

### Removed
- **Subtasks / checklists** (introduced in 0.5.0). The whole feature was removed — the in‑card
  checklist, the card `☑ done/total` badge, and the `subtasks` table with its DB helpers — per a
  product decision to drop that approach for now.

### Fixed
- **Windows taskbar icon.** The window/app/tray icon is resolved by absolute path and prefers the
  multi‑resolution `ekin_icon.ico`, so launching from the desktop shortcut (a different working
  directory) no longer falls back to Python's generic taskbar icon.

## [0.5.0] - 2026-07-29

### Added
- **Subtasks / checklists inside a task.** Each task detail dialog has a checklist section — add,
  tick, rename and delete items — that persists immediately. Board cards show a **`☑ done/total`**
  progress badge (green when complete). New `subtasks` table + `database` helpers (`create_subtask`,
  `get_subtasks`, `set_subtask_done`, `update_subtask_title`, `delete_subtask`,
  `get_subtasks_progress_bulk`); `get_tasks` exposes `subtasks_done`/`subtasks_total`; copying a
  column/board carries subtasks; deleting a task cascades them.
- **Global search & filter.** A 🔍 button in the sidebar (and **Ctrl+F**) opens a search dialog that
  filters tasks across all boards by **text** (title/description), **board**, **tag**, and
  **only-with-due-date**; clicking a result jumps to its card. New `database.search_tasks()`.
- **CI workflow** (`.github/workflows/ci.yml`): runs `ruff` and `pytest` (Python 3.10–3.12, with the
  Qt system libraries PySide6 needs on Linux) on every push to `main` and on pull requests.
- `ruff` as a dev dependency with a high-signal lint config (`E4/E7/E9/F`); cleaned up the handful of
  unused imports / variables it surfaced.

## [0.4.0] - 2026-07-22

### Added
- **Overdue tasks in the deadline bell.** The bell popup now shows an **"ATRASADAS"** group
  (highlighted) for tasks past their due date, above **HOY** and **MAÑANA**, and the count badge
  includes them. Backed by querying everything due on or before tomorrow.
- **Drag a task in the calendar to reschedule it.** Calendar chips are draggable; dropping one on
  another day updates that task's due date (new `database.update_task_due_date`) and re-syncs the
  bell and the `.ics` feed automatically.
- **"Subscribe in Google" helper in Ajustes.** A field for the public `.ics` URL plus a button that
  saves it (`ics_public_url` setting), copies it to the clipboard and opens Google Calendar's
  *add-by-URL* page — automating the manual step users trip on.
- **Automatic database backups on startup.** New `backups.py` writes a consistent SQLite snapshot to
  a `backups/` folder before any schema migration runs, keeping the 5 most recent. No-op on first run.

### Changed
- **`database.py` `db_path` handling is now uniform.** All ~38 data-access functions resolve
  `db_path` at call time (`db_path=None` -> `db_path or DB_NAME`) instead of freezing `DB_NAME` at
  import. Reassigning `database.DB_NAME` is now honored everywhere, and the whole layer is testable
  against temporary databases without monkeypatching. `ics_export.build_ics/export_ics` too.
- Renamed `TaskListArea.layout` to `list_layout` so it no longer shadows `QWidget.layout()`.

### Fixed
- **Same-column drag reorder off-by-one.** The hidden dragged card was counted when computing the
  drop index, mismatching the target list (which excludes the moved card) and misplacing a card
  dropped below its original slot. The index is now computed in the non-dragged card space
  (extracted to `widgets.compute_drop_index`, unit-tested).
- **iCalendar line folding** could emit continuation lines 1 octet over the 75-octet RFC 5545 limit
  (the leading continuation space wasn't counted); continuations are now capped at 74 content octets.
- Removed a dead `#TaskCardDueDate` object name that had no QSS rule (the label is styled inline).

## [0.3.2] - 2026-07-17

### Fixed
- The board header now shows the selected board's real name instead of a static "Mi Tablero".

### Changed
- Tag loading is batched to remove an N+1 query: `get_tasks` and `get_scheduled_tasks` now fetch all
  tags in a single query via the new `get_task_tags_bulk()` helper (cheaper board/calendar/bell loads).
- Test suite aligned with the current tag shape (`category_id`) and extended with coverage for the
  scheduled-task queries, `app_settings`, `get_task_board_id`, and bulk tag loading.

## [0.3.1] - 2026-07-14

### Added
- Safety-net timer that re-writes the synced `.ics` every 5 minutes while the app is open (in
  addition to the existing change-driven writes). It only writes when the content actually changed,
  so it never produces redundant cloud re-uploads.

## [0.3.0] - 2026-07-13

### Added
- Sidebar utility bar with a live date/time clock, a deadline **bell**, and a **calendar** button.
- Deadline bell: a popup listing tasks due **today or tomorrow across all boards**, grouped by day,
  with a count badge on the bell. Clicking a task jumps to its board and opens the card.
- Native **Windows notifications** (via a system-tray icon) for tasks due today, plus a tray menu
  (Open / Quit) and double-click-to-restore.
- **Monthly calendar view** (toggled from the sidebar) showing tasks by due date, with month
  navigation, a "Hoy" shortcut, and per-task chips that open the card; **✖ Cerrar** returns to the
  board and **⚙ Ajustes** configures sync.
- **Calendar sync via iCalendar (.ics)**: a one-off export plus an **auto-updated feed** that Ekin
  keeps current and you subscribe to from Google Calendar, Apple Calendar or Outlook. Events carry a
  stable per-task `UID` with `SEQUENCE`/`LAST-MODIFIED`, and the file is deterministic (it only
  changes when task data changes) to avoid spurious re-uploads in cloud-synced folders.
- `app_settings` key/value table to persist the `.ics` sync path.
- README guide: "Syncing Your Due Dates with Google Calendar, Apple & Outlook".

### Changed
- New database helpers: `get_scheduled_tasks`, `get_task_board_id`, `get_setting`/`set_setting`.
  These (and the new scheduled query) resolve `DB_NAME` at call time, so the module's DB path is
  actually overridable instead of being frozen at import.
- `board_view` now emits a `data_changed` signal after (re)loading, which keeps the deadline bell,
  the calendar view, and the synced `.ics` file in sync automatically.

## [0.2.0] - 2026-07-13

### Added
- Drag columns by their title to reorder them within a board, or drop them onto another board's
  button in the sidebar to move them there — replacing the old "Move to another board..." dialog.
- Structured, permanent tags: tags are a reusable Category + Value pair (e.g. "Prioridad: Alta"),
  rendered as "CATEGORÍA: VALOR" pills everywhere. A task holds a single value per tag; clicking a
  pill in the task detail edits its value in place, or sets it to "Ninguno" to hide/remove it (the
  card only shows tags that have a value). A dedicated tag manager lets you create/rename/delete
  tags and pre-define each one's palette of values with colors; assigning picks from that catalog.
- Basic rich text formatting (bold, italic, bullet lists) for both the task description and the
  diary/chat entries, via a small toolbar above each editor. The Bold/Italic buttons are properly
  styled with an active-state highlight and stay in sync with the native Ctrl+B / Ctrl+I shortcuts.
  Typing `* `, `- ` or `+ ` at the start of a line auto-creates a bullet list (and `1. ` / `1) ` a
  numbered list); pressing Enter on an empty item exits the list.
- Sidebar header now shows the Ekin logo next to "EKIN" instead of plain "EKIN KANBAN" text.

### Changed
- `database.set_task_tags()` now takes a list of tag-value ids instead of `{"text", "color"}`
  dicts; `get_task_tags()`/`get_tasks()`/`get_task()`/`get_tag_value()` return `{"tag_value_id",
  "category_id", "category", "value", "color"}`. Existing freeform tags are migrated automatically
  into a "General" category on upgrade.
- Tag catalog is now managed explicitly: added `create_tag_category`/`rename_tag_category`/
  `delete_tag_category`, `create_tag_value`/`update_tag_value`/`delete_tag_value`, and
  `value_exists_in_category` in `database.py`. Values and colors are defined up front in the tag
  manager rather than created on the fly while assigning.
- Diary entries are now stored as rich HTML (from the new formatting toolbar) instead of plain text.

### Fixed
- Desktop shortcut created by `install.ps1` now uses a proper multi-resolution `ekin_icon.ico`
  instead of a `.png` (Windows `.lnk` shortcuts don't render `.png` icons reliably, causing the
  generic file icon to show instead).
- Set an explicit Windows `AppUserModelID` on startup so the running app is not grouped under
  `pythonw.exe`'s generic icon in the taskbar.

## [0.1.0] - 2026-07-10

### Added
- Initial Kanban board: boards, columns, tasks, and per-task journal (diario) with SQLite persistence.
- Due dates, multiple colored tags per task, and copy/move columns & boards between each other.
- Collapsible sidebar and per-board accent colors.
- PowerShell one-click installer (`install.ps1`) and a silent git-based auto-updater on startup.
- Formal dependency management via `pyproject.toml` (PySide6 pinned, `pytest` as a `dev` extra).
- `pytest` test suite covering `database.py` (CRUD, cascading deletes, drag-and-drop repositioning, board/column copy-move).
- Version now shown in the application window title.

### Changed
- Consolidated the duplicated `hex_to_rgb` helper (previously repeated in `sidebar.py`, `board_view.py`, and `widgets.py`) into `styles.py`.
