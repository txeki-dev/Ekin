# Ekin Kanban (Trello Lite)

Ekin Kanban is a sleek, resource-friendly, and offline-first personal Kanban board application. Designed for individual developers, project managers, and writers, it replicates the core Kanban workflow (similar to Trello or Linear) and pairs each task card with a personal activity journal (diary). This allows you to track not just where a task is, but also write daily logs, updates, and thoughts directly on each card.

---

## ✨ Key Features
- **Offline-First & Serverless**: Runs entirely on your local machine using SQLite. Your data never leaves your computer.
- **Ultra-lightweight**: Operates with a minimal memory footprint (< 60MB RAM idle) compared to heavy electron-based alternatives.
- **Fluid Drag & Drop**: Native, smooth mouse controls to drag tasks across columns or reorder them.
- **Task Journaling (Diario)**: A vertical, scrollable timestamped diary inside each task card, perfect for keeping track of daily progress logs.
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
   pip install PySide6
   ```

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
* Select a board and click **✏️ Editar** to rename or recolor it, or click **🗑️ Borrar** to remove it along with all columns and tasks inside.

### 2. Organizing Columns & Tasks
* Inside a board, click **➕ Nueva Columna** to create stage headers (e.g., "To-Do", "In Progress", "Done"). You can edit columns at any time by clicking the three dots (**⋮**) in their header.
* Click **➕ Añadir Tarea** at the bottom of any column to quickly add a card.
* **Drag & Drop**: Click and hold a task card to drag it to another column or change its vertical position.

### 3. Writing in the Developer Diary (Diario)
* Click on a task card to open the **Detail View**.
* On the **left panel**, you can change the title, description (supporting Rich Text / HTML), and add a tag pill (like "High Priority" or "Research") with custom colors.
* On the **right panel (Diario)**, type notes or updates about what you did, and press `Ctrl + Enter` (or click **✍️ Añadir al Diario**) to post it. Each note is saved with an automatic date and time stamp.
* Click the red cross (**×**) on any note if you need to remove it.
* Click **💾 Guardar Cambios** to apply your updates, or click **🗑️ Eliminar** to delete the entire task.
