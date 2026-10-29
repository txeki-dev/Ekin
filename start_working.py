"""
START WORKING (#87): desde un tablero con directorio local, arranca el servidor MCP de Ekin,
actualiza la CLI del agente de IA, registra en ella el MCP del tablero y la abre en una consola
externa, en el repo, con el prompt de inicio (INTRO) del pack del tablero; INITIAL si la carpeta
aún no tiene código.
"""
import os

from PySide6.QtCore import QEventLoop, Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QProgressDialog

import cli_quota
import cli_tools
import database
import prompt_packs
from detail_dialog.repo_files import list_repo_files
from mcp_server import get_mcp_manager
from prompt_clipboard_dialog import ask_variable_values
from quota_popup import quota_lines
from strings import t


# Archivos que cuentan como código: si la carpeta no tiene ninguno, el proyecto está por empezar
_CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".mjs", ".ts", ".tsx", ".java", ".kt", ".go", ".rs", ".c", ".h", ".cpp",
    ".hpp", ".cs", ".rb", ".php", ".swift", ".dart", ".lua", ".r", ".scala", ".sh", ".ps1", ".bat",
    ".sql", ".html", ".css", ".scss", ".vue", ".svelte",
}


def has_code(folder):
    """True si `folder` tiene algún archivo de código (sin contar dependencias ni lo ignorado)."""
    return any(os.path.splitext(f)[1].lower() in _CODE_EXTENSIONS for f in list_repo_files(folder, limit=2000))


def start_prompt(board):
    """Prompt de inicio del pack del tablero ('intro', si no '*_intro', si no el primero), con
    las variables del tablero ya rellenas. Si el pack tiene INITIAL y el directorio local aún no
    tiene código, arranca con INITIAL, que prepara el proyecto (#152)."""
    prompts = prompt_packs.load_pack(prompt_packs.resolve_pack_id(board.get("prompt_pack")))
    local_dir = board.get("local_dir")
    initial = next((p for p in prompts if p["id"] == "initial"), None)
    new_project = bool(initial and local_dir and os.path.isdir(local_dir) and not has_code(local_dir))
    chosen = ((initial if new_project else None)
              or next((p for p in prompts if p["id"] == "intro"), None)
              or next((p for p in prompts if p["id"].endswith("_intro")), prompts[0]))
    return prompt_packs.fill_variables(chosen["prompt"], prompt_packs.board_variables(board))


class StartWorkingWorker(QThread):
    """Los pasos lentos (update de la CLI y registro del MCP) fuera del hilo de la interfaz."""
    step = Signal(str)
    done = Signal(list)  # avisos no bloqueantes

    def __init__(self, tool, exe_path, board, sse_url, rpc_url, cwd, parent=None):
        super().__init__(parent)
        self.args = (tool, exe_path, board, sse_url, rpc_url, cwd)

    def run(self):
        tool, exe_path, board, sse_url, rpc_url, cwd = self.args
        warnings = []
        self.step.emit(t("start_working.step_update", tool=tool.name))
        ok, msg = cli_tools.update_cli(tool, exe_path, on_retry=lambda attempt: self.step.emit(
            t("start_working.step_update_retry", tool=tool.name, attempt=attempt, total=cli_tools.UPDATE_ATTEMPTS)))
        if not ok:
            warnings.append(t("start_working.warn_update", tool=tool.name, msg=msg))
        self.step.emit(t("start_working.step_mcp", tool=tool.name))
        ok, msg = cli_tools.ensure_mcp_registered(tool, exe_path, board, sse_url, rpc_url, cwd)
        if not ok:
            warnings.append(t("start_working.warn_mcp", tool=tool.name, msg=msg))
        self.done.emit(warnings)


def _pick_cli(parent):
    installed = cli_tools.detect_installed()
    if not installed:
        names = ", ".join(tool.name for tool in cli_tools.KNOWN_CLIS)
        QMessageBox.warning(parent, t("start_working.title"), t("start_working.no_cli", clis=names))
        return None
    if len(installed) == 1:
        return installed[0]
    names = [tool.name for tool, _ in installed]
    name, ok = QInputDialog.getItem(parent, t("start_working.title"), t("start_working.pick_cli"), names, 0, False)
    return installed[names.index(name)] if ok else None


def start_working(parent, board_id, db_path=None, open_mcp_dialog=None):
    """Ejecuta START WORKING para el tablero. Devuelve el id de la CLI abierta, o None si se
    canceló o no se pudo (avisando al usuario). Sin MCP activado abre `open_mcp_dialog()`."""
    board = database.get_board(board_id, db_path)
    cwd = board.get("local_dir")
    if not cwd or not os.path.isdir(cwd):
        QMessageBox.warning(parent, t("start_working.title"), t("start_working.no_dir"))
        return None
    if not board.get("mcp_enabled"):
        QMessageBox.information(parent, t("start_working.title"), t("start_working.mcp_disabled"))
        if open_mcp_dialog:
            open_mcp_dialog()
        return None
    picked = _pick_cli(parent)
    if not picked:
        return None
    tool, exe_path = picked
    if tool.id == "claude":
        snapshot = cli_quota.read_quota()
        if cli_quota.quota_state(snapshot) == cli_quota.RED:
            answer = QMessageBox.question(
                parent, t("start_working.title"),
                t("start_working.quota_red", lines="\n".join(quota_lines(snapshot))),
            )
            if answer != QMessageBox.Yes:
                return None

    prompt = start_prompt(board)
    missing = prompt_packs.find_variables(prompt)
    if missing:
        values = ask_variable_values(parent, missing)
        if values is None:
            return None
        prompt = prompt_packs.fill_variables(prompt, values)

    manager = get_mcp_manager(db_path)
    if not manager.start():
        QMessageBox.warning(parent, t("start_working.title"), t("start_working.mcp_failed", port=manager.port))
        return None
    sse_url = manager.get_board_sse_url(board["board_uuid"], board.get("mcp_secret"))
    rpc_url = sse_url.replace("/sse?", "/rpc?", 1)

    progress = QProgressDialog(t("start_working.step_update", tool=tool.name), None, 0, 0, parent)
    progress.setWindowTitle(t("start_working.title"))
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(0)
    progress.show()
    worker = StartWorkingWorker(tool, exe_path, board, sse_url, rpc_url, cwd)
    worker.step.connect(progress.setLabelText)
    warnings = []
    loop = QEventLoop()
    worker.done.connect(lambda found: (warnings.extend(found), loop.quit()))
    worker.start()
    loop.exec()
    worker.wait()
    progress.close()

    argv, via_clipboard = cli_tools.build_launch(tool, exe_path, prompt)
    if via_clipboard:
        QApplication.clipboard().setText(prompt)
        warnings.append(t("start_working.prompt_in_clipboard", tool=tool.name))
    cli_tools.launch(argv, cwd)
    if warnings:
        QMessageBox.information(parent, t("start_working.title"), "\n\n".join(warnings))
    return tool.id
