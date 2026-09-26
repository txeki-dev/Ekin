"""Pruebas unitarias para el motor de plantillas de tablero (Board Templates)."""
import os
import tempfile
import database
import templates
from templates import (
    create_board_from_template, export_board_to_template,
    save_custom_template, get_custom_templates, delete_custom_template,
    get_all_templates, get_template_by_id
)


def test_builtin_templates_exist():
    builtins = templates.get_builtin_templates()
    ids = [t.id for t in builtins]
    assert "blank" in ids
    assert "software_agile" in ids
    assert "opositor_study" in ids
    assert "gtd_personal" in ids


def test_create_board_from_software_template(db_path):
    tmpl = templates.TEMPLATE_SOFTWARE_AGILE
    board_id = create_board_from_template("Mi Proyecto SW", "#2563eb", tmpl, db_path=db_path)
    assert board_id is not None

    board = database.get_board(board_id, db_path=db_path)
    assert board["name"] == "Mi Proyecto SW"
    assert board["color"] == "#2563eb"

    columns = database.get_columns(board_id, db_path=db_path)
    assert len(columns) == 5
    col_names = [c["name"] for c in columns]
    assert "📥 Backlog & Triage" in col_names
    assert "⚡ In Progress" in col_names

    # Verificar límites WIP
    wips = {c["name"]: c["wip_limit"] for c in columns}
    assert wips["📋 Ready to Code"] == 5
    assert wips["⚡ In Progress"] == 3

    # Verificar tareas semilla
    all_tasks = []
    for c in columns:
        all_tasks.extend(database.get_tasks(c["id"], db_path=db_path))
    assert len(all_tasks) == 2

    # Verificar tags creados
    categories = [cat["name"] for cat in database.get_tag_categories(db_path=db_path)]
    assert "Tipo" in categories


def test_create_board_from_opositor_template(db_path):
    tmpl = templates.TEMPLATE_OPOSITOR
    board_id = create_board_from_template("Oposición AGE", "#7c3aed", tmpl, db_path=db_path)
    columns = database.get_columns(board_id, db_path=db_path)
    assert len(columns) == 6
    col_names = [c["name"] for c in columns]
    assert "📚 Temas Pendientes" in col_names
    assert "🏆 Tema Dominado" in col_names

    categories = [cat["name"] for cat in database.get_tag_categories(db_path=db_path)]
    assert "Bloque" in categories
    assert "Fase" in categories


def test_create_board_from_blank_template(db_path):
    tmpl = templates.TEMPLATE_BLANK
    board_id = create_board_from_template("Tablero Limpio", "#3b82f6", tmpl, db_path=db_path)
    columns = database.get_columns(board_id, db_path=db_path)
    assert len(columns) == 0


def test_custom_template_lifecycle(db_path):
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Crear un tablero manual en la BD
        board_id = database.create_board("Tablero Base", "#10b981", db_path=db_path)
        col1 = database.create_column(board_id, "Fase 1", "#10b981", db_path=db_path, wip_limit=2)
        database.create_column(board_id, "Fase 2", "#3b82f6", db_path=db_path)

        task_id = database.create_task(col1, "Tarea de ejemplo", description="Detalle", db_path=db_path)
        val_id = database.get_or_create_tag_value("General", "Urgente", "#ef4444", db_path=db_path)
        database.set_task_tags(task_id, [val_id], db_path=db_path)

        # 2. Exportar a plantilla
        exported = export_board_to_template(
            board_id=board_id,
            template_id="mi_plantilla_custom",
            name="Mi Flujo Custom",
            description="Plantilla de prueba exportada",
            category="Mis Plantillas",
            include_tasks=True,
            db_path=db_path,
        )
        assert exported.name == "Mi Flujo Custom"
        assert len(exported.columns) == 2
        assert len(exported.seed_tasks) == 1

        # 3. Guardar a disco
        filepath = save_custom_template(exported, templates_dir=tmp_dir)
        assert os.path.exists(filepath)

        # 4. Listar plantillas custom
        customs = get_custom_templates(templates_dir=tmp_dir)
        assert len(customs) == 1
        assert customs[0].id == "mi_plantilla_custom"

        # 5. Obtener por ID y verificar unificación
        all_tmpls = get_all_templates(templates_dir=tmp_dir)
        assert any(t.id == "mi_plantilla_custom" for t in all_tmpls)

        found = get_template_by_id("mi_plantilla_custom", templates_dir=tmp_dir)
        assert found is not None
        assert found.name == "Mi Flujo Custom"

        # 6. Instanciar nuevo tablero desde la plantilla personalizada
        new_b_id = create_board_from_template("Clon desde Custom", "#0ea5e9", found, db_path=db_path)
        new_cols = database.get_columns(new_b_id, db_path=db_path)
        assert len(new_cols) == 2
        assert new_cols[0]["name"] == "Fase 1"
        assert new_cols[0]["wip_limit"] == 2

        new_tasks = database.get_tasks(new_cols[0]["id"], db_path=db_path)
        assert len(new_tasks) == 1
        assert new_tasks[0]["title"] == "Tarea de ejemplo"

        # 7. Eliminar plantilla
        deleted = delete_custom_template("mi_plantilla_custom", templates_dir=tmp_dir)
        assert deleted is True
        assert len(get_custom_templates(templates_dir=tmp_dir)) == 0


def test_create_board_dialog_headless(qapp, db_path):
    from board_template_dialogs import CreateBoardDialog
    with tempfile.TemporaryDirectory() as tmp_dir:
        dlg = CreateBoardDialog(templates_dir=tmp_dir, db_path=db_path)
        assert len(dlg.card_widgets) >= 4

        # Seleccionar plantilla opositor
        dlg._on_template_selected("opositor_study")
        assert dlg.selected_template.id == "opositor_study"
        assert dlg.name_input.text() == "Opositor (Estudio Sistemático)"

        # Comprobar filtro
        dlg._on_category_filter_changed(1)  # builtin
        assert all(w.template.is_builtin for w in dlg.card_widgets)

        dlg._on_category_filter_changed(2)  # custom (vacío inicialmente)
        assert len(dlg.card_widgets) == 0

        # Volver a all
        dlg._on_category_filter_changed(0)
        assert len(dlg.card_widgets) >= 4

        name, color, tmpl = dlg.get_data()
        assert name is not None
        assert tmpl is not None
        dlg.reject()


def test_save_as_template_dialog_headless(qapp, db_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from board_template_dialogs import SaveAsTemplateDialog
    monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)
    monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Ok)
    with tempfile.TemporaryDirectory() as tmp_dir:
        board_id = database.create_board("Tablero Opos", "#7c3aed", db_path=db_path)
        database.create_column(board_id, "Tema 1", "#7c3aed", db_path=db_path)

        dlg = SaveAsTemplateDialog(board_id, templates_dir=tmp_dir, db_path=db_path)
        dlg.name_input.setText("Plantilla Opos Test")
        dlg.desc_input.setText("Descripción test")
        dlg.include_tasks_chk.setChecked(True)
        dlg._save_template()

        customs = get_custom_templates(templates_dir=tmp_dir)
        assert len(customs) == 1
        assert customs[0].name == "Plantilla Opos Test"


def test_delete_custom_template_path_traversal_blocked(tmp_path):
    """Verifica que intentos de path traversal sean bloqueados en delete_custom_template."""
    # Crear un archivo fuera del directorio de plantillas
    outside_file = tmp_path / "important.json"
    outside_file.write_text('{"secret": true}', encoding="utf-8")
    assert outside_file.exists()

    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Intentar borrar con path traversal relativo
    deleted = delete_custom_template("../important", templates_dir=str(templates_dir))
    assert deleted is False
    assert outside_file.exists()


def test_extract_template_preserves_ai_system_prompt(db_path):
    """Verifica que extract_template_from_board preserve el ai_system_prompt del tablero."""
    board_id = database.create_board("Tablero IA", "#2563eb", db_path=db_path)
    database.set_board_mcp_config(
        board_id,
        enabled=True,
        ai_system_prompt="Eres un Agile Coach experto.",
        db_path=db_path,
    )

    tmpl = templates.export_board_to_template(
        board_id=board_id,
        template_id="custom_ai_tmpl",
        name="Plantilla IA",
        description="Con prompt",
        db_path=db_path,
    )
    assert tmpl.ai_system_prompt == "Eres un Agile Coach experto."

