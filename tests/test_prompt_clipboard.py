"""#67: AI Prompt Clipboard por tablero (packs DEV / Opositor / GTD con el esquema JSON de
AI-Dev-Prompt-Clipboard, variables {{...}} y pack recordado por tablero)."""
import json

import pytest
from PySide6.QtWidgets import QApplication

import database
import prompt_packs
import templates
from prompt_clipboard_dialog import PromptClipboardDialog


@pytest.fixture(autouse=True)
def user_packs_dir(tmp_path, monkeypatch):
    d = tmp_path / "user_packs"
    monkeypatch.setattr(prompt_packs, "USER_PACKS_DIR", str(d))
    return d


# --- prompt_packs (lógica pura) ------------------------------------------------

@pytest.mark.parametrize("pack_id", ["dev", "opositor", "gtd"])
def test_builtin_packs_are_valid_and_target_the_board_mcp(pack_id):
    prompts = prompt_packs.load_pack(pack_id)
    assert prompts
    assert len({p["id"] for p in prompts}) == len(prompts)
    for p in prompts:
        assert p["title"] and p["category"] and p["prompt"]
        assert "{{mcp_server}}" in p["prompt"]


def test_dev_pack_keeps_the_twelve_protocols_on_the_board_not_markdown_files():
    prompts = {p["id"]: p for p in prompt_packs.load_pack("dev")}
    assert set(prompts) == {
        "intro", "feature_plan", "feature_build", "outro", "initial", "migrate",
        "audit", "remediate", "rdi", "product_strategy", "business_strategy", "recover",
    }
    for pid, p in prompts.items():
        if pid not in ("initial", "migrate"):  # esos dos solo los nombran para no crearlos / migrarlos
            assert "diary.md" not in p["prompt"] and "backlog.md" not in p["prompt"], pid


def test_find_and_fill_variables():
    text = "Board {{board_name}} via {{ mcp_server }} on {{tema}} and {{tema}}"
    assert prompt_packs.find_variables(text) == ["board_name", "mcp_server", "tema"]
    filled = prompt_packs.fill_variables(text, {"board_name": "SW", "mcp_server": "ekin-sw"})
    assert filled == "Board SW via ekin-sw on {{tema}} and {{tema}}"


def test_board_variables_use_the_claude_code_server_name():
    assert prompt_packs.board_variables({"name": "SW - Ekin"}) == {
        "board_name": "SW - Ekin", "mcp_server": "ekin-sw_-_ekin",
    }


def test_import_pack_validates_and_lists_it(tmp_path):
    good = tmp_path / "Frontend UI.json"
    good.write_text(json.dumps([{"id": "a", "title": "A", "tag": "<a>", "category": "UI",
                                 "color": "#fff", "role": "R", "description": "d", "prompt": "P {{x}}"}]),
                    encoding="utf-8-sig")  # los packs del Clipboard pueden llevar BOM
    pack_id = prompt_packs.import_pack(str(good))
    assert (pack_id, "Frontend UI") in prompt_packs.list_packs()
    assert prompt_packs.load_pack(pack_id)[0]["prompt"] == "P {{x}}"

    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([{"title": "sin id ni prompt"}]), encoding="utf-8")
    with pytest.raises(ValueError):
        prompt_packs.import_pack(str(bad))
    assert all(pid != "user:bad" for pid, _ in prompt_packs.list_packs())


def test_resolve_pack_id_falls_back_to_dev():
    assert prompt_packs.resolve_pack_id(None) == "dev"
    assert prompt_packs.resolve_pack_id("user:borrado") == "dev"
    assert prompt_packs.resolve_pack_id("gtd") == "gtd"


# --- Pack recordado por tablero y preasignado por plantilla ---------------------

@pytest.mark.parametrize("template, expected", [
    (templates.TEMPLATE_SOFTWARE_AGILE, "dev"),
    (templates.TEMPLATE_OPOSITOR, "opositor"),
    (templates.TEMPLATE_GTD_PERSONAL, "gtd"),
    (templates.TEMPLATE_BLANK, None),
])
def test_boards_created_from_templates_get_their_prompt_pack(db_path, template, expected):
    board_id = templates.create_board_from_template("T", "#000000", template, db_path=db_path)
    assert database.get_board(board_id, db_path)["prompt_pack"] == expected


def test_set_board_prompt_pack(db_path):
    board_id = database.create_board("B", db_path=db_path)
    assert database.get_board(board_id, db_path)["prompt_pack"] is None
    database.set_board_prompt_pack(board_id, "gtd", db_path)
    assert database.get_board(board_id, db_path)["prompt_pack"] == "gtd"


# --- Modal ---------------------------------------------------------------------

def _dialog(qapp, db_path, name="SW - Ekin", pack=None):
    board_id = database.create_board(name, db_path=db_path)
    if pack:
        database.set_board_prompt_pack(board_id, pack, db_path)
    return board_id, PromptClipboardDialog(board_id, db_path=db_path)


def _titles(dlg):
    return [dlg.prompt_list.item(i).text() for i in range(dlg.prompt_list.count())]


def test_dialog_opens_on_the_board_pack_with_board_variables_filled(qapp, db_path):
    _, dlg = _dialog(qapp, db_path, pack="opositor")
    assert dlg.pack_combo.currentData() == "opositor"
    assert dlg.prompt_list.count() == len(prompt_packs.load_pack("opositor"))
    dlg.prompt_list.setCurrentRow(0)
    preview = dlg.preview.toPlainText()
    assert "ekin-sw_-_ekin" in preview and "SW - Ekin" in preview
    assert "{{mcp_server}}" not in preview
    dlg.close()


def test_changing_pack_is_remembered_for_the_board(qapp, db_path):
    board_id, dlg = _dialog(qapp, db_path)
    assert dlg.pack_combo.currentData() == "dev"
    dlg.pack_combo.setCurrentIndex(dlg.pack_combo.findData("gtd"))
    assert database.get_board(board_id, db_path)["prompt_pack"] == "gtd"
    assert dlg.prompt_list.count() == len(prompt_packs.load_pack("gtd"))
    dlg.close()


def test_search_and_category_filter(qapp, db_path):
    _, dlg = _dialog(qapp, db_path)
    dlg.search_input.setText("REMEDIAT")  # título, tag, rol o descripción; sin distinguir mayúsculas
    assert _titles(dlg) == ["REMEDIATE"]
    dlg.search_input.clear()
    dlg.category_combo.setCurrentIndex(dlg.category_combo.findData("TDD"))
    assert dlg.prompt_list.count() == 2
    dlg.close()


def test_copy_fills_board_vars_and_asks_for_the_rest(qapp, db_path, monkeypatch):
    _, dlg = _dialog(qapp, db_path, pack="opositor")
    asked = []

    def fake_ask(parent, names):
        asked.append(names)
        return {"tema": "Tema 3: La Corona"}

    monkeypatch.setattr("prompt_clipboard_dialog.ask_variable_values", fake_ask)
    row = next(i for i, p in enumerate(dlg.visible_prompts) if p["id"] == "self_test")
    dlg.prompt_list.setCurrentRow(row)
    dlg.copy_btn.click()

    copied = QApplication.clipboard().text()
    assert asked == [["tema"]]
    assert "Topic: Tema 3: La Corona" in copied
    assert "ekin-sw_-_ekin" in copied and "{{" not in copied
    dlg.close()


def test_copy_is_cancelled_if_variables_dialog_is_cancelled(qapp, db_path, monkeypatch):
    _, dlg = _dialog(qapp, db_path, pack="opositor")
    QApplication.clipboard().setText("previo")
    monkeypatch.setattr("prompt_clipboard_dialog.ask_variable_values", lambda parent, names: None)
    row = next(i for i, p in enumerate(dlg.visible_prompts) if p["id"] == "self_test")
    dlg.prompt_list.setCurrentRow(row)
    dlg.copy_btn.click()
    assert QApplication.clipboard().text() == "previo"
    dlg.close()


def test_import_button_adds_pack_and_selects_it(qapp, db_path, monkeypatch, tmp_path):
    pack_file = tmp_path / "Security.json"
    pack_file.write_text(json.dumps([{"id": "s", "title": "THREAT MODEL", "category": "SecOps", "prompt": "x"}]),
                         encoding="utf-8")
    board_id, dlg = _dialog(qapp, db_path)
    monkeypatch.setattr("prompt_clipboard_dialog.QFileDialog.getOpenFileName",
                        staticmethod(lambda *a, **k: (str(pack_file), "")))
    dlg.import_btn.click()
    assert dlg.pack_combo.currentData() == "user:Security"
    assert _titles(dlg) == ["THREAT MODEL"]
    assert database.get_board(board_id, db_path)["prompt_pack"] == "user:Security"
    dlg.close()
