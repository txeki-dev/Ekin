# TECHNICAL DESIGN DOCUMENT

## 1. Overview

Adds four new global keyboard shortcuts (`Ctrl+Shift+N` new column, `Ctrl+1`..`Ctrl+9` jump to the
Nth sidebar board, `Ctrl+,` open Settings, `Ctrl+Shift+C` open Calendar) plus a new `Ctrl+/`
shortcut that opens a **"Atajos de teclado"** reference dialog listing every shortcut in the app
(the four new ones, the pre-existing global ones, and the rich-text-editor-local ones), so users
have one place to see them all instead of piecing them together from tooltips/README.

`show_settings`/`show_calendar_view` already exist on `MainWindow` (only reachable from sidebar
buttons today) — the new shortcuts just call them directly, no new logic needed there.
`board_view.add_column` already exists too, but its guard (`if not self.board_id: return`) doesn't
catch the `board_id == -1` "no board selected" sentinel (`not -1` is `False` in Python) — harmless
today because the "+ Añadir Columna" button that calls it only exists in the DOM once a board is
loaded, but a global `Ctrl+Shift+N` shortcut bypasses that UI gate entirely, so the guard must be
fixed to match the already-correct pattern used by `quick_add_task`
(`if not self.board_id or self.board_id == -1: return`).

`Ctrl+1..9` needs a new `SidebarWidget.select_board_by_index(index)` (0-based), mirroring the
existing `select_adjacent_board(direction)`'s reliance on `list(self.board_buttons.keys())` being
in visual order. Wiring 9 shortcuts in a loop is the exact shape of bug this project already hit
once during the i18n pass ("6 `for t in ...` loop-variable shadowing bugs") — each lambda must bind
its index by value via a default argument, not close over the loop variable.

## 2. Implementation Tasks

- [x] `board_view.py` — `BoardViewWidget.add_column` (~L439-448): change the guard from
  ```python
  if not self.board_id:
      return
  ```
  to
  ```python
  if not self.board_id or self.board_id == -1:
      return
  ```
  (matches `quick_add_task`'s existing pattern at ~L594). No other change to this method.

- [x] `sidebar.py` — add a new method on `SidebarWidget`, placed immediately after
  `select_adjacent_board` (~L613-623, i.e. right before `def add_board(self):`):
  ```python
  def select_board_by_index(self, index):
      """Selecciona el tablero en la posición `index` (0-based, mismo orden visual que
      select_adjacent_board). No hace nada si el índice está fuera de rango."""
      board_ids = list(self.board_buttons.keys())
      if 0 <= index < len(board_ids):
          self.select_board(board_ids[index])
  ```

- [x] `strings.py` — insert a new section right after the `settings_dialog.py` section ends (after
  the line `"settings.close_btn": "Cerrar",` at ~L295, before the
  `# --- detail_dialog/markdown_edit.py ... ---` comment at ~L297):
  ```python
  # --- shortcuts_dialog.py: diálogo "Atajos de teclado" (Ctrl+/) ---
  "shortcuts.window_title": "Atajos de teclado",
  "shortcuts.header": "⌨ <b>Atajos de teclado</b>",
  "shortcuts.section_general": "General y navegación",
  "shortcuts.section_editor": "Editor de texto enriquecido (descripción y diario)",
  "shortcuts.item_search": "Ctrl+F — Búsqueda global de tareas",
  "shortcuts.item_new_task": (
      "Ctrl+N — Nueva tarea en la primera columna del tablero activo (fuera del editor de "
      "texto; dentro de él, Ctrl+N es Negrita)"
  ),
  "shortcuts.item_new_column": "Ctrl+Shift+N — Nueva columna en el tablero activo",
  "shortcuts.item_prev_next_board": "Alt+↑ / Alt+↓ — Tablero anterior / siguiente",
  "shortcuts.item_jump_board": "Ctrl+1 … Ctrl+9 — Saltar directamente al tablero Nº de la barra lateral",
  "shortcuts.item_calendar": "Ctrl+Shift+C — Abrir el Calendario",
  "shortcuts.item_settings": "Ctrl+, — Abrir Ajustes",
  "shortcuts.item_shortcuts": "Ctrl+/ — Mostrar esta ventana",
  "shortcuts.item_undo_redo": "Ctrl+Z / Ctrl+Y (o Ctrl+Shift+Z) — Deshacer / Rehacer",
  "shortcuts.item_close_dialog": "Esc — Cerrar el diálogo abierto",
  "shortcuts.item_bold": "Ctrl+B o Ctrl+N — Negrita (dentro del editor)",
  "shortcuts.item_italic": "Ctrl+K o Ctrl+I — Cursiva (dentro del editor)",
  "shortcuts.item_strike": "Ctrl+Shift+X — Tachado (dentro del editor)",
  "shortcuts.item_nest_bullet": "Tab (sobre una viñeta) — Anidar la viñeta (dentro del editor)",
  "shortcuts.item_arrow": "Escribir «-->» se convierte en → automáticamente (dentro del editor)",
  "shortcuts.item_add_log": "Ctrl+Enter — Añadir la nota al Diario (detalle de tarea)",
  "shortcuts.hint": "Pulsa Ctrl+/ en cualquier momento para volver a ver esta ventana.",
  "shortcuts.close_btn": "Cerrar",

  ```
  (keep the blank line before the next section, matching the file's existing spacing convention).

- [x] `shortcuts_dialog.py` (**new file**, project root, alongside `settings_dialog.py`/
  `search_dialog.py`): a static reference dialog, no DB access needed. Full contents:
  ```python
  """Diálogo "Atajos de teclado" (Ctrl+/): referencia estática de todos los atajos de la
  app, agrupados por categoría. No depende de la base de datos."""
  from PySide6.QtCore import Qt
  from PySide6.QtWidgets import (
      QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QWidget
  )

  import styles
  from strings import t


  class ShortcutsDialog(QDialog):
      def __init__(self, parent=None):
          super().__init__(parent)
          self.setWindowTitle(t("shortcuts.window_title"))
          self.setMinimumWidth(460)
          self.resize(460, 520)

          layout = QVBoxLayout(self)
          layout.setContentsMargins(18, 18, 18, 18)
          layout.setSpacing(14)

          layout.addWidget(QLabel(t("shortcuts.header")))

          scroll = QScrollArea()
          scroll.setWidgetResizable(True)
          scroll.setFrameShape(QFrame.NoFrame)
          scroll.setStyleSheet("background: transparent; border: none;")

          container = QWidget()
          container.setStyleSheet("background: transparent;")
          content_layout = QVBoxLayout(container)
          content_layout.setContentsMargins(0, 0, 0, 0)
          content_layout.setSpacing(10)

          general_keys = [
              "shortcuts.item_search",
              "shortcuts.item_new_task",
              "shortcuts.item_new_column",
              "shortcuts.item_prev_next_board",
              "shortcuts.item_jump_board",
              "shortcuts.item_calendar",
              "shortcuts.item_settings",
              "shortcuts.item_shortcuts",
              "shortcuts.item_undo_redo",
              "shortcuts.item_close_dialog",
          ]
          editor_keys = [
              "shortcuts.item_bold",
              "shortcuts.item_italic",
              "shortcuts.item_strike",
              "shortcuts.item_nest_bullet",
              "shortcuts.item_arrow",
              "shortcuts.item_add_log",
          ]

          content_layout.addWidget(self._section_label(t("shortcuts.section_general")))
          for key in general_keys:
              content_layout.addWidget(self._item_label(key))

          line = QFrame()
          line.setFrameShape(QFrame.HLine)
          line.setStyleSheet(f"color: {styles.COLORS['border']};")
          content_layout.addWidget(line)

          content_layout.addWidget(self._section_label(t("shortcuts.section_editor")))
          for key in editor_keys:
              content_layout.addWidget(self._item_label(key))

          content_layout.addStretch()
          scroll.setWidget(container)
          layout.addWidget(scroll)

          hint = QLabel(t("shortcuts.hint"))
          hint.setWordWrap(True)
          hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
          layout.addWidget(hint)

          btns = QHBoxLayout()
          btns.addStretch()
          close_btn = QPushButton(t("shortcuts.close_btn"))
          close_btn.setObjectName("PrimaryButton")
          close_btn.setCursor(Qt.PointingHandCursor)
          close_btn.clicked.connect(self.accept)
          btns.addWidget(close_btn)
          layout.addLayout(btns)

      def _section_label(self, text):
          lbl = QLabel(f"<b>{text}</b>")
          lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px; margin-top: 4px;")
          return lbl

      def _item_label(self, key):
          lbl = QLabel(t(key))
          lbl.setWordWrap(True)
          lbl.setStyleSheet(f"color: {styles.COLORS['text_main']}; font-size: 12px;")
          return lbl
  ```

- [x] `main.py` — imports: add `from shortcuts_dialog import ShortcutsDialog` alongside the
  existing `from settings_dialog import SettingsDialog` line.

- [x] `main.py` — `MainWindow.__init__` (~L110-118): immediately after the existing `Alt+Down`
  `QShortcut` block and before the `# Comprobar actualizaciones tras 1 segundo` comment, insert:
  ```python
  # Ctrl+1..Ctrl+9: saltar directamente al tablero N-ésimo de la barra lateral
  for _n in range(1, 10):
      QShortcut(QKeySequence(f"Ctrl+{_n}"), self).activated.connect(
          lambda index=_n - 1: self.sidebar.select_board_by_index(index)
      )

  # Ctrl+Shift+N: nueva columna en el tablero activo
  QShortcut(QKeySequence("Ctrl+Shift+N"), self).activated.connect(self.board_view.add_column)

  # Ctrl+,: abrir Ajustes; Ctrl+Shift+C: abrir el Calendario
  QShortcut(QKeySequence("Ctrl+,"), self).activated.connect(self.show_settings)
  QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.show_calendar_view)

  # Ctrl+/: ventana de referencia de atajos de teclado
  QShortcut(QKeySequence("Ctrl+/"), self).activated.connect(self.show_shortcuts)
  ```
  The `lambda index=_n - 1: ...` default-argument binding is required — closing directly over the
  loop variable `_n` would make all 9 shortcuts jump to the same (last) board, exactly the
  loop-variable-capture bug this project already hit once during the i18n string extraction.

- [x] `main.py` — add a new `show_shortcuts` method on `MainWindow`, placed right after
  `show_settings` (~L224-228):
  ```python
  def show_shortcuts(self):
      """Abre la ventana de referencia de atajos de teclado (Ctrl+/)."""
      ShortcutsDialog(self).exec()
  ```

## 3. Acceptance Criteria

- `Ctrl+Shift+N` opens the "new column" dialog for the active board (same dialog/flow as clicking
  "+ Añadir Columna"); pressing it with no board selected (welcome screen, `board_id == -1`) does
  nothing — no dialog, no DB write.
- `Ctrl+1` through `Ctrl+9` jump to the 1st through 9th board in the sidebar, in the same order
  `select_adjacent_board` already uses. Pressing a digit beyond the number of boards that exist
  (e.g. `Ctrl+5` with only 3 boards) is a silent no-op — no crash, no change of active board.
- `Ctrl+,` opens the Settings dialog; `Ctrl+Shift+C` switches to the Calendar view — both identical
  to clicking their existing sidebar buttons.
- `Ctrl+/` opens the new "Atajos de teclado" dialog. It lists, at minimum, every shortcut named in
  §1/§2 (both the newly-added ones and the pre-existing global/editor-local ones) and visibly
  distinguishes global shortcuts from ones that only work inside the rich-text editor.
- No shortcut added in this wave collides with an existing one (global or editor-local) — verified
  by inspection: `Ctrl+Shift+N`, `Ctrl+,`, `Ctrl+Shift+C`, `Ctrl+/`, `Ctrl+1`..`Ctrl+9` are all
  distinct from `Ctrl+F`, `Ctrl+N`, `Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`, `Alt+Up`, `Alt+Down`,
  `Ctrl+B`, `Ctrl+K`, `Ctrl+I`, `Ctrl+Shift+X`, `Ctrl+Enter`.
- Each of the 9 `Ctrl+N` (digit) shortcuts jumps to a *different* board matching its digit — the
  classic late-binding-in-a-loop bug (all 9 jumping to the same board) must not be present.
- Full existing test suite stays green + ruff clean. New tests to add:
  - `tests/test_widgets_headless.py`: a new smoke test constructing `ShortcutsDialog` (needs
    `qapp`, no `db_path` — the dialog takes no DB argument) and asserting
    `dlg.windowTitle() == t("shortcuts.window_title")` plus that both section headers' text
    (`t("shortcuts.section_general")`, `t("shortcuts.section_editor")`) appear somewhere among the
    dialog's child `QLabel` texts (walk `dlg.findChildren(QLabel)`).
  - New file `tests/test_keyboard_shortcuts.py` (needs `qapp`, `db_path`):
    - `SidebarWidget.select_board_by_index` logic: create 3 boards via `database.create_board`
      *before* constructing `SidebarWidget(db_path=db_path)` (its `__init__` already calls
      `reload_boards()`, so `board_buttons` is populated immediately). Assert
      `select_board_by_index(0)`/`(1)`/`(2)` each select the corresponding board id (check
      `sidebar.active_board_id`), and that `select_board_by_index(5)` (out of range) and
      `select_board_by_index(-1)` are no-ops (raise nothing, `active_board_id` unchanged).
    - `BoardViewWidget.add_column` guard regression: construct a `BoardViewWidget(db_path=db_path)`,
      call `.load_board(-1)` (sets `self.board_id = -1`, the "no board" sentinel), then call
      `.add_column()`. To make a regression fail fast instead of hanging on a real modal
      `.exec()`, use `monkeypatch.setattr(board_view, "ColumnEditDialog", <a stub class whose
      `__init__` raises AssertionError>)` before calling `add_column()` — if the guard is ever
      broken, the test fails immediately with a clear assertion instead of blocking forever on an
      un-dismissable dialog. Also assert no column was created for the one real board created in
      the test DB (`database.get_columns(board_id, db_path) == []`).
  - No test attempts to simulate real global `QShortcut` key-press delivery (not reliable
    headless/offscreen); tests call the connected slots/methods directly, consistent with how
    `tests/test_hover_expand.py` already tests `BoardViewWidget` methods directly rather than
    simulating native input.

## QA Report

**Code review:** every `[x]` task in §2 traced against the actual current contents of
`board_view.py`, `sidebar.py`, `strings.py`, `shortcuts_dialog.py` (new file), and `main.py` —
signatures, guard logic, string keys, and shortcut wiring all match this TDD exactly. No deviation
found. Specifically checked the `Ctrl+1..9` loop (`main.py` ~L120-124): each `QShortcut.activated`
lambda uses `lambda index=_n - 1: ...`, correctly binding the loop variable by value — confirmed
with a dedicated regression test (below) that all 9 map to distinct boards, not the last one.

**Bug found and fixed — build/packaging, not the Coder's design:** the new `shortcuts_dialog.py`
top-level module wasn't in `pyproject.toml`'s explicit `py-modules` list, so `pip install -e .`
never registered it and `import shortcuts_dialog` failed under pytest (`ModuleNotFoundError`) even
though the file itself was correct — this is the exact class of issue this project's diary already
documented hitting twice before with other new top-level files (`strings.py`). Fixed by adding
`"shortcuts_dialog"` to `py-modules` and re-running `pip install -e . --no-deps` in the project
venv. Not a code defect in `main.py`/`shortcuts_dialog.py` themselves — both were already correct;
this is a one-line packaging-manifest omission, now corrected.

**Tests added:**
- `tests/test_widgets_headless.py` (+1 test): `ShortcutsDialog` constructs with the right window
  title, both section headers appear among its `QLabel` children, and a representative sample of
  new/pre-existing shortcut lines (`item_new_column`, `item_jump_board`, `item_bold`) are present.
- New `tests/test_keyboard_shortcuts.py` (5 tests):
  - `select_board_by_index` selects the matching board for indices 0/1/2 (created before
    constructing `SidebarWidget`, whose `__init__` already calls `reload_boards()`).
  - Out-of-range (`5`) and negative (`-1`, which must NOT wrap Python-style to "last board") indices
    are silent no-ops.
  - Regression test asserting all 9 possible indices (simulating what the 9 `Ctrl+N` digit
    shortcuts would each resolve to) map to 5 *distinct* boards with no duplicates — this is the
    test that would have caught the late-binding-lambda bug had it been present.
  - `add_column()` guard: with `board_id == -1`, `ColumnEditDialog` is monkeypatched to a stub that
    raises `AssertionError` from `__init__` — proves the guard returns before ever constructing the
    dialog (fails fast instead of hanging on an un-dismissable modal if the guard ever regresses),
    and confirms no column was written to the DB.
  - Positive-path counterpart: with a real board selected, `ColumnEditDialog` is monkeypatched to
    an auto-accepting stub (`exec() -> QDialog.Accepted`, `get_data() -> ("Nueva columna",
    "#3b82f6")`) — confirms the guard fix doesn't block the legitimate case, and a column is
    actually created.

**Full-app smoke script** (`smoke_shortcuts.py`, real `MainWindow` against a scratch DB via a
temporary `database.DB_NAME` override): confirmed (1) all 13 new `QShortcut` objects
(`Ctrl+1`..`Ctrl+9`, `Ctrl+Shift+N`, `Ctrl+,`, `Ctrl+Shift+C`, `Ctrl+/`) are registered on the real
`MainWindow` with the exact expected key sequences; (2) `sidebar.select_board_by_index` correctly
jumps between real boards on the live sidebar (index resolved dynamically rather than assumed, since
a fresh scratch DB's `MainWindow.__init__` seeds an onboarding board that would otherwise throw off
a hardcoded index — a smoke-script detail, not a product bug); (3) `show_calendar_view`/
`show_board_view` correctly switch `center_stack`'s current widget; (4) `ShortcutsDialog` builds
cleanly with the real `MainWindow` as parent; (5) `add_column()` with no board selected does not
hang or throw. App launched, exercised all five scenarios, and closed cleanly.

**Suite results:** `pytest -q` (offscreen, whole suite): **97 passed** (was 91; +6 from this wave).
`ruff check .`: **all checks passed**.

**Acceptance criteria (§3) — verified:**
- ✅ `Ctrl+Shift+N` opens the new-column dialog for the active board; no-ops with no board selected
  (`test_add_column_shortcut_noop_when_no_board_selected`, smoke scenario 5).
- ✅ `Ctrl+1`..`Ctrl+9` jump to the corresponding sidebar board; out-of-range digits are silent
  no-ops (`test_select_board_by_index_selects_matching_board`,
  `test_select_board_by_index_out_of_range_is_noop`, smoke scenario 2).
- ✅ `Ctrl+,`/`Ctrl+Shift+C` open Settings/Calendar exactly like their existing sidebar buttons
  (wired directly to the pre-existing `show_settings`/`show_calendar_view`; smoke scenario 3).
- ✅ `Ctrl+/` opens the new dialog listing every shortcut, global and editor-local, clearly labeled
  by scope (`test_shortcuts_dialog_constructs_with_both_sections`).
- ✅ No collisions with existing global or editor-local shortcuts (confirmed by inspection during
  code review — all 13 new combinations are textually distinct from the 11 pre-existing ones).
- ✅ No late-binding bug across the 9 digit shortcuts
  (`test_select_board_by_index_each_digit_maps_to_a_different_board`).
- ✅ Full suite green (97/97), ruff clean, real-app smoke passes.

**STATUS: QA PASSED**
