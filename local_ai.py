"""
Módulo de IA Local Autónoma para Ekin (Vía B).
Permite seleccionar múltiples tarjetas del tablero (Kanban/Backlog) y sintetizar
especificaciones de ingeniería (SPEC) optimizadas para agentes de programación
(Google Antigravity, Claude Code, Cursor, Windsurf), historias de usuario y planes de QA.

Soporta:
1. Detección automática de runners locales existentes (Ollama, LM Studio, llama-server).
2. Runner autónomo gestionado por Ekin (Vía B): sin requerir configuración externa.
3. Generador de especificaciones estructurales instantáneo (fallback offline sin modelo).
4. Solicitud de inferencia en streaming estándar OpenAI-compatible (/v1/chat/completions).
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import atexit
import subprocess
from typing import Optional, Generator
from PySide6.QtCore import QThread, Signal

# Rutas estándar de almacenamiento de modelos y binarios de Ekin
DEFAULT_EKIN_DIR = os.path.expanduser("~/.ekin")
DEFAULT_MODEL_DIR = os.path.join(DEFAULT_EKIN_DIR, "models")
DEFAULT_RUNNER_DIR = os.path.join(DEFAULT_EKIN_DIR, "bin")

MODEL_FILENAME = "qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
MODEL_PATH = os.path.join(DEFAULT_MODEL_DIR, MODEL_FILENAME)
RUNNER_EXE_NAME = "llama-server.exe" if sys.platform == "win32" else "llama-server"
RUNNER_PATH = os.path.join(DEFAULT_RUNNER_DIR, RUNNER_EXE_NAME)

# URLs oficiales
MODEL_DOWNLOAD_URL = (
    "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
)
RUNNER_DOWNLOAD_URL = (
    "https://github.com/ggerganov/llama.cpp/releases/download/b3900/llama-b3900-bin-win-avx2-x64.zip"
)

MANAGED_SERVER_PORT = 28192

# Proceso global del runner autónomo gestionado
_MANAGED_PROCESS: Optional[subprocess.Popen] = None


def ensure_directories():
    """Asegura que los directorios ~/.ekin/models y ~/.ekin/bin existan."""
    os.makedirs(DEFAULT_MODEL_DIR, exist_ok=True)
    os.makedirs(DEFAULT_RUNNER_DIR, exist_ok=True)


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
        return {
            "status": "ready",
            "type": "ollama",
            "url": "http://127.0.0.1:11434",
            "name": "Ollama (Local)",
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


def format_tasks_for_prompt(tasks: list[dict]) -> str:
    """Formatea la lista de tarjetas de tareas seleccionadas en un bloque de texto legible."""
    parts = []
    for idx, t in enumerate(tasks, 1):
        title = t.get("title", "Sin título")
        col = t.get("column_name", "Backlog")
        desc = t.get("description", "").strip() or "Sin descripción detallada."
        due = t.get("due_date") or "Sin fecha límite"
        
        # Tags
        tags = t.get("tags", [])
        tags_str = ", ".join(f"{tag.get('category', '')}:{tag.get('value', '')}" for tag in tags) if tags else "Ninguna"

        # Logs / Diario
        logs = t.get("logs", [])
        logs_text = ""
        if logs:
            clean_logs = [entry.get("content", "").replace("<p>", "").replace("</p>", "").strip() for entry in logs[:5]]
            logs_text = "\n  - " + "\n  - ".join(clean_logs)

        part = (
            f"### Tarea {idx}: {title}\n"
            f"- **Columna / Estado**: {col}\n"
            f"- **Vencimiento**: {due}\n"
            f"- **Etiquetas**: {tags_str}\n"
            f"- **Descripción**:\n{desc}\n"
        )
        if logs_text:
            part += f"- **Notas de Discusión / Chat**:{logs_text}\n"

        parts.append(part)

    return "\n---\n".join(parts)


def build_spec_prompts(tasks: list[dict], mode: str = "coding_agent", custom_instructions: str = "") -> tuple[str, str]:
    """Genera el system prompt y user prompt según el modo de especificación seleccionado."""
    tasks_block = format_tasks_for_prompt(tasks)

    if mode == "coding_agent":
        system_prompt = (
            "Eres un Arquitecto de Software Principal y Líder Técnico Senior especializado en preparar "
            "Especificaciones Técnicas (SPEC) de alta precisión para Agentes Autónomos de IA "
            "(como Google Antigravity, Claude Code, Cursor y Windsurf).\n"
            "Tu objetivo es convertir tareas de Backlog en un documento exhaustivo, libre de ambigüedades, "
            "con arquitectura clara, contratos de datos, pasos de implementación ordenados y criterios de verificación."
        )
        user_prompt = f"""Analiza las siguientes tareas de Kanban/Backlog seleccionadas por el equipo y genera una ESPECIFICACIÓN TÉCNICA (SPEC) completa para un Agente de IA.

{tasks_block}

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}

La especificación DEBE seguir rigurosamente esta estructura en Markdown:

# SPEC: [Título Sintético de la Iniciativa]

## 1. Resumen Ejecutivo & Objetivo
- Propósito técnico y valor aportado.
- Alcance (Scope) y qué queda explícitamente fuera de alcance (Out-of-Scope).

## 2. Desglose de Tareas & Requisitos Técnicos
- Mapeo detallado de cada una de las tareas seleccionadas con sus requisitos funcionales.
- Dependencias y orden crítico de ejecución.

## 3. Arquitectura del Sistema & Diseño de Componentes
- Módulos, servicios o archivos afectados.
- Esquema de base de datos / modelos de datos / contratos de interfaz (firmas de funciones clave).

## 4. Plan de Implementación Paso a Paso
- Secuencia de pasos atómicos de implementación que el agente de IA debe ejecutar en la codebase.

## 5. Casos Límite (Edge Cases), Errores & Seguridad
- Validaciones, manejo de fallos y condiciones de carrera a prever.

## 6. Criterios de Aceptación & Verificación (Definition of Done)
- Pruebas unitarias o de integración requeridas.
- Checklist de verificación paso a paso para dar la iniciativa por completada.
"""

    elif mode == "user_stories":
        system_prompt = (
            "Eres un Product Owner y Agile Coach Senior. Tu función es transformar requisitos y notas "
            "de tarjetas Kanban en Historias de Usuario completas bajo el formato estándar de la industria "
            "con Criterios de Aceptación en formato Gherkin (Given-When-Then)."
        )
        user_prompt = f"""Convierte las siguientes tareas de Backlog en un conjunto formal de Historias de Usuario con Criterios de Aceptación:

{tasks_block}

{f"Instrucciones adicionales: {custom_instructions}" if custom_instructions else ""}

Genera la salida estructurada con:
1. **Épica / Tema Principal**
2. Para cada tarea:
   - **Título de la Historia de Usuario**
   - **Narrativa**: *Como [rol], quiero [acción], para [beneficio]*
   - **Criterios de Aceptación (Given-When-Then)**
   - **Condiciones de Frontera y Consideraciones UX/Técnicas**
"""

    else:  # qa_tests
        system_prompt = (
            "Eres un QA Lead y Especialista en Pruebas de Software. Tu objetivo es crear un Plan de Verificación "
            "y Matriz de Pruebas detallada para validar las funcionalidades descritas en las tareas de Backlog."
        )
        user_prompt = f"""Diseña un Plan de Pruebas y Matriz de QA exhaustiva para las siguientes tareas:

{tasks_block}

{f"Instrucciones adicionales: {custom_instructions}" if custom_instructions else ""}

Estructura el documento con:
1. **Estrategia de Prueba (Unitarias, Integración, UI/E2E)**
2. **Matriz de Casos de Prueba (ID, Precondición, Pasos, Resultado Esperado)**
3. **Casos Límite y Pruebas Negativas (Edge Cases)**
4. **Criterios de Éxito para Release**
"""

    return system_prompt, user_prompt


def generate_structural_spec(tasks: list[dict], mode: str = "coding_agent", custom_instructions: str = "") -> str:
    """Generador offline instantáneo que sintetiza una SPEC estructurada sin necesidad de descargar el modelo."""
    task_count = len(tasks)
    initiative_title = " - ".join(t.get("title", "Tarea") for t in tasks[:3])
    if task_count > 3:
        initiative_title += f" (+{task_count - 3} tareas)"

    if mode == "coding_agent":
        lines = [
            f"# SPEC: {initiative_title}",
            "",
            "## 1. Resumen Ejecutivo & Objetivo",
            f"Esta especificación técnica agrupa y estructura **{task_count} tareas de backlog** seleccionadas para su ejecución coordinada por un agente autónomo de IA.",
            "",
            "- **Objetivo principal**: Implementar, verificar e integrar las tareas descritas manteniendo coherencia arquitectónica.",
            "- **Alcance**: Modificaciones en la lógica de negocio, interfaz de usuario y modelos de datos pertinentes.",
            "",
            "## 2. Desglose de Tareas & Requisitos",
            "",
        ]
        for idx, t in enumerate(tasks, 1):
            title = t.get("title", "")
            desc = t.get("description", "").strip() or "Sin descripción detallada."
            col = t.get("column_name", "General")
            lines.append(f"### 2.{idx}. {title} `[{col}]`")
            lines.append(f"**Detalle de la tarea**: {desc}")
            if t.get("due_date"):
                lines.append(f"- **Vencimiento objetivo**: `{t.get('due_date')}`")
            if t.get("tags"):
                tags_formatted = " ".join(f"`{tag.get('category')}:{tag.get('value')}`" for tag in t["tags"])
                lines.append(f"- **Etiquetas**: {tags_formatted}")
            lines.append("")

        lines.extend([
            "## 3. Arquitectura del Sistema & Componentes Afectados",
            "- **Modularidad**: Separar responsabilidades entre el almacenamiento de datos, lógica de dominio e interfaz.",
            "- **Persistencia**: Aplicar transacciones atómicas con rollback seguro.",
            "- **Contratos**: Garantizar consistencia en tipos de retorno y manejo explícito de errores.",
            "",
            "## 4. Plan de Implementación Paso a Paso",
            "1. **Preparación y Validación de Entorno**: Comprobar el estado de los tests actuales antes de comenzar.",
            "2. **Implementación de Modelos / Lógica Base**: Crear o extender las funciones de soporte necesarias.",
            "3. **Integración con la Interfaz de Usuario**: Conectar los nuevos flujos con widgets o controles interactivos.",
            "4. **Manejo de Errores y Casos Límite**: Validar entradas nulas, desconexiones o fallos en cascada.",
            "5. **Pruebas Automatizadas**: Crear tests unitarios dedicados con aserciones rigurosas.",
            "",
            "## 5. Casos Límite & Consideraciones de Seguridad",
            "- Prevenir bloqueos de UI delegando tareas pesadas a hilos secundarios (`QThread`).",
            "- Asegurar que las modificaciones no introduzcan regresiones en el flujo existente.",
            "- Manejar codificación UTF-8 e interoperabilidad multiplataforma.",
            "",
            "## 6. Criterios de Aceptación & Definición de Hecho (DoD)",
            "- [ ] Todas las tareas seleccionadas han sido implementadas de acuerdo a sus especificaciones.",
            "- [ ] La suite de pruebas unitarias pasa al 100% sin advertencias ni regresiones.",
            "- [ ] La documentación y comentarios de código reflejan los cambios introducidos.",
        ])

    elif mode == "user_stories":
        lines = [
            f"# HISTORIAS DE USUARIO: {initiative_title}",
            "",
            f"Documento de requerimientos ágiles derivado de **{task_count} tareas de backlog**.",
            "",
        ]
        for idx, t in enumerate(tasks, 1):
            title = t.get("title", "")
            desc = t.get("description", "").strip() or "Implementación requerida."
            lines.extend([
                f"## HU-{idx:02d}: {title}",
                "",
                "**Como** usuario del sistema,",
                f"**Quiero** {desc.lower() if len(desc) < 120 else title.lower()},",
                "**Para** optimizar el flujo de trabajo y productividad en el tablero.",
                "",
                "### Criterios de Aceptación (Gherkin):",
                "```gherkin",
                f"Escenario: Ejecución exitosa de {title}",
                "  Dado que el usuario accede a la sección correspondiente",
                "  Cuando realiza la acción prevista",
                "  Entonces el sistema responde de forma inmediata y persiste los cambios",
                "```",
                "",
            ])

    else:  # qa_tests
        lines = [
            f"# PLAN DE PRUEBAS & QA: {initiative_title}",
            "",
            f"Matriz de verificación técnica para **{task_count} tareas**.",
            "",
            "## Matriz de Casos de Prueba",
            "",
            "| ID | Tarea Evaluada | Tipo de Prueba | Precondición | Resultado Esperado |",
            "|---|---|---|---|---|",
        ]
        for idx, t in enumerate(tasks, 1):
            lines.append(
                f"| TC-{idx:02d} | {t.get('title', '')} | Funcional / Integración | Entorno listo | Cumple el criterio sin errores |"
            )
        lines.extend([
            "",
            "## Checklist de Verificación Manual",
            "- [ ] Comprobación visual y respuesta de la UI.",
            "- [ ] Validación con datos de prueba reales y entradas atípicas.",
            "- [ ] Comprobación de persistencia tras reiniciar la aplicación.",
        ])

    if custom_instructions:
        lines.extend([
            "",
            "---",
            "### Notas e Instrucciones Adicionales del Equipo:",
            f"> {custom_instructions}",
        ])

    return "\n".join(lines)


def stream_openai_chat_completion(
    endpoint: str,
    system_prompt: str,
    user_prompt: str,
    model_name: str = "qwen2.5-coder",
    timeout: float = 60.0
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
        for line in response:
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


class ModelDownloadThread(QThread):
    """Hilo para descargar en segundo plano el modelo Qwen 2.5 Coder con reporte de progreso."""
    progress = Signal(int, float, str)  # porcentaje, velocidad_mb_s, tiempo_restante_str
    download_finished = Signal(bool, str)  # exito, mensaje

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        ensure_directories()
        target_path = MODEL_PATH
        temp_path = MODEL_PATH + ".part"

        try:
            req = urllib.request.Request(
                MODEL_DOWNLOAD_URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EkinKanban/1.0"}
            )
            with urllib.request.urlopen(req, timeout=30.0) as response:
                total_bytes = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                start_time = time.time()
                last_update = start_time
                chunk_size = 1024 * 512  # 512 KB

                with open(temp_path, "wb") as out_file:
                    while True:
                        if self._is_cancelled:
                            out_file.close()
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                            self.download_finished.emit(False, "Descarga cancelada.")
                            return

                        chunk = response.read(chunk_size)
                        if not chunk:
                            break

                        out_file.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_update >= 0.4:
                            elapsed = now - start_time
                            speed_mb = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0.0
                            percent = int((downloaded / total_bytes) * 100) if total_bytes > 0 else 0
                            remaining_bytes = max(0, total_bytes - downloaded)
                            eta_sec = int(remaining_bytes / (speed_mb * 1024 * 1024)) if speed_mb > 0 else 0
                            eta_str = f"{eta_sec // 60}m {eta_sec % 60}s" if eta_sec >= 60 else f"{eta_sec}s"

                            self.progress.emit(percent, speed_mb, eta_str)
                            last_update = now

            # Renombrar atómicamente el archivo temporal
            if os.path.exists(target_path):
                os.remove(target_path)
            os.rename(temp_path, target_path)

            self.progress.emit(100, 0.0, "Completado")
            self.download_finished.emit(True, "Modelo descargado e instalado con éxito.")
        except Exception as e:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            self.download_finished.emit(False, f"Error durante la descarga: {e}")


class SpecGenerationThread(QThread):
    """Hilo para ejecutar la inferencia de la SPEC en segundo plano con soporte de streaming."""
    token_received = Signal(str)
    generation_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, tasks: list[dict], mode: str, custom_instructions: str = "", parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.mode = mode
        self.custom_instructions = custom_instructions
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        system_prompt, user_prompt = build_spec_prompts(self.tasks, self.mode, self.custom_instructions)
        detection = detect_available_llm()

        # Si hay un runner listo o que se puede arrancar:
        if detection["status"] == "can_start":
            start_managed_runner()
            detection = detect_available_llm()

        if detection["status"] == "ready":
            endpoint = detection["url"]
            accumulated = []
            try:
                for token in stream_openai_chat_completion(endpoint, system_prompt, user_prompt):
                    if self._is_cancelled:
                        return
                    accumulated.append(token)
                    self.token_received.emit(token)

                full_text = "".join(accumulated)
                if full_text.strip():
                    self.generation_finished.emit(full_text)
                    return
            except Exception:
                # Si falla la llamada HTTP a la IA, recurrir al generador estructural transparente
                pass

        # Fallback estructural rápido: garantizado 100% fiable y sin dependencias
        structural_spec = generate_structural_spec(self.tasks, self.mode, self.custom_instructions)
        # Emitir tokens en pequeños fragmentos para dar respuesta fluida
        lines = structural_spec.split("\n")
        for line in lines:
            if self._is_cancelled:
                return
            self.token_received.emit(line + "\n")
            time.sleep(0.01)

        self.generation_finished.emit(structural_spec)
