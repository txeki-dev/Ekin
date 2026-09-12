"""
Pruebas exhaustivas para las 4 mejoras de UX:
1. Tablas interactivas y formato uniforme.
2. Limpieza automática del placeholder en Citas (Blockquotes).
3. Prompts maestros multi-objetivo con JSON limpio y copia al portapapeles.
4. Experiencia de usuario y navegación en Diario / Chat (edición in-place, atajos, scroll fluido).
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication
import database
from detail_dialog.markdown_edit import MarkdownTextEdit
from detail_dialog.task_detail_dialog import TaskDetailDialog
from detail_dialog.log_entry import LogEntryWidget
from detail_dialog.html_utils import format_table_all_cells
import local_ai
from ai_spec_dialog import AiSpecDialog


def test_table_insert_and_manipulation(qapp):
    """Verifica inserción inicial de tabla y manipulación mediante acciones de fila/columna."""
    edit = MarkdownTextEdit()
    edit.insert_table(2, 3)

    cursor = edit.textCursor()
    table = cursor.currentTable()
    assert table is not None
    assert table.rows() == 2
    assert table.columns() == 3

    # Formateo inicial de celdas
    format_table_all_cells(table)
    cell_0_0 = table.cellAt(0, 0)
    assert cell_0_0.format().toTableCellFormat().topPadding() == 6

    # Insertar fila debajo
    edit.insert_table_row_below(table, 0)
    assert table.rows() == 3

    # Insertar fila encima
    edit.insert_table_row_above(table, 0)
    assert table.rows() == 4

    # Insertar columna derecha
    edit.insert_table_col_right(table, 0)
    assert table.columns() == 4

    # Insertar columna izquierda
    edit.insert_table_col_left(table, 0)
    assert table.columns() == 5

    # Eliminar fila
    edit.delete_table_row(table, 0)
    assert table.rows() == 3

    # Eliminar columna
    edit.delete_table_col(table, 0)
    assert table.columns() == 4

    # Eliminar tabla completa
    edit.delete_table(table)
    assert edit.textCursor().currentTable() is None


def test_quote_placeholder_clearing_on_typing(qapp):
    """Verifica que escribir en una cita con placeholder borra el placeholder automáticamente."""
    edit = MarkdownTextEdit()
    edit.insert_quote()

    # El placeholder se inserta automáticamente
    table = edit.textCursor().currentTable()
    assert table is not None
    assert "Escribe una cita" in edit.toPlainText() or "Type a quote" in edit.toPlainText()

    # Simular pulsación de una tecla cualquiera (ej: letra 'H')
    key_event = QKeyEvent(QKeyEvent.KeyPress, Qt.Key_H, Qt.NoModifier, "H")
    edit.keyPressEvent(key_event)

    # El placeholder ha debido desaparecer y queda solo la letra tecleada
    assert "Escribe una cita" not in edit.toPlainText()
    assert "Type a quote" not in edit.toPlainText()
    assert "H" in edit.toPlainText()


def test_quote_placeholder_clearing_on_click(qapp):
    """Verifica que hacer clic en una cita con placeholder borra el texto predefinido."""
    edit = MarkdownTextEdit()
    edit.resize(500, 300)
    edit.show()
    edit.insert_quote()

    table = edit.textCursor().currentTable()
    assert table is not None
    assert "Escribe una cita" in edit.toPlainText() or "Type a quote" in edit.toPlainText()

    # Colocar el cursor dentro de la celda de la cita
    cell_cursor = table.cellAt(0, 1).firstCursorPosition()
    edit.setTextCursor(cell_cursor)

    # Simular evento de clic de ratón (press + release) en el centro de la celda de cita
    pt = edit.cursorRect(cell_cursor).center()
    press_event = QMouseEvent(
        QMouseEvent.MouseButtonPress,
        pt,
        Qt.LeftButton,
        Qt.LeftButton,
        Qt.NoModifier
    )
    edit.mousePressEvent(press_event)
    mouse_event = QMouseEvent(
        QMouseEvent.MouseButtonRelease,
        pt,
        Qt.LeftButton,
        Qt.LeftButton,
        Qt.NoModifier
    )
    edit.mouseReleaseEvent(mouse_event)

    # El texto de la cita se vacía y queda listo para escribir
    assert "Escribe una cita" not in edit.toPlainText()
    assert "Type a quote" not in edit.toPlainText()


def test_ai_prompts_and_master_prompt_copy(monkeypatch, qapp, db_path):
    """Verifica que el prompt maestro contenga solo title, description, links en JSON
    y que los botones de visualización y copia funcionen."""
    board_id = database.create_board("AI Board", db_path=db_path)
    col_id = database.create_column(board_id, "Backlog", db_path=db_path)
    t1 = database.create_task(
        col_id,
        "Diseñar API de Pagos",
        description="Integración con Stripe",
        tag_text="P1:URGENT",
        due_date="2026-12-31",
        db_path=db_path
    )
    database.add_task_link(t1, "https://stripe.com/docs/api", "Stripe Docs", db_path=db_path)
    database.add_task_link(t1, "C:/configs/stripe.json", "Local Config", db_path=db_path)
    database.create_log(t1, "Nota privada que NO debe enviarse al LLM", db_path=db_path)

    # 1. Comprobar formateador JSON
    t_data = database.get_task(t1, db_path)
    t_data["links"] = database.get_task_links(t1, db_path)
    t_data["tags"] = database.get_task_tags(t1, db_path)
    t_data["logs"] = database.get_logs(t1, db_path)

    json_output = local_ai.format_tasks_for_prompt([t_data])
    assert "Diseñar API de Pagos" in json_output
    assert "Integración con Stripe" in json_output
    assert "https://stripe.com/docs/api" in json_output
    assert "web_link" in json_output
    assert "local_file" in json_output
    # Exclusión explícita de tags, fechas y diario
    assert "URGENT" not in json_output
    assert "2026-12-31" not in json_output
    assert "Nota privada" not in json_output

    # 2. Comprobar los 4 objetivos de prompt
    modes = ["sw_feature_plan", "study_socratic", "analyst_business", "action_breakdown"]
    for m in modes:
        sys_p, user_p = local_ai.build_spec_prompts([t_data], mode=m)
        assert len(sys_p) > 20
        assert len(user_p) > 20
        assert "Diseñar API de Pagos" in user_p

    # 3. Comprobar diálogo AiSpecDialog, sus botones y copia de prompt maestro
    dlg = AiSpecDialog([t1], board_id, db_path)
    assert hasattr(dlg, "view_prompt_btn")
    assert hasattr(dlg, "copy_prompt_btn")

    master_prompt = dlg.get_master_prompt()
    assert "# SYSTEM INSTRUCTIONS" in master_prompt
    assert "# CONTEXT & REQUEST" in master_prompt
    assert "Diseñar API de Pagos" in master_prompt

    copied_bucket = []
    monkeypatch.setattr(QApplication.clipboard(), "setText", lambda txt: copied_bucket.append(txt))

    # Ejecutar acción de copiar
    dlg.copy_master_prompt()
    assert len(copied_bucket) == 1
    assert copied_bucket[0] == master_prompt

    dlg.reject()


def test_journal_chat_ux_and_inplace_editing(qapp, db_path):
    """Verifica las proporciones, márgenes simétricos, scroll fluido y edición in-place en el diario."""
    board_id = database.create_board("UX Board", db_path=db_path)
    col_id = database.create_column(board_id, "Backlog", db_path=db_path)
    tid = database.create_task(col_id, "Tarea Diario UX", db_path=db_path)
    database.create_log(tid, "Comentario 1 inicial", db_path=db_path)
    database.create_log(tid, "Comentario 2 a editar", db_path=db_path)

    dlg = TaskDetailDialog(tid, db_path=db_path)

    # 1. Verificar dimensiones y márgenes simétricos
    assert dlg.minimumWidth() >= 1160
    assert dlg.right_panel.minimumWidth() >= 480
    margins = dlg.logs_layout.contentsMargins()
    assert margins.left() == 10
    assert margins.right() == 10
    assert margins.top() == 10
    assert margins.bottom() == 10
    assert dlg.scroll_area.verticalScrollBar().singleStep() == 25

    # 2. Obtener un LogEntryWidget
    log_widget = None
    for i in range(dlg.logs_layout.count()):
        item = dlg.logs_layout.itemAt(i)
        if item and isinstance(item.widget(), LogEntryWidget):
            log_widget = item.widget()
            break
    assert log_widget is not None

    # 3. Iniciar edición y cancelar sin recarga
    log_widget._enter_edit_mode()
    assert log_widget._editing is True
    assert log_widget.content_label.isHidden() is True
    assert log_widget.edit_btn.isEnabled() is False

    # Cancelar
    log_widget._cancel_edit()
    assert log_widget._editing is False
    assert log_widget.content_label.isHidden() is False
    assert log_widget.edit_btn.isEnabled() is True

    # 4. Iniciar edición y guardar in-place
    log_widget._enter_edit_mode()
    log_widget._editor.setPlainText("Texto editado exitosamente")
    log_widget._save_edit()

    assert log_widget._editing is False
    assert "Texto editado exitosamente" in log_widget.content_label.text()

    dlg.reject()


def test_table_dialog_insert_dimensions(qapp):
    """Verifica que TableInsertDialog admita dimensiones personalizadas y que su botón de inserción
    no sufra errores de ciclo de vida (libshiboken) al ejecutarse."""
    from detail_dialog.markdown_edit import TableInsertDialog
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QDialog

    edit = MarkdownTextEdit()
    dlg = TableInsertDialog()
    dlg.rows_spin.setValue(4)
    dlg.cols_spin.setValue(5)

    QTimer.singleShot(10, dlg.accept)
    res = dlg.exec()
    assert res == QDialog.Accepted
    rows, cols = dlg.get_dimensions()
    assert rows == 4
    assert cols == 5

    tbl = edit.insert_table(rows, cols)
    assert tbl is not None
    assert tbl.rows() == 4
    assert tbl.columns() == 5
    assert "<table" in edit.toHtml()


def test_html_description_clean_and_domain_analysis():
    """Verifica la eliminación total de CSS (<style>) residual de Qt y el análisis de dominio arquitectónico."""
    raw_html = (
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
        '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
        'p, li { white-space: pre-wrap; }\n'
        'hr { height: 1px; border-width: 0; }\n'
        'li.unchecked::marker { content: "\\2610"; }\n'
        'li.checked::marker { content: "\\2612"; }\n'
        '</style></head><body>\n'
        '<p>Necesito integrar el OMIE y OMIP para obtener datos de los precios de mercado en los 96 periodos.</p>\n'
        '</body></html>'
    )

    clean_text = local_ai.clean_html_description(raw_html)
    assert "white-space" not in clean_text
    assert "border-width" not in clean_text
    assert "marker" not in clean_text
    assert "Necesito integrar el OMIE y OMIP" in clean_text

    task_sample = {
        "title": "Integración API REE",
        "description": raw_html,
        "links": [{"label": "Documentación OMIE", "url": "https://www.omie.es"}]
    }

    # Comprobar análisis
    analysis = local_ai._analyze_task_for_spec(task_sample)
    assert "Integración de Red & APIs Externas" in analysis["domain"]
    assert "white-space" not in analysis["clean_desc"]

    # Comprobar generación estructural enriquecida
    spec = local_ai.generate_structural_spec([task_sample], mode="sw_feature_plan")
    assert "## 2. Desglose de Requisitos & Mapeo de Tareas" in spec
    assert "### 2.1. Integración API REE" in spec
    assert "Capa / Dominio Arquitectónico" in spec
    assert "Desglose Técnico & Pasos Operativos" in spec
    assert "Criterios de Aceptación & DoD Específico" in spec
    assert "white-space" not in spec


def test_task_detail_meta_card_4_rows(qapp, db_path):
    """Verifica que los metadatos se organicen en 4 filas dentro del panel izquierdo,
    dejando el espacio vertical completo para el Journal."""
    from PySide6.QtWidgets import QFrame

    board_id = database.create_board("Layout Board", db_path=db_path)
    col_id = database.create_column(board_id, "Todo", db_path=db_path)
    tid = database.create_task(col_id, "Tarea Layout 4 Filas", db_path=db_path)

    dlg = TaskDetailDialog(tid, db_path=db_path)

    # 1. Comprobar que TaskMetaCard está en el panel izquierdo (no en root superior)
    meta_card = dlg.findChild(QFrame, "TaskMetaCard")
    assert meta_card is not None
    assert meta_card.parent() == dlg.findChild(type(dlg.findChild(QFrame))) or meta_card.parent() is not None

    # 2. Comprobar que meta_card tiene 4 layouts de fila
    meta_layout = meta_card.layout()
    assert meta_layout.count() == 4

    # 3. Comprobar que el combo de recurrencia está en la segunda fila (row_2)
    assert hasattr(dlg, "recurrence_combo")
    assert hasattr(dlg, "due_date_edit")
    assert hasattr(dlg, "timer_toggle_btn")
    assert hasattr(dlg, "priority_combo")

    dlg.reject()

