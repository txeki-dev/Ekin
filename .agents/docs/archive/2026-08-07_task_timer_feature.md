# TECHNICAL DESIGN DOCUMENT

## 1. Overview

New v0.9.0 feature: a per-task **Temporizador** (timer). In the task detail dialog, an "Iniciar"
button records the current timestamp; while running, a live elapsed-time label sits next to it
("↺ Reiniciar" restarts it to now, "✕ Detener" clears it). The same elapsed time is shown as a
badge directly on the task's board-view **card** (not just the dialog), so stale tasks are visible
without opening each one — the badge turns red once elapsed time crosses a **globally configurable
threshold** (Ajustes → hours), mirroring the overdue-due-date badge's existing red/muted styling.

Single-timestamp design (no pause/resume, no session log): `tasks.timer_started_at` is `NULL`
(never started) or an ISO datetime string. "Reiniciar" sets it to now again; "Detener" sets it back
to `NULL`. The Start/Restart/Clear button is an **instant-persist action** (writes to the DB the
moment it's clicked, like adding a diary entry or a link) — not deferred to "💾 Guardar Cambios"
like title/description/due-date/priority/tags/linked-board already are.

The threshold (`app_settings.timer_alert_hours`, default `"24"`) is global, configured in Ajustes.
Changing it does not live-recolor already-rendered cards — they pick it up next time that column
is rebuilt (board switch, drag/drop, editing a task, etc.). This is a deliberate simplification,
not an oversight: it avoids wiring a settings-changed signal down into every live `TaskCard`.

## 2. Implementation Tasks

### Database layer

- [x] `database/__init__.py` — in the existing `tasks` migration block (~L83-98, right after the
  `linked_board_id` migration), add:
  ```python
  # Migración: temporizador de una tarea (fecha/hora de inicio, o NULL si no está en marcha)
  if "timer_started_at" not in tasks_columns:
      cursor.execute("ALTER TABLE tasks ADD COLUMN timer_started_at TEXT")
  ```

- [x] `database/tasks.py` — add `t.timer_started_at` to `_TASK_SELECT_COLUMNS` (~L32-36), e.g.:
  ```python
  _TASK_SELECT_COLUMNS = """
      t.id, t.column_id, t.title, t.description, t.tag_text, t.tag_color, t.position,
      t.created_at, t.updated_at, t.due_date, t.due_time, t.recurrence, t.linked_board_id,
      t.timer_started_at,
      b.name AS linked_board_name, b.color AS linked_board_color
  """
  ```

- [x] `database/tasks.py` — add a new function, placed right after `set_task_linked_board`:
  ```python
  def set_task_timer_started(task_id, started_at, db_path=None):
      """Inicia (started_at = timestamp ISO de datetime.now()) o borra (started_at = None)
      el temporizador de una tarea."""
      with get_connection(db_path) as conn:
          conn.execute("UPDATE tasks SET timer_started_at = ? WHERE id = ?", (started_at, task_id))
          conn.commit()
  ```
  and add `"set_task_timer_started"` to `__all__` (~L7-12).

- [x] `database/snapshots.py` — `snapshot_task` (~L15-31): add
  `"timer_started_at": task.get("timer_started_at"),` to the returned dict (next to
  `"linked_board_id"`). `restore_task` (~L33-59): add `timer_started_at` to the `INSERT INTO tasks`
  column list and its value tuple:
  ```python
  cursor.execute(
      "INSERT INTO tasks (column_id, title, description, position, due_date, due_time, "
      "recurrence, linked_board_id, timer_started_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (column_id, snap["title"], snap["description"], pos, snap.get("due_date"),
       snap.get("due_time"), snap.get("recurrence", "none"), linked_board_id,
       snap.get("timer_started_at"))
  )
  ```

### Shared formatting helper

- [x] `styles.py` — add a new function, placed near `tag_pill_css` (or any of the other small
  standalone helpers):
  ```python
  def format_elapsed_time(total_seconds):
      """Da formato compacto a una duración en segundos: '45m', '3h 20m', '2d 5h'."""
      total_seconds = max(0, int(total_seconds))
      minutes = total_seconds // 60
      hours = minutes // 60
      days = hours // 24
      if days > 0:
          return f"{days}d {hours % 24}h"
      if hours > 0:
          return f"{hours}h {minutes % 60}m"
      return f"{minutes}m"
  ```

### `strings.py`

- [x] Insert right before `"task_detail.due_label"` (~L394):
  ```python
  "task_detail.timer_label": "⏱ <b>Temporizador:</b>",
  "task_detail.timer_start_btn": "▶ Iniciar",
  "task_detail.timer_restart_btn": "↺ Reiniciar",
  "task_detail.timer_clear_btn": "✕ Detener",
  "task_detail.timer_clear_tooltip": "Detiene el temporizador y quita la insignia de la tarjeta",
  "task_detail.timer_elapsed": "En marcha desde hace {elapsed}",
  ```
- [x] Insert right after `"settings.notifications_checkbox"` (~L294), before
  `"settings.geometry_hint"`:
  ```python
  "settings.timer_alert_label": "⏱ Avisar en la tarjeta si un temporizador lleva más de:",
  "settings.timer_alert_suffix": " h",
  "settings.timer_alert_hint": (
      "Las tarjetas con un temporizador activo se resaltan en rojo al superar este tiempo. "
      "Las que ya estén abiertas no se recolorean al cambiar este valor hasta que se "
      "recarguen (cambiar de tablero, editar una tarea, etc.)."
  ),
  ```

### `widgets.py` — `TaskCard` board-view badge

- [x] `TaskCard.__init__` (~L159-171): add `self._timer_alert_hours = 24` next to
  `self.board_color_hex = "#3b82f6"`.

- [x] `TaskCard.init_ui` (~L202-257): add a 4th metadata row, right after the
  `board_link_container` block and before `layout.addLayout(self.meta_layout)`:
  ```python
  # Contenedor para la insignia del temporizador (Fila 4, opcional)
  self.timer_container = QWidget()
  self.timer_container.setStyleSheet("background: transparent; border: none;")
  timer_row_layout = QHBoxLayout(self.timer_container)
  timer_row_layout.setContentsMargins(0, 0, 0, 0)
  timer_row_layout.setSpacing(6)
  self.timer_badge_label = QLabel()
  timer_row_layout.addWidget(self.timer_badge_label)
  timer_row_layout.addStretch()
  self.meta_layout.addWidget(self.timer_container)
  ```
  and add `self.update_timer_badge()` at the end of `init_ui`, alongside the existing
  `self.update_tags_and_due(...)` / `self._update_board_link()` calls.

- [x] `TaskCard` — add two new methods, placed right after `_update_board_link`:
  ```python
  def set_timer_alert_hours(self, hours):
      """Umbral (en horas) a partir del cual la insignia del temporizador se resalta en
      rojo. Se fija externamente tras construir la tarjeta -- TaskCard no tiene acceso
      directo a app_settings (ver BoardViewWidget._build_column_widget)."""
      self._timer_alert_hours = hours
      self.update_timer_badge()

  def update_timer_badge(self):
      """Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo
      si supera self._timer_alert_hours -- mismo patrón visual que la fecha de vencimiento
      vencida/no vencida en update_tags_and_due."""
      started_at = self.task_data.get("timer_started_at")
      if not started_at:
          self.timer_container.hide()
          return
      try:
          started = datetime.fromisoformat(started_at)
      except ValueError:
          self.timer_container.hide()
          return

      elapsed = datetime.now() - started
      elapsed_hours = elapsed.total_seconds() / 3600
      is_stale = elapsed_hours >= self._timer_alert_hours

      self.timer_badge_label.setText(f"⏱ {styles.format_elapsed_time(elapsed.total_seconds())}")
      if is_stale:
          dr, dg, db = hex_to_rgb(styles.COLORS['danger'])
          self.timer_badge_label.setStyleSheet(
              f"color: {styles.COLORS['danger']}; font-weight: bold; font-size: 10px; "
              f"background-color: rgba({dr}, {dg}, {db}, 0.15); border-radius: 4px; padding: 2px 4px;"
          )
      else:
          mr, mg, mb = hex_to_rgb(styles.COLORS['text_muted'])
          self.timer_badge_label.setStyleSheet(
              f"color: {styles.COLORS['text_muted']}; font-size: 10px; "
              f"background-color: rgba({mr}, {mg}, {mb}, 0.15); border-radius: 4px; padding: 2px 4px;"
          )
      self.timer_container.show()
  ```
  (`datetime` and `hex_to_rgb` are already imported in `widgets.py`; no new imports needed here.)

### `board_view.py` — wiring + periodic badge refresh

- [x] Imports (~L1): add `QTimer` to the existing
  `from PySide6.QtCore import Qt, Signal, QSize` line.

- [x] `BoardViewWidget.__init__` (near the other timer/tracking attributes, e.g. right after
  `self._hover_expanded_column_id = None`): add
  ```python
  self._timer_badge_refresh_timer = QTimer(self)
  self._timer_badge_refresh_timer.timeout.connect(self.refresh_timer_badges)
  self._timer_badge_refresh_timer.start(60_000)  # refresca las insignias cada 60s
  ```

- [x] `_build_column_widget` (~L322-350): right after computing `col_widget = ColumnWidget(...)`
  (i.e. before or alongside the existing signal-connection block), add one line to read the
  threshold once per call:
  ```python
  timer_alert_hours = int(database.get_setting("timer_alert_hours", "24", self.db_path))
  ```
  and inside the `if not col_data.get("collapsed"):` task-card loop, right after
  `card.set_card_style(board_info["color"])`, add:
  ```python
  card.set_timer_alert_hours(timer_alert_hours)
  ```

- [x] Add a new method, placed near `_rebuild_single_column`:
  ```python
  def refresh_timer_badges(self):
      """Refresca la insignia de tiempo transcurrido en todas las tarjetas con un
      temporizador activo, sin recargar el tablero -- el tiempo transcurrido cambia solo
      con el paso del tiempo, no hay datos nuevos que leer de la BD; solo hace falta
      recalcular el texto/color ya mostrado en cada TaskCard viva."""
      for col_widget in self.column_widgets.values():
          for card in col_widget.findChildren(TaskCard):
              card.update_timer_badge()
  ```

### `detail_dialog/task_detail_dialog.py` — dialog UI + instant-persist actions

- [x] Imports (~L1, ~L8): add `QTimer` to the existing
  `from PySide6.QtCore import Qt, QDate, QTime, QUrl, QSize` line; add a new line
  `from datetime import datetime` near the top (alongside the other imports, before `import database`).

- [x] `__init__` (~L20-33): add `self._timer_started_at = None` next to the other state attributes
  (`self.current_tags`, `self.task_deleted`, `self.modified`), and — after `self.init_ui()` /
  `self.load_task_data()` — start a periodic UI-only refresh (no DB read) so the elapsed label
  ticks up while the dialog stays open:
  ```python
  self._timer_refresh_timer = QTimer(self)
  self._timer_refresh_timer.timeout.connect(self._refresh_timer_ui)
  self._timer_refresh_timer.start(30_000)
  ```

- [x] `init_ui` (~L60-62): insert a new "2.5 Temporizador" section between
  `left_layout.addWidget(self.desc_input)` and the `# 3. Fecha de Vencimiento` comment:
  ```python
  # 2.5 Temporizador
  timer_section = QWidget()
  timer_section_layout = QHBoxLayout(timer_section)
  timer_section_layout.setContentsMargins(0, 0, 0, 0)
  timer_section_layout.setSpacing(10)

  timer_section_layout.addWidget(QLabel(t("task_detail.timer_label")))

  self.timer_toggle_btn = QPushButton(t("task_detail.timer_start_btn"))
  self.timer_toggle_btn.setCursor(Qt.PointingHandCursor)
  self.timer_toggle_btn.clicked.connect(self._on_timer_toggle_clicked)
  timer_section_layout.addWidget(self.timer_toggle_btn)

  self.timer_clear_btn = QPushButton(t("task_detail.timer_clear_btn"))
  self.timer_clear_btn.setCursor(Qt.PointingHandCursor)
  self.timer_clear_btn.setToolTip(t("task_detail.timer_clear_tooltip"))
  self.timer_clear_btn.clicked.connect(self._on_timer_clear_clicked)
  timer_section_layout.addWidget(self.timer_clear_btn)

  self.timer_elapsed_label = QLabel("")
  self.timer_elapsed_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
  timer_section_layout.addWidget(self.timer_elapsed_label)
  timer_section_layout.addStretch()

  left_layout.addWidget(timer_section)
  ```

- [x] Add three new methods, placed right after `save_changes` (or any convenient spot near the
  other instant-persist handlers like `add_log_entry`/`remove_link`):
  ```python
  def _on_timer_toggle_clicked(self):
      """Inicia el temporizador, o lo reinicia a ahora si ya estaba en marcha. Acción
      instantánea (como añadir una nota al diario o un enlace): se persiste en el
      momento, no espera a "Guardar Cambios"."""
      self._timer_started_at = datetime.now().isoformat()
      database.set_task_timer_started(self.task_id, self._timer_started_at, self.db_path)
      self.modified = True
      self._refresh_timer_ui()

  def _on_timer_clear_clicked(self):
      """Detiene y borra el temporizador: deja de contar y quita la insignia de la tarjeta."""
      self._timer_started_at = None
      database.set_task_timer_started(self.task_id, None, self.db_path)
      self.modified = True
      self._refresh_timer_ui()

  def _refresh_timer_ui(self):
      """Actualiza el botón y la etiqueta de tiempo transcurrido según self._timer_started_at.
      Se llama al cargar la tarea, tras cada acción, y cada 30s mientras el diálogo está
      abierto (self._timer_refresh_timer) para que el contador avance en vivo."""
      if self._timer_started_at:
          self.timer_toggle_btn.setText(t("task_detail.timer_restart_btn"))
          self.timer_clear_btn.show()
          try:
              started = datetime.fromisoformat(self._timer_started_at)
              elapsed = datetime.now() - started
              self.timer_elapsed_label.setText(
                  t("task_detail.timer_elapsed", elapsed=styles.format_elapsed_time(elapsed.total_seconds()))
              )
          except ValueError:
              self.timer_elapsed_label.setText("")
      else:
          self.timer_toggle_btn.setText(t("task_detail.timer_start_btn"))
          self.timer_clear_btn.hide()
          self.timer_elapsed_label.setText("")
  ```

- [x] `load_task_data` (~L305-351): right after `self.desc_input.setHtml(task["description"] or "")`,
  add:
  ```python
  self._timer_started_at = task.get("timer_started_at")
  self._refresh_timer_ui()
  ```

### `settings_dialog.py` — configurable threshold

- [x] Imports (~L6-8): add `QSpinBox` to the existing
  `from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QFrame)` line.

- [x] `__init__` (~L49-57): right after the existing `self.notif_chk` block
  (`layout.addWidget(self.notif_chk)`) and before the `QFrame` `HLine` separator, add:
  ```python
  # --- Temporizador de tareas ---
  timer_row = QHBoxLayout()
  timer_row.addWidget(QLabel(t("settings.timer_alert_label")))
  self.timer_alert_spin = QSpinBox()
  self.timer_alert_spin.setRange(1, 720)
  self.timer_alert_spin.setSuffix(t("settings.timer_alert_suffix"))
  self.timer_alert_spin.setValue(int(database.get_setting("timer_alert_hours", "24", self.db_path)))
  self.timer_alert_spin.valueChanged.connect(
      lambda hours: database.set_setting("timer_alert_hours", str(hours), self.db_path)
  )
  timer_row.addWidget(self.timer_alert_spin)
  timer_row.addStretch()
  layout.addLayout(timer_row)

  timer_hint = QLabel(t("settings.timer_alert_hint"))
  timer_hint.setWordWrap(True)
  timer_hint.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
  layout.addWidget(timer_hint)
  ```

## 3. Acceptance Criteria

- Opening a task with no timer shows "▶ Iniciar" and no elapsed label; the card shows no timer
  badge.
- Clicking "▶ Iniciar" immediately persists `timer_started_at` to the DB (verified by re-reading
  via `database.get_task`, independent of clicking "Guardar Cambios" or even closing the dialog
  via "Cerrar" instead), sets `self.modified = True`, switches the button to "↺ Reiniciar", shows
  the elapsed label, and shows the "✕ Detener" button.
- Clicking "↺ Reiniciar" while running updates `timer_started_at` to a new, later timestamp
  (persisted instantly) — elapsed time visibly resets.
- Clicking "✕ Detener" clears `timer_started_at` back to `None` (persisted instantly), hides the
  elapsed label and the "✕ Detener" button, reverts the toggle button to "▶ Iniciar".
- The elapsed label's text updates over time without needing to close/reopen the dialog (driven by
  `self._timer_refresh_timer`).
- The board card shows a "⏱ <elapsed>" badge whenever `timer_started_at` is set, styled muted
  (`text_muted`) under the configured threshold and in `danger` red (bold) at/above it — mirroring
  exactly the due-date overdue/not-overdue styling. No badge when `timer_started_at` is `None`.
- Changing the threshold in Ajustes (`QSpinBox`, range 1–720h) persists instantly to
  `app_settings.timer_alert_hours` and is picked up by any newly-built column (board switch,
  drag/drop, task edit) — it does not need to live-recolor cards already on screen.
- `BoardViewWidget.refresh_timer_badges()` (ticking every 60s) keeps visible timer badges'
  elapsed text current without a full board reload and without any DB query.
- `snapshot_task`/`restore_task` round-trip `timer_started_at` — deleting a task with a running
  timer and undoing (Ctrl+Z) restores the same `timer_started_at`, not `None`.
- `format_elapsed_time` produces the documented compact format: minutes-only under 1h, "Hh Mm"
  under 24h, "Dd Hh" at/above 24h. Never negative, never crashes on `0`.
- `init_db()` migration is idempotent (adding `timer_started_at` to an already-migrated DB is a
  no-op) and doesn't break any existing task row (`timer_started_at` is `NULL` for pre-existing
  tasks, which the app already treats as "no timer").
- Full existing test suite (110 tests before this wave) + ruff stay green. New tests to add,
  following this project's established conventions (temp `db_path` fixture, `qapp` fixture for
  anything constructing a Qt widget, monkeypatched modal-opening calls where needed so nothing can
  hang headless):
  - `tests/test_database.py` (or a new focused test module): `set_task_timer_started` sets and
    clears the column; `get_task`/`get_tasks` expose `timer_started_at`; migration idempotency
    (`init_db` twice doesn't error, doesn't wipe existing `timer_started_at` values); snapshot/
    restore round-trip (create a task, start its timer, snapshot, delete, restore, assert the
    restored task's `timer_started_at` matches the original).
  - A new test module (e.g. `tests/test_timer_formatting.py`) for `styles.format_elapsed_time`:
    boundary values (`0` → `"0m"`, `59` → `"0m"`, `60` → `"1m"`, `3599` → `"59m"`, `3600` →
    `"1h 0m"`, `86399` → `"23h 59m"`, `86400` → `"1d 0h"`, a multi-day value), and that negative
    input never produces a negative-looking string (clamped to `0`).
  - `tests/test_widgets_headless.py` or a new module: `TaskCard.update_timer_badge()` hides the
    badge when `timer_started_at` is absent; shows it with muted styling under the threshold and
    danger styling at/above it (construct with `timer_started_at` set to a known past ISO
    timestamp and a small `set_timer_alert_hours` value to deterministically cross the threshold
    without waiting).
  - A new test module for `BoardViewWidget`: `_build_column_widget` applies the configured
    `timer_alert_hours` to every card it creates; `refresh_timer_badges()` updates an existing
    card's badge text/style in place (mutate the card's `task_data["timer_started_at"]` — or
    change the configured threshold and call `set_timer_alert_hours` again — and confirm
    `refresh_timer_badges()` reflects it) without touching `column_widgets` identity or requiring
    a DB round-trip.
  - `TaskDetailDialog`: constructing with a task that has/doesn't have `timer_started_at` shows
    the right initial button/label state; clicking `_on_timer_toggle_clicked`/
    `_on_timer_clear_clicked` (call directly, don't simulate a real click if that's more direct)
    persists correctly to the DB and sets `self.modified`.
  - `SettingsDialog`: `timer_alert_spin` initializes from `app_settings`, and changing its value
    persists instantly via `database.get_setting`.
- Full-app smoke check (per this project's convention) against a real `MainWindow` + scratch DB:
  start a timer on a real task via the dialog flow, confirm the board card shows the badge with
  muted styling, then lower the alert threshold below the elapsed time and rebuild that column
  (e.g. via any action that calls `_build_column_widget` again) to confirm the badge turns red;
  confirm `refresh_timer_badges()` runs without error on a fully-populated real board.

## QA Report

**Code review:** every `[x]` task in §2 traced against the actual current contents of
`database/__init__.py`, `database/tasks.py`, `database/snapshots.py`, `styles.py`, `strings.py`,
`widgets.py`, `board_view.py`, `detail_dialog/task_detail_dialog.py`, `settings_dialog.py` —
migration, `_TASK_SELECT_COLUMNS`, `set_task_timer_started` + `__all__`, snapshot/restore,
`format_elapsed_time`, all 9 new `strings.py` keys, `TaskCard`'s 4th metadata row +
`set_timer_alert_hours`/`update_timer_badge`, `BoardViewWidget`'s `QTimer` + threshold read +
`refresh_timer_badges`, the dialog's "2.5 Temporizador" section + 3 new handlers + `load_task_data`
wiring, and `SettingsDialog`'s `QSpinBox` all match this TDD exactly, byte-for-byte on the styling
blocks (confirmed identical `danger`/`text_muted` rgba pattern to the existing due-date badge).

**Pre-existing suite regression check:** ran the full 110-test suite that existed *before* this
wave, prior to writing any new tests, to confirm the DB migration and all touched files introduced
no regressions on their own — all 110 passed unmodified.

**Tests added (35 new, 145 total):**
- `tests/test_timer_formatting.py` (11 tests, pure logic, no `qapp` needed): `format_elapsed_time`
  boundary values exactly as specified (0/59/60/3599/3600/9000/86399/86400/multi-day), negative
  input clamped to `0`, float input (matches `timedelta.total_seconds()`'s real return type) not
  rejected.
- `tests/test_database.py` (+7 tests): default `None`, set/clear round-trip, `get_tasks` exposure,
  migration idempotency with an existing non-null value preserved, snapshot/restore round-trip
  both with and without a timer set.
- `tests/test_widgets_headless.py` (+13 tests): `TaskCard` timer badge hidden with no timer, muted
  under threshold, danger at/above threshold, re-evaluates correctly when
  `set_timer_alert_hours` changes on a live card, hides gracefully on an unparseable
  `timer_started_at` (defensive `except ValueError` path exercised directly, not just by
  inspection); `TaskDetailDialog` initial state with/without an existing timer, start persists
  instantly + sets `modified`, restart advances the timestamp, clear persists instantly and
  reverts all three widgets (button text, elapsed label, clear-button visibility);
  `SettingsDialog.timer_alert_spin` reflects a saved value, defaults to 24, and persists instantly
  on change.
- `tests/test_timer_board_view.py` (5 tests, new file): `_build_column_widget` applies a
  non-default configured threshold to every card (and defaults to 24 when unset);
  `refresh_timer_badges()` updates an already-existing card's styling in place *without*
  replacing its `ColumnWidget` (identity check, same pattern already used for the hover-expand
  regression test) and without any DB write; no-ops safely both on a board with zero active
  timers and on the `board_id == -1` welcome screen (`column_widgets` empty).

**Full-app smoke script** (`smoke_timer_feature.py`, real `MainWindow` against a scratch DB):
(1) started a timer through the real `TaskDetailDialog` flow and confirmed instant persistence;
(2) reloaded the board and confirmed the task's card shows the "⏱ <elapsed>" badge in muted
styling, while a sibling task with no timer shows no badge at all; (3) lowered
`timer_alert_hours` to `0` via `database.set_setting` (equivalent to the Ajustes spinbox) and
called `_rebuild_single_column` on just that column, confirming the badge switched to danger/red
styling; (4) called `refresh_timer_badges()` on the fully-populated real board with no exception.
One incidental finding purely in the smoke *script* itself, not the app: printing the ⏱ emoji via
a bare `print()` on this Windows console raised `UnicodeEncodeError` under the default `cp1252`
stdout codec — fixed by running the script with `PYTHONIOENCODING=utf-8`. This is a test-harness/
console concern only; the application itself never writes to stdout with these characters (they
only ever render inside Qt widgets, which handle Unicode natively regardless of console codepage).

**Suite results:** `pytest -q` (offscreen, whole suite): **145 passed** (was 110; +35 from this
wave). `ruff check .`: **all checks passed**.

**Acceptance criteria (§3) — verified:**
- ✅ All dialog button/label state transitions (no timer → started → restarted → cleared) covered
  by direct tests and the smoke script's dialog-flow step.
- ✅ Instant persistence (not deferred to "Guardar Cambios") — every dialog test calls the handler
  directly and reads back via a fresh `database.get_task`, with no `save_changes()`/`accept()` in
  between.
- ✅ Live elapsed label ticking is driven by `_timer_refresh_timer` (code-reviewed; not
  independently re-tested via a real 30s wait, which would be impractical — the underlying
  `_refresh_timer_ui` logic it calls is already covered directly).
- ✅ Board card badge presence/absence and muted/danger styling — unit-tested exhaustively and
  confirmed end-to-end on the real app in the smoke script.
- ✅ Threshold configuration persists instantly and is picked up by newly-built columns, not
  live-recolored on already-rendered cards — matches the documented deliberate simplification.
- ✅ `refresh_timer_badges()` is DB-free and identity-preserving (no column reconstruction).
- ✅ `snapshot_task`/`restore_task` round-trip `timer_started_at` in both directions (present and
  absent).
- ✅ `format_elapsed_time` matches the documented format spec across all boundaries.
- ✅ Migration idempotency confirmed both via a dedicated test and implicitly by the full suite
  running `init_db` fresh per test with no failures.
- ✅ Full suite green (145/145), ruff clean, full-app smoke passes all scenarios.

**STATUS: QA PASSED**
