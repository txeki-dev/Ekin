"""
Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py).
"""

import local_ai


def test_format_tasks_for_prompt():
    tasks = [
        {
            "id": 1,
            "title": "OAuth2 con Google",
            "column_name": "Backlog",
            "description": "Implementar flujo PKCE para autenticación.",
            "due_date": "2026-10-01",
            "tags": [{"category": "AUTH", "value": "SECURITY", "color": "#ef4444"}],
            "logs": [{"content": "Nota: verificar redirección en localhost."}],
        },
        {
            "id": 2,
            "title": "Persistir Tokens en SQLite",
            "column_name": "En Progreso",
            "description": "Guardar refresh tokens cifrados.",
            "due_date": None,
            "tags": [],
            "logs": [],
        },
    ]

    formatted = local_ai.format_tasks_for_prompt(tasks)
    assert "OAuth2 con Google" in formatted
    assert "Backlog" in formatted
    assert "AUTH:SECURITY" in formatted
    assert "verificar redirección" in formatted
    assert "Persistir Tokens en SQLite" in formatted


def test_build_spec_prompts_coding_agent():
    tasks = [{"id": 1, "title": "Crear API REST", "description": "Endpoints FastAPI"}]
    sys_prompt, user_prompt = local_ai.build_spec_prompts(tasks, mode="coding_agent", custom_instructions="Usa Pydantic v2")

    assert "Arquitecto de Software Principal" in sys_prompt
    assert "Crear API REST" in user_prompt
    assert "Usa Pydantic v2" in user_prompt
    assert "Plan de Implementación Paso a Paso" in user_prompt


def test_build_spec_prompts_user_stories():
    tasks = [{"id": 1, "title": "Filtro de búsqueda", "description": "Buscar por fecha"}]
    sys_prompt, user_prompt = local_ai.build_spec_prompts(tasks, mode="user_stories")

    assert "Product Owner" in sys_prompt
    assert "Filtro de búsqueda" in user_prompt
    assert "Gherkin" in user_prompt or "Given-When-Then" in user_prompt


def test_build_spec_prompts_qa_tests():
    tasks = [{"id": 1, "title": "Cálculo de impuestos", "description": "Aplicar 21% IVA"}]
    sys_prompt, user_prompt = local_ai.build_spec_prompts(tasks, mode="qa_tests")

    assert "QA Lead" in sys_prompt
    assert "Matriz de Casos de Prueba" in user_prompt


def test_generate_structural_spec_offline():
    tasks = [
        {"id": 1, "title": "Login con Google", "description": "Flujo OAuth2", "column_name": "Backlog", "tags": []},
        {"id": 2, "title": "Registro de Auditoría", "description": "Log de accesos", "column_name": "Backlog", "tags": []},
    ]
    spec = local_ai.generate_structural_spec(tasks, mode="coding_agent", custom_instructions="Seguridad estricta")

    assert "# SPEC: Login con Google - Registro de Auditoría" in spec
    assert "## 1. Resumen Ejecutivo & Objetivo" in spec
    assert "### 2.1. Login con Google" in spec
    assert "### 2.2. Registro de Auditoría" in spec
    assert "## 4. Plan de Implementación Paso a Paso" in spec
    assert "Seguridad estricta" in spec


def test_detect_available_llm():
    status = local_ai.detect_available_llm()
    assert "status" in status
    assert "type" in status
    assert "name" in status
