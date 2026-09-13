# 🗂️ Ekin Kanban — Backlog

Living planning doc: forensic findings (tech debt) + ideas for future releases.
Ordered roughly by value/effort. Checkboxes track what's done.

## 🎯 Prioritized Backlog

_Added 2026-09-13 from an RDi exploration session (`<rdi_exploration_protocol>`), grounded in
graphify AST analysis and cross-referenced against this backlog. Listed simplest → hardest by
estimated complexity. (WAL/`busy_timeout`/`foreign_keys`, EN/ES i18n + live switcher, and Lucide
icon `@lru_cache` were screened out as already shipped.)_

- [x] **DONE (2026-09-13) — Post-sync outcome summary** `[FEAT]` (sync observability)
  · Impact: Med · Complexity: S · `board_view.format_sync_summary` — concise result shown after any
    user-initiated sync + in the sync-button tooltip. 4 tests. (Persistent per-board history left as a
    later nice-to-have — kept to no schema change.)
  - **Problem:** the two-way merge engine silently archives superseded edits into the task diary
    (`board_sync.py`); the user only sees a static status badge and never learns what a sync did.
    `SyncResult` already carries the outcome and flows through `board_view._on_sync_finished()`.
  - **Solution:** surface a concise summary from the existing `SyncResult` after each sync
    ("Synced · 2 tasks updated · 1 conflict auto-archived"); optionally persist a small per-board
    sync log viewable from the sync context menu. Builds on data that already exists — no engine changes.

- [x] **DONE (2026-09-13) — Application diagnostic logging + global crash handler** `[RESILIENCE]`
  · Impact: High · Complexity: S–M · `logging_setup.py` (rotating `~/.ekin/logs/ekin.log`, `sys.excepthook`
    non-fatal dialog, Qt message handler); wired in `main()`, silent `print`s → `log`; "Open logs folder"
    palette command. 3 tests.
  - **Problem:** no logging infrastructure exists anywhere (no `logging`, `sys.excepthook`, or
    `qInstallMessageHandler`). Many past field failures were un-observable (icon-cache staleness,
    partial `install.ps1` clones, sync `WinError 32`, CI flakiness), and the recurring critical bugs
    (`Ctrl+Z` FK `IntegrityError`, leaked-timer `STATUS_HEAP_CORRUPTION`) share one class: an uncaught
    exception in a Qt slot terminates the process silently.
  - **Solution:** a rotating file logger under `~/.ekin/logs/` (`RotatingFileHandler`) installed at the
    top of `main()`; a `sys.excepthook` **and** `qInstallMessageHandler` that log the traceback and show
    a non-fatal "Something went wrong (details saved to log)" dialog instead of hard-crashing; structured
    log lines around sync/update/download paths (`board_sync.py`, `local_ai.py` runner,
    `ReleaseCheckThread`/`InstallerDownloadThread`); optional "Open logs folder" entry in Settings.

- [x] **DONE (2026-09-13) — Per-column WIP limits** `[FEAT]` · Impact: Med–High · Complexity: S–M
  · nullable `columns.wip_limit` (migration) threaded through `columns.py`; stepper in `ColumnEditDialog`;
    `ColumnWidget` header shows `n/limit`, danger accent when exceeded. 5 tests.
  - **Problem:** no WIP-limit concept exists (a core Kanban capability). The board header already
    computes a live task count in `load_board`, and `ColumnWidget`/`ColumnEditDialog` are self-contained.
  - **Solution:** nullable `columns.wip_limit INTEGER` (additive migration matching the existing
    `PRAGMA table_info` pattern in `database/__init__.py`); an optional stepper in `ColumnEditDialog`;
    `ColumnWidget` header shows `count / limit` and switches to the warm `danger` accent when exceeded
    (reuses `contrast_text()`/existing pill styling). Soft visual signal only — no drag-blocking.

- [x] **DONE (2026-09-13) — Extract a `BoardSyncController` from the `BoardViewWidget` god object** `[ARCH]`
  · Impact: Med · Complexity: M · `board_sync_controller.py` (`BoardSyncController(QObject)`); decouples
    `BoardSyncWorker` concurrency, `QFileSystemWatcher` debounce, and sync status from the view. 5 tests.
  - **Problem:** `BoardViewWidget` is a god node (91 edges, betweenness 0.090, cross-community bridge).
    A whole sync cluster lives on the widget: `_run_async_sync`, `_on_sync_finished`, `_on_sync_btn_clicked`,
    `_update_sync_ui`, `_link_board_new_file`, plus the `QFileSystemWatcher` + `BoardSyncWorker` wiring —
    the app's trickiest concurrency entangled with UI code.
  - **Solution:** move sync-worker lifecycle, the debounced file-watcher reactive reload, and sync-status
    state into a dedicated `BoardSyncController(QObject)` that emits signals the widget renders. Shrinks the
    widget's fan-in and makes the concurrency path independently testable. Preserve public
    signatures/signals so the current test suite stays green.

- [x] **DONE (2026-09-13) — Incremental board rendering for single-item mutations** `[PERF]`
  · Impact: Med · Complexity: M–L · Surgical single-column rebuild (`_rebuild_single_column`) and header
    counter refresh (`_update_board_counts`) on `add_task`, `create_quick_task`, `edit_column`,
    `handle_column_collapse`, `handle_task_drop`, and `open_task_details`. 5 tests.
  - **Problem:** `load_board()` tears down and rebuilds every `ColumnWidget`/`TaskCard` on nearly every
    operation (add/delete/move task, timer changes, theme toggle). The surgical path already exists —
    `_rebuild_single_column()` — but is used only for hover-expand; the ~6 UI "Refine rounds" below were
    largely repaint quirks that only surface during full-board reconstruction.
  - **Solution:** route single-item mutations through targeted updates (`_rebuild_single_column` for the
    affected column, in-place `TaskCard` refresh for badges) instead of `load_board()`; keep full
    `load_board()` only for board switch / structural reload.

_Added 2026-09-13 from a Product Strategy discovery session (`<product_strategy_discovery>`), grounded
in `README.md` + graphify workflow analysis. Ekin is offline-first / single-user / PolyForm-Noncommercial,
so these raise product & (potential) commercial value **within** that model — no server-side RBAC / SaaS
proposed. Ready for the `<feature_plan_tdd>` protocol._

- [x] **DONE (2026-09-13) — Command Palette (`Ctrl+K`): unified search + actions + quick capture** `[PRODUCT]` `[UX-REV]`
  · Impact: High · Effort: M · `command_palette.py` (reuses `search_tasks`; commands + `+ title`
    quick capture via `board_view.create_quick_task`); `Ctrl+K` + shortcuts dialog; 5 tests, 320 green.
  - **Friction:** actions scattered across ~15 shortcuts/menus; creating/finding anything requires
    navigating to the right board+column first (README benchmarks against Linear, which has this).
  - **Solution:** a `Ctrl+K` overlay reusing `SearchDialog.search_tasks()` for fuzzy task/board lookup
    **and** a command list (new task/column, go to board, open Calendar/Settings, export, toggle theme);
    inline quick-capture (`+ title @board`). Jump reuses `on_notification_task`/`on_calendar_task`.

- [x] **DONE (2026-09-13) — "My Work / Today" cross-board home view** `[PRODUCT]` `[UX-REV]`
  · Impact: High · Effort: M · `my_work_view.py` (list icon in sidebar + `Ctrl+0`); 5 tests, 309 green.
  - **Friction:** Ekin shows one board at a time; the deadline bell is a popup, not a workspace. No single
    place to see everything due today across all boards.
  - **Solution:** a home view (sidebar entry / `Ctrl+0`) aggregating Overdue · Today · Tomorrow · This week
    + an "In progress" group (running timer). Reuses `get_scheduled_tasks()` (already spans all boards) and
    the notification aggregation; each row jumps to its card. New view only — no schema change.

- [x] **DONE (2026-09-13) — In-app Analytics Dashboard + PDF report export** `[PRODUCT]` `[DATA-EXP]`
  · Impact: High · Effort: M–L · `analytics.py` (pure `gather_stats` + `render_report_html` + `export_report_pdf`
    via `QPdfWriter`, no new deps) + `dashboard_view.py` (stat tiles + hand-painted bar charts); `Ctrl+D` +
    palette command. 4 tests, 332 green.
  - **Friction:** rich data (tags, priorities, due dates, timer elapsed, per-board counts, diary
    timestamps) exists but the only output is raw JSON/CSV/MD from `exporter.py` — no visualization,
    no client-ready report.
  - **Solution:** a dashboard view with charts grounded strictly in existing data (task distribution by
    column/board/tag/priority, overdue-vs-due-soon, total timer time per board/tag, diary activity over
    time) + a **PDF export** extending the Markdown-report path in `exporter.py`. (Cycle-time deferred —
    needs column-transition history the app doesn't record yet.)

- [x] **DONE (2026-09-13) — Smart reminders (lead-time) + weekly review digest** `[PRODUCT]` `[AUTOMATION]`
  · Impact: Med–High · Effort: M · `reminders.py` + Settings (lead-days stepper, digest toggle);
    widened `notify_due_today` window + once-per-ISO-week `WeeklyDigestDialog`; 6 tests, 315 green.
  - **Friction:** notifications only fire day-of ("due today") — no advance warning, no periodic summary.
  - **Solution:** configurable **reminder lead-time** (notify N hours/days before due) layered on the
    existing due-scan + tray toasts + `.ics` `VALARM`; plus an auto-generated **weekly digest** (due next
    week, overdue, what moved) via `exporter.py`, surfaced on the first launch of each week using the
    existing once-per-day check scheduler in `main.py`.

- [x] **DONE (2026-09-13, offline-first) — Extend the Local-AI engine into workflows (task breakdown + diary summarizer)** `[PRODUCT]` `[BIZ-CAP]`
  · Impact: High · Effort: M · `local_ai.suggest_subtasks_offline`/`parse_subtask_lines`/`summarize_diary_offline`
    + `ai_assist_dialog.py`; two ✨ buttons in Task Detail (break down → create sibling tasks; summarize →
    post to journal). 8 tests, 328 green.
  - [x] **DONE (2026-09-13) — LLM-streaming enhancement:** added `task_breakdown`/`diary_summary` modes to
    `build_spec_prompts` + `generate_structural_spec`; `AiAssistDialog` now shows "✨ Enhance with local AI"
    that streams via `SpecGenerationThread` (falls back to the offline draft). 6 tests.
  - **Friction:** the local-AI engine (Ekin's rarest differentiator) is siloed to the multi-select
    "generate SPEC" flow; it does nothing for everyday task hygiene.
  - **Solution:** two additive local-AI actions reusing `local_ai.py` + `SpecGenerationThread` streaming +
    offline fallback: (a) **AI task breakdown** — one large card → suggested child tasks acceptable into
    the column; (b) **AI diary/standup summarizer** — condense a task's/board's diary into "what happened /
    what's next". Same engine, model selector, offline fallback already shipped. Premium "Pro AI" candidate.

---

## 🚧 In progress (2026-09-05 — UI Refactor: "Warm Shell" from Claude Design handoff)

Full presentation refactor per the `Refactor UI para EKIN-handoff.zip` spec (design system
"Organic": cream ground `#f5ead8`, single terracotta accent `#c67139`, sage second voice,
Caprasimo display + Figtree body, Lucide icons). No data-model/schema changes. Landed in
verified chunks (ruff clean, 248/248 pytest green after each). Light "Warm shell" is now the
default theme; the native window frame is kept.

- [x] **Palette + `build_qss()` overhaul (`styles.py`):** 12-key palette expanded to the full
  Organic ramp (~24 keys); `accent_blue` kept as a transitional alias for `accent`. Light
  default (`main.py`, `settings_dialog.py`). Dark stays Slate provisionally (the "Night lanes"
  retune is pending).
- [x] **Fonts vendored + registered (`assets/fonts/`, `main.py`):** Caprasimo + Figtree (OFL)
  loaded via `QFontDatabase` so titles render without a system install.
- [x] **Lucide icons + tint helper (`assets/icons/lucide/`, `icons.py`):** 30 SVGs (ISC),
  recolored per state, replacing every emoji glyph.
- [x] **UI copy flipped to English, emoji stripped (`strings.py`).**
- [x] **Board screen (`widgets.py`, `board_view.py`):** flat cream task cards with drop
  shadows (no borders), radius-28 columns with an 8px stage dot (the color underline removed),
  56px collapsed strip, warm due/timer/tag pills, `bg_board` carril, Caprasimo board title,
  Lucide chevrons/menu/plus/cloud.
- [x] **Sidebar (`sidebar.py`):** board rows as 42px/radius-16 with a color dot + accent
  selection, Lucide utility bar (bell/search/calendar/settings/shortcuts), cloud/archive board
  badges, version chip + `offline · everything on this machine` tagline.
- [x] **Calendar** (`calendar_view.py`): month in Caprasimo 32, day cells radius-16 borderless,
  today = `bg_main` + 2px accent ring + accent number, Lucide chevron nav, warm drag highlight.
- [x] **Task detail** (`task_detail_dialog.py`, `markdown_edit.py`, `log_entry.py`): warm styling
  inherited from QSS + emoji→Lucide (add-link, link/attachment rows, tag pills, journal edit/delete),
  warm priority colors, code blocks on `bg_dark` with `#eee7db` text, English color-picker names.
  (Kept the delicate two-panel restructure of the detail dialog for the refine pass.)
- [x] **AI spec + Selection dock** (`ai_spec_dialog.py`, `board_view.py`): 74px dark dock with
  accent check circle + Caprasimo count + `sparkles` generate + outline Clear; ai_spec dialog
  fully de-Spanished, `rotate-ccw` refresh, warm engine-status colors, `bg_dark` code editor.
- [x] **Small dialogs** (`settings_dialog.py`, `shortcuts_dialog.py`, `search_dialog.py`,
  `tag_manager_dialog.py`): warm via inherited QSS + token fixes (warm default tag color).
- [x] **`main.py`:** min window 1024×640 (resize 1280×800).
- [x] **Dark "Night lanes" palette** (`styles.py`): warm-espresso `DARK` mirroring the Warm-Shell
  level hierarchy; both palettes build clean and keys match.

**Deferred to the test-&-refine pass** (nice-to-haves, not blockers): two-panel task-detail
restructure; 6-circle preset color picker (New board / Edit column); settings segmented/toggle/
stepper controls; global `QComboBox`/`QCheckBox`/`QSpinBox` warm styling; full keyboard focus-ring
system; sub-1180 sidebar auto-collapse (manual toggle already exists); per-token pygments palette
in code blocks.

### Refine round 1 (2026-09-06 — from live dark-theme testing)

- [x] **Fixed the "dark box" integration bug** (`widgets.py`, `styles.py`, `calendar_view.py`):
  Qt paints an object-name-styled `QLabel` sitting on a styled-background parent with the
  *window* color, not the parent's — leaving a mismatched box. Only an explicit matching
  background clears it (verified by rendering). Fixed card titles (`set_card_style`), "+ Add
  task" (`bg_column`), journal timestamp/content (`bg_card`), and calendar day numbers.
- [x] **Removed the `...` from Import/Export labels** (`strings.py`).
- [x] **"Background color" → "Board color"** (`strings.py`): the board color is *not* unused —
  it now drives the sidebar color dot and the calendar legend/chips — so the control is kept
  and the label renamed to match its new role (an accent dot, not a background).
- [x] **Board options modal** (`sidebar.py`): new `BoardConfigDialog` (Edit / Copy / Archive /
  Import / Export / Delete) opened by a config button on the active board row; the sidebar
  bottom now shows only **New board** + **Archived boards**.
- [x] **`on_accent` token** (`styles.py` + call sites): a cream foreground for text/icons on the
  accent (and on dark surfaces) so dark theme no longer renders dark-on-terracotta. Light theme
  unchanged (its `bg_main` was already cream).
- [x] **Light theme broke on theme-toggle** (`board_view.py`, `widgets.py`, `styles.py`): the
  board's carril/columns/cards had theme colors **baked into inline stylesheets at build time**,
  so toggling dark→light left the whole board area dark. Root-caused by rendering: Qt does **not**
  paint these custom `QFrame`/`QWidget` backgrounds from app-level QSS (only an inline stylesheet
  paints them). Fix: the carril bg is re-applied in `load_board()` (which runs on every theme
  toggle), columns/cards are already rebuilt there, and the board title moved to an object-name
  QSS rule (labels *do* take app-QSS color). Verified by rendering a dark→light toggle.

### Refine round 2 (2026-09-07 — closing the structural gaps vs the handoff)

- [x] **Task detail restructured to the handoff shape** (`task_detail_dialog.py`, `styles.py`,
  `strings.py`): header with kicker (`BOARD · COLUMN`) + big Caprasimo in-place title + close
  circle → metadata card → two panels **Notes | Journal** (Caprasimo "Journal" header + "N
  entries") → action bar (Delete ghost · "Changes save as you type" · Close · Save changes). All
  public widgets/methods preserved (timer, links, scroll, `right_panel` ≥480) so the 248 stay green.
- [x] **Global form-control theming** (`styles.py`): `QComboBox` / `QAbstractSpinBox` (date/time/
  spin) / `QCheckBox` now themed by app QSS. **This was the real dark-theme bug** — those controls
  rendered Qt's default white palette in dark mode across Task detail, Settings, Calendar & AI spec.
- [x] **Settings → segmented / toggle / stepper** (`settings_dialog.py`): segmented Light/Dark, an
  accent `ToggleSwitch` (paintEvent knob), and a −/+ stepper with a Caprasimo value. Backing
  `theme_combo`/`notif_chk`/`timer_alert_spin` kept hidden as the state + persistence path (tests green).
- [x] **Board header counts chip** (`board_view.py`): `{tasks} tasks · {due} due this week`,
  computed in `load_board`.
- [x] **6-circle preset color picker** (`color_picker.py`, wired into `BoardEditDialog` &
  `ColumnEditDialog`): six design-system circles with a double-ring selection + a dashed "+" for a
  custom color; `get_data()`/`self.color` contract preserved.

Verified by rendering every screen in both light and dark. Remaining minor niceties (not blockers):
card metadata is stacked rather than a single reading-order row; the QCalendar date popup and
pygments per-token palette aren't warm-themed yet.

### Refine round 3 (2026-09-07 — dark-theme overhaul + legibility + icon)

- [x] **Dark palette redesigned for real elevation** (`styles.py`): carril `#201d19` (darkest) <
  columns/sidebar `#2f2b25` < task cards `#3c362e` (lightest). Before, `bg_column ≈ bg_board ≈
  bg_main`, so columns looked transparent and the header/`+Add task` blended into the window.
- [x] **`contrast_text()` for legible pills** (`styles.py`, `widgets.py`, `task_detail_dialog.py`):
  tag/priority pills now pick dark ink on light colors (yellow) and cream on dark colors (red),
  by perceptual luminance — fixes the illegible white-on-yellow tags in both themes.
- [x] **Linked-board pill made theme-safe** (`widgets.py`): neutral `bg_hover` pill with the board
  color only on the link icon, instead of low-contrast colored text on a faint tint.
- [x] **Segmented Light/Dark toggle fixed** (`settings_dialog.py`): fully-pill (999) buttons inside
  a stadium container, so the active segment no longer pokes square corners past the border.
- [x] **New app icon** (`ekin_icon.png` 512², `ekin_icon.ico` 16–256): terracotta squircle with the
  brand's Caprasimo "e" in cream + a sage accent dot — organic/modern, matched to the light theme.

### Refine round 4 (2026-09-07 — column fill + segmented pill, follow-ups)

- [x] **Column interior now uniformly `bg_column`** (`widgets.py`): a `QScrollArea` with children
  does NOT reliably show the container's fill behind it, so the empty task area rendered as the
  darker carril ("transparent columns"). Fixed by painting `bg_column` explicitly on the header,
  the scroll viewport and the inner `TaskListArea`, plus an explicit bg on the column title label
  (the QLabel-on-styled-parent dark-box bug). The whole column is now the same color as its card.
- [x] **Segmented Light/Dark pill actually rounds** (`settings_dialog.py`): Qt ignores
  `border-radius` on a `QPushButton` when `border: none` (it fills a square). Added a
  `1px solid transparent` border so the active segment renders as a clean stadium pill.

### Refine round 5 (2026-09-07 — add-task fill, 3-row card, dark header title)

- [x] **"+ Add task" fill fixed** (`widgets.py`): it rendered transparent (showed the carril)
  because the app-QSS `#AddTaskButton` background didn't paint — same class of Qt quirk as the
  columns. Set its background/border/hover explicitly inline (bg_column), matching the column.
- [x] **Task card metadata in exactly 3 rows** (`widgets.py`): Row 1 tags (category·value +
  priority, wraps), Row 2 due + timer inline, Row 3 linked board. `timer_container` kept as an
  attribute (tests) but moved into the shared row 2.
- [x] **Dark board header + title** (`board_view.py`, `styles.py`): the header bar background was
  set inline at construction (light `bg_sidebar`) and never refreshed on theme toggle, so in dark
  it stayed light and the cream title vanished. Now the header bar bg is re-applied in
  `load_board()` (reactive), and `#BoardHeaderTitle` is recolored to the accent (terracotta) —
  visible and on-brand in both themes.

### Refine round 6 (2026-09-07 — add-task border, title/icon theming, real 3-row card)

- [x] **"+ Add task" border removed** (`widgets.py`): no dashed frame — just the solid `bg_column`
  fill with an accent-tint hover.
- [x] **Board title white in dark, terracotta in light** (`styles.py`): added a `header_title`
  palette key (`#c67139` light, `#f5ead8` dark) so `#BoardHeaderTitle` is high-contrast in both.
- [x] **Sidebar theme refresh on toggle** (`sidebar.py`, `main.py`): the utility icons
  (bell/search/calendar/settings/shortcuts), the New-board/Archived icons, the version chip and
  tagline all bake their color at construction and went invisible after a hot theme switch. Added
  `SidebarWidget.refresh_theme()` (re-colors those + reloads the board list), called from
  `MainWindow.apply_theme()`.
- [x] **Task card metadata is now really 3 rows** (`widgets.py`): the previous layout collapsed to
  2 rows for a card without a linked board. Split the **Priority** tag onto its own row so the
  reading order is Row 1 tags · Row 2 priority · Row 3 due + timer + linked board — matching the
  handoff. Priority detected by category name (`priority`/`prioridad`, covers legacy Spanish data).

---

## ✅ Done (2026-09-03 — Forensic Audit Bug Fixes & Refactors)

- [x] **Snapshot UUID Preservation on Undo/Redo (`database/snapshots.py`):** `snapshot_task`, `snapshot_column`, and `snapshot_board` now preserve `task_uuid`, `column_uuid`, and `board_uuid` so restored items never lose synchronization compatibility with OneDrive `.ekboard` files.
- [x] **Zombie Process Termination (`local_ai.py`, `main.py`):** Registered `atexit.register(stop_managed_runner)` with timeout/kill and connected `QApplication.aboutToQuit` to guarantee `llama-server.exe` exits cleanly.
- [x] **Remote Task Deletion Sync & No-Resurrection (`board_sync.py`):** If a collaborator deletes a task in OneDrive and the local task was already synced and untouched, the system removes it locally instead of resurrecting it into the shared file.
- [x] **Transient File Lock Retry on Windows (`board_sync.py`):** `write_sync_file_atomic` implements exponential backoff retry on `os.replace` to prevent `WinError 32` sharing violation errors on OneDrive shares.
- [x] **Database Layer Decoupling (`database/connection.py`):** Extracted `get_connection` and dynamic `DB_NAME` resolution into `connection.py`, breaking cyclic dependencies across database submodules.
- [x] **HTML Utilities DRY Centralization (`detail_dialog/html_utils.py`):** Moved `fit_html_images` and `linkify_urls` into a decoupled shared utility module.
- [x] **236/236 automated tests passing, ruff clean.**

---

## ✅ Done (2026-09-03 — Phase 2: Multi-Card Selection & Autonomous Local AI Spec Generator)

- [x] **Multi-Card Selection with `Ctrl + Click` (`widgets.py`, `board_view.py`):**
  - Toggle card selection across columns with `Ctrl + Click` without opening detail dialog.
  - Card visual feedback with accent-blue 2px border, tinted background, and top-right `✓` badge.
  - Bottom action dock showing selected count, `🤖 Generar SPEC con IA Local` action, and `❌ Deseleccionar` (`Escape` key support).
- [x] **Autonomous Local AI Module (`local_ai.py` — Vía B):**
  - Zero-setup architecture for non-technical users: supports Qwen 2.5 Coder 1.5B Instruct (~980 MB) and portable background runner.
  - Multi-engine auto-detection (Ollama, LM Studio, llama-server on ports 11434, 8080, 1234, 28192).
  - Deterministic structural fallback synthesizer for instant, 100% offline spec generation.
  - Real-time OpenAI-compatible streaming tokens worker thread (`SpecGenerationThread`).
- [x] **AI Spec Generation Modal Dialog (`ai_spec_dialog.py`):**
  - Supports 3 modes: Code Agent Spec (Antigravity/Claude Code/Cursor), User Stories (Gherkin), and QA Test Plans.
  - Real-time streaming editor with 1-click Copy, Save to file, and direct board task creation.
- [x] **234/234 automated tests passing, ruff clean.**

---

## ✅ Done (2026-09-03 — Phase 1: Shared Boards & Asynchronous OneDrive Synchronization)

- [x] **Database schema migrations (`database/__init__.py`, `database/sync.py`):** Added `sync_path`, `last_synced_at`, `sync_hash`, and `board_uuid` to `boards`; `column_uuid` to `columns`; `task_uuid`, `version`, and `synced_version` to `tasks`.
- [x] **Asynchronous Two-Way Merge & Sync Engine (`board_sync.py`):**
  - Offline-first differential synchronizer operating on standard JSON `.ekboard` files.
  - State-based revision tracking (`synced_version`) immune to clock skew and sub-second race conditions.
  - **No-Data-Loss Conflict Resolution:** superseded conflicting edits are automatically archived into the task's personal diary/chat log.
  - Automated pre-merge safety snapshots saved to `backups/sync_premerge_board_...`.
- [x] **Reactive UI Integration (`board_view.py`, `sidebar.py`):**
  - Header pill button with sync status badge (`☁️ Sincronizado` / `☁️ Vincular con OneDrive`).
  - Context actions: Sync now, open file location in Explorer, unlink board.
  - `QFileSystemWatcher` integration with debounced reactive reload when OneDrive writes changes to disk.
  - Sidebar cloud badges (`☁️ `) for linked boards with dedicated context actions.
- [x] **225/225 automated tests passing, ruff clean.**

---

## ✅ Shipped (2026-09-03, v0.9.7 — Rich Text Formatting Wave: Syntax-Highlighted Code Blocks, Horizontal Rules, Text Color Palette, Web Links & Deletion)

- [x] **Syntax-highlighted code blocks (`MarkdownTextEdit`, `pygments`):** Monokai dark styling, language selector (`CodeBlockDialog`), markdown shortcut (```` ``` ```` + Enter), fluid 100% responsive tables in description and chat, and 3 deletion mechanisms (button `✕ Borrar`, right-click context menu, and empty cell Backspace).
- [x] **Horizontal separator rules (`---`):** Typing `---` or pressing Enter on hyphens converts to full-width `<hr />`, with dedicated `―` toolbar button.
- [x] **Text color palette picker (`RichTextToolbar`):** Palette popup with 9 modern presets, custom color dialog (`QColorDialog`), and active color underline indicator.
- [x] **Preservation and active dispatch of web links (`🔗`):** Pasting URLs wraps selected text, dedicated link dialog, auto-linkification of plain text URLs in chat comments (`linkify_urls`), and external browser dispatch via `QDesktopServices.openUrl()`.
- [x] **213/213 automated tests passing, ruff clean. Cut as v0.9.7.**

---

## ✅ Done (2026-08-21 — Advanced Export/Import: Single/All Boards, Column Structure Templates, Full Metadata)

- [x] **Export modal dialog & enhanced formats (`exporter.py`, `export_dialog.py`):**
  - **Scope:** Export all boards or current active board.
  - **JSON:** Export full boards with tasks, or column structure only (board templates without tasks).
  - **Metadata:** Now exports task links/attachments (`task_links`), timer state (`timer_started_at`), linked boards (`linked_board_id`/`linked_board_name`), tag colors, and logs.
  - **CSV:** Task counts, links count, and single-board filtering support.
  - **Markdown:** Formatted project reports with task descriptions, links, and log notes.
- [x] **JSON Import modal dialog & pure importer engine (`importer.py`, `export_dialog.py`):**
  - Pure parsing with schema detection (`boards`, `board`, or list) and statistics preview.
  - Interactive import mode: Full import vs. Column structure only (importing any JSON as a clean template without tasks).
  - Automatic tag category and value creation/reuse with color assignment.
  - Atomic database insertion with rollback safety and automatic UI selection/refresh.
  - 203/203 tests passing, ruff clean.

---

## ✅ Fixed (2026-08-18, v0.9.6 — TaskDetailDialog click-outside auto-save, title simplification, log layout fixes)

- [x] **Task card popup click-outside auto-save and close:** Clicking outside `TaskDetailDialog` within the main window now automatically executes `save_changes()` and closes returning to board view without forcing the user to press "Guardar Cambios".
- [x] **Window title simplified:** Changed `"main.window_title"` from `"Ekin Kanban - Trello Lite v{version}"` to `"Ekin v{version}"` and updated README title.
- [x] **Task diary/log horizontal card overflow & scroll position:** Removed QSS margin/padding from `#LogEntryWidget`, added `fit_html_images` to constrain images to chat width, replaced `AlignTop` with `addStretch()` and `QSizePolicy.Preferred` to ensure opening a task lands flush on the latest comment without empty bottom space. 190/190 tests passing, ruff clean.

---

## ✅ Fixed (2026-08-17, v0.9.5 — Windows taskbar icon hardening & installer direct binding)

- [x] **Windows taskbar icon fallback to generic Python script icon + installer launcher indirection.**
  Root cause (1): `SetCurrentProcessExplicitAppUserModelID` was executed inside `def main()` after
  `PySide6` imports had already loaded Qt's Windows platform plugin (`qwindows.dll`), which registered
  the process under the default `pythonw.exe` identity before the AppUserModelID was set. Fixed by moving
  the call to line 1 of `main.py` before any Qt/GUI imports, paired with an explicit `apply_win32_icon(window)`
  native `WM_SETICON` injection directly onto the window `HWND`.
  Root cause (2): `install.ps1` created desktop `.lnk` shortcuts targeting `lanzar.bat`, which spawned a detached
  `pythonw.exe` subprocess that Windows could not associate with the shortcut's icon. Fixed by making the
  desktop shortcut target `venv\Scripts\pythonw.exe` directly with `Arguments = "main.py"` and `IconLocation = ekin_icon.ico,0`.

---

## ✅ Fixed (2026-08-13, v0.9.4 — installer icon bug, user-reported)

- [x] **Desktop shortcut showing a blank icon + taskbar falling back to Python's generic icon
  on a colleague's machine.** Previously (2026-08-12) a similar taskbar-icon report on a second
  PC was traced to Windows icon-cache staleness with the app code already correct. This report
  paired a *blank* desktop icon (not even a generic one) with the taskbar issue — a symptom the
  cache-staleness explanation doesn't cover, since a cached-but-wrong icon still renders as
  *some* icon. Root cause: `install.ps1`'s `git pull`/`git clone` had zero error/exit-code
  checking, so a failed or partial update on a repeat install (existing `~/EkinKanban` folder)
  silently left the local checkout outdated or incomplete — including possibly missing
  `ekin_icon.ico` — while the script carried on regardless and built a shortcut against that
  broken checkout: `IconLocation` pointing at a nonexistent file renders as Windows' blank
  generic icon, and `main.py`'s `app_icon()` finding neither `.ico` nor `.png` returns a null
  `QIcon`, so the taskbar falls back to `pythonw.exe`'s own icon. Fixed by checking
  `$LASTEXITCODE` after `git pull`/`git clone` (stop with a clear message instead of continuing
  silently) and verifying `ekin_icon.ico` exists right before shortcut creation (warn explicitly
  if not, instead of producing a shortcut with a dead icon path). Also marked `*.ico`/`*.png` as
  `binary` in `.gitattributes`, defensively ruling out autocrlf line-ending corruption on
  checkout as a contributing factor. **Immediate workaround for the affected machine** (doesn't
  need to wait for a re-run): delete `~/EkinKanban` and re-run the installer for a clean clone,
  since the existing folder's `git pull` history/state is unknown.

---

## ✅ Fixed in the forensic pass (2026-08-12, third pass)

Same two-independent-agent format as the two prior passes — this time, both planned parallel
audit agents hit an API session-limit mid-run (one produced zero output, the other was cut off
with only a one-line hint recovered: "restore_column with a deleted board"). Rather than wait
for the limit to reset, continued the audit directly with `Read`/`Grep`/`Bash`, using that hint
as a starting point. Full writeup:
`.agents/docs/archive/2026-08-12_forensic-pass-restore-fk-and-imagepreview-leak.md`.

- [x] **Critical, systemic (two manifestations): `restore_task`/`restore_column` could crash
  the app on Ctrl+Z** — both functions fall back to the snapshot's own stored parent id
  (`column_id`/`board_id`) when none is passed explicitly, with no guard that it still exists;
  `tasks.column_id`/`columns.board_id` are `NOT NULL` FKs with `ON DELETE CASCADE`. Same
  failure class already fixed once for `restore_task`'s `linked_board_id`/`tag_value_ids`,
  never applied to either function's own required parent-id fallback. Reachable via an
  ordinary sequence: delete a task, delete its column, Ctrl+Z twice (or one level up: delete a
  column, delete its board, Ctrl+Z twice). Both crashes manually reproduced against the real
  `database` module before the fix, and reproduced again via `git stash` against the pre-fix
  code as part of QA. Fixed with a new `database/columns.py::get_column` (symmetric with the
  existing `get_board`) plus a guard in each `restore_*` function returning `None` instead of
  crashing — required zero caller changes, since `board_view.py`'s `_push_delete_undo` was
  already written to tolerate a `None` return.
- [x] **`ImagePreviewDialog` was never destroyed after closing** — same leak class already
  fixed once for `TaskDetailDialog`, never applied to this newer dialog (added 2026-08-12,
  first forensic pass to touch it). Confirmed via a direct repro (5 open+close cycles, all 5
  left as permanent children) before and after the fix. Fixed with the identical
  `self.finished.connect(self.deleteLater)` pattern.

---

## ✅ Fixed in the forensic pass (2026-08-10, v0.9.1)

Same two-independent-agent format as the 2026-08-07 pass (data/logic layer, UI layer + a dedicated
CI-flakiness investigation), every finding re-verified against actual source before acceptance.
Triggered by CI intermittently failing since the 2026-08-07 task-timer commit — pinpointed via the
GitHub Actions check-runs API (no `gh` CLI / log access available) to a different single
Python-version job failing on different runs, which pointed at a race/leak rather than a
deterministic cross-platform bug.

- [x] **CI crash root cause found and fixed: a stray, unparented `QTimer.singleShot` could fire
  against an already-destroyed widget.** `detail_dialog/task_detail_dialog.py`'s
  `scroll_to_bottom()` (called on every dialog open and every diary edit) scheduled a bare
  `QTimer.singleShot(50, lambda: scrollbar.setValue(...))` holding a closure over a child
  scrollbar. If the dialog was destroyed before the 50ms elapsed — which never happens during
  normal use, but routinely happens across a 166-test session where the event loop is only pumped
  once, at the very end — the timer fires later against a deleted C++ object. Reproduced directly
  (including the actual `STATUS_HEAP_CORRUPTION`/`0xC0000374` crash) against a realistic population
  of leftover dialogs. Fixed by parenting the timer to the dialog (`QTimer(self)`), so Qt cancels
  it automatically when the dialog is destroyed instead of leaving it dangling.
- [x] **Contributing hazard: `tests/test_main_window.py` left 3 `MainWindow()` instances alive with
  two more real, unparented timers pending** — one of which (`check_for_updates`) runs live `git
  fetch`/`git status` subprocess calls. Fixed by monkeypatching both to no-ops before construction
  and explicitly closing/deleting each window after its test.
- [x] **`restore_task()` (Ctrl+Z) loses `task_links` ordering** — was hardcoding every restored
  link's `position` to `0`; now the original position is captured in the snapshot and restored.
  Closes the item of the same name below. New regression test:
  `test_snapshot_and_restore_task_preserves_link_order`.
- [x] **Systemic double-commit pattern, audited and ruled out** — the dedicated audit this backlog
  asked for (below) happened as a side effect of removing ~40 redundant trailing `conn.commit()`
  calls across the whole `database/` package: every one of them was individually verified to be
  the *last* statement before its function returns (the connection context manager already commits
  on clean exit), never a *premature* mid-transaction commit like the original `create_log` bug.
  No other atomicity-breaking commits found.
- [x] **Dead code**: unused `styles.QSS` module-level constant (nothing has read it since
  `set_theme()` took over in the previous forensic pass) and an unreachable `sys.exit(0)` after
  `os.execv()` in `main.check_for_updates`.
- [x] **CI still red after the fix above (py3.10 only) — the broader "no shared cleanup" pattern
  really was load-bearing, not just theoretical.** The first push (timer fix + `MainWindow` cleanup)
  flipped CI from "all 3 Python versions fail" to "2 of 3 pass," confirming the mechanism but
  exposing that it wasn't the *only* source: dozens of other tests construct a
  `BoardViewWidget`/`TaskDetailDialog` and never close it, so hundreds of orphaned widgets still
  converged on one final teardown burst. Fixed with a `tests/conftest.py` autouse fixture that
  closes every top-level widget after *each* test instead of letting them all accumulate to
  session end — the fix originally logged below as "deferred, provably safe today" turned out not
  to be safe enough; it's done now, verified by re-polling GitHub Actions after the follow-up push
  (all 3 Python versions + lint + release green).

**New tech debt found this pass, deferred on purpose (see "Code quality & tech debt" below):**
`restore_column`/`restore_board` aren't atomic across their children (each nested
`restore_task`/`restore_column` call opens its own connection/transaction) — low practical impact,
not acted on.

---

## ✅ Fixed in the forensic pass (2026-08-07, pre-v0.9.0)

Two independent audit agents (data/logic layer, UI layer), every finding individually re-verified
against actual source before acceptance. Full writeup: `.agents/docs/archive/2026-08-07_forensic_fixes_pre_v0.9.0.md`.

- [x] **Critical: `TaskDetailDialog` leaked forever** — every task opened from the board or
  calendar left the dialog alive in the background with its 30s refresh `QTimer` still running,
  because nothing destroyed it after closing. Fixed with `self.finished.connect(self.deleteLater)`.
- [x] **Critical: `Ctrl+Z` could crash the app** — restoring a deleted task's tags during undo
  assumed every tag it had still existed in the catalog; a tag deleted in between raised an
  uncaught `sqlite3.IntegrityError` that escaped a Qt slot and terminated the process. Fixed by
  filtering stale `tag_value_id`s before restoring, mirroring the existing `linked_board_id` guard.
- [x] **Stale shortcuts help text** — `Ctrl+/`'s dialog still described `Ctrl+N`'s pre-"last active
  column" behavior.
- [x] **Calendar edits left the board card stale** — `on_calendar_task` never reloaded `board_view`
  (only its sibling `on_notification_task` did); fixed, scoped to only reload when the edited
  task's board matches the sidebar's active board.
- [x] **Copying a column/board silently dropped due time, recurrence, linked board, timer, and
  links** — `copy_column_to_board`/`copy_board` only ever carried title/description/tags/logs.
  Fixed via a shared `_duplicate_task_into_column` helper (also removed ~35 lines of duplicated
  logic between the two callers).
- [x] **`create_log` broke transaction atomicity** with a premature `commit()` between the diary
  insert and the parent task's `updated_at` update.
- [x] **Efficiency: `timer_alert_hours` re-read once per column** on every `load_board()` — now
  read once and passed down.
- [x] **Efficiency: N+1 diary export** — added `database.get_logs_bulk()`, wired into
  `exporter._gather()`.
- [x] **Dead code**: `app.setStyleSheet(styles.QSS)` in `main()`, unreachable since
  `apply_theme()` always overwrites it before any widget renders.
- [x] **Test-harness only: `pytest` crashed with `STATUS_HEAP_CORRUPTION` at interpreter shutdown**,
  after every test already reported `PASSED` — invisible until process exit codes were checked
  directly. Confirmed pre-existing (not a regression from this wave) via `git stash` against
  pristine pre-wave code. Root cause: the session-scoped `qapp` fixture never tore down
  accumulated Qt widgets before `QApplication` teardown, racing against CPython's own interpreter
  shutdown. Fixed with an explicit `qapp` fixture teardown in `tests/conftest.py`. Never affected
  the shipped app (which exits via `sys.exit(app.exec())`, not a pytest fixture).

**Explicitly deferred (documented, not acted on this wave — see "Code quality & tech debt" below):**
systemic double-commit pattern beyond `create_log`, `get_task()`/`get_tasks()` shape inconsistency,
an unreachable `backups._prune_backups(keep=0)` edge case, minor task-link ordering loss on
`restore_task()` (Ctrl+Z), `CalendarViewWidget.refresh()` running while hidden.

---

## ✅ Fixed in the forensic pass (2026-07-16)

- [x] **Board header showed a static "Mi Tablero"** — `load_board` never updated the title label; it
  now shows the selected board's real name. *(bug)*
- [x] **N+1 tag queries** — `get_tasks` / `get_scheduled_tasks` opened one connection per task to load
  tags. Added `get_task_tags_bulk()` (single query, grouped) and wired both to it. *(efficiency)*
- [x] **Stale test suite** — 3 `database` tests asserted the pre-`category_id` tag shape and were
  silently not running (pytest not installed). Aligned them and added tests for the new helpers
  (`get_scheduled_tasks`, `get_task_board_id`, `get_setting/set_setting`, `get_task_tags_bulk`).

---

## 🧹 Code quality & tech debt (found, not yet fixed)

- [x] **`db_path=DB_NAME` default binding is frozen at import.** *(Done in v0.4.0.)* All 38
  `database.py` functions now use `db_path=None` → `db_path or DB_NAME`, resolving at call time.
  Reassigning `database.DB_NAME` is honored everywhere; proven by `test_db_name_is_resolved_at_call_time`.
  **(P1 — consistency)**
- [x] **`TaskListArea.layout` shadows `QWidget.layout()`** (`widgets.py`). *(Done in v0.4.0.)* Renamed
  to `list_layout`. **(P2)**
- [x] **Connections are never explicitly closed.** *(Done in the post-0.6.0 readability pass.)*
  `get_connection` is now a real `contextlib.contextmanager` that closes in a `finally` block
  (commit on success, rollback on exception); all 58 call sites unchanged. **(P2 — perf)**
- [x] **`data_changed` fires on plain navigation, not just mutations.** *(Done in the post-0.6.0
  readability pass.)* `board_view.load_board(board_id, notify=True)` now skips the emit for
  pure-navigation callers (board switch, startup, theme reload); `TaskDetailDialog` tracks
  `self.modified` so opening a task to just look no longer triggers a bell/calendar/`.ics`
  refresh. **(P2 — perf)**
- [x] **Duplicated inline stylesheets.** *(Done in the post-0.6.0 readability pass — QMenu/swatch;
  extended 2026-08-03 with tag pills.)* `styles.style_menu()` / `styles.color_swatch_css()` /
  `styles.tag_pill_css()` cover QMenu, color-swatch and tag-pill duplicates across
  `widgets.py`/`sidebar.py`/`board_view.py`/`detail_dialog/*`, plus the tray menu. Other ad-hoc
  one-off inline styles (not actually duplicated elsewhere) intentionally left alone. **(P3)**
- [x] **Dead `#TaskCardDueDate` object name** *(Done in v0.4.0.)* — dropped the unused name (label is
  styled inline). **(P3)**
- [x] **iCalendar line folding** *(Done in v0.4.0.)* — continuations now cap at 74 content octets so
  the folded line (incl. the leading space) stays ≤75; unit-tested. **(P3)**
- [x] **Same-column drag reorder off-by-one** *(Done in v0.4.0.)* — the dragged card is excluded from
  the drop-index calc (`widgets.compute_drop_index`), with a regression test. **(P2 — bug)**
- [x] **Auto-updater uses `git pull`** *(Done 2026-09-11 in Theme D)* — implemented hybrid updater:
  checks GitHub Release assets when frozen/installed via `ReleaseCheckThread` and downloads setup executable,
  preserving git pull fallback in development. **(P2)**
- [x] **Systemic double-commit pattern beyond `create_log`** *(Audited and ruled out 2026-08-10 —
  see the forensic-pass section above.)* Found during the 2026-08-07 forensic pass while fixing
  `create_log`'s premature commit; the dedicated audit this item asked for happened as a side
  effect of removing ~40 redundant *trailing* commits — none were premature/mid-transaction.
  **(P2 — correctness/atomicity)**
- [x] **`get_task()` / `get_tasks()` return shape inconsistency** *(Done 2026-08-21)* — `get_task()` now populates `links` via `get_task_links()`, matching `get_tasks()` exact dictionary shape. **(P2 — consistency)**
- [x] **`backups._prune_backups(keep=0)` edge case** *(Done 2026-08-21)* — guarded against `keep <= 0` returning early without unintended pruning of all backups. **(P3)**
- [x] **`restore_task()` loses `task_links` ordering on Ctrl+Z** *(Done 2026-08-10 — see the
  forensic-pass section above.)* Links are now captured and restored with their real `position`.
- [x] **`CalendarViewWidget.refresh()` runs even while the calendar isn't visible** *(Done 2026-08-21)* — `refresh()` skips heavy queries and widget rebuilding when hidden, setting `_dirty=True` to refresh on `showEvent` / `show_calendar_view()`. **(P3 — efficiency)**
- [x] **Missing-file link rendering has no automated regression test** *(Done 2026-08-21)* — added comprehensive tests in `test_widgets_headless.py` for missing local files (danger color, missing tooltip), existing files (blue, path tooltip), and web links. **(P3 — test coverage)**
- [x] **`restore_column`/`restore_board` aren't atomic across their children** *(Done 2026-08-21)* — `restore_board` and `restore_column` run all nested child restorations within a single transaction / connection. **(P3 — atomicity)**
- [x] **No shared cleanup fixture for widget-constructing tests** *(Done 2026-08-10 — see the
  forensic-pass section above.)* Found during the CI-flakiness investigation: dozens of tests
  construct a `BoardViewWidget`/`TaskDetailDialog` without ever closing/deleting it, relying
  entirely on the session-end `qapp` teardown — turned out to still be a live CI-flakiness source
  (py3.10 kept failing even after the first fix), not just a theoretical one. Fixed with an
  autouse `tests/conftest.py` fixture that closes every top-level widget after each test.

---

## 🧪 Testing & tooling

- [x] Tests for `ics_export` (escaping, folding, `SEQUENCE`/`LAST-MODIFIED`, all-day `DTSTART/DTEND`).
  *(Done in v0.4.0 — `tests/test_ics_export.py`.)*
- [x] Headless (offscreen) smoke tests for the Qt widgets (calendar grid, bell popup, settings dialog).
  *(Done 2026-08-03 — `tests/test_widgets_headless.py` + a session-scoped `qapp` fixture in
  `conftest.py`; passes with `QT_QPA_PLATFORM=offscreen`, matching CI.)*
- [x] CI workflow running `pytest` on push/PR *(Done — `.github/workflows/ci.yml`, matrix py3.10–3.12
  with the Qt system libs; `test` job).*
- [x] `ruff` lint check in CI *(Done — `lint` job; ruleset `E4/E7/E9/F` in `[tool.ruff.lint]`, baseline
  clean).*

---

## 🚀 Feature backlog for new releases

### Reminders & calendar (build on 0.3.x)
- [x] **Overdue in the bell** *(Done in v0.4.0)* — past-due tasks now surface in their own "ATRASADAS"
  group above today/tomorrow, included in the badge count.
- [x] **Time-of-day due + `VALARM`** *(Done in v0.6.0)* — optional time on due dates, and reminder
  alarms in the `.ics`.
- [x] **Calendar: drag a task to change its due date** *(Done in v0.4.0)*, plus **Month/Week/Day
  views** *(Done in v0.6.0)*.
- [x] **Calendar: filter by board** + a board color legend *(Done in v0.6.0)*.
- [x] **"Subscribe in Google" helper** in Ajustes *(Done in v0.4.0)* — stores the public feed URL
  (`ics_public_url`) and a button that copies it and opens Google's *add-by-URL* page.
- [x] **Per-board `.ics` feeds** so each board can be a separate subscribable calendar. One-off
  **export** was per-board since v0.6.0; **auto-sync** (the always-up-to-date subscribable feed)
  became per-board too on 2026-08-03 — `board_ics_sync` table + `database/ics_sync.py`, a board
  picker in `CalendarSettingsDialog`'s auto-sync section (mirrors the export picker), and
  `main.py`'s `sync_ics()` now rewrites the global feed plus every configured per-board feed.

### Task power features
- [x] **Global search & filter** (by title, tag, due, board) *(Done in v0.5.0 — 🔍 sidebar button + Ctrl+F)*.
- [~] **Subtasks / checklists** inside a card — shipped in **v0.5.0** but **removed in v0.5.1** (product
  decision; the nested-checklist approach wasn't a fit). Could be revisited later with a different UX.
- [x] **Recurring tasks** (daily/weekly/monthly) *(Done in v0.6.0)*.
- [x] **Attachments / links** on cards *(Done in v0.6.0 — `task_links` table)*. **Extended
  2026-08-10** (user-requested): a **📁** browse button next to the existing URL/label inputs opens
  the native OS file picker to attach a local file instead of only pasting a URL (label auto-fills
  from the file name if left blank). Link rows now render **📎** for local attachments vs **🔗** for
  web links, and flag a local attachment in red with a tooltip if its file has since been moved or
  deleted (`os.path.exists` check at render time). Also fixed a latent bug where opening a local
  path silently did nothing — `QDesktopServices.openUrl(QUrl(raw_path))` is malformed for a bare
  Windows path; local links now go through `QUrl.fromLocalFile(...)`, and any link that still fails
  to open shows a warning dialog. No DB schema change (`task_links.url` already held either kind);
  classification is a scheme heuristic (`_is_local_link`) at render/open time.
- [x] **Undo/redo** for destructive actions (delete task/column/board) *(Done in v0.6.0 — snapshot/restore + `undo.py`)*.
- [x] **Keyboard shortcuts** — ~~`Ctrl+N` new task~~, ~~`Ctrl+F` search~~, ~~`Ctrl+Z`/`Ctrl+Y`
  undo/redo~~ all done earlier. `Esc` to close dialogs was already free (Qt's default `QDialog`
  behavior — verified empirically with a headless `QTest.keyClick` sweep across all 9 dialogs, no
  code needed). Arrow-key board navigation added 2026-08-03: **Alt+Up/Alt+Down** cycle boards
  (`SidebarWidget.select_adjacent_board`) — bare arrows were unavailable, already claimed by every
  text field and list widget in the app. **Extended 2026-08-07**: `Ctrl+Shift+N` (new column),
  `Ctrl+1`..`Ctrl+9` (jump to the Nth sidebar board via the new
  `SidebarWidget.select_board_by_index`), `Ctrl+,` (Ajustes), `Ctrl+Shift+C` (Calendar) — plus
  **Ctrl+/** opening a new `ShortcutsDialog` reference window that lists every shortcut in the
  app (new, pre-existing global, and rich-text-editor-local) grouped by category, since they'd
  been scattered across tooltips/README with no in-app place to see them all. **`Ctrl+N`
  refined 2026-08-07** (user-requested): now targets `BoardViewWidget._last_active_column_id`
  (the last column a card/`+ Añadir Tarea`/click touched, tracked via a new
  `ColumnWidget.column_activated` signal + task-card click wrapper), re-validated against the
  active board on every use so a stale or cross-board id safely falls back to the first column —
  instead of always adding to the first column regardless of context. Also fixed a latent
  guard bug in `board_view.add_column` (`board_id == -1` wasn't rejected, since `not -1` is
  `False` in Python) surfaced by exposing it to a global shortcut with no UI-visibility gate.
  **2026-08-07:** added a visible **❔** button to the sidebar utility bar (next to 🔍/📅/⚙) that
  opens the same shortcuts dialog — `Ctrl+/` alone had no UI entry point, and reads as
  `Ctrl+Shift+/` on a Spanish keyboard layout since `/` requires Shift there.
- [x] **Rich-text tables + strikethrough** in the description/diary editors *(Done post-0.6.0,
  2026-08-03)*. Pasting a table (Excel/Sheets/Word, or tab-separated text) inserts a real table
  instead of flattening it to text; the toolbar's **▦** button inserts an empty one. Strikethrough
  via Ctrl+Shift+X or a toolbar button, alongside the existing bold/italic/bullets.
- [x] **Arrows in rich text** *(Done 2026-08-05)*. Typing `-->` in the description or diary/chat
  editor auto-converts it to `→`; a toolbar button (next to bullets) inserts one too.
- [x] **Priority quick-selector** *(Done 2026-08-05)*. A **🚩 Prioridad** dropdown next to
  Etiquetas in the task detail dialog (Baja/Media/Alta by default, seeded on first use and merged
  with the pre-existing onboarding "Prioridad: Alta" demo tag rather than duplicating it). It's a
  fast UI shortcut over the same tag system — no new DB schema — so the chosen priority shows up
  as a pill on the board card automatically, through the existing tag-pill rendering.
- [x] **Board links on task cards** *(Done 2026-08-05)*. A task can point at a *different* board
  (e.g. a summary task in "Tareas" linking to the dedicated "SW X" board tracking that work in
  detail) via a new **🔗 Tablero vinculado** selector next to Etiquetas/Prioridad. The card then
  shows a colored, clickable **🔗 <board>** pill that jumps to that board instead of opening the
  task's own detail. New nullable `tasks.linked_board_id` column (`ON DELETE SET NULL`, so
  deleting the target board just clears the link); included in the task snapshot/restore
  (Ctrl+Z) round-trip.
- [x] **Hover-to-expand on collapsed columns** *(Done 2026-08-06)*. Extends the 0.5.1
  "drop-to-expand" behavior (which always dropped the card at the end): holding a dragged card
  over a collapsed column for ~650ms now unfolds it automatically so a real drop position can be
  chosen, via the same `compute_drop_index` mechanism already used by expanded columns. A quick
  drop before the timer fires still falls to the end (unchanged). **Critical crash fixed
  2026-08-07** (user-reported, real production drag): the initial implementation reloaded the
  *entire* board on hover-expand, which destroyed and rebuilt every column — including the one the
  dragged card was still being dragged out of; dropping the card afterward could crash the app.
  Fixed with a surgical `BoardViewWidget._rebuild_single_column(column_id)` that only ever touches
  the one column whose state actually changed, never the drag's source column. **Behavior
  finalized 2026-08-07** (same day, user-requested): the column now *always* folds back up once
  the drag ends, whether the card was dropped inside it, elsewhere, or the drag was cancelled — it
  no longer stays permanently unfolded just because the drop happened to land there. It's purely a
  temporary peek, never equivalent to manually clicking unfold.
- [x] **Task timer with a board-card badge + configurable alert threshold** *(Done 2026-08-07,
  user-requested)*. New **⏱ Temporizador** control in the task detail: **▶ Iniciar** records the
  start time (`tasks.timer_started_at`, nullable ISO timestamp) and shows a live elapsed-time
  counter; **↺ Reiniciar** resets it to now; **✕ Detener** clears it. All three are instant-persist
  (write to the DB immediately, like a diary entry or a link) rather than deferred to "Guardar
  Cambios". The same elapsed time shows as a badge directly on the board-view card — not just in
  the dialog — so tasks running too long are visible without opening each one; the badge turns red
  once it crosses `app_settings.timer_alert_hours` (a `QSpinBox` in Ajustes, default 24h, global
  for the whole app). `BoardViewWidget.refresh_timer_badges()` (a 60s `QTimer`) keeps visible
  badges' elapsed text current without any DB query or widget reconstruction. Carried through
  `snapshot_task`/`restore_task` for Ctrl+Z undo, same as `linked_board_id`.
- [x] **Click-to-enlarge pasted images** *(Done 2026-08-12, user-requested)*. An image pasted
  into the task description or diary/chat now opens in a larger centered view when clicked —
  while composing, while editing an existing entry, or once it's already been posted.
  `MarkdownTextEdit._insert_image` wraps the pasted image's data URI in a same-URI `<a href>`
  at insertion time, clickable via `QTextEdit.anchorAt()` (the three editable surfaces, all
  sharing `MarkdownTextEdit`) or `QLabel.linkActivated` (an already-posted entry's read-only
  `content_label`). New `detail_dialog/image_preview_dialog.py::ImagePreviewDialog` scales to
  90% of screen size and closes on click/Esc/close button. A press/release position-delta
  check keeps normal text-selection drags from being hijacked into opening the preview.
  **Fixed in v0.9.2** (same-day user feedback): a real bug — `content_label`'s
  `setTextInteractionFlags(Qt.TextSelectableByMouse)` was *replacing* the flag set instead of
  adding to it, silently stripping `LinksAccessibleByMouse`, so the preview silently did
  nothing on an already-posted entry despite working fine while composing (closed with a test
  that fires a real click, verified via `git stash` to fail against the pre-fix code — the
  original test only called the handler directly, missing this entirely). Also: the preview
  now always scales small images *up* instead of only ever scaling large ones down; and
  description-pasted images default to the same width as chat images
  (`desc_input.image_width_provider = self._chat_image_width`) instead of risking overflow on
  dialog resize. **Fixed same day, follow-up**: the preview still looked blurry — v0.9.2's
  "always scale up-or-down" fix addressed the dialog's scaling logic correctly, but `<a href>`
  and `<img src>` were still the *same* small, already-downscaled data URI, so enlarging meant
  interpolating detail an earlier downscale had already thrown away. `_insert_image` now stores
  a second, separately-scaled copy (capped at 1920px) specifically for the `href`, so the
  dialog scales down from real detail instead of up from a thumbnail. Manually verified: a
  3000×2000 paste now yields a 1920×1280 preview vs. a 614×409 inline thumbnail.

### Data & safety
- [x] **Automatic DB backups** *(Done in v0.4.0)* — `backups.py` writes a consistent SQLite snapshot
  to `backups/` on startup and keeps the 5 most recent.
- [x] **Export/report** — dump boards to JSON/CSV or a Markdown project report *(Done in v0.6.0 —
  `exporter.py`)*.
- [x] **Board archiving** (hide without deleting) *(Done in v0.6.0)*.

### UX & platform
- [x] **Two-row sidebar utility bar** *(Done 2026-08-07, user-requested)*. `SidebarWidget.
  _build_utility_bar()`'s clock + 5 icon buttons (🔔🔍📅⚙❔) were cramped into a single row that
  didn't fit comfortably in the ~220px sidebar; now the clock sits on its own centered row above a
  second, centered row of icon buttons. Purely a layout change (`QHBoxLayout` → `QVBoxLayout` +
  a nested row) — no button's behavior, size, tooltip, or object name changed.
- [x] **Settings screen** — persist window size/position, theme, notification prefs, sync path *(Done
  in v0.6.0 — `settings_dialog.py`; sync path already lived in `app_settings` since 0.4.0)*.
- [x] **Light theme** + theme toggle *(Done in v0.6.0 — QSS was already centralized)*.
- [x] **Internationalization (i18n)** — infrastructure done 2026-08-03: every user-facing string
  (~280) moved into `strings.py` (a flat `STRINGS` dict + `t(key, **kwargs)`), covering the whole
  app — `main.py`, `board_view.py`, `widgets.py`, `sidebar.py`, `calendar_view.py`,
  `search_dialog.py`, `settings_dialog.py`, `detail_dialog/*`. Spanish is still the only *active*
  language (no `.ts`/`.qm`/translator tooling, no language switcher yet — deliberately scoped to
  extraction-only per the user's direction) but adding a second language now only touches `strings.py`.
- [x] **Cross-platform notifications** — audited 2026-08-03 (code review, not live macOS/Linux
  testing — no such machine available here). Already portable: the only two OS-specific call sites
  (`subprocess.STARTUPINFO`, `ctypes.windll` AppUserModelID) are correctly guarded behind
  `os.name == 'nt'`, and `QSystemTrayIcon` usage already checks `isSystemTrayAvailable()`. One
  documented, unfixable-from-here limitation: `QSystemTrayIcon.showMessage()` has weak Notification
  Center integration on macOS (a Qt/OS gap — would need a native bridge like PyObjC).
- [x] **Taskbar icon showing as the generic Python icon on a second PC** *(Done 2026-08-12,
  user-reported)*. The code (absolute icon paths, an explicit AppUserModelID) was already
  correct as of 2026-07-29 — likely explanation is Windows caching the wrong icon on that PC
  under the *old* AppUserModelID from before that fix, a cache nothing since had invalidated.
  Versioned the AppUserModelID (`"EkinKanban.TrelloLite.2"`, `main.py`) so Windows treats it
  as a fresh identity. **Not fully verifiable from here** — the affected PC needs a `git pull`
  + relaunch; if the icon still doesn't refresh, the user needs to unpin/re-pin the taskbar
  icon or reboot, since no app-level code can force-clear another machine's OS icon cache.
- [x] **App icon redesigned with a transparent background** *(Done 2026-08-12,
  user-requested)*. `ekin_icon.png`/`.ico` no longer carry a baked-in white background/drop
  shadow — regenerated via a one-off Pillow script (per-pixel whiteness threshold, not a new
  runtime dependency) at all 7 `.ico` resolutions. **Retuned same day (v0.9.2)**: the first
  threshold (170–225) still left a visible grayish halo — most background pixels actually sit
  in 195–225 per a finer histogram of the true original (re-pulled from git history, since the
  file had already been overwritten once). Tightened to 140–165; outer-edge alpha is now
  uniformly `0` (was `0`–`97`). An opacity-mask visualization clarified along the way that what
  looked like a stray white shape was actually the badge's own intentional torn-corner design,
  correctly kept opaque — not something to remove.

### Packaging & distribution
- [x] **Standalone executable** (PyInstaller) so non-developers don't need Python/git. *(Done 2026-09-11 — `ekin.spec` & `installer.iss`)*
- [x] **Update from Releases** instead of `git pull` (download the latest release asset). *(Done 2026-09-11 — `main.py` ReleaseCheckThread)*

---

## 🗺️ Suggested next steps
1. ~~**0.3.2 (patch)** — ship the forensic fixes.~~ ✅ Released.
2. ~~**0.4.0** — reminders polish + automatic DB backups + P1 `db_path` normalization.~~ ✅ 2026-07-22.
3. ~~**0.5.0** — global search + subtasks/checklists.~~ ✅ 2026-07-29 *(subtasks later removed in 0.5.1)*.
4. ~~**0.5.1** — UX refinements: collapsible columns (+ drop-to-expand), plain/image paste, comment
   edit/delete, painted icons, Ctrl+B/N & Ctrl+K/I formatting, Outlook/iCloud sync docs, taskbar icon.~~
   ✅ 2026-07-30.
5. ~~**0.6.0** — calendar depth (Mes/Semana/Día + filter + VALARM + per-board feeds); recurring
   tasks; undo/redo; attachments/links; board archiving; export (JSON/CSV/MD); dark/light theme +
   Settings screen.~~ ✅ 2026-08-03.
6. ~~**Post-0.6.0 readability pass** — connection leak fix; `data_changed` over-firing fix;
   centralize QMenu/swatch QSS; split `detail_dialog.py` → `detail_dialog/` package (7 classes,
   one per file); split `database.py` → `database/` package (~60 functions across 11 domain
   modules, `DB_NAME`/`get_connection` kept together in `__init__.py` to preserve call-time
   resolution).~~ ✅ 2026-08-03.
7. ~~**0.7.0** — table paste/insert (Excel/Sheets/Word or tab-separated text; **▦** toolbar button
   for an empty table) + strikethrough (Ctrl+Shift+X) in the description/diary editors, released
   together with the readability-pass fixes above.~~ ✅ 2026-08-03.
8. ~~**Small-wins + medium batch** — `Esc`-closes-dialogs (verified, already free) + Alt+Up/Down
   board nav; tag-pill QSS centralization; light-theme hardcoded-color fixes (+ an `apply_theme`
   ordering bug so the fix actually takes effect on startup); per-board auto-sync `.ics` feeds;
   i18n string-extraction infrastructure (`strings.py`, ~280 strings); cross-platform notification
   audit (already portable, one documented macOS limitation); headless Qt widget smoke tests.~~
   ✅ 2026-08-03.
9. ~~**Arrows + Priority selector** — `-->` auto-converts to `→` in rich text (+ toolbar button);
   a **🚩 Prioridad** quick-selector in the task detail dialog, next to Etiquetas, that reuses the
   tag system so it shows on board cards for free.~~ ✅ 2026-08-05.
10. ~~**Board links on task cards** — a **🔗 Tablero vinculado** selector in the task detail dialog
   links a task to a different board; the card shows a clickable pill that jumps straight there.~~
   ✅ 2026-08-05.
11. ~~**Hover-to-expand on collapsed columns** — holding a dragged card over a collapsed column
   unfolds it temporarily so a drop position can be chosen, instead of always landing at the end;
   folds back up if the drag ends without dropping there.~~ ✅ 2026-08-06.
12. ~~**More keyboard shortcuts + a shortcuts dialog** — `Ctrl+Shift+N` new column, `Ctrl+1..9`
   jump to a sidebar board, `Ctrl+,` Ajustes, `Ctrl+Shift+C` Calendar, and **Ctrl+/** opens a
   reference dialog listing every shortcut in the app.~~ ✅ 2026-08-07.
13. ~~**Ctrl+N last-active column, two-row utility bar, hover-expand always re-collapses** —
   three independent refinements: `Ctrl+N` targets the last column interacted with instead of
   always the first; the sidebar utility bar spans two rows instead of one cramped one; a
   hover-expanded column now always folds back up when the drag ends, even if the card was
   dropped inside it.~~ ✅ 2026-08-07.
14. ~~**Task timer + board-card badge** — a **⏱ Temporizador** in the task detail (Iniciar/
   Reiniciar/Detener, instant-persist) shows the same elapsed time as a badge on the board card,
   turning red past a configurable Ajustes threshold — so stale tasks are visible without opening
   each one.~~ ✅ 2026-08-07.
15. ~~**v0.9.0 — forensic bug-hunt pass** — 2 critical fixes (leaked `TaskDetailDialog`+`QTimer`;
   uncaught `IntegrityError` crash on Ctrl+Z), 4 correctness fixes (stale shortcuts text, stale
   calendar-edited board card, silent data loss on column/board copy, `create_log` atomicity), 3
   efficiency/cleanup items, plus a pre-existing test-harness crash (`STATUS_HEAP_CORRUPTION` at
   pytest shutdown) found and fixed along the way. 159/159 tests passing, clean exit code.~~
   ✅ 2026-08-07.
16. ~~**Local file attachments on task links** — a **📁** browse button next to the existing
   enlaces/adjuntos inputs opens the native OS file picker to attach a local file instead of only
   pasting a URL; link rows render 📎 for local attachments vs 🔗 for web links, flag a missing
   local file in red, and fixed a latent bug where local paths never actually opened
   (`QUrl.fromLocalFile` instead of a malformed raw-path `QUrl`). No DB schema change. 166/166
   tests passing (7 new).~~ ✅ 2026-08-10.
17. ~~**v0.9.1 — forensic bug-hunt pass + CI fix** — found and fixed the root cause of CI
   intermittently failing since 2026-08-07 (a stray, unparented `QTimer.singleShot` that could fire
   against an already-destroyed widget, reproduced down to the actual native crash); a first push
   fixed that plus `tests/test_main_window.py` leaking real timers (incl. live `git` subprocess
   calls), which flipped CI from "all 3 Python versions fail" to "2 of 3 pass" — confirming the
   mechanism but exposing a second, broader source (dozens of tests never closing the widgets they
   construct), fixed with a follow-up push adding an autouse test-cleanup fixture, landing CI fully
   green (3 Python versions + lint + release), verified via the GitHub Actions API after each push.
   Also fixed `restore_task()` losing link order on Ctrl+Z; removed ~40 redundant `conn.commit()`
   calls across `database/` (doubling as the dedicated double-commit audit an earlier item asked
   for) plus two confirmed dead-code spots. 167/167 tests passing, ruff clean.~~ ✅ 2026-08-10.
18. ~~**Click-to-enlarge pasted images, taskbar icon cache fix, transparent icon redesign** —
   pasted images in the description/diary now open larger on click (new
   `ImagePreviewDialog`); the taskbar showing Ekin as a generic Python icon on a second PC
   traced to Windows caching an icon under a since-fixed AppUserModelID, addressed by
   versioning the identifier; `ekin_icon.png`/`.ico` regenerated with a real transparent
   background instead of a baked-in white one. 176/176 tests passing (9 new), ruff clean.~~
   ✅ 2026-08-12.
19. ~~**v0.9.2 — same-day fixes to the wave above, from direct user feedback** — a real bug
   (a `QLabel` interaction-flag call silently stripping `LinksAccessibleByMouse`) meant
   click-to-enlarge did nothing on an already-posted diary entry, fixed and locked in with a
   test proven via `git stash` to fail against the pre-fix code; the preview now upscales
   small images instead of only ever scaling large ones down; description-pasted images
   default to the same width as chat images; the icon's transparency threshold retuned
   (140–165, was 170–225) for a genuinely crisp, halo-free background. 178/178 tests passing
   (2 new), ruff clean. Cut as **v0.9.2**, tag + GitHub Release confirmed published.~~
   ✅ 2026-08-12.
20. ~~**Image preview resolution fix — same-day follow-up on v0.9.2** — the enlarged preview
   still looked blurry because `<a href>`/`<img src>` shared the same already-downscaled data
   URI; `_insert_image` now stores a separate, higher-resolution copy (capped at 1920px) just
   for the preview, so `ImagePreviewDialog` scales down from real detail instead of up from a
   thumbnail. Manually verified end-to-end (3000×2000 → 1920×1280 preview vs. 614×409 inline).
   180/180 tests passing (2 new), ruff clean. Cut as **v0.9.3**, tag + GitHub Release confirmed
   published.~~ ✅ 2026-08-12.
21. ~~**Third forensic bug-hunt pass** — a critical, systemic Ctrl+Z crash
   (`restore_task`/`restore_column` could raise an uncaught FK `IntegrityError` if a
   task's/column's parent was also deleted before the undo ran) and the `ImagePreviewDialog`
   memory leak (never destroyed after closing, same class already fixed once for
   `TaskDetailDialog`). Both bugs manually reproduced before the fix, and reproduced again via
   `git stash` against the pre-fix code during QA. Two planned parallel audit agents hit an API
   session limit mid-run; the audit continued directly rather than waiting for it to reset.
   183/183 tests passing (3 new), ruff clean. Not versioned as a new release — folded into
   `[Unreleased]` for the next cut.~~ ✅ 2026-08-12.
22. ~~**Task card popup click-outside auto-save, title simplification, log layout fixes** —
   clicking outside `TaskDetailDialog` within the main window auto-saves and closes into board view;
   simplified window title to `Ekin v{version}` and README title; fixed `#LogContent` font-size
   from invalid `12.5px` to `13px` (resolving vertical text collapse on edited comments);
   eliminated horizontal overflow on chat cards with image bounding and margin cleanup.
   189/189 tests passing (6 new), ruff clean. Cut as **v0.9.6**.~~ ✅ 2026-08-18.
23. ~~**Rich Text Formatting Wave: Syntax-Highlighted Code Blocks, Horizontal Rules, Text Color Palette, Web Links & Deletion** —
   Pygments code blocks with language dialog, markdown shortcut and 3-way deletion; separator line `---`; text color picker;
   URL link preservation and browser opening; full regression coverage.
   213/213 tests passing (10 new), ruff clean. Cut as **v0.9.7**.~~ ✅ 2026-09-03.

### 🎯 Theme D — Distribution ✅ (Done 2026-09-11)
**PyInstaller** standalone build (`ekin.spec`) + **Inno Setup installer** (`installer.iss`) + **update-from-Releases** (`main.py` `ReleaseCheckThread`) + automated Windows CI/CD release workflow (`.github/workflows/release.yml`) + version bump CLI (`scripts/bump_version.py`).

### 🔧 Ongoing tech debt (fold into any wave)
Remaining inline QSS beyond QMenu/swatch/tag-pill (misc one-off buttons, not actually duplicated so lower value).

