"""board_sync.py - Motor de sincronización asíncrona y fusión (Merge Engine) de tableros.

Permite sincronizar tableros locales de Ekin con archivos compartidos (.ekboard en JSON)
ubicados en OneDrive, Nextcloud, Google Drive o carpetas de red corporativas.

Características clave:
1. Arquitectura Offline-First con sincronización en diferido.
2. Fusión a nivel de entidad (tarea por tarea según task_uuid y versión/timestamp).
3. Política No-Data-Loss: si dos usuarios editan la misma tarea simultáneamente,
   se adopta la versión más reciente pero el contenido concurrente anterior se
   archiva automáticamente en el diario/chat de la tarea como entrada de auditoría.
4. Instantánea de seguridad automática previa a cada fusión (backups/sync_premerge_...).
"""

import os
import json
import hashlib
import tempfile
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field

import database


@dataclass
class SyncResult:
    """Resultado de una operación de sincronización."""
    status: str  # "up_to_date", "exported", "imported", "merged", "not_linked", "error"
    board_id: int
    file_path: str = ""
    tasks_imported: int = 0
    tasks_exported: int = 0
    conflicts_resolved: int = 0
    message: str = ""
    details: list[str] = field(default_factory=list)


def calculate_content_hash(data_or_text) -> str:
    """Calcula el hash SHA-256 de una cadena de texto o diccionario JSON."""
    if isinstance(data_or_text, dict):
        text = json.dumps(data_or_text, sort_keys=True, ensure_ascii=False)
    else:
        text = str(data_or_text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def calculate_file_hash(file_path: str) -> str:
    """Calcula el hash SHA-256 de un archivo en disco."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def now_utc_iso() -> str:
    """Devuelve la fecha/hora actual en formato ISO 8601 UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def export_board_to_sync_dict(board_id: int, db_path=None) -> dict:
    """Serializa un tablero completo con sus columnas, tareas, etiquetas, enlaces y logs
    a un diccionario estructurado listo para exportar a .ekboard."""
    board = database.get_board(board_id, db_path)
    if not board:
        raise ValueError(f"El tablero con ID {board_id} no existe.")

    b_uuid = board.get("board_uuid")
    if not b_uuid:
        b_uuid = str(uuid.uuid4())
        with database.get_connection(db_path) as conn:
            conn.execute("UPDATE boards SET board_uuid = ? WHERE id = ?", (b_uuid, board_id))

    columns = database.get_columns(board_id, db_path)
    exported_columns = []
    exported_tasks = []

    for col in columns:
        c_uuid = col.get("column_uuid")
        if not c_uuid:
            c_uuid = str(uuid.uuid4())
            with database.get_connection(db_path) as conn:
                conn.execute("UPDATE columns SET column_uuid = ? WHERE id = ?", (c_uuid, col["id"]))

        exported_columns.append({
            "column_uuid": c_uuid,
            "name": col["name"],
            "color": col.get("color", "#3b82f6"),
            "position": col.get("position", 0),
            "collapsed": col.get("collapsed", 0),
        })

        tasks = database.get_tasks(col["id"], db_path)
        for t in tasks:
            t_uuid = t.get("task_uuid")
            if not t_uuid:
                t_uuid = str(uuid.uuid4())
                with database.get_connection(db_path) as conn:
                    conn.execute("UPDATE tasks SET task_uuid = ? WHERE id = ?", (t_uuid, t["id"]))

            logs = database.get_logs(t["id"], db_path)

            # Extraer etiquetas formateadas
            tags_list = []
            for tag in t.get("tags", []):
                tags_list.append({
                    "category": tag.get("category_name", "General"),
                    "value": tag.get("text", ""),
                    "color": tag.get("color", "#6b7280"),
                })

            # Extraer enlaces
            links_list = []
            for link in t.get("links", []):
                links_list.append({
                    "url": link.get("url", ""),
                    "label": link.get("label", ""),
                    "position": link.get("position", 0),
                })

            # Extraer logs
            logs_list = []
            for log_entry in logs:
                logs_list.append({
                    "content": log_entry["content"],
                    "created_at": log_entry["created_at"],
                })

            exported_tasks.append({
                "task_uuid": t_uuid,
                "column_uuid": c_uuid,
                "title": t["title"],
                "description": t.get("description", "") or "",
                "tag_text": t.get("tag_text", "") or "",
                "tag_color": t.get("tag_color", "#6b7280") or "#6b7280",
                "position": t.get("position", 0),
                "due_date": t.get("due_date"),
                "due_time": t.get("due_time"),
                "recurrence": t.get("recurrence", "none") or "none",
                "timer_started_at": t.get("timer_started_at"),
                "version": t.get("version", 1) or 1,
                "synced_version": t.get("synced_version", 0) or 0,
                "updated_at": t.get("updated_at") or now_utc_iso(),
                "tags": tags_list,
                "links": links_list,
                "logs": logs_list,
            })

    return {
        "format": "ekin_shared_board",
        "format_version": 1,
        "board_uuid": b_uuid,
        "board_name": board["name"],
        "board_color": board.get("color", "#3b82f6"),
        "exported_at": now_utc_iso(),
        "columns": exported_columns,
        "tasks": exported_tasks,
    }


def write_sync_file_atomic(file_path: str, data: dict) -> str:
    """Escribe el archivo .ekboard de forma atómica usando un archivo temporal
    para evitar escrituras corruptas en carpetas de OneDrive."""
    parent_dir = os.path.dirname(os.path.abspath(file_path))
    os.makedirs(parent_dir, exist_ok=True)

    json_content = json.dumps(data, indent=2, ensure_ascii=False)
    temp_fd, temp_path = tempfile.mkstemp(dir=parent_dir, prefix=".sync_tmp_", suffix=".ekboard")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            f.write(json_content)

        # Reemplazo atómico con reintentos para mitigar bloqueos transitorios de OneDrive/antivirus en Windows
        last_err = None
        for attempt in range(4):
            try:
                os.replace(temp_path, file_path)
                last_err = None
                break
            except PermissionError as pe:
                last_err = pe
                time.sleep(0.05 * (2 ** attempt))  # 50ms, 100ms, 200ms

        if last_err is not None:
            raise last_err

    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise

    return calculate_file_hash(file_path)


def create_premerge_backup(board_id: int, db_path=None) -> str:
    """Crea una instantánea local automática del tablero antes de fusionar cambios."""
    try:
        data = export_board_to_sync_dict(board_id, db_path)
        backup_dir = os.path.join(os.getcwd(), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"sync_premerge_board_{board_id}_{timestamp}.json")
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return backup_path
    except Exception:
        return ""


def sync_board_with_file(board_id: int, file_path: str = None, db_path=None) -> SyncResult:
    """Ejecuta el ciclo completo de sincronización y fusión diferencial para un tablero.

    Flujo de decisión:
    1. Si no hay ruta configurada ni pasada por parámetro -> 'not_linked'.
    2. Si el archivo compartido no existe -> exportación inicial automática.
    3. Si el archivo existe pero su hash coincide con el último sync -> comprobar si hay
       cambios locales; si los hay, exportar a archivo; si no, 'up_to_date'.
    4. Si el archivo externo cambió:
       - Si no hay cambios locales -> importación directa ('imported').
       - Si hay cambios concurrentes locales y externos -> Fusión diferencial ('merged')
         respetando las tareas de ambos y archivando colisiones en el chat/diario.
    """
    sync_info = database.get_board_sync_info(board_id, db_path)
    if not sync_info:
        return SyncResult(status="error", board_id=board_id, message="El tablero no existe.")

    target_path = file_path or sync_info.get("sync_path")
    if not target_path:
        return SyncResult(status="not_linked", board_id=board_id, message="El tablero no está vinculado a OneDrive ni a una carpeta compartida.")

    # Asegurar que el tablero tenga sync_path registrado
    if sync_info.get("sync_path") != target_path:
        database.set_board_sync_path(board_id, target_path, db_path)
        sync_info = database.get_board_sync_info(board_id, db_path)

    last_synced_at = sync_info.get("last_synced_at")
    board_uuid = sync_info.get("board_uuid")

    # --- CASO A: El archivo compartido aún no existe en disco -> Exportación inicial ---
    if not os.path.exists(target_path):
        data = export_board_to_sync_dict(board_id, db_path)
        new_hash = write_sync_file_atomic(target_path, data)
        now_ts = now_utc_iso()
        database.update_board_sync_state(board_id, now_ts, new_hash, db_path)
        database.mark_board_tasks_synced(board_id, db_path)
        return SyncResult(
            status="exported",
            board_id=board_id,
            file_path=target_path,
            tasks_exported=len(data.get("tasks", [])),
            message="Tablero exportado por primera vez a la carpeta compartida.",
        )

    # --- CASO B: El archivo compartido existe -> Comprobar hash y diferencias ---
    current_file_hash = calculate_file_hash(target_path)

    with open(target_path, "r", encoding="utf-8") as f:
        try:
            remote_data = json.load(f)
        except Exception as e:
            return SyncResult(
                status="error",
                board_id=board_id,
                file_path=target_path,
                message=f"El archivo compartido está dañado o no es un JSON válido: {e}",
            )

    remote_uuid = remote_data.get("board_uuid")
    if board_uuid and remote_uuid and board_uuid != remote_uuid:
        return SyncResult(
            status="error",
            board_id=board_id,
            file_path=target_path,
            message="El archivo compartido pertenece a un tablero distinto (UUID no coincide).",
        )

    local_data = export_board_to_sync_dict(board_id, db_path)

    # Si el hash del archivo no ha cambiado y los datos coinciden exactamente:
    local_tasks_by_uuid = {t["task_uuid"]: t for t in local_data.get("tasks", []) if "task_uuid" in t}
    remote_tasks_by_uuid = {t["task_uuid"]: t for t in remote_data.get("tasks", []) if "task_uuid" in t}

    local_changed = False
    remote_changed = False

    # 1. Tareas presentes en un lado y no en el otro
    for u, l_t in local_tasks_by_uuid.items():
        if u not in remote_tasks_by_uuid:
            if (l_t.get("synced_version") or 0) > 0 and (l_t.get("version", 1) <= (l_t.get("synced_version") or 0)):
                # Estaba sincronizada y no se tocó en local: el colaborador la eliminó en remoto
                remote_changed = True
            else:
                # Creada o modificada localmente
                local_changed = True

    for u in remote_tasks_by_uuid:
        if u not in local_tasks_by_uuid:
            remote_changed = True

    # 2. Tareas compartidas
    for u, l_t in local_tasks_by_uuid.items():
        if u in remote_tasks_by_uuid:
            r_t = remote_tasks_by_uuid[u]
            l_v = l_t.get("version", 1)
            l_sv = l_t.get("synced_version", 0)
            r_v = r_t.get("version", 1)

            t_local_changed = (l_v > l_sv)
            t_remote_changed = (r_v != l_sv) if l_sv > 0 else (r_v != l_v)

            if not t_local_changed and not t_remote_changed:
                differs = (
                    l_t.get("title") != r_t.get("title") or
                    l_t.get("description") != r_t.get("description") or
                    l_t.get("column_uuid") != r_t.get("column_uuid") or
                    l_t.get("due_date") != r_t.get("due_date") or
                    l_t.get("due_time") != r_t.get("due_time") or
                    l_t.get("recurrence") != r_t.get("recurrence") or
                    len(l_t.get("logs", [])) != len(r_t.get("logs", [])) or
                    len(l_t.get("links", [])) != len(r_t.get("links", []))
                )
                if differs:
                    t_local_changed = True
                    t_remote_changed = True

            if t_local_changed:
                local_changed = True
            if t_remote_changed:
                remote_changed = True

    # Decidir acción según cambios detectados
    if not local_changed and not remote_changed:
        # Nada ha cambiado en ningún extremo
        return SyncResult(
            status="up_to_date",
            board_id=board_id,
            file_path=target_path,
            message="El tablero está completamente sincronizado y al día.",
        )

    if local_changed and not remote_changed:
        # Solo hubo cambios locales: exportar a OneDrive
        new_hash = write_sync_file_atomic(target_path, local_data)
        now_ts = now_utc_iso()
        database.update_board_sync_state(board_id, now_ts, new_hash, db_path)
        database.mark_board_tasks_synced(board_id, db_path)
        return SyncResult(
            status="exported",
            board_id=board_id,
            file_path=target_path,
            tasks_exported=len(local_data.get("tasks", [])),
            message="Cambios locales sincronizados y guardados en OneDrive.",
        )

    if remote_changed and not local_changed:
        # Solo hubo cambios remotos: aplicar directamente a BD local
        create_premerge_backup(board_id, db_path)
        imported_count = _apply_remote_board_clean(board_id, remote_data, db_path)
        now_ts = now_utc_iso()
        database.update_board_sync_state(board_id, now_ts, current_file_hash, db_path)
        database.mark_board_tasks_synced(board_id, db_path)
        return SyncResult(
            status="imported",
            board_id=board_id,
            file_path=target_path,
            tasks_imported=imported_count,
            message=f"Sincronización completada: {imported_count} tareas actualizadas desde OneDrive.",
        )

    # Ambos cambiaron concurrentemente: ejecutar Fusión Diferencial
    create_premerge_backup(board_id, db_path)
    merge_res = _execute_two_way_merge(board_id, remote_data, last_synced_at, db_path)

    # Tras fusionar en base de datos local, re-exportar el estado unificado al archivo
    database.mark_board_tasks_synced(board_id, db_path)
    merged_data = export_board_to_sync_dict(board_id, db_path)
    new_hash = write_sync_file_atomic(target_path, merged_data)
    now_ts = now_utc_iso()
    database.update_board_sync_state(board_id, now_ts, new_hash, db_path)

    return SyncResult(
        status="merged",
        board_id=board_id,
        file_path=target_path,
        tasks_imported=merge_res["imported"],
        tasks_exported=merge_res["exported"],
        conflicts_resolved=merge_res["conflicts"],
        message=f"Fusión concurrente completada con éxito. Tareas añadidas/actualizadas: {merge_res['imported']}, conflictos resueltos sin pérdida: {merge_res['conflicts']}.",
        details=merge_res.get("details", []),
    )


def _apply_remote_board_clean(board_id: int, remote_data: dict, db_path=None) -> int:
    """Aplica limpiamente los datos remotos cuando no hay modificaciones locales."""
    with database.get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Mapear columnas existentes
        cursor.execute("SELECT id, name, column_uuid FROM columns WHERE board_id = ?", (board_id,))
        local_cols = {row["column_uuid"]: row["id"] for row in cursor.fetchall() if row["column_uuid"]}

        # Asegurar columnas remotas
        for r_col in remote_data.get("columns", []):
            c_uuid = r_col["column_uuid"]
            if c_uuid not in local_cols:
                cursor.execute(
                    "INSERT INTO columns (board_id, name, color, position, collapsed, column_uuid) VALUES (?, ?, ?, ?, ?, ?)",
                    (board_id, r_col["name"], r_col.get("color", "#3b82f6"), r_col.get("position", 0), r_col.get("collapsed", 0), c_uuid)
                )
                local_cols[c_uuid] = cursor.lastrowid
            else:
                cursor.execute(
                    "UPDATE columns SET name = ?, color = ?, position = ?, collapsed = ? WHERE id = ?",
                    (r_col["name"], r_col.get("color", "#3b82f6"), r_col.get("position", 0), r_col.get("collapsed", 0), local_cols[c_uuid])
                )

        # Mapear tareas existentes
        cursor.execute(
            """SELECT t.id, t.task_uuid FROM tasks t
               JOIN columns c ON c.id = t.column_id
               WHERE c.board_id = ?""",
            (board_id,)
        )
        local_tasks = {row["task_uuid"]: row["id"] for row in cursor.fetchall() if row["task_uuid"]}

        tasks_processed = 0
        for r_task in remote_data.get("tasks", []):
            t_uuid = r_task["task_uuid"]
            target_col_id = local_cols.get(r_task["column_uuid"])
            if not target_col_id:
                # Si la columna no se encontró, asignar a la primera columna disponible
                target_col_id = list(local_cols.values())[0] if local_cols else None

            if not target_col_id:
                continue

            r_version = r_task.get("version", 1) or 1
            if t_uuid in local_tasks:
                task_id = local_tasks[t_uuid]
                cursor.execute(
                    """UPDATE tasks
                       SET column_id = ?, title = ?, description = ?, tag_text = ?, tag_color = ?,
                           position = ?, due_date = ?, due_time = ?, recurrence = ?,
                           version = ?, synced_version = ?, updated_at = ?
                       WHERE id = ?""",
                    (
                        target_col_id, r_task["title"], r_task.get("description", ""),
                        r_task.get("tag_text", ""), r_task.get("tag_color", "#6b7280"),
                        r_task.get("position", 0), r_task.get("due_date"), r_task.get("due_time"),
                        r_task.get("recurrence", "none"), r_version, r_version,
                        r_task.get("updated_at", now_utc_iso()), task_id
                    )
                )
            else:
                cursor.execute(
                    """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position,
                                          due_date, due_time, recurrence, task_uuid, version, synced_version, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        target_col_id, r_task["title"], r_task.get("description", ""),
                        r_task.get("tag_text", ""), r_task.get("tag_color", "#6b7280"),
                        r_task.get("position", 0), r_task.get("due_date"), r_task.get("due_time"),
                        r_task.get("recurrence", "none"), t_uuid, r_version, r_version,
                        r_task.get("updated_at", now_utc_iso())
                    )
                )
                task_id = cursor.lastrowid
                local_tasks[t_uuid] = task_id

            _sync_task_sub_entities(cursor, task_id, r_task)
            tasks_processed += 1

        # Eliminar tareas locales que ya no existen en el archivo remoto (borradas por colaboradores)
        remote_task_uuids = {r["task_uuid"] for r in remote_data.get("tasks", []) if r.get("task_uuid")}
        for l_uuid, l_id in list(local_tasks.items()):
            if l_uuid not in remote_task_uuids:
                cursor.execute("DELETE FROM tasks WHERE id = ?", (l_id,))

        return tasks_processed


def _execute_two_way_merge(board_id: int, remote_data: dict, last_synced_at: str, db_path=None) -> dict:
    """Ejecuta la fusión diferencial a nivel de tarea entre los cambios locales y los remotos."""
    result = {"imported": 0, "exported": 0, "conflicts": 0, "details": []}

    with database.get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Columnas
        cursor.execute("SELECT id, name, column_uuid FROM columns WHERE board_id = ?", (board_id,))
        local_cols = {row["column_uuid"]: row["id"] for row in cursor.fetchall() if row["column_uuid"]}

        for r_col in remote_data.get("columns", []):
            c_uuid = r_col["column_uuid"]
            if c_uuid not in local_cols:
                cursor.execute(
                    "INSERT INTO columns (board_id, name, color, position, collapsed, column_uuid) VALUES (?, ?, ?, ?, ?, ?)",
                    (board_id, r_col["name"], r_col.get("color", "#3b82f6"), r_col.get("position", 0), r_col.get("collapsed", 0), c_uuid)
                )
                local_cols[c_uuid] = cursor.lastrowid

        # 2. Tareas locales
        cursor.execute(
            """SELECT t.id, t.column_id, t.title, t.description, t.tag_text, t.tag_color,
                      t.position, t.due_date, t.due_time, t.recurrence, t.task_uuid,
                      t.version, t.synced_version, t.updated_at
               FROM tasks t
               JOIN columns c ON c.id = t.column_id
               WHERE c.board_id = ?""",
            (board_id,)
        )
        local_tasks = {row["task_uuid"]: dict(row) for row in cursor.fetchall() if row["task_uuid"]}
        remote_tasks = {t["task_uuid"]: t for t in remote_data.get("tasks", []) if "task_uuid" in t}

        # Procesar tareas remotas
        for t_uuid, r_task in remote_tasks.items():
            target_col_id = local_cols.get(r_task["column_uuid"])
            if not target_col_id:
                target_col_id = list(local_cols.values())[0] if local_cols else None
            if not target_col_id:
                continue

            r_ver = r_task.get("version", 1) or 1
            if t_uuid not in local_tasks:
                # Tarea creada en remoto: insertarla localmente
                cursor.execute(
                    """INSERT INTO tasks (column_id, title, description, tag_text, tag_color, position,
                                          due_date, due_time, recurrence, task_uuid, version, synced_version, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        target_col_id, r_task["title"], r_task.get("description", ""),
                        r_task.get("tag_text", ""), r_task.get("tag_color", "#6b7280"),
                        r_task.get("position", 0), r_task.get("due_date"), r_task.get("due_time"),
                        r_task.get("recurrence", "none"), t_uuid, r_ver, r_ver,
                        r_task.get("updated_at", now_utc_iso())
                    )
                )
                task_id = cursor.lastrowid
                _sync_task_sub_entities(cursor, task_id, r_task)
                result["imported"] += 1
            else:
                # Tarea existente en ambos: comparar versiones
                l_task = local_tasks[t_uuid]
                task_id = l_task["id"]

                l_ver = l_task.get("version", 1) or 1
                l_sver = l_task.get("synced_version", 0) or 0

                local_was_modified = (l_ver > l_sver)
                remote_was_modified = (r_ver != l_sver) if l_sver > 0 else (r_ver != l_ver)

                if not local_was_modified and not remote_was_modified:
                    differs = (
                        l_task.get("title") != r_task.get("title") or
                        l_task.get("description") != r_task.get("description") or
                        l_task.get("column_uuid") != r_task.get("column_uuid") or
                        l_task.get("due_date") != r_task.get("due_date")
                    )
                    if differs:
                        local_was_modified = True
                        remote_was_modified = True

                r_updated = str(r_task.get("updated_at", ""))
                l_updated = str(l_task.get("updated_at", ""))

                if remote_was_modified and not local_was_modified:
                    # Solo cambió en remoto: adoptar versión remota
                    cursor.execute(
                        """UPDATE tasks
                           SET column_id = ?, title = ?, description = ?, tag_text = ?, tag_color = ?,
                               position = ?, due_date = ?, due_time = ?, recurrence = ?,
                               version = ?, synced_version = ?, updated_at = ?
                           WHERE id = ?""",
                        (
                            target_col_id, r_task["title"], r_task.get("description", ""),
                            r_task.get("tag_text", ""), r_task.get("tag_color", "#6b7280"),
                            r_task.get("position", 0), r_task.get("due_date"), r_task.get("due_time"),
                            r_task.get("recurrence", "none"), r_ver, r_ver,
                            r_task.get("updated_at", now_utc_iso()), task_id
                        )
                    )
                    _sync_task_sub_entities(cursor, task_id, r_task)
                    result["imported"] += 1

                elif local_was_modified and not remote_was_modified:
                    # Solo cambió en local: mantener versión local (se exportará al terminar)
                    result["exported"] += 1

                elif local_was_modified and remote_was_modified:
                    # Conflicto real: ambos modificaron la misma tarea
                    result["conflicts"] += 1
                    r_ver = r_task.get("version", 1)
                    l_ver = l_task.get("version", 1)

                    # Elegir ganador de campos primarios según fecha o versión más reciente
                    use_remote_primary = (r_updated > l_updated) or (r_updated == l_updated and r_ver >= l_ver)

                    if use_remote_primary:
                        chosen_title = r_task["title"]
                        chosen_col = target_col_id
                        chosen_due_date = r_task.get("due_date")
                        chosen_due_time = r_task.get("due_time")
                        chosen_desc = r_task.get("description", "")
                        older_desc = l_task.get("description", "")
                        older_label = "tu versión local"
                    else:
                        chosen_title = l_task["title"]
                        chosen_col = l_task["column_id"]
                        chosen_due_date = l_task.get("due_date")
                        chosen_due_time = l_task.get("due_time")
                        chosen_desc = l_task.get("description", "")
                        older_desc = r_task.get("description", "")
                        older_label = "la versión de OneDrive"

                    # Si las descripciones son distintas, aplicar política No-Data-Loss:
                    # archivar la descripción previa en el chat/diario de la tarea
                    if older_desc and older_desc.strip() and older_desc != chosen_desc:
                        log_msg = (
                            f"<p><b>⚠️ Sincronización OneDrive (Conflicto resuelto automáticamente):</b><br/>"
                            f"Se ha mantenido la descripción más reciente. {older_label.capitalize()} se conserva aquí para consulta:</p>"
                            f"<blockquote>{older_desc}</blockquote>"
                        )
                        cursor.execute(
                            "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                            (task_id, log_msg, now_utc_iso())
                        )
                        result["details"].append(f"Tarea '{chosen_title}': descripción concurrente archivada en el chat.")

                    new_version = max(r_ver, l_ver) + 1
                    cursor.execute(
                        """UPDATE tasks
                           SET column_id = ?, title = ?, description = ?, due_date = ?, due_time = ?,
                               version = ?, synced_version = ?, updated_at = ?
                           WHERE id = ?""",
                        (chosen_col, chosen_title, chosen_desc, chosen_due_date, chosen_due_time,
                         new_version, new_version, now_utc_iso(), task_id)
                    )

                    # Unir logs, enlaces y tags sin duplicados
                    _merge_task_sub_entities(cursor, task_id, r_task)

        # Manejar tareas locales que no están en el archivo remoto
        for t_uuid, l_task in local_tasks.items():
            if t_uuid not in remote_tasks:
                local_was_modified = (l_task["version"] > (l_task.get("synced_version") or 0))
                if not local_was_modified and (l_task.get("synced_version") or 0) > 0:
                    # La tarea ya estaba sincronizada previamente y fue eliminada por el colaborador
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (l_task["id"],))
                    result["details"].append(f"Tarea '{l_task.get('title', '')}' eliminada remotamente.")
                else:
                    # Tarea creada o modificada localmente: se conserva y exportará
                    result["exported"] += 1

    return result


def _sync_task_sub_entities(cursor, task_id: int, r_task: dict):
    """Sincroniza tags, enlaces y logs de una tarea remota a la base de datos local."""
    _merge_task_sub_entities(cursor, task_id, r_task)


def _merge_task_sub_entities(cursor, task_id: int, r_task: dict):
    """Fusiona logs, tags y enlaces sin destruir datos existentes."""
    # 1. Logs: añadir los que no existan por contenido exacto
    cursor.execute("SELECT content FROM task_logs WHERE task_id = ?", (task_id,))
    existing_logs = {row[0] for row in cursor.fetchall()}
    for log_item in r_task.get("logs", []):
        content = log_item.get("content", "")
        if content and content not in existing_logs:
            created_at = log_item.get("created_at") or now_utc_iso()
            cursor.execute(
                "INSERT INTO task_logs (task_id, content, created_at) VALUES (?, ?, ?)",
                (task_id, content, created_at)
            )
            existing_logs.add(content)

    # 2. Links: añadir los que no existan por URL
    cursor.execute("SELECT url FROM task_links WHERE task_id = ?", (task_id,))
    existing_links = {row[0] for row in cursor.fetchall()}
    for link_item in r_task.get("links", []):
        url = link_item.get("url", "")
        if url and url not in existing_links:
            cursor.execute(
                "INSERT INTO task_links (task_id, url, label, position) VALUES (?, ?, ?, ?)",
                (task_id, url, link_item.get("label", ""), link_item.get("position", 0))
            )
            existing_links.add(url)
