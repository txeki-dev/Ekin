# TECHNICAL DESIGN DOCUMENT

## 1. Overview

Today, dropping a `TaskCard` onto a **collapsed** column (`ColumnWidget.collapsed == True`)
always lands the task at the bottom: `ColumnWidget.dropEvent` (widgets.py ~L700-708) emits
`collapsed_card_drop(task_id, column_id)`, and `BoardViewWidget.handle_collapsed_card_drop`
(board_view.py ~L500-504) unfolds the column then calls `handle_task_drop(task_id, column_id,
10**9)` — a deliberately oversized position that `handle_task_drop` clamps to the end.

We're adding a **hover-to-expand**: if the drag hovers over a collapsed column for
`ColumnWidget.HOVER_EXPAND_MS` (650 ms) without leaving, the column expands automatically so the
user can pick a real drop position, exactly like any column that started out expanded — the
existing `compute_drop_index` / `TaskListArea.dropEvent` / `task_dropped` machinery is reused
untouched.

The expansion is **temporary**: if the drag ends (dropped elsewhere, dropped on a *different*
collapsed column that itself hover-expands, or cancelled) without a real drop landing inside the
hover-expanded column, the column re-collapses itself. If the drop *does* land inside it, it
simply stays expanded (same as manually unfolding it).

**Key design decision — how "drag ended without dropping here" is detected:** not via
`dragEnterEvent`/`dragLeaveEvent` bookkeeping (moving the cursor between a column's header and its
task list already fires spurious enter/leave pairs today purely for the existing hover-highlight
style, and piggybacking re-collapse logic on that would flicker). Instead we use the one moment
that is unambiguous and already proven reliable in this codebase: **`QDrag.exec()` returning**, in
`TaskCard.mouseMoveEvent`. Because every drop handler (`handle_task_drop`,
`handle_collapsed_card_drop`) runs *synchronously inside* the drop event, which itself runs inside
`QDrag.exec()`'s nested loop, by the time `exec()` returns we know with certainty whether a
matching drop already happened. A new `TaskCard.drag_ended` signal, emitted right after `exec()`
returns (in every case — drop or cancel), is the single checkpoint `BoardViewWidget` uses to decide
whether to re-collapse. This sidesteps the enter/leave-flicker risk entirely.

State that must survive across the whole drag (multiple `load_board()` reloads recreate every
`ColumnWidget`/`TaskCard` instance) lives on `BoardViewWidget` itself as `_hover_expanded_column_id`
(the column currently expanded *by hover*, or `None`).

Persisted DB state (`columns.collapsed`) is only ever touched with real value flips
(`True→False` on hover-expand, `False→True` on re-collapse) — a hover-expand that ends without a
drop returns the flag to exactly what it was before the drag started.

---

## 2. Implementation Tasks

- [x] `widgets.py` — imports: add `QTimer` to the existing `from PySide6.QtCore import Qt, Signal, QSize` line (→ `Qt, Signal, QSize, QTimer`).

- [x] `widgets.py` — `TaskCard` (class starts ~L153): add a new signal `drag_ended = Signal()`
  alongside the existing `clicked`/`board_link_clicked` signals. In `mouseMoveEvent`, right after
  the existing block
  ```python
  drop_action = drag.exec(Qt.MoveAction)

  # Si la tarea no se colocó en ningún lado (fue cancelada), volvemos a mostrarla
  if drop_action == Qt.IgnoreAction:
      self.show()
  ```
  add `self.drag_ended.emit()` as the next line — unconditionally, after the `if`, so it fires for
  every possible outcome (real drop, drop elsewhere, or cancel).

- [x] `widgets.py` — `ColumnWidget` (class starts ~L525): add class constant
  `HOVER_EXPAND_MS = 650` next to `COLLAPSED_WIDTH`/`EXPANDED_WIDTH`, and a new signal
  `hover_expand_requested = Signal(int)` (column_id) next to `collapsed_card_drop`.

- [x] `widgets.py` — `ColumnWidget.__init__` (~L538-547): before the `self.init_ui()` call, add:
  ```python
  self._hover_timer = QTimer(self)
  self._hover_timer.setSingleShot(True)
  self._hover_timer.setInterval(self.HOVER_EXPAND_MS)
  self._hover_timer.timeout.connect(self._on_hover_timeout)
  ```
  and a new method:
  ```python
  def _on_hover_timeout(self):
      """Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo
      suficiente: pide que se despliegue para poder elegir posición."""
      if self.collapsed:
          self.hover_expand_requested.emit(self.column_id)
  ```

- [x] `widgets.py` — `ColumnWidget.dragEnterEvent` (collapsed-only branch, ~L682-687): after
  `event.acceptProposedAction()` / `self.set_column_style(dragging=True)`, add
  `self._hover_timer.start()`.

- [x] `widgets.py` — `ColumnWidget.dragLeaveEvent` (~L695-698): inside the existing
  `if self.collapsed:` branch, add `self._hover_timer.stop()` (alongside the existing
  `self.set_column_style(dragging=False)`).

- [x] `widgets.py` — `ColumnWidget.dropEvent` (~L700-708): as the first line inside the
  `if self.collapsed and mime.hasFormat(...):` branch, add `self._hover_timer.stop()` — a quick
  drop before the hover threshold must not leave a stray timer that fires after the column is
  already gone (defensive; also correct hygiene since the widget is about to be replaced by
  `handle_collapsed_card_drop`'s reload).

- [x] `board_view.py` — `BoardViewWidget.__init__` (~L197-205): add
  `self._hover_expanded_column_id = None` (the column_id currently expanded *by hover* during an
  in-progress drag, or `None`).

- [x] `board_view.py` — `load_board` (~L370-392): in the per-column loop, alongside the existing
  `col_widget.collapsed_card_drop.connect(self.handle_collapsed_card_drop)`, add
  `col_widget.hover_expand_requested.connect(self.handle_hover_expand_requested)`. In the
  per-task-card loop, alongside the existing `card.board_link_clicked.connect(...)`, add
  `card.drag_ended.connect(self.finalize_hover_expand)`.

- [x] `board_view.py` — add three new methods near `handle_collapsed_card_drop` (~L500):
  ```python
  def handle_hover_expand_requested(self, column_id):
      """Expansión temporal (por hover durante un arrastre) de una columna
      plegada: permite elegir la posición de destino en vez de caer siempre al
      final. Si había otra columna expandida por hover en este mismo
      arrastre, se repliega primero."""
      if column_id == self._hover_expanded_column_id:
          return
      self._collapse_hover_expanded_column()
      database.set_column_collapsed(column_id, False, self.db_path)
      self._hover_expanded_column_id = column_id
      self.load_board(self.board_id, notify=False)

  def _collapse_hover_expanded_column(self):
      """Repliega la columna actualmente expandida por hover (si la hay) sin
      recargar el tablero — quien llama se encarga de recargar después."""
      if self._hover_expanded_column_id is not None:
          database.set_column_collapsed(self._hover_expanded_column_id, True, self.db_path)
          self._hover_expanded_column_id = None

  def finalize_hover_expand(self):
      """Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier
      arrastre de tarjeta (soltada donde sea, o cancelado). Si queda una
      columna expandida por hover sin haber recibido el drop, se repliega."""
      if self._hover_expanded_column_id is None:
          return
      self._collapse_hover_expanded_column()
      self.load_board(self.board_id, notify=False)
  ```

- [x] `board_view.py` — `handle_task_drop` (~L599-655): immediately before the final
  `self.load_board(self.board_id)` call, add:
  ```python
  if target_column_id == self._hover_expanded_column_id:
      self._hover_expanded_column_id = None
  ```
  This is what makes a *real* drop into the hover-expanded column stick (DB stays
  `collapsed=False`, tracking clears, so `finalize_hover_expand` becomes a no-op when
  `drag_ended` fires right after). No change needed in `handle_collapsed_card_drop`: it can only
  ever fire for a column that is still `collapsed=True` at drop time, which by construction can
  never be the column currently tracked in `_hover_expanded_column_id` (that one was flipped to
  `collapsed=False` the moment it started being tracked).

## 3. Acceptance Criteria

- Dragging a task over a collapsed column and holding it there for ≥ `HOVER_EXPAND_MS` expands
  the column; the user can then drop at any position within it via the normal
  `compute_drop_index`-driven mechanism (top, middle, bottom — not just the end).
- Dragging over a collapsed column and dropping **before** the hover threshold elapses still works
  exactly as before: task lands at the end of the column (regression check on the existing
  `collapsed_card_drop` → `handle_collapsed_card_drop` path).
- After a hover-expand, if the task is actually dropped inside that column: the column stays
  expanded afterwards (`columns.collapsed == 0` in the DB), regardless of what position was chosen.
- After a hover-expand, if the drag instead ends by dropping into a *different* column, or is
  cancelled entirely (e.g. released outside any valid drop target), the hover-expanded column
  re-collapses (`columns.collapsed == 1` in the DB) — i.e. its persisted state ends up identical to
  what it was before the drag started.
- If the user hover-expands column A, then — without dropping — hovers a *different* collapsed
  column B long enough to trigger its own hover-expand: A re-collapses immediately (not just at
  the end of the drag) and B expands. `BoardViewWidget._hover_expanded_column_id` tracks only one
  column at a time and always reflects the most recently hover-expanded one still pending.
- No new `data_changed` fan-out (bell/calendar/`.ics` refresh) is triggered by hover-expand or
  hover-re-collapse — both `load_board()` calls in `handle_hover_expand_requested` and
  `finalize_hover_expand` must pass `notify=False`. (`handle_task_drop`'s own final `load_board()`
  call is unchanged — it keeps its existing default `notify=True`, since a real task move is a
  real mutation; that pre-existing behavior is out of scope.)
- `ColumnWidget._hover_timer` never fires (no stray `hover_expand_requested`) once the drag has
  left the column (`dragLeaveEvent`) or already dropped on it (`dropEvent`) before the threshold —
  both call `self._hover_timer.stop()`.
- No regression in existing drag-and-drop behavior for already-expanded columns, column
  reordering, or column-to-board drag/drop — none of the touched code paths are shared with those.
- Full existing test suite (currently 80 tests) + ruff stay green. New tests to add (headless, no
  real `QDrag.exec()` — follow the existing `tests/test_widgets_logic.py` philosophy of testing
  DnD-adjacent logic deterministically rather than simulating native drag, since a real OS-level
  drag cannot run under pytest/CI):
  - New pytest module `tests/test_hover_expand.py` using the existing `qapp` (session-scoped
    `QApplication`, from `tests/conftest.py`) and `db_path` (temp initialized DB) fixtures:
    - Build a `BoardViewWidget(db_path=db_path)`, create a board with 1-2 columns via
      `database.create_column`, collapse one via `database.set_column_collapsed(col_id, True,
      db_path)`, call `board_view.load_board(board_id)`.
    - Call `board_view.handle_hover_expand_requested(col_id)` directly → assert
      `database.get_columns(board_id, db_path)` shows that column `collapsed == 0` and
      `board_view._hover_expanded_column_id == col_id`.
    - Call `board_view.finalize_hover_expand()` next (simulating "drag ended, no drop happened
      here") → assert the column is `collapsed == 1` again and
      `board_view._hover_expanded_column_id is None`.
    - Repeat, but this time call `board_view.handle_task_drop(task_id, col_id, 0)` (simulating "the
      drop actually landed here") *before* `finalize_hover_expand()` → assert
      `_hover_expanded_column_id` is already `None` after `handle_task_drop`, and that a
      subsequent `finalize_hover_expand()` call is a no-op (column stays `collapsed == 0`).
    - Two-columns case: hover-expand column A, then hover-expand column B (different column) →
      assert A is back to `collapsed == 1`, B is `collapsed == 0`, and
      `_hover_expanded_column_id == B`.
  - Extend `tests/test_widgets_logic.py` or add a small widget-level test (needs `qapp`) that
    constructs a `ColumnWidget` with `collapsed=True` column data, and verifies via direct calls
    (no real `QDrag`) that: calling `dragEnterEvent`/`dragLeaveEvent` with a minimal fake event
    object (only needs `.mimeData()` returning a `QMimeData` with
    `application/x-ekin-task-id` set, plus `.acceptProposedAction()`/`.ignore()` no-ops) starts and
    stops `self._hover_timer` (`.isActive()`); and that calling `_on_hover_timeout()` directly emits
    `hover_expand_requested` with the right `column_id` (via a connected test slot / list capture,
    no `QSignalSpy` needed).
  - App-launch smoke check (per this project's convention for every wave) after the change: launch
    against a seeded scratch DB, confirm the app starts and an ordinary (non-hover) collapsed-column
    drop still lands at the bottom as before.

## QA Report

**Code review (Read/Grep against this document's task list):** every `[x]` task in §2 was traced
against the actual current contents of `widgets.py` and `board_view.py` — signal names, method
bodies, and insertion points match this TDD exactly (imports, `TaskCard.drag_ended` +
its emission site, `ColumnWidget.HOVER_EXPAND_MS`/`hover_expand_requested`/`_hover_timer`/
`_on_hover_timeout`, the three `dragEnterEvent`/`dragLeaveEvent`/`dropEvent` timer start/stop
edits, `BoardViewWidget._hover_expanded_column_id` init, the two new signal connections in
`load_board`, the three new `BoardViewWidget` methods, and the guard added in `handle_task_drop`).
No deviation from the design found.

**Tests added:**
- `tests/test_hover_expand.py` (7 new tests) — pure logic against `BoardViewWidget`, no real
  `QDrag`: hover-expand persists + tracks; `finalize_hover_expand` re-collapses when nothing was
  dropped; `finalize_hover_expand` is a no-op with nothing pending; a real drop inside the
  hover-expanded column clears tracking and survives a subsequent `finalize_hover_expand`; a real
  drop in a *different* column leaves the hover-expanded one pending for `finalize_hover_expand` to
  close; switching hover-expand between two collapsed columns collapses the first immediately;
  hover-expanding the same column twice is a no-op.
- `tests/test_widgets_headless.py` (+4 new tests) — `ColumnWidget`-level, using real
  `QDragEnterEvent`/`QDragLeaveEvent`/`QDropEvent` objects (not simulated/fake), calling the event
  handlers directly (no native `QDrag.exec()`, consistent with why `compute_drop_index` is tested
  the same deterministic way): hover timer starts on drag-enter; stops on drag-leave; stops on drop
  before timeout (and the pre-existing `collapsed_card_drop` signal still fires — regression
  guard); `_on_hover_timeout` only emits while still `collapsed` (guards a late timer fire after
  the column was already unfolded by some other path).
- Full-app smoke script (`smoke_hover_expand.py`, run against a scratch DB via a temporary
  `database.DB_NAME` override, real `MainWindow` + real `BoardViewWidget`, not an isolated test
  double): confirmed (1) an ordinary fast drop on a collapsed column still lands at the end
  (pre-existing behavior, unchanged), (2) hover-expand followed by a real drop *inside* that column
  lets the task land at an arbitrary chosen position (first, not last) and the column stays
  expanded afterwards, (3) hover-expand followed by the drag ending via a drop in a *different*
  column re-collapses the hover-expanded column back to its original state. App launched, loaded a
  seeded board, and closed cleanly with no exceptions in all three scenarios.

**Bug found and fixed — test-code only, not production code:** the first draft of the
`ColumnWidget` event tests constructed each `QDragEnterEvent`/`QDropEvent` with an inline
`QMimeData()` temporary not stored in any variable. PySide6 does not keep the `QMimeData` Python
wrapper alive on the event's behalf; once the constructor call returned, the wrapper was garbage
collected and `event.mimeData()` came back as a type-erased plain `QObject` (no `.hasFormat`),
which crashed the whole pytest run with a native access-violation while pytest tried to format the
resulting `AttributeError`'s traceback (`saferepr` touching the now-invalid object). Fixed by adding
`_drag_enter_event()`/`_drop_event()` helpers that stash the `QMimeData` on the event as
`ev._keepalive` so its lifetime matches the event's. Confirmed root cause with an isolated repro
before and after the fix (`venv/Scripts/python.exe -c "..."`, run outside pytest). No production
code was touched for this — `widgets.py`/`board_view.py` never construct these events themselves;
Qt's native drag machinery keeps the real `QMimeData` alive via the `QDrag` object for the whole
drag, so this pitfall cannot occur in the shipped app, only in a synthetic test harness that builds
these events by hand.

**Suite results:** `pytest -q` (offscreen, whole suite): **91 passed** (was 80; +11 from this
wave). `ruff check .`: **all checks passed**, no new lint issues.

**Acceptance criteria (§3) — verified:**
- ✅ Hover ≥ `HOVER_EXPAND_MS` on a collapsed column expands it and a drop can land at any chosen
  position (smoke scenario 2: task inserted at index 0, not appended).
- ✅ A quick drop before the threshold still lands at the end (smoke scenario 1; regression test in
  `test_widgets_headless.py`).
- ✅ A real drop inside the hover-expanded column leaves it expanded (`collapsed == 0`) regardless
  of chosen position (smoke scenario 2; `test_hover_expand.py::test_real_drop_inside_hover_expanded_column_sticks`).
- ✅ Drag ending elsewhere (different column, or nothing pending) re-collapses the hover-expanded
  column back to its pre-drag state (smoke scenario 3;
  `test_finalize_without_drop_recollapses`, `test_drop_in_other_column_leaves_hover_expanded_pending_for_finalize`).
- ✅ Switching hover-expand between two collapsed columns mid-drag collapses the first immediately,
  not just at drag end (`test_hover_expand_switches_between_two_collapsed_columns`).
- ✅ No new `data_changed` fan-out: both new `load_board()` call sites in
  `handle_hover_expand_requested`/`finalize_hover_expand` pass `notify=False` (confirmed by
  reading the code — no test directly asserts on `data_changed` emission count, but the signal
  connection graph makes an accidental omission structurally visible: it's a literal keyword
  argument at each of the two call sites, present and correct in both).
- ✅ `_hover_timer` never fires stray signals after leave/drop before threshold (`test_widgets_headless.py`
  timer-stop tests + the `_on_hover_timeout` late-fire guard test).
- ✅ No regression elsewhere: full 91-test suite green, including all pre-existing column-reorder,
  column-to-board, and already-expanded-column drop tests untouched by this change.

**STATUS: QA PASSED**
