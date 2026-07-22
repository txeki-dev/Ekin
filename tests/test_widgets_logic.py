"""Pruebas de lógica pura de la UI que no requieren un bucle de eventos Qt:
el cálculo del índice de inserción en el arrastre de tarjetas."""
from widgets import compute_drop_index


# Tres tarjetas apiladas verticalmente: id -> (y, height). Altura 100, sin separación.
#   A(id=1): y=0..100   (medio 50)
#   B(id=2): y=100..200 (medio 150)
#   C(id=3): y=200..300 (medio 250)
GEOM = [(1, 0, 100), (2, 100, 100), (3, 200, 100)]


def test_drop_above_first_card_inserts_at_zero():
    assert compute_drop_index(GEOM, drop_y=10, dragged_id=99) == 0


def test_drop_at_end_inserts_after_last():
    assert compute_drop_index(GEOM, drop_y=290, dragged_id=99) == 3


def test_dragging_first_card_down_is_not_off_by_one():
    """Arrastrar A (id=1) y soltarla justo debajo de B debe dar el índice 1 en el
    espacio SIN A -> orden final B, A, C. Con el bug anterior (contando A) daba 2."""
    # A está oculta durante el arrastre; su hueco no cuenta. Espacio no arrastrado: [B, C].
    # Soltar por debajo del medio de B (150) y por encima del medio de C (250) -> índice 1.
    assert compute_drop_index(GEOM, drop_y=180, dragged_id=1) == 1


def test_dragging_card_excludes_itself_from_count():
    # Soltar C (id=3) al principio -> índice 0 en el espacio [A, B]
    assert compute_drop_index(GEOM, drop_y=5, dragged_id=3) == 0
    # Soltar C entre A y B -> índice 1
    assert compute_drop_index(GEOM, drop_y=120, dragged_id=3) == 1
