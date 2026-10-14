"""
CLIs de agentes de IA que Ekin sabe lanzar desde un tablero (START WORKING): detección, update,
registro del servidor MCP del tablero y línea de comandos de arranque con el prompt de inicio.
Sin Qt: lo usa start_working.py desde un hilo de trabajo.
"""
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable, List, Optional

from mcp_server import claude_code_server_name

_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


@dataclass(frozen=True)
class CliTool:
    id: str
    name: str
    exe: str
    update_args: Optional[List[str]]           # None = la CLI no se actualiza sola
    prompt_args: Callable[[str], List[str]]    # argumentos para arrancar con un prompt inicial


KNOWN_CLIS = (
    CliTool("claude", "Claude Code", "claude", ["update"], lambda p: [p]),
    CliTool("agy", "Antigravity CLI", "agy", ["update"], lambda p: ["-i", p]),
    CliTool("gemini", "Gemini CLI", "gemini", None, lambda p: ["-i", p]),
)


def detect_installed():
    """[(CliTool, ruta del ejecutable)] de las CLIs conocidas que están en el PATH."""
    found = []
    for tool in KNOWN_CLIS:
        path = shutil.which(tool.exe)
        if path:
            found.append((tool, path))
    return found


def build_launch(tool, exe_path, prompt):
    """(argv, prompt_por_portapapeles). Un shim .cmd/.bat (instalación npm) pasa por cmd.exe, que
    no admite un argumento multilínea con < > ; " de forma segura: en ese caso se arranca sin
    prompt y el prompt va al portapapeles."""
    if os.path.splitext(exe_path)[1].lower() in (".cmd", ".bat"):
        return [exe_path], True
    return [exe_path, *tool.prompt_args(prompt)], False


def _run(argv, cwd=None, timeout=60):
    return subprocess.run(
        argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, creationflags=_NO_WINDOW,
    )


def update_cli(tool, exe_path):
    """Actualiza la CLI. Devuelve (ok, mensaje). Nunca lanza: un fallo no debe bloquear el inicio."""
    if tool.update_args is None:
        return True, ""
    try:
        res = _run([exe_path, *tool.update_args], timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    return res.returncode == 0, (res.stdout or res.stderr).strip()[-300:]


def ensure_mcp_registered(tool, exe_path, board, sse_url, rpc_url, cwd):
    """Registra el servidor MCP del tablero en la CLI si aún no lo está.
    Devuelve (ok, mensaje). Claude Code lo guarda en el ámbito local del directorio `cwd`."""
    name = claude_code_server_name(board["name"])
    try:
        if tool.id == "claude":
            if _run([exe_path, "mcp", "get", name], cwd=cwd).returncode == 0:
                return True, ""
            res = _run([exe_path, "mcp", "add", "--transport", "sse", name, sse_url], cwd=cwd)
        elif tool.id == "agy":
            if name in _run([exe_path, "mcp", "list"], cwd=cwd).stdout:
                return True, ""
            # agy no habla SSE: se registra el endpoint JSON-RPC por HTTP del servidor de Ekin
            res = _run([exe_path, "mcp", "add", name, rpc_url], cwd=cwd)
        else:
            return False, f"{tool.name}: registro MCP manual"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    return res.returncode == 0, (res.stdout or res.stderr).strip()[-300:]


def launch(argv, cwd):
    """Abre la CLI en una consola nueva (Windows Terminal si es la consola por defecto)."""
    return subprocess.Popen(argv, cwd=cwd, creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
