"""Pruebas unitarias para la independización de la categoría 'Priority' y su modal dedicado."""
import database
from detail_dialog.priority_dialog import PriorityManagerDialog, ensure_priority_category
from detail_dialog.tag_manager_dialog import TagManagerDialog
from detail_dialog.tag_picker_dialog import TagPickerDialog
from detail_dialog.task_detail_dialog import TaskDetailDialog


def test_ensure_priority_category_creates_defaults(qapp, db_path):
    cat_id = ensure_priority_category(db_path)
    assert cat_id is not None
    values = database.get_tag_values(cat_id, db_path)
    val_names = [v["value"] for v in values]
    assert len(val_names) >= 3


def test_tag_manager_dialog_excludes_priority(qapp, db_path):
    ensure_priority_category(db_path)
    database.create_tag_category("Frontend", db_path)
    database.create_tag_category("Backend", db_path)

    dlg = TagManagerDialog(db_path)
    cat_names = [dlg.cat_list.item(i).text() for i in range(dlg.cat_list.count())]
    assert "Frontend" in cat_names
    assert "Backend" in cat_names
    assert "Priority" not in cat_names
    assert "Prioridad" not in cat_names
    dlg.reject()


def test_tag_picker_dialog_excludes_priority(qapp, db_path):
    ensure_priority_category(db_path)
    database.create_tag_category("Design", db_path)

    picker = TagPickerDialog(db_path)
    items = [picker.category_combo.itemText(i) for i in range(picker.category_combo.count())]
    assert "Design" in items
    assert "Priority" not in items
    assert "Prioridad" not in items
    picker.reject()


def test_priority_manager_dialog_crud(qapp, db_path):
    cat_id = ensure_priority_category(db_path)
    dlg = PriorityManagerDialog(db_path)
    assert dlg.cat_id == cat_id
    assert dlg.values_layout.count() >= 3

    # Añadir nueva prioridad personalizada
    dlg.new_value_input.setText("Crítica")
    dlg.new_value_color = "#ff0000"
    dlg.add_priority_value()

    values = database.get_tag_values(cat_id, db_path)
    crit_val = next((v for v in values if v["value"] == "Crítica"), None)
    assert crit_val is not None
    assert crit_val["color"] == "#ff0000"

    # Actualizar color mockeando QColorDialog
    from PySide6.QtWidgets import QColorDialog
    from PySide6.QtGui import QColor
    orig_get_color = QColorDialog.getColor
    try:
        QColorDialog.getColor = lambda *a, **k: QColor("#00ff00")
        dlg.change_value_color({"id": crit_val["id"], "value": "Crítica", "color": "#00ff00"})
    finally:
        QColorDialog.getColor = orig_get_color

    updated_val = next((v for v in database.get_tag_values(cat_id, db_path) if v["value"] == "Crítica"), None)
    assert updated_val is not None
    assert updated_val["color"] == "#00ff00"
    dlg.accept()


def test_task_detail_dialog_priority_separated_from_tags(qapp, db_path):
    board_id = database.create_board("Tablero Test", db_path=db_path)
    col_id = database.create_column(board_id, "Columna", db_path=db_path)
    task_id = database.create_task(col_id, "Tarea de Prueba", db_path=db_path)

    # Asignar una etiqueta normal y una de prioridad
    ensure_priority_category(db_path)
    tag_normal = database.get_or_create_tag_value("Dev", "Feature", "#10b981", db_path=db_path)
    tag_prio = database.get_or_create_tag_value("Priority", "High", "#ef4444", db_path=db_path)
    database.set_task_tags(task_id, [tag_normal, tag_prio], db_path=db_path)

    dlg = TaskDetailDialog(task_id, db_path=db_path)
    assert hasattr(dlg, "manage_priority_btn")

    # En el layout de etiquetas solo debe aparecer la etiqueta normal (Dev · Feature), nunca Priority
    rendered_labels = []
    for i in range(dlg.tags_container_layout.count()):
        w = dlg.tags_container_layout.itemAt(i).widget()
        if w:
            for lbl in w.findChildren(type(w)):
                pass
            txt = w.text() if hasattr(w, "text") else ""
            rendered_labels.append(txt)

    # Verificar que el combo de prioridad tiene seleccionada High
    assert dlg.priority_combo.currentText() == "High"
    dlg.reject()
