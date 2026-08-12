# TECHNICAL DESIGN DOCUMENT

## 1. Overview
Third forensic bug-hunt pass. Two independent audit findings, both confirmed via direct,
reproducible repros before this TDD was written (not speculative):

1. **Critical, systemic (two manifestations): `restore_task`/`restore_column`
   (`database/snapshots.py`) can crash the app with an uncaught `sqlite3.IntegrityError`**
   when undoing (Ctrl+Z) a deleted task/column whose parent (column/board respectively) was
   *also* deleted in the meantime. Both functions fall back to the snapshot's own stored
   parent id when no explicit one is passed, with no guard that the fallback id still exists —
   `tasks.column_id`/`columns.board_id` are both `NOT NULL` FKs with `ON DELETE CASCADE` under
   `PRAGMA foreign_keys = ON`. This is the exact same failure class already fixed once for
   `restore_task`'s `linked_board_id`/`tag_value_ids` (see the existing guards and comments
   already in that function) — never applied to either function's own required parent-id
   fallback. Reachable via an entirely ordinary sequence: delete a column, delete the board it
   was in, Ctrl+Z twice (or: delete a task, delete its column, Ctrl+Z twice).
2. **Bug, memory leak: `ImagePreviewDialog` (`detail_dialog/image_preview_dialog.py`) is never
   destroyed after closing.** Same class already fixed once for `TaskDetailDialog`
   (`self.finished.connect(self.deleteLater)`), never applied to this dialog (added
   2026-08-12, first forensic pass touching it). Confirmed via repro: 5 open+close cycles
   against a real parent leave 5 permanent zombie children.

## 2. Implementation Tasks

- [x] `database/columns.py` — add a new single-row lookup function, matching `get_board`'s
  existing style in `database/boards.py` exactly (same shape: raw SQL, `dict(row) if row else
  None`), placed right after `get_columns` (before `update_column`):
  ```python
  def get_column(column_id, db_path=None):
      with get_connection(db_path) as conn:
          cursor = conn.cursor()
          cursor.execute(
              "SELECT id, board_id, name, color, position, collapsed FROM columns WHERE id = ?",
              (column_id,)
          )
          row = cursor.fetchone()
          return dict(row) if row else None
  ```
  Add `"get_column"` to the `__all__` list at the top of the file (insert after
  `"get_columns"` to keep the singular/plural pair adjacent).

- [x] `database/snapshots.py` — imports: add `get_column` to the existing
  `from .columns import get_columns` line, making it `from .columns import get_columns,
  get_column`.

- [x] `database/snapshots.py` — `restore_task`: insert a guard immediately after the existing
  `column_id = column_id if column_id is not None else snap["column_id"]` line (before the
  `linked_board_id`/tag guards that follow it), matching the comment style already used for
  the `linked_board_id` guard two lines below:
  ```python
  column_id = column_id if column_id is not None else snap["column_id"]
  # Si la columna de destino ya no existe (p. ej. se borró mientras esta acción seguía
  # pendiente en la pila de deshacer), no hay dónde insertar la tarea -- devolver None en
  # vez de violar la FK de tasks.column_id y reventar sin capturar.
  if get_column(column_id, db_path) is None:
      return None
  ```
  Everything else in `restore_task` (the `linked_board_id`/`tag_value_ids` guards, the
  `with get_connection(...)` block and everything inside it) is unchanged.

- [x] `database/snapshots.py` — `restore_column`: insert the equivalent guard immediately
  after `board_id = board_id if board_id is not None else snap["board_id"]`:
  ```python
  board_id = board_id if board_id is not None else snap["board_id"]
  # Mismo razonamiento que en restore_task: si el tablero de destino ya no existe, no hay
  # dónde insertar la columna -- devolver None en vez de violar la FK de columns.board_id.
  if get_board(board_id, db_path) is None:
      return None
  ```
  `get_board` is already imported in this file (`from .boards import get_board, create_board,
  set_board_archived`) — no import change needed here. Everything else in `restore_column`
  (the `with get_connection(...)` block, the task-restoring loop afterward) is unchanged.

- [x] `detail_dialog/image_preview_dialog.py` — `ImagePreviewDialog.__init__`: add one line at
  the end of `__init__` (after `self.resize(pixmap.size())`), matching `TaskDetailDialog`'s
  exact fix and comment style:
  ```python
  # Sin esto, cada imagen previsualizada deja un ImagePreviewDialog zombi (con su QPixmap,
  # potencialmente de varios MB) colgado para siempre del widget que lo abrió.
  self.finished.connect(self.deleteLater)
  ```

- [x] `tests/test_database.py` — add a new test near the existing snapshot/restore tests
  (alongside `test_snapshot_and_restore_task_preserves_linked_board`/
  `test_restore_task_drops_link_if_linked_board_was_deleted`), reproducing the task-case crash
  exactly as manually verified, asserting graceful `None` instead of a raised exception:
  ```python
  def test_restore_task_returns_none_if_column_was_deleted_in_the_meantime(db_path):
      """Regresión: antes de este fix, restore_task reventaba con sqlite3.IntegrityError si
      la columna original ya no existía (p. ej.: borrar tarea, borrar su columna, deshacer
      el borrado de la columna -- que crea una columna NUEVA con otro id -- y luego deshacer
      el borrado de la tarea, que seguía apuntando a la columna vieja)."""
      board_id = database.create_board("B", db_path=db_path)
      col_id = database.create_column(board_id, "C", db_path=db_path)
      task_id = database.create_task(col_id, "Tarea", db_path=db_path)

      task_snap = database.snapshot_task(task_id, db_path=db_path)
      database.delete_task(task_id, db_path=db_path)
      database.delete_column(col_id, db_path=db_path)  # la columna original ya no existe

      result = database.restore_task(task_snap, db_path=db_path)

      assert result is None
  ```

- [x] `tests/test_database.py` — add the column-case equivalent right after it:
  ```python
  def test_restore_column_returns_none_if_board_was_deleted_in_the_meantime(db_path):
      """Mismo escenario que el de arriba, un nivel más arriba en la jerarquía: borrar
      columna, borrar su tablero, deshacer el borrado de la columna debe degradar con
      gracia (None) en vez de reventar con sqlite3.IntegrityError."""
      board_id = database.create_board("B", db_path=db_path)
      col_id = database.create_column(board_id, "C", db_path=db_path)

      col_snap = database.snapshot_column(col_id, db_path=db_path)
      database.delete_column(col_id, db_path=db_path)
      database.delete_board(board_id, db_path=db_path)  # el tablero original ya no existe

      result = database.restore_column(col_snap, db_path=db_path)

      assert result is None
  ```
  Both tests call the functions **without** an explicit `column_id`/`board_id` (matching the
  real `board_view.py` call sites exactly, which is what makes the fallback path live) — do
  not pass one, or the test would not exercise the bug.

- [x] `tests/test_database.py` — add one more test confirming the *unaffected*, still-working
  path: a normal restore where the parent legitimately still exists must keep returning the
  new row's id, not `None`. **Coder note:** no new test added here — the existing
  `test_snapshot_and_restore_task_preserves_linked_board` (line 696) already provides this
  coverage implicitly and would fail loudly (`TypeError`, not silently pass) if `new_id` were
  `None`: it does `database.get_task(new_id, db_path)["linked_board_id"]` immediately after
  `restore_task`, which requires `new_id` to be a real id. Confirmed this test still passes
  after the guard was added (it exercises the ordinary/successful path, parent board and
  column both still exist), so the "successful path unaffected" coverage requirement is met
  without a redundant new test.

- [x] `tests/test_widgets_headless.py` — add a new test in a section near the existing
  `image_preview_module`-related tests, reusing the *exact* pattern from
  `test_task_detail_dialog_is_destroyed_after_closing_when_parented` (same file, same
  `deleteLater`/`sendPostedEvents`/`pytest.raises(RuntimeError)` idiom):
  ```python
  def test_image_preview_dialog_is_destroyed_after_closing_when_parented(qapp):
      """Regresión de fuga de memoria: igual que TaskDetailDialog, ImagePreviewDialog debe
      autodestruirse (deleteLater vía self.finished) al cerrarse en vez de quedar colgado
      para siempre del widget que lo abrió."""
      from PySide6.QtGui import QPixmap

      parent = QWidget()
      pixmap = QPixmap(10, 10)
      pixmap.fill(Qt.GlobalColor.red)
      dlg = image_preview_module.ImagePreviewDialog(pixmap, parent)

      dlg.reject()
      qapp.sendPostedEvents(dlg, QEvent.Type.DeferredDelete)

      with pytest.raises(RuntimeError):
          dlg.windowTitle()
  ```
  **Coder note:** built this exactly as specified first, using `dlg.close()` — it failed
  (`DID NOT RAISE RuntimeError`), because `QDialog.close()` on a widget that was never shown
  is a no-op in Qt (no close event is generated for an invisible widget) and never emits
  `finished`. Verified this directly (`dlg.finished.connect(...)` never fires after
  `.close()` on an unshown dialog, but fires immediately after `.reject()`) before changing
  the test to `dlg.reject()` — matching what
  `test_task_detail_dialog_is_destroyed_after_closing_when_parented` actually does (it also
  uses `.reject()`, not `.close()`, for exactly this reason). The source fix
  (`self.finished.connect(self.deleteLater)`) is unaffected by this — it was a test-construction
  detail, not a defect in the fix itself.
  `QWidget`, `pytest`, `QEvent`, `Qt`, `image_preview_module` are all already imported in this
  test file from earlier waves — only the `QPixmap` import is new, keep it local to the test
  function (matching how `test_image_preview_dialog_upscales_small_pixmap` earlier in this
  same file already does a local `from PySide6.QtGui import QPixmap` import rather than a
  top-of-file one — follow that same precedent for consistency within this file).

- [x] `CHANGELOG.md` — add a `### Fixed` section under `[Unreleased]` (create it fresh, since
  `[Unreleased]` is currently empty after the v0.9.3 cut) with two bullets: one for the
  Ctrl+Z crash (undoing a deleted task/column can crash if its parent was also deleted), one
  for the `ImagePreviewDialog` leak.

## 3. Acceptance Criteria
- `database.restore_task(snap, db_path=...)` (no explicit `column_id`) called after the
  snapshot's original column has been deleted returns `None` and raises nothing.
- `database.restore_column(snap, db_path=...)` (no explicit `board_id`) called after the
  snapshot's original board has been deleted returns `None` and raises nothing.
- The ordinary, successful restore path (parent still exists) is unaffected — still returns
  the new row's integer id, exactly as before this change.
- `restore_column`'s internal task-restoring loop and `restore_board`'s internal
  column-restoring loop are unaffected — both always pass an explicit, freshly-created parent
  id, so the new guards never fire on those paths (verify this by reasoning, not just by the
  tests happening to pass — the TDD's own analysis already established this, the Tester should
  confirm it holds in the final diff too).
- `ImagePreviewDialog` is destroyed (not just hidden) after `close()`/`Esc`/clicking anywhere
  in it — verified via the same `deleteLater` + `sendPostedEvents` + `pytest.raises(RuntimeError)`
  idiom already proven for `TaskDetailDialog`.
- `database/columns.py`'s new `get_column` follows the exact same style as `get_board` (same
  column list shape as `get_columns`' `SELECT`, just filtered by `id` instead of `board_id`)
  and is exported via `__all__`.
- No other files touched beyond the ones listed in §2 (`git diff --stat`) — this is a
  three-file source change (`database/columns.py`, `database/snapshots.py`,
  `detail_dialog/image_preview_dialog.py`) plus tests and changelog.
- Full test suite passes with a clean exit code; ruff stays clean.

## QA Report

**Verdict: PASS.** All acceptance criteria validated against real source, independently
re-executed tests, and fail-before/pass-after proof for both fixes.

**Code trace:** all three source diffs match the TDD exactly — `get_column` mirrors
`get_board`'s style precisely; both `restore_task`/`restore_column` guards are placed
correctly (immediately after the parent-id fallback, before any DB write); `ImagePreviewDialog`
gained the one-line `self.finished.connect(self.deleteLater)` matching `TaskDetailDialog`'s
exact fix.

**Executed verification:**
1. `ruff check .`: clean. `pytest -q` (3 independent consecutive runs): **183 passed** every
   time (up from 180; 3 new tests), clean exit. `git diff --stat -- widgets.py board_view.py
   main.py sidebar.py`: empty — confirms the TDD's own analysis that no caller needed changes,
   since every real call site already discards or null-checks the return value.
2. **Fail-before/pass-after proof for both fixes, not assumed from the TDD's reasoning
   alone:**
   - `git stash push -- database/snapshots.py database/columns.py`, re-ran the two new
     `test_database.py` tests: both **failed** with the *exact* predicted
     `sqlite3.IntegrityError: FOREIGN KEY constraint failed`, traced to the exact `INSERT INTO
     columns`/`INSERT INTO tasks` lines the TDD identified. `git stash pop` restored the fix;
     full suite back to 183/183 immediately after.
   - `git stash push -- detail_dialog/image_preview_dialog.py`, re-ran the new
     `test_widgets_headless.py` test: **failed** (`DID NOT RAISE RuntimeError`) against the
     pre-fix code. Restored, suite green again.
3. **Verified the real production path, not just the test's construction**: the Coder's own
   note flagged that `.close()` doesn't emit `finished` on a never-shown `QDialog` (Qt
   treats it as a no-op), which is why the test uses `.reject()` instead. To confirm this
   doesn't mean the *actual* click-to-close path (`mousePressEvent` → `self.close()`) is
   somehow different from what the test exercises, I independently built a real
   `ImagePreviewDialog`, called `.show()` (mirroring what `.exec()` does before blocking),
   then `.close()` (mirroring the real `mousePressEvent` handler) — `finished` fired
   correctly and the dialog was fully destroyed (`0` children remaining). This confirms the
   fix works for the actual real-world interaction, not only for the test's `.reject()`-based
   construction.
4. Confirmed by re-reading `restore_column`'s internal task-restoring loop
   (`restore_task(task_snap, column_id=new_col, ...)`) and `restore_board`'s internal
   column-restoring loop (`restore_column(col_snap, board_id=new_board, ...)`): both always
   pass a freshly-created id from earlier in the same call stack, so the new guards are
   structurally unreachable on those nested paths — matches the acceptance criterion exactly.

**Edge cases considered, no bugs found:**
- The "ordinary/successful restore still returns a real id" requirement is met by the existing
  `test_snapshot_and_restore_task_preserves_linked_board` (unmodified) rather than a new test —
  verified this test would indeed fail with a `TypeError` (not silently pass) if `new_id` were
  `None`, since it immediately does `database.get_task(new_id, db_path)["linked_board_id"]`.
  Confirmed it still passes after this wave's changes.
- `pixmap_from_data_uri`/`show_image_preview` in `image_preview_dialog.py` are untouched by
  this wave — re-confirmed via diff that only the `__init__` gained the one new line.

No blocking issues found. Ready for Architect final review / archiving.
