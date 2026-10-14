"""Pruebas del clasificador de roles de columna (column_roles.py) sobre las plantillas de fábrica."""
import pytest

import column_roles as cr
import templates


def _roles_of(template):
    return [cr.classify_column(c.name) for c in template.columns]


def test_software_agile_template_roles():
    assert _roles_of(templates.TEMPLATE_SOFTWARE_AGILE) == [
        cr.BACKLOG, cr.READY, cr.IN_PROGRESS, cr.REVIEW, cr.DONE,
    ]


def test_gtd_template_roles():
    assert _roles_of(templates.TEMPLATE_GTD_PERSONAL) == [
        cr.BACKLOG, cr.READY, cr.OTHER, cr.OTHER, cr.DONE,
    ]


def test_opositor_template_roles():
    assert _roles_of(templates.TEMPLATE_OPOSITOR) == [
        cr.BACKLOG, cr.OTHER, cr.OTHER, cr.OTHER, cr.REVIEW, cr.DONE,
    ]


def test_getting_started_template_roles():
    assert _roles_of(templates.TEMPLATE_GETTING_STARTED) == [
        cr.OTHER, cr.IN_PROGRESS, cr.OTHER, cr.DONE,
    ]


@pytest.mark.parametrize("name, role", [
    ("Por hacer", cr.BACKLOG),
    ("Hecho", cr.DONE),
    ("Revisión pendiente", cr.REVIEW),
    ("Pending Review", cr.REVIEW),
    ("En curso", cr.IN_PROGRESS),
    ("Proactivo", cr.OTHER),  # prefijo de palabra, no subcadena
    ("Aquarius", cr.OTHER),
    ("", cr.OTHER),
])
def test_classify_column_names(name, role):
    assert cr.classify_column(name) == role


def test_column_roles_first_column_falls_back_to_backlog_but_done_needs_a_name():
    cols = [
        {"id": 7, "name": "Ideas", "position": 0},
        {"id": 8, "name": "Doing", "position": 1},
        {"id": 9, "name": "Fin", "position": 2},
    ]
    assert cr.column_roles(cols) == {7: cr.BACKLOG, 8: cr.IN_PROGRESS, 9: cr.OTHER}


def test_column_roles_keeps_named_backlog():
    cols = [
        {"id": 1, "name": "Ideas", "position": 0},
        {"id": 2, "name": "Backlog", "position": 1},
    ]
    assert cr.column_roles(cols) == {1: cr.OTHER, 2: cr.BACKLOG}
