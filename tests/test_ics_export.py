"""Pruebas del exportador iCalendar (.ics): escapado, plegado de líneas,
SEQUENCE/LAST-MODIFIED y la construcción del calendario completo."""
import database
import ics_export


# --- _escape ---

def test_escape_special_characters():
    assert ics_export._escape(None) == ""
    assert ics_export._escape("a;b,c") == "a\\;b\\,c"
    assert ics_export._escape("back\\slash") == "back\\\\slash"
    # Los saltos de línea (en cualquier variante) se convierten en la secuencia \n literal
    assert ics_export._escape("l1\r\nl2\rl3\nl4") == "l1\\nl2\\nl3\\nl4"


# --- _fold_line ---

def _physical_lines(folded):
    return folded.split("\r\n")


def test_fold_line_short_line_is_unchanged():
    line = "SUMMARY:hola"
    assert ics_export._fold_line(line) == line


def test_fold_line_respects_75_octet_limit_including_continuation_space():
    line = "DESCRIPTION:" + "x" * 300
    folded = ics_export._fold_line(line)
    physical = _physical_lines(folded)
    assert len(physical) > 1
    # Cada línea física (incluido el espacio inicial de continuación) <= 75 octetos
    for i, pl in enumerate(physical):
        octets = len(pl.encode("utf-8"))
        assert octets <= 75, (i, octets, pl)
    # Las continuaciones empiezan por un espacio
    for pl in physical[1:]:
        assert pl.startswith(" ")
    # Se puede reconstruir la línea original quitando los CRLF+espacio de continuación
    rebuilt = physical[0] + "".join(pl[1:] for pl in physical[1:])
    assert rebuilt == line


def test_fold_line_never_splits_a_multibyte_character():
    line = "SUMMARY:" + "áéíóú" * 40  # cada carácter ocupa 2 octetos en UTF-8
    folded = ics_export._fold_line(line)
    # No debe lanzar y cada trozo ha de decodificar correctamente (implícito al no fallar)
    for pl in _physical_lines(folded):
        assert len(pl.encode("utf-8")) <= 75


# --- _sequence_and_modified ---

def test_sequence_and_modified():
    assert ics_export._sequence_and_modified(None) == (0, None)
    assert ics_export._sequence_and_modified("no es fecha") == (0, None)
    seq0, mod0 = ics_export._sequence_and_modified("2020-01-01 00:00:00")
    assert seq0 == 0 and mod0 == "20200101T000000Z"
    seq1, mod1 = ics_export._sequence_and_modified("2020-01-01 00:01:00")
    assert seq1 == 60 and mod1 == "20200101T000100Z"


# --- build_ics (contra una BD temporal) ---

def _make_task(db_path, title="Tarea", due_date="2026-07-22"):
    bid = database.create_board("Tablero", db_path=db_path)
    cid = database.create_column(bid, "Col", db_path=db_path)
    return database.create_task(cid, title, due_date=due_date, db_path=db_path)


def test_build_ics_all_day_event_shape(db_path):
    task_id = _make_task(db_path, title="Entrega", due_date="2026-07-22")
    content = ics_export.build_ics(db_path)

    assert content.startswith("BEGIN:VCALENDAR\r\n")
    assert content.rstrip().endswith("END:VCALENDAR")
    assert content.count("BEGIN:VEVENT") == 1
    # Evento de día completo: DTEND es el día siguiente (exclusivo)
    assert "DTSTART;VALUE=DATE:20260722" in content
    assert "DTEND;VALUE=DATE:20260723" in content
    # UID estable y ligado al id de la tarea
    assert f"UID:ekin-task-{task_id}@ekin-kanban" in content


def test_build_ics_escapes_summary(db_path):
    _make_task(db_path, title="A, B; C", due_date="2026-07-22")
    content = ics_export.build_ics(db_path)
    assert "SUMMARY:A\\, B\\; C" in content


def test_build_ics_skips_tasks_without_due_date(db_path):
    bid = database.create_board("T", db_path=db_path)
    cid = database.create_column(bid, "C", db_path=db_path)
    database.create_task(cid, "Sin fecha", db_path=db_path)
    content = ics_export.build_ics(db_path)
    assert content.count("BEGIN:VEVENT") == 0


# --- Hora de vencimiento + VALARM + feed por tablero (v0.6.0) ---

def test_build_ics_timed_event_with_valarm(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path)
    t = database.create_task(c, "Reunión", due_date="2026-08-01", db_path=db_path)
    database.set_task_due_time(t, "09:30", db_path=db_path)

    content = ics_export.build_ics(db_path)
    assert "DTSTART:20260801T093000" in content        # evento con hora (no VALUE=DATE)
    assert "DTEND:20260801T103000" in content          # +1 h
    assert "BEGIN:VALARM" in content and "TRIGGER:-PT15M" in content


def test_build_ics_all_day_when_no_time(db_path):
    b = database.create_board("B", db_path=db_path)
    c = database.create_column(b, "C", db_path=db_path)
    database.create_task(c, "Todo el día", due_date="2026-08-02", db_path=db_path)
    content = ics_export.build_ics(db_path)
    assert "DTSTART;VALUE=DATE:20260802" in content
    assert "BEGIN:VALARM" not in content


def test_build_ics_per_board_filter(db_path):
    b1 = database.create_board("B1", db_path=db_path)
    c1 = database.create_column(b1, "C", db_path=db_path)
    b2 = database.create_board("B2", db_path=db_path)
    c2 = database.create_column(b2, "C", db_path=db_path)
    database.create_task(c1, "Tarea B1", due_date="2026-08-01", db_path=db_path)
    database.create_task(c2, "Tarea B2", due_date="2026-08-01", db_path=db_path)

    only_b1 = ics_export.build_ics(db_path, board_id=b1)
    assert "Tarea B1" in only_b1 and "Tarea B2" not in only_b1
    assert only_b1.count("BEGIN:VEVENT") == 1
