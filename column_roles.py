"""
Rol de cada columna en el flujo del tablero (backlog, ready, in_progress, review, done u other),
deducido de su nombre. Lo usan el resumen ejecutivo del MCP y las reglas que dependen del flujo
(p. ej. quitar la fecha al pasar a Done), para que agentes y prompts no tengan que adivinarlo.
"""
import re
import unicodedata

BACKLOG = "backlog"
READY = "ready"
IN_PROGRESS = "in_progress"
REVIEW = "review"
DONE = "done"
OTHER = "other"

# En orden de precedencia: "Revisión pendiente" es review, no backlog. Cada clave es el prefijo
# de una palabra del nombre (sin acentos); las de varias palabras deben aparecer seguidas.
_KEYWORDS = (
    (DONE, ("done", "hecho", "shipped", "completad", "completed", "terminad", "cerrad", "closed",
            "resuelt", "resolved", "finaliz", "finished", "dominad")),
    (REVIEW, ("review", "revision", "qa", "test", "validac", "verificac")),
    (IN_PROGRESS, ("progres", "curso", "doing", "haciendo", "wip", "activo", "desarrollo")),
    (READY, ("ready", "listo", "next", "proxim", "selected", "seleccionad")),
    (BACKLOG, ("backlog", "triage", "inbox", "bandeja", "pendiente", "todo", "to do", "por hacer")),
)


def _words(name):
    plain = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", plain)


def classify_column(name):
    """Rol de una columna según su nombre; OTHER si ninguna palabra clave encaja."""
    words = _words(name)
    joined = f" {' '.join(words)} "
    for role, keys in _KEYWORDS:
        for key in keys:
            if (f" {key} " in joined) if " " in key else any(w.startswith(key) for w in words):
                return role
    return OTHER


def column_roles(columns):
    """{column_id: rol} para las columnas de un tablero (en orden de `position`). Si ninguna
    se reconoce como backlog, la primera sin rol hace de backlog. Done no tiene ese respaldo:
    solo se considera Done una columna que lo diga en su nombre."""
    ordered = sorted(columns, key=lambda c: c["position"])
    roles = {c["id"]: classify_column(c["name"]) for c in ordered}
    if ordered and BACKLOG not in roles.values() and roles[ordered[0]["id"]] == OTHER:
        roles[ordered[0]["id"]] = BACKLOG
    return roles
