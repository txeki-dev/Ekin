"""
Status line de Claude Code instalada por Ekin (#88). Claude Code le pasa por stdin el JSON de la
sesión, que incluye `rate_limits` (uso de la ventana de 5 h y de 7 días, solo Pro/Max). Este
script guarda esa parte en ~/.ekin/cli_quota/claude.json para el semáforo de Ekin y después
imprime la status line: la que el usuario tenía antes (si la había) o una línea mínima.
Solo biblioteca estándar: se ejecuta en cada refresco de la status line.
"""
import json
import os
import subprocess
import sys
import time

QUOTA_DIR = os.path.join(os.path.expanduser("~"), ".ekin", "cli_quota")
PREVIOUS_FILE = os.path.join(QUOTA_DIR, "claude_prev_statusline.json")


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        data = {}
    limits = data.get("rate_limits")
    if limits:
        os.makedirs(QUOTA_DIR, exist_ok=True)
        tmp = os.path.join(QUOTA_DIR, "claude.json.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"rate_limits": limits, "captured_at": time.time()}, fh)
        os.replace(tmp, os.path.join(QUOTA_DIR, "claude.json"))

    try:
        with open(PREVIOUS_FILE, encoding="utf-8") as fh:
            previous = json.load(fh).get("command")
    except (OSError, ValueError):
        previous = None
    if previous:
        res = subprocess.run(previous, input=raw, shell=True, capture_output=True, text=True, timeout=10)
        sys.stdout.write(res.stdout)
        return

    parts = [(data.get("model") or {}).get("display_name", "")]
    for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
        window = (limits or {}).get(key) or {}
        if window.get("used_percentage") is not None:
            parts.append(f"{label} {100 - window['used_percentage']:.0f}% left")
    print(" · ".join(p for p in parts if p))


if __name__ == "__main__":
    main()
