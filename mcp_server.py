"""
Servidor MCP (Model Context Protocol) para Ekin Kanban.

Permite a agentes de IA externos (Claude Code, Antigravity, Cursor, etc.) interactuar
de forma bidireccional y segura con un tablero específico de Ekin mediante el estándar MCP.

Principios de Seguridad y Aislamiento:
1. Sandboxing Estricto: El servidor solo expone y permite operar sobre el tablero
   configurado mediante su `board_uuid` y `mcp_token`. Ningún otro tablero o ajuste de Ekin
   es accesible ni visible para el agente.
2. Inmutabilidad de Columnas ("Human-Only"): Las columnas son sagradas para el usuario humano.
   El agente no puede crear, renombrar, reordenar ni borrar columnas.
3. Trazabilidad & Auditoría: Todo comentario o cambio realizado por el agente se registra
   en el historial con autoría explícita `[Agente IA]`.
4. Protocolo Dual: Soporta tanto transporte HTTP/SSE (estándar MCP) como llamadas JSON-RPC directas.
"""

from __future__ import annotations

import html
import json
import logging
import queue
import re
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import database
from html_utils import clean_html_description

logger = logging.getLogger("ekin.mcp")

DEFAULT_MCP_PORT = 8765
MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "ekin-kanban-mcp"
SERVER_VERSION = "1.0.2"
MAX_MCP_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB limit for DoS mitigation

try:
    from PySide6.QtCore import QObject, Signal

    class McpEventBus(QObject):
        """Emite señales Qt cuando el agente IA modifica datos a través de MCP."""
        board_mutated = Signal(int)  # board_id

except ImportError:
    class _DummySignal:
        def emit(self, *args, **kwargs):
            pass

        def connect(self, *args, **kwargs):
            pass

    class McpEventBus:  # type: ignore
        """Fallback sin interfaz gráfica Qt cuando se ejecuta en entornos headless puros."""
        def __init__(self):
            self.board_mutated = _DummySignal()


_event_bus: Optional[McpEventBus] = None


def get_mcp_event_bus() -> McpEventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = McpEventBus()
    return _event_bus


# --- VALIDADOR DE ACCESO Y SANDBOX ---

class McpSecurityError(Exception):
    """Excepción para violaciones de acceso, tokens inválidos o intentos fuera de sandbox."""
    pass


class McpPermissionDenied(Exception):
    """Excepción para operaciones bloqueadas para agentes IA (como alterar columnas)."""
    pass


def authenticate_and_get_board(board_uuid: str, token: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Valida que el tablero exista, tenga MCP activado y que el token coincida si está configurado."""
    if not board_uuid:
        raise McpSecurityError("Se requiere 'board_uuid' para autenticar la conexión MCP.")

    board = database.get_board_by_uuid(board_uuid, db_path=db_path)
    if not board:
        raise McpSecurityError(f"Tablero con UUID '{board_uuid}' no encontrado.")

    if not board.get("mcp_enabled"):
        raise McpSecurityError(f"El acceso MCP está desactivado por el usuario para el tablero '{board['name']}'.")

    expected_secret = board.get("mcp_secret")
    if expected_secret:
        if not token or not secrets.compare_digest(token, expected_secret):
            raise McpSecurityError("Token secreto de autenticación MCP inválido o no proporcionado.")

    return board


# --- DEFINICIÓN DE HERRAMIENTAS (MCP TOOLS) ---

def get_mcp_tools_schema() -> List[Dict[str, Any]]:
    """Retorna la especificación JSON-Schema de las herramientas expuestas por Ekin Kanban."""
    return [
        {
            "name": "get_board_info",
            "description": "Obtiene información general del tablero: nombre, color, columnas activas y resumen de tareas.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "list_columns",
            "description": "Lista todas las columnas del tablero en su orden visual con sus IDs y límites WIP.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        {
            "name": "list_tasks",
            "description": "Lista las tarjetas/tareas del tablero, opcionalmente filtradas por columna o etiqueta.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "column_id": {"type": "integer", "description": "ID de la columna para filtrar tareas."},
                    "tag": {"type": "string", "description": "Nombre de la etiqueta para filtrar."},
                },
            },
        },
        {
            "name": "get_task",
            "description": "Obtiene todos los detalles de una tarea: título, descripción Markdown, tags, fechas, checklist, links e historial de logs.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID único de la tarea."},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "create_task",
            "description": "Crea una nueva tarjeta de tarea dentro de una de las columnas del tablero.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "column_id": {"type": "integer", "description": "ID de la columna donde se ubicará la tarea."},
                    "title": {"type": "string", "description": "Título breve y descriptivo de la tarea."},
                    "description": {"type": "string", "description": "Descripción detallada en formato Markdown."},
                    "due_date": {"type": "string", "description": "Fecha de vencimiento en formato ISO (YYYY-MM-DD)."},
                    "priority": {"type": "string", "description": "Prioridad sugerida (ej. 'High', 'Medium', 'Low', 'P0-Critical')."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Lista de nombres de etiquetas a asociar."},
                },
                "required": ["column_id", "title"],
            },
        },
        {
            "name": "update_task",
            "description": "Modifica el título, descripción, fecha de vencimiento, prioridad o etiquetas de una tarea.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea a actualizar."},
                    "title": {"type": "string", "description": "Nuevo título."},
                    "description": {"type": "string", "description": "Nueva descripción en Markdown."},
                    "due_date": {"type": "string", "description": "Nueva fecha de vencimiento (YYYY-MM-DD o vacío para quitar)."},
                    "priority": {"type": "string", "description": "Nueva prioridad."},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Nueva lista de etiquetas."},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "move_task",
            "description": "Mueve una tarea de una columna a otra o cambia su posición. Por defecto se ubica en la parte superior (posición 0, más reciente arriba).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea a desplazar."},
                    "target_column_id": {"type": "integer", "description": "ID de la columna de destino."},
                    "target_position": {"type": "integer", "description": "Posición ordinal en la columna (opcional, por defecto 0 para situarla arriba del todo)."},
                },
                "required": ["task_id", "target_column_id"],
            },
        },
        {
            "name": "add_task_comment",
            "description": "Añade una nota o comentario al diario/historial de la tarea. Se marcará con autoría IA.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                    "comment": {"type": "string", "description": "Contenido de la nota o comentario en Markdown."},
                },
                "required": ["task_id", "comment"],
            },
        },
        {
            "name": "list_task_comments",
            "description": "Consulta todas las notas y entradas de diario registradas para una tarea.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "add_task_link",
            "description": "Asocia un enlace URL o ruta de archivo local a la tarjeta de la tarea.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                    "url": {"type": "string", "description": "URL o ruta de archivo."},
                    "label": {"type": "string", "description": "Texto descriptivo del enlace."},
                },
                "required": ["task_id", "url"],
            },
        },
        {
            "name": "delete_task_link",
            "description": "Elimina un enlace o archivo adjunto de una tarea.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                    "link_id": {"type": "integer", "description": "ID del enlace a eliminar."},
                },
                "required": ["task_id", "link_id"],
            },
        },
        {
            "name": "get_board_executive_summary",
            "description": "Obtiene un resumen ejecutivo de alto nivel del estado del tablero, flujo Kanban, métricas WIP y cuellos de botella (ahorra miles de tokens de contexto al agente).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mask_sensitive": {
                        "type": "boolean",
                        "description": "Si es True, aplica sanitización local de datos sensibles y PII (API keys, emails, credenciales).",
                    },
                },
            },
        },
        {
            "name": "get_task_condensed_context",
            "description": "Obtiene el contexto condensado y sintetizado de una tarea (título, descripción limpia y resumen ejecutivo del diario) optimizado para minimizar el consumo de tokens del agente.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                    "mask_sensitive": {
                        "type": "boolean",
                        "description": "Si es True, aplica sanitización local de datos sensibles y PII.",
                    },
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "sanitize_text",
            "description": "Filtra y sanitiza cadenas de texto en local, enmascarando claves de API, tokens privados, credenciales y correos electrónicos.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto a sanitizar."},
                },
                "required": ["text"],
            },
        },
        {
            "name": "search_tasks_semantic",
            "description": "Realiza una búsqueda semántica basada en embeddings sobre las tareas del tablero para encontrar tareas conceptualmente afines a una consulta en lenguaje natural.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Consulta en lenguaje natural o concepto a buscar."},
                    "top_k": {"type": "integer", "description": "Número máximo de tareas a retornar (por defecto 5)."},
                    "mask_sensitive": {
                        "type": "boolean",
                        "description": "Si es True, aplica sanitización local de datos sensibles y PII (claves API, tokens, emails).",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "create_tasks_batch",
            "description": "Crea múltiples tarjetas de tareas de forma atómica en una columna dentro de una única transacción.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "column_id": {"type": "integer", "description": "ID de la columna donde se crearán las tareas."},
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Título de la tarea."},
                                "description": {"type": "string", "description": "Descripción en Markdown."},
                                "priority": {"type": "string", "description": "Prioridad sugerida (ej. 'High', 'Medium', 'P0-Critical')."},
                                "due_date": {"type": "string", "description": "Fecha de vencimiento en formato ISO (YYYY-MM-DD)."},
                                "tags": {"type": "array", "items": {"type": "string"}, "description": "Lista de etiquetas."},
                            },
                            "required": ["title"],
                        },
                        "description": "Lista de tareas a crear.",
                    },
                },
                "required": ["column_id", "tasks"],
            },
        },
        {
            "name": "control_task_timer",
            "description": "Controla el temporizador de ejecución de una tarea (iniciar, detener o consultar estado) para rastrear el tiempo dedicado por el agente.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID de la tarea."},
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status"],
                        "description": "Acción a realizar sobre el temporizador: 'start' para iniciarlo, 'stop' para detenerlo, 'status' para consultar tiempo transcurrido.",
                    },
                },
                "required": ["task_id", "action"],
            },
        },
    ]


# --- EJECUTOR DE TOOLS CON SANDBOXING ESTRICTO ---

class McpToolExecutor:
    """Ejecuta herramientas MCP garantizando que no se sobrepasen los límites del tablero."""

    def __init__(self, board: Dict[str, Any], db_path: Optional[str] = None, client_name: str = "Agente IA"):
        self.board = board
        self.board_id = board["id"]
        self.db_path = db_path
        self.client_name = client_name

    def _verify_column_belongs_to_board(self, column_id: int) -> Dict[str, Any]:
        columns = database.get_columns(self.board_id, db_path=self.db_path)
        for col in columns:
            if col["id"] == column_id:
                return col
        raise McpSecurityError(f"La columna ID {column_id} no pertenece al tablero vinculado (ID {self.board_id}).")

    def _verify_task_belongs_to_board(self, task_id: int) -> Dict[str, Any]:
        task = database.get_task(task_id, db_path=self.db_path)
        if not task:
            raise McpSecurityError(f"Tarea con ID {task_id} no encontrada.")

        # Verificar que la columna de la tarea pertenezca al tablero
        self._verify_column_belongs_to_board(task["column_id"])
        return task

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # BLOQUEO EXPLÍCITO DE COLUMNAS (REGLA HUMAN-ONLY)
        if any(tool_name.startswith(p) for p in ("create_column", "delete_column", "update_column", "rename_column")):
            raise McpPermissionDenied(
                "Operación denegada: la creación, edición, renombrado o eliminación de columnas "
                "está reservada exclusivamente al usuario humano para garantizar el gobierno del flujo de trabajo."
            )

        handler = getattr(self, f"_tool_{tool_name}", None)
        if not handler:
            raise ValueError(f"Herramienta desconocida: '{tool_name}'")

        res_data = handler(arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(res_data, indent=2, ensure_ascii=False),
                }
            ]
        }

    def _tool_get_board_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        columns = database.get_columns(self.board_id, db_path=self.db_path)
        total_tasks = 0
        cols_summary = []
        for c in columns:
            t_list = database.get_tasks(c["id"], db_path=self.db_path)
            total_tasks += len(t_list)
            cols_summary.append({
                "id": c["id"],
                "name": c["name"],
                "position": c["position"],
                "color": c["color"],
                "wip_limit": c.get("wip_limit"),
                "tasks_count": len(t_list),
            })

        return {
            "board_id": self.board_id,
            "board_uuid": self.board["board_uuid"],
            "name": self.board["name"],
            "color": self.board["color"],
            "ai_system_prompt": self.board.get("ai_system_prompt") or "",
            "total_tasks": total_tasks,
            "columns": cols_summary,
        }

    def _tool_list_columns(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        columns = database.get_columns(self.board_id, db_path=self.db_path)
        return [
            {
                "id": c["id"],
                "name": c["name"],
                "color": c["color"],
                "position": c["position"],
                "wip_limit": c.get("wip_limit"),
                "collapsed": bool(c.get("collapsed", 0)),
            }
            for c in columns
        ]

    def _tool_list_tasks(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        target_col_id = args.get("column_id")
        tag_filter = args.get("tag", "").lower().strip()

        columns = database.get_columns(self.board_id, db_path=self.db_path)
        columns_map = {c["id"]: c["name"] for c in columns}

        if target_col_id:
            self._verify_column_belongs_to_board(target_col_id)
            cols_to_query = [target_col_id]
        else:
            cols_to_query = list(columns_map.keys())

        result = []
        for col_id in cols_to_query:
            tasks = database.get_tasks(col_id, db_path=self.db_path)
            task_ids = [t["id"] for t in tasks]
            tags_by_task = database.get_task_tags_bulk(task_ids, db_path=self.db_path)

            for t_item in tasks:
                t_tags = tags_by_task.get(t_item["id"], [])
                tag_values = [tg["value"] for tg in t_tags]

                if tag_filter and not any(tag_filter in tv.lower() for tv in tag_values):
                    continue

        mask_sensitive = bool(args.get("mask_sensitive", False))
        result = []
        for col_id in cols_to_query:
            tasks = database.get_tasks(col_id, db_path=self.db_path)
            task_ids = [t["id"] for t in tasks]
            tags_by_task = database.get_task_tags_bulk(task_ids, db_path=self.db_path)

            for t_item in tasks:
                t_tags = tags_by_task.get(t_item["id"], [])
                tag_values = [tg["value"] for tg in t_tags]

                if tag_filter and not any(tag_filter in tv.lower() for tv in tag_values):
                    continue

                desc = clean_html_description(t_item.get("description", "") or "")
                if mask_sensitive and desc:
                    import privacy_shield
                    desc, _ = privacy_shield.sanitize_text(desc)

                result.append({
                    "id": t_item["id"],
                    "column_id": col_id,
                    "column_name": columns_map.get(col_id, ""),
                    "title": t_item["title"],
                    "description": desc,
                    "due_date": t_item.get("due_date"),
                    "position": t_item["position"],
                    "tags": tag_values,
                })

        return result

    def _tool_get_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        mask_sensitive = bool(args.get("mask_sensitive", False))
        task = self._verify_task_belongs_to_board(task_id)

        columns = database.get_columns(self.board_id, db_path=self.db_path)
        col_name = next((c["name"] for c in columns if c["id"] == task["column_id"]), "")

        tags = database.get_task_tags(task_id, db_path=self.db_path)
        links = database.get_task_links(task_id, db_path=self.db_path)
        logs = database.get_task_logs(task_id, db_path=self.db_path)

        desc = task.get("description", "") or ""
        if mask_sensitive and desc:
            import privacy_shield
            desc, _ = privacy_shield.sanitize_text(desc)

        return {
            "id": task["id"],
            "column_id": task["column_id"],
            "column_name": col_name,
            "title": task["title"],
            "description": desc,
            "due_date": task.get("due_date"),
            "due_time": task.get("due_time"),
            "recurrence": task.get("recurrence", "none"),
            "tags": [{"category": tg["category"], "value": tg["value"], "color": tg["color"]} for tg in tags],
            "links": [{"id": lnk["id"], "url": lnk["url"], "label": lnk["label"]} for lnk in links],
            "logs": [{"id": lg["id"], "content": lg["content"], "created_at": lg["created_at"]} for lg in logs],
        }

    def _tool_create_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        col_id = args["column_id"]
        title = args["title"].strip()
        desc = args.get("description", "")
        due_date = args.get("due_date")
        priority = args.get("priority")
        tag_names = args.get("tags", [])

        self._verify_column_belongs_to_board(col_id)

        task_id = database.create_task(
            column_id=col_id,
            title=title,
            description=desc,
            due_date=due_date,
            db_path=self.db_path,
        )

        # Asignar etiquetas y prioridad si se especifican
        tag_ids = []
        if priority:
            prio_id = database.get_or_create_tag_value("Priority", priority, "#f59e0b", db_path=self.db_path)
            tag_ids.append(prio_id)

        for tname in tag_names:
            t_id = database.get_or_create_tag_value("General", tname, "#6b7280", db_path=self.db_path)
            if t_id not in tag_ids:
                tag_ids.append(t_id)

        if tag_ids:
            database.set_task_tags(task_id, tag_ids, db_path=self.db_path)

        # Registrar entrada de auditoría (escapando client_name para evitar inyección en QLabel)
        safe_client = html.escape(self.client_name)
        audit_entry = f"[{safe_client}]: Tarea creada a través de integración MCP."
        database.add_task_log(task_id, audit_entry, db_path=self.db_path)

        # Auto-indexar embedding para búsquedas semánticas inmediatas
        try:
            import local_ai
            local_ai.index_task_embedding(task_id, title, desc, db_path=self.db_path)
        except Exception:
            pass

        # Notificar a la UI
        get_mcp_event_bus().board_mutated.emit(self.board_id)

        return {"success": True, "task_id": task_id, "message": f"Tarea '{title}' creada con éxito."}

    def _tool_update_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        task = self._verify_task_belongs_to_board(task_id)

        new_title = args.get("title", task["title"])
        new_desc = args.get("description", task.get("description", ""))
        new_due = args.get("due_date", task.get("due_date"))

        database.update_task(
            task_id=task_id,
            title=new_title,
            description=new_desc,
            due_date=new_due,
            db_path=self.db_path,
        )

        if "tags" in args or "priority" in args:
            existing_tags = database.get_task_tags(task_id, db_path=self.db_path)
            tag_ids = []

            # Prioridad
            if "priority" in args:
                prio = args["priority"]
                if prio:
                    p_id = database.get_or_create_tag_value("Priority", prio, "#f59e0b", db_path=self.db_path)
                    tag_ids.append(p_id)
            else:
                for et in existing_tags:
                    if et["category"].lower() == "priority":
                        tag_ids.append(et["tag_value_id"])

            # Tags
            if "tags" in args:
                for tname in args["tags"]:
                    t_id = database.get_or_create_tag_value("General", tname, "#6b7280", db_path=self.db_path)
                    if t_id not in tag_ids:
                        tag_ids.append(t_id)
            else:
                for et in existing_tags:
                    if et["category"].lower() != "priority" and et["tag_value_id"] not in tag_ids:
                        tag_ids.append(et["tag_value_id"])

            database.set_task_tags(task_id, tag_ids, db_path=self.db_path)

        audit_entry = f"[{self.client_name}]: Tarea actualizada a través de MCP."
        database.add_task_log(task_id, audit_entry, db_path=self.db_path)

        get_mcp_event_bus().board_mutated.emit(self.board_id)
        return {"success": True, "task_id": task_id}

    def _tool_move_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        target_col_id = args["target_column_id"]
        target_pos = args.get("target_position")

        self._verify_task_belongs_to_board(task_id)
        target_col = self._verify_column_belongs_to_board(target_col_id)

        with database.get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            if target_pos is None or target_pos <= 0:
                target_pos = 0
                cursor.execute(
                    "UPDATE tasks SET position = position + 1 WHERE column_id = ? AND id != ?",
                    (target_col_id, task_id),
                )
            else:
                cursor.execute(
                    "UPDATE tasks SET position = position + 1 WHERE column_id = ? AND id != ? AND position >= ?",
                    (target_col_id, task_id, target_pos),
                )

            cursor.execute(
                "UPDATE tasks SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (target_col_id, target_pos, task_id),
            )

        audit_entry = f"[{self.client_name}]: Tarea desplazada a columna '{target_col['name']}' (situada arriba, pos {target_pos})."
        database.add_task_log(task_id, audit_entry, db_path=self.db_path)

        get_mcp_event_bus().board_mutated.emit(self.board_id)
        return {
            "success": True,
            "task_id": task_id,
            "column_id": target_col_id,
            "column_name": target_col["name"],
            "position": target_pos,
        }

    def _tool_add_task_comment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        comment = html.escape(args["comment"].strip())
        self._verify_task_belongs_to_board(task_id)

        safe_client = html.escape(self.client_name)
        entry = f"[{safe_client}]: {comment}"
        log_id = database.add_task_log(task_id, entry, db_path=self.db_path)

        get_mcp_event_bus().board_mutated.emit(self.board_id)
        return {"success": True, "log_id": log_id}

    def _tool_list_task_comments(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        task_id = args["task_id"]
        self._verify_task_belongs_to_board(task_id)
        logs = database.get_task_logs(task_id, db_path=self.db_path)
        return [{"id": entry["id"], "content": entry["content"], "created_at": entry["created_at"]} for entry in logs]

    def _tool_add_task_link(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        url = args["url"].strip()
        label = args.get("label", "").strip() or None
        self._verify_task_belongs_to_board(task_id)

        link_id = database.add_task_link(task_id, url, label=label, db_path=self.db_path)
        get_mcp_event_bus().board_mutated.emit(self.board_id)
        return {"success": True, "link_id": link_id}

    def _tool_delete_task_link(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        link_id = args["link_id"]
        self._verify_task_belongs_to_board(task_id)

        database.delete_task_link(link_id, db_path=self.db_path)
        get_mcp_event_bus().board_mutated.emit(self.board_id)
        return {"success": True, "link_id": link_id}

    def _tool_get_board_executive_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        mask_sensitive = bool(args.get("mask_sensitive", False))
        import local_ai
        import privacy_shield
        data = local_ai.generate_daily_standup_data(self.board_id, db_path=self.db_path)
        markdown = local_ai.format_daily_standup_markdown(data, self.board["name"])
        if mask_sensitive:
            markdown, _ = privacy_shield.sanitize_text(markdown)

        return {
            "board_id": self.board_id,
            "board_name": self.board["name"],
            "total_tasks": data["total_tasks"],
            "in_progress_count": len(data["in_progress"]),
            "stagnant_count": len(data["stagnant"]),
            "completed_recently_count": len(data["completed_recently"]),
            "wip_violations": data["wip_violations"],
            "executive_markdown": markdown,
        }

    def _tool_get_task_condensed_context(self, args: Dict[str, Any]) -> Dict[str, Any]:
        task_id = args["task_id"]
        mask_sensitive = bool(args.get("mask_sensitive", False))
        task = self._verify_task_belongs_to_board(task_id)

        columns = database.get_columns(self.board_id, db_path=self.db_path)
        col_name = next((c["name"] for c in columns if c["id"] == task["column_id"]), "")
        logs = database.get_task_logs(task_id, db_path=self.db_path)

        import local_ai
        import privacy_shield
        diary_summary = local_ai.summarize_diary_offline(logs, task["title"])
        clean_desc = local_ai.clean_html_description(task.get("description", "") or "")

        if mask_sensitive:
            clean_desc, _ = privacy_shield.sanitize_text(clean_desc)
            diary_summary, _ = privacy_shield.sanitize_text(diary_summary)

        return {
            "task_id": task["id"],
            "title": task["title"],
            "column_name": col_name,
            "due_date": task.get("due_date"),
            "description": clean_desc,
            "journal_summary": diary_summary,
            "total_logs_count": len(logs),
        }

    def _tool_sanitize_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        import privacy_shield
        text = args.get("text", "")
        sanitized, redactions = privacy_shield.sanitize_text(text)
        return {
            "sanitized_text": sanitized,
            "redactions_count": len(redactions),
            "redactions": redactions,
        }

    def _tool_search_tasks_semantic(self, args: Dict[str, Any]) -> List[Dict[str, Any]]:
        query = str(args.get("query", "")).strip()
        top_k = int(args.get("top_k", 5))
        mask_sensitive = bool(args.get("mask_sensitive", False))
        if not query:
            return []

        import local_ai
        results = local_ai.semantic_search_tasks(
            query=query,
            board_id=self.board_id,
            top_k=top_k,
            db_path=self.db_path,
        )

        formatted = []
        for item in results:
            desc = item.get("description", "") or ""
            if mask_sensitive and desc:
                import privacy_shield
                desc, _ = privacy_shield.sanitize_text(desc)

            formatted.append({
                "id": item["id"],
                "title": item["title"],
                "column_id": item["column_id"],
                "column_name": item.get("column_name", ""),
                "description": desc,
                "due_date": item.get("due_date"),
                "similarity": round(float(item.get("similarity", 0.0)), 3),
            })
        return formatted

    def _tool_create_tasks_batch(self, args: Dict[str, Any]) -> Dict[str, Any]:
        col_id = args["column_id"]
        tasks_list = args.get("tasks", [])
        if not tasks_list:
            return {"success": True, "created_count": 0, "tasks": []}

        self._verify_column_belongs_to_board(col_id)

        tasks_data = []
        for t in tasks_list:
            title = str(t.get("title", "")).strip()
            desc = t.get("description", "") or ""
            due = t.get("due_date")
            tasks_data.append({
                "column_id": col_id,
                "title": title,
                "description": desc,
                "due_date": due,
            })

        created_ids = database.create_tasks_batch(tasks_data, db_path=self.db_path)

        safe_client = html.escape(self.client_name)
        audit_entry = f"[{safe_client}]: Tarea creada en lote (batch) a través de integración MCP."

        created_summary = []
        import local_ai
        for idx, tid in enumerate(created_ids):
            t_orig = tasks_list[idx]
            tag_names = t_orig.get("tags", [])
            priority = t_orig.get("priority")
            tag_ids = []
            if priority:
                prio_id = database.get_or_create_tag_value("Priority", priority, "#f59e0b", db_path=self.db_path)
                tag_ids.append(prio_id)
            for tname in tag_names:
                t_id = database.get_or_create_tag_value("General", tname, "#6b7280", db_path=self.db_path)
                if t_id not in tag_ids:
                    tag_ids.append(t_id)
            if tag_ids:
                database.set_task_tags(tid, tag_ids, db_path=self.db_path)

            database.add_task_log(tid, audit_entry, db_path=self.db_path)

            try:
                local_ai.index_task_embedding(tid, t_orig.get("title", ""), t_orig.get("description", ""), db_path=self.db_path)
            except Exception:
                pass

            created_summary.append({
                "task_id": tid,
                "title": t_orig.get("title", ""),
                "column_id": col_id,
            })

        get_mcp_event_bus().board_mutated.emit(self.board_id)

        return {
            "success": True,
            "created_count": len(created_ids),
            "tasks": created_summary,
            "message": f"Se crearon {len(created_ids)} tareas con éxito en la columna ID {col_id}."
        }

    def _tool_control_task_timer(self, args: Dict[str, Any]) -> Dict[str, Any]:
        from datetime import datetime
        task_id = args["task_id"]
        action = str(args.get("action", "")).lower().strip()
        task = self._verify_task_belongs_to_board(task_id)

        now_dt = datetime.now()
        timer_started_at = task.get("timer_started_at")

        def _calc_elapsed(raw_val: Any) -> float:
            if not raw_val:
                return 0.0
            try:
                if isinstance(raw_val, (int, float)):
                    return max(0.0, now_dt.timestamp() - raw_val)
                st = datetime.fromisoformat(str(raw_val))
                return max(0.0, (now_dt - st).total_seconds())
            except Exception:
                return 0.0

        if action == "start":
            if not timer_started_at:
                iso_now = now_dt.isoformat()
                database.set_task_timer_started(task_id, iso_now, db_path=self.db_path)
                safe_client = html.escape(self.client_name)
                database.add_task_log(task_id, f"[{safe_client}]: Temporizador iniciado.", db_path=self.db_path)
                get_mcp_event_bus().board_mutated.emit(self.board_id)
                timer_started_at = iso_now
            return {
                "task_id": task_id,
                "timer_running": True,
                "started_at": timer_started_at,
                "message": f"Temporizador en marcha para tarea {task_id}.",
            }
        elif action == "stop":
            elapsed = _calc_elapsed(timer_started_at)
            if timer_started_at:
                database.set_task_timer_started(task_id, None, db_path=self.db_path)
                safe_client = html.escape(self.client_name)
                hrs = elapsed / 3600.0
                database.add_task_log(task_id, f"[{safe_client}]: Temporizador detenido ({hrs:.2f}h dedicadas).", db_path=self.db_path)
                get_mcp_event_bus().board_mutated.emit(self.board_id)
            return {
                "task_id": task_id,
                "timer_running": False,
                "elapsed_seconds": round(elapsed, 1),
                "message": f"Temporizador detenido para tarea {task_id}.",
            }
        elif action == "status":
            is_running = bool(timer_started_at)
            elapsed = _calc_elapsed(timer_started_at) if is_running else 0.0
            return {
                "task_id": task_id,
                "timer_running": is_running,
                "started_at": timer_started_at,
                "elapsed_seconds": round(elapsed, 1),
            }
        else:
            raise ValueError(f"Acción de temporizador no reconocida: '{action}'. Debe ser 'start', 'stop' o 'status'.")


# --- PROCESADOR JSON-RPC DE PROTOCOLO MCP ---

class McpProtocolHandler:
    """Maneja las peticiones JSON-RPC 2.0 del estándar Model Context Protocol."""

    def __init__(self, board: Dict[str, Any], db_path: Optional[str] = None, client_name: str = "Agente IA"):
        self.board = board
        self.db_path = db_path
        self.executor = McpToolExecutor(board, db_path=db_path, client_name=client_name)

    def handle(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Si es una notificación (sin id), devolver None
        if req_id is None and method.startswith("notifications/"):
            return None

        try:
            if method == "initialize":
                result = {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {},
                        "prompts": {},
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                    "instructions": self._build_instructions(),
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": get_mcp_tools_schema()}
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = self.executor.execute(tool_name, arguments)
            elif method == "prompts/list":
                result = {
                    "prompts": [
                        {
                            "name": "kanban_board_context",
                            "description": f"Contexto operativo e instrucciones metodológicas para el tablero '{self.board['name']}'.",
                            "arguments": [],
                        }
                    ]
                }
            elif method == "prompts/get":
                prompt_name = params.get("name")
                if prompt_name == "kanban_board_context":
                    result = {
                        "description": f"Contexto para '{self.board['name']}'",
                        "messages": [
                            {
                                "role": "user",
                                "content": {
                                    "type": "text",
                                    "text": self._build_instructions(),
                                },
                            }
                        ],
                    }
                else:
                    raise ValueError(f"Prompt no encontrado: '{prompt_name}'")
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Método no soportado: '{method}'",
                    },
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result,
            }

        except McpPermissionDenied as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32600,
                    "message": str(exc),
                },
            }
        except McpSecurityError as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32000,
                    "message": f"Violación de seguridad Sandbox: {str(exc)}",
                },
            }
        except Exception as exc:
            logger.exception("Error procesando solicitud MCP")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Error interno MCP: {str(exc)}",
                },
            }

    def _build_instructions(self) -> str:
        prompt_custom = self.board.get("ai_system_prompt") or ""
        columns = database.get_columns(self.board["id"], db_path=self.db_path)
        cols_str = ", ".join(f"'{c['name']}' (ID: {c['id']})" for c in columns)

        instructions = [
            f"# Contexto del Tablero Ekin Kanban: '{self.board['name']}'",
            f"- Columnas disponibles: {cols_str}",
            "- Regla Fundamental de Gobierno: NO intentes crear, editar o eliminar columnas. Solo el usuario humano puede alterar la estructura de columnas.",
            "- Política de Orden y Posicionamiento: El orden visual de las tareas en cada columna es de más reciente a más antiguo (de arriba hacia abajo). Al mover o crear tareas, sitúalas en la parte superior (posición 0 por defecto) para que lo más reciente aparezca siempre arriba.",
            "- Puedes leer y mover tareas a lo largo de las columnas existentes, añadir notas en su diario y actualizar prioridades y etiquetas.",
        ]
        if prompt_custom:
            instructions.append(f"\n### Instrucciones Metodológicas Específicas:\n{prompt_custom}")

        return "\n".join(instructions)


# --- SERVIDOR HTTP / SSE CONCURRENTE ---

class _SseClientSession:
    def __init__(self, session_id: str, board_uuid: str):
        self.session_id = session_id
        self.board_uuid = board_uuid
        self.message_queue: queue.Queue = queue.Queue(maxsize=100)
        self.created_at: float = time.time()
        self.last_active_at: float = time.time()
        self.is_closed: bool = False


class McpHttpHandler(BaseHTTPRequestHandler):
    """Manejador HTTP para Server-Sent Events (SSE) y llamadas JSON-RPC directas."""

    server: McpHttpServer

    def log_message(self, format, *args):
        # Desactivar logging verboso por consola
        pass

    def _send_cors_headers(self):
        """Envía cabeceras CORS restrictivas para evitar que sitios web maliciosos lean datos locales."""
        origin = self.headers.get("Origin")
        if not origin:
            # Clientes locales no basados en navegador (Claude Code, Cursor, AGY CLI) no envían Origin.
            # No se emite comodín '*' para evitar concesiones indebidas a clientes no autenticados.
            return

        # Para clientes web locales o de extensiones de IDE (vscode-webview, localhost, 127.0.0.1)
        parsed = urlparse(origin)
        hostname = (parsed.hostname or "").lower()
        scheme = (parsed.scheme or "").lower()
        if hostname in ("localhost", "127.0.0.1") or scheme in ("vscode-webview", "app", "file"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

    def do_OPTIONS(self):
        """Maneja peticiones preflight CORS de clientes web o navegadores."""
        self.send_response(204)
        self._send_cors_headers()
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Client-Name")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/status" or parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            resp = {
                "status": "ok",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "protocol": MCP_PROTOCOL_VERSION,
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if parsed.path == "/sse":
            board_uuid = params.get("board", [""])[0]
            token = params.get("token", [None])[0]

            try:
                authenticate_and_get_board(board_uuid, token, db_path=self.server.db_path)
            except McpSecurityError as exc:
                self.send_response(403)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"Error 403 Forbidden: {str(exc)}".encode("utf-8"))
                return

            session_id = secrets.token_hex(16)
            session = _SseClientSession(session_id, board_uuid)
            self.server.register_session(session)

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self._send_cors_headers()
            self.end_headers()

            # Enviar evento de endpoint de handshake SSE según MCP spec
            post_endpoint = f"/message?session_id={session_id}&board={board_uuid}"
            if token:
                post_endpoint += f"&token={token}"

            init_event = f"event: endpoint\ndata: {post_endpoint}\n\n"
            self.wfile.write(init_event.encode("utf-8"))
            self.wfile.flush()

            try:
                while self.server.is_running and not session.is_closed:
                    try:
                        msg = session.message_queue.get(timeout=1.0)
                        if msg is None:
                            break
                        event_payload = f"event: message\ndata: {json.dumps(msg)}\n\n"
                        self.wfile.write(event_payload.encode("utf-8"))
                        self.wfile.flush()
                        session.last_active_at = time.time()
                    except queue.Empty:
                        # Enviar comentario keepalive para evitar desconexiones de timeout
                        self.wfile.write(b": keepalive\n\n")
                        self.wfile.flush()
                        session.last_active_at = time.time()
            except (ConnectionError, BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                session.is_closed = True
                self.server.unregister_session(session_id)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        board_uuid = params.get("board", [""])[0]
        token = params.get("token", [None])[0]
        session_id = params.get("session_id", [None])[0]

        try:
            board = authenticate_and_get_board(board_uuid, token, db_path=self.server.db_path)
        except McpSecurityError as exc:
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        # Mitigación DoS: validar tamaño máximo de cuerpo HTTP
        try:
            content_len_hdr = self.headers.get("Content-Length", 0)
            content_len = int(content_len_hdr)
            if content_len < 0 or content_len > MAX_MCP_PAYLOAD_SIZE:
                self.send_response(413)
                self.end_headers()
                return
        except (ValueError, TypeError):
            self.send_response(400)
            self.end_headers()
            return

        raw_body = self.rfile.read(content_len).decode("utf-8", errors="replace")
        try:
            req_data = json.loads(raw_body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        # Sanitizar nombre de cliente opcional de cabeceras
        raw_client_name = self.headers.get("X-Client-Name", "Agente IA")
        client_name = re.sub(r"[^\w\s\-\.\(\)\[\]]", "", raw_client_name)[:40].strip() or "Agente IA"
        protocol = McpProtocolHandler(board, db_path=self.server.db_path, client_name=client_name)
        response_data = protocol.handle(req_data)

        if parsed.path == "/message":
            # Si hay session_id de SSE activa, enrutar la respuesta por SSE
            if session_id and response_data is not None:
                self.server.send_to_session(session_id, response_data)

            self.send_response(202)
            self.send_header("Content-Type", "text/plain")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"Accepted")
            return

        if parsed.path == "/rpc":
            # Respuesta JSON-RPC directa por HTTP
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            if response_data is not None:
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


class McpHttpServer(ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass, db_path: Optional[str] = None):
        super().__init__(server_address, RequestHandlerClass)
        self.db_path = db_path
        self.is_running = True
        self._sessions: Dict[str, _SseClientSession] = {}
        self._lock = threading.Lock()
        self._scavenger_thread: Optional[threading.Thread] = None

    def start_scavenger(self, interval_seconds: float = 10.0, max_idle_seconds: float = 120.0):
        """Inicia un hilo en segundo plano que limpia sesiones SSE inactivas o zombies."""
        def _scavenger_loop():
            while self.is_running:
                time.sleep(interval_seconds)
                if not self.is_running:
                    break
                try:
                    self.scavenge_stale_sessions(max_idle_seconds=max_idle_seconds)
                except Exception:
                    pass

        self._scavenger_thread = threading.Thread(target=_scavenger_loop, daemon=True, name="EkinMcpScavenger")
        self._scavenger_thread.start()

    def scavenge_stale_sessions(self, max_idle_seconds: float = 120.0) -> int:
        """Detecta y purga sesiones inactivas o cerradas para evitar fugas de memoria."""
        now = time.time()
        stale_ids = []
        with self._lock:
            for sid, sess in list(self._sessions.items()):
                if sess.is_closed or (now - sess.last_active_at > max_idle_seconds):
                    stale_ids.append(sid)
            for sid in stale_ids:
                sess = self._sessions.pop(sid, None)
                if sess:
                    sess.is_closed = True
                    try:
                        sess.message_queue.put_nowait(None)
                    except Exception:
                        pass
        return len(stale_ids)

    def register_session(self, session: _SseClientSession):
        with self._lock:
            self._sessions[session.session_id] = session

    def unregister_session(self, session_id: str):
        with self._lock:
            sess = self._sessions.pop(session_id, None)
            if sess:
                sess.is_closed = True

    def send_to_session(self, session_id: str, data: Any) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or session.is_closed:
                return False
            try:
                # Si la cola excede 100 mensajes, el cliente no está consumiendo (zombie)
                if session.message_queue.qsize() >= 100:
                    session.is_closed = True
                    self._sessions.pop(session_id, None)
                    return False
                session.message_queue.put_nowait(data)
                return True
            except Exception:
                session.is_closed = True
                self._sessions.pop(session_id, None)
                return False

    def close_all_sessions(self):
        with self._lock:
            for session in list(self._sessions.values()):
                session.is_closed = True
                try:
                    session.message_queue.put_nowait(None)
                except Exception:
                    pass
            self._sessions.clear()


# --- GESTOR GLOBAL DE SERVIDOR MCP (SINGLETON) ---

class McpManager:
    """Controla el ciclo de vida del servidor MCP embebido en Ekin Kanban."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        self.port: int = DEFAULT_MCP_PORT
        self.server: Optional[McpHttpServer] = None
        self.thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        return self.server is not None and self.server.is_running

    def get_base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def start(self, port: int = DEFAULT_MCP_PORT) -> bool:
        if self.is_running():
            return True

        self.port = port
        try:
            self.server = McpHttpServer(("127.0.0.1", self.port), McpHttpHandler, db_path=self.db_path)
            self.server.start_scavenger()
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="EkinMcpServer")
            self.thread.start()
            logger.info("Servidor MCP de Ekin iniciado en http://127.0.0.1:%s", self.port)
            return True
        except Exception as exc:
            logger.error("No se pudo iniciar el servidor MCP en puerto %s: %s", port, exc)
            self.server = None
            return False

    def stop(self):
        if self.server:
            self.server.is_running = False
            self.server.close_all_sessions()
            self.server.shutdown()
            self.server.server_close()
            self.server = None
            self.thread = None
            logger.info("Servidor MCP de Ekin detenido.")

    def get_board_sse_url(self, board_uuid: str, token: Optional[str] = None) -> str:
        url = f"{self.get_base_url()}/sse?board={board_uuid}"
        if token:
            url += f"&token={token}"
        return url

    def get_claude_code_command(self, board_name: str, board_uuid: str, token: Optional[str] = None) -> str:
        sse_url = self.get_board_sse_url(board_uuid, token)
        safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in board_name.lower())
        return f'claude mcp add --transport sse ekin-{safe_name} "{sse_url}"'

    def get_claude_desktop_config(self, board_name: str, board_uuid: str, token: Optional[str] = None) -> Dict[str, Any]:
        sse_url = self.get_board_sse_url(board_uuid, token)
        safe_name = f"ekin-{board_uuid[:8]}"
        return {
            "mcpServers": {
                safe_name: {
                    "url": sse_url,
                }
            }
        }

    def get_cursor_config(self, board_name: str, board_uuid: str, token: Optional[str] = None) -> Dict[str, Any]:
        sse_url = self.get_board_sse_url(board_uuid, token)
        safe_name = f"ekin-{board_uuid[:8]}"
        return {
            "mcpServers": {
                safe_name: {
                    "url": sse_url,
                }
            }
        }


_global_manager: Optional[McpManager] = None


def get_mcp_manager(db_path: Optional[str] = None) -> McpManager:
    global _global_manager
    if _global_manager is None:
        _global_manager = McpManager(db_path=db_path)
    return _global_manager
