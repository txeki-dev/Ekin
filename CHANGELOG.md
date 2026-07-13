# Changelog

All notable changes to Ekin Kanban are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Drag columns by their title to reorder them within a board, or drop them onto another board's
  button in the sidebar to move them there — replacing the old "Move to another board..." dialog.
- Structured tags: instead of freeform per-tag text, tags are now a Category + Value pair (e.g.
  "Prioridad: Alta") drawn from a reusable catalog. Picking an existing value reuses its color;
  typing a new one creates it on the fly. Rendered as "CATEGORÍA: VALOR" pills everywhere.
- Basic rich text formatting (bold, italic, bullet lists) for both the task description and the
  diary/chat entries, via a small toolbar above each editor.
- Sidebar header now shows the Ekin logo next to "EKIN" instead of plain "EKIN KANBAN" text.

### Changed
- `database.set_task_tags()` now takes a list of tag-value ids instead of `{"text", "color"}`
  dicts; `get_task_tags()`/`get_tasks()`/`get_task()` return `{"tag_value_id", "category", "value",
  "color"}`. Existing freeform tags are migrated automatically into a "General" category on upgrade.
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
