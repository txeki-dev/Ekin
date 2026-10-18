# Ekin Kanban

[![CI](https://github.com/txeki-dev/Ekin/actions/workflows/ci.yml/badge.svg)](https://github.com/txeki-dev/Ekin/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/txeki-dev/Ekin?label=release&sort=semver)](https://github.com/txeki-dev/Ekin/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-PolyForm--Noncommercial-lightgrey)](LICENSE)

Ekin Kanban is a sleek, resource-friendly, and offline-first personal Kanban board application. Designed for individual developers, project managers, and writers, it replicates the core Kanban workflow (similar to Trello or Linear) and pairs each task card with a personal activity journal (diary). This allows you to track not just where a task is, but also write daily logs, updates, and thoughts directly on each card.

---

## ✨ Key Features
- **Offline-First & Serverless**: Runs entirely on your local machine using SQLite. Your data never leaves your computer.
- **Native & Lightweight**: A native desktop app (Python + Qt) that ships no browser engine, unlike Electron-based alternatives.
- **Fluid Drag & Drop**: Native, smooth mouse controls to drag tasks across columns or reorder them, featuring crisp high-DPI drag previews and a dynamic insertion slot indicator that parts cards in real time to visualize exact target placement. Now supports **multi-card batch dragging** (`Ctrl + Click` to select multiple cards and drag the entire batch together) with 3D stacked previews, task count badges (`📦 {count}`), and full atomic undo/redo transactions.
- **Task Journaling (Diario)**: A vertical, scrollable, timestamped diary inside each task card, perfect for keeping track of developer progress logs.
- **Rich Notes & Code Blocks**: The description and diary feature enhanced 135% proportional line-height for effortless readability. Supports **bold** (Ctrl+B), *italic* (Ctrl+K), ~~strikethrough~~ (Ctrl+Shift+X), <u>underline</u> (Ctrl+U or Ctrl+S), **blockquotes / citations** (Ctrl+Shift+Q or `> `), **full paragraph alignment** (Left Ctrl+L, Center Ctrl+E, Right Ctrl+R, Justify Ctrl+J), **case transformations** (UPPERCASE Ctrl+Shift+U, lowercase Ctrl+Shift+L, toggle Shift+F3), **syntax-highlighted code blocks** (type ` ``` ` or click `</>`), **horizontal separators** (`---` or `―`), **text color customization**, nested bullet lists (Tab to indent), **numbered lists** (`1.` button or typing `1. `), and **clickable hyperlinks** (auto-linkified plain URLs or via `🔗`). External text can be pasted with original styling (Ctrl+V) or as plain text (Ctrl+Shift+V). Supports **pasting images** with context menu resizing (25%, 50%, 75%, 100%, custom px) and zoom preview, **Word-style tables**, and **local file/folder path detection** which automatically creates links in the task attachments panel. The **📎 insert file** button adds one or more files as links (also listed under attachments) — or just **drag files in from Explorer** — and typing **`@`** suggests the task's links/attachments (plus, on boards linked to a local folder, the repo's files) to mention them inline. Includes a last-edited timestamp visible in the Notes header.
- **Collapsible Columns**: Fold a column you're not working on down to a slim strip (just its name and task count) with the **◀** button to save horizontal space.
- **Global Search & Filter**: A 🔍 button (or **Ctrl+F**) searches every board by title/description and filters by board, tag, or due date; click a result to jump straight to its card.
- **Due Dates, Times & Recurring Tasks**: Assign a due date (and optional **time**), plus a **recurrence** (daily/weekly/monthly) — overdue recurring tasks roll forward automatically. Cards show **🔁** for recurring and multiple custom-colored tag pills.
- **Independent Priority Management**: Completely decoupled from generic tags with a dedicated **Priority Manager** dialog (accessible via "Gestionar" in Task Detail) to customize priority levels and color swatches independently, showing as its own pill row on the board card.
- **Task Timer**: Click **Start** in the task detail to record when you started it; a live "time elapsed" counter shows next to it, and the same badge appears right on the board card — turning terracotta once it crosses a configurable threshold in Settings, so stale tasks stand out without opening each one.
- **Board Links**: Point a task at a *different* board — e.g. a summary task in "Tareas" that links to the dedicated "SW X" board where its detailed work lives. Pick the target from **Linked board** in the task detail; the card then shows a clickable pill that jumps straight there.
- **Calendar View & Reminders**: **Month / Week / Day** views with a **board filter** and color legend; **drag a chip to reschedule**; a deadline **bell** that groups **overdue**, today's and tomorrow's tasks; and native **Windows notifications**.
- **Calendar Sync (iCalendar)**: An always-updated `.ics` feed (with **timed events + `VALARM` reminders** and **per-board feeds**) you can **subscribe** to from Google/Apple/Outlook. A **"Subscribe"** helper copies the URL and opens the provider page.
- **Attachments / Links**: Attach a web URL, or click **📁** to browse your PC and attach a local file. Local attachments show a **📎** icon (web links keep **🔗**) and turn red with a warning if the file's since moved or been deleted; open or remove either kind from the task detail. Files inserted, pasted or dragged into the description or journal are added here automatically, and `@` in either editor mentions any of them.
- **Undo / Redo**: **Ctrl+Z / Ctrl+Y** restores a deleted task, column or board — with all its tags, diary and links.
- **Keyboard Shortcuts**: Quick actions for new tasks/columns, jumping between boards, opening Settings/Calendar, and more — press **Ctrl+/** anytime to open a reference dialog listing every shortcut in the app.
- **Board Archiving & Advanced Export/Import**: Archive boards to declutter the sidebar; export everything or single boards to **JSON / CSV / Markdown** with options for full task backup or **column structure templates** without tasks; import JSON boards and templates directly into Ekin.
- **Shared Boards & Cloud Linking (Google Drive, Dropbox, OneDrive, LAN)**: Link any board to an `.ekboard` file or open existing shared boards from collaborators, from the board footer or the sidebar. Features an offline-first **two-way differential merge engine** (concurrent edits of the same task are merged field by field) with automated pre-merge snapshots, non-blocking asynchronous background sync, reactive file watching, and **no-data-loss conflict resolution** (superseded concurrent edits are automatically archived into the task's personal diary/chat).
- **Bulk Task Creation**: Quickly define and import multiple tasks at once through the dedicated **Bulk add** button in the board header. Supports column assignment and copy-pasting directly from spreadsheets (Excel, Google Sheets).
- **Multi-Card Selection (`Ctrl + Click`) & Batch Drag**: Select multiple task cards across columns with `Ctrl + Click` and drag them together to another column in a single move.
- **Internationalization (i18n)**: Full bilingual support (**English** by default, **Español**) with live hot-reloading across the entire UI, boards, sidebar, and tray menu, switchable instantly in Settings.
- **Themes & Settings**: A settings screen with two tabs — **General** (Light / Dark theme, with the light "Warm Shell" as default; language; notifications; task-timer alert threshold; reminder lead days; weekly digest; update check; welcome tour) and **Local folders** (each board's repo folder) — plus a remembered window size.
- **Automatic Backups**: On every startup Ekin snapshots your database into a `backups/` folder (keeping the most recent few) before applying any changes — a cheap safety net against accidents.
- **Collapsible Sidebar & Status Footer**: Hide or reveal the sidebar with the **‹ / ›** button at the left of the board header to maximize work space. The board header holds the title and the actions (Bulk add, Prompts, Diary, Work); a **status footer** shows the task count and the AI agent (MCP) and cloud sync buttons.
- **Column & Board Copying/Moving**: Easily move or copy columns to other boards, or copy complete boards with all sub-tasks, tags, and diaries.
- **"My Work / Today" Cross-Board Workspace**: A dedicated home view (sidebar list icon or **Ctrl+0**) aggregating everything due Today, Tomorrow, Overdue, and This Week across all your boards, plus an active "In Progress" section tracking running timers. Click any task to navigate directly to its card.
- **Command Palette (`Ctrl+K`) & Quick Capture**: Unified search overlay and command runner. Instant fuzzy search across boards and tasks, one-click execution of navigation and view commands, and inline quick capture (`+ title`) to create tasks on the fly without changing views.
- **In-App Analytics Dashboard & PDF Report Export**: Real-time metrics dashboard (**Ctrl+D**) with custom-rendered charts for task distribution by status, column, tag, priority, and board, alongside timer analytics and diary velocity. Export clean, client-ready PDF reports natively with zero external dependencies.
- **Smart Reminders & Weekly Digest**: Configurable advance notifications (alert N days prior to due dates in Settings) plus automated once-per-week Monday morning digests summarizing upcoming deadlines, overdue tasks, and past week completions.
- **Focused Local AI**: Local AI only does what complements frontier agents connected through MCP: detecting duplicate tasks within a board (local vector embeddings via Ollama, or a pure-Python fallback), masking sensitive data before it leaves the app (Privacy Shield), and condensing the board and task context served over MCP to save tokens (executive summaries with WIP/stagnation metrics, condensed task context). Per-task helpers (break down, summarize, checklist, tag/title suggestions), the SPEC generator and the Daily Standup view were removed: an agent working through MCP does these better.
- **Application Diagnostic Logging & Crash Guard**: File logging with rotation under `~/.ekin/logs/ekin.log` and non-fatal crash handlers intercepting unexpected exceptions to safeguard user data.
- **Board Templates & Custom Presets**: Quickly bootstrap new workspaces using factory-designed presets (`DEV` with Scrum stages & WIP limits, `Socrático` — question-guided study for any subject, with study rounds, spaced repetition and mock exams — `GTD` with Getting Things Done contexts, or Blank), or save any configured board as a reusable custom template with starter seed tasks.
- **AI Agent Integration via Model Context Protocol (MCP), Live Refresh & Privacy Shield**: Connect external AI coding assistants (Google Antigravity / AGY CLI, Claude Code, Cursor, Claude Desktop) directly to specific boards via a sandboxed local MCP server (HTTP/SSE or STDIO) with semantic vector search (`search_tasks_semantic`), batch task creation (`create_tasks_batch`), and ISO task timer controls. Features zero-cost, lock-free SQLite multi-process reactive auto-refresh (`PRAGMA data_version`), preserving scroll positions and flashing an activity badge (`✨ Updated by AI`) on the MCP button in the board footer, plus real-time hot-reloading of open task detail modals — and closing a task only saves the fields *you* changed, so edits made meanwhile by an agent, another window or a synced board are never reverted. The server starts with the app whenever a board has MCP enabled (only one open Ekin can hold its port: a second one shows *AI Agent (MCP) unavailable* in the footer instead of silently sharing it); agents see each column's role (backlog / ready / in progress / review / done) and the active task, and their Markdown renders with formatting. Includes automated Privacy Shield sanitization (masking API keys, tokens, SSH keys, URLs with credentials, and emails), executive summaries, and condensed task context tools. Strictly protects board isolation and enforces human governance (column structures cannot be modified by AI).
- **Local Folder per Board, *Work* & Dev Diary**: Link a board to its local folder (repo) — from **Settings → Local folders**, **Edit board**, or simply the first time you click **▶ Work**. AI agents get it over MCP as their working directory, and `@` mentions offer its files. **▶ Work** (*Trabajar*) starts the MCP server, updates your AI CLI (Claude Code, Antigravity CLI or Gemini CLI — auto-detected, with a picker if you have several), registers the board in it and opens it in a new console in the repo with the board's start prompt (CLIs installed through npm get it on the clipboard). A **Diary** button opens the repo's Markdown and text files: `diary.md` / `diary_archive.md` first, then the other `.md` / `.txt` files of the root, each in its own tab, plus a **More…** menu with the ones in subfolders (dependency and build folders are skipped). The folder never leaves your computer (not synced, exported or templated).
- **AI CLI Quota Traffic Light**: A dot in the sidebar turns green / amber / red with Claude Code's remaining session (5 h) and weekly quota; click it for the details and reset times. Opt-in: it reads Claude Code's documented status-line data through a small status line Ekin installs (backing up `~/.claude/settings.json` and keeping any status line you already had).
- **AI Prompt Clipboard per Board**: The **Prompts** button in the board header opens ready-to-copy prompts for AI agents working on that board through MCP, with the board name and its MCP server already filled in. Ships with a **DEV** pack (the hybrid TDD workflow: INTRO, FEATURE PLAN/BUILD, OUTRO, AUDIT, REMEDIATE, RDi, RECOVER… with the board replacing `diary.md`/`backlog.md`), a **Socratic** pack for any subject (study sessions, a Socratic dialogue that makes you explain a topic and guides you with questions and hints instead of answers, self-tests that let you retry before revealing the answer, outlines that start from your own draft, spaced repetition, mock exams) and a **GTD** pack (a start prompt for **▶ Work**, capture, inbox processing, daily plan, weekly review). Packs share the JSON format of [AI-Dev-Prompt-Clipboard](https://github.com/txeki-dev/AI-Dev-Prompt-Clipboard) and can be imported; each board remembers its pack.
- **Interactive In-Situ Onboarding & Landing Tour**: On first launch, new users are welcomed with an interactive "🚀 Primeros Pasos" ("Getting Started") demo board featuring structured seed tasks and a step-by-step contextual tour banner (`InteractiveTourBanner`) guiding them through task editing, drag & drop, WIP limits, shortcuts, and AI agent integration. Also includes the illustrated 4-slide visual guide (`LandingTourDialog`), accessible anytime from Settings.
- **Manual Update Check**: Instantly verify whether you are on the latest version with the "Check for updates" button in Settings, supporting both Git-managed developer checkouts and standalone Windows installer packages.
- **"Warm Shell" Organic Design**: A calm, modern interface built on a single warm accent (terracotta) over a cream ground, with Caprasimo display type and Lucide icons. Ships with a **light "Warm Shell"** theme (the default) and a warm-espresso **"Night Lanes"** dark theme, both switchable live from Settings, plus customizable colors for columns, boards, and tags.

---

## 🛠️ Setup & Installation

### 🚀 Standalone Windows Installer (Recommended for Users)

No Python, Git, or administrative rights required!

1. Download the latest installer (`Ekin-Setup-vX.X.X.exe`) from the [**GitHub Releases**](https://github.com/txeki-dev/Ekin/releases/latest) page.
2. Double-click the installer and follow the wizard.
3. Launch Ekin Kanban directly from your Desktop or Start Menu shortcut.

> [!TIP]
> **Automatic Updates**: When a new release is published, Ekin automatically detects it on startup, notifies you, and can download and apply the update seamlessly with one click.

> [!NOTE]
> **Windows SmartScreen Notice**: Windows may display a blue warning (*"Windows protected your PC / Unknown publisher"*) when launching the installer for the first time. This is standard for newly released software that does not carry an expensive enterprise commercial signing certificate. Simply click **"More info"** and then click **"Run anyway"**.

---

### 💻 Developer Installation (From Source)

If you prefer to run from source, contribute, or are on macOS/Linux:

#### Prerequisites
Ensure you have **Python 3.10+** and **Git** installed on your system.
* [Download Python](https://www.python.org/downloads/)
* [Download Git](https://git-scm.com/downloads)

#### Quick Setup (Windows PowerShell)
```powershell
irm https://raw.githubusercontent.com/txeki-dev/Ekin/main/install.ps1 | iex
```

#### Manual Setup (All Platforms)
1. **Clone the repository**:
   ```bash
   git clone https://github.com/txeki-dev/Ekin.git
   cd Ekin
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the environment**:
   - **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
   - **Windows (CMD)**: `.\venv\Scripts\activate.bat`
   - **macOS / Linux**: `source venv/bin/activate`
4. **Install dependencies**:
   ```bash
   pip install -e .
   ```

---

## 🧪 Development & Testing

For development, install the optional `dev` dependencies (includes `pytest`):

```bash
pip install -e ".[dev]"
```

Run the linter and test suite before opening a pull request (the CI workflow runs the same checks on
every push to `main` and every PR, across Python 3.10–3.12):

```bash
ruff check .
pytest
```

The suite (600+ tests) covers the database layer, the `.ekboard` sync engine, the MCP server, prompt packs, local AI helpers, exporters, backups and the Qt widgets (headless, with `QT_QPA_PLATFORM=offscreen`), always against temporary, isolated SQLite databases (no risk to your local `ekin_board.db`).

---

## 🔄 Automatic Updates

When you open Ekin Kanban, the application automatically performs a quick, silent check against this GitHub repository in the background. 

If there is a newer version available on the `main` branch, a prompt will ask:
> *“A new version of Ekin Kanban is available on GitHub. Do you want to download it and restart the app now?”*

Clicking **Yes** fast-forwards the checkout (`git pull --ff-only`) and restarts the app on the spot. Installer-based copies check GitHub Releases instead and download the new installer.

---

## 🚀 Running Ekin Kanban

* **Windows**: Double-click the **Ekin Kanban** shortcut on your Desktop (or Start Menu), or run `venv\Scripts\pythonw.exe main.py` in the application folder.
* **Manual/Other Platforms**: Run `python main.py` inside your active virtual environment.

The database (`ekin_board.db`) is automatically initialized on the first run, and a demo board with onboarding columns and cards is generated for you.

---

## 📖 How to Use Ekin Kanban

### 1. Managing Boards (Sidebar)
* Use the **Sidebar (left panel)** to switch between different projects or workspaces.
* Click **New board** (*Nuevo tablero*) at the bottom of the sidebar to open the template browser (see section 6), name the board and pick its color. **Archived boards** sit behind the button next to it.
* The active board's row has an **options** button (sliders icon) that opens the board options: **Edit** (name, color and local folder), **Copy** (clones columns, tasks, tags and diaries), **Archive**, **Link / sync with the cloud**, **Save as template**, **AI agent (MCP)**, **Import**, **Export** and **Delete**.
* Use **Alt+Up / Alt+Down** anywhere to jump to the previous/next board without touching the sidebar.
* **Reorder boards** by dragging a board onto another one in the sidebar (it lands before or after it); the order is saved and `Ctrl+1..9` follows it.
* **Link a board to its local folder (repo)** in **Settings → Local folders** (every board at a glance), in **Edit board**, or by clicking **▶ Work** on a board that has none yet.
* **Export** writes all boards or the active one to JSON, CSV or Markdown (also column-structure-only templates); **Import** brings JSON backups or templates into Ekin.

### 2. Organizing Columns & Tasks
* Inside a board, click **New column** (*Nueva columna*) to create stage headers (e.g., "To-Do", "In Progress", "Done").
* **Reorder or move columns**: click and drag a column by its **title** to reorder it within the board, or drop it onto another board's button in the sidebar to move it there.
* **Column Actions**: Click the **pencil (✎)** button in a column header to edit its name/color, delete it, or **copy** (clone) it and its tasks to another board.
* **Collapse a column**: Click **◀** in the header to fold a column into a slim strip (name + task count); click **▶** on the strip to expand it again. The state is remembered per column, and **dropping a card onto a collapsed column expands it** and drops the card in. If you instead **hover a dragged card over the collapsed strip for about a second**, it unfolds automatically *while you're still dragging*, so you can pick exactly where in the column the card lands instead of it always going to the bottom — drag it away without dropping there and the column quietly folds back up.
* Click **+ Add task** (*Añadir tarea*) at the bottom of any column to quickly add a card.
* **Drag & Drop**: Click and hold a task card to drag it to another column or change its vertical position.

### 3. Detail View, Structured Tags & Due Dates
* Click on a task card to open the **Detail View**.
* On the **left panel**:
  - Change the task title and description. The toolbar (and shortcuts) give **bold** (Ctrl+B), *italic* (Ctrl+K), ~~strikethrough~~ (Ctrl+Shift+X), bullet lists — press **Tab** on a bullet to nest it — and **arrows** (type `-->` or use the toolbar's **→** button). Pasting keeps the original formatting (**Ctrl+V**) or pastes plain text (**Ctrl+Shift+V**), and you can **paste images** directly into the notes. Pasting a **table** (from Excel/Sheets/Word, or plain tab-separated text) inserts a real table, and the **▦** toolbar button creates an empty one (asks for rows/columns) — press **Tab** in the last cell to add a row.
  - **⏱ Temporizador**: click **▶ Iniciar** to record the start time; while running, **↺ Reiniciar** resets it to now and **✕ Detener** clears it. Both take effect immediately (no need to click "Save changes"). The elapsed time also shows as a badge on the board card, in red once it's been running longer than the threshold set in Ajustes.
  - Set a **due date** using the calendar popup widget.
  - Click **➕ Asignar Etiqueta** to add a tag as a **Category: Value** pair (e.g. "Prioridad: Alta"), with its own color. Reusing an existing value keeps its color consistent everywhere it's used; typing a new one creates it on the fly. Next to Etiquetas, the **🚩 Prioridad** dropdown is a one-click shortcut for the same "Prioridad" tag — pick Baja/Media/Alta (or "— Sin prioridad —") without going through the full tag picker. Next to that, **🔗 Tablero vinculado** links the task to a *different* board (any board except the one the task is already on); once set, the card shows a clickable pill that jumps straight to that board.
  - **🔗 Enlaces / adjuntos**: paste a URL/path directly, or click **📁** to browse your PC and attach a local file — the label auto-fills with the file name if you leave it blank. Web links show **🔗**, local files show **📎**; an attachment whose file has since been moved or deleted turns red with a tooltip explaining why, but stays there so you can remove it. Both are saved instantly (no need to click "Save changes") and can be opened or removed (🗑) at any time. You can also **drag files from Explorer** onto the description or a journal entry: they're linked inline and attached here.
* On the **right panel (Diario)**, type notes or updates about what you did (same formatting, tables, pasting, images and attachments), and press `Ctrl + Enter` (or click **✍️ Añadir al Diario**) to post it. Each note is saved with an automatic date and time stamp.
* Each note has an **edit (✎)** and a **delete (×)** button — editing opens an inline editor (save or cancel); deleting removes the note.
* Click **Save changes** — or simply click outside the detail, which saves and closes it — or **Delete** to remove the entire task. Only the fields *you* changed are saved: if an AI agent, another window or a synced board changed the task meanwhile, its other changes are kept. While you have nothing unsaved, the detail even refreshes live, and if the task is deleted elsewhere it tells you and closes.
* Collapse the sidebar with the **‹ / ›** button at the left of the board header to maximize workspace size.

### 4. Calendar, Reminders & Notifications
At the top of the sidebar there is a small utility bar:
* 🕐 A live **date & time** clock.
* ☰ A **My Work** button (or **Ctrl+0**) with everything due or in progress across all boards.
* 🔔 A **deadline bell** with a count badge: click it to see the tasks (from **all** boards) grouped into **ATRASADAS** (overdue), **HOY** (today) and **MAÑANA** (tomorrow). Click any of them to jump straight to its board and open the card.
* 🔍 A **search button** (or **Ctrl+F** anywhere) that opens global search: filter tasks across every board by text (title/description), board, tag, and "only with a due date", then click a result to jump to its card.
* 📅 A **calendar button** that switches the main area to a **monthly calendar view**. Navigate months with `‹ › / Hoy`, click a task chip to open its card, **drag a chip onto another day to change its due date**, and use **✖ Cerrar** to return to the board or **⚙ Ajustes** to configure calendar sync (see below).
* ● A **quota traffic light** for your AI CLIs (Claude Code's remaining 5-hour and weekly quota; enable the reading once from its popup).
* ⚙ A **Settings** button (or **Ctrl+,**): General preferences and the **Local folders** of your boards.
* ❔ A **shortcuts button** that opens the "Atajos de teclado" reference dialog (same as pressing **Ctrl+/**).

When the app starts (and once per day thereafter), Ekin also shows a **native Windows notification** listing the cards that are due today. Ekin lives in the system tray while running — double-click the tray icon to bring the window back.

Every time Ekin starts it also writes an automatic **backup** of your database into a `backups/` folder next to `ekin_board.db` (the five most recent are kept), so an accidental delete is never fatal.

### 5. Keyboard Shortcuts
Press **Ctrl+/** anywhere, or click the **❔** button in the sidebar utility bar, to open a reference dialog listing every shortcut in the app, grouped by category — the list below is a summary:
* **Ctrl+N** — new task in the last column you interacted with (opened a card in, clicked "+ Añadir Tarea" in, or just clicked); falls back to the first column if nothing qualifies yet. **Ctrl+Shift+N** — new column in the active board.
* **Ctrl+1** … **Ctrl+9** — jump straight to the 1st through 9th board in the sidebar. **Alt+↑ / Alt+↓** — previous/next board.
* **Ctrl+K** — Command Palette (search tasks and boards, run commands, inline quick task capture with `+ title`).
* **Ctrl+0** — open "My Work / Today" cross-board overview.
* **Ctrl+D** — open Analytics Dashboard with visual charts and PDF report export.
* **Ctrl+F** — global search dialog. **Ctrl+,** — open Settings. **Ctrl+Shift+C** — open the Calendar.
* **Ctrl+Z / Ctrl+Y** (or **Ctrl+Shift+Z**) — undo/redo. **Esc** — close the open dialog.
* Inside the description/diary editor: **bold** (Ctrl+B or Ctrl+N), *italic* (Ctrl+K or Ctrl+I), ~~strikethrough~~ (Ctrl+Shift+X), underline (Ctrl+U or Ctrl+S), `@` to mention an attachment, **Tab** to nest a bullet, typing `-->` for **→**, and **Ctrl+Enter** to post a diary note.
 
### 6. Board Templates & Custom Presets
* **Create from Template**: Click **New board** to open the template browser. Pick from factory presets (`DEV`, `Socrático`, `GTD`, `Tablero en Blanco`) or your saved custom templates. Preview columns, WIP limits, and tags directly in responsive chips.
* **Save Board as Template**: Open the active board's **options** (sliders icon on its sidebar row) and choose **Save as template** to snapshot your column workflow, tag categories, and (optionally) existing tasks as starter seeds for future boards. Saved templates can be managed, filtered, and reused anytime.

### 7. Connecting AI Agents via MCP (Model Context Protocol)
* **Sandboxed AI Collaboration**: Click the **Connect AI (MCP)** / **AI Agent (MCP)** button in the board's **footer** (which also shows the task count and cloud sync status) to connect external AI agents (Google Antigravity / AGY CLI, Claude Code, Cursor, Claude Desktop).
* **1-Click Setup**: Turn on **Enable MCP access for this board** and save: the local server starts (`http://127.0.0.1:8765`) and, from then on, starts with the app. If you leave the token field empty, Ekin generates one, so only clients you give it to can reach the board. Copy the snippet for your client from the dialog's tabs:
  - **Claude Code**: `claude mcp add --transport sse ekin-<board> "http://127.0.0.1:8765/sse?board=<UUID>&token=<TOKEN>"` (or let **▶ Work** register it for you).
  - **Claude Desktop / Cursor / Windsurf**: JSON configuration with the board's SSE URL.
  - **AGY CLI / stdio**: `python -m ekin_mcp --board-uuid <UUID> --token <TOKEN>`.
* **▶ Work**: on a board linked to a local folder, the **Work** button in the board header opens your AI CLI right in the repo, with the board's MCP server running and registered and the start prompt (INTRO) loaded — or on the clipboard for npm-installed CLIs.
* **Secure Governance**: The AI agent operates in a strict sandbox restricted only to that board. The agent can list, create, update, move, and comment on tasks (its journal entries are signed `[<client>]: …`, e.g. `[Claude Code]`), while column creation and structural alterations remain strictly reserved for the human user. All agent mutations reflect live in Ekin in real time.
* **Task ids**: agents refer to cards by their id. Every card shows it in muted text before its title (e.g. `#108`), and so does the header of its detail view, so you can always tell which card an agent means.

---

## 📅 Syncing Your Due Dates with Google Calendar, Apple & Outlook

Ekin turns every task that has a due date into an **all-day event** in a standard **iCalendar (`.ics`)** file. There are two ways to use it, reached from **Calendario → ⚙ Ajustes**:

* **⬇ Exportar copia…** — a one-off snapshot you can *import*. Simple, but it's a fixed photo: later changes and deletions are **not** reflected, and re-importing can create duplicates in some apps.
* **📂 Elegir archivo… (recommended)** — Ekin keeps a single `.ics` **always up to date** (it rewrites it whenever tasks change). You **subscribe** to that file once, and additions/edits/deletions then propagate automatically, with no duplicates.

### Setting up an auto-updating subscription
1. In Ekin, open **Calendario → ⚙ Ajustes → 📂 Elegir archivo…** and save the `.ics` **inside a cloud-synced folder** (Dropbox, Google Drive, or OneDrive), e.g. `Google Drive/Ekin/ekin.ics`. Ekin keeps it fresh; your cloud client uploads it.
2. Get a **public, direct-download URL** for that file (this is the step people get wrong — the plain "share" link points to an HTML preview page, which calendars can't read):
   * **Google Drive** — share the file as **"Anyone with the link → Viewer"**, then build the direct URL from the file ID (the part between `/d/` and `/view`):
     ```
     Share link:  https://drive.google.com/file/d/FILE_ID/view?usp=sharing
     Use instead: https://drive.google.com/uc?export=download&id=FILE_ID
     ```
   * **Dropbox** — copy the share link and change its trailing `?dl=0` to **`?dl=1`**.
   * **OneDrive** — **Share** → **Anyone with the link** → copy the link.
   * **Tip:** open your final URL in a private/incognito window — you should see raw text starting with `BEGIN:VCALENDAR`. If you get a login page or an HTML preview, the URL or the sharing permission is wrong.
3. Subscribe from your calendar app using that URL. In **⚙ Ajustes** paste it into the **🌐 Suscribirse en tu calendario** box, then use the button for your provider (it saves the URL, copies it, and opens the right page). Detailed steps per provider:

   **🟦 Google Calendar** (must be done on a computer — the mobile app can't add by URL):
   1. Click **Google** in Ekin (or go to Google Calendar on the web).
   2. Left sidebar → **Other calendars** → **+** → **From URL**.
   3. Paste the URL (`Ctrl+V`) → **Add calendar**.
   4. Google re-fetches external URLs **slowly (every several hours, up to ~24 h)** — this can't be forced.

   **🟧 Outlook**:
   * **Outlook.com / Microsoft 365 (web)** — click **Outlook** in Ekin (opens *Add calendar*), then **Subscribe from web** → paste the URL → give it a name/color → **Import/Subscribe**. (Work/365 accounts: same option at *outlook.office.com*.)
   * **Outlook desktop (classic)** — **Home** → **Open Calendar** → **From Internet…** → paste the URL → **OK**.

   **🍎 Apple / iCloud** (uses a `webcal://` link — click **Apple / iCloud** in Ekin to copy it in that form):
   * **iPhone / iPad** — **Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar** → paste the link → **Next**.
   * **Mac (Calendar app)** — **File → New Calendar Subscription…** → paste the link → **Subscribe**; here you can set the **refresh frequency** (as often as every few minutes). The subscription lives in iCloud and appears on all your Apple devices.

### What to expect
* The calendar **appears within a minute or two** if the URL is valid. If it shows up empty or errors out, it's the URL/permissions — **not** a matter of waiting.
* **Refresh cadence:** subscribed calendars are re-fetched by the *provider*, not by Ekin. **Google refreshes external URLs slowly — every several hours, up to ~24 h — and this can't be forced.** **Apple Calendar** lets you pick the refresh interval (as fast as every few minutes) against the *same* URL if you want quicker updates.
* **Sanity check without waiting a day:** add a dated task in Ekin, confirm the local `.ics` updated, and confirm the direct URL (in incognito) shows the new event. If both do, the Ekin → cloud half works instantly; only the provider's refresh is slow.
