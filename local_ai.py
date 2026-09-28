"""
Módulo de IA Local de Ekin. Tras #60 su alcance queda acotado a:
1. Detección de tareas repetidas en un mismo tablero (embeddings locales + similitud coseno).
2. Resumen/focalización del contexto que se expone por MCP para ahorrar tokens
   (resumen ejecutivo del tablero y resumen determinista del diario de una tarea).
3. Motor LLM local (runners existentes como Ollama / LM Studio / llama-server, o runner
   gestionado por Ekin) con inferencia en streaming OpenAI-compatible, reservado para la
   traducción a inglés del JSON del MCP.
La detección de información sensible vive en privacy_shield.py.
"""

import os
import re
import sys
import json
import time
import socket
import threading
import urllib.request
import urllib.error
import atexit
import subprocess
import zipfile
import math
import hashlib
from datetime import datetime
from typing import Optional, Generator, Callable
import database
from html_utils import clean_html_description
from strings import t as _t  # alias: `t` se usa como variable de bucle en este módulo

# Rutas estándar de almacenamiento de modelos y binarios de Ekin
DEFAULT_EKIN_DIR = os.path.expanduser("~/.ekin")
DEFAULT_MODEL_DIR = os.path.join(DEFAULT_EKIN_DIR, "models")
DEFAULT_RUNNER_DIR = os.path.join(DEFAULT_EKIN_DIR, "bin")

MODEL_FILENAME = "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, MODEL_FILENAME)
RUNNER_EXE_NAME = "llama-server.exe" if sys.platform == "win32" else "llama-server"
RUNNER_PATH = os.path.join(DEFAULT_RUNNER_DIR, RUNNER_EXE_NAME)


def get_runner_download_url() -> str:
    """Devuelve la URL oficial de descarga del binario portable de llama-server según la plataforma."""
    if sys.platform == "win32":
        return "https://github.com/ggerganov/llama.cpp/releases/download/b3900/llama-b3900-bin-win-avx2-x64.zip"
    elif sys.platform == "darwin":
        return "https://github.com/ggerganov/llama.cpp/releases/download/b3900/llama-b3900-bin-macos-arm64.zip"
    else:
        return "https://github.com/ggerganov/llama.cpp/releases/download/b3900/llama-b3900-bin-ubuntu-x64.zip"


MANAGED_SERVER_PORT = 28192

# Proceso global del runner autónomo gestionado
_MANAGED_PROCESS: Optional[subprocess.Popen] = None


# Modelos populares recomendados para Ollama cuando no está activo o como sugerencia
DEFAULT_OLLAMA_MODELS = [
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:7b",
    "deepseek-coder:6.7b",
    "codellama:7b",
    "llama3.2:3b",
    "mistral:7b",
]


def is_model_downloaded() -> bool:
    """Verifica si el modelo Qwen 2.5 Coder existe localmente y no está vacío."""
    return os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 100_000_000


def is_runner_installed() -> bool:
    """Verifica si el ejecutable llama-server existe localmente."""
    return os.path.exists(RUNNER_PATH)


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


def get_ollama_models(timeout: float = 1.0) -> list[str]:
    """Obtiene la lista de nombres de modelos disponibles en Ollama local."""
    for host in ("127.0.0.1", "localhost"):
        try:
            req = urllib.request.Request(f"http://{host}:11434/api/tags", headers={"User-Agent": "Ekin-AI"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    models = [m["name"] for m in data.get("models", []) if "name" in m]
                    if models:
                        return models
        except Exception:
            pass
    return []


def detect_available_llm() -> dict:
    """Detecta qué servicio de LLM local está disponible en el equipo."""
    # 1. ¿Runner gestionado por Ekin ya activo en puerto 28192?
    if check_http_endpoint(f"http://127.0.0.1:{MANAGED_SERVER_PORT}/health", timeout=0.5):
        return {
            "status": "ready",
            "type": "managed",
            "url": f"http://127.0.0.1:{MANAGED_SERVER_PORT}",
            "name": "Ekin Local Runner (Qwen 2.5 Coder 1.5B)",
        }

    # 2. ¿Ollama activo en puerto 11434?
    if check_http_endpoint("http://127.0.0.1:11434/api/tags", timeout=0.5):
        models = get_ollama_models(timeout=0.5)
        return {
            "status": "ready",
            "type": "ollama",
            "url": "http://127.0.0.1:11434",
            "name": "Ollama (Local)",
            "models": models,
        }

    # 3. ¿Servidor OpenAI-compatible local activo (LM Studio / llama-server en 8080 o 1234)?
    for port in (8080, 1234):
        if check_http_endpoint(f"http://127.0.0.1:{port}/v1/models", timeout=0.5):
            return {
                "status": "ready",
                "type": "openai_compatible",
                "url": f"http://127.0.0.1:{port}",
                "name": f"Local LLM Server (puerto {port})",
            }

    # 4. ¿El modelo y runner de Ekin están en disco listos para iniciar?
    if is_model_downloaded() and is_runner_installed():
        return {
            "status": "can_start",
            "type": "managed",
            "url": f"http://127.0.0.1:{MANAGED_SERVER_PORT}",
            "name": "Ekin Local Runner (En disco, listo para iniciar)",
        }

    # 5. No hay modelo ni runner
    return {
        "status": "needs_download",
        "type": "structural_fallback",
        "model_exists": is_model_downloaded(),
        "runner_exists": is_runner_installed(),
        "name": "Sintetizador Estructural Ekin (Sin descarga)",
    }


def start_managed_runner() -> bool:
    """Inicia en segundo plano el ejecutable portable llama-server con el modelo Qwen 2.5 Coder."""
    global _MANAGED_PROCESS
    if check_http_endpoint(f"http://127.0.0.1:{MANAGED_SERVER_PORT}/health", timeout=0.5):
        return True

    if not is_model_downloaded() or not is_runner_installed():
        return False

    cmd = [
        RUNNER_PATH,
        "-m", MODEL_PATH,
        "--port", str(MANAGED_SERVER_PORT),
        "--host", "127.0.0.1",
        "-c", "4096",
        "--threads", str(max(1, os.cpu_count() - 1 if os.cpu_count() else 2)),
        "-ngl", "0",
    ]

    try:
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        _MANAGED_PROCESS = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags
        )

        # Esperar hasta 8 segundos a que responda
        for _ in range(16):
            time.sleep(0.5)
            if check_http_endpoint(f"http://127.0.0.1:{MANAGED_SERVER_PORT}/health", timeout=0.5):
                return True
            if _MANAGED_PROCESS.poll() is not None:
                return False
    except Exception:
        return False

    return False


def stop_managed_runner():
    """Detiene el runner autónomo gestionado si está en ejecución."""
    global _MANAGED_PROCESS
    if _MANAGED_PROCESS is not None:
        try:
            _MANAGED_PROCESS.terminate()
            try:
                _MANAGED_PROCESS.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                _MANAGED_PROCESS.kill()
                _MANAGED_PROCESS.wait(timeout=1.0)
        except Exception:
            try:
                _MANAGED_PROCESS.kill()
            except Exception:
                pass
        finally:
            _MANAGED_PROCESS = None


atexit.register(stop_managed_runner)



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
    board_name = board["name"] if board else "Tablero"
    columns = database.get_columns(board_id, db_path)

    completed_recently = []
    in_progress = []
    stagnant = []
    wip_violations = []
    total_tasks = 0

    now = datetime.now()

    for col in columns:
        col_id = col["id"]
        col_name = col["name"]
        wip_limit = col.get("wip_limit")
        tasks = database.get_tasks(col_id, db_path)
        total_tasks += len(tasks)

        col_lower = col_name.lower()
        is_done = any(k in col_lower for k in ("done", "hecho", "shipped", "completad", "terminad", "cerrad", "resuelto", "finaliz"))
        is_in_progress = any(k in col_lower for k in ("progress", "curso", "doing", "haciendo", "wip", "activo", "desarrollo"))

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

    return {
        "board_id": board_id,
        "board_name": board_name,
        "total_tasks": total_tasks,
        "completed_recently": completed_recently,
        "in_progress": in_progress,
        "stagnant": stagnant,
        "wip_violations": wip_violations,
        "columns_count": len(columns),
    }


def format_daily_standup_markdown(standup_data: dict, board_name: str = "") -> str:
    """Formatea la estructura de standup_data en un reporte Markdown elegante."""
    b_name = board_name or standup_data.get("board_name") or "Tablero"
    completed = standup_data.get("completed_recently", [])
    in_prog = standup_data.get("in_progress", [])
    stagnant = standup_data.get("stagnant", [])
    wip_warns = standup_data.get("wip_violations", [])
    total = standup_data.get("total_tasks", 0)

    lines = [
        f"# 📋 Daily Standup — {b_name}",
        "*Resumen ejecutivo de flujo y salud del tablero*",
        "",
        "## 🟢 Completado recientemente",
    ]
    if completed:
        for t in completed[:8]:
            lines.append(f"- **{t.get('title')}** `[#{t.get('id')}]` ({t.get('column_name')})")
    else:
        lines.append("- *(Ninguna tarea completada recientemente)*")

    lines.append("")
    lines.append("## 🟡 En curso / Próximo foco")
    if in_prog:
        for t in in_prog[:10]:
            days = t.get("days_inactive", 0)
            inact_str = f" — *inactiva {days}d*" if days > 0 else ""
            lines.append(f"- **{t.get('title')}** `[#{t.get('id')}]` ({t.get('column_name')}){inact_str}")
    else:
        lines.append("- *(No hay tareas activas actualmente en curso)*")

    lines.append("")
    lines.append("## 🔴 Bloqueos / Tareas estancadas")
    if stagnant:
        for t in stagnant:
            lines.append(f"- ⚠️ **{t.get('title')}** `[#{t.get('id')}]` lleva **{t.get('days_inactive')} días** sin actividad en *{t.get('column_name')}*.")
    elif wip_warns:
        for w in wip_warns:
            lines.append(f"- ⚠️ Límite WIP superado en columna **{w['column_name']}** ({w['count']}/{w['limit']} tareas).")
    else:
        lines.append("- ✨ *¡Flujo limpio! Sin bloqueos ni tareas estancadas detectadas.*")

    lines.append("")
    lines.append("## 📊 Métricas de Salud del Tablero")
    wip_status = f"⚠️ {len(wip_warns)} columnas con exceso WIP" if wip_warns else "✅ Óptimo (WIP respetado)"
    lines.append(f"- **Total de tareas**: {total} | **En curso**: {len(in_prog)} | **Hechas**: {len(completed)}")
    lines.append(f"- **Estado de límites WIP**: {wip_status}")

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



def stream_openai_chat_completion(
    endpoint: str,
    system_prompt: str,
    user_prompt: str,
    model_name: str = "qwen2.5-coder",
    timeout: float = 60.0,
    read_timeout: Optional[float] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
    on_response: Optional[Callable[[object], None]] = None,
) -> Generator[str, None, None]:
    """Envía una solicitud en streaming al endpoint OpenAI-compatible y produce tokens sucesivos."""
    url = f"{endpoint.rstrip('/')}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "stream": True,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Ekin-AI"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        if on_response is not None:
            on_response(response)

        # Si se especifica un timeout de lectura por token distinto, aplicarlo al socket
        if read_timeout is not None:
            try:
                sock = getattr(getattr(response, "fp", None), "raw", None)
                if sock and hasattr(sock, "_sock"):
                    sock._sock.settimeout(read_timeout)
            except Exception:
                pass

        try:
            for line in response:
                if cancel_check is not None and cancel_check():
                    break
                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str.startswith("data:"):
                    continue
                data_str = line_str[5:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                except Exception:
                    continue
        except (socket.timeout, TimeoutError) as exc:
            effective_timeout = read_timeout if read_timeout is not None else timeout
            raise TimeoutError(f"Streaming token delivery stalled after {effective_timeout}s: {exc}") from exc


def download_and_extract_runner(
    runner_url: Optional[str] = None,
    runner_dir: Optional[str] = None,
    cancel_check: Optional[Callable[[], bool]] = None,
    progress_callback: Optional[Callable[[int, float, str], None]] = None,
) -> tuple[bool, str]:
    """Descarga y extrae el ejecutable portable de llama-server en runner_dir."""
    url = runner_url or get_runner_download_url()
    target_dir = runner_dir or DEFAULT_RUNNER_DIR
    os.makedirs(target_dir, exist_ok=True)
    temp_zip = os.path.join(target_dir, ".llama_runner.zip")

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EkinKanban/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30.0) as response:
            total_bytes = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            start_time = time.time()
            last_update = start_time
            chunk_size = 1024 * 256  # 256 KB

            with open(temp_zip, "wb") as out_file:
                while True:
                    if cancel_check and cancel_check():
                        out_file.close()
                        if os.path.exists(temp_zip):
                            os.remove(temp_zip)
                        return False, "Descarga de runner cancelada."

                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)

                    now = time.time()
                    if progress_callback and (now - last_update >= 0.4 or downloaded == total_bytes):
                        elapsed = now - start_time
                        speed_mb = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
                        percent = int((downloaded / total_bytes) * 100) if total_bytes > 0 else 0
                        remaining_bytes = max(0, total_bytes - downloaded)
                        eta_sec = int(remaining_bytes / (speed_mb * 1024 * 1024)) if speed_mb > 0 else 0
                        eta_str = f"{eta_sec // 60}m {eta_sec % 60}s" if eta_sec >= 60 else f"{eta_sec}s"
                        progress_callback(percent, speed_mb, eta_str)
                        last_update = now

        # Extraer el archivo ZIP en target_dir de forma segura (mitigación CWE-22 / Zip Slip)
        resolved_target = os.path.abspath(target_dir)
        with zipfile.ZipFile(temp_zip, "r") as zf:
            for member in zf.infolist():
                dest_path = os.path.abspath(os.path.join(resolved_target, member.filename))
                if os.path.commonpath([resolved_target, dest_path]) != resolved_target:
                    raise RuntimeError(f"Ruta no permitida en archivo comprimido (Zip Slip): {member.filename}")
            zf.extractall(resolved_target)

        if os.path.exists(temp_zip):
            os.remove(temp_zip)

        # En sistemas Unix/macOS asegurar permisos de ejecución
        if sys.platform != "win32" and os.path.exists(RUNNER_PATH):
            try:
                os.chmod(RUNNER_PATH, os.stat(RUNNER_PATH).st_mode | 0o755)
            except Exception:
                pass

        if progress_callback:
            progress_callback(100, 0.0, "Completado")
        return True, "Runner descargado e instalado con éxito."
    except Exception as e:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except Exception:
                pass
        return False, f"Error durante la descarga del runner: {e}"
