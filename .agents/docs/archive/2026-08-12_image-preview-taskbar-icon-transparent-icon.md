# TECHNICAL DESIGN DOCUMENT

## 1. Overview
Three independent, user-requested changes bundled into one wave:

1. **Click-to-enlarge pasted images.** Images pasted into the task description or the
   diary/chat currently render tiny and inline, with no way to see them bigger. Clicking one
   (in the description editor, the diary compose box, an in-progress diary edit, or an
   already-posted diary entry) should open it in a larger modal view.
2. **Taskbar icon showing as the generic Python icon on a second PC.** `main.py` already
   resolves `ekin_icon.ico`/`.png` by absolute path and sets an explicit AppUserModelID before
   `QApplication` is created — both fixed in two prior commits (2026-07-10, 2026-07-29)
   targeting this exact bug class. The code is correct on inspection. The most likely
   explanation is Windows-side icon-cache staleness on that other PC (it probably ran Ekin
   for the first time before the 2026-07-29 fix, and Windows cached the wrong icon under the
   `"EkinKanban.TrelloLite"` AppUserModelID identity — a cache nothing has since invalidated).
   No code change can force-clear another machine's OS icon cache, but bumping the
   AppUserModelID string makes Windows treat the app as a new identity and re-resolve the
   icon fresh instead of serving the stale cached one. The Docs phase must clearly tell the
   user this is what's happening and what to do on the affected PC (`git pull` + relaunch;
   if the icon still doesn't refresh, unpin/re-pin the taskbar icon or reboot, since Windows
   caches icons per-identity outside any app's control).
3. **Icon redesign (already done, not a Coder task — verify only).** `ekin_icon.png`/`.ico`
   had a white/near-white baked-in background, drop shadow, and a stray white shape instead
   of true transparency. Already fixed directly via Pillow: per-pixel "whiteness" computed as
   `min(r, g, b)`, with `alpha = original_alpha * ramp(whiteness)` linearly feathered between
   170 (fully opaque, keep) and 225 (fully transparent, remove) — chosen from a histogram
   showing a low-density valley in that range separating the dark navy/cyan artwork from the
   white background/shadow. `ekin_icon.png` (RGBA) and `ekin_icon.ico` (16/24/32/48/64/128/256,
   verified structurally multi-res) were regenerated from the processed master and visually
   verified (composited over solid red and over a dark taskbar-like background) before being
   written to disk. `git status` currently shows both files modified, uncommitted.

**Explicit non-goal:** the "enlarge" view shows the image at whatever resolution was stored
at paste time (already scaled down to fit the chat/description width via
`image_width_provider`, see `markdown_edit.py`) — not a separately-kept original full-res
copy. Storing both a thumbnail and a full-res original is out of scope; the ask is "see it
bigger than the tiny inline size," not "recover full source resolution."

## 2. Implementation Tasks

- [x] `detail_dialog/image_preview_dialog.py` (**new file**): a small, reusable modal dialog
  plus two module-level helper functions. Exact contents:
  ```python
  from PySide6.QtCore import Qt, QByteArray
  from PySide6.QtGui import QPixmap
  from PySide6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

  import styles
  from strings import t


  class ImagePreviewDialog(QDialog):
      """Muestra una imagen pegada en la descripción/diario a tamaño grande. Se cierra
      con un clic en cualquier parte de la ventana, con Esc, o con el botón de cerrar."""

      def __init__(self, pixmap, parent=None):
          super().__init__(parent)
          self.setWindowTitle(t("image_preview.window_title"))
          self.setModal(True)
          self.setStyleSheet(f"QDialog {{ background-color: {styles.COLORS['bg_main']}; }}")

          screen = self.screen() or QApplication.primaryScreen()
          available = screen.availableGeometry()
          max_w = int(available.width() * 0.9)
          max_h = int(available.height() * 0.9)
          if pixmap.width() > max_w or pixmap.height() > max_h:
              pixmap = pixmap.scaled(
                  max_w, max_h, Qt.AspectRatioMode.KeepAspectRatio,
                  Qt.TransformationMode.SmoothTransformation
              )

          label = QLabel()
          label.setPixmap(pixmap)
          label.setAlignment(Qt.AlignmentFlag.AlignCenter)

          layout = QVBoxLayout(self)
          layout.setContentsMargins(0, 0, 0, 0)
          layout.addWidget(label)
          self.resize(pixmap.size())

      def mousePressEvent(self, event):
          self.close()

      def keyPressEvent(self, event):
          if event.key() == Qt.Key.Key_Escape:
              self.close()
          else:
              super().keyPressEvent(event)


  def pixmap_from_data_uri(data_uri):
      """Decodifica 'data:image/xxx;base64,....' a un QPixmap. Devuelve un QPixmap nulo
      (isNull()) si el URI no trae una coma separadora o el base64 no decodifica a una
      imagen válida -- defensivo, nunca debería pasar con URIs generados por
      MarkdownTextEdit._insert_image, pero un click en contenido corrupto/antiguo no debe
      poder reventar la UI."""
      if "," not in data_uri:
          return QPixmap()
      b64 = data_uri.split(",", 1)[1]
      raw = QByteArray.fromBase64(b64.encode("ascii"))
      pixmap = QPixmap()
      pixmap.loadFromData(raw)
      return pixmap


  def show_image_preview(data_uri, parent=None):
      """Abre ImagePreviewDialog para el data URI dado. No-op si no decodifica a una
      imagen válida."""
      pixmap = pixmap_from_data_uri(data_uri)
      if pixmap.isNull():
          return
      dlg = ImagePreviewDialog(pixmap, parent)
      dlg.exec()
  ```

- [x] `detail_dialog/markdown_edit.py` — imports: add
  `from .image_preview_dialog import show_image_preview` (relative import, matching how
  `markdown_edit.py`'s sibling modules import each other inside the `detail_dialog` package).

- [x] `detail_dialog/markdown_edit.py` — `MarkdownTextEdit.__init__` (currently just sets
  `self.image_width_provider = None`): also add `self.setMouseTracking(True)` and
  `self.viewport().setMouseTracking(True)` (hover-cursor feedback needs tracking on both;
  cheap, harmless if one turns out redundant) and `self._press_pos = None`.

- [x] `detail_dialog/markdown_edit.py` — add three new `MarkdownTextEdit` methods (place them
  near `keyPressEvent`, before `insert_table`/`_insert_image`):
  ```python
  def mousePressEvent(self, event):
      self._press_pos = event.pos()
      super().mousePressEvent(event)

  def mouseReleaseEvent(self, event):
      if event.button() == Qt.LeftButton and self._press_pos is not None:
          moved = (event.pos() - self._press_pos).manhattanLength()
          if moved < 4:
              anchor = self.anchorAt(event.pos())
              if anchor.startswith("data:image/"):
                  show_image_preview(anchor, self)
                  return
      super().mouseReleaseEvent(event)

  def mouseMoveEvent(self, event):
      anchor = self.anchorAt(event.pos())
      self.viewport().setCursor(
          Qt.CursorShape.PointingHandCursor if anchor.startswith("data:image/")
          else Qt.CursorShape.IBeamCursor
      )
      super().mouseMoveEvent(event)
  ```
  The `manhattanLength() < 4` check distinguishes a genuine click from a drag-selection that
  happens to end over an image (a real drag must not be hijacked into opening the preview).

- [x] `detail_dialog/markdown_edit.py` — `_insert_image(self, image)`: change the final line
  (currently `self.textCursor().insertHtml(f'<img src="data:image/png;base64,{b64}" />')`) to
  build the data URI once and wrap the `<img>` in a same-URI `<a href>`:
  ```python
  data_uri = f"data:image/png;base64,{b64}"
  self.textCursor().insertHtml(f'<a href="{data_uri}"><img src="{data_uri}" /></a>')
  ```
  Everything above this line in `_insert_image` (scaling to `avail` width, PNG-encoding to
  `b64`) is unchanged.

- [x] `detail_dialog/log_entry.py` — imports: add
  `from .image_preview_dialog import show_image_preview`.

- [x] `detail_dialog/log_entry.py` — in `init_ui`, right after `self.content_label` is built
  and configured (currently ends at `self.content_label.setTextInteractionFlags(...)`), wire
  the click handler and set a pointing-hand cursor only when the entry actually contains an
  image (a plain-text-only entry must keep the normal I-beam/arrow cursor — `QLabel` has no
  cheap per-glyph cursor control, so this whole-label heuristic is the pragmatic choice, not a
  precision hit-test):
  ```python
  self.content_label.setOpenExternalLinks(False)
  self.content_label.linkActivated.connect(self._on_content_link_activated)
  if "<img" in log_data["content"]:
      self.content_label.setCursor(Qt.PointingHandCursor)
  ```
  `QLabel.openExternalLinks` already defaults to `False`; setting it explicitly here is just
  documentation-by-code of the assumption, not a behavior change.

- [x] `detail_dialog/log_entry.py` — add a new method:
  ```python
  def _on_content_link_activated(self, url):
      if url.startswith("data:image/"):
          show_image_preview(url, self)
  ```
  (Guards against a future non-image link type being added to log content and accidentally
  being routed into the image preview.)

- [x] `strings.py` — add one new key next to the other window-title-style entries (e.g. near
  `task_detail.window_title`):
  ```python
  "image_preview.window_title": "Vista previa de imagen",
  ```

- [x] `CHANGELOG.md` — add an `### Added` entry under `[Unreleased]` for the click-to-enlarge
  feature (own bullet), and a `### Fixed` entry for the taskbar icon (mentioning the
  AppUserModelID bump and, briefly, that it's paired with a transparent icon redesign).

- [x] `README.md` — update the existing "Rich Notes" bullet (task description/diary paste
  bullet point) to mention pasted images are now clickable to view larger; no other README
  sections need touching for this wave.

- [x] `main.py` — bump the AppUserModelID string (currently
  `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EkinKanban.TrelloLite")`,
  around line 505) to `"EkinKanban.TrelloLite.2"`, and extend the existing comment above it to
  explain why:
  ```python
  if os.name == 'nt':
      # En Windows, pythonw.exe agrupa la ventana bajo su propio icono genérico en la
      # barra de tareas a menos que el proceso declare un AppUserModelID propio. El sufijo
      # ".2" es deliberado: en máquinas que ejecutaron Ekin antes del fix de icono por ruta
      # absoluta (2026-07-29), Windows pudo cachear el icono genérico bajo el identificador
      # antiguo "EkinKanban.TrelloLite" -- ese caché sobrevive a un `git pull` porque nada lo
      # invalida. Cambiar el identificador fuerza a Windows a tratarlo como una app nueva y
      # resolver el icono de cero en vez de servir el cacheado.
      try:
          import ctypes
          ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EkinKanban.TrelloLite.2")
      except Exception:
          pass
  ```

- [x] `tests/test_widgets_headless.py` — add a new section
  (`# --- Click-to-enlarge pasted images (post-v0.9.1) ---`) near the end, with these tests
  (import `detail_dialog.markdown_edit as markdown_edit_module` and
  `detail_dialog.image_preview_dialog as image_preview_module` at the top, following the same
  `import X as X_module` convention already used for `task_detail_dialog_module`):
  - `test_pixmap_from_data_uri_decodes_valid_png()` — build a tiny known-good PNG data URI
    (base64 of a 1x1 PNG is fine — reuse the literal already present in
    `test_widgets_headless.py`'s hover-expand mime-data helpers' spirit, or any valid 1x1 PNG
    base64 string), call `image_preview_module.pixmap_from_data_uri(uri)`, assert
    `not pixmap.isNull()`.
  - `test_pixmap_from_data_uri_returns_null_for_garbage()` — call with `"not-a-data-uri"` and
    with `"data:image/png;base64,not-valid-base64!!"`; assert `.isNull()` for both (no
    exception raised either way).
  - `test_show_image_preview_opens_dialog_for_valid_image(qapp, monkeypatch)` — monkeypatch
    `image_preview_module.ImagePreviewDialog.exec` to a lambda recording a call instead of
    blocking (mirrors the existing modal-call monkeypatch convention used for
    `QFileDialog`/`QMessageBox` elsewhere in this file); call `show_image_preview(valid_uri)`;
    assert the recorded call list has exactly one entry.
  - `test_show_image_preview_noop_for_invalid_uri(qapp, monkeypatch)` — same monkeypatch, call
    `show_image_preview("garbage")`; assert the recorded call list is empty (dialog never
    opened).
  - `test_markdown_text_edit_wraps_pasted_image_in_anchor(qapp)` — construct a bare
    `MarkdownTextEdit()`, call `editor._insert_image(QImage(4, 4, QImage.Format.Format_RGB32))`
    directly (a tiny in-memory image, no real clipboard needed), then assert
    `'<a href="data:image/png;base64,' in editor.toHtml()` (confirms the anchor-wrapping
    landed, without needing to simulate an actual paste event).
  - `test_markdown_text_edit_click_on_image_anchor_opens_preview(qapp, monkeypatch)` — build a
    `MarkdownTextEdit()`, insert a tiny image via `_insert_image` as above, monkeypatch
    `markdown_edit_module.show_image_preview` to record calls, then simulate a click
    sequence: find the image's position via
    `editor.document().firstBlock().layout().lineAt(0)`-style geometry is fragile — instead,
    locate the anchor position robustly by walking the document: iterate
    `QTextCursor` positions from 0 to `editor.document().characterCount()` calling
    `editor.anchorAt(editor.cursorRect(cursor).center())` is also fragile. **Simplest robust
    approach**: call `editor.mousePressEvent`/`mouseReleaseEvent` directly with a
    hand-built `QMouseEvent` at a position obtained from
    `editor.cursorRect(QTextCursor(editor.document()))` is not reliable either — instead,
    bypass geometry entirely for this unit test by monkeypatching `editor.anchorAt` itself
    (`monkeypatch.setattr(editor, "anchorAt", lambda pos: "data:image/png;base64,AAAA")`)
    and directly invoke `editor.mousePressEvent(...)` then `editor.mouseReleaseEvent(...)`
    with a `QMouseEvent` built at the same position for both (zero movement, so
    `manhattanLength() < 4` holds) — this tests the click-vs-drag distinction and the
    dispatch-to-`show_image_preview` logic in isolation from real text-layout geometry, which
    is exactly the unit under test. Assert `show_image_preview` was called once with the
    monkeypatched anchor string.
  - `test_markdown_text_edit_drag_does_not_open_preview(qapp, monkeypatch)` — same
    `anchorAt` monkeypatch and `show_image_preview` monkeypatch, but press at one position and
    release at a position more than 4px away (a real drag); assert `show_image_preview` was
    NOT called (regression guard for the drag-selection-must-not-be-hijacked requirement).
  - `test_log_entry_widget_routes_image_link_to_preview(qapp, monkeypatch)` — build a
    `LogEntryWidget` with `log_data={"id": 1, "content": '<a href="data:image/png;base64,AAAA"><img .../></a>', "created_at": "..."}` and no-op `delete_callback`/`save_edit_callback`
    lambdas; monkeypatch `detail_dialog.log_entry.show_image_preview` to record calls; call
    `widget._on_content_link_activated("data:image/png;base64,AAAA")` directly; assert one
    call recorded. Also assert `widget.content_label.cursor().shape() ==
    Qt.CursorShape.PointingHandCursor` (the `"<img" in content` heuristic fired).
  - `test_log_entry_widget_plain_text_keeps_default_cursor(qapp)` — same construction with
    `content="solo texto, sin imagen"`; assert
    `widget.content_label.cursor().shape() != Qt.CursorShape.PointingHandCursor`.

## 3. Acceptance Criteria
- Pasting an image into the task description, the diary compose box, or an in-progress diary
  edit stores it wrapped in `<a href="data:...">...<img .../></a>` — confirmed by
  `test_markdown_text_edit_wraps_pasted_image_in_anchor`.
- Clicking directly on a pasted image (not on adjacent plain text) in any of those three
  editable surfaces, or on an already-posted diary entry's image, opens `ImagePreviewDialog`
  showing that image scaled up to at most 90% of the screen's available width/height
  (unscaled if it's already smaller than that), centered, preserving aspect ratio.
- The preview dialog closes on any click inside it, on `Esc`, or via the window's own close
  button; it does not require the user to find some other, hard-to-discover unsplit affordance.
- A drag-selection that starts on ordinary text and ends while hovering over an image does
  **not** open the preview (`test_markdown_text_edit_drag_does_not_open_preview`) — normal
  text selection must keep working exactly as before everywhere images can appear.
- A diary entry with no image in it does not get a pointing-hand cursor over its text
  (`test_log_entry_widget_plain_text_keeps_default_cursor`); one that does have an image does.
- Malformed/garbage image data (corrupted content, or a future non-image link type) never
  raises or crashes — `show_image_preview`/`pixmap_from_data_uri` degrade to a silent no-op.
- `main.py`'s AppUserModelID is `"EkinKanban.TrelloLite.2"`, with a comment explaining the
  cache-invalidation rationale; no other AppUserModelID-setting call sites exist to miss
  (verify via `grep -rn SetCurrentProcessExplicitAppUserModelID` — there must be exactly one).
- `ekin_icon.png` is RGBA with a genuinely transparent (not just alpha-present-but-opaque)
  background — spot-check that corner/edge alpha values are now low, not 255 — and
  `ekin_icon.ico` still structurally contains all 7 resolutions (16/24/32/48/64/128/256), each
  32bpp, each with a plausible non-zero byte size. This was already produced before the TDD;
  the Tester's job is to confirm the artifact is correct, not to redo the image processing.
- `database/*.py`, `widgets.py`, `board_view.py`, and every file outside the list in §2 are
  untouched (`git diff --stat` before considering this done) — this is a UI+asset-only wave,
  no schema or unrelated-module changes.
- Full test suite passes (including the new tests above) with a clean process exit code; ruff
  stays clean.
- `CHANGELOG.md`'s `[Unreleased]` section and `README.md`'s Rich Notes bullet both mention the
  click-to-enlarge capability; `CHANGELOG.md` also documents the taskbar-icon
  cache-invalidation fix and the icon transparency redesign.

## QA Report

**Verdict: PASS.** All acceptance criteria validated against the real implementation and
independently re-executed evidence, not the Coder's say-so.

**Code trace:**
- `detail_dialog/image_preview_dialog.py`: matches the TDD's prescribed code verbatim.
- `detail_dialog/markdown_edit.py`: `_insert_image`'s final line builds `data_uri` once and
  wraps `<img>` in `<a href>` as specified. `MarkdownTextEdit.__init__` adds
  `setMouseTracking(True)` on both `self` and `self.viewport()`, plus `_press_pos = None`.
  `mousePressEvent`/`mouseReleaseEvent`/`mouseMoveEvent` match the TDD's logic — with one
  deliberate, correct deviation: the Coder used `event.position().toPoint()` instead of the
  TDD's `event.pos()`. Verified this is the *right* call, not a slip: `widgets.py` (drag/drop
  code) already exclusively uses `event.position().toPoint()`, never `.pos()`; using `.pos()`
  as literally specified would have introduced a `DeprecationWarning` on every mouse
  interaction with these widgets in this PySide6 version, inconsistent with the rest of the
  codebase. Re-ran the affected tests after this substitution — still 7/7 green — so the
  swap didn't just avoid a warning, it's behaviorally identical and correctly implemented.
- `detail_dialog/log_entry.py`: `content_label` wiring and `_on_content_link_activated` match
  the TDD exactly.
- `strings.py`: `image_preview.window_title` key present, correctly placed, used via `t(...)`.
- `main.py`: AppUserModelID is `"EkinKanban.TrelloLite.2"` with the explanatory comment;
  `grep -rn SetCurrentProcessExplicitAppUserModelID` (independently re-run, not trusting the
  Coder's earlier grep) confirms exactly one call site in the whole repo.

**Executed verification (not just static review):**
1. `pytest -q` (full suite, independent re-run, 3 consecutive times): **176 passed** every
   time (up from 167 pre-wave; 9 new tests), clean exit code, no flakiness observed.
2. `ruff check .` (whole project): all checks passed.
3. `git diff --stat -- database/ widgets.py board_view.py`: **empty** — confirms this wave
   touched none of the layers explicitly declared out of scope.
4. `git status --porcelain`: exactly the files the TDD's task list named, no stray files.
5. **Icon artifacts, independently re-verified from scratch** (not reusing the Coder-phase
   check): `ekin_icon.png` outer-edge alpha now ranges 0–97 across all sampled border pixels
   (was uniformly 255 — fully opaque — before this wave), confirming genuine transparency, not
   just an alpha channel that's present but unused. `ekin_icon.ico` parsed byte-by-byte:
   contains exactly the 7 required resolutions (16/24/32/48/64/128/256), each 32bpp, each with
   a plausible nonzero byte size (939–121207 bytes, scaling sensibly with resolution).

**Edge cases considered, no bugs found:**
- Malformed image data: `pixmap_from_data_uri("not-a-data-uri")` and a string with invalid
  base64 both return a null `QPixmap` without raising — confirmed by
  `test_pixmap_from_data_uri_returns_null_for_garbage`, and `show_image_preview` on top of
  that never constructs/opens a dialog for a null pixmap.
  the coma-splitting (`if "," not in data_uri`) guard means a URI with no `,` (e.g. a bare
  `"garbage"` string, as used in `test_show_image_preview_noop_for_invalid_uri`) is caught
  before ever reaching `QByteArray.fromBase64`, so it can't misinterpret garbage as a 0-length
  base64 payload.
- Drag-vs-click distinction: `manhattanLength() < 4` correctly separates a real click
  (`test_markdown_text_edit_click_on_image_anchor_opens_preview`, 0px movement) from a drag
  ending over an image (`test_markdown_text_edit_drag_does_not_open_preview`, 40px+ movement)
  — this is the single most important regression guard in this wave (a false positive here
  would silently break text selection anywhere an image can appear), and it's directly tested,
  not just asserted in a docstring.
- Plain-text diary entries don't get a misleading pointing-hand cursor over the whole label
  (`test_log_entry_widget_plain_text_keeps_default_cursor`) — confirms the `"<img" in content`
  heuristic doesn't false-positive on ordinary entries.
- The description editor (`desc_input`) needed no direct changes or dedicated tests beyond the
  shared `MarkdownTextEdit` ones, since it's a plain instance of that class with no overriding
  behavior — verified by re-reading `task_detail_dialog.py`'s `self.desc_input =
  MarkdownTextEdit()` construction, confirming there's no separate description-specific mouse
  handling that could have been left stale.
- Non-image future link types in a diary entry: `_on_content_link_activated`'s
  `url.startswith("data:image/")` guard means a hypothetical future non-image link would be a
  silent no-op today rather than crash or misbehave — matches the TDD's stated intent.

No blocking issues found. Ready for Architect final review / archiving.
