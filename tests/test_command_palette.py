"""Pruebas headless de la paleta de comandos (command_palette.py):
filtrado de comandos, captura rápida (+), búsqueda de tareas y emisión de señales."""
import database
from command_palette import CommandPalette

COMMANDS = [
    ("new_task", "New task"),
    ("calendar", "Open Calendar"),
    ("settings", "Open Settings"),
]


def _rows(palette, object_name):
    # palette._rows es la lista autoritativa de filas actuales (evita widgets viejos aún
    # pendientes de deleteLater, que findChildren sí devolvería en un test sin event loop).
    return [btn for (btn, _) in palette._rows if btn.objectName() == object_name]


def test_palette_lists_all_commands_when_empty(qapp, db_path):
    palette = CommandPalette(db_path, COMMANDS)
    labels = [b.text() for b in _rows(palette, "CommandItem")]
    assert labels == ["New task", "Open Calendar", "Open Settings"]


def test_palette_filters_commands_by_query(qapp, db_path):
    palette = CommandPalette(db_path, COMMANDS)
    palette.input.setText("open cal")
    labels = [b.text() for b in _rows(palette, "CommandItem")]
    assert labels == ["Open Calendar"]


def test_palette_command_click_emits_command_invoked(qapp, db_path):
    palette = CommandPalette(db_path, COMMANDS)
    palette.input.setText("settings")
    captured = []
    palette.command_invoked.connect(captured.append)
    _rows(palette, "CommandItem")[0].click()
    assert captured == ["settings"]


def test_palette_quick_capture(qapp, db_path):
    palette = CommandPalette(db_path, COMMANDS)
    palette.input.setText("+ Buy milk")
    rows = _rows(palette, "CommandItem")
    assert len(rows) == 1  # solo la fila de captura: ni comandos de la app ni tareas
    captured = []
    palette.quick_capture_requested.connect(captured.append)
    rows[0].click()
    assert captured == ["Buy milk"]


def test_palette_task_search_click_emits_task_activated(qapp, db_path):
    board_id = database.create_board("Proyecto", db_path=db_path)
    col_id = database.create_column(board_id, "To do", db_path=db_path)
    task_id = database.create_task(col_id, "Alpha release", db_path=db_path)

    palette = CommandPalette(db_path, COMMANDS)
    palette.input.setText("Alpha")
    task_rows = _rows(palette, "NotificationItem")
    assert len(task_rows) == 1

    captured = []
    palette.task_activated.connect(lambda tid, bid: captured.append((tid, bid)))
    task_rows[0].click()
    assert captured == [(task_id, board_id)]
