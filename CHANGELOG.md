# Changelog

All notable changes to Ekin Kanban are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
