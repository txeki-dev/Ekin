"""
Pruebas exhaustivas para la Nueva Suite de IA Local Autónoma & RDi:
- Fase 1: Ergonomía de Tarjetas & Standup (Pilares 1 y 2).
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
# FASE 1: ERGONOMÍA DE TARJETAS & STANDUP (PILARES 1 Y 2)
# =====================================================================

def test_extract_checklist_offline_various_inputs():
    # 1. Fallback vacío
    empty_items = local_ai.extract_checklist_offline("")
    assert len(empty_items) >= 2
    assert any("Requisitos" in it or "requisitos" in it.lower() for it in empty_items)

    # 2. Texto con checkboxes existentes
    chk_text = "- [ ] Configurar auth\n- [x] Crear endpoints\n* [ ] Escribir tests"
    chk_items = local_ai.extract_checklist_offline(chk_text)
    assert chk_items == ["Configurar auth", "Crear endpoints", "Escribir tests"]

    # 3. Texto con viñetas estándar
    bullet_text = "- Instalar dependencias\n* Configurar base de datos\n1. Validar esquema"
    bullet_items = local_ai.extract_checklist_offline(bullet_text)
    assert bullet_items == ["Instalar dependencias", "Configurar base de datos", "Validar esquema"]

    # 4. Párrafo de texto libre
    para_text = (
        "Es necesario implementar la autenticación mediante token JWT. "
        "Se debe verificar la caducidad del token en cada petición. "
        "Finalmente, añadir pruebas unitarias exhaustivas."
    )
    para_items = local_ai.extract_checklist_offline(para_text)
    assert len(para_items) >= 2
    assert any("autenticación" in it.lower() for it in para_items)


def test_build_spec_prompts_and_structural_spec_new_modes():
    tasks = [{"title": "Tarea A", "description": "- [ ] Sub A1\n- [ ] Sub A2", "links": []}]

    # Modo extract_checklist
    sys_p, usr_p = local_ai.build_spec_prompts(tasks, mode="extract_checklist")
    assert "criterios de aceptación" in sys_p.lower()
    assert "- [ ]" in usr_p

    spec_chk = local_ai.generate_structural_spec(tasks, mode="extract_checklist")
    assert "- [ ] Sub A1" in spec_chk
    assert "- [ ] Sub A2" in spec_chk

    # Modo daily_standup
    sys_stand, usr_stand = local_ai.build_spec_prompts(tasks, mode="daily_standup")
    assert "daily standup" in sys_stand.lower()
    spec_stand = local_ai.generate_structural_spec(tasks, mode="daily_standup")
    assert "Daily Standup" in spec_stand


def test_suggest_tags_offline():
    # Coincidencia con taxonomía estándar
    tags_bug = local_ai.suggest_tags_offline("Error al iniciar sesión", "Ocurre un crash al recibir null")
    assert "bug" in tags_bug
    assert "security" in tags_bug or "auth" in tags_bug

    tags_ui = local_ai.suggest_tags_offline("Rediseño del diálogo", "Cambiar color del botón y layout")
    assert "ui" in tags_ui

    tags_api = local_ai.suggest_tags_offline("Nuevo endpoint REST", "Crear ruta HTTP para sincronización")
    assert "api" in tags_api

    # Coincidencia con etiquetas del tablero existentes
    available = ["Sprint-24", "Billing", "Frontend"]
    custom_suggested = local_ai.suggest_tags_offline("Ajustes de Billing en el sprint", "Trabajo en Frontend", available_tags=available)
    assert "Billing" in custom_suggested
    assert "Frontend" in custom_suggested


def test_suggest_conventional_title():
    # Título ya formateado
    assert local_ai.suggest_conventional_title("fix(ui): botón roto") == "fix(ui): botón roto"
    assert local_ai.suggest_conventional_title("FEAT: nueva vista") == "feat: nueva vista"

    # Detección de bug
    t_bug = local_ai.suggest_conventional_title("Error en el login al conectar")
    assert t_bug.startswith("fix")

    # Detección de pruebas
    t_test = local_ai.suggest_conventional_title("Añadir tests para la base de datos")
    assert t_test.startswith("test")

    # Detección de documentación
    t_doc = local_ai.suggest_conventional_title("Actualizar el readme y manual de usuario")
    assert t_doc.startswith("docs")

    # Detección de refactor
    t_ref = local_ai.suggest_conventional_title("Limpiar y refactorizar código de sync")
    assert t_ref.startswith("refactor")


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


def test_daily_standup_dialog_ui(qapp, db_path):
    from daily_standup_dialog import DailyStandupDialog
    board_id = database.create_board("Tablero Standup", db_path=db_path)
    col_id = database.create_column(board_id, "In Progress", db_path=db_path)
    database.create_task(col_id, "Desarrollar feature", db_path=db_path)

    dlg = DailyStandupDialog(board_id, "Tablero Standup", db_path=db_path)
    assert dlg.editor.toPlainText() != ""
    assert "Daily Standup — Tablero Standup" in dlg.editor.toPlainText()

    # Copiado al portapapeles
    dlg._copy_to_clipboard()
    # Cancelación segura de hilo
    dlg._cancel_thread()
    dlg.close()


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


def test_search_dialog_with_semantic_toggle(qapp, db_path):
    from search_dialog import SearchDialog
    board_id = database.create_board("Board Search Dialog", db_path=db_path)
    col_id = database.create_column(board_id, "Col", db_path=db_path)
    database.create_task(col_id, "Gestión de memoria y caché", db_path=db_path)

    dlg = SearchDialog(db_path=db_path)
    assert hasattr(dlg, "semantic_chk")

    dlg.text_input.setText("memoria")
    dlg.semantic_chk.setChecked(True)
    dlg.refresh_results()
    assert dlg.results_layout.count() >= 1

    dlg.close()


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
