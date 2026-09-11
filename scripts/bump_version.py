#!/usr/bin/env python3
"""Script para automatizar el incremento de versión (version bump) en Ekin Kanban.

Uso:
    python scripts/bump_version.py patch          # 1.0.0 -> 1.0.1
    python scripts/bump_version.py minor          # 1.0.0 -> 1.1.0
    python scripts/bump_version.py major          # 1.0.0 -> 2.0.0
    python scripts/bump_version.py 1.0.2          # Fija 1.0.2 explícitamente

Opciones adicionales:
    --commit, -c: Ejecuta `git add` y `git commit -m "chore(release): bump version to vX.Y.Z"`
    --push, -p:   Ejecuta commit y push a origin main (dispara el workflow de Release en GitHub)
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent


def get_current_version() -> str:
    version_file = ROOT_DIR / "version.py"
    content = version_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("No se pudo encontrar __version__ en version.py")
    return match.group(1).strip()


def calculate_next_version(current: str, bump_type: str) -> str:
    bump = bump_type.lower().strip()
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", current)
    if not match:
        raise ValueError(f"Formato de versión semver no reconocido en version.py: {current}")
    major, minor, patch = map(int, match.groups())

    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    elif bump == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump == "major":
        return f"{major + 1}.0.0"
    elif re.match(r"^\d+\.\d+\.\d+", bump):
        return bump
    else:
        raise ValueError(f"Tipo de incremento desconocido: '{bump_type}'. Usa patch, minor, major o 'X.Y.Z'.")


def update_version_py(new_version: str):
    version_file = ROOT_DIR / "version.py"
    version_file.write_text(f'__version__ = "{new_version}"\n', encoding="utf-8")
    print(f"[OK] version.py actualizado a: {new_version}")


def update_installer_iss(new_version: str):
    iss_file = ROOT_DIR / "installer.iss"
    if not iss_file.exists():
        return
    content = iss_file.read_text(encoding="utf-8")
    updated = re.sub(
        r'#define MyAppVersion\s+["\'][^"\']+["\']',
        f'#define MyAppVersion "{new_version}"',
        content,
    )
    iss_file.write_text(updated, encoding="utf-8")
    print(f"[OK] installer.iss actualizado con versión: {new_version}")


def update_changelog(new_version: str):
    changelog_file = ROOT_DIR / "CHANGELOG.md"
    if not changelog_file.exists():
        return
    content = changelog_file.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()

    # Si ya contiene [Unreleased], transformar o preparar la cabecera
    unreleased_pattern = re.compile(r"##\s+\[Unreleased\]\s*\n", re.IGNORECASE)
    match = unreleased_pattern.search(content)

    if match:
        idx = match.end()
        remainder = content[idx:]
        next_heading_match = re.search(r"##\s+\[", remainder)
        unreleased_body = remainder[:next_heading_match.start()].strip() if next_heading_match else ""

        if unreleased_body:
            # Hay cambios bajo Unreleased: crear nueva sección con esos cambios
            replacement = (
                f"## [Unreleased]\n\n"
                f"## [{new_version}] - {today}\n\n"
                f"{unreleased_body}\n\n"
            )
            new_content = content[:match.start()] + replacement + remainder[next_heading_match.start():]
        else:
            # Unreleased estaba vacío: añadir sección para la versión
            replacement = (
                f"## [Unreleased]\n\n"
                f"## [{new_version}] - {today}\n\n"
                f"### Changed\n- Release version v{new_version}.\n\n"
            )
            new_content = content[:match.start()] + replacement + (remainder[next_heading_match.start():] if next_heading_match else remainder)
        changelog_file.write_text(new_content, encoding="utf-8")
        print(f"[OK] CHANGELOG.md actualizado con sección: [{new_version}] - {today}")


def main():
    parser = argparse.ArgumentParser(description="Automatizar el incremento de versión en Ekin Kanban.")
    parser.add_argument(
        "bump",
        nargs="?",
        default="patch",
        help="Tipo de incremento ('patch', 'minor', 'major' o versión explícita 'X.Y.Z'). Por defecto: patch",
    )
    parser.add_argument("-c", "--commit", action="store_true", help="Crear commit git automáticamente.")
    parser.add_argument("-p", "--push", action="store_true", help="Crear commit y hacer push a origin main.")

    args = parser.parse_args()

    current_ver = get_current_version()
    new_ver = calculate_next_version(current_ver, args.bump)

    print(f"\n[Ekin] Version Bump: v{current_ver} -> v{new_ver}")
    print("-" * 45)

    update_version_py(new_ver)
    update_installer_iss(new_ver)
    update_changelog(new_ver)

    if args.commit or args.push:
        subprocess.run(["git", "add", "-A"], cwd=ROOT_DIR, check=True)
        commit_msg = f"chore(release): bump version to v{new_ver}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT_DIR, check=True)
        print(f"[OK] Git commit creado: '{commit_msg}'")

        if args.push:
            subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, check=True)
            print("[OK] Push a origin main completado. GitHub Actions compilará la Release automáticamente.")
    else:
        print("\nPróximos pasos para publicar:")
        print("  git add -A")
        print(f'  git commit -m "chore(release): bump version to v{new_ver}"')
        print("  git push origin main")
        print("  (Al hacer push, GitHub Actions compilará el instalador y creará la Release automáticamente)\n")


if __name__ == "__main__":
    main()
