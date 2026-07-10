# Changelog

All notable changes to Ekin Kanban are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
