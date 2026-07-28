# Technical Design Document — Wave 2, Part 1: Subtasks / Checklists

**STATUS: PART 1 COMPLETE (on branch, PR open) — Part 2 (global search) pending**
**Author:** Architect persona (Trinity Stack Protocol)
**Date:** 2026-07-28
**Target:** v0.5.0 (Part 1 of 2 — checklists now, global search next). Feature **branch**
`feat/0.5.0-subtasks` → PR (UI needs manual verification, so not straight to main per the
"branch only if untested" rule).

---

## 1. Mission
Add **subtasks / checklists** inside a task card: a checklist in the task detail dialog (add /
toggle / rename / delete items) plus a progress badge on the board card. Fully covered at the DB
layer by headless tests; the Qt interactions are validated by construction + a manual pass before merge.

---

## 2. Scope
### A. Data layer (`database.py`) — fully headless-testable
- **A1** New `subtasks` table + idempotent migration in `init_db`:
  `id, task_id FK→tasks ON DELETE CASCADE, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0,
  position INTEGER NOT NULL`.
- **A2** Helpers (all `db_path=None` → `db_path or DB_NAME`):
  - `create_subtask(task_id, title, db_path=None) -> id` (position = max+1)
  - `get_subtasks(task_id, db_path=None) -> [dict]` ordered by position (`done` as 0/1 int)
  - `set_subtask_done(subtask_id, done, db_path=None)` (bumps parent `tasks.updated_at`)
  - `update_subtask_title(subtask_id, title, db_path=None)`
  - `delete_subtask(subtask_id, db_path=None)`
  - `get_subtasks_progress_bulk(task_ids, db_path=None) -> {task_id: (done, total)}` (single query,
    N+1-free — mirrors `get_task_tags_bulk`)
- **A3** `get_tasks` sets `t["subtasks_done"]` / `t["subtasks_total"]` via the bulk helper.
- **A4** `copy_column_to_board` and `copy_board` duplicate each task's subtasks (like logs/tags).

### B. UI
- **B1** `detail_dialog.py`: a **"☑️ Subtareas"** section in the left panel (between Etiquetas and the
  stretch): a progress label (`hechas/total` + %), a scrollable item list (checkbox + inline-editable
  title + `×` delete), and an add row (`QLineEdit` + **➕ Añadir**). Changes persist **immediately**
  (like diary logs), so they survive Cancel and don't depend on "Guardar".
- **B2** `widgets.py :: TaskCard`: show a small **"☑ done/total"** badge (in the due row) when
  `subtasks_total > 0`; green when complete.

### C. Tests (`tests/test_database.py`)
- subtasks CRUD + ordering, `done` toggle, cascade on task delete, `get_subtasks_progress_bulk`
  (grouping + empty input), `get_tasks` exposes progress, and copy-duplication of subtasks.

### Out of scope (Part 2 / later)
Global search & filter (next PR), drag-to-reorder subtasks, converting a subtask into a task.

---

## 3. Contracts / decisions
- `done` stored as INTEGER 0/1 (SQLite has no bool); helpers accept truthy and store `1 if done else 0`.
- Immediate persistence in the dialog avoids a save-time diff of checklist state; consistent with logs.
- Card badge reads `subtasks_done/subtasks_total` already loaded by `get_tasks` (no extra query per card).

## 4. Task checklist
### Coder
- [x] A1 schema + migration
- [x] A2 helpers (+ `get_subtasks_progress_bulk`)
- [x] A3 wire into `get_tasks` (`subtasks_done`/`subtasks_total`)
- [x] A4 duplicate in copy_column_to_board / copy_board
- [x] B1 detail_dialog checklist section (immediate persistence; `clicked` not `toggled`)
- [x] B2 TaskCard progress badge (`☑ n/m`, green when complete)
### Tester
- [x] C subtasks DB tests (7 new); full suite green (53); ruff clean; headless UI smoke
### Docs/Release
- [x] CHANGELOG [Unreleased]; open PR (no version bump — Part 2 completes 0.5.0)

---

## QA Report (Tester)

**Result: PASS.** `pytest` → **53 passed** (+7 subtask tests: CRUD, ordering, done-toggle, cascade
on task delete, `get_subtasks_progress_bulk` grouping/empty, `get_tasks` progress exposure, copy
duplication). `ruff check .` clean. Headless UI smoke drove `TaskDetailDialog`: add ×2 → toggle →
progress label "1/2 · 50%" → rename → empty-rename restores prior title → remove; `TaskCard` badge
renders `☑ 1/2` for a task with subtasks and stays empty/hidden for one without.

**Residual (manual, GUI-only):** checkbox click feel, inline-edit focus behaviour, and the scroll
area at many items weren't driven by a live event loop — validated by construction. Manual pass
before merge recommended.

## 5. Acceptance
1. `pytest` green incl. new subtask coverage; `ruff` clean.
2. Checklist items add/toggle/rename/delete and persist across dialog reopen.
3. Card shows `☑ n/m` when a task has subtasks.
4. Copying a column/board carries subtasks; deleting a task cascades them.
</content>
