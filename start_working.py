"""
START WORKING (#87): desde un tablero con directorio local, arranca el servidor MCP de Ekin,
actualiza la CLI del agente de IA, registra en ella el MCP del tablero y la abre en una consola
externa, en el repo, con el prompt de inicio (INTRO) del pack del tablero.
"""
import os

from PySide6.QtCore import QEventLoop, Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox, QProgressDialog

import cli_tools
import database
import prompt_packs
from mcp_server import get_mcp_manager
from prompt_clipboard_dialog import ask_variable_values
from strings import t


def start_prompt(board):
    """Prompt de inicio del pack del tablero ('intro', si no '*_intro', si no el primero), con
    las variables del tablero ya rellenas."""
    prompts = prompt_packs.load_pack(prompt_packs.resolve_pack_id(board.get("prompt_pack")))
    chosen = (next((p for p in prompts if p["id"] == "intro"), None)
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
        ok, msg = cli_tools.update_cli(tool, exe_path)
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
