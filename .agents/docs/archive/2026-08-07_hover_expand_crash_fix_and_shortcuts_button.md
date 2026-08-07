# TECHNICAL DESIGN DOCUMENT

## 1. Overview

**Critical fix:** the app crashes when a task card is dropped into a column that hover-expanded
during that same drag (real-world, native drag-and-drop — not reproduced by any existing test,
all of which call the handler methods directly instead of driving a real `QDrag`). Root cause:
`handle_hover_expand_requested`/`finalize_hover_expand` (board_view.py) call the full
`self.load_board(self.board_id, notify=False)`, whose `clear_columns_layout()` calls
`deleteLater()` on **every** column widget in the board — including the column the dragged
`TaskCard` currently lives in (its `mouseMoveEvent` is still on the call stack, blocked inside
`drag.exec()`). Because this reload happens well before the drop (the user keeps moving the mouse
for seconds afterward to pick a position), Qt's native event pump has ample opportunity to actually
process that deferred deletion mid-drag — unlike the pre-existing, safe, single reload
`handle_task_drop` already did at drop time (right as the drag is ending, with no more mouse
movement left to pump events through). When the drag finally ends and `drag.exec()` returns, the
rest of `TaskCard.mouseMoveEvent` runs against a widget whose C++ side no longer exists, and
PySide6 aborts the process on the resulting unhandled failure — matching the user's report exactly
(a hard crash right at drop time, plus a preceding visual glitch from destroying/rebuilding the
*entire* column row mid-drag).

Fix: never call the full `load_board()` mid-drag. A collapsed column can only ever be the *target*
of a hover-expand, never the *source* of the drag that triggered it (cards can't be dragged out of
a collapsed column — it renders none). So a column-state-changing operation only ever needs to
touch the *one* column whose state actually changed; every other column, including the drag's
source column, must be left completely alone. This TDD extracts `load_board`'s per-column
construction into a shared helper and adds a surgical single-column rebuild used by the two
hover-expand code paths, leaving `handle_task_drop`'s existing (already-safe) full reload untouched.

**UX fix:** `Ctrl+/` (opens the shortcuts dialog) has no visible entry point anywhere in the UI —
and on a Spanish keyboard layout, typing `/` requires Shift, so it reads to the user as
"Ctrl+Shift+/", not an intuitive sole entry point. Add a visible **❔** button to the sidebar's
existing utility bar (next to 🔍/📅/⚙), mirroring those buttons exactly, that opens the same
dialog.

## 2. Implementation Tasks

- [x] `board_view.py` — extract a new private helper, placed right before `load_board`
  (~L322): moves the per-column construction logic that currently lives inline inside
  `load_board`'s loop (~L368-394) into its own method:
  ```python
  def _build_column_widget(self, col_data, tasks, board_info):
      """Construye un ColumnWidget completo (señales conectadas y, si está desplegada,
      sus TaskCard) para una columna dada. No lo añade a ningún layout ni a
      self.column_widgets -- eso lo decide el llamante: load_board() para reconstruir
      el tablero entero, _rebuild_single_column() para sustituir solo una columna sin
      tocar el resto (necesario para no destruir la columna de ORIGEN de un drag en
      curso -- ver _rebuild_single_column)."""
      col_widget = ColumnWidget(col_data, self)

      col_widget.task_dropped.connect(self.handle_task_drop)
      col_widget.add_task_requested.connect(self.add_task)
      col_widget.edit_column_requested.connect(self.edit_column)
      col_widget.delete_column_requested.connect(self.delete_column)
      col_widget.copy_column_requested.connect(self.copy_column)
      col_widget.collapse_toggle_requested.connect(self.handle_column_collapse)
      col_widget.collapsed_card_drop.connect(self.handle_collapsed_card_drop)
      col_widget.hover_expand_requested.connect(self.handle_hover_expand_requested)

      if not col_data.get("collapsed"):
          for task_data in tasks:
              card = TaskCard(task_data, self)
              if board_info:
                  card.set_card_style(board_info["color"])
              card.clicked.connect(self.open_task_details)
              card.board_link_clicked.connect(self.board_link_activated.emit)
              card.drag_ended.connect(self.finalize_hover_expand)
              col_widget.add_task_card(card)

      return col_widget
  ```

- [x] `board_view.py` — `load_board`'s column loop (~L368-397): replace the inline construction
  with a call to the new helper, keeping everything else (task-count computation, adding to the
  layout, populating `column_widgets`) exactly as-is:
  ```python
  for col_data in columns:
      # Cargar las tareas primero: hace falta el contador para la vista plegada.
      tasks = database.get_tasks(col_data["id"], self.db_path)
      col_data["task_count"] = len(tasks)

      col_widget = self._build_column_widget(col_data, tasks, board_info)

      self.columns_layout.addWidget(col_widget)
      self.column_widgets[col_data["id"]] = col_widget
  ```

- [x] `board_view.py` — add a new method, placed right after `_build_column_widget`:
  ```python
  def _rebuild_single_column(self, column_id):
      """Reconstruye el ColumnWidget de UNA sola columna (datos/tareas frescos de la
      BD) y lo sustituye en su misma posición dentro de columns_layout, sin tocar
      ninguna otra columna. A diferencia de load_board(), esto SÍ es seguro de llamar
      a mitad de un QDrag.exec() nativo en curso: el hover-expand solo actúa sobre
      columnas colapsadas, y una tarjeta solo puede arrastrarse desde una columna ya
      desplegada, así que la columna de origen del arrastre nunca puede coincidir con
      la columna que aquí se reconstruye -- nunca se le llama deleteLater()."""
      old_widget = self.column_widgets.get(column_id)
      if old_widget is None or not self.board_id or self.board_id == -1:
          return

      index = self.columns_layout.indexOf(old_widget)
      if index == -1:
          return

      columns = database.get_columns(self.board_id, self.db_path)
      col_data = next((c for c in columns if c["id"] == column_id), None)
      if col_data is None:
          return

      tasks = database.get_tasks(column_id, self.db_path)
      col_data["task_count"] = len(tasks)
      board_info = database.get_board(self.board_id, self.db_path)

      new_widget = self._build_column_widget(col_data, tasks, board_info)

      self.columns_layout.removeWidget(old_widget)
      old_widget.deleteLater()
      self.columns_layout.insertWidget(index, new_widget)
      self.column_widgets[column_id] = new_widget
  ```

- [x] `board_view.py` — rewrite the three hover-expand methods (~L511-537) to use
  `_rebuild_single_column` instead of `load_board`:
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
      self._rebuild_single_column(column_id)

  def _collapse_hover_expanded_column(self):
      """Repliega (BD + widget) la columna actualmente expandida por hover, si la
      hay. Reconstruye solo esa columna -- nunca toca el resto del tablero."""
      if self._hover_expanded_column_id is not None:
          column_id = self._hover_expanded_column_id
          database.set_column_collapsed(column_id, True, self.db_path)
          self._hover_expanded_column_id = None
          self._rebuild_single_column(column_id)

  def finalize_hover_expand(self):
      """Conectado a TaskCard.drag_ended: se ejecuta al terminar cualquier
      arrastre de tarjeta (soltada donde sea, o cancelado). Si queda una
      columna expandida por hover sin haber recibido el drop, se repliega."""
      self._collapse_hover_expanded_column()
  ```
  Note `finalize_hover_expand` is now a one-line delegation — `_collapse_hover_expanded_column`
  already no-ops correctly when nothing is tracked, so no behavior changes versus before.

- [x] `board_view.py` — **do not touch** `handle_task_drop`'s existing final
  `self.load_board(self.board_id)` call, nor its existing
  `if target_column_id == self._hover_expanded_column_id: self._hover_expanded_column_id = None`
  guard. That reload only ever runs at actual drop time (the drag is already ending, no more mouse
  movement follows), which is the pre-existing, already-safe pattern this bug report does not
  implicate.

- [x] `sidebar.py` — `SidebarWidget` (~L287-290): add a new signal next to
  `open_settings_requested`:
  ```python
  open_shortcuts_requested = Signal()   # Emite al pulsar el botón de atajos de teclado
  ```

- [x] `sidebar.py` — `_build_utility_bar` (~L458-465): immediately after the existing
  `settings_btn` block (after `bar_layout.addWidget(self.settings_btn)`), add:
  ```python
  self.shortcuts_btn = QPushButton("❔")
  self.shortcuts_btn.setObjectName("UtilityIconButton")
  self.shortcuts_btn.setFixedSize(34, 28)
  self.shortcuts_btn.setCursor(Qt.PointingHandCursor)
  self.shortcuts_btn.setToolTip(t("sidebar.shortcuts_tooltip"))
  self.shortcuts_btn.clicked.connect(self.open_shortcuts_requested.emit)
  bar_layout.addWidget(self.shortcuts_btn)
  ```

- [x] `strings.py` — insert a new key right after `"sidebar.settings_tooltip"` (~L105):
  ```python
  "sidebar.shortcuts_tooltip": "Atajos de teclado (Ctrl+/)",
  ```

- [x] `main.py` — `init_ui` (~L191-194, alongside the existing
  `self.sidebar.open_settings_requested.connect(self.show_settings)`): add
  ```python
  self.sidebar.open_shortcuts_requested.connect(self.show_shortcuts)
  ```

## 3. Acceptance Criteria

- **Crash fix — the critical one:** during a real drag (or the equivalent direct-call sequence used
  by tests, since a native `QDrag` can't be driven headless), hover-expanding a collapsed column
  must never touch, recreate, or schedule deletion of any *other* column's widget — specifically
  not the drag's source column. Concretely: capture the `ColumnWidget` Python instance (and one of
  its live `TaskCard` children) for an *expanded* column A before calling
  `handle_hover_expand_requested` on a *different*, collapsed column B; afterward,
  `board_view.column_widgets[A_id]` must be the *same* object (`is`, not just equal), and the
  captured `TaskCard` must still be among `old_col_a_widget.findChildren(TaskCard)`. This must hold
  through the full cycle: hover-expand B, then `finalize_hover_expand()` (simulating the drag
  ending without a drop in B) — column A's widget identity must never change at any point.
- Column B itself must still end up correctly rebuilt: a *new* `ColumnWidget` instance,
  `collapsed == False`, in the same layout position B occupied before.
- All previously-passing behavior in `tests/test_hover_expand.py` (DB-state assertions:
  hover-expand persists/tracks, finalize re-collapses, a real drop inside sticks, drop elsewhere
  leaves it pending, switching between two collapsed columns, double-hover-expand no-op) must keep
  passing unmodified — the externally-observable behavior (DB `collapsed` flag,
  `_hover_expanded_column_id` tracking) is unchanged by this fix, only the *scope* of what gets
  rebuilt internally narrows.
- `handle_task_drop`'s own behavior (position selection, moving between columns, the
  `_hover_expanded_column_id`-clearing guard when a real drop lands in the hover-expanded column)
  is unchanged — still uses the full `load_board()`, still only at actual drop time.
- No regression in ordinary (non-hover) collapsed-column drops, already-expanded-column drag/drop,
  or column reordering — none of the touched code paths are shared with those.
- **UX fix:** a **❔** button appears in the sidebar utility bar, styled identically to
  🔍/📅/⚙ (`UtilityIconButton`, 34×28, pointing-hand cursor), with a tooltip mentioning `Ctrl+/`.
  Clicking it opens the exact same `ShortcutsDialog` the `Ctrl+/` shortcut already opens (both
  ultimately call `MainWindow.show_shortcuts`).
- Full existing test suite (97 tests before this fix) + ruff stay green. New test to add in
  `tests/test_hover_expand.py` (needs `from widgets import TaskCard` added to its imports):
  a test named along the lines of `test_hover_expand_never_touches_other_columns_widgets` that
  implements the identity-preservation check described above — written so it demonstrably would
  have **failed** against the pre-fix implementation (full `load_board()` replaces every entry in
  `column_widgets`, so the identity check fails) and **passes** after this fix.
- A full-app smoke check (per this project's convention) exercising the same sequence
  (hover-expand → drop inside; hover-expand → drop elsewhere) against a real `BoardViewWidget`
  inside a real `MainWindow`, confirming no exception is raised and column A's widget identity is
  preserved throughout — as close as this environment can get to reproducing the real native-drag
  crash scenario without an actual OS-level `QDrag`.

## QA Report

**Code review:** every `[x]` task in §2 traced against the actual current contents of
`board_view.py`, `sidebar.py`, `strings.py`, `main.py` — `_build_column_widget`,
`_rebuild_single_column`, the rewritten `handle_hover_expand_requested`/
`_collapse_hover_expanded_column`/`finalize_hover_expand`, `load_board`'s updated loop, the
`shortcuts_btn`/`open_shortcuts_requested` wiring, and the new `strings.py` key all match this TDD
exactly. Confirmed `handle_task_drop` was **not** touched (still the full `load_board()`, still
only at drop time) — grepped for `load_board` in board_view.py: the only remaining call sites are
`load_board` itself (welcome-screen early-return branch) and `handle_task_drop`'s final line; the
three hover-expand methods no longer call it at all.

**Regression-test validity, verified empirically (not just by inspection):** temporarily stashed
just `board_view.py` (`git stash push -- board_view.py`) to restore the pre-fix implementation
while keeping the new test file, and confirmed
`test_hover_expand_never_touches_other_columns_widgets` **fails** against it — exactly as
expected, since the old `load_board()`-based implementation replaces every entry in
`column_widgets`, including column A's:
```
assert board_view.column_widgets[col_a] is old_col_a_widget
E   assert <widgets.ColumnWidget(...) at 0x...E80> is <widgets.ColumnWidget(...) at 0x...F40>
```
Restored the fix (`git stash pop`) and re-ran: passes, along with the rest of the suite. This is
direct proof the new test would have caught the exact bug the user reported, and that the fix
resolves it.

**Tests added:** `tests/test_hover_expand.py` (+2 tests, `from widgets import TaskCard` added to
imports):
- `test_hover_expand_never_touches_other_columns_widgets` — the core regression test described
  above, covering both the hover-expand-only state and the post-`finalize_hover_expand` state.
- `test_hover_expand_column_widget_swapped_at_same_layout_position` — confirms the rebuilt column
  lands at the exact same `columns_layout` index (no reordering), and that column A's position is
  untouched too. (This one also happens to pass against the pre-fix code, since `load_board`
  rebuilds columns in the same DB order — it's a correctness check for the new code path, not
  itself a regression discriminator; the identity test above is the one that discriminates.)

**Full-app smoke check** (`smoke_hover_expand_crash_fix.py`, real `MainWindow` against a scratch
DB): reproduced both possible endings of the bug scenario on the real, fully-wired app —
(1) hover-expand the collapsed target column while an origin column holds a task, verify the
origin column's widget and `TaskCard` are never touched, then drop the task *inside* the
now-expanded target at a chosen (non-last) position, confirming it lands there and stays expanded;
(2) repeat the hover-expand, but this time the drop lands back in the *origin* column instead —
confirms the target column re-collapses via `finalize_hover_expand` with no exception anywhere in
the sequence. Also separately verified the new **❔** sidebar button: present, tooltip mentions
`Ctrl+/`, and clicking it emits `open_shortcuts_requested` (checked via a temporary spy after
disconnecting the real `show_shortcuts` slot, to avoid blocking the headless script on a real modal
`QDialog.exec()` — a script-only concern, not a product issue: `MainWindow.init_ui` wires
`open_shortcuts_requested` to `show_shortcuts` exactly once, confirmed by the clean
`disconnect()` succeeding).

**Suite results:** `pytest -q` (offscreen, whole suite): **99 passed** (was 97; +2 from this fix).
`ruff check .`: **all checks passed**.

**Acceptance criteria (§3) — verified:**
- ✅ Crash fix: origin column widget/TaskCard identity preserved through the full hover-expand →
  finalize cycle (regression test + smoke scenario 2).
- ✅ Target column correctly rebuilt (new instance, `collapsed == False`, same layout index).
- ✅ All 7 pre-existing `test_hover_expand.py` tests pass unmodified.
- ✅ `handle_task_drop` unchanged — confirmed by code review (no edits to that method in the diff).
- ✅ No regression elsewhere — full 99-test suite green.
- ✅ UX fix: ❔ button present, styled like its siblings, tooltip mentions `Ctrl+/`, opens the same
  dialog.

**STATUS: QA PASSED**
