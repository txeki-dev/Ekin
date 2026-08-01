# Technical Design Document — v0.6.0 (Themes A + B + C)

**STATUS: IN PROGRESS**
**Author:** Architect persona (Trinity Stack Protocol)
**Date:** 2026-07-30
**Branch:** `feat/0.6.0` → PR (UI-heavy; merge cuts the release). Then: validate all, discuss
readability before **D** (distribution).

---

## Mission
Deliver the v0.6.0 wave: **A · Calendar depth**, **B · Power features**, **C · Polish & platform**.
Build DB/logic-testable pieces first (headless-covered), UI pieces after (built + smoke-tested).

## Scope & sequencing (sub-waves)

### Sub-wave 1 — Data foundations (headless-testable)
- **C1 Board archiving** — `boards.archived` flag (+ migration); `set_board_archived`,
  `get_boards(include_archived=False)`; sidebar hides archived, with a toggle to view/unarchive.
- **C2 Export / report** — new `export.py`: boards → JSON, CSV (tasks), and a Markdown project report.
  Pure functions over the DB; a menu/settings entry to save the file.
- **B1 Recurring tasks** — `tasks.recurrence` (`none|daily|weekly|monthly`, + migration). When a dated
  recurring task is marked done/advanced, spawn the next occurrence at the next date. DB helper
  `advance_recurrence` / `complete_recurring_task`.

### Sub-wave 2 — Calendar depth (A)
- **A1 Time-of-day due + `VALARM`** — allow an optional `HH:MM` on due dates (store `due_date` +
  `due_time`), surface in the picker/card/bell; emit timed `VEVENT` + `VALARM` in `ics_export`.
- **A2 Calendar filter by board + legend** — a board filter control + colored legend on the calendar.
- **A3 Week/day view** — a week (and optionally day) layout toggle in the calendar.
- **A4 Per-board `.ics` feeds** — `build_ics(board_id=…)` + per-board sync path setting.

### Sub-wave 3 — Power + polish UI (B, C)
- **B2 Keyboard shortcuts** — `Esc` closes dialogs, `Ctrl+N` new task, arrow nav on the board.
- **B3 Undo/redo** — an undo stack for destructive actions (delete task/column/board), `Ctrl+Z`/`Ctrl+Y`.
- **B4 Attachments / links** — attach URLs (and/or file paths) to a card.
- **C3 Light theme + toggle** — a light palette in `styles.py` + a toggle, persisted in `app_settings`.
- **C4 Settings screen** — persist window size/position, theme, notification prefs, sync path.

### Ongoing tech debt (fold in opportunistically)
Closing-connection context manager; `data_changed` only on real mutations; centralize duplicated
inline stylesheets; headless Qt smoke tests.

## Contracts / decisions
- Schema changes are additive with idempotent `ALTER TABLE ... ADD COLUMN` migrations (like prior waves).
- `due_time` stored as `TEXT` `HH:MM` (nullable); all-day when null (keeps back-compat with 0.5.x data).
- Recurrence advances by calendar unit; weekly = +7 days, monthly = same day next month (clamped).
- Export is a pure module (no Qt) so it's fully unit-tested.
- Light theme: keep `styles.COLORS`/`QSS` as the dark default; add a `build_qss(theme)` + palette map.

## Acceptance (per sub-wave)
Each feature ships with headless tests where it has a DB/logic surface; UI is smoke-tested by
construction. Full suite green + ruff clean at each commit. `version.py` → 0.6.0 at the end; CHANGELOG
`[0.6.0]` grouped by theme; README + context + diary updated.

## Task checklist
### Sub-wave 1 — DONE
- [x] C1 board archiving (db + sidebar: right-click archive, "🗄 Archivados" toggle)
- [x] C2 export/report module (`exporter.py`) + sidebar "⬇ Exportar" menu (JSON/CSV/MD)
- [x] B1 recurring tasks (schema + `next_occurrence`/`advance*`; detail-dialog combo; 🔁 card badge;
  startup `advance_overdue_recurring`)
### Sub-wave 2 — DONE
- [x] A1 time-of-day (`due_time`) + `VALARM` in ics; detail-dialog time field; card shows time
- [x] A2 calendar board filter + colored legend
- [x] A3 month/week/day view modes
- [x] A4 per-board `.ics` (`build_ics(board_id=…)`) + per-board export picker in settings
### Sub-wave 3 — DONE
- [x] B2 shortcuts (Ctrl+N new task; Ctrl+Z/Ctrl+Y undo/redo; Esc closes dialogs by default)
- [x] B3 undo/redo (snapshot/restore task·column·board; `undo.py` UndoManager; wired into deletes)
- [x] B4 attachments/links (`task_links` + helpers; detail-dialog section; 🔗 card badge)
- [x] C3 light theme (`styles.build_qss`/`set_theme` + LIGHT palette; live apply + persist)
- [x] C4 settings screen (`settings_dialog.py`: theme, notifications; window geometry persisted)
### Close-out
- [x] version 0.6.0, CHANGELOG/README/context/diary, full validation (64 tests, ruff clean), PR
</content>
