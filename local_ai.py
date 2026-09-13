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
import re
import sys
import json
import time
import urllib.request
import urllib.error
import atexit
import subprocess
import zipfile
from typing import Optional, Generator, Callable
from PySide6.QtCore import QThread, Signal
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


RUNNER_DOWNLOAD_URL = get_runner_download_url()

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



def _analyze_task_for_spec(task: dict) -> dict:
    """Realiza un análisis heurístico de la tarea para deducir el dominio arquitectónico,
    identificar componentes y generar un desglose técnico rico en lugar de un volcado plano."""
    title = task.get("title", "").strip() or "Tarea sin título"
    raw_desc = task.get("description", "")
    desc = clean_html_description(raw_desc) or "Sin descripción detallada proporcionada."
    combined = f"{title} {desc}".lower()

    domains = []
    if any(k in combined for k in ("api", "ree", "omie", "omip", "http", "request", "endpoint", "rest", "red", "crawler", "sync", "scrap", "json", "webhook", "curl", "url")):
        domains.append("Integración de Red & APIs Externas")
    if any(k in combined for k in ("db", "bd", "sql", "sqlite", "query", "migra", "persisten", "tabla", "modelo", "schema", "repositorio")):
        domains.append("Persistencia & Modelo de Datos")
    if any(k in combined for k in ("ui", "dialog", "boton", "botón", "interfaz", "widget", "vista", "pantalla", "menu", "css", "color", "render", "ventana", "layout", "toolbar")):
        domains.append("Interfaz de Usuario & Presentación (GUI)")
    if any(k in combined for k in ("test", "prueba", "qa", "cobertura", "assert", "mock", "validar", "escenario")):
        domains.append("Aseguramiento de Calidad & Tests")
    if any(k in combined for k in ("auth", "token", "seguridad", "cifrado", "password", "permiso", "login", "jwt", "credencial")):
        domains.append("Seguridad & Gestión de Accesos")
    if not domains:
        domains.append("Lógica de Dominio & Procesamiento Central")

    return {
        "title": title,
        "clean_desc": desc,
        "domain": " + ".join(domains),
        "links": task.get("links", [])
    }


def format_tasks_for_prompt(tasks: list[dict]) -> str:
    """Prepara un JSON estructurado con las tareas seleccionadas conteniendo
    ÚNICAMENTE título, descripción depurada y enlaces/adjuntos clasificados (descartando etiquetas, fechas y diario)."""
    cleaned = []
    for idx, t in enumerate(tasks, 1):
        clean_desc = clean_html_description(t.get("description", "")) or "Sin descripción detallada."

        links = []
        for link_item in t.get("links", []):
            url = link_item.get("url", "")
            is_local = (
                os.path.isabs(url)
                or (len(url) > 2 and url[1] == ":" and url[2] in ("/", "\\"))
                or url.startswith(("\\\\", "//"))
            )
            links.append({
                "label": link_item.get("label") or os.path.basename(url),
                "target": url,
                "type": "local_file" if is_local else "web_link"
            })

        analysis = _analyze_task_for_spec(t)
        cleaned.append({
            "task_number": idx,
            "title": t.get("title", ""),
            "inferred_domain": analysis["domain"],
            "description": clean_desc,
            "links": links
        })

    return json.dumps(cleaned, indent=2, ensure_ascii=False)


def build_spec_prompts(tasks: list[dict], mode: str = "sw_feature_plan", custom_instructions: str = "") -> tuple[str, str]:
    """Genera el system prompt y user prompt según el objetivo y plantilla seleccionada."""
    tasks_json = format_tasks_for_prompt(tasks)

    # Compatibilidad con identificadores previos
    if mode in ("coding_agent", "sw_feature_plan"):
        system_prompt = (
            "Eres un Arquitecto de Software Principal y Líder Técnico Senior especializado en preparar "
            "Especificaciones Técnicas (Feature Plans / Technical Specs) de alta precisión para Desarrolladores "
            "y Agentes Autónomos de IA (Google Antigravity, Claude Code, Cursor, Windsurf).\n"
            "Tu objetivo es transformar los requisitos y referencias en un plan de ingeniería exhaustivo, libre de ambigüedades, "
            "con arquitectura clara, contratos de datos, pasos de implementación ordenados y criterios de verificación."
        )
        user_prompt = f"""Analiza las siguientes tareas de desarrollo y sus referencias asociadas (enlaces y archivos locales) presentadas en JSON y elabora una ESPECIFICACIÓN TÉCNICA (FEATURE PLAN) completa:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}

INSTRUCCIONES DE ANÁLISIS EXHAUSTIVO (NO COPIAR Y PEGAR):
- No te limites a volcar los títulos y descripciones de las tareas.
- Analiza cada tarea en profundidad: deduce las capas arquitectónicas afectadas (persistencia, APIs de red, UI, lógica de dominio), identifica componentes clave y anticipa posibles cuellos de botella o fallos de conexión.
- Desglosa cada tarea en pasos atómicos de implementación con criterios de verificación concretos.

La especificación DEBE seguir rigurosamente esta estructura en Markdown:

# FEATURE PLAN: [Título Sintético de la Iniciativa]

## 1. Resumen Ejecutivo & Objetivo
- Propósito técnico y valor aportado.
- Alcance (Scope) y exclusiones explícitas (Out-of-Scope).

## 2. Desglose de Requisitos & Mapeo de Tareas
- Análisis técnico enriquecido de cada tarea y referencias adjuntas.
- Identificación de componentes y contratos afectados.
- Dependencias técnicas y orden crítico de ejecución.

## 3. Arquitectura del Sistema & Diseño de Componentes
- Módulos, servicios o archivos afectados.
- Esquema de base de datos / modelos de datos / contratos de interfaz (firmas de funciones clave).

## 4. Plan de Implementación Paso a Paso
- Secuencia de pasos atómicos de implementación que el desarrollador o agente de IA debe ejecutar en la codebase.

## 5. Casos Límite (Edge Cases), Errores & Seguridad
- Validaciones, manejo de fallos y condiciones de carrera a prever.

## 6. Criterios de Aceptación & Verificación (Definition of Done)
- Pruebas unitarias o de integración requeridas.
- Checklist de verificación paso a paso para dar la iniciativa por completada.
"""

    elif mode == "study_socratic":
        system_prompt = (
            "Eres un Tutor y Mentor Académico de Alto Rendimiento, especialista en el Método Socrático, "
            "Técnicas de Estudio Avanzadas (Active Recall, Técnica Feynman, Repetición Espaciada) y preparación "
            "de Oposiciones y Exámenes Oficiales.\n"
            "Tu objetivo es transformar los temas y referencias en un Plan de Estudio profundo, estructurado y "
            "estimulante que garantice la asimilación conceptual duradera."
        )
        user_prompt = f"""Analiza las siguientes materias, temas y referencias proporcionadas en JSON y elabora un PLAN DE ESTUDIO & EVALUACIÓN SOCRÁTICA exhaustivo:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}

Estructura el documento rigurosamente en Markdown:

# PLAN DE ESTUDIO & PREGUNTAS SOCRÁTICAS: [Tema / Materia Principal]

## 1. Resumen Conceptual & Síntesis Estructurada
- Marco teórico fundamental explicado con máxima claridad pedagógica.
- Ideas fuerza y principios esenciales.

## 2. Glosario de Conceptos Clave & Relaciones
- Definiciones precisas de los términos nucleares y sus interconexiones.

## 3. Esquema Mnemotécnico & Mapas Mentales
- Reglas de asociación mental, acrónimos o esquemas visuales para memorización a largo plazo.

## 4. Batería de Preguntas Socráticas de Autoevaluación
- Batería de preguntas desafiantes diseñadas para estimular la reflexión crítica (con sus correspondientes soluciones explicadas al detalle para autotest).

## 5. Supuestos Prácticos & Casos de Examen
- Ejercicios prácticos o preguntas tipo test/desarrollo representativas de examen real.
"""

    elif mode == "analyst_business":
        system_prompt = (
            "Eres un Consultor Estratégico Senior y Analista de Negocio y Operaciones especializado en "
            "evaluación de viabilidad, diseño de modelos de negocio, proyectos de montaje e innovación de producto.\n"
            "Tu objetivo es evaluar iniciativas y estructurar planes de viabilidad comercial, técnica y operativa rigurosos."
        )
        user_prompt = f"""Analiza las siguientes iniciativas, ideas o proyectos descritos en JSON junto con sus referencias y elabora un PLAN DE ANÁLISIS DE NEGOCIO Y VIABILIDAD completo:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}

Estructura el documento en Markdown con:

# PLAN DE NEGOCIO & ANÁLISIS DE VIABILIDAD: [Iniciativa Principal]

## 1. Resumen Ejecutivo & Propuesta de Valor
- Justificación del proyecto y propuesta de valor diferencial.

## 2. Análisis de Viabilidad Técnica, Operativa y de Mercado
- Factibilidad técnica, requerimientos de fabricación/montaje/desarrollo y demanda potencial.

## 3. Matriz DAFO (SWOT)
- Fortalezas, Oportunidades, Debilidades y Amenazas detalladas.

## 4. Desglose de Recursos, Materiales y Presupuesto
- Equipamiento, componentes, materiales, herramientas y estimación presupuestaria.

## 5. Matriz de Riesgos & Plan de Mitigación
- Riesgos operacionales, técnicos y financieros con sus medidas de contingencia.

## 6. Plan de Acción por Fases, Hitos y Métricas (KPIs)
- Cronograma de ejecución por etapas y métricas de éxito para validación.
"""

    elif mode == "user_stories":
        system_prompt = (
            "Eres un Product Owner y Agile Coach Senior especializado en Especificaciones de Requisitos.\n"
            "Tu objetivo es transformar los requerimientos en Historias de Usuario con criterios de aceptación Gherkin."
        )
        user_prompt = f"""Analiza las siguientes tareas en JSON y elabora historias de usuario con criterios Given-When-Then:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}
"""

    elif mode == "qa_tests":
        system_prompt = (
            "Eres un QA Lead y Test Architect Senior especializado en aseguramiento de calidad de software.\n"
            "Tu objetivo es diseñar una Matriz de Casos de Prueba exhaustiva y plan de pruebas automatizadas."
        )
        user_prompt = f"""Analiza las siguientes tareas en JSON y genera la Matriz de Casos de Prueba con escenarios límite:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}
"""

    elif mode == "task_breakdown":
        system_prompt = (
            "Eres un ingeniero senior que descompone una tarea en subtareas atómicas y accionables.\n"
            "Devuelve EXCLUSIVAMENTE una lista de títulos de subtarea, uno por línea, sin numeración, "
            "sin viñetas, sin markdown y sin texto introductorio ni de cierre."
        )
        user_prompt = f"""Descompón la siguiente tarea (en JSON) en subtareas concretas. Un título por línea:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}"""

    elif mode == "diary_summary":
        system_prompt = (
            "Eres un asistente que resume el diario de trabajo de una tarea de forma concisa y útil.\n"
            "Devuelve dos secciones en markdown: '## Qué se hizo' con viñetas de lo realizado y "
            "'## Siguiente paso' con la acción siguiente recomendada. Sin texto adicional."
        )
        user_prompt = f"""Resume el diario de la siguiente tarea (el texto del diario está en la descripción del JSON):

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}"""

    else:  # action_breakdown fallback
        system_prompt = (
            "Eres un Director de Proyectos Senior (PMP / Agile Coach) enfocado en ejecución operativa impecable.\n"
            "Tu objetivo es descomponer iniciativas complejas en planes de acción accionables paso a paso con hitos, "
            "dependencias y entregables claramente definidos."
        )
        user_prompt = f"""Analiza las siguientes tareas y referencias descritas en JSON y elabora un PLAN DE ACCIÓN Y DESGLOSE OPERATIVO detallado:

```json
{tasks_json}
```

{f"Instrucciones adicionales del usuario: {custom_instructions}" if custom_instructions else ""}

Estructura el documento en Markdown con:

# PLAN DE ACCIÓN & DESGLOSE OPERATIVO: [Objetivo de la Iniciativa]

## 1. Objetivo Global & Alcance del Plan
- Meta concreta a alcanzar y criterios de éxito.

## 2. Hitos Clave y Cronograma
- Fases temporales y momentos de entrega clave.

## 3. Desglose de Tareas Atómicas con Dependencias
- Acciones ordenadas paso a paso para cada una de las tareas especificadas.

## 4. Checklist de Entregables & Criterios de Aceptación
- Lista de verificación final para asegurar el cumplimiento del 100% de los requisitos.
"""

    return system_prompt, user_prompt


def generate_structural_spec(tasks: list[dict], mode: str = "sw_feature_plan", custom_instructions: str = "") -> str:
    """Generador offline instantáneo que sintetiza una SPEC estructurada sin necesidad de descargar el modelo."""
    task_count = len(tasks)
    initiative_title = " - ".join(t.get("title", "Tarea") for t in tasks[:3])
    if task_count > 3:
        initiative_title += f" (+{task_count - 3} tareas)"

    if mode in ("coding_agent", "sw_feature_plan"):
        header_title = f"# SPEC: {initiative_title}" if mode == "coding_agent" else f"# FEATURE PLAN: {initiative_title}"
        lines = [
            header_title,
            "",
            "## 1. Resumen Ejecutivo & Objetivo",
            f"Esta especificación técnica estructura **{task_count} tareas** seleccionadas para su ejecución técnica coordinada.",
            "",
            "- **Objetivo principal**: Implementar, verificar e integrar las tareas descritas manteniendo coherencia arquitectónica.",
            "- **Alcance**: Modificaciones en la lógica de negocio, interfaz de usuario y modelos de datos pertinentes.",
            "",
            "## 2. Desglose de Requisitos & Mapeo de Tareas",
            "",
        ]
        for idx, t in enumerate(tasks, 1):
            analysis = _analyze_task_for_spec(t)
            title = analysis["title"]
            desc = analysis["clean_desc"]
            domain = analysis["domain"]
            lines.append(f"### 2.{idx}. {title}")
            lines.append(f"- **Capa / Dominio Arquitectónico**: {domain}")
            lines.append(f"- **Análisis del Requerimiento**: {desc}")
            lines.append("- **Desglose Técnico & Pasos Operativos**:")
            lines.append(f"  1. *Modelado & Contratos*: Definir estructuras de datos, interfaces y firmas para `{title}`.")
            lines.append("  2. *Lógica Central*: Implementar procesamiento, validaciones y tratamiento de errores/fallos de red.")
            lines.append("  3. *Verificación & Testing*: Crear pruebas unitarias con casos nominales y escenarios límite.")
            lines.append("- **Criterios de Aceptación & DoD Específico**:")
            lines.append(f"  - [ ] Implementación de `{title}` completada sin regresiones.")
            lines.append("  - [ ] Validación mediante suite de tests automatizados al 100%.")
            links = analysis["links"]
            if links:
                links_str = ", ".join(f"[{lnk.get('label') or 'Enlace'}]({lnk.get('url', '')})" for lnk in links)
                lines.append(f"- **Referencias / Enlaces**: {links_str}")
            lines.append("")

        lines.extend([
            "## 3. Arquitectura del Sistema & Componentes Afectados",
            "- **Modularidad**: Separación de responsabilidades entre persistencia, lógica de dominio e interfaz.",
            "- **Persistencia**: Transacciones atómicas seguras y consistentes.",
            "- **Contratos**: Garantizar consistencia en tipos de retorno y manejo explícito de errores.",
            "",
            "## 4. Plan de Implementación Paso a Paso",
            "1. **Preparación de Entorno**: Validar la suite de pruebas antes de comenzar.",
            "2. **Lógica de Negocio / Modelos**: Implementar o extender las funciones de soporte requeridas.",
            "3. **Integración UI**: Conectar los nuevos flujos con widgets o controles interactivos.",
            "4. **Casos Límite**: Gestionar validaciones, desconexiones o entradas atípicas.",
            "5. **Pruebas Automatizadas**: Crear tests unitarios con aserciones exhaustivas.",
            "",
            "## 5. Casos Límite & Consideraciones de Seguridad",
            "- Mantener la fluidez de la UI delegando operaciones asíncronas.",
            "- Prevenir regresiones en flujos existentes.",
            "",
            "## 6. Criterios de Aceptación & Definición de Hecho (DoD)",
            "- [ ] Todas las tareas seleccionadas han sido implementadas de acuerdo a sus especificaciones.",
            "- [ ] La suite de pruebas unitarias pasa al 100% sin advertencias ni regresiones.",
            "- [ ] La documentación y comentarios reflejan fielmente los cambios introducidos.",
        ])

    elif mode == "study_socratic":
        lines = [
            f"# PLAN DE ESTUDIO & PREGUNTAS SOCRÁTICAS: {initiative_title}",
            "",
            f"Plan conceptual y batería de autoevaluación socrática para **{task_count} temas**.",
            "",
            "## 1. Resumen Conceptual & Síntesis",
        ]
        for idx, t in enumerate(tasks, 1):
            analysis = _analyze_task_for_spec(t)
            title = analysis["title"]
            desc = analysis["clean_desc"]
            domain = analysis["domain"]
            lines.append(f"### Tema {idx}: {title}")
            lines.append(f"- **Área Conceptual**: {domain}")
            lines.append(f"- **Síntesis del Contenido**: {desc}")
            lines.append("- **Puntos Nucleares para Active Recall**:")
            lines.append(f"  1. *Definición precisa*: Explicar con palabras propias qué es `{title}` y cuál es su principio fundamental.")
            lines.append("  2. *Mecanismo de acción*: Cómo interactúa con los conceptos adyacentes de su disciplina.")
            lines.append("  3. *Aplicación en supuesto real*: Resolver un problema práctico fundamentando cada decisión.")
            lines.append(f"- **Pregunta Socrática de Reflexión**: *¿Por qué `{title}` es crítico en este campo y qué fallo conceptual se cometería al ignorar sus premisas básicas?*")
            links = analysis["links"]
            if links:
                links_str = ", ".join(f"[{lnk.get('label') or 'Material'}]({lnk.get('url', '')})" for lnk in links)
                lines.append(f"- **Materiales / Fuentes**: {links_str}")
            lines.append("")

        lines.extend([
            "## 2. Batería de Preguntas Socráticas de Autoevaluación",
            "1. *¿Cuál es el principio subyacente que conecta los temas analizados y cómo se aplica a un caso real?*",
            "   - **Explicación**: El dominio conceptual exige distinguir la causa fundamental de los efectos secundarios.",
            "2. *¿Qué sucedería si se altera una de las variables o premisas básicas planteadas?*",
            "   - **Explicación**: Permite verificar la solidez del razonamiento y detectar lagunas teóricas.",
            "",
            "## 3. Reglas Mnemotécnicas & Consejos de Fijación",
            "- Aplicar active recall mediante explicaciones en voz alta con palabras propias.",
            "- Relacionar cada término técnico con una analogía práctica visualizable.",
        ])

    elif mode == "analyst_business":
        lines = [
            f"# PLAN DE NEGOCIO & ANÁLISIS DE VIABILIDAD: {initiative_title}",
            "",
            f"Análisis estratégico y de recursos para **{task_count} iniciativas**.",
            "",
            "## 1. Resumen Ejecutivo & Propuesta de Valor",
            "Evaluación de viabilidad y requerimientos operativos para la ejecución exitosa de la iniciativa.",
            "",
            "## 2. Matriz DAFO (SWOT)",
            "- **Fortalezas (F)**: Dominio técnico, herramientas disponibles y alcance acotado.",
            "- **Oportunidades (O)**: Automatización, escalabilidad y optimización de flujos.",
            "- **Debilidades (D)**: Curva de aprendizaje inicial o dependencias externas.",
            "- **Amenazas (A)**: Tiempos de entrega ajustados o cambios imprevistos en requisitos.",
            "",
            "## 3. Recursos & Plan de Acción",
        ]
        for idx, t in enumerate(tasks, 1):
            analysis = _analyze_task_for_spec(t)
            title = analysis["title"]
            desc = analysis["clean_desc"]
            domain = analysis["domain"]
            lines.append(f"### Fase {idx}: {title}")
            lines.append(f"- **Área de Impacto**: {domain}")
            lines.append(f"- **Diagnóstico de Necesidad**: {desc}")
            lines.append("- **Plan de Ejecución & Recursos**:")
            lines.append(f"  1. *Evaluación previa*: Cuantificar viabilidad técnica y dependencias operativas de `{title}`.")
            lines.append("  2. *Despliegue operativo*: Asignar herramientas, responsables y cronograma de hitos.")
            lines.append("  3. *Control de calidad*: Pruebas de aceptación y mitigación de desviaciones de presupuesto/tiempo.")
            lines.append(f"- **Métrica Clave (KPI)**: Entregable de `{title}` operativo con 100% de cumplimiento funcional.")
            links = analysis["links"]
            if links:
                links_str = ", ".join(f"[{lnk.get('label') or 'Referencia'}]({lnk.get('url', '')})" for lnk in links)
                lines.append(f"- **Fuentes / Documentación**: {links_str}")
            lines.append("")

    elif mode == "task_breakdown":
        lines = suggest_subtasks_offline(tasks[0]) if tasks else []

    elif mode == "diary_summary":
        desc = clean_html_description(tasks[0].get("description", "")) if tasks else ""
        paras = [p.strip() for p in desc.splitlines() if p.strip()]
        lines = [f"## {_t('ai.summary.what_happened')}"]
        lines += [f"- {p[:200]}" for p in paras[-6:]] or [f"- {_t('ai.summary.empty')}"]
        lines += ["", f"## {_t('ai.summary.next_step')}", f"- {paras[-1][:200] if paras else ''}"]

    else:  # action_breakdown / user_stories / qa_tests
        lines = [
            f"# PLAN DE ACCIÓN & DESGLOSE OPERATIVO: {initiative_title}",
            "",
            f"Desglose táctico de ejecución para **{task_count} tareas**.",
            "",
            "## Desglose de Acciones por Tarea",
            "",
        ]
        for idx, t in enumerate(tasks, 1):
            analysis = _analyze_task_for_spec(t)
            title = analysis["title"]
            desc = analysis["clean_desc"]
            domain = analysis["domain"]
            lines.append(f"### Acción {idx}: {title}")
            lines.append(f"- **Ámbito Operativo**: {domain}")
            lines.append(f"- **Alcance & Objetivo**: {desc}")
            lines.append("- **Sub-tareas Atómicas**:")
            lines.append(f"  1. Preparación de entorno y dependencias para `{title}`.")
            lines.append("  2. Ejecución directa del desarrollo o actividad operativa.")
            lines.append("  3. Verificación de calidad, revisión de resultados y cierre formal.")
            lines.append(f"- **Entregable Verificable**: Hito `{title}` completado y validado.")
            links = analysis["links"]
            if links:
                links_str = ", ".join(f"[{lnk.get('label') or 'Referencia'}]({lnk.get('url', '')})" for lnk in links)
                lines.append(f"- **Recursos / Enlaces**: {links_str}")
            lines.append("")

    if custom_instructions:
        lines.extend([
            "---",
            f"**Instrucciones Adicionales**: {custom_instructions}",
            "",
        ])

    return "\n".join(lines)


# --- Ayudantes de flujo por tarea (offline, deterministas) -------------------
# Usados por la vista de detalle de tarea: desglose en subtareas y resumen del diario.
# Son 100% offline (mismo espíritu que el sintetizador estructural), por lo que funcionan
# sin descargar el modelo. Lógica pura -> probada sin bucle de eventos.

def suggest_subtasks_offline(task: dict) -> list[str]:
    """Descompone una tarea en títulos de subtareas (tareas hermanas) de forma
    determinista. Si la descripción trae viñetas/líneas, las usa; si no, genera un
    desglose por fases (Planificar / Implementar / Verificar)."""
    title = (task.get("title") or "").strip() or _t("ai.breakdown.default_title")
    desc = clean_html_description(task.get("description", "") or "")
    items = parse_subtask_lines(desc)
    if items:
        return items[:8]
    return [
        _t("ai.breakdown.phase_plan", title=title),
        _t("ai.breakdown.phase_implement", title=title),
        _t("ai.breakdown.phase_verify", title=title),
    ]


def parse_subtask_lines(text: str) -> list[str]:
    """Convierte un texto (una tarea por línea) en títulos limpios: quita viñetas,
    numeración y markdown, y descarta líneas vacías o de cabecera (#). Se reutiliza al
    aceptar el desglose para crear las tareas."""
    titles = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        line = line.lstrip("-*•").strip()
        line = re.sub(r"^\d+[.)]\s*", "", line).strip()
        line = line.strip("`").strip()
        if line:
            titles.append(line[:200])
    return titles


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


def stream_openai_chat_completion(
    endpoint: str,
    system_prompt: str,
    user_prompt: str,
    model_name: str = "qwen2.5-coder",
    timeout: float = 60.0,
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


class RunnerDownloadThread(QThread):
    """Hilo para descargar y extraer en segundo plano el ejecutable portable de llama-server."""
    progress = Signal(int, float, str)  # porcentaje, velocidad_mb_s, tiempo_restante_str
    download_finished = Signal(bool, str)  # exito, mensaje

    def __init__(self, runner_url: Optional[str] = None, runner_dir: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.runner_url = runner_url
        self.runner_dir = runner_dir
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        ensure_directories()
        success, msg = download_and_extract_runner(
            runner_url=self.runner_url,
            runner_dir=self.runner_dir,
            cancel_check=lambda: self._is_cancelled,
            progress_callback=lambda p, s, eta: self.progress.emit(p, s, eta),
        )
        self.download_finished.emit(success, msg)


class SpecGenerationThread(QThread):
    """Hilo para ejecutar la inferencia de la SPEC en segundo plano con soporte de streaming."""
    token_received = Signal(str)
    generation_finished = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, tasks: list[dict], mode: str, custom_instructions: str = "", model_name: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.tasks = tasks
        self.mode = mode
        self.custom_instructions = custom_instructions
        self.model_name = model_name
        self._is_cancelled = False
        self._active_response = None

    def cancel(self):
        self._is_cancelled = True
        if self._active_response is not None:
            try:
                self._active_response.close()
            except Exception:
                pass

    def run(self):
        system_prompt, user_prompt = build_spec_prompts(self.tasks, self.mode, self.custom_instructions)
        detection = detect_available_llm()

        # Si hay un runner listo o que se puede arrancar:
        if detection["status"] == "can_start":
            start_managed_runner()
            detection = detect_available_llm()

        fallback_warning = ""

        if detection["status"] == "ready":
            endpoint = detection["url"]
            target_model = self.model_name
            if not target_model:
                target_model = "qwen2.5-coder"
            accumulated = []
            try:
                def _store_resp(resp):
                    self._active_response = resp

                for token in stream_openai_chat_completion(
                    endpoint,
                    system_prompt,
                    user_prompt,
                    model_name=target_model,
                    cancel_check=lambda: self._is_cancelled,
                    on_response=_store_resp,
                ):
                    if self._is_cancelled:
                        return
                    accumulated.append(token)
                    self.token_received.emit(token)

                full_text = "".join(accumulated)
                if full_text.strip():
                    self.generation_finished.emit(full_text)
                    return
            except Exception as exc:
                if self._is_cancelled:
                    return
                # Si ya se emitieron tokens a la interfaz, emitir error_occurred en lugar de
                # concatenar el fallback estructural sobre una respuesta a medias.
                if accumulated:
                    self.error_occurred.emit(f"Error durante la inferencia con '{target_model}': {exc}")
                    return
                # Si falló antes de emitir ningún token, preparamos un aviso informativo visible
                fallback_warning = (
                    f"> ⚠️ **Aviso**: No se pudo generar con el modelo '{target_model}' ({exc}). "
                    f"Se ha recurrido al sintetizador estructural local.\n\n"
                )
            finally:
                self._active_response = None

        if self._is_cancelled:
            return

        # Fallback estructural rápido: garantizado 100% fiable y sin dependencias
        structural_spec = generate_structural_spec(self.tasks, self.mode, self.custom_instructions)
        full_spec = fallback_warning + structural_spec if fallback_warning else structural_spec

        lines = full_spec.split("\n")
        for line in lines:
            if self._is_cancelled:
                return
            self.token_received.emit(line + "\n")
            time.sleep(0.01)

        self.generation_finished.emit(full_spec)
