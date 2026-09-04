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


def test_get_ollama_models_and_spec_dialog_model_selector(monkeypatch, qapp, db_path):
    import database
    from ai_spec_dialog import AiSpecDialog

    class FakeResponse:
        status = 200
        def read(self):
            import json
            return json.dumps({
                "models": [
                    {"name": "llama3.2:latest"},
                    {"name": "qwen2.5-coder:7b"},
                    {"name": "mistral:latest"}
                ]
            }).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=1.0: FakeResponse())
    monkeypatch.setattr(local_ai, "check_http_endpoint", lambda url, timeout=0.5: "11434" in url)

    models = local_ai.get_ollama_models()
    assert models == ["llama3.2:latest", "qwen2.5-coder:7b", "mistral:latest"]

    board_id = database.create_board("Board AI", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    t1 = database.create_task(col_id, "Task 1", db_path=db_path)

    dlg = AiSpecDialog([t1], board_id, db_path)
    assert dlg.model_combo.isHidden() is False
    assert dlg.model_combo.count() == 3
    assert dlg.model_combo.currentText() == "qwen2.5-coder:7b"
    dlg.reject()


def test_spec_dialog_model_selector_always_visible_when_ollama_offline(monkeypatch, qapp, db_path):
    """Verifica que el selector de modelos de Ollama SIEMPRE esté visible y editable aunque Ollama no esté corriendo."""
    import database
    from ai_spec_dialog import AiSpecDialog

    monkeypatch.setattr(local_ai, "get_ollama_models", lambda *a, **k: [])
    monkeypatch.setattr(local_ai, "check_http_endpoint", lambda *a, **k: False)

    board_id = database.create_board("Board Offline", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    t1 = database.create_task(col_id, "Task Offline", db_path=db_path)

    dlg = AiSpecDialog([t1], board_id, db_path)
    assert dlg.model_label.isHidden() is False
    assert dlg.model_combo.isHidden() is False
    assert dlg.refresh_models_btn.isHidden() is False
    assert dlg.model_combo.isEditable() is True
    assert dlg.model_combo.count() >= 5
    assert "qwen2.5-coder:1.5b" in [dlg.model_combo.itemText(i) for i in range(dlg.model_combo.count())]

    # Verificar que el botón de refresco funciona sin errores
    dlg.refresh_models_btn.click()
    assert dlg.model_combo.isHidden() is False
    dlg.reject()


def test_spec_generation_thread_error_handling_and_cancellation(monkeypatch, qapp):
    """Verifica que un fallo a mitad de streaming emita error_occurred sin corromper el buffer,
    y que la cancelación cierre el socket/respuesta."""
    tasks = [{"id": 1, "title": "Test Task", "description": "Desc", "column_name": "Col"}]
    thread = local_ai.SpecGenerationThread(tasks, mode="coding_agent", model_name="test-model")

    class FakeBrokenResponse:
        def __init__(self):
            self.closed = False
        def close(self):
            self.closed = True
        def __iter__(self):
            yield b'data: {"choices":[{"delta":{"content":"Primer token"}}]}\n'
            raise ConnectionResetError("Connection lost mid-stream")
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=60.0: FakeBrokenResponse())
    monkeypatch.setattr(local_ai, "detect_available_llm", lambda: {"status": "ready", "url": "http://127.0.0.1:11434", "type": "ollama"})

    emitted_tokens = []
    errors = []
    finished = []

    thread.token_received.connect(emitted_tokens.append)
    thread.error_occurred.connect(errors.append)
    thread.generation_finished.connect(finished.append)

    thread.run()

    # Debe haber emitido el token inicial
    assert "Primer token" in emitted_tokens
    # Debe haber emitido error_occurred
    assert len(errors) == 1
    assert "Connection lost mid-stream" in errors[0]
    # No debe haber invocado finished con la spec estructural sobreescrita
    assert len(finished) == 0

    # Probar cancelación inmediata
    thread2 = local_ai.SpecGenerationThread(tasks, mode="coding_agent")
    fake_resp = FakeBrokenResponse()
    thread2._active_response = fake_resp
    thread2.cancel()
    assert thread2._is_cancelled is True
    assert fake_resp.closed is True


