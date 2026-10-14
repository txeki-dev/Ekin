"""
Archivos del directorio local (repo) asociado a un tablero, para ofrecerlos en la mención «@».
Si el directorio es un repo git se respeta su .gitignore; si no, se recorre saltando las
carpetas habituales de dependencias y artefactos.
"""
import os
import subprocess

_SKIP_DIRS = {".git", "venv", ".venv", "node_modules", "__pycache__", "dist", "build", ".pytest_cache"}


def list_repo_files(root, limit=5000):
    """Rutas relativas (con «/») de los archivos de `root`, como mucho `limit`."""
    try:
        result = subprocess.run(
            ["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True, text=True, encoding="utf-8", timeout=3,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode == 0:
            return [line for line in result.stdout.splitlines() if line][:limit]
    except (OSError, subprocess.SubprocessError):
        pass

    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS)
        rel_dir = os.path.relpath(dirpath, root)
        for name in sorted(filenames):
            files.append(name if rel_dir == "." else f"{rel_dir}/{name}".replace("\\", "/"))
            if len(files) >= limit:
                return files
    return files
