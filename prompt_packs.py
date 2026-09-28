"""
Packs de prompts del AI Prompt Clipboard de cada tablero.

Usan el mismo esquema JSON que AI-Dev-Prompt-Clipboard (una lista de
{id, title, tag, category, color, role, description, prompt}), así que los packs se
pueden intercambiar entre ambas aplicaciones. Los de fábrica viven en
assets/prompt_packs/; los importados por el usuario, en ~/.ekin/prompt_packs/.
Los prompts admiten variables {{nombre}}: las del tablero se rellenan solas y el
resto se piden al copiar.
"""
import json
import os
import re

from mcp_server import claude_code_server_name
from strings import t

_BUILTIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "prompt_packs")
USER_PACKS_DIR = os.path.join(os.path.expanduser("~/.ekin"), "prompt_packs")

DEFAULT_PACK = "dev"
# id del pack de fábrica -> clave de strings.py con su nombre visible
BUILTIN_PACKS = {
    "dev": "prompt_clipboard.pack_dev",
    "opositor": "prompt_clipboard.pack_opositor",
    "gtd": "prompt_clipboard.pack_gtd",
}
_USER_PREFIX = "user:"
_FIELDS = ("id", "title", "tag", "category", "color", "role", "description", "prompt")
_REQUIRED = ("id", "title", "prompt")
_VAR_RE = re.compile(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}")


def list_packs():
    """[(pack_id, nombre visible)]: primero los de fábrica, luego los importados."""
    packs = [(pack_id, t(key)) for pack_id, key in BUILTIN_PACKS.items()]
    if os.path.isdir(USER_PACKS_DIR):
        for name in sorted(os.listdir(USER_PACKS_DIR)):
            stem, ext = os.path.splitext(name)
            if ext.lower() == ".json":
                packs.append((_USER_PREFIX + stem, stem))
    return packs


def resolve_pack_id(pack_id):
    """El pack guardado en el tablero, o el de por defecto si ya no existe (o no hay)."""
    return pack_id if pack_id in {pid for pid, _ in list_packs()} else DEFAULT_PACK


def _pack_path(pack_id):
    if pack_id in BUILTIN_PACKS:
        return os.path.join(_BUILTIN_DIR, f"{pack_id}.json")
    if pack_id.startswith(_USER_PREFIX):
        return os.path.join(USER_PACKS_DIR, pack_id[len(_USER_PREFIX):] + ".json")
    raise ValueError(f"Pack de prompts desconocido: {pack_id}")


def _validate(data):
    """Normaliza una lista de prompts; ValueError si no sigue el esquema del Clipboard."""
    if not isinstance(data, list) or not data:
        raise ValueError(t("prompt_clipboard.import_invalid_list"))
    prompts = []
    for item in data:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip() for k in _REQUIRED):
            raise ValueError(t("prompt_clipboard.import_invalid_item", fields=", ".join(_REQUIRED)))
        prompts.append({k: str(item.get(k) or "") for k in _FIELDS})
    return prompts


def load_pack(pack_id):
    with open(_pack_path(pack_id), encoding="utf-8-sig") as fh:
        return _validate(json.load(fh))


def import_pack(path):
    """Valida un pack JSON (p. ej. exportado de AI-Dev-Prompt-Clipboard), lo guarda entre
    los packs del usuario (sustituye a uno previo del mismo nombre) y devuelve su id."""
    with open(path, encoding="utf-8-sig") as fh:
        try:
            prompts = _validate(json.load(fh))
        except json.JSONDecodeError as exc:
            raise ValueError(str(exc)) from exc
    os.makedirs(USER_PACKS_DIR, exist_ok=True)
    stem = os.path.splitext(os.path.basename(path))[0]
    with open(os.path.join(USER_PACKS_DIR, stem + ".json"), "w", encoding="utf-8") as fh:
        json.dump(prompts, fh, ensure_ascii=False, indent=2)
    return _USER_PREFIX + stem


def find_variables(text):
    """Nombres de las variables {{...}} del texto, en orden de aparición y sin repetir."""
    return list(dict.fromkeys(_VAR_RE.findall(text)))


def fill_variables(text, values):
    """Sustituye las variables con valor en `values`; deja intactas las demás."""
    return _VAR_RE.sub(lambda m: values.get(m.group(1), m.group(0)), text)


def board_variables(board):
    """Variables que se rellenan solas a partir del tablero."""
    return {"board_name": board["name"], "mcp_server": claude_code_server_name(board["name"])}
