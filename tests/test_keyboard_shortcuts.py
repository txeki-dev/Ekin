import database
import board_view as board_view_module
from board_view import BoardViewWidget
from sidebar import SidebarWidget


# --- SidebarWidget.select_board_by_index (Ctrl+1..Ctrl+9) ---

def test_select_board_by_index_selects_matching_board(qapp, db_path):
    board_ids = [database.create_board(f"B{i}", db_path=db_path) for i in range(3)]

    sidebar = SidebarWidget(db_path=db_path)  # __init__ ya llama a reload_boards()
    assert list(sidebar.board_buttons.keys()) == board_ids

    for i, board_id in enumerate(board_ids):
        sidebar.select_board_by_index(i)
        assert sidebar.active_board_id == board_id


def test_select_board_by_index_out_of_range_is_noop(qapp, db_path):
    board_ids = [database.create_board(f"B{i}", db_path=db_path) for i in range(3)]
    sidebar = SidebarWidget(db_path=db_path)
    sidebar.select_board_by_index(0)
    assert sidebar.active_board_id == board_ids[0]

    sidebar.select_board_by_index(5)  # más allá del último tablero
    assert sidebar.active_board_id == board_ids[0]

    sidebar.select_board_by_index(-1)  # no debe interpretarse como "el último" (indexado Python)
    assert sidebar.active_board_id == board_ids[0]


def test_select_board_by_index_each_digit_maps_to_a_different_board(qapp, db_path):
    """Regresión específica contra el bug de captura tardía de variable de bucle: las 9
    lambdas Ctrl+1..Ctrl+9 de main.py deben apuntar cada una a un índice distinto."""
    board_ids = [database.create_board(f"B{i}", db_path=db_path) for i in range(5)]
    sidebar = SidebarWidget(db_path=db_path)

    selected = []
    for i in range(len(board_ids)):
        sidebar.select_board_by_index(i)
        selected.append(sidebar.active_board_id)

    assert selected == board_ids
    assert len(set(selected)) == len(board_ids)  # todas distintas, ninguna repetida


# --- BoardViewWidget.add_column guard (Ctrl+Shift+N) ---

def test_add_column_shortcut_noop_when_no_board_selected(qapp, db_path, monkeypatch):
    """Ctrl+Shift+N ya no está protegido por la visibilidad del botón "+ Añadir Columna":
    add_column() debe autoprotegerse cuando board_id == -1 (pantalla de bienvenida)."""
    board_id = database.create_board("B", db_path=db_path)

    class _NeverOpen:
        def __init__(self, *args, **kwargs):
            raise AssertionError(
                "ColumnEditDialog no debe construirse cuando no hay tablero seleccionado"
            )

    monkeypatch.setattr(board_view_module, "ColumnEditDialog", _NeverOpen)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(-1)  # pantalla de bienvenida: board_id queda en -1

    bv.add_column()  # no debe intentar abrir el diálogo (lanzaría AssertionError si lo hiciera)

    assert database.get_columns(board_id, db_path) == []


def test_add_column_shortcut_works_normally_with_board_selected(qapp, db_path, monkeypatch):
    """El fix del guard no debe bloquear el caso normal: con un tablero real seleccionado,
    add_column() sigue abriendo el diálogo y creando la columna como antes."""
    from PySide6.QtWidgets import QDialog

    board_id = database.create_board("B", db_path=db_path)

    class _AutoAccept:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return QDialog.Accepted

        def get_data(self):
            return "Nueva columna", "#3b82f6"

    monkeypatch.setattr(board_view_module, "ColumnEditDialog", _AutoAccept)

    bv = BoardViewWidget(db_path=db_path)
    bv.load_board(board_id)
    bv.add_column()

    cols = database.get_columns(board_id, db_path)
    assert len(cols) == 1
    assert cols[0]["name"] == "Nueva columna"


# --- SidebarWidget._build_utility_bar: reloj y botones en dos filas ---

def test_utility_bar_widgets_survive_two_row_layout(qapp, db_path):
    """La reestructuración en dos filas (reloj arriba, iconos abajo) no debe perder
    ni renombrar ningún widget/atributo, tooltip o comportamiento existente."""
    sidebar = SidebarWidget(db_path=db_path)

    for attr in ("clock_label", "bell_btn", "bell_badge", "search_btn",
                 "calendar_btn", "settings_btn", "shortcuts_btn"):
        assert hasattr(sidebar, attr), f"falta el atributo {attr} tras reestructurar la barra"

    from strings import t
    assert sidebar.search_btn.toolTip() == t("sidebar.search_tooltip")
    assert sidebar.calendar_btn.toolTip() == t("sidebar.calendar_tooltip")
    assert sidebar.settings_btn.toolTip() == t("sidebar.settings_tooltip")
    assert sidebar.shortcuts_btn.toolTip() == t("sidebar.shortcuts_tooltip")

    for btn in (sidebar.bell_btn, sidebar.search_btn, sidebar.calendar_btn,
                sidebar.settings_btn, sidebar.shortcuts_btn):
        assert btn.size().width() == 34
        assert btn.size().height() == 28


def test_utility_bar_clock_is_on_its_own_row_above_the_icons(qapp, db_path):
    """El reloj debe estar en una fila propia (fila 0 del layout exterior), separada
    de la fila que agrupa los botones de icono."""
    sidebar = SidebarWidget(db_path=db_path)
    bar = sidebar.clock_label.parentWidget()
    outer_layout = bar.layout()

    # Fila 0: el propio clock_label como item directo del layout exterior.
    assert outer_layout.itemAt(0).widget() is sidebar.clock_label

    # Fila 1: un sub-layout (no un widget) que contiene los botones de icono.
    second_item = outer_layout.itemAt(1)
    assert second_item.widget() is None
    icons_row = second_item.layout()
    assert icons_row is not None
    icon_widgets = [
        icons_row.itemAt(i).widget()
        for i in range(icons_row.count())
        if icons_row.itemAt(i).widget() is not None
    ]
    assert sidebar.search_btn in icon_widgets
    assert sidebar.calendar_btn in icon_widgets
    assert sidebar.settings_btn in icon_widgets
    assert sidebar.shortcuts_btn in icon_widgets
