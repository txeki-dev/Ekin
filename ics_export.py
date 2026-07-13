"""Exporta las tareas de Ekin a un archivo iCalendar (.ics) estándar (RFC 5545).

Cada tarea con fecha de vencimiento se convierte en un evento de día completo, de modo
que el archivo pueda importarse o suscribirse desde Google Calendar, Apple Calendar u
Outlook. Sin dependencias externas: el formato iCalendar es texto plano.
"""
import re
from datetime import datetime, timedelta, timezone

import database


def _escape(text):
    """Escapa un valor de texto para una propiedad iCalendar (RFC 5545 §3.3.11)."""
    if text is None:
        return ""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;").replace(",", "\\,")
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
    return text


def _strip_html(html):
    """Convierte la descripción HTML de una tarea en texto plano razonable."""
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|li)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)  # eliminar el resto de etiquetas
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    # Colapsar líneas en blanco excesivas
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


_SEQ_BASE = datetime(2020, 1, 1)


def _sequence_and_modified(updated_at):
    """Deriva (SEQUENCE, LAST-MODIFIED) del `updated_at` de la tarea.

    SEQUENCE debe crecer cuando el evento cambia: usamos los segundos desde 2020
    (entero monótono y dentro del rango válido). LAST-MODIFIED ayuda a los clientes
    a reconocer que un evento con el mismo UID se ha actualizado.
    """
    if not updated_at:
        return 0, None
    try:
        dt = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return 0, None
    seq = max(0, int((dt - _SEQ_BASE).total_seconds()))
    return seq, dt.strftime("%Y%m%dT%H%M%SZ")


def _fold_line(line):
    """Pliega líneas a 75 octetos con continuación por espacio (RFC 5545 §3.1)."""
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line
    pieces = []
    while len(encoded) > 75:
        cut = 75
        # No partir un carácter UTF-8 multibyte
        while cut > 0 and (encoded[cut] & 0xC0) == 0x80:
            cut -= 1
        pieces.append(encoded[:cut])
        encoded = encoded[cut:]
    pieces.append(encoded)
    return "\r\n ".join(p.decode("utf-8") for p in pieces)


def build_ics(db_path=database.DB_NAME):
    """Construye el contenido .ics (texto) con todas las tareas que tienen due_date."""
    tasks = database.get_scheduled_tasks(db_path=db_path)
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ekin Kanban//Ekin//ES",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Ekin Kanban",
    ]

    for t in tasks:
        try:
            start = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        end = start + timedelta(days=1)  # DTEND es exclusivo en eventos de día completo

        description_parts = [f"Tablero: {t['board_name']}"]
        if t.get("tags"):
            description_parts.append(
                "Etiquetas: " + ", ".join(f"{tag['category']}: {tag['value']}" for tag in t["tags"])
            )
        notes = _strip_html(t.get("description"))
        if notes:
            description_parts.append(notes)

        sequence, last_modified = _sequence_and_modified(t.get("updated_at"))
        # DTSTAMP se deriva del updated_at (no de la hora actual) para que el .ics sea
        # determinista: así solo cambia cuando cambian los datos, y la sincronización a
        # carpetas en la nube no genera subidas espurias.
        stamp = last_modified or now_utc

        event = [
            "BEGIN:VEVENT",
            f"UID:ekin-task-{t['id']}@ekin-kanban",
            f"DTSTAMP:{stamp}",
            f"SEQUENCE:{sequence}",
            f"DTSTART;VALUE=DATE:{start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{end.strftime('%Y%m%d')}",
            f"SUMMARY:{_escape(t['title'] or '(sin título)')}",
            f"DESCRIPTION:{_escape(chr(10).join(description_parts))}",
            f"CATEGORIES:{_escape(t['board_name'])}",
            "TRANSP:TRANSPARENT",
        ]
        if last_modified:
            event.append(f"LAST-MODIFIED:{last_modified}")
        event.append("END:VEVENT")
        lines.extend(event)

    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold_line(line) for line in lines) + "\r\n"


def export_ics(path, db_path=database.DB_NAME):
    """Escribe el archivo .ics en `path`. Devuelve el número de eventos exportados."""
    content = build_ics(db_path=db_path)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)
    return content.count("BEGIN:VEVENT")
