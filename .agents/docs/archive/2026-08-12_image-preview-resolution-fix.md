# TECHNICAL DESIGN DOCUMENT

## 1. Overview
Follow-up fix on click-to-enlarge (shipped v0.9.2, commit `2887663`): the enlarged preview
looks blurry. Root cause is not a rendering bug in `ImagePreviewDialog` — it's an
information-loss problem upstream. `MarkdownTextEdit._insert_image` scales the pasted `QImage`
down to the chat/description display width (typically 300–500px via `image_width_provider`)
*before* encoding it, and reuses that same already-shrunk data URI for both the visible
`<img src>` **and** the click-target `<a href>` (added in the click-to-enlarge wave).
`ImagePreviewDialog` then scales that tiny source *up* to ~90% of screen size — interpolating
pixels that were already destroyed by the earlier downscale. You cannot sharpen data that
isn't there; the dialog's own scale-up-or-down logic (fixed in v0.9.2) is correct and needs no
further changes.

**Fix:** capture a second, higher-resolution copy of the pasted image at paste time — before
the chat/description-width downscale, capped at a bounded max width — and put that in
`<a href>`, while the existing small chat/description-width copy stays in `<img src>`. This
reuses the href/src split that already exists; no new HTML structure, no new anchor scheme.
`ImagePreviewDialog` will now usually scale *down* from real detail instead of *up* from a
thumbnail, which is what actually fixes the perceived blur.

**Explicit non-goals:** no retroactive fix for already-posted diary entries (their stored HTML
has `href == src`, both already tiny — same "new pastes only" scoping already established for
click-to-enlarge itself, no migration). No screen-size-aware cap (querying `QScreen` from
inside a paste-time text-editing method is unneeded complexity for a first pass) — one fixed,
generous constant instead.

## 2. Implementation Tasks

- [x] `detail_dialog/markdown_edit.py` — `MarkdownTextEdit`: add a new class attribute next to
  the existing `_BULLET_MARKERS`/`_ORDERED_RE` (same placement convention, top of the class):
  ```python
  _PREVIEW_MAX_WIDTH = 1920
  ```

- [x] `detail_dialog/markdown_edit.py` — `MarkdownTextEdit`: add a new `@staticmethod` (matching
  the existing `_style_for_indent` static-method convention in this same class) that extracts
  the QBuffer/base64 encoding `_insert_image` already does, so it can be called twice without
  duplicating logic:
  ```python
  @staticmethod
  def _image_to_data_uri(image):
      """Codifica un QImage como data URI PNG en base64."""
      buffer = QBuffer()
      buffer.open(QIODevice.WriteOnly)
      image.save(buffer, "PNG")
      b64 = bytes(buffer.data().toBase64()).decode("ascii")
      buffer.close()
      return f"data:image/png;base64,{b64}"
  ```

- [x] `detail_dialog/markdown_edit.py` — rewrite `_insert_image` to build two data URIs instead
  of one, using the new helper. Exact replacement:
  ```python
  def _insert_image(self, image):
      """Embebe un QImage como data URI base64 (queda guardado dentro del HTML). Se
      guardan DOS copias: una ajustada al ancho útil (el del histórico del chat si se ha
      configurado un `image_width_provider`, más estrecho que el editor) para mostrarla
      inline, y otra de mayor resolución (hasta _PREVIEW_MAX_WIDTH) para la vista
      ampliada -- así ImagePreviewDialog escala hacia ABAJO desde una fuente con detalle
      real al pulsar la imagen, en vez de estirar (y emborronar) la miniatura ya reducida."""
      preview_image = image
      if preview_image.width() > self._PREVIEW_MAX_WIDTH:
          preview_image = preview_image.scaledToWidth(self._PREVIEW_MAX_WIDTH, Qt.SmoothTransformation)
      preview_uri = self._image_to_data_uri(preview_image)

      if self.image_width_provider:
          avail = max(120, self.image_width_provider())
      else:
          avail = max(120, self.viewport().width() - 24)
      if image.width() > avail:
          image = image.scaledToWidth(avail, Qt.SmoothTransformation)
      inline_uri = self._image_to_data_uri(image)

      self.textCursor().insertHtml(f'<a href="{preview_uri}"><img src="{inline_uri}" /></a>')
  ```
  Note the ordering is deliberate: `preview_image` is computed from the **original** `image`
  parameter *before* the existing `avail`-scaling block reassigns the local `image` variable —
  do not reorder this, or the preview copy would silently end up derived from the already-
  shrunk inline copy instead of the original.

- [x] `tests/test_widgets_headless.py` — add `import re` at the top if not already present
  (check first; likely not, since no existing test does regex extraction).

- [x] `tests/test_widgets_headless.py` — new test,
  `test_markdown_text_edit_stores_higher_res_copy_for_preview`: paste an image larger than
  `_PREVIEW_MAX_WIDTH`, confirm the `href` decodes to something both larger than the `src` and
  capped at `_PREVIEW_MAX_WIDTH`:
  ```python
  def test_markdown_text_edit_stores_higher_res_copy_for_preview(qapp):
      editor = markdown_edit_module.MarkdownTextEdit()
      big_image = QImage(2400, 1600, QImage.Format.Format_RGB32)
      big_image.fill(Qt.GlobalColor.blue)

      editor._insert_image(big_image)
      html = editor.toHtml()

      href = re.search(r'<a href="(data:image/[^"]+)"', html).group(1)
      src = re.search(r'<img src="(data:image/[^"]+)"', html).group(1)
      href_pixmap = image_preview_module.pixmap_from_data_uri(href)
      src_pixmap = image_preview_module.pixmap_from_data_uri(src)

      assert href_pixmap.width() > src_pixmap.width()
      assert href_pixmap.width() <= markdown_edit_module.MarkdownTextEdit._PREVIEW_MAX_WIDTH
  ```

- [x] `tests/test_widgets_headless.py` — new test,
  `test_markdown_text_edit_small_image_reuses_same_data_for_preview_and_inline`: a source
  image smaller than *both* the inline width and `_PREVIEW_MAX_WIDTH` legitimately produces
  identical `href`/`src` — document this as expected behavior in the test, not a bug:
  ```python
  def test_markdown_text_edit_small_image_reuses_same_data_for_preview_and_inline(qapp):
      """Cuando la imagen original ya es más pequeña que ambos objetivos (inline y
      preview), href y src acaban siendo el mismo data URI -- comportamiento correcto,
      no un caso a evitar: no hay ninguna resolución mayor que guardar."""
      editor = markdown_edit_module.MarkdownTextEdit()
      tiny = QImage(50, 50, QImage.Format.Format_RGB32)
      tiny.fill(Qt.GlobalColor.green)

      editor._insert_image(tiny)
      html = editor.toHtml()

      href = re.search(r'<a href="(data:image/[^"]+)"', html).group(1)
      src = re.search(r'<img src="(data:image/[^"]+)"', html).group(1)
      assert href == src
  ```

- [x] `tests/test_widgets_headless.py` — the pre-existing
  `test_markdown_text_edit_wraps_pasted_image_in_anchor` uses a `QImage(4, 4, ...)` — well
  under every threshold involved, so `href == src` there too; its existing assertion
  (`'<a href="data:image/png;base64,' in editor.toHtml()`) still holds unchanged. Confirm this
  during Testing rather than editing the test — no source change should be needed for it to
  keep passing.

- [x] `CHANGELOG.md` — add one bullet under `[Unreleased]` → `### Fixed` (create the section if
  `[Unreleased]` is currently empty, matching the pattern already used after every release cut
  in this file): the enlarged preview no longer looks blurry, because a higher-resolution copy
  (up to 1920px wide) is now stored specifically for it instead of upscaling the small inline
  thumbnail.

## 3. Acceptance Criteria
- Pasting an image wider than 1920px produces a stored `<a href>` data URI that decodes to a
  *wider* image than the `<img src>` one, capped at 1920px — never wider.
- Pasting an image narrower than both the inline width and 1920px produces `href == src`
  (byte-identical data URIs) — this is correct, expected behavior, not something to special-case
  away or flag as a defect.
- `ImagePreviewDialog`/`show_image_preview`/`pixmap_from_data_uri` are **unchanged** — this wave
  is entirely about what data gets stored at paste time, not how the preview dialog renders it.
- The existing `test_markdown_text_edit_wraps_pasted_image_in_anchor` still passes with no
  modification.
- `database/*.py`, `widgets.py`, `board_view.py`, `detail_dialog/image_preview_dialog.py`,
  `detail_dialog/log_entry.py`, `detail_dialog/task_detail_dialog.py` all untouched
  (`git diff --stat`) — this is a single-file source change (`markdown_edit.py`) plus tests and
  changelog.
- Full test suite passes with a clean exit code; ruff stays clean.
- No new runtime dependency introduced (`re` is stdlib, already available).

## QA Report

**Verdict: PASS.** All acceptance criteria validated against real source, independently
re-executed tests, and a manual out-of-band verification.

**Code trace:** `_insert_image` matches the TDD exactly — `preview_image` is computed from the
original `image` parameter *before* the existing `avail`-scaling block reassigns it, so the
ordering hazard the TDD explicitly warned about does not exist in the final code. The new
`_image_to_data_uri` static method is a clean extraction with no behavior change from the
inline code it replaces.

**Executed verification:**
1. `ruff check .`: clean. `git diff --stat` against every out-of-scope file
   (`database/*`, `widgets.py`, `board_view.py`, `image_preview_dialog.py`, `log_entry.py`,
   `task_detail_dialog.py`, `version.py`): empty — confirms this really is the single-file
   change (`markdown_edit.py`) plus tests/changelog the TDD scoped it to.
2. **Manual out-of-band verification** (not just trusting the new unit tests): pasted a real
   3000×2000 `QImage` through `_insert_image` outside of pytest, decoded both resulting data
   URIs, and confirmed `href` → 1920×1280 (correctly capped, aspect ratio preserved) while
   `src` → 614×409 (the ordinary inline thumbnail width) — a ~3× resolution difference,
   directly addressing the reported blur.
3. `test_markdown_text_edit_stores_higher_res_copy_for_preview` and
   `test_markdown_text_edit_small_image_reuses_same_data_for_preview_and_inline` both pass, as
   does the pre-existing `test_markdown_text_edit_wraps_pasted_image_in_anchor` (unmodified, as
   the TDD required).

**Investigated the Coder's flagged flake, not dismissed on trust:** one `pytest` run out of the
Coder's 26 showed `180 passed, ... 1 error` in an unrelated, unmodified test
(`test_markdown_text_edit_click_on_image_anchor_opens_preview`). Ran the full suite an
**additional 45 times independently** (20 then 25, across two batches) specifically hunting for
a reproduction — zero anomalies in all 45. This is qualitatively different from the
`STATUS_HEAP_CORRUPTION` class of bug fixed earlier this session (that was a native process
crash with a non-zero process-level fault; this was a clean pytest-level fixture error with a
normal process exit) — and the failing test doesn't exercise any of this wave's new
dual-resolution logic in a way that plausibly explains a *fixture-teardown-time* error. Given
1-in-71 total runs and total unreproducibility under dedicated hunting, this is logged as a
probable one-off environmental fluke (e.g. transient OS/antivirus interference on freshly-
written files), not a regression from this change — but it's worth keeping an eye on if it
recurs in CI, since this session has already seen genuine intermittent Qt-teardown issues
before and "couldn't reproduce locally" was true right up until it wasn't, in that earlier case
too.

No blocking issues found. Ready for Architect final review / archiving.
