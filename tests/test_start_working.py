"""#87: START WORKING abre la CLI del agente en el directorio local del tablero, con el MCP del
tablero en marcha y registrado y el prompt de inicio cargado. Sin procesos reales: subprocess,
shutil.which y el gestor MCP se simulan."""
import subprocess
from types import SimpleNamespace

import pytest

import cli_tools
import database
import prompt_packs
import start_working as sw
import templates
from board_view import BoardViewWidget


@pytest.fixture(autouse=True)
def no_real_quota(tmp_path, monkeypatch):
    """La cuota real de Claude Code de esta máquina no debe influir (en rojo, preguntaría)."""
    import cli_quota
    monkeypatch.setattr(cli_quota, "QUOTA_DIR", str(tmp_path / "cli_quota"))


def _sw_board(db_path, local_dir, mcp=True):
    board_id = templates.create_board_from_template("SW - Demo", "#2563eb", templates.TEMPLATE_SOFTWARE_AGILE, db_path=db_path)
    database.set_board_local_dir(board_id, local_dir, db_path=db_path)
    database.set_board_mcp_config(board_id, enabled=mcp, secret="s3cr3t", db_path=db_path)
    return board_id


# --- cli_tools ---------------------------------------------------------------

def test_detect_installed_uses_the_path(monkeypatch):
    paths = {"claude": r"C:\npm\claude.CMD", "agy": r"C:\agy\agy.EXE"}
    monkeypatch.setattr(cli_tools.shutil, "which", paths.get)
    assert [(tool.id, path) for tool, path in cli_tools.detect_installed()] == [
        ("claude", paths["claude"]), ("agy", paths["agy"]),
    ]


def test_build_launch_passes_the_prompt_to_exes_and_uses_the_clipboard_for_npm_shims():
    claude, agy = cli_tools.KNOWN_CLIS[0], cli_tools.KNOWN_CLIS[1]
    prompt = 'Multi\n<line> "prompt"; x'
    assert cli_tools.build_launch(agy, r"C:\agy\agy.EXE", prompt) == ([r"C:\agy\agy.EXE", "-i", prompt], False)
    assert cli_tools.build_launch(claude, r"C:\bin\claude.exe", prompt) == ([r"C:\bin\claude.exe", prompt], False)
    assert cli_tools.build_launch(claude, r"C:\npm\claude.CMD", prompt) == ([r"C:\npm\claude.CMD"], True)


class _Runs:
    """subprocess.run simulado: devuelve el resultado indicado según el subcomando."""
    def __init__(self, results):
        self.results, self.calls = results, []

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs.get("cwd")))
        key = " ".join(argv[1:3])
        code, out = self.results.get(key, (0, ""))
        return SimpleNamespace(returncode=code, stdout=out, stderr="")


def test_claude_mcp_is_added_in_the_repo_scope_only_when_missing(monkeypatch):
    claude = cli_tools.KNOWN_CLIS[0]
    board = {"name": "SW - Demo"}
    runs = _Runs({"mcp get": (1, "")})
    monkeypatch.setattr(cli_tools.subprocess, "run", runs)
    assert cli_tools.ensure_mcp_registered(claude, "claude", board, "http://sse", "http://rpc", r"C:\repo") == (True, "")
    assert runs.calls[-1] == (["claude", "mcp", "add", "--transport", "sse", "ekin-sw_-_demo", "http://sse"], r"C:\repo")

    runs = _Runs({"mcp get": (0, "ekin-sw_-_demo: ...")})
    monkeypatch.setattr(cli_tools.subprocess, "run", runs)
    cli_tools.ensure_mcp_registered(claude, "claude", board, "http://sse", "http://rpc", r"C:\repo")
    assert [argv[2] for argv, _ in runs.calls] == ["get"]


def test_agy_mcp_uses_the_http_rpc_endpoint(monkeypatch):
    agy = cli_tools.KNOWN_CLIS[1]
    runs = _Runs({"mcp list": (0, "No MCP servers configured.")})
    monkeypatch.setattr(cli_tools.subprocess, "run", runs)
    cli_tools.ensure_mcp_registered(agy, "agy", {"name": "SW - Demo"}, "http://sse", "http://rpc", r"C:\repo")
    assert runs.calls[-1][0] == ["agy", "mcp", "add", "ekin-sw_-_demo", "http://rpc"]


def test_update_failure_is_reported_not_raised(monkeypatch):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired("claude update", 120)
    monkeypatch.setattr(cli_tools.subprocess, "run", boom)
    ok, msg = cli_tools.update_cli(cli_tools.KNOWN_CLIS[0], "claude")
    assert not ok and "timed out" in msg
    assert cli_tools.update_cli(cli_tools.KNOWN_CLIS[2], "gemini") == (True, "")


# --- start_working (flujo) ---------------------------------------------------

def test_start_prompt_is_the_pack_intro_with_board_variables(db_path, tmp_path):
    (tmp_path / "main.py").write_text("print('hola')")
    board = database.get_board(_sw_board(db_path, str(tmp_path)), db_path=db_path)
    prompt = sw.start_prompt(board)
    assert prompt.startswith("Execute the `<session_start_hybrid>` protocol.")
    assert "ekin-sw_-_demo" in prompt and "{{" not in prompt

    opositor = {**board, "prompt_pack": "opositor"}
    assert "<study_session_start>" in sw.start_prompt(opositor)

    # #136: el pack GTD no tenía prompt de inicio y Work arrancaba con CAPTURA RÁPIDA, que
    # termina en un «BRAIN DUMP:» vacío
    gtd = sw.start_prompt({**board, "prompt_pack": "gtd"})
    assert "<gtd_session_start>" in gtd and "BRAIN DUMP" not in gtd


@pytest.fixture
def flow(monkeypatch, qapp):
    """Simula todo lo externo y registra lo que haría START WORKING."""
    rec = SimpleNamespace(launched=None, messages=[], started=0, mcp_dialog=0, clipboard=None)
    monkeypatch.setattr(sw.cli_tools, "detect_installed", lambda: [(cli_tools.KNOWN_CLIS[0], r"C:\npm\claude.CMD")])
    monkeypatch.setattr(sw.cli_tools, "update_cli", lambda tool, exe, on_retry=None: (False, "EBUSY"))
    monkeypatch.setattr(sw.cli_tools, "ensure_mcp_registered", lambda *a: (True, ""))
    monkeypatch.setattr(sw.cli_tools, "launch", lambda argv, cwd: setattr(rec, "launched", (argv, cwd)))
    manager = SimpleNamespace(port=8765, start=lambda: setattr(rec, "started", rec.started + 1) or True,
                              get_board_sse_url=lambda uuid, token: f"http://127.0.0.1:8765/sse?board={uuid}&token={token}")
    monkeypatch.setattr(sw, "get_mcp_manager", lambda db_path=None: manager)
    for kind in ("information", "warning"):
        monkeypatch.setattr(sw.QMessageBox, kind, staticmethod(lambda parent, title, text: rec.messages.append(text)))
    monkeypatch.setattr(sw.QApplication.clipboard(), "setText", lambda text: setattr(rec, "clipboard", text))
    return rec


def test_start_working_opens_the_cli_in_the_repo(db_path, tmp_path, flow):
    (tmp_path / "main.py").write_text("print('hola')")
    board_id = _sw_board(db_path, str(tmp_path))
    assert sw.start_working(None, board_id, db_path=db_path) == "claude"

    assert flow.started == 1
    assert flow.launched == ([r"C:\npm\claude.CMD"], str(tmp_path))
    assert flow.clipboard.startswith("Execute the `<session_start_hybrid>` protocol.")
    assert any("EBUSY" in m for m in flow.messages)  # el update falló pero no bloqueó
    assert any("Ctrl+V" in m for m in flow.messages)


def test_start_working_without_mcp_opens_the_mcp_dialog_and_stops(db_path, tmp_path, flow):
    board_id = _sw_board(db_path, str(tmp_path), mcp=False)
    opened = []
    assert sw.start_working(None, board_id, db_path=db_path, open_mcp_dialog=lambda: opened.append(1)) is None
    assert opened == [1] and flow.launched is None and flow.started == 0


def test_start_working_asks_which_cli_when_several_are_installed(db_path, tmp_path, flow, monkeypatch):
    board_id = _sw_board(db_path, str(tmp_path))
    monkeypatch.setattr(sw.cli_tools, "detect_installed", lambda: [
        (cli_tools.KNOWN_CLIS[0], r"C:\npm\claude.CMD"), (cli_tools.KNOWN_CLIS[1], r"C:\agy\agy.EXE"),
    ])
    monkeypatch.setattr(sw.QInputDialog, "getItem", staticmethod(lambda *a, **k: ("Antigravity CLI", True)))
    assert sw.start_working(None, board_id, db_path=db_path) == "agy"
    argv, cwd = flow.launched
    assert argv[:2] == [r"C:\agy\agy.EXE", "-i"] and argv[2].startswith("Execute the")


def test_start_working_without_folder_or_cli_warns(db_path, tmp_path, flow, monkeypatch):
    assert sw.start_working(None, _sw_board(db_path, str(tmp_path / "no-existe")), db_path=db_path) is None
    monkeypatch.setattr(sw.cli_tools, "detect_installed", lambda: [])
    assert sw.start_working(None, _sw_board(db_path, str(tmp_path)), db_path=db_path) is None
    assert flow.launched is None and len(flow.messages) == 2


def test_work_button_is_always_there_and_says_what_it_will_do(qapp, db_path, tmp_path):
    view = BoardViewWidget(db_path=db_path)
    view.load_board(_sw_board(db_path, None))
    assert not view.start_working_btn.isHidden()
    assert view.start_working_btn.toolTip() == sw.t("board_view.work_link_tooltip")
    view.load_board(_sw_board(db_path, str(tmp_path)))
    assert view.start_working_btn.toolTip() == sw.t("board_view.start_working_tooltip")
    view.close()


def test_work_without_a_folder_asks_for_it_then_starts(qapp, db_path, tmp_path, monkeypatch):
    """Enlazar el directorio cuesta un clic: Work lo pide si falta y sigue con START WORKING."""
    import board_view as bv_module
    view = BoardViewWidget(db_path=db_path)
    board_id = _sw_board(db_path, None)
    view.load_board(board_id)
    started = []
    monkeypatch.setattr(sw, "start_working", lambda *a, **k: started.append(a[1]))

    monkeypatch.setattr(bv_module.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: ""))
    view.start_working_btn.click()  # cancelado: no enlaza ni arranca
    assert database.get_board(board_id, db_path=db_path)["local_dir"] is None and started == []

    monkeypatch.setattr(bv_module.QFileDialog, "getExistingDirectory",
                        staticmethod(lambda *a, **k: str(tmp_path).replace("\\", "/")))
    view.start_working_btn.click()
    assert database.get_board(board_id, db_path=db_path)["local_dir"] == str(tmp_path)
    assert started == [board_id]
    assert view.start_working_btn.toolTip() == sw.t("board_view.start_working_tooltip")
    view.close()


def test_status_moves_to_the_board_footer(qapp, db_path, tmp_path):
    """La cabecera se recortaba: el recuento, el MCP y la sync viven ahora en el pie de página."""
    view = BoardViewWidget(db_path=db_path)
    view.load_board(_sw_board(db_path, None))
    for widget in (view.board_counts_chip, view.mcp_btn, view.sync_btn):
        assert view.board_footer.isAncestorOf(widget) and not view.board_header.isAncestorOf(widget)
    for widget in (view.bulk_add_btn, view.prompts_btn, view.diary_btn, view.start_working_btn):
        assert view.board_header.isAncestorOf(widget)
    assert not view.board_footer.isHidden()
    view.load_board(-1)
    assert view.board_footer.isHidden()
    view.close()


def test_settings_local_folders_tab(qapp, db_path, tmp_path, monkeypatch):
    import settings_dialog
    linked = _sw_board(db_path, str(tmp_path))
    unlinked = _sw_board(db_path, None)
    dlg = settings_dialog.SettingsDialog(db_path)
    assert dlg.tabs.count() == 3  # General, Directorios locales y Carpetas de Ekin (#153)
    assert set(dlg.local_dir_rows) >= {linked, unlinked}
    assert dlg.local_dir_rows[linked][0].text() == str(tmp_path)
    changes = []
    dlg.local_dirs_changed.connect(lambda: changes.append(1))

    other = tmp_path / "otro"
    other.mkdir()
    monkeypatch.setattr(settings_dialog.QFileDialog, "getExistingDirectory", staticmethod(lambda *a, **k: str(other)))
    dlg._browse_local_dir(unlinked)
    assert database.get_board(unlinked, db_path=db_path)["local_dir"] == str(other)

    dlg.local_dir_rows[linked][1].click()  # Quitar
    assert database.get_board(linked, db_path=db_path)["local_dir"] is None
    assert not dlg.local_dir_rows[linked][1].isEnabled() and changes == [1, 1]
    dlg.close()


def test_update_is_retried_before_warning(monkeypatch):
    """#151: un update que falla a la primera se reintenta (hasta 3 veces) antes de avisar."""
    claude = cli_tools.KNOWN_CLIS[0]
    monkeypatch.setattr(cli_tools, "UPDATE_RETRY_DELAY", 0)
    results = iter([(1, "EBUSY"), (1, "EBUSY"), (0, "updated")])
    calls, retries = [], []

    def flaky(argv, **kwargs):
        calls.append(argv)
        code, out = next(results)
        return SimpleNamespace(returncode=code, stdout=out, stderr="")

    monkeypatch.setattr(cli_tools.subprocess, "run", flaky)
    assert cli_tools.update_cli(claude, "claude", on_retry=retries.append) == (True, "updated")
    assert len(calls) == 3 and retries == [2, 3]

    monkeypatch.setattr(cli_tools.subprocess, "run", _Runs({"update": (1, "offline")}))
    assert cli_tools.update_cli(claude, "claude") == (False, "offline")


def test_a_folder_without_code_starts_with_initial(db_path, tmp_path):
    """#152: si la carpeta del tablero aún no tiene código, ▶ Trabajar arranca con INITIAL (prepara
    graphify y siembra el backlog) en vez de INTRO. Los packs sin INITIAL no cambian."""
    (tmp_path / "README.md").write_text("# Idea")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.js").write_text("")
    board = database.get_board(_sw_board(db_path, str(tmp_path)), db_path=db_path)
    initial = next(p for p in prompt_packs.load_pack("dev") if p["id"] == "initial")
    assert sw.start_prompt(board) == prompt_packs.fill_variables(initial["prompt"], prompt_packs.board_variables(board))
    assert "<gtd_session_start>" in sw.start_prompt({**board, "prompt_pack": "gtd"})

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("export {}")
    assert sw.start_prompt(board).startswith("Execute the `<session_start_hybrid>` protocol.")
