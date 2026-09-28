"""
Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi:
- Fase 1: Datos de Standup que alimentan el resumen ejecutivo del MCP.
- Fase 2: Motor de Embeddings & Búsqueda Semántica (Pilar 3).
- Fase 3: Escudo de Privacidad & Condensador MCP (Pilar 4).
"""

import math
from datetime import datetime, timedelta
import pytest
import database
import local_ai
import privacy_shield
import mcp_server


# =====================================================================
# FASE 1: DATOS DE STANDUP (RESUMEN EJECUTIVO MCP)
# =====================================================================

def test_generate_daily_standup_data_and_markdown(db_path):
    board_id = database.create_board("Proyecto Alpha", color="#10b981", db_path=db_path)
    database.create_column(board_id, "To Do", db_path=db_path)
    col_wip = database.create_column(board_id, "In Progress", wip_limit=1, db_path=db_path)
    col_done = database.create_column(board_id, "Done", db_path=db_path)

    # Tarea completada hoy
    database.create_task(col_done, "Tarea Finalizada", db_path=db_path)

    # Dos tareas en WIP (provocará exceso de límite WIP ya que límite es 1)
    t_wip1 = database.create_task(col_wip, "Tarea Activa 1", db_path=db_path)
    database.create_task(col_wip, "Tarea Activa 2", db_path=db_path)

    # Simular que t_wip1 lleva 5 días inactiva
    past_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
    with database.get_connection(db_path) as conn:
        conn.execute("UPDATE tasks SET updated_at = ? WHERE id = ?", (past_date, t_wip1))

    data = local_ai.generate_daily_standup_data(board_id, db_path=db_path)
    assert data["board_name"] == "Proyecto Alpha"
    assert data["total_tasks"] == 3
    assert len(data["completed_recently"]) == 1
    assert len(data["in_progress"]) == 2
    assert len(data["stagnant"]) == 1
    assert len(data["wip_violations"]) == 1

    md = local_ai.format_daily_standup_markdown(data, "Proyecto Alpha")
    assert "Daily Standup — Proyecto Alpha" in md
    assert "Completado recientemente" in md
    assert "Tarea Finalizada" in md
    assert "En curso / Próximo foco" in md
    assert "Bloqueos / Tareas estancadas" in md
    assert "exceso WIP" in md or "límite WIP" in md.lower()


# =====================================================================
# FASE 2: MOTOR DE EMBEDDINGS & BÚSQUEDA SEMÁNTICA (PILAR 3)
# =====================================================================

def test_database_task_embeddings_crud(db_path):
    board_id = database.create_board("Board Vector", db_path=db_path)
    col_id = database.create_column(board_id, "Backlog", db_path=db_path)
    t_id = database.create_task(col_id, "Tarea de Prueba", db_path=db_path)

    vec = [0.1, 0.2, 0.3, 0.4]
    database.save_task_embedding(t_id, vec, model_name="test_model", db_path=db_path)

    retrieved = database.get_task_embedding(t_id, db_path=db_path)
    assert retrieved is not None
    assert len(retrieved) == 4
    for a, b in zip(vec, retrieved):
        assert pytest.approx(a, 0.001) == b

    board_embs = database.get_board_embeddings(board_id, db_path=db_path)
    assert len(board_embs) == 1
    assert board_embs[0][0] == t_id

    database.delete_task_embedding(t_id, db_path=db_path)
    assert database.get_task_embedding(t_id, db_path=db_path) is None


def test_compute_fallback_embedding_and_cosine_similarity():
    # Vector normalizado unitario
    v1 = local_ai.compute_fallback_embedding("Error en la conexión a la base de datos sqlite")
    norm1 = math.sqrt(sum(x * x for x in v1))
    assert pytest.approx(norm1, 0.0001) == 1.0

    # Texto similar semántica/léxicamente
    v2 = local_ai.compute_fallback_embedding("Fallo de conexión en base datos sqlite")
    # Texto totalmente distinto
    v3 = local_ai.compute_fallback_embedding("Diseñar logotipo de colores pastel para la app")

    sim_similar = local_ai.cosine_similarity(v1, v2)
    sim_distinct = local_ai.cosine_similarity(v1, v3)

    assert sim_similar > 0.40
    assert sim_similar > sim_distinct
    assert local_ai.cosine_similarity(v1, v1) == pytest.approx(1.0, 0.0001)
    assert local_ai.cosine_similarity([], v1) == 0.0


def test_semantic_search_tasks_and_find_duplicates(db_path):
    board_id = database.create_board("Board Search", db_path=db_path)
    col_id = database.create_column(board_id, "Dev", db_path=db_path)

    t1 = database.create_task(col_id, "Problemas de CORS en el servidor local", description="Cabeceras HTTP cruzadas", db_path=db_path)
    t2 = database.create_task(col_id, "Diseño de la paleta de colores del tema oscuro", description="Estilos CSS", db_path=db_path)
    database.create_task(col_id, "Autenticación mediante tokens JWT seguros", description="Bearer tokens", db_path=db_path)

    # Búsqueda semántica por concepto
    results = local_ai.semantic_search_tasks("Fallo con cabeceras CORS de red", board_id=board_id, top_k=5, db_path=db_path)
    assert len(results) >= 1
    # La tarea t1 debe ser la primera por relevancia
    assert results[0]["id"] == t1
    assert "similarity" in results[0]

    # Detector de duplicados
    dups = local_ai.find_duplicate_tasks(
        "Problemas con CORS en servidor",
        description="Cabeceras HTTP",
        board_id=board_id,
        threshold=0.60,
        exclude_task_id=None,
        db_path=db_path
    )
    assert len(dups) >= 1
    assert dups[0]["id"] == t1
    assert dups[0]["id"] != t2


# =====================================================================
# FASE 3: ESCUDO DE PRIVACIDAD & CONDENSADOR MCP (PILAR 4)
# =====================================================================

def test_privacy_shield_sanitization():
    # OpenAI key
    text_openai = "Usa esta clave sk-abcdef1234567890ABCDEF para llamar a la API."
    san_openai, red_openai = privacy_shield.sanitize_text(text_openai)
    assert "[REDACTED_OPENAI_API_KEY]" in san_openai
    assert "sk-" not in san_openai
    assert len(red_openai) == 1

    # GitHub token
    text_gh = "Token de GitHub: ghp_123456789012345678901234567890123456."
    san_gh, _ = privacy_shield.sanitize_text(text_gh)
    assert "[REDACTED_GITHUB_TOKEN]" in san_gh

    # Email
    text_email = "Contactar con soporte@example.com o admin@test.org para dudas."
    san_email, red_email = privacy_shield.sanitize_text(text_email, mask_email=True)
    assert "[REDACTED_EMAIL]" in san_email
    assert "soporte@example.com" not in san_email

    # Clave privada RSA multilínea
    rsa_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0mockkey...\n-----END RSA PRIVATE KEY-----"
    san_rsa, _ = privacy_shield.sanitize_text(f"Config: {rsa_key}")
    assert "[REDACTED_PRIVATE_KEY]" in san_rsa
    assert "BEGIN RSA PRIVATE KEY" not in san_rsa

    # URL con credenciales
    url_text = "Conectar a postgresql://admin:superpassword123@db.internal:5432/production"
    san_url, _ = privacy_shield.sanitize_text(url_text)
    assert "[REDACTED_PASSWORD]" in san_url
    assert "superpassword123" not in san_url

    # Verificación rápida con has_sensitive_data
    assert privacy_shield.has_sensitive_data("sk-12345678901234567890ABC")
    assert not privacy_shield.has_sensitive_data("Texto normal sin ningún secreto")


def test_mcp_new_tools_and_mask_sensitive(db_path):
    board_id = database.create_board("Tablero MCP Test", db_path=db_path)
    database.set_board_mcp_config(board_id, True, secret="mcp_secret_pass", db_path=db_path)
    col_id = database.create_column(board_id, "Desarrollo", db_path=db_path)

    # Tarea con información confidencial
    t_secret = database.create_task(
        col_id,
        "Configurar backend con sk-123456789012345678901234",
        description="Enviar emails a contacto@empresa.com usando sk-abcdef1234567890123456.",
        db_path=db_path,
    )
    database.create_log(t_secret, "<p>Log con token secreto sk-secrettoken1234567890</p>", db_path=db_path)

    board_info = database.get_board(board_id, db_path=db_path)
    executor = mcp_server.McpToolExecutor(board_info, db_path=db_path)

    # 1. get_board_executive_summary
    res_exec = executor.execute("get_board_executive_summary", {"mask_sensitive": True})
    content_exec = res_exec["content"][0]["text"]
    assert "executive_markdown" in content_exec
    assert "sk-" not in content_exec  # Sanitizado

    # 2. get_task_condensed_context
    res_condensed = executor.execute("get_task_condensed_context", {"task_id": t_secret, "mask_sensitive": True})
    content_condensed = res_condensed["content"][0]["text"]
    assert "[REDACTED_OPENAI_API_KEY]" in content_condensed
    assert "[REDACTED_EMAIL]" in content_condensed
    assert "journal_summary" in content_condensed

    # 3. sanitize_text
    res_san = executor.execute("sanitize_text", {"text": "Clave sk-98765432109876543210"})
    content_san = res_san["content"][0]["text"]
    assert "[REDACTED_OPENAI_API_KEY]" in content_san

    # 4. get_task con mask_sensitive=True
    res_task = executor.execute("get_task", {"task_id": t_secret, "mask_sensitive": True})
    assert "[REDACTED_OPENAI_API_KEY]" in res_task["content"][0]["text"]

    # 5. list_tasks con mask_sensitive=True
    res_list = executor.execute("list_tasks", {"mask_sensitive": True})
    assert "[REDACTED_OPENAI_API_KEY]" in res_list["content"][0]["text"]


# =====================================================================
# FASE 4: RESILIENCIA - CIRCUIT BREAKER LOCAL AI
# =====================================================================

def test_local_ai_circuit_breaker_lifecycle():
    import time

    cb = local_ai.LocalAiCircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_CLOSED
    assert cb.allow_request() is True

    # 1. Primer fallo: sigue CLOSED
    cb.record_failure()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_CLOSED
    assert cb.allow_request() is True

    # 2. Segundo fallo: supera el umbral y pasa a OPEN
    cb.record_failure()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_OPEN
    assert cb.allow_request() is False

    # 3. Esperar cooldown para pasar a HALF_OPEN
    time.sleep(0.12)
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_HALF_OPEN
    assert cb.allow_request() is True

    # 4. Fallo en HALF_OPEN: vuelve inmediatamente a OPEN
    cb.record_failure()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_OPEN
    assert cb.allow_request() is False

    # 5. Esperar cooldown y éxito en HALF_OPEN -> vuelve a CLOSED
    time.sleep(0.12)
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_HALF_OPEN
    cb.record_success()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_CLOSED
    assert cb.allow_request() is True

    # 6. Reset manual
    cb.record_failure()
    cb.record_failure()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_OPEN
    cb.reset()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_CLOSED
    assert cb.allow_request() is True


def test_circuit_breaker_embedding_fast_fail(monkeypatch):
    cb = local_ai.get_llm_circuit_breaker()
    cb.reset()

    # Forzar estado OPEN en el circuit breaker global
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == local_ai.LocalAiCircuitBreaker.STATE_OPEN

    # Mockear is_ollama_available para asegurar que NO se llama al estar OPEN
    called = []
    def fake_ollama():
        called.append(True)
        return True

    monkeypatch.setattr(local_ai, "is_ollama_available", fake_ollama)

    # get_local_embedding debe derivar inmediatamente al fallback sin acceder a la red
    vec = local_ai.get_local_embedding("Texto de prueba de resiliencia")
    assert len(vec) == 128
    assert len(called) == 0

    cb.reset()

