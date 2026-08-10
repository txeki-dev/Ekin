# TECHNICAL DESIGN DOCUMENT

## 1. Overview
Today the "🔗 Enlaces / adjuntos" section in `TaskDetailDialog` (`detail_dialog/task_detail_dialog.py`)
only lets the user type/paste a string into `link_url_input` and click ➕. The `task_links.url` column
was already designed to hold *either* a URL or a file path (see its schema comment in
`database/__init__.py`), but the UI never exposed a way to browse for a local file, and the open-link
handler (`QDesktopServices.openUrl(QUrl(url))`) is broken for raw local paths (e.g. `C:\Users\...\x.pdf`)
because a bare Windows path is not a well-formed `QUrl` — it needs `QUrl.fromLocalFile(...)`.

This feature adds a **📁 Browse** button next to the existing URL/label inputs that opens the native
OS file picker (`QFileDialog.getOpenFileName`) so the user can search the PC and attach a local file,
fixes link-opening so local paths actually open, and visually distinguishes web links (🔗) from local
attachments (📎), including a "file not found" indicator/warning for attachments that have moved or
been deleted since they were added.

**No database schema change.** `task_links.url` already accepts any string; whether a given link is a
web URL or a local path is classified by a scheme heuristic at render/open time (not persisted), so
`database/links.py`, `database/snapshots.py`, and `database/board_ops.py` are **out of scope** —
do not touch them. `widgets.py`/`board_view.py` (the board-card widget) are also **out of scope**: this
feature only touches the task-detail dialog's existing links section, mirroring how tags/priority/
board-link are all edited there without a dedicated card-level indicator.

## 2. Implementation Tasks

- [x] `detail_dialog/task_detail_dialog.py` — imports: add `import os` at the top of the file; add
  `QFileDialog` to the existing `from PySide6.QtWidgets import (...)` block (`QMessageBox` and `QUrl`
  are already imported).

- [x] `detail_dialog/task_detail_dialog.py` — add a module-level classifier function (above the
  `TaskDetailDialog` class, so it's importable and unit-testable standalone):
  ```python
  _WEB_LINK_SCHEMES = ("http://", "https://", "ftp://", "mailto:", "file://")

  def _is_local_link(url):
      """True unless the string starts with a recognized web scheme (case-insensitive)."""
      return not url.lower().startswith(_WEB_LINK_SCHEMES)
  ```

- [x] `detail_dialog/task_detail_dialog.py` — in the links section UI (currently around line 224-239,
  the `add_link_row` `QHBoxLayout` holding `self.link_url_input`, `self.link_label_input`, and
  `add_link_btn`), insert a new browse button **before** `self.link_url_input` so the row reads
  `[📁 browse][url][label][➕]`:
  ```python
  browse_link_btn = QPushButton("📁")
  browse_link_btn.setFixedWidth(30)
  browse_link_btn.setCursor(Qt.PointingHandCursor)
  browse_link_btn.setToolTip(t("task_detail.browse_file_tooltip"))
  browse_link_btn.clicked.connect(self.browse_local_file)
  add_link_row.addWidget(browse_link_btn)
  ```
  Store it as `self.browse_link_btn` (not a local var) so tests/other code can reference it, matching
  how `add_link_btn`'s sibling widgets are otherwise accessed via `self.*`.

- [x] `detail_dialog/task_detail_dialog.py` — add two new methods near `add_link`/`remove_link`
  (split into two so the native-dialog call is separated from the testable logic):
  ```python
  def browse_local_file(self):
      path, _ = QFileDialog.getOpenFileName(self, t("task_detail.browse_file_title"))
      if path:
          self._apply_browsed_file(path)

  def _apply_browsed_file(self, path):
      self.link_url_input.setText(path)
      if not self.link_label_input.text().strip():
          self.link_label_input.setText(os.path.basename(path))
  ```

- [x] `detail_dialog/task_detail_dialog.py` — rewrite `_build_link_row(self, link)` to distinguish
  local attachments from web links and to warn on a missing file:
  ```python
  def _build_link_row(self, link):
      row = QWidget()
      row.setStyleSheet("background: transparent;")
      h = QHBoxLayout(row)
      h.setContentsMargins(0, 0, 0, 0)
      h.setSpacing(6)

      is_local = _is_local_link(link["url"])
      missing = is_local and not os.path.exists(link["url"])
      icon = "📎" if is_local else "🔗"

      open_btn = QPushButton(icon + " " + (link["label"] or link["url"]))
      open_btn.setCursor(Qt.PointingHandCursor)
      open_btn.setToolTip(
          t("task_detail.link_missing_tooltip", path=link["url"]) if missing else link["url"]
      )
      text_color = styles.COLORS["danger"] if missing else "#60a5fa"
      open_btn.setStyleSheet(
          f"QPushButton {{ background: transparent; border: none; color: {text_color}; text-align: left; }}"
          "QPushButton:hover { text-decoration: underline; }"
      )
      open_btn.clicked.connect(lambda _=False, u=link["url"], loc=is_local: self._open_link(u, loc))
      h.addWidget(open_btn, 1)

      del_btn = QPushButton()
      del_btn.setFixedSize(18, 18)
      del_btn.setCursor(Qt.PointingHandCursor)
      del_btn.setToolTip(t("task_detail.delete_link_tooltip"))
      del_btn.setIcon(make_glyph_icon("cross", "#ef4444", 12))
      del_btn.setIconSize(QSize(12, 12))
      del_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
      del_btn.clicked.connect(lambda _=False, lid=link["id"]: self.remove_link(lid))
      h.addWidget(del_btn)
      return row

  def _open_link(self, url, is_local):
      qurl = QUrl.fromLocalFile(url) if is_local else QUrl(url)
      if not QDesktopServices.openUrl(qurl):
          QMessageBox.warning(
              self, t("task_detail.link_open_failed_title"), t("task_detail.link_open_failed_msg")
          )
  ```
  `add_link()` and `remove_link()` keep their current bodies unchanged — they already work for any
  string in `link_url_input`, whether typed or filled in by `browse_local_file`.

- [x] `strings.py` — add these five keys next to the existing `task_detail.link*`/`no_links_hint`
  entries (around line 430-451):
  ```python
  "task_detail.browse_file_tooltip": "Buscar un archivo local del PC para adjuntar",
  "task_detail.browse_file_title": "Seleccionar archivo para adjuntar",
  "task_detail.link_missing_tooltip": "⚠ Archivo no encontrado: {path}",
  "task_detail.link_open_failed_title": "No se pudo abrir",
  "task_detail.link_open_failed_msg": "No se pudo abrir el enlace o el archivo adjunto. Puede que se haya movido o eliminado.",
  ```
  (`{path}` is substituted via the existing `t(key, **kwargs)` `.format()`-style mechanism already used
  elsewhere in `strings.py` — follow the same interpolation convention as other parametrized keys.)

- [x] `tests/test_widgets_headless.py` — add a new section (mirroring the existing
  `# --- TaskDetailDialog: temporizador (v0.9.0) ---` section's style/fixtures) with:
  - `test_is_local_link_classifies_urls_vs_paths` — pure function test (no `qapp` needed): assert
    `_is_local_link("https://x.com")`, `_is_local_link("http://x.com")`, `_is_local_link("mailto:a@b.com")`,
    `_is_local_link("file://C:/x.txt")` are all `False`; assert `_is_local_link(r"C:\Users\foo\bar.pdf")`
    and `_is_local_link("/home/user/file.txt")` are both `True`. Import `_is_local_link` from
    `detail_dialog.task_detail_dialog`.
  - `test_browse_local_file_fills_url_and_autofills_empty_label(qapp, db_path)` — build a
    `TaskDetailDialog` via the existing `_make_task(db_path)` helper, call
    `dlg._apply_browsed_file(r"C:\docs\report.pdf")`, assert `dlg.link_url_input.text() ==
    r"C:\docs\report.pdf"` and `dlg.link_label_input.text() == "report.pdf"`.
  - `test_browse_local_file_does_not_overwrite_existing_label(qapp, db_path)` — set
    `dlg.link_label_input.setText("Mi informe")` first, then call `_apply_browsed_file(...)`, assert the
    label is still `"Mi informe"`.
  - `test_add_link_with_local_path_renders_with_attachment_icon(qapp, db_path, tmp_path)` — create a
    real file under `tmp_path`, set `dlg.link_url_input.setText(str(file_path))`, call `dlg.add_link()`,
    then find the rendered link row's `QPushButton` (via `dlg.links_container.findChildren(QPushButton)`)
    and assert its text starts with `"📎"`.
  - `test_add_link_with_web_url_renders_with_link_icon(qapp, db_path)` — same shape but
    `dlg.link_url_input.setText("https://example.com")`; assert the rendered button text starts with
    `"🔗"`.
  - `test_open_link_warns_when_target_cannot_be_opened(qapp, db_path, monkeypatch)` — monkeypatch
    `task_detail_dialog.QDesktopServices.openUrl` to a lambda returning `False`, and
    `task_detail_dialog.QMessageBox.warning` to append to a list instead of showing a real modal
    (same monkeypatch-a-modal-call pattern already used in `tests/test_last_active_column.py` and
    `tests/test_keyboard_shortcuts.py`); call `dlg._open_link(r"C:\nope.txt", True)`; assert the warning
    list has exactly one entry.
  - `test_open_link_no_warning_when_openurl_succeeds(qapp, db_path, monkeypatch)` — same setup but
    `openUrl` returns `True`; assert the warning list stays empty.

## 3. Acceptance Criteria
- The links-section UI now shows four controls in one row: 📁 browse, URL/path text field, label text
  field, ➕ add — in that order — with no change to the existing ➕/add-link persistence behavior
  (`database.add_task_link` signature and call sites are untouched).
- Clicking 📁 opens the native "open file" dialog; selecting a file fills the URL field with its full
  path and, **only if the label field is currently empty**, auto-fills the label with the file's base
  name. Cancelling the dialog changes nothing.
- Existing web links (`http://`, `https://`, `ftp://`, `mailto:`, `file://`) keep rendering with the 🔗
  icon and keep opening exactly as before (`QUrl(url)` passed to `QDesktopServices.openUrl`).
- Links whose stored value is not a recognized web scheme are treated as local file attachments:
  rendered with a 📎 icon, and opened via `QUrl.fromLocalFile(url)` (so plain Windows paths like
  `C:\Users\...\file.pdf` actually launch in the OS-associated app, which they do not today).
- A local attachment whose file no longer exists on disk (`os.path.exists` is `False`) is rendered with
  `styles.COLORS["danger"]` text and a tooltip stating the file was not found, but remains clickable
  (deletable via the existing del button either way).
- If `QDesktopServices.openUrl(...)` returns `False` for any link (local or web), a `QMessageBox.warning`
  is shown to the user instead of failing silently; if it returns `True`, no dialog appears.
- No changes to `database/*.py` (schema, `add_task_link`/`get_task_links`/`snapshot_task`/`restore_task`/
  `_duplicate_task_into_column` all untouched — verify via `git diff --stat` before marking this done),
  `widgets.py`, or `board_view.py`.
- Full test suite passes, including the new tests above, with a clean process exit code (per the
  existing `qapp` fixture teardown fix — no `STATUS_HEAP_CORRUPTION` regression). `ruff` stays clean.
- All five new `strings.py` keys are used via `t(...)` (no hardcoded Spanish literals introduced in
  `task_detail_dialog.py` for this feature) and follow the existing flat-key naming convention
  (`task_detail.<name>`).

## QA Report

**Verdict: PASS.** All acceptance criteria in §3 validated against the actual implementation, not
assumptions. Full trace below.

**Code trace (`detail_dialog/task_detail_dialog.py`):**
- Imports: `import os` (line 1) and `QFileDialog` added to the `QtWidgets` import (line 7) — exact
  match to task 1.
- `_WEB_LINK_SCHEMES`/`_is_local_link` (lines 20-25): module-level, importable standalone — confirmed
  via `import detail_dialog.task_detail_dialog as m; m._is_local_link(...)` in the new tests.
- Links row order (lines 232-253): `browse_link_btn` (📁) → `link_url_input` → `link_label_input` →
  `add_link_btn` (➕), stored as `self.browse_link_btn` — matches task 3 and AC bullet 1 exactly.
- `_build_link_row`/`_open_link`/`browse_local_file`/`_apply_browsed_file` (lines 728-788): matches the
  TDD's prescribed code verbatim.

**Executed verification (not just static review):**
1. `pytest -q` (full suite, independent re-run): **166 passed**, exit code **0** — up from the
   pre-existing 159, confirming the 7 new tests registered and pass, and confirming no regression of
   the previously-fixed `STATUS_HEAP_CORRUPTION` clean-exit issue.
2. `ruff check .` (whole project, not just changed files): **all checks passed**.
3. `git diff --stat`: only `detail_dialog/task_detail_dialog.py`, `strings.py`,
   `tests/test_widgets_headless.py` changed. `database/*.py`, `widgets.py`, `board_view.py` confirmed
   untouched — satisfies the "out of scope" constraint from §1 and the AC bullet requiring this check.
4. **Manual scenario not covered by an automated test** (the Architect's own §2 test list omitted a
   dedicated "missing file" render test even though §3 requires the behavior): built a real
   `TaskDetailDialog` against a temp DB with a `task_links` row pointing at a nonexistent path
   (`C:\this\path\does\not\exist.pdf`). Confirmed by inspecting the live widget:
   - Button text: `📎 Missing file` (attachment icon, not 🔗).
   - Tooltip: `⚠ Archivo no encontrado: C:\this\path\does\not\exist.pdf` (via the new
     `link_missing_tooltip` key, `{path}` interpolated correctly).
   - Stylesheet contains `color: #ef4444` (`styles.COLORS["danger"]`, confirmed identical in both the
     DARK and LIGHT palettes, so this is correct in both themes).
   This closes the gap between the Architect's test-list (§2) and acceptance criteria (§3) — recommend
   folding a permanent regression test for this into a future pass, but the behavior itself is
   confirmed correct today so it does not block this wave.

**Edge cases considered, no bugs found:**
- Cancelling the native file dialog: `QFileDialog.getOpenFileName` returns `("", "")` on cancel;
  `browse_local_file`'s `if path:` guard correctly no-ops — nothing is overwritten.
- Whitespace-only label before browsing: `_apply_browsed_file` uses
  `.text().strip()`, so a whitespace-only label is (correctly) treated as empty and gets
  auto-filled, consistent with `add_link()`'s own `.strip() or None` treatment of the label field.
- Re-browsing a second file without clearing an already-auto-filled label leaves the stale first
  label in place (by design — `_apply_browsed_file` only fills an *empty* label, per AC bullet 2,
  and `test_browse_local_file_does_not_overwrite_existing_label` locks in exactly this behavior).
  Noted as an intentional, spec-compliant behavior, not a defect.
- Web links with unrecognized schemes (e.g. `sftp://`, `git://`) fall through to the "local path"
  branch and get an `os.path.exists` check (always `False` for those) — cosmetically mislabeled as a
  "missing local file" rather than a broken web link. Explicitly out of scope: §3's AC bullet 3 only
  requires correct handling of the five listed schemes, and none of those are affected.
- Existing `add_task_link`/`get_task_links`/`snapshot_task`/`restore_task`/
  `_duplicate_task_into_column`/`get_task_links_bulk` call sites and their existing test coverage
  (`tests/test_database.py`) are unaffected — confirmed no signature or behavior change in
  `database/links.py`, `database/snapshots.py`, `database/board_ops.py`.

No blocking issues found. Ready for Architect final review / archiving.
