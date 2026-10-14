"""#88: semáforo de cuota restante de las CLIs de IA. Claude Code la expone en el JSON de su
status line; Ekin instala (solo si se le pide) una status line que la guarda y la lee de ahí.
Todas las rutas de usuario se redirigen a tmp_path."""
import json
import os
import subprocess
import sys
import time

import pytest

import cli_quota
import cli_tools
import quota_popup
import sidebar
import start_working as sw

HOUR = 3600


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    quota_dir = tmp_path / ".ekin" / "cli_quota"
    monkeypatch.setattr(cli_quota, "QUOTA_DIR", str(quota_dir))
    monkeypatch.setattr(cli_quota, "PREVIOUS_FILE", str(quota_dir / "claude_prev_statusline.json"))
    monkeypatch.setattr(cli_quota, "SCRIPT_TARGET", str(tmp_path / ".ekin" / "bin" / "claude_statusline.py"))
    monkeypatch.setattr(cli_quota, "CLAUDE_SETTINGS", str(tmp_path / ".claude" / "settings.json"))
    monkeypatch.setattr(cli_quota, "_python_for_scripts", lambda: r"C:\py\python.exe")
    return tmp_path


def _write_snapshot(five_used=23.5, week_used=41.2, five_reset=None, week_reset=None):
    now = time.time()
    os.makedirs(cli_quota.QUOTA_DIR, exist_ok=True)
    data = {"rate_limits": {
        "five_hour": {"used_percentage": five_used, "resets_at": five_reset or now + HOUR},
        "seven_day": {"used_percentage": week_used, "resets_at": week_reset or now + 48 * HOUR},
    }, "captured_at": now}
    with open(os.path.join(cli_quota.QUOTA_DIR, "claude.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def test_read_quota_drops_expired_windows():
    assert cli_quota.read_quota() is None
    _write_snapshot(five_reset=time.time() - 10)
    snapshot = cli_quota.read_quota()
    assert "five_hour" not in snapshot and snapshot["seven_day"]["used_percentage"] == 41.2
    _write_snapshot(five_reset=time.time() - 10, week_reset=time.time() - 10)
    assert cli_quota.read_quota() is None


@pytest.mark.parametrize("five, week, state", [
    (10, 69.9, cli_quota.GREEN), (70, 20, cli_quota.AMBER), (20, 95, cli_quota.RED),
])
def test_quota_state_uses_the_most_used_window(five, week, state):
    _write_snapshot(five, week)
    assert cli_quota.quota_state(cli_quota.read_quota()) == state
    assert cli_quota.quota_state(None) == cli_quota.GREY


def _run_statusline(home, payload):
    env = {**os.environ, "USERPROFILE": str(home), "HOME": str(home)}
    return subprocess.run(
        [sys.executable, cli_quota.SCRIPT_SOURCE], input=json.dumps(payload), capture_output=True,
        text=True, env=env, timeout=30,
    )


def test_statusline_script_saves_the_quota_and_prints_a_line(home):
    reset = int(time.time()) + HOUR
    payload = {"model": {"display_name": "Opus"},
               "rate_limits": {"five_hour": {"used_percentage": 23, "resets_at": reset},
                               "seven_day": {"used_percentage": 41, "resets_at": reset}}}
    res = _run_statusline(home, payload)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == "Opus · 5h 77% left · 7d 59% left"
    assert cli_quota.read_quota()["five_hour"]["used_percentage"] == 23


def test_statusline_script_keeps_showing_the_previous_status_line(home):
    os.makedirs(cli_quota.QUOTA_DIR, exist_ok=True)
    previous = f'"{sys.executable}" -c "import sys; print(\'PREV\', len(sys.stdin.read()) > 0)"'
    with open(cli_quota.PREVIOUS_FILE, "w", encoding="utf-8") as fh:
        json.dump({"type": "command", "command": previous}, fh)
    res = _run_statusline(home, {"model": {"display_name": "Opus"}})
    assert res.stdout.strip() == "PREV True"


def test_install_and_uninstall_keep_other_settings_and_the_previous_status_line():
    os.makedirs(os.path.dirname(cli_quota.CLAUDE_SETTINGS))
    original = {"theme": "dark", "statusLine": {"type": "command", "command": "mi-statusline.sh"}}
    with open(cli_quota.CLAUDE_SETTINGS, "w", encoding="utf-8") as fh:
        json.dump(original, fh)

    cli_quota.install_claude_statusline()
    with open(cli_quota.CLAUDE_SETTINGS, encoding="utf-8") as fh:
        settings = json.load(fh)
    assert settings["theme"] == "dark"
    assert settings["statusLine"]["command"] == '"C:/py/python.exe" "' + cli_quota.SCRIPT_TARGET.replace("\\", "/") + '"'
    assert os.path.isfile(cli_quota.SCRIPT_TARGET) and os.path.isfile(cli_quota.CLAUDE_SETTINGS + ".ekin-backup")
    assert cli_quota.is_installed()
    cli_quota.install_claude_statusline()  # reinstalar no pisa la status line previa guardada

    cli_quota.uninstall_claude_statusline()
    with open(cli_quota.CLAUDE_SETTINGS, encoding="utf-8") as fh:
        assert json.load(fh) == original
    assert not cli_quota.is_installed() and not os.path.exists(cli_quota.PREVIOUS_FILE)


def test_install_without_previous_status_line_and_uninstall_removes_it():
    cli_quota.install_claude_statusline()
    cli_quota.uninstall_claude_statusline()
    with open(cli_quota.CLAUDE_SETTINGS, encoding="utf-8") as fh:
        assert "statusLine" not in json.load(fh)


def test_sidebar_quota_indicator(qapp, db_path):
    bar = sidebar.SidebarWidget(db_path=db_path)
    assert bar.quota_btn.toolTip() == quota_popup.tooltip_text(None)
    _write_snapshot(23, 41)
    bar.refresh_quota_indicator()
    assert "77" in bar.quota_btn.toolTip() and "59" in bar.quota_btn.toolTip()
    bar.close()


def test_quota_popup_offers_enabling_then_shows_the_quota(qapp, monkeypatch):
    monkeypatch.setattr(cli_tools, "detect_installed", lambda: [
        (cli_tools.KNOWN_CLIS[0], "claude.CMD"), (cli_tools.KNOWN_CLIS[1], "agy.EXE"),
    ])
    popup = quota_popup.QuotaPopup()
    assert hasattr(popup, "enable_btn") and not hasattr(popup, "disable_btn")
    popup.close()

    cli_quota.install_claude_statusline()
    _write_snapshot(23, 41)
    popup = quota_popup.QuotaPopup()
    from PySide6.QtWidgets import QLabel
    texts = " ".join(label.text() for label in popup.findChildren(QLabel))
    assert "77" in texts and "59" in texts and hasattr(popup, "disable_btn")
    popup.close()


def test_start_working_asks_before_opening_claude_with_red_quota(qapp, db_path, tmp_path, monkeypatch):
    import database
    board_id = database.create_board("SW", db_path=db_path)
    database.create_column(board_id, "Backlog", db_path=db_path)
    database.set_board_local_dir(board_id, str(tmp_path), db_path=db_path)
    database.set_board_mcp_config(board_id, enabled=True, db_path=db_path)
    _write_snapshot(97, 50)
    monkeypatch.setattr(sw.cli_tools, "detect_installed", lambda: [(cli_tools.KNOWN_CLIS[0], "claude.CMD")])
    asked = []
    monkeypatch.setattr(sw.QMessageBox, "question", staticmethod(lambda *a, **k: asked.append(a[2]) or sw.QMessageBox.No))
    monkeypatch.setattr(sw, "get_mcp_manager", lambda db_path=None: pytest.fail("no debe arrancar"))

    assert sw.start_working(None, board_id, db_path=db_path) is None
    assert "3%" in asked[0]
