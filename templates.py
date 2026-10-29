"""
Motor de Plantillas de Tableros (Board Templates Engine) para Ekin Kanban.

Permite instanciar tableros preconfigurados (Software Agile, Opositor, GTD/Personal, Blanco)
así como guardar, importar, exportar y gestionar plantillas personalizadas de usuario.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import database
from strings import t


@dataclass
class ColumnTemplate:
    name: str
    color: str = "#3b82f6"
    wip_limit: Optional[int] = None


@dataclass
class TagTemplate:
    category: str
    value: str
    color: str = "#6b7280"


@dataclass
class SeedTaskTemplate:
    title: str
    column_index: int
    description: str = ""
    priority: Optional[str] = None
    tags: List[str] = field(default_factory=list)  # Lista de tag values
    due_days_offset: Optional[int] = None
    initial_log: Optional[str] = None


@dataclass
class BoardTemplate:
    id: str
    name: str
    description: str
    category: str
    color: str
    icon: str
    columns: List[ColumnTemplate] = field(default_factory=list)
    default_tags: List[TagTemplate] = field(default_factory=list)
    seed_tasks: List[SeedTaskTemplate] = field(default_factory=list)
    ai_system_prompt: str = ""
    is_builtin: bool = True
    prompt_pack: str = ""  # pack del AI Prompt Clipboard ("" = el de por defecto)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BoardTemplate:
        columns = [
            ColumnTemplate(**c) if isinstance(c, dict) else c
            for c in data.get("columns", [])
        ]
        default_tags = [
            TagTemplate(**t) if isinstance(t, dict) else t
            for t in data.get("default_tags", [])
        ]
        seed_tasks = [
            SeedTaskTemplate(**st) if isinstance(st, dict) else st
            for st in data.get("seed_tasks", [])
        ]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "General"),
            color=data.get("color", "#3b82f6"),
            icon=data.get("icon", "table"),
            columns=columns,
            default_tags=default_tags,
            seed_tasks=seed_tasks,
            ai_system_prompt=data.get("ai_system_prompt", ""),
            is_builtin=data.get("is_builtin", False),
            prompt_pack=data.get("prompt_pack", ""),
        )


# Las plantillas de fábrica guardan en sus textos claves de strings.py, que se traducen al idioma
# de la interfaz al mostrarlas y al crear el tablero (#144). El tutorial solo traduce su ficha.
_TEXT_KEY = "template_builtin."


def _tr(text):
    return t(text) if isinstance(text, str) and text.startswith(_TEXT_KEY) else text


def localized(template: BoardTemplate) -> BoardTemplate:
    """Copia de la plantilla con sus textos en el idioma de la interfaz."""
    tmpl = BoardTemplate.from_dict(template.to_dict())
    tmpl.name, tmpl.description, tmpl.category = _tr(tmpl.name), _tr(tmpl.description), _tr(tmpl.category)
    tmpl.ai_system_prompt = _tr(tmpl.ai_system_prompt)
    for col in tmpl.columns:
        col.name = _tr(col.name)
    for tag in tmpl.default_tags:
        tag.category, tag.value = _tr(tag.category), _tr(tag.value)
    for st in tmpl.seed_tasks:
        st.title, st.description = _tr(st.title), _tr(st.description)
        st.tags = [_tr(value) for value in st.tags]
    return tmpl


# --- PLANTILLAS DE FÁBRICA (BUILT-IN) ---

TEMPLATE_GETTING_STARTED = BoardTemplate(
    id="getting_started",
    name="template_builtin.getting_started.name",
    description="template_builtin.getting_started.description",
    category="template_builtin.getting_started.category",
    color="#2563eb",
    icon="sparkles",
    columns=[
        ColumnTemplate("👋 ¡Empieza aquí!", "#3b82f6", None),
        ColumnTemplate("⚡ En Progreso & Edición", "#0ea5e9", 3),
        ColumnTemplate("🛠️ Productividad & Atajos", "#f59e0b", None),
        ColumnTemplate("🎉 ¡Completado!", "#10b981", None),
    ],
    default_tags=[
        TagTemplate("Tipo", "Tutorial", "#3b82f6"),
        TagTemplate("Tipo", "Diario", "#8b5cf6"),
        TagTemplate("Tipo", "Interacción", "#0ea5e9"),
        TagTemplate("Tipo", "Columnas", "#10b981"),
        TagTemplate("Tipo", "Productividad", "#f59e0b"),
        TagTemplate("Tipo", "IA", "#6366f1"),
        TagTemplate("Tipo", "Listo", "#059669"),
        TagTemplate("Priority", "Alta", "#ef4444"),
        TagTemplate("Priority", "Media", "#f59e0b"),
        TagTemplate("Priority", "Baja", "#6b7280"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title="1. Haz clic aquí para ver el Diario y Editor",
            column_index=0,
            description=(
                "¡Te damos la bienvenida a **Ekin Kanban**! 🎉\n\n"
                "Esta tarjeta es un ejemplo vivo de las capacidades del editor enriquecido:\n"
                "- [x] **Markdown completo**: negritas, cursivas, listas interactivas y citas.\n"
                "- [x] **Bloques de código**: con sintaxis coloreada (`</>`) y botón de copiado rápido.\n"
                "- [x] **Diario personal integrado**: mira la pestaña inferior con registros cronológicos y horas trabajadas.\n"
                "- [x] **Temporizador Pomodoro**: pulsa el cronómetro arriba a la derecha para contabilizar tu sesión.\n\n"
                "```python\n"
                "# Script de ejemplo en Ekin\n"
                "def welcome_to_ekin():\n"
                "    print('¡Productividad fluida y control total!')\n"
                "```\n\n"
                "> 💡 **Siguiente paso del tour**: Cierra este diálogo y arrastra la siguiente tarjeta hacia la derecha."
            ),
            priority="Alta",
            tags=["Tutorial", "Diario"],
            initial_log="He abierto Ekin Kanban por primera vez. ¡Todo listo para empezar a trabajar con el diario personal!",
        ),
        SeedTaskTemplate(
            title="2. Arrástrame a la columna '⚡ En Progreso'",
            column_index=0,
            description=(
                "### 🎯 Misión Drag & Drop\n"
                "1. Haz clic sobre esta tarjeta y mantenla pulsada con el ratón.\n"
                "2. Arrástrala hacia la columna **'⚡ En Progreso & Edición'**.\n"
                "3. Observa la miniatura en alta resolución y la **ranura de inserción interactiva** que separa las tarjetas en tiempo real para indicar exactamente dónde quedará colocada.\n"
                "4. Suelta el ratón para completar el movimiento."
            ),
            priority="Media",
            tags=["Interacción"],
        ),
        SeedTaskTemplate(
            title="3. Prueba a editar o personalizar esta columna",
            column_index=1,
            description=(
                "### 🛠️ Personalización de Columnas\n"
                "Cada columna de Ekin se adapta totalmente a tu flujo de trabajo:\n"
                "1. Haz **doble clic en el encabezado** de esta columna (o clic en el menú `⋮`).\n"
                "2. Puedes cambiar su **nombre**, asignar un **color temático** o fijar un **Límite WIP (Work In Progress)**.\n"
                "3. Esta columna tiene configurado un límite de **3 tareas** para evitar cuellos de botella y mantener el foco."
            ),
            priority="Media",
            tags=["Columnas"],
        ),
        SeedTaskTemplate(
            title="4. Crea una nueva tarea con '+' o Ctrl+N",
            column_index=1,
            description=(
                "### ✍️ Creación Rápida\n"
                "- Haz clic en el botón **`+`** al pie de cualquier columna.\n"
                "- O simplemente presiona el atajo de teclado global **`Ctrl+N`** para abrir la creación en tu columna activa.\n"
                "- Podrás asignar fechas de vencimiento, etiquetas personalizadas, prioridades independientes y adjuntar archivos locales."
            ),
            priority="Baja",
            tags=["Atajos"],
        ),
        SeedTaskTemplate(
            title="5. Pulsa Ctrl+K para la Paleta o Ctrl+0 / Ctrl+O para 'Mi Trabajo'",
            column_index=2,
            description=(
                "### ⚡ Navegación y Atajos de Teclado\n"
                "Ekin está diseñado para que no tengas que despegar las manos del teclado:\n"
                "- **`Ctrl+K`**: Paleta de comandos universal estilo Spotlight. Escribe cualquier comando, busca tareas al vuelo o escribe `+ Título` para captura rápida.\n"
                "- **`Ctrl+0` / `Ctrl+O`**: Vista transversal **Mi Trabajo**, que reúne tus tareas pendientes de todos los tableros organizadas por fechas (Hoy, Mañana, Esta Semana, Atrasadas).\n"
                "- **`Ctrl+Shift+C`**: Vista de calendario interactiva.\n"
                "- **`Ctrl+D`**: Panel de analíticas de productividad con métricas de flujo y exportación a PDF.\n"
                "- **`Ctrl+F`**: Búsqueda global en el tablero."
            ),
            priority="Media",
            tags=["Productividad"],
        ),
        SeedTaskTemplate(
            title="6. Sincroniza y comparte con Cloud (.ekboard)",
            column_index=2,
            description=(
                "### ☁️ Sincronización en la Nube y Carpetas Compartidas\n"
                "Ekin te permite colaborar y mantener tus tableros respaldados de forma offline-first:\n"
                "- **Vincular a la Nube**: Haz clic en el botón de la nube en el pie del tablero o en las opciones del tablero (`...` o clic derecho en la barra lateral).\n"
                "- **Archivo único `.ekboard`**: Se genera un archivo portátil que puedes guardar en **Google Drive, Dropbox, OneDrive** o una carpeta compartida en red local (LAN).\n"
                "- **Sincronización Reactiva**: Ekin detecta cambios automáticamente en segundo plano. Si otro usuario o tú editáis a la vez, el motor *No-Data-Loss* fusiona los cambios y archiva cualquier versión concurrente en el diario de la tarea.\n"
                "- **Atajo rápido**: Usa `Ctrl+K` y escribe *Sincronizar* para forzar una sincronización manual al instante."
            ),
            priority="Alta",
            tags=["Cloud", "Sync"],
        ),
        SeedTaskTemplate(
            title="7. Organiza entregas en el Calendario (Ctrl+Shift+C) y feed .ics",
            column_index=2,
            description=(
                "### 📅 Calendario Integrado y Sincronización Externa\n"
                "Gestiona todas tus fechas de vencimiento con visión global:\n"
                "- **Abrir Calendario**: Pulsa **`Ctrl+Shift+C`** o el icono de calendario en la barra lateral.\n"
                "- **Vistas flexibles**: Alterna entre vistas de **Mes, Semana o Día** y filtra por tablero o visualiza todos a la vez.\n"
                "- **Reprogramar con Drag & Drop**: Arrastra el chip de cualquier tarea a otro día del calendario para cambiar su fecha de entrega automáticamente.\n"
                "- **Feed iCalendar (.ics)**: En los Ajustes del Calendario puedes exportar un archivo `.ics` con actualización automática y suscribirte desde **Google Calendar, Outlook o Apple Calendar** para ver tus tareas en el móvil o reloj."
            ),
            priority="Media",
            tags=["Calendario"],
        ),
        SeedTaskTemplate(
            title="8. Trabaja con un agente de IA (▶ Trabajar) o abre Ajustes (⚙️)",
            column_index=2,
            description=(
                "### 🤖 Trabajar con un agente de IA\n"
                "- Enlaza el tablero con su carpeta local y pulsa **▶ Trabajar** en la cabecera: Ekin arranca el servidor MCP y abre tu CLI de IA (**Claude Code, Antigravity CLI o Gemini CLI**) en esa carpeta con el prompt de inicio.\n"
                "- El agente lee el tablero, toma la tarea activa, deja su avance como comentarios y la mueve de columna; las columnas solo las cambias tú.\n"
                "- **Prompts** (cabecera) tiene los prompts de tu tipo de tablero listos para copiar, y el botón **MCP** del pie conecta otros clientes (Cursor, Claude Desktop…). Cada tablero opera con un sandbox aislado y token secreto.\n"
                "- Para ver el flujo completo: **Ctrl+K → Ver el diagrama del flujo de trabajo con IA**.\n"
                "- Abre **Ajustes (⚙️)** en la barra lateral para alternar entre tema Claro y Oscuro, configurar avisos por anticipación o comprobar actualizaciones."
            ),
            priority="Alta",
            tags=["IA"],
        ),
        SeedTaskTemplate(
            title="9. ¡Enhorabuena! Listo para crear tus propios tableros",
            column_index=3,
            description=(
                "### 🚀 ¡Has dominado los aspectos fundamentales de Ekin!\n"
                "Ahora tienes todo el control:\n"
                "- Haz clic en el botón **`+`** de la barra lateral izquierda para crear un nuevo tablero.\n"
                "- Elige empezar con un lienzo en blanco o con uno de los tipos de tablero (**DEV** para software, **Socrático** para estudiar guiado por preguntas, **GTD** para tu productividad personal).\n"
                "- Puedes volver a consultar este tutorial o abrir la guía gráfica en cualquier momento desde **Ajustes (⚙️) > Tour y Bienvenida**."
            ),
            priority="Alta",
            tags=["Listo"],
        ),
    ],
    ai_system_prompt=(
        "Actúas como un mentor y guía interactivo para nuevos usuarios de Ekin Kanban. "
        "Ayuda al usuario a entender los conceptos de tarjetas, columnas con límites WIP, "
        "diario personal de desarrollo y atajos de teclado para maximizar su flujo de trabajo."
    ),
    is_builtin=True,
)

TEMPLATE_BLANK = BoardTemplate(
    id="blank",
    name="template_builtin.blank.name",
    description="template_builtin.blank.description",
    category="template_builtin.blank.category",
    color="#3b82f6",
    icon="table",
    columns=[],
    default_tags=[],
    seed_tasks=[],
    ai_system_prompt="template_builtin.blank.ai_prompt",
    is_builtin=True,
)

# Columnas cortas, con emoji y en mayúsculas (#149). Cada nombre conserva una palabra clave de
# column_roles.py en los dos idiomas, porque el rol de la columna se deduce de su nombre.
_SW = "template_builtin.software_agile."
TEMPLATE_SOFTWARE_AGILE = BoardTemplate(
    id="software_agile",
    name=_SW + "name",
    description=_SW + "description",
    category=_SW + "category",
    color="#2563eb",
    icon="code",
    columns=[
        ColumnTemplate(_SW + "col_backlog", "#64748b", None),
        ColumnTemplate(_SW + "col_ready", "#8b5cf6", 5),
        ColumnTemplate(_SW + "col_in_progress", "#0ea5e9", 3),
        ColumnTemplate(_SW + "col_review", "#f59e0b", 3),
        ColumnTemplate(_SW + "col_done", "#10b981", None),
    ],
    default_tags=[
        TagTemplate(_SW + "tag_type", "bug", "#ef4444"),
        TagTemplate(_SW + "tag_type", "feature", "#3b82f6"),
        TagTemplate(_SW + "tag_type", "refactor", "#8b5cf6"),
        TagTemplate(_SW + "tag_type", "tech-debt", "#f97316"),
        TagTemplate(_SW + "tag_type", "security", "#dc2626"),
        TagTemplate("Priority", "P0-Critical", "#ef4444"),
        TagTemplate("Priority", "P1-High", "#f59e0b"),
        TagTemplate("Priority", "P2-Medium", "#3b82f6"),
        TagTemplate("Priority", "P3-Low", "#6b7280"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title=_SW + "seed1_title",
            column_index=1,
            description=_SW + "seed1_description",
            priority="P1-High",
            tags=["feature", "tech-debt"],
            due_days_offset=3,
        ),
        SeedTaskTemplate(
            title=_SW + "seed2_title",
            column_index=0,
            description=_SW + "seed2_description",
            priority="P2-Medium",
            tags=["tech-debt"],
            due_days_offset=7,
        ),
    ],
    ai_system_prompt=_SW + "ai_prompt",
    is_builtin=True,
    prompt_pack="dev",
)

_OP = "template_builtin.opositor_study."
TEMPLATE_OPOSITOR = BoardTemplate(
    id="opositor_study",
    name=_OP + "name",
    description=_OP + "description",
    category=_OP + "category",
    color="#7c3aed",
    icon="list",
    columns=[
        ColumnTemplate(_OP + "col_todo", "#64748b", None),
        ColumnTemplate(_OP + "col_round1", "#0284c7", 4),
        ColumnTemplate(_OP + "col_round2", "#8b5cf6", 3),
        ColumnTemplate(_OP + "col_repetition", "#d97706", 5),
        ColumnTemplate(_OP + "col_test", "#dc2626", 4),
        ColumnTemplate(_OP + "col_mastered", "#059669", None),
    ],
    default_tags=[
        TagTemplate(_OP + "tag_content", _OP + "tag_theory", "#3b82f6"),
        TagTemplate(_OP + "tag_content", _OP + "tag_practice", "#8b5cf6"),
        TagTemplate(_OP + "tag_content", _OP + "tag_cases", "#0ea5e9"),
        TagTemplate(_OP + "tag_status", _OP + "tag_failed", "#ef4444"),
        TagTemplate(_OP + "tag_status", _OP + "tag_question", "#f59e0b"),
        TagTemplate(_OP + "tag_status", _OP + "tag_key", "#e11d48"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title=_OP + "seed1_title",
            column_index=1,
            description=_OP + "seed1_description",
            tags=[_OP + "tag_theory", _OP + "tag_key"],
            due_days_offset=2,
        ),
        SeedTaskTemplate(
            title=_OP + "seed2_title",
            column_index=0,
            description=_OP + "seed2_description",
            tags=[_OP + "tag_practice"],
            due_days_offset=5,
        ),
    ],
    ai_system_prompt=_OP + "ai_prompt",
    is_builtin=True,
    prompt_pack="opositor",
)

_GTD = "template_builtin.gtd_personal."
TEMPLATE_GTD_PERSONAL = BoardTemplate(
    id="gtd_personal",
    name=_GTD + "name",
    description=_GTD + "description",
    category=_GTD + "category",
    color="#059669",
    icon="check",
    columns=[
        ColumnTemplate(_GTD + "col_inbox", "#64748b", None),
        ColumnTemplate(_GTD + "col_next", "#0284c7", 7),
        ColumnTemplate(_GTD + "col_waiting", "#d97706", None),
        ColumnTemplate(_GTD + "col_someday", "#8b5cf6", None),
        ColumnTemplate(_GTD + "col_done", "#059669", None),
    ],
    default_tags=[
        TagTemplate(_GTD + "tag_context", _GTD + "tag_computer", "#3b82f6"),
        TagTemplate(_GTD + "tag_context", _GTD + "tag_calls", "#10b981"),
        TagTemplate(_GTD + "tag_context", _GTD + "tag_home", "#f59e0b"),
        TagTemplate(_GTD + "tag_context", _GTD + "tag_shopping", "#ec4899"),
        TagTemplate(_GTD + "tag_context", _GTD + "tag_errands", "#8b5cf6"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title=_GTD + "seed1_title",
            column_index=1,
            description=_GTD + "seed1_description",
            tags=[_GTD + "tag_computer"],
            due_days_offset=3,
        ),
    ],
    ai_system_prompt=_GTD + "ai_prompt",
    is_builtin=True,
    prompt_pack="gtd",
)

BUILTIN_TEMPLATES = [
    TEMPLATE_GETTING_STARTED,
    TEMPLATE_BLANK,
    TEMPLATE_SOFTWARE_AGILE,
    TEMPLATE_OPOSITOR,
    TEMPLATE_GTD_PERSONAL,
]


# --- GESTOR DE DIRECTORIO Y PERSISTENCIA ---

def get_templates_dir() -> str:
    """Devuelve la ruta al directorio donde se guardan las plantillas personalizadas de usuario."""
    custom_dir = os.environ.get("EKIN_TEMPLATES_DIR")
    if custom_dir:
        os.makedirs(custom_dir, exist_ok=True)
        return custom_dir

    base_dir = os.path.expanduser("~/.ekin/templates")
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def get_builtin_templates() -> List[BoardTemplate]:
    """Retorna una lista de copias de las plantillas predefinidas de fábrica, en el idioma de la interfaz."""
    return [localized(tmpl) for tmpl in BUILTIN_TEMPLATES]


def get_custom_templates(templates_dir: Optional[str] = None) -> List[BoardTemplate]:
    """Carga todas las plantillas de usuario personalizadas desde archivos JSON."""
    directory = templates_dir or get_templates_dir()
    templates = []
    if not os.path.exists(directory):
        return templates

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["is_builtin"] = False
                    templates.append(BoardTemplate.from_dict(data))
            except Exception:
                # Ignorar archivos corruptos para no bloquear la app
                continue
    return templates


def get_all_templates(templates_dir: Optional[str] = None) -> List[BoardTemplate]:
    """Retorna la lista unificada de plantillas de fábrica + personalizadas del usuario."""
    builtin = get_builtin_templates()
    custom = get_custom_templates(templates_dir)
    return builtin + custom


def get_template_by_id(template_id: str, templates_dir: Optional[str] = None) -> Optional[BoardTemplate]:
    """Busca una plantilla por su identificador único."""
    for tmpl in get_all_templates(templates_dir):
        if tmpl.id == template_id:
            return tmpl
    return None


def save_custom_template(template: BoardTemplate, templates_dir: Optional[str] = None) -> str:
    """Guarda una plantilla personalizada como archivo JSON en el directorio de plantillas."""
    directory = templates_dir or get_templates_dir()
    os.makedirs(directory, exist_ok=True)

    # Sanitizar el ID para el nombre de archivo
    safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in template.id).strip("_")
    if not safe_id:
        import uuid
        safe_id = f"template_{uuid.uuid4().hex[:8]}"

    template.id = safe_id
    template.is_builtin = False
    filepath = os.path.join(directory, f"{safe_id}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)

    return filepath


def delete_custom_template(template_id: str, templates_dir: Optional[str] = None) -> bool:
    """Elimina una plantilla personalizada de disco si existe, con validación anti path-traversal."""
    if not template_id:
        return False
    directory = os.path.abspath(templates_dir or get_templates_dir())
    # Sanitizar template_id eliminando cualquier carácter peligroso de ruta
    safe_id = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in template_id).strip("_")
    if not safe_id:
        return False
    filepath = os.path.abspath(os.path.join(directory, f"{safe_id}.json"))

    # Mitigación estricta de Path Traversal
    try:
        if os.path.commonpath([directory, filepath]) != directory:
            return False
    except ValueError:
        return False

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except OSError:
            return False
    return False


# --- CREACIÓN Y APLICACIÓN DE PLANTILLAS A LA BASE DE DATOS ---

def apply_template_to_board(board_id: int, template: BoardTemplate, db_path: Optional[str] = None) -> None:
    """Aplica las columnas, etiquetas y tareas semilla de una plantilla a un tablero recién creado."""
    template = localized(template)
    # 1. Crear columnas y mapear índices a nuevos column_ids
    col_id_by_index = {}
    for idx, col in enumerate(template.columns):
        col_id = database.create_column(
            board_id,
            col.name,
            col.color,
            db_path=db_path,
            wip_limit=col.wip_limit,
        )
        col_id_by_index[idx] = col_id

    # 2. Registrar categorías y valores de etiquetas predeterminadas
    tag_val_ids_by_name = {}
    for tag in template.default_tags:
        database.create_tag_category(tag.category, db_path=db_path)
        val_id = database.get_or_create_tag_value(tag.category, tag.value, tag.color, db_path=db_path)
        tag_val_ids_by_name[tag.value.lower()] = val_id

    # 3. Insertar tareas semilla si las hay
    for st in template.seed_tasks:
        col_id = col_id_by_index.get(st.column_index)
        if not col_id:
            continue

        due_date_str = None
        if st.due_days_offset is not None:
            target_date = date.today() + timedelta(days=st.due_days_offset)
            due_date_str = target_date.isoformat()

        task_id = database.create_task(
            column_id=col_id,
            title=st.title,
            description=st.description,
            due_date=due_date_str,
            db_path=db_path,
        )

        # Asociar tags
        assigned_tag_ids = []
        for tname in st.tags:
            t_id = tag_val_ids_by_name.get(tname.lower())
            if t_id and t_id not in assigned_tag_ids:
                assigned_tag_ids.append(t_id)

        # Si tiene prioridad indicada, enlazar el tag de Priority correspondiente
        if st.priority:
            prio_id = tag_val_ids_by_name.get(st.priority.lower())
            if prio_id and prio_id not in assigned_tag_ids:
                assigned_tag_ids.append(prio_id)

        if assigned_tag_ids:
            database.set_task_tags(task_id, assigned_tag_ids, db_path=db_path)

        # Si tiene nota de diario inicial, registrarla
        if st.initial_log:
            database.create_log(task_id, st.initial_log, db_path=db_path)


def create_board_from_template(
    name: str,
    color: str,
    template: BoardTemplate,
    db_path: Optional[str] = None,
) -> int:
    """Crea un nuevo tablero en la base de datos a partir de una plantilla dada."""
    template = localized(template)
    board_id = database.create_board(
        name=name,
        color=color,
        db_path=db_path,
        ai_system_prompt=template.ai_system_prompt or None,
    )
    if template.prompt_pack:
        database.set_board_prompt_pack(board_id, template.prompt_pack, db_path)
    apply_template_to_board(board_id=board_id, template=template, db_path=db_path)
    return board_id


def create_getting_started_board(db_path: Optional[str] = None) -> int:
    """Crea el tablero tutorial interactivo '🚀 Primeros Pasos' a partir de su plantilla."""
    return create_board_from_template(
        name=t("main.onboarding.board_name"),
        color="#2563eb",
        template=TEMPLATE_GETTING_STARTED,
        db_path=db_path,
    )


def export_board_to_template(
    board_id: int,
    template_id: str,
    name: str,
    description: str,
    category: str = "Mis Plantillas",
    include_tasks: bool = False,
    db_path: Optional[str] = None,
) -> BoardTemplate:
    """Genera una instancia de BoardTemplate extrayendo la estructura (y opcionalmente tareas) de un tablero existente."""
    board = database.get_board(board_id, db_path=db_path)
    board_color = board["color"] if board else "#3b82f6"

    # Extraer columnas
    columns_data = database.get_columns(board_id, db_path=db_path)
    template_columns = []
    col_id_to_index = {}
    for idx, c in enumerate(columns_data):
        template_columns.append(ColumnTemplate(
            name=c["name"],
            color=c["color"],
            wip_limit=c.get("wip_limit"),
        ))
        col_id_to_index[c["id"]] = idx

    template_tags: List[TagTemplate] = []
    seed_tasks: List[SeedTaskTemplate] = []
    recorded_tag_keys = set()

    if include_tasks:
        for col_id, col_idx in col_id_to_index.items():
            tasks = database.get_tasks(col_id, db_path=db_path)
            for t_item in tasks:
                t_tags = database.get_task_tags(t_item["id"], db_path=db_path)
                tag_values = []
                for tg in t_tags:
                    tag_values.append(tg["value"])
                    key = (tg["category"], tg["value"])
                    if key not in recorded_tag_keys:
                        recorded_tag_keys.add(key)
                        template_tags.append(TagTemplate(
                            category=tg["category"],
                            value=tg["value"],
                            color=tg["color"],
                        ))

                seed_tasks.append(SeedTaskTemplate(
                    title=t_item["title"],
                    column_index=col_idx,
                    description=t_item.get("description", "") or "",
                    tags=tag_values,
                    due_days_offset=None,
                ))

    prompt_val = (board.get("ai_system_prompt") or "") if board else ""

    return BoardTemplate(
        id=template_id,
        name=name,
        description=description,
        category=category,
        color=board_color,
        icon="table",
        columns=template_columns,
        default_tags=template_tags,
        seed_tasks=seed_tasks,
        ai_system_prompt=prompt_val,
        is_builtin=False,
        prompt_pack=(board.get("prompt_pack") or "") if board else "",
    )
