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


# --- PLANTILLAS DE FÁBRICA (BUILT-IN) ---

TEMPLATE_GETTING_STARTED = BoardTemplate(
    id="getting_started",
    name="🚀 Primeros Pasos",
    description="Tablero interactivo tutorial in-situ con misiones guiadas para dominar las tarjetas, columnas, atajos e integraciones.",
    category="Tutorial & Onboarding",
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
                "- **Vincular a la Nube**: Haz clic en el botón de la nube en la cabecera del tablero o en las opciones del tablero (`...` o clic derecho en la barra lateral).\n"
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
            title="8. Conecta agentes IA con MCP o abre Ajustes (⚙️)",
            column_index=2,
            description=(
                "### 🤖 Ecosistema Local MCP (Model Context Protocol)\n"
                "- Pulsa el botón **`🤖 MCP`** en la cabecera superior del tablero para conectar asistentes IA (**Claude Code, Cursor, AGY CLI y Claude Desktop**).\n"
                "- Cada tablero opera con un sandbox aislado y token secreto.\n"
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
                "- Elige empezar con un lienzo en blanco o con una de las plantillas especializadas (**Desarrollo Software Agile**, **Opositor**, **GTD / Personal**).\n"
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
    prompt_pack="dev",
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
    prompt_pack="opositor",
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
