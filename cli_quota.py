"""
Cuota restante de las CLIs de IA (#88). Claude Code la expone de forma documentada en el JSON
de su status line (`rate_limits.five_hour` / `seven_day`: `used_percentage` y `resets_at`, solo
Pro/Max y tras la primera respuesta de la sesión). Ekin instala, solo cuando el usuario lo pide,
una status line (assets/claude_statusline.py) que guarda ese dato en ~/.ekin/cli_quota/; las
demás CLIs no exponen su cuota.
"""
import json
import os
import shutil
import sys
import time

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_SOURCE = os.path.join(_APP_DIR, "assets", "claude_statusline.py")
QUOTA_DIR = os.path.join(os.path.expanduser("~"), ".ekin", "cli_quota")
SCRIPT_TARGET = os.path.join(os.path.expanduser("~"), ".ekin", "bin", "claude_statusline.py")
PREVIOUS_FILE = os.path.join(QUOTA_DIR, "claude_prev_statusline.json")
CLAUDE_SETTINGS = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")

WINDOWS = (("five_hour", "session"), ("seven_day", "weekly"))
GREEN, AMBER, RED, GREY = "green", "amber", "red", "grey"


def read_quota(now=None):
    """{"five_hour": {...}, "seven_day": {...}, "captured_at": ts} con las ventanas aún vigentes
    (una ventana cuyo `resets_at` ya pasó no dice nada del uso actual), o None sin datos."""
    try:
        with open(os.path.join(QUOTA_DIR, "claude.json"), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    now = time.time() if now is None else now
    limits = data.get("rate_limits") or {}
    snapshot = {
        key: limits[key] for key, _ in WINDOWS
        if isinstance(limits.get(key), dict) and limits[key].get("used_percentage") is not None
        and (limits[key].get("resets_at") or 0) > now
    }
    if not snapshot:
        return None
    snapshot["captured_at"] = data.get("captured_at")
    return snapshot


def quota_state(snapshot):
    """Color del semáforo según la ventana más gastada: verde < 70 %, ámbar < 90 %, rojo."""
    used = [snapshot[key]["used_percentage"] for key, _ in WINDOWS if snapshot and key in snapshot]
    if not used:
        return GREY
    worst = max(used)
    return GREEN if worst < 70 else AMBER if worst < 90 else RED


def _python_for_scripts():
    """Intérprete con consola para la status line (pythonw no tiene stdout)."""
    if not getattr(sys, "frozen", False):
        candidate = os.path.join(os.path.dirname(sys.executable), "python.exe" if os.name == "nt" else "python")
        if os.path.isfile(candidate):
            return candidate
    return shutil.which("python") or shutil.which("python3")


def _command():
    python = _python_for_scripts()
    return f'"{python}" "{SCRIPT_TARGET}"'.replace("\\", "/") if python else None


def _load_settings():
    try:
        with open(CLAUDE_SETTINGS, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def _save_settings(settings):
    os.makedirs(os.path.dirname(CLAUDE_SETTINGS), exist_ok=True)
    tmp = CLAUDE_SETTINGS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, CLAUDE_SETTINGS)


def is_installed():
    command = _command()
    return bool(command) and (_load_settings().get("statusLine") or {}).get("command") == command


def install_claude_statusline():
    """Pone la status line de Ekin en ~/.claude/settings.json (con copia de seguridad, sin tocar
    el resto de claves). La status line previa se guarda y la de Ekin la sigue mostrando."""
    command = _command()
    if not command:
        raise RuntimeError("No Python interpreter found to run the status line script")
    os.makedirs(os.path.dirname(SCRIPT_TARGET), exist_ok=True)
    shutil.copyfile(SCRIPT_SOURCE, SCRIPT_TARGET)
    settings = _load_settings()
    if os.path.isfile(CLAUDE_SETTINGS):
        shutil.copyfile(CLAUDE_SETTINGS, CLAUDE_SETTINGS + ".ekin-backup")
    previous = settings.get("statusLine")
    if previous and previous.get("command") != command:
        os.makedirs(QUOTA_DIR, exist_ok=True)
        with open(PREVIOUS_FILE, "w", encoding="utf-8") as fh:
            json.dump(previous, fh)
    settings["statusLine"] = {"type": "command", "command": command}
    _save_settings(settings)


def uninstall_claude_statusline():
    """Quita la status line de Ekin y restaura la que hubiera antes."""
    settings = _load_settings()
    try:
        with open(PREVIOUS_FILE, encoding="utf-8") as fh:
            settings["statusLine"] = json.load(fh)
        os.remove(PREVIOUS_FILE)
    except (OSError, ValueError):
        settings.pop("statusLine", None)
    _save_settings(settings)
