"""#153: Ajustes → Carpetas de Ekin enseña dónde guarda Ekin cada cosa y abre cada carpeta."""
import os

import settings_dialog
from strings import t


def test_folders_follow_the_database_and_the_user_folders(db_path):
    folders = {key: (icon, path) for key, icon, path in settings_dialog.ekin_folders(db_path)}
    assert list(folders) == ["program", "data", "backups", "logs", "templates", "prompt_packs"]
    data_dir = os.path.dirname(os.path.abspath(db_path))
    assert folders["data"][1] == data_dir
    assert folders["backups"][1] == os.path.join(data_dir, "backups")
    assert folders["program"][1] == os.path.dirname(os.path.abspath(settings_dialog.__file__))
    assert all(icon for icon, _ in folders.values())


def test_folders_tab_opens_each_existing_folder(qapp, db_path, monkeypatch):
    opened = []
    monkeypatch.setattr(settings_dialog.QDesktopServices, "openUrl", lambda url: opened.append(url.toLocalFile()))
    dlg = settings_dialog.SettingsDialog(db_path)
    assert dlg.tabs.tabText(2) == t("settings.tab_folders")

    data_btn = dlg.folder_open_buttons["data"]
    assert data_btn.isEnabled()
    data_btn.click()
    assert os.path.normcase(os.path.normpath(opened[0])) == os.path.normcase(os.path.dirname(os.path.abspath(db_path)))

    backups = dlg.folder_open_buttons["backups"]  # aún no hay copias: no se puede abrir
    assert not backups.isEnabled() and backups.toolTip() == t("settings.folder_missing")
    dlg.reject()
