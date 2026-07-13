#!/usr/bin/env python3
"""Print the CHANGELOG.md section for a given version, to use as GitHub Release notes.

Usage: python extract_release_notes.py 0.2.0

Reads the section under a `## [<version>] ...` heading up to the next `## [` heading.
Exits 0 with empty output if the version has no section (the workflow falls back to a
generic note in that case).
"""
import re
import sys
from pathlib import Path


def extract(changelog_text: str, version: str) -> str:
    header_re = re.compile(r"^##\s+\[([^\]]+)\]")
    lines = changelog_text.splitlines()
    captured: list[str] = []
    capturing = False
    for line in lines:
        match = header_re.match(line)
        if match:
            if capturing:
                break  # reached the next version section
            capturing = match.group(1).strip() == version
            continue
        if capturing:
            captured.append(line)
    # Trim surrounding blank lines
    while captured and not captured[0].strip():
        captured.pop(0)
    while captured and not captured[-1].strip():
        captured.pop()
    return "\n".join(captured)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_release_notes.py <version>", file=sys.stderr)
        return 2
    version = sys.argv[1].lstrip("v").strip()
    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        return 0
    notes = extract(changelog.read_text(encoding="utf-8"), version)
    if notes:
        sys.stdout.write(notes + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
