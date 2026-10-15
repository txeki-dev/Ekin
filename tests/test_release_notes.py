"""El workflow de release (windows-latest, pwsh) extrae las notas de CHANGELOG.md con
.github/scripts/extract_release_notes.py. Con la salida en cp1252, un emoji o una flecha en
las notas tumbaba el paso y la versión no se publicaba (pasó a estar en Windows en v1.0.1)."""
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / ".github" / "scripts" / "extract_release_notes.py"
CHANGELOG = "# Changelog\n\n## [Unreleased]\n\n## [9.9.9] - 2026-10-15\n\n### Added\n- Enlaces 📄 → «adjuntos» — sí\n\n## [9.9.8]\n- old\n"


def _run(tmp_path, *args):
    (tmp_path / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    env = {**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=tmp_path, env=env, capture_output=True)


def test_notes_with_emoji_are_written_as_utf8_to_the_output_file(tmp_path):
    res = _run(tmp_path, "9.9.9", "RELEASE_NOTES.md")
    assert res.returncode == 0, res.stderr.decode(errors="replace")
    assert (tmp_path / "RELEASE_NOTES.md").read_text(encoding="utf-8") == "### Added\n- Enlaces 📄 → «adjuntos» — sí\n"


def test_notes_on_stdout_are_utf8_whatever_the_console_encoding(tmp_path):
    res = _run(tmp_path, "9.9.9")
    assert res.returncode == 0, res.stderr.decode(errors="replace")
    assert "📄 →" in res.stdout.decode("utf-8")


def test_release_workflow_writes_the_notes_file_without_a_pipe():
    workflow = (SCRIPT.parent.parent / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert 'extract_release_notes.py "$env:VERSION" RELEASE_NOTES.md' in workflow
