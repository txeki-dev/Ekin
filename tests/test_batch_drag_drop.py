"""Pruebas unitarias para la funcionalidad de Multi-Card Batch Drag-and-Drop (Iniciativa #52).
Cubre:
1. Cálculo de índice de inserción con exclusión múltiple (compute_drop_index).
2. Generación del visual stack pixmap y badge numérico en TaskCard.
3. Eventos de arrastre y soltado en lote en TaskListArea con MIME JSON.
4. Recolocación atómica en lote a través de BoardViewWidget.handle_task_drop.
5. Soporte integral de Undo/Redo para movimientos en lote.
6. Soltado en lote sobre columnas plegadas (despliegue automático y colocación al final).
"""

import json
from PySide6.QtCore import Qt, QMimeData, QPointF
from PySide6.QtGui import QDropEvent, QDragEnterEvent
import database
from undo import UndoManager
from board_view import BoardViewWidget
from widgets import TaskCard, TaskListArea, compute_drop_index


def test_compute_drop_index_multi_card():
    """Verifica que compute_drop_index excluya todas las tareas del lote para evitar off-by-one."""
    cards_geom = [
        (101, 0, 50),
        (102, 60, 50),
        (103, 120, 50),
        (104, 180, 50),
    ]
    # Arrastrando tareas 102 y 103 (quedan 101 a y=0..50 y 104 a y=180..230)
    # Soltar en y = 200 (después de 104)
    idx_end = compute_drop_index(cards_geom, 220, [102, 103])
    assert idx_end == 2  # Debe haber 2 tarjetas en el espacio resultante: [101, 104]

    # Soltar en y = 10 (antes de 101)
    idx_start = compute_drop_index(cards_geom, 10, [102, 103])
    assert idx_start == 0

    # Soltar entre 101 y 104 (ej. y = 100)
    idx_mid = compute_drop_index(cards_geom, 100, [102, 103])
    assert idx_mid == 1


def test_task_card_drag_pixmap_badge(qapp):
    """Verifica que _create_drag_pixmap genere una imagen con dimensiones válidas para lotes."""
    task_data = {"id": 1, "column_id": 10, "title": "Test Task", "description": "", "tag_text": "", "due_date": None}
    card = TaskCard(task_data)
    card.resize(260, 80)

    # Vista previa individual
    pix_single = card._create_drag_pixmap(1)
    assert not pix_single.isNull()
    assert pix_single.width() > 0

    # Vista previa en lote (3 tarjetas)
    pix_batch = card._create_drag_pixmap(3)
    assert not pix_batch.isNull()
    # Debe ser más ancha/alta debido al apilamiento 3D y badge
    assert pix_batch.width() >= pix_single.width()


def test_task_list_area_batch_drop_event(qapp):
    """Verifica que TaskListArea emita batch_tasks_dropped cuando se suelta un payload JSON con múltiples IDs."""
    area = TaskListArea(column_id=25)
    area.resize(280, 400)

    # 1. Drop con múltiples IDs
    mime_batch = QMimeData()
    mime_batch.setData("application/x-ekin-tasks-json", json.dumps([11, 12, 13]).encode("utf-8"))
    mime_batch.setData("application/x-ekin-task-id", b"11")

    # Enter
    enter_ev = QDragEnterEvent(QPointF(10, 10).toPoint(), Qt.MoveAction, mime_batch, Qt.LeftButton, Qt.NoModifier)
    area.dragEnterEvent(enter_ev)
    assert enter_ev.isAccepted()
    assert area._drop_indicator is not None

    # Drop
    batch_received = []
    single_received = []
    area.batch_tasks_dropped.connect(lambda tids, cid, pos: batch_received.append((tids, cid, pos)))
    area.task_dropped.connect(lambda tid, cid, pos: single_received.append((tid, cid, pos)))

    drop_ev = QDropEvent(QPointF(10, 100).toPoint(), Qt.MoveAction, mime_batch, Qt.LeftButton, Qt.NoModifier)
    area.dropEvent(drop_ev)

    assert len(batch_received) == 1
    assert batch_received[0][0] == [11, 12, 13]
    assert batch_received[0][1] == 25
    assert len(single_received) == 0

    # 2. Drop con un solo ID en el JSON
    mime_single = QMimeData()
    mime_single.setData("application/x-ekin-tasks-json", json.dumps([42]).encode("utf-8"))
    drop_single_ev = QDropEvent(QPointF(10, 50).toPoint(), Qt.MoveAction, mime_single, Qt.LeftButton, Qt.NoModifier)
    area.dropEvent(drop_single_ev)

    assert len(single_received) == 1
    assert single_received[0][0] == 42


def test_board_view_batch_task_drop_across_columns_and_incremental(qapp, db_path):
    """Verifica la recolocación en lote entre columnas: atomicidad DB y renderizado incremental."""
    board_id = database.create_board("Tablero Batch", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Col A", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Col B", "#10b981", db_path)
    col_c = database.create_column(board_id, "Col C", "#f59e0b", db_path)

    t1 = database.create_task(col_a, "Tarea 1", db_path=db_path)
    t2 = database.create_task(col_a, "Tarea 2", db_path=db_path)
    t3 = database.create_task(col_a, "Tarea 3", db_path=db_path)
    tb1 = database.create_task(col_b, "Tarea B1", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    widget_c_before = bv.column_widgets[col_c]
    widget_a_before = bv.column_widgets[col_a]
    widget_b_before = bv.column_widgets[col_b]

    # Mover [t1, t2] de Col A a Col B en la posición 0
    bv.handle_task_drop([t1, t2], col_b, 0)

    # Col C no debe haber sido tocada
    assert bv.column_widgets[col_c] is widget_c_before
    # Col A y B deben haberse reconstruido
    assert bv.column_widgets[col_a] is not widget_a_before
    assert bv.column_widgets[col_b] is not widget_b_before

    # Verificar posiciones en DB
    tasks_a = database.get_tasks(col_a, db_path)
    tasks_b = database.get_tasks(col_b, db_path)

    assert len(tasks_a) == 1
    assert tasks_a[0]["id"] == t3
    assert tasks_a[0]["position"] == 0

    assert len(tasks_b) == 3
    assert tasks_b[0]["id"] == t1
    assert tasks_b[0]["position"] == 0
    assert tasks_b[1]["id"] == t2
    assert tasks_b[1]["position"] == 1
    assert tasks_b[2]["id"] == tb1
    assert tasks_b[2]["position"] == 2


def test_board_view_batch_task_drop_same_column(qapp, db_path):
    """Verifica el reordenamiento en lote dentro de la misma columna."""
    board_id = database.create_board("Tablero Reorder", "#3b82f6", db_path)
    col = database.create_column(board_id, "Desarrollo", "#3b82f6", db_path)

    t1 = database.create_task(col, "T1", db_path=db_path)
    t2 = database.create_task(col, "T2", db_path=db_path)
    t3 = database.create_task(col, "T3", db_path=db_path)
    t4 = database.create_task(col, "T4", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    # Mover [t1, t2] al final de la columna (tras t3 y t4)
    bv.handle_task_drop([t1, t2], col, 2)

    tasks = database.get_tasks(col, db_path)
    assert [t["id"] for t in tasks] == [t3, t4, t1, t2]
    assert [t["position"] for t in tasks] == [0, 1, 2, 3]


def test_batch_move_undo_and_redo(qapp, db_path):
    """Verifica que el movimiento en lote registre acción deshacer/rehacer y restaure columnas."""
    board_id = database.create_board("Tablero Undo Batch", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Origen", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Destino", "#10b981", db_path)

    t1 = database.create_task(col_a, "Task A1", db_path=db_path)
    t2 = database.create_task(col_a, "Task A2", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    undo_mgr = UndoManager()
    bv.undo_manager = undo_mgr
    bv.load_board(board_id)

    assert not undo_mgr.can_undo()

    # Mover lote de 2 tareas
    bv.handle_task_drop([t1, t2], col_b, 0)
    assert undo_mgr.can_undo()

    # Verificar que están en destino
    assert len(database.get_tasks(col_b, db_path)) == 2
    assert len(database.get_tasks(col_a, db_path)) == 0

    # Ejecutar UNDO
    undo_label = undo_mgr.undo()
    assert "2" in undo_label or "tarea" in undo_label.lower() or "task" in undo_label.lower()

    # Deben haber regresado a la columna origen
    tasks_a_restored = database.get_tasks(col_a, db_path)
    assert len(tasks_a_restored) == 2
    assert [t["id"] for t in tasks_a_restored] == [t1, t2]
    assert len(database.get_tasks(col_b, db_path)) == 0

    # Ejecutar REDO
    undo_mgr.redo()
    assert len(database.get_tasks(col_b, db_path)) == 2
    assert len(database.get_tasks(col_a, db_path)) == 0


def test_collapsed_column_batch_drop(qapp, db_path):
    """Soltar un lote sobre una columna plegada debe desplegarla y colocar todas las tareas al final."""
    board_id = database.create_board("Tablero Collapsed Batch", "#3b82f6", db_path)
    col_a = database.create_column(board_id, "Col Activa", "#3b82f6", db_path)
    col_b = database.create_column(board_id, "Col Plegada", "#10b981", db_path)
    database.set_column_collapsed(col_b, True, db_path)

    t1 = database.create_task(col_a, "Card 1", db_path=db_path)
    t2 = database.create_task(col_a, "Card 2", db_path=db_path)
    existing_b = database.create_task(col_b, "Existing B", db_path=db_path)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)

    # Simular drop de lote en la columna plegada
    col_b_widget = bv.column_widgets[col_b]
    assert col_b_widget.collapsed

    mime = QMimeData()
    mime.setData("application/x-ekin-tasks-json", json.dumps([t1, t2]).encode("utf-8"))
    drop_ev = QDropEvent(QPointF(10, 20).toPoint(), Qt.MoveAction, mime, Qt.LeftButton, Qt.NoModifier)
    col_b_widget.dropEvent(drop_ev)

    # Columna B debe haberse desplegado en la BD
    assert not database.get_column(col_b, db_path)["collapsed"]

    # Las tareas t1 y t2 deben estar en Col B tras existing_b
    tasks_b = database.get_tasks(col_b, db_path)
    assert len(tasks_b) == 3
    assert [t["id"] for t in tasks_b] == [existing_b, t1, t2]
