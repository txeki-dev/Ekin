# Ekin Kanban

[![CI](https://github.com/txeki-dev/Ekin/actions/workflows/ci.yml/badge.svg)](https://github.com/txeki-dev/Ekin/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/txeki-dev/Ekin?label=release&sort=semver)](https://github.com/txeki-dev/Ekin/releases/latest)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-PolyForm--Noncommercial-lightgrey)](LICENSE)

Ekin Kanban is a sleek, resource-friendly, and offline-first personal Kanban board application. Designed for individual developers, project managers, and writers, it replicates the core Kanban workflow (similar to Trello or Linear) and pairs each task card with a personal activity journal (diary). This allows you to track not just where a task is, but also write daily logs, updates, and thoughts directly on each card.

---

## ✨ Key Features
- **Offline-First & Serverless**: Runs entirely on your local machine using SQLite. Your data never leaves your computer.
- **Ultra-lightweight**: Operates with a minimal memory footprint (< 60MB RAM idle) compared to heavy Electron-based alternatives.
- **Fluid Drag & Drop**: Native, smooth mouse controls to drag tasks across columns or reorder them.
- **Task Journaling (Diario)**: A vertical, scrollable, timestamped diary inside each task card, perfect for keeping track of developer progress logs.
- **Rich Notes**: The description and diary support **bold** (Ctrl+B), *italic* (Ctrl+K), ~~strikethrough~~ (Ctrl+Shift+X), nested bullet lists (Tab to indent) and **arrows** (type `-->` or use the toolbar button). External text pastes as **plain text**, and you can **paste images** — click one to open it larger — and **tables** (from Excel/Sheets/Word, or tab-separated text) straight in — or insert an empty one from the toolbar.
- **Collapsible Columns**: Fold a column you're not working on down to a slim strip (just its name and task count) with the **◀** button to save horizontal space.
- **Global Search & Filter**: A 🔍 button (or **Ctrl+F**) searches every board by title/description and filters by board, tag, or due date; click a result to jump straight to its card.
- **Due Dates, Times & Recurring Tasks**: Assign a due date (and optional **time**), plus a **recurrence** (daily/weekly/monthly) — overdue recurring tasks roll forward automatically. Cards show **🔁** for recurring and multiple custom-colored tag pills.
- **Priority**: A quick **🚩 Prioridad** selector in the task detail (Baja/Media/Alta by default, customizable) shows up as a pill on the board card, same as any other tag.
- **Task Timer**: Click **▶ Iniciar** in the task detail to record when you started it; a live "time elapsed" counter shows next to it, and the same **⏱** badge appears right on the board card — turning red once it crosses a configurable threshold in Ajustes, so stale tasks stand out without opening each one.
- **Board Links**: Point a task at a *different* board — e.g. a summary task in "Tareas" that links to the dedicated "SW X" board where its detailed work lives. Pick the target from **🔗 Tablero vinculado** in the task detail; the card then shows a clickable **🔗 <board>** pill that jumps straight there.
- **Calendar View & Reminders**: **Month / Week / Day** views with a **board filter** and color legend; **drag a chip to reschedule**; a deadline **bell** that groups **overdue**, today's and tomorrow's tasks; and native **Windows notifications**.
- **Calendar Sync (iCalendar)**: An always-updated `.ics` feed (with **timed events + `VALARM` reminders** and **per-board feeds**) you can **subscribe** to from Google/Apple/Outlook. A **"Subscribe"** helper copies the URL and opens the provider page.
- **Attachments / Links**: Attach a web URL, or click **📁** to browse your PC and attach a local file. Local attachments show a **📎** icon (web links keep **🔗**) and turn red with a warning if the file's since moved or been deleted; open or remove either kind from the task detail.
- **Undo / Redo**: **Ctrl+Z / Ctrl+Y** restores a deleted task, column or board — with all its tags, diary and links.
- **Keyboard Shortcuts**: Quick actions for new tasks/columns, jumping between boards, opening Settings/Calendar, and more — press **Ctrl+/** anytime to open a reference dialog listing every shortcut in the app.
- **Board Archiving & Export**: Archive boards to declutter the sidebar; export everything to **JSON / CSV / Markdown**.
- **Themes & Settings**: A ⚙ settings screen with a **dark/light theme** toggle, notification prefs, a configurable task-timer alert threshold, and a remembered window size.
- **Automatic Backups**: On every startup Ekin snapshots your database into a `backups/` folder (keeping the most recent few) before applying any changes — a cheap safety net against accidents.
- **Collapsible Sidebar**: Hide or reveal the sidebar using the toggle (`☰`) button in the board header to maximize work space.
- **Column & Board Copying/Moving**: Easily move or copy columns to other boards, or copy complete boards with all sub-tasks, tags, and diaries.
- **Modern Slate Design**: Out-of-the-box support for a premium dark mode UI, customizable colors for columns, boards, and tags.

---

## 🛠️ Setup & Installation

Ekin Kanban can be installed automatically on Windows in one step, or manually on any platform.

### Prerequisites
Before installing, ensure you have **Python 3.10+** and **Git** installed on your system and added to your system PATH.
* [Download Python](https://www.python.org/downloads/)
* [Download Git](https://git-scm.com/downloads)

---

### 🚀 Easy Installation (Windows - One Click)

Open **PowerShell** and run the following command to download and execute the automatic installer:

```powershell
irm https://raw.githubusercontent.com/txeki-dev/Ekin/main/install.ps1 | iex
```

**What the installer does:**
1. Clones this repository into `~/EkinKanban` (your home directory).
2. Sets up a local Python virtual environment (`venv`).
3. Installs `PySide6` (the GUI library).
4. Generates a silent launcher script (`lanzar.bat`).
5. **Creates a shortcut on your Desktop** labeled **Ekin Kanban** to launch the app instantly without showing background terminal windows.

---

### 💻 Manual Installation (All Platforms)

If you prefer to install it manually or are using macOS/Linux:

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

The tests exercise `database.py`, the iCalendar exporter (`ics_export.py`), automatic backups (`backups.py`), and the task drop-index logic against temporary, isolated SQLite databases (no risk to your local `ekin_board.db`).

---

## 🔄 Automatic Updates

When you open Ekin Kanban, the application automatically performs a quick, silent check against this GitHub repository in the background. 

If there is a newer version available on the `main` branch, a prompt will ask: 
> *“Hay una nueva versión de Ekin Kanban en GitHub. ¿Deseas descargarla y reiniciar la aplicación ahora?”*

Clicking **Yes** will pull the updates automatically and restart the app on the spot.

---

## 🚀 Running Ekin Kanban

* **Windows**: Double-click the **Ekin Kanban** shortcut on your Desktop, or run `lanzar.bat` in the application folder.
* **Manual/Other Platforms**: Run `python main.py` inside your active virtual environment.

The database (`ekin_board.db`) is automatically initialized on the first run, and a demo board with onboarding columns and cards is generated for you.

---

## 📖 How to Use Ekin Kanban

### 1. Managing Boards (Sidebar)
* Use the **Sidebar (left panel)** to switch between different projects or workspaces.
* Click **➕ Nuevo Tablero** to create a board. You can name it and choose a unique background accent color.
* Select a board and click **✏️ Editar** to rename or recolor it, or click **🗑️ Borrar** to remove it.
* You can clone an entire board (including its columns, tasks, tags, and diaries) by clicking **✏️ Editar** and selecting the Copy/Clone options.
* Use **Alt+Up / Alt+Down** anywhere to jump to the previous/next board without touching the sidebar.

### 2. Organizing Columns & Tasks
* Inside a board, click **➕ Nueva Columna** to create stage headers (e.g., "To-Do", "In Progress", "Done").
* **Reorder or move columns**: click and drag a column by its **title** to reorder it within the board, or drop it onto another board's button in the sidebar to move it there.
* **Column Actions**: Click the **pencil (✎)** button in a column header to edit its name/color, delete it, or **copy** (clone) it and its tasks to another board.
* **Collapse a column**: Click **◀** in the header to fold a column into a slim strip (name + task count); click **▶** on the strip to expand it again. The state is remembered per column, and **dropping a card onto a collapsed column expands it** and drops the card in. If you instead **hover a dragged card over the collapsed strip for about a second**, it unfolds automatically *while you're still dragging*, so you can pick exactly where in the column the card lands instead of it always going to the bottom — drag it away without dropping there and the column quietly folds back up.
* Click **➕ Añadir Tarea** at the bottom of any column to quickly add a card.
* **Drag & Drop**: Click and hold a task card to drag it to another column or change its vertical position.

### 3. Detail View, Structured Tags & Due Dates
* Click on a task card to open the **Detail View**.
* On the **left panel**:
  - Change the task title and description. The toolbar (and shortcuts) give **bold** (Ctrl+B), *italic* (Ctrl+K), ~~strikethrough~~ (Ctrl+Shift+X), bullet lists — press **Tab** on a bullet to nest it — and **arrows** (type `-->` or use the toolbar's **→** button). Text pasted from elsewhere comes in as **plain text**, and you can **paste images** directly into the notes. Pasting a **table** (from Excel/Sheets/Word, or plain tab-separated text) inserts a real table, and the **▦** toolbar button creates an empty one (asks for rows/columns) — press **Tab** in the last cell to add a row.
  - **⏱ Temporizador**: click **▶ Iniciar** to record the start time; while running, **↺ Reiniciar** resets it to now and **✕ Detener** clears it. Both take effect immediately (no need to click "Guardar Cambios"). The elapsed time also shows as a badge on the board card, in red once it's been running longer than the threshold set in Ajustes.
  - Set a **due date** using the calendar popup widget.
  - Click **➕ Asignar Etiqueta** to add a tag as a **Category: Value** pair (e.g. "Prioridad: Alta"), with its own color. Reusing an existing value keeps its color consistent everywhere it's used; typing a new one creates it on the fly. Next to Etiquetas, the **🚩 Prioridad** dropdown is a one-click shortcut for the same "Prioridad" tag — pick Baja/Media/Alta (or "— Sin prioridad —") without going through the full tag picker. Next to that, **🔗 Tablero vinculado** links the task to a *different* board (any board except the one the task is already on); once set, the card shows a clickable pill that jumps straight to that board.
  - **🔗 Enlaces / adjuntos**: paste a URL/path directly, or click **📁** to browse your PC and attach a local file — the label auto-fills with the file name if you leave it blank. Web links show **🔗**, local files show **📎**; an attachment whose file has since been moved or deleted turns red with a tooltip explaining why, but stays there so you can remove it. Both are saved instantly (no need to click "Guardar Cambios") and can be opened or removed (🗑) at any time.
* On the **right panel (Diario)**, type notes or updates about what you did (same formatting, table paste/insert, plain-text paste and image paste), and press `Ctrl + Enter` (or click **✍️ Añadir al Diario**) to post it. Each note is saved with an automatic date and time stamp.
* Each note has an **edit (✎)** and a **delete (×)** button — editing opens an inline editor (save or cancel); deleting removes the note.
* Click **💾 Guardar Cambios** to apply your updates, or click **🗑️ Eliminar** to delete the entire task.
* Collapse the sidebar with the **◀ / ▶** button in the top-left header bar to maximize workspace size.

### 4. Calendar, Reminders & Notifications
At the top of the sidebar there is a small utility bar:
* 🕐 A live **date & time** clock.
* 🔔 A **deadline bell** with a count badge: click it to see the tasks (from **all** boards) grouped into **ATRASADAS** (overdue), **HOY** (today) and **MAÑANA** (tomorrow). Click any of them to jump straight to its board and open the card.
* 🔍 A **search button** (or **Ctrl+F** anywhere) that opens global search: filter tasks across every board by text (title/description), board, tag, and "only with a due date", then click a result to jump to its card.
* 📅 A **calendar button** that switches the main area to a **monthly calendar view**. Navigate months with `‹ › / Hoy`, click a task chip to open its card, **drag a chip onto another day to change its due date**, and use **✖ Cerrar** to return to the board or **⚙ Ajustes** to configure calendar sync (see below).
* ❔ A **shortcuts button** that opens the "Atajos de teclado" reference dialog (same as pressing **Ctrl+/**).

When the app starts (and once per day thereafter), Ekin also shows a **native Windows notification** listing the cards that are due today. Ekin lives in the system tray while running — double-click the tray icon to bring the window back.

Every time Ekin starts it also writes an automatic **backup** of your database into a `backups/` folder next to `ekin_board.db` (the five most recent are kept), so an accidental delete is never fatal.

### 5. Keyboard Shortcuts
Press **Ctrl+/** anywhere, or click the **❔** button in the sidebar utility bar, to open a reference dialog listing every shortcut in the app, grouped by category — the list below is a summary:
* **Ctrl+N** — new task in the last column you interacted with (opened a card in, clicked "+ Añadir Tarea" in, or just clicked); falls back to the first column if nothing qualifies yet. **Ctrl+Shift+N** — new column in the active board.
* **Ctrl+1** … **Ctrl+9** — jump straight to the 1st through 9th board in the sidebar. **Alt+↑ / Alt+↓** — previous/next board.
* **Ctrl+F** — global search. **Ctrl+,** — open Ajustes. **Ctrl+Shift+C** — open the Calendar.
* **Ctrl+Z / Ctrl+Y** (or **Ctrl+Shift+Z**) — undo/redo. **Esc** — close the open dialog.
* Inside the description/diary editor: **bold** (Ctrl+B or Ctrl+N), *italic* (Ctrl+K or Ctrl+I), ~~strikethrough~~ (Ctrl+Shift+X), **Tab** to nest a bullet, typing `-->` for **→**, and **Ctrl+Enter** to post a diary note.

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
