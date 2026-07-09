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

### Prerequisites
Make sure you have **Python 3.10** or higher installed on your system. You can check your version by running:
```bash
python --version
```

### Installation Steps

1. **Download or Clone** the project files to a folder on your computer.
2. **Open a terminal/command prompt** and navigate to the project directory:
   ```powershell
   cd "C:\Users\sergi\Documents\Txek Systems\Ekin"
   ```
3. **Create a Python Virtual Environment**:
   ```bash
   python -m venv venv
   ```
4. **Activate the Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt - CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
5. **Install PySide6 (Qt for Python)**:
   ```bash
   pip install PySide6
   ```

---

## 🚀 Running Ekin Kanban

Once you have installed the dependency, you can launch the application by running:
```bash
python main.py
```

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
