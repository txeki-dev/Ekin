# TECHNICAL DESIGN DOCUMENT

## 1. Overview

Three independent, user-requested refinements bundled into one wave:

1. `Ctrl+N` currently always adds a new task to the *first* column of the active board. It should
   instead target the last column the user actually interacted with (clicked a card in, clicked
   "+ Añadir Tarea" in, or just clicked anywhere in) — falling back to the first column only when
   nothing has been clicked yet, or the previously-clicked column no longer exists / belongs to a
   board that isn't the one currently open.
2. The sidebar's utility bar (clock + 🔔🔍📅⚙❔) is cramped into a single row inside a narrow
   (~220px) sidebar. Split it into two rows: date/time on top, icon buttons below.
3. After the crash-fix wave, dropping a card *inside* a column that hover-expanded during that
   same drag leaves the column expanded permanently. The user now wants the opposite: it should
   fold back up in that case too, exactly as it already does when the drag ends without a drop
   landing there.

## 2. Implementation Tasks

### Item 1 — Ctrl+N targets the last-interacted-with column

- [x] `board_view.py` — `BoardViewWidget.__init__` (~L197-201): add
  `self._last_active_column_id = None` (the column_id of the last card/`+ Añadir Tarea`/column
  click, used only as a *hint* for `quick_add_task` — re-validated against the active board's
  actual columns every time it's read, never trusted blindly).

- [x] `board_view.py` — add a new one-line method, placed near `add_task` (~L640):
  ```python
  def _set_last_active_column(self, column_id):
      self._last_active_column_id = column_id
  ```

- [x] `board_view.py` — `add_task` (~L640-648): track the column as the first line:
  ```python
  def add_task(self, column_id):
      """Crea una tarea solicitando el título rápidamente."""
      self._last_active_column_id = column_id
      title, ok = QInputDialog.getText(
          self, t("board_view.add_task.title"), t("board_view.add_task.prompt"),
          text=""
      )
      if ok and title.strip():
          database.create_task(column_id, title.strip(), db_path=self.db_path)
          self.load_board(self.board_id)
  ```
  This covers the "+ Añadir Tarea" button for free (`add_task_requested.connect(self.add_task)`
  already passes the right `column_id` — no change needed to that connection).

- [x] `board_view.py` — add a new method, placed right after `open_task_details`'s definition
  ends (before `handle_column_collapse` or wherever the next method starts): a thin wrapper so a
  task-card click also records its column:
  ```python
  def _handle_task_card_clicked(self, task_id, column_id):
      self._set_last_active_column(column_id)
      self.open_task_details(task_id)
  ```

- [x] `board_view.py` — `_build_column_widget` (~L322-350): change the task-card click connection
  from `card.clicked.connect(self.open_task_details)` to
  ```python
  card.clicked.connect(lambda tid, cid=col_data["id"]: self._handle_task_card_clicked(tid, cid))
  ```
  and add, right after `col_widget.hover_expand_requested.connect(self.handle_hover_expand_requested)`:
  ```python
  col_widget.column_activated.connect(self._set_last_active_column)
  ```

- [x] `board_view.py` — `quick_add_task` (~L632-638): replace the "always first column" logic:
  ```python
  def quick_add_task(self):
      """Atajo Ctrl+N: añade una tarea a la última columna con la que se ha
      interactuado (tarjeta abierta, botón "+ Añadir Tarea", o clic en la propia
      columna). Si no hay ninguna registrada -- o ya no pertenece al tablero
      activo (p. ej. se borró, o se cambió de tablero desde entonces) -- cae a
      la primera columna, como antes."""
      if not self.board_id or self.board_id == -1:
          return
      columns = database.get_columns(self.board_id, self.db_path)
      if not columns:
          return
      column_ids = [c["id"] for c in columns]
      target_id = (
          self._last_active_column_id
          if self._last_active_column_id in column_ids
          else column_ids[0]
      )
      self.add_task(target_id)
  ```

- [x] `widgets.py` — `ColumnWidget` (class ~L533): add a new signal next to `hover_expand_requested`:
  ```python
  column_activated = Signal(int)  # column_id (clic en cualquier parte "en blanco" de la columna)
  ```
  and a new method (place anywhere among the other event-ish methods, e.g. right after `__init__`
  or near `dragEnterEvent`):
  ```python
  def mousePressEvent(self, event):
      """Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta
      hijo (los widgets internos consumen su propio click y no burbujean aquí):
      sirve de pista para "última columna activa" (ver BoardViewWidget.quick_add_task)."""
      self.column_activated.emit(self.column_id)
      super().mousePressEvent(event)
  ```
  This does not conflict with the existing collapsed-only `dragEnterEvent`/`dragMoveEvent`/
  `dragLeaveEvent`/`dropEvent` overrides (drag events, not mouse-press) nor with any child widget's
  own click handling (buttons/cards consume their own press and don't propagate it up).

### Item 2 — Two-row utility bar

- [x] `sidebar.py` — `_build_utility_bar` (~L412-475): restructure the outer layout from
  `QHBoxLayout` to `QVBoxLayout` with the clock on its own row and the icon buttons in a second,
  centered row. Full replacement:
  ```python
  def _build_utility_bar(self):
      """Barra con reloj (fecha/hora) en su propia fila arriba, y accesos rápidos
      (campana, búsqueda, calendario, ajustes, atajos) centrados en una fila propia
      debajo -- separados para que quepan con holgura en el ancho estrecho de la
      sidebar."""
      bar = QFrame()
      bar.setObjectName("UtilityBar")
      outer_layout = QVBoxLayout(bar)
      outer_layout.setContentsMargins(10, 6, 8, 6)
      outer_layout.setSpacing(6)

      self.clock_label = QLabel("")
      self.clock_label.setObjectName("ClockLabel")
      self.clock_label.setAlignment(Qt.AlignCenter)
      outer_layout.addWidget(self.clock_label)

      icons_row = QHBoxLayout()
      icons_row.setSpacing(6)
      icons_row.addStretch()

      # Campana con badge de conteo superpuesto
      bell_container = QWidget()
      bell_container.setFixedSize(34, 28)
      self.bell_btn = QPushButton("🔔", bell_container)
      self.bell_btn.setObjectName("UtilityIconButton")
      self.bell_btn.setGeometry(0, 0, 34, 28)
      self.bell_btn.setCursor(Qt.PointingHandCursor)
      self.bell_btn.setToolTip(t("sidebar.bell_tooltip"))
      self.bell_btn.clicked.connect(self.show_notifications)

      self.bell_badge = QLabel("0", bell_container)
      self.bell_badge.setObjectName("BellBadge")
      self.bell_badge.setAlignment(Qt.AlignCenter)
      self.bell_badge.setFixedSize(15, 15)
      self.bell_badge.move(19, -1)
      self.bell_badge.hide()
      icons_row.addWidget(bell_container)

      self.search_btn = QPushButton("🔍")
      self.search_btn.setObjectName("UtilityIconButton")
      self.search_btn.setFixedSize(34, 28)
      self.search_btn.setCursor(Qt.PointingHandCursor)
      self.search_btn.setToolTip(t("sidebar.search_tooltip"))
      self.search_btn.clicked.connect(self.open_search_requested.emit)
      icons_row.addWidget(self.search_btn)

      self.calendar_btn = QPushButton("📅")
      self.calendar_btn.setObjectName("UtilityIconButton")
      self.calendar_btn.setFixedSize(34, 28)
      self.calendar_btn.setCursor(Qt.PointingHandCursor)
      self.calendar_btn.setToolTip(t("sidebar.calendar_tooltip"))
      self.calendar_btn.clicked.connect(self.open_calendar_requested.emit)
      icons_row.addWidget(self.calendar_btn)

      self.settings_btn = QPushButton("⚙")
      self.settings_btn.setObjectName("UtilityIconButton")
      self.settings_btn.setFixedSize(34, 28)
      self.settings_btn.setCursor(Qt.PointingHandCursor)
      self.settings_btn.setToolTip(t("sidebar.settings_tooltip"))
      self.settings_btn.clicked.connect(self.open_settings_requested.emit)
      icons_row.addWidget(self.settings_btn)

      self.shortcuts_btn = QPushButton("❔")
      self.shortcuts_btn.setObjectName("UtilityIconButton")
      self.shortcuts_btn.setFixedSize(34, 28)
      self.shortcuts_btn.setCursor(Qt.PointingHandCursor)
      self.shortcuts_btn.setToolTip(t("sidebar.shortcuts_tooltip"))
      self.shortcuts_btn.clicked.connect(self.open_shortcuts_requested.emit)
      icons_row.addWidget(self.shortcuts_btn)

      icons_row.addStretch()
      outer_layout.addLayout(icons_row)

      return bar
  ```
  Every widget attribute (`clock_label`, `bell_btn`, `bell_badge`, `search_btn`, `calendar_btn`,
  `settings_btn`, `shortcuts_btn`), object name, tooltip, size, cursor, and signal connection is
  byte-for-byte identical to today — only the container layout changes from one `QHBoxLayout` to
  a `QVBoxLayout` wrapping the clock and a new inner `QHBoxLayout` for the icons. No other method
  in `sidebar.py` references `bar_layout`, so renaming it away entirely is safe.

### Item 3 — Hover-expanded column always re-collapses when the drag ends, even on a drop inside it

- [x] `board_view.py` — `handle_task_drop` (~L727-730): delete these three lines entirely (no
  replacement):
  ```python
  if target_column_id == self._hover_expanded_column_id:
      self._hover_expanded_column_id = None
  ```
  Everything else in `handle_task_drop` is unchanged. `_hover_expanded_column_id` now stays set
  through the drop; `TaskCard.drag_ended` (emitted right after this whole call chain returns, once
  `QDrag.exec()` unblocks) drives `finalize_hover_expand()` → `_collapse_hover_expanded_column()`,
  which persists `collapsed=True` and calls `_rebuild_single_column()` regardless of where the
  drop landed. `handle_collapsed_card_drop` (the no-hover quick-drop path) is untouched — it never
  touches `_hover_expanded_column_id` and keeps expanding-and-leaving-expanded as today.

## 3. Acceptance Criteria

**Item 1:**
- Clicking a task card, then pressing `Ctrl+N`, adds the new task to that card's column (not
  necessarily the first one).
- Clicking "+ Añadir Tarea" in some column, then pressing `Ctrl+N` again, adds to that same column.
- Clicking blank space inside a column (header padding, empty area below the cards), then
  `Ctrl+N`, targets that column.
- With nothing clicked yet (fresh board load), `Ctrl+N` still targets the first column (unchanged
  default).
- If the last-clicked column was since deleted, or the user switched to a *different* board,
  `Ctrl+N` falls back to the first column of the currently active board — never targets a column
  belonging to another board, never crashes on a stale/missing id.
- No change to the "+ Añadir Tarea" button's own behavior (it already explicitly specifies its
  column; this feature only changes `Ctrl+N`'s implicit target).

**Item 2:**
- The utility bar renders the clock on its own row above a centered row of the 5 icon buttons.
  Every button keeps its exact size (34×28), object name, tooltip, and click behavior — only the
  layout changes. `tests/test_widgets_headless.py` (or manual inspection) should confirm
  `sidebar.clock_label`, `sidebar.bell_btn`, `sidebar.search_btn`, `sidebar.calendar_btn`,
  `sidebar.settings_btn`, `sidebar.shortcuts_btn` all still exist with unchanged tooltips.

**Item 3:**
- Hover-expand a collapsed column, then drop the dragged card *inside* it (any position): the
  column ends up collapsed again after the drag fully ends (i.e., after the equivalent of
  `finalize_hover_expand()`/`drag_ended` runs) — `columns.collapsed == 1` in the DB — and the task
  that was dropped is still assigned to that column with the chosen position (only hidden from
  view because the column is collapsed, not moved or lost).
- Hover-expand a collapsed column, drop elsewhere, or cancel: unchanged from the crash-fix wave —
  still re-collapses.
- The no-hover quick-drop path (`handle_collapsed_card_drop`) is unaffected: dropping directly on
  a still-collapsed column (before the hover timer fires) still expands it and *leaves it
  expanded* — this is a deliberately different, untouched behavior.
- Rewrite `tests/test_hover_expand.py::test_real_drop_inside_hover_expanded_column_sticks` (name
  and assertions both now contradict the desired behavior) into a test verifying the new
  contract: after `handle_hover_expand_requested` + `handle_task_drop` (drop inside),
  `_hover_expanded_column_id` must still equal that column (not yet cleared); after a subsequent
  `finalize_hover_expand()` call (simulating `drag_ended`), the column must be `collapsed == 1`
  in the DB, `_hover_expanded_column_id` must be `None`, and the dropped task must still be
  present in that column's task list (`database.get_tasks`).

**General:**
- Full existing test suite (99 tests before this wave) + ruff stay green, apart from the one
  intentionally-rewritten test in item 3.
- A full-app smoke check (per this project's convention) exercising: (a) clicking a card in a
  non-first column then invoking `quick_add_task` on the real `MainWindow`/`BoardViewWidget` and
  confirming the new task lands in that column; (b) the two-row utility bar renders without
  layout errors; (c) the item-3 hover-expand-drop-inside-then-recollapse sequence end-to-end.

## QA Report

**Code review:** every `[x]` task in §2 traced against the actual current contents of
`board_view.py`, `widgets.py`, `sidebar.py` — `_last_active_column_id` init, `_set_last_active_column`,
`_handle_task_card_clicked`, the rewritten `add_task`/`quick_add_task`, the task-card click lambda
and `column_activated` connection in `_build_column_widget`, `ColumnWidget.column_activated` +
`mousePressEvent`, the deleted 3-line block in `handle_task_drop`, and the two-row
`_build_utility_bar` all match this TDD exactly (confirmed byte-for-byte on the icon-button block:
same object names, sizes, cursors, tooltips, signal connections, only the container layout
changed). `handle_collapsed_card_drop` confirmed untouched by grep — still the only caller besides
`handle_hover_expand_requested`/`_collapse_hover_expanded_column` that ever writes
`columns.collapsed`, and it never reads/writes `_hover_expanded_column_id`.

**Regression baseline, verified empirically:** ran the full suite *before* touching any test files
— exactly one failure, `test_real_drop_inside_hover_expanded_column_sticks`, asserting
`_hover_expanded_column_id is None` right after `handle_task_drop` where it's now `1` (the column
id) — precisely the old contract the user asked to invert. This confirms the code change took
effect and pinpoints exactly the one test needing rewrite, with no other unexpected breakage.

**Tests added/changed:**
- `tests/test_hover_expand.py::test_real_drop_inside_hover_expanded_column_sticks` renamed to
  `test_real_drop_inside_hover_expanded_column_still_recollapses` and rewritten per the TDD's
  exact new contract (tracking survives the drop, `finalize_hover_expand()` then collapses and the
  task is confirmed still present via `database.get_tasks`). All other 8 pre-existing tests in
  that file pass unmodified (none of them depended on the "sticks expanded" behavior).
- New `tests/test_last_active_column.py` (9 tests): `ColumnWidget.mousePressEvent` emits
  `column_activated` with a real `QMouseEvent` (not a fake — same standard used for the
  drag-event tests in `test_widgets_headless.py`); clicking a column's blank background, a task
  card, and `add_task` (via `+ Añadir Tarea`) each set `_last_active_column_id`; `quick_add_task`
  uses it when valid, and falls back to the first column in three distinct invalid cases (nothing
  clicked yet, the tracked column belongs to a *different* board, the tracked column was deleted)
  plus the pre-existing no-board-selected no-op. `QInputDialog.getText` monkeypatched (returns
  "cancelled") wherever `add_task`'s real modal path is exercised, so no test can hang on an
  un-dismissable dialog headless — same defensive pattern already used for `ColumnEditDialog` in
  `tests/test_keyboard_shortcuts.py`.
- `tests/test_keyboard_shortcuts.py` (+2 tests): confirms every utility-bar widget/attribute,
  tooltip, and size survived the two-row restructuring, and that the layout tree is actually
  two rows (`clock_label` as layout item 0, a nested `QHBoxLayout` — not a bare widget — as item 1,
  containing the four directly-added icon buttons).

**Full-app smoke script** (`smoke_three_fixes.py`, real `MainWindow` against a scratch DB):
(1) clicked a real `TaskCard` in column B (with `open_task_details` stubbed out to avoid blocking
on the real modal detail dialog), then called `quick_add_task()` — new task landed in B, not the
board's first column (A); switched to a second board and confirmed `quick_add_task()` correctly
fell back to that board's own first column rather than reusing the now-stale column id from the
first board; (2) confirmed the utility bar's layout tree has the clock as row 0 and a sub-layout
(not a widget) as row 1; (3) hover-expanded a collapsed column, dropped a card inside it, confirmed
tracking survived the drop, then called `finalize_hover_expand()` and confirmed the column
collapsed again with the task still present in it. No exceptions, no hangs.

**Suite results:** `pytest -q` (offscreen, whole suite): **110 passed** (was 99; +11 from this
wave, net of the 1 rewritten test). `ruff check .`: **all checks passed**.

**Acceptance criteria — verified:**
- ✅ Item 1: all five bullet points (card click, add-task-button click, blank-column click,
  fresh-board default, stale/cross-board fallback) covered by dedicated tests + smoke scenario 1.
- ✅ Item 2: all utility-bar widgets/tooltips/sizes preserved; layout genuinely two rows.
- ✅ Item 3: drop-inside now re-collapses (rewritten test + smoke scenario 3);
  `handle_collapsed_card_drop`'s different, untouched behavior confirmed by code review.
- ✅ Full suite green apart from the one intentionally-rewritten test; ruff clean.
- ✅ Full-app smoke check covers all three items end-to-end.

**STATUS: QA PASSED**
