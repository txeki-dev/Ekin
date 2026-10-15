"""
Módulo de IA Local de Ekin. Tras #60 su alcance queda acotado a:
1. Detección de tareas repetidas en un mismo tablero (embeddings locales + similitud coseno).
2. Resumen/focalización del contexto que se expone por MCP para ahorrar tokens
   (resumen ejecutivo del tablero y resumen determinista del diario de una tarea).
La detección de información sensible vive en privacy_shield.py.
"""

import re
import json
import time
import threading
import urllib.request
import urllib.error
import math
import hashlib
from datetime import datetime, timedelta
from typing import Optional
import column_roles
import database
from html_utils import clean_html_description
from strings import t as _t  # alias: `t` se usa como variable de bucle en este módulo


def check_http_endpoint(url: str, timeout: float = 1.0) -> bool:
    """Comprueba rápidamente si un endpoint HTTP local está respondiendo."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Ekin-AI"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status in (200, 204, 404)
    except Exception:
        return False


def is_ollama_available(timeout: float = 0.1) -> bool:
    """Comprueba rápidamente si Ollama está respondiendo en localhost."""
    return check_http_endpoint("http://127.0.0.1:11434/api/tags", timeout=timeout)


def summarize_diary_offline(logs: list[dict], task_title: str = "") -> str:
    """Resumen determinista del diario de una tarea: 'Qué se hizo' (últimas entradas) +
    'Siguiente paso'. `logs` son las entradas (con 'content' HTML y 'created_at')."""
    entries = []
    for log in logs:
        text = clean_html_description(log.get("content", "") or "").strip()
        if text:
            entries.append((log.get("created_at", "") or "", text))
    if not entries:
        return _t("ai.summary.empty")

    recent = entries[-6:]
    lines = [f"## {_t('ai.summary.what_happened')}"]
    for created, text in recent:
        first = text.splitlines()[0][:200]
        date_str = created[:10]
        lines.append(f"- {date_str + ' — ' if date_str else ''}{first}")
    lines.append("")
    lines.append(f"## {_t('ai.summary.next_step')}")
    lines.append(f"- {recent[-1][1].splitlines()[0][:200]}")
    return "\n".join(lines)


def generate_daily_standup_data(board_id: int, db_path: Optional[str] = None) -> dict:
    """Extrae métricas y estado del flujo del tablero para generar el informe Daily Standup."""
    board = database.get_board(board_id, db_path)
    board_name = board["name"] if board else "Board"
    columns = database.get_columns(board_id, db_path)

    completed_recently = []
    in_progress = []
    stagnant = []
    wip_violations = []
    total_tasks = 0

    now = datetime.now()
    roles = column_roles.column_roles(columns)
    columns_flow = []
    first_by_role = {}
    due_soon = []
    due_limit = (now + timedelta(days=7)).strftime("%Y-%m-%d")

    for col in columns:
        col_id = col["id"]
        col_name = col["name"]
        wip_limit = col.get("wip_limit")
        tasks = database.get_tasks(col_id, db_path)
        total_tasks += len(tasks)

        role = roles[col_id]
        is_done = role == column_roles.DONE
        is_in_progress = role == column_roles.IN_PROGRESS

        # Flujo por columnas: lo que el agente necesita para encontrar trabajo sin list_tasks
        columns_flow.append({
            "id": col_id,
            "name": col_name,
            "role": role,
            "count": len(tasks),
            "wip_limit": wip_limit,
            "top_tasks": [] if is_done else [
                {"id": t["id"], "title": t["title"], "due_date": t.get("due_date")} for t in tasks[:5]
            ],
        })
        if tasks and role not in first_by_role:
            first_by_role[role] = {"id": tasks[0]["id"], "title": tasks[0]["title"], "column_name": col_name, "role": role}
        if not is_done:
            due_soon += [
                {"id": t["id"], "title": t["title"], "column_name": col_name, "due_date": t["due_date"]}
                for t in tasks if t.get("due_date") and t["due_date"] <= due_limit
            ]

        if wip_limit and len(tasks) > wip_limit:
            wip_violations.append({
                "column_id": col_id,
                "column_name": col_name,
                "count": len(tasks),
                "limit": wip_limit
            })

        for t in tasks:
            t_data = dict(t)
            t_data["column_name"] = col_name

            updated_str = t_data.get("updated_at") or t_data.get("created_at") or ""
            days_inactive = 0
            if updated_str:
                try:
                    clean_dt = updated_str.replace("T", " ").split(".")[0]
                    dt = datetime.strptime(clean_dt, "%Y-%m-%d %H:%M:%S")
                    days_inactive = max(0, (now - dt).days)
                except Exception:
                    days_inactive = 0

            t_data["days_inactive"] = days_inactive

            if is_done:
                if days_inactive <= 3 or len(completed_recently) < 5:
                    completed_recently.append(t_data)
            elif is_in_progress:
                in_progress.append(t_data)
                if days_inactive >= 3:
                    stagnant.append(t_data)

    # Tarea activa: lo que está en curso, después lo pendiente de revisión, después lo listo
    active_task = next(
        (first_by_role[r] for r in (column_roles.IN_PROGRESS, column_roles.REVIEW, column_roles.READY) if r in first_by_role),
        None,
    )

    return {
        "board_id": board_id,
        "board_name": board_name,
        "total_tasks": total_tasks,
        "completed_recently": completed_recently,
        "in_progress": in_progress,
        "stagnant": stagnant,
        "wip_violations": wip_violations,
        "columns_count": len(columns),
        "active_task": active_task,
        "columns_flow": columns_flow,
        "due_soon": sorted(due_soon, key=lambda t: t["due_date"])[:10],
    }


def format_daily_standup_markdown(standup_data: dict, board_name: str = "") -> str:
    """Formatea la estructura de standup_data en un reporte Markdown elegante."""
    b_name = board_name or standup_data.get("board_name") or "Board"
    completed = standup_data.get("completed_recently", [])
    in_prog = standup_data.get("in_progress", [])
    stagnant = standup_data.get("stagnant", [])
    wip_warns = standup_data.get("wip_violations", [])
    total = standup_data.get("total_tasks", 0)

    lines = [
        f"# 📋 Daily Standup — {b_name}",
        "*Executive summary of the board's flow and health*",
        "",
        "## 🎯 Active task",
    ]
    active = standup_data.get("active_task")
    if active:
        lines.append(f"- **{active['title']}** `[#{active['id']}]` ({active['column_name']}, {active['role']})")
    else:
        lines.append("- *(Nothing in In Progress, Review or Ready: check the Backlog)*")

    lines.append("")
    lines.append("## 🧭 Flow by column")
    for c in standup_data.get("columns_flow", []):
        limit = f"/{c['wip_limit']}" if c.get("wip_limit") else ""
        tops = ", ".join(f"#{t['id']} {t['title']}" for t in c["top_tasks"])
        more = c["count"] - len(c["top_tasks"])
        if tops and more > 0:
            tops += f" (+{more} more)"
        lines.append(f"- **{c['name']}** [{c['role']}] {c['count']}{limit}" + (f": {tops}" if tops else ""))

    lines.append("")
    lines.append("## 📅 Due in the next 7 days")
    due = standup_data.get("due_soon", [])
    if due:
        for t in due:
            lines.append(f"- **{t['title']}** `[#{t['id']}]` — {t['due_date']} ({t['column_name']})")
    else:
        lines.append("- *(Nothing due in the next 7 days)*")

    lines.append("")
    lines.append("## 🟢 Recently completed")
    if completed:
        for t in completed[:8]:
            lines.append(f"- **{t.get('title')}** `[#{t.get('id')}]` ({t.get('column_name')})")
    else:
        lines.append("- *(No recently completed tasks)*")

    lines.append("")
    lines.append("## 🟡 In progress")
    if in_prog:
        for t in in_prog[:10]:
            days = t.get("days_inactive", 0)
            inact_str = f" — *idle {days}d*" if days > 0 else ""
            lines.append(f"- **{t.get('title')}** `[#{t.get('id')}]` ({t.get('column_name')}){inact_str}")
    else:
        lines.append("- *(No tasks in progress)*")

    lines.append("")
    lines.append("## 🔴 Blocked / stalled")
    if stagnant:
        for t in stagnant:
            lines.append(f"- ⚠️ **{t.get('title')}** `[#{t.get('id')}]` idle for **{t.get('days_inactive')} days** in *{t.get('column_name')}*.")
    elif wip_warns:
        for w in wip_warns:
            lines.append(f"- ⚠️ WIP limit exceeded in **{w['column_name']}** ({w['count']}/{w['limit']} tasks).")
    else:
        lines.append("- ✨ *Clean flow: nothing blocked or stalled.*")

    lines.append("")
    lines.append("## 📊 Board health")
    wip_status = f"⚠️ {len(wip_warns)} columns over their WIP limit" if wip_warns else "✅ WIP limits respected"
    lines.append(f"- **Tasks**: {total} | **In progress**: {len(in_prog)} | **Done recently**: {len(completed)}")
    lines.append(f"- **WIP limits**: {wip_status}")

    return "\n".join(lines)


class LocalAiCircuitBreaker:
    """Disyuntor (Circuit Breaker) para el servicio local de inferencia y embeddings.

    Previene bloqueos de la UI y demoras acumuladas cuando Ollama o llama-server
    no responden, caen o devuelven errores de socket de forma repetida.

    Estados:
    - CLOSED: Operación normal. Las peticiones se dirigen al modelo local.
    - OPEN: El circuito ha saltado tras N fallos consecutivos. Las peticiones
      se desvían inmediatamente al fallback determinista local sin esperar timeouts.
    - HALF_OPEN: Tras el periodo de enfriamiento (cooldown), permite una petición
      de prueba para verificar si el servicio local se ha recuperado.
    """

    STATE_CLOSED = "CLOSED"
    STATE_OPEN = "OPEN"
    STATE_HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.STATE_CLOSED
        self._consecutive_failures = 0
        self._last_failure_time = 0.0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            if self._state == self.STATE_OPEN:
                if (time.time() - self._last_failure_time) >= self.recovery_timeout:
                    self._state = self.STATE_HALF_OPEN
            return self._state

    def allow_request(self) -> bool:
        """Determina si se debe permitir el intento de llamada al servicio local de IA."""
        with self._lock:
            if self._state == self.STATE_CLOSED:
                return True
            if self._state == self.STATE_OPEN:
                if (time.time() - self._last_failure_time) >= self.recovery_timeout:
                    self._state = self.STATE_HALF_OPEN
                    return True
                return False
            # HALF_OPEN permite la petición de prueba
            return True

    def record_success(self) -> None:
        """Registra una respuesta satisfactoria del servicio local, cerrando el circuito."""
        with self._lock:
            self._state = self.STATE_CLOSED
            self._consecutive_failures = 0

    def record_failure(self) -> None:
        """Registra un fallo o timeout del servicio local. Si supera el umbral, abre el circuito."""
        with self._lock:
            self._consecutive_failures += 1
            self._last_failure_time = time.time()
            if self._consecutive_failures >= self.failure_threshold or self._state == self.STATE_HALF_OPEN:
                self._state = self.STATE_OPEN

    def reset(self) -> None:
        """Restablece manualmente el disyuntor al estado inicial CLOSED."""
        with self._lock:
            self._state = self.STATE_CLOSED
            self._consecutive_failures = 0
            self._last_failure_time = 0.0


_LLM_CIRCUIT_BREAKER = LocalAiCircuitBreaker()


def get_llm_circuit_breaker() -> LocalAiCircuitBreaker:
    """Obtiene la instancia global del Circuit Breaker para el servicio local de IA."""
    return _LLM_CIRCUIT_BREAKER


def compute_fallback_embedding(text: str, dim: int = 128) -> list[float]:
    """Genera un vector denso determinista y normalizado a partir de n-gramas de caracteres y palabras."""
    clean = re.sub(r"[^\w\s]", " ", (text or "").lower())
    tokens = clean.split()
    if not tokens and not clean.strip():
        return [0.0] * dim

    vector = [0.0] * dim
    features = list(tokens)
    for word in tokens:
        if len(word) >= 3:
            for i in range(len(word) - 2):
                features.append(word[i:i+3])

    for feat in features:
        h = hashlib.sha256(feat.encode("utf-8")).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        sign = 1.0 if (h[4] % 2 == 0) else -1.0
        weight = 2.0 if len(feat) > 3 else 1.0
        vector[idx] += sign * weight

    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 1e-9:
        return [x / norm for x in vector]
    return vector


def get_local_embedding(text: str, model_name: str = "nomic-embed-text", timeout: float = 3.0) -> list[float]:
    """Obtiene el embedding vectorial usando Ollama (puerto 11434).
    Si Ollama no está disponible o el modelo no está cargado, recae de forma transparente
    y determinista en `compute_fallback_embedding`."""
    clean_text = (text or "").strip()
    if not clean_text:
        return compute_fallback_embedding("")

    cb = get_llm_circuit_breaker()
    if not cb.allow_request():
        return compute_fallback_embedding(clean_text)

    if is_ollama_available():
        try:
            url = "http://127.0.0.1:11434/api/embeddings"
            payload = json.dumps({"model": model_name, "prompt": clean_text[:2000]}).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "Ekin-AI"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    emb = data.get("embedding")
                    if emb and isinstance(emb, list) and len(emb) > 0:
                        cb.record_success()
                        norm = math.sqrt(sum(x * x for x in emb))
                        return [x / norm for x in emb] if norm > 1e-9 else emb
        except Exception:
            cb.record_failure()

    return compute_fallback_embedding(clean_text)


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calcula la similitud coseno entre dos vectores (entre 0.0 y 1.0)."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 < 1e-9 or norm2 < 1e-9:
        return 0.0
    val = dot / (norm1 * norm2)
    return max(0.0, min(1.0, float(val)))


def index_task_embedding(task_id: int, title: str, description: str = "", model_name: str = "local_embedding", db_path: Optional[str] = None) -> bool:
    """Genera e indexa en SQLite el vector de embedding para una tarea."""
    content = f"{title}\n{clean_html_description(description or '')}".strip()
    vec = get_local_embedding(content)
    try:
        database.save_task_embedding(task_id, vec, model_name=model_name, db_path=db_path)
        return True
    except Exception:
        return False


def semantic_search_tasks(query: str, board_id: Optional[int] = None, top_k: int = 10, db_path: Optional[str] = None) -> list[dict]:
    """Realiza una búsqueda semántica de tareas ordenadas por similitud conceptual con la consulta."""
    clean_q = (query or "").strip()
    if not clean_q:
        return []

    q_vec = get_local_embedding(clean_q)

    if board_id is not None:
        board_ids = [board_id]
    else:
        boards = database.get_boards(db_path)
        board_ids = [b["id"] for b in boards if not b.get("archived")]

    scores = []
    for bid in board_ids:
        board_info = database.get_board(bid, db_path)
        board_name = board_info["name"] if board_info else ""
        board_color = board_info["color"] if board_info else "#3b82f6"

        stored = database.get_board_embeddings(bid, db_path)
        stored_dict = dict(stored)

        columns = database.get_columns(bid, db_path)
        for col in columns:
            tasks = database.get_tasks(col["id"], db_path)
            for t in tasks:
                tid = t["id"]
                t_vec = stored_dict.get(tid)
                if not t_vec:
                    t_content = f"{t.get('title', '')}\n{clean_html_description(t.get('description', '') or '')}"
                    t_vec = get_local_embedding(t_content)
                    try:
                        database.save_task_embedding(tid, t_vec, db_path=db_path)
                    except Exception:
                        pass

                sim = cosine_similarity(q_vec, t_vec)
                if sim > 0.05:
                    t_row = dict(t)
                    t_row["board_id"] = bid
                    t_row["board_name"] = board_name
                    t_row["board_color"] = board_color
                    t_row["column_name"] = col["name"]
                    t_row["similarity"] = sim
                    scores.append((sim, t_row))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scores[:top_k]]


def find_duplicate_tasks(title: str, description: str = "", board_id: Optional[int] = None, threshold: float = 0.70, exclude_task_id: Optional[int] = None, db_path: Optional[str] = None) -> list[dict]:
    """Detecta posibles tareas duplicadas en un tablero basándose en alta similitud semántica."""
    text = f"{title}\n{clean_html_description(description or '')}".strip()
    if not text or board_id is None:
        return []

    q_vec = get_local_embedding(text)
    stored = database.get_board_embeddings(board_id, db_path)
    stored_dict = dict(stored)

    columns = database.get_columns(board_id, db_path)
    duplicates = []

    for col in columns:
        tasks = database.get_tasks(col["id"], db_path)
        for t in tasks:
            tid = t["id"]
            if exclude_task_id is not None and tid == exclude_task_id:
                continue

            t_vec = stored_dict.get(tid)
            if not t_vec:
                t_content = f"{t.get('title', '')}\n{clean_html_description(t.get('description', '') or '')}"
                t_vec = get_local_embedding(t_content)
                try:
                    database.save_task_embedding(tid, t_vec, db_path=db_path)
                except Exception:
                    pass

            sim = cosine_similarity(q_vec, t_vec)
            if sim >= threshold:
                dup_item = dict(t)
                dup_item["similarity"] = sim
                dup_item["column_name"] = col["name"]
                duplicates.append(dup_item)

    duplicates.sort(key=lambda x: x["similarity"], reverse=True)
    return duplicates
