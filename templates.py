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
        )


# --- PLANTILLAS DE FÁBRICA (BUILT-IN) ---

TEMPLATE_BLANK = BoardTemplate(
    id="blank",
    name="Tablero en Blanco",
    description="Lienzo vacío para diseñar tu propio flujo de trabajo desde cero.",
    category="Básico",
    color="#3b82f6",
    icon="table",
    columns=[],
    default_tags=[],
    seed_tasks=[],
    ai_system_prompt="Asistente general de productividad para gestión de tareas Kanban en Ekin.",
    is_builtin=True,
)

TEMPLATE_SOFTWARE_AGILE = BoardTemplate(
    id="software_agile",
    name="Desarrollo Software (Agile/Kanban)",
    description="Flujo completo de ingeniería: Triage, Especificación, En Desarrollo, Code Review y Producción con límites WIP.",
    category="Ingeniería & Software",
    color="#2563eb",
    icon="code",
    columns=[
        ColumnTemplate("📥 Backlog & Triage", "#64748b", None),
        ColumnTemplate("📋 Ready to Code", "#8b5cf6", 5),
        ColumnTemplate("⚡ In Progress", "#0ea5e9", 3),
        ColumnTemplate("🔍 Code Review & QA", "#f59e0b", 3),
        ColumnTemplate("🚀 Shipped / Done", "#10b981", None),
    ],
    default_tags=[
        TagTemplate("Tipo", "bug", "#ef4444"),
        TagTemplate("Tipo", "feature", "#3b82f6"),
        TagTemplate("Tipo", "refactor", "#8b5cf6"),
        TagTemplate("Tipo", "tech-debt", "#f97316"),
        TagTemplate("Tipo", "security", "#dc2626"),
        TagTemplate("Priority", "P0-Critical", "#ef4444"),
        TagTemplate("Priority", "P1-High", "#f59e0b"),
        TagTemplate("Priority", "P2-Medium", "#3b82f6"),
        TagTemplate("Priority", "P3-Low", "#6b7280"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title="Configurar pipeline CI/CD y tests",
            column_index=1,
            description="### Criterios de Aceptación (DoD)\n- [ ] Linter ruff sin advertencias (0 errores)\n- [ ] Cobertura de tests unitarios completa\n- [ ] Verificación de regresión en cada commit",
            priority="P1-High",
            tags=["feature", "tech-debt"],
            due_days_offset=3,
        ),
        SeedTaskTemplate(
            title="Documentar arquitectura y dependencias",
            column_index=0,
            description="Mantener actualizado el grafo de componentes, esquemas de base de datos y manual técnico de la arquitectura.",
            priority="P2-Medium",
            tags=["tech-debt"],
            due_days_offset=7,
        ),
    ],
    ai_system_prompt=(
        "Actúas como Tech Lead y Scrum Master asistente para este tablero de desarrollo software. "
        "Cuando el usuario o tú creéis o actualicéis tareas, verifica que tengan una especificación "
        "técnica clara, criterios de aceptación (Definition of Done) y cobertura de pruebas. "
        "Ayuda a desglosar tareas complejas y a mantener los límites WIP de desarrollo respetados."
    ),
    is_builtin=True,
)

TEMPLATE_OPOSITOR = BoardTemplate(
    id="opositor_study",
    name="Opositor (Estudio Sistemático)",
    description="Metodología basada en la curva del olvido y repetición espaciada: lecturas, esquemas, vueltas al temario y simulacros.",
    category="Estudio & Oposiciones",
    color="#7c3aed",
    icon="list",
    columns=[
        ColumnTemplate("📚 Temas Pendientes", "#64748b", None),
        ColumnTemplate("📖 1ª Vuelta: Lectura & Subrayado", "#0284c7", 4),
        ColumnTemplate("✍️ 2ª Vuelta: Esquemas & Resumen", "#8b5cf6", 3),
        ColumnTemplate("🔄 Repaso Espaciado (Vueltas 3+)", "#d97706", 5),
        ColumnTemplate("🎯 Simulacro & Test", "#dc2626", 4),
        ColumnTemplate("🏆 Tema Dominado", "#059669", None),
    ],
    default_tags=[
        TagTemplate("Bloque", "Constitucional", "#3b82f6"),
        TagTemplate("Bloque", "Administrativo", "#8b5cf6"),
        TagTemplate("Bloque", "Parte Específica", "#0ea5e9"),
        TagTemplate("Bloque", "Ofimática / Informática", "#10b981"),
        TagTemplate("Fase", "Test Fallado", "#ef4444"),
        TagTemplate("Fase", "Duda a Consultar", "#f59e0b"),
        TagTemplate("Fase", "Tema Clave Examen", "#e11d48"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title="Tema 1: Constitución Española de 1978",
            column_index=1,
            description="### Objetivos de la Vuelta\n- [ ] Título Preliminar y Título I (Derechos Fundamentales)\n- [ ] Artículos clave: 14, 24, 53, 86\n- [ ] Esquema de plazos y mayorías parlamentarias\n- [ ] Batería de 30 preguntas de test oficial",
            tags=["Constitucional", "Tema Clave Examen"],
            due_days_offset=2,
        ),
        SeedTaskTemplate(
            title="Planificar calendario de simulacros cronometrados",
            column_index=0,
            description="Reservar los sábados por la mañana para simulacros completos de examen en condiciones reales (sin apuntes ni pausas).",
            tags=["Administrativo"],
            due_days_offset=5,
        ),
    ],
    ai_system_prompt=(
        "Actúas como un preparador de oposiciones y tutor de estudio sistemático. "
        "Ayuda al opositor a planificar intervalos de repaso según la curva del olvido (1-7-30 días), "
        "genera preguntas tipo test de autoevaluación con 4 opciones sobre los artículos o normas "
        "asociadas al tema, y detecta trampas de examen habituales de la legislación aplicable."
    ),
    is_builtin=True,
)

TEMPLATE_GTD_PERSONAL = BoardTemplate(
    id="gtd_personal",
    name="Personal / GTD (Getting Things Done)",
    description="Metodología GTD para despejar la mente: capturar, procesar, organizar y actuar con enfoque.",
    category="Productividad Personal",
    color="#059669",
    icon="check",
    columns=[
        ColumnTemplate("📥 Bandeja de Entrada (Inbox)", "#64748b", None),
        ColumnTemplate("⚡ Próximas Acciones (@Next)", "#0284c7", 7),
        ColumnTemplate("⏳ En Espera (@Waiting)", "#d97706", None),
        ColumnTemplate("💡 Algún Día / Quizás", "#8b5cf6", None),
        ColumnTemplate("✅ Terminado", "#059669", None),
    ],
    default_tags=[
        TagTemplate("Contexto", "@ordenador", "#3b82f6"),
        TagTemplate("Contexto", "@llamadas", "#10b981"),
        TagTemplate("Contexto", "@casa", "#f59e0b"),
        TagTemplate("Contexto", "@compras", "#ec4899"),
        TagTemplate("Contexto", "@recados", "#8b5cf6"),
    ],
    seed_tasks=[
        SeedTaskTemplate(
            title="Revisión Semanal de compromisos y bandejas",
            column_index=1,
            description="Vaciar la bandeja de entrada, revisar listas de @Next y @Waiting, actualizar proyectos y calendarizar la próxima semana.",
            tags=["@ordenador"],
            due_days_offset=3,
        ),
    ],
    ai_system_prompt=(
        "Actúas como un asistente de productividad GTD (Getting Things Done). "
        "Cuando el usuario registre pensamientos o notas en Inbox, ayúdale a procesarlos preguntando: "
        "¿Es accionable? ¿Cuál es la siguiente acción física inmediata? Si lleva menos de 2 minutos, "
        "hazla ya; si no, clasifícala en @Next con su contexto (@ordenador, @llamadas, etc.) o en @Waiting."
    ),
    is_builtin=True,
)

BUILTIN_TEMPLATES = [
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
    """Retorna una lista de copias de las plantillas predefinidas de fábrica."""
    return [BoardTemplate.from_dict(t.to_dict()) for t in BUILTIN_TEMPLATES]


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


def create_board_from_template(
    name: str,
    color: str,
    template: BoardTemplate,
    db_path: Optional[str] = None,
) -> int:
    """Crea un nuevo tablero en la base de datos a partir de una plantilla dada."""
    board_id = database.create_board(
        name=name,
        color=color,
        db_path=db_path,
        ai_system_prompt=template.ai_system_prompt or None,
    )
    apply_template_to_board(board_id=board_id, template=template, db_path=db_path)
    return board_id


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
    )
