from PySide6.QtCore import Qt, QMimeData, QPoint, Signal, QRect, QSize
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QMenu, QApplication, QLayout
)
from PySide6.QtGui import QDrag, QPixmap, QCursor, QPainter, QColor, QIcon, QPolygon, QPen
from datetime import datetime
import styles
from styles import hex_to_rgb


class FlowLayout(QLayout):
    """Layout que distribuye los widgets de izquierda a derecha y salta de línea si no caben."""
    def __init__(self, parent=None, margin=0, spacing=4):
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    def doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(+left, +top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        spaceX = self.spacing()
        spaceY = self.spacing()

        for item in self.itemList:
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom


def make_glyph_icon(kind, color, size=16):
    """Dibuja un icono (triángulo o lápiz) como QPixmap, sin depender de fuentes.

    Los glifos Unicode de flechas/lápiz no se renderizan de forma fiable en todas las
    fuentes/instalaciones de Windows, así que los pintamos a mano (siempre visibles)."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    c = QColor(color)
    s = float(size)
    if kind in ("left", "right"):
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        if kind == "left":   # ◀
            pts = [QPoint(int(s * 0.62), int(s * 0.20)),
                   QPoint(int(s * 0.62), int(s * 0.80)),
                   QPoint(int(s * 0.33), int(s * 0.50))]
        else:                # ▶
            pts = [QPoint(int(s * 0.38), int(s * 0.20)),
                   QPoint(int(s * 0.38), int(s * 0.80)),
                   QPoint(int(s * 0.67), int(s * 0.50))]
        p.drawPolygon(QPolygon(pts))
    elif kind == "pencil":   # lápiz (editar)
        pen = QPen(c, max(2, int(s * 0.16)))
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        p.drawLine(int(s * 0.28), int(s * 0.72), int(s * 0.60), int(s * 0.40))  # cuerpo
        p.setPen(Qt.NoPen)
        p.setBrush(c)
        p.drawPolygon(QPolygon([          # punta (triángulo)
            QPoint(int(s * 0.58), int(s * 0.38)),
            QPoint(int(s * 0.82), int(s * 0.18)),
            QPoint(int(s * 0.68), int(s * 0.48)),
        ]))
    elif kind == "cross":    # ✕ (borrar)
        pen = QPen(c, max(2, int(s * 0.16)))
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        m = s * 0.28
        p.drawLine(int(m), int(m), int(s - m), int(s - m))
        p.drawLine(int(s - m), int(m), int(m), int(s - m))
    p.end()
    return QIcon(pix)


def compute_drop_index(cards_geom, drop_y, dragged_id):
    """Índice de inserción para una tarjeta soltada en `drop_y`.

    `cards_geom` es una lista de `(task_id, y, height)` en orden visual. Se EXCLUYE la
    tarjeta arrastrada (`dragged_id`), que está oculta durante el arrastre: su hueco no
    debe contar. El índice resultante vive en el mismo espacio (sin la tarjeta movida)
    que usa `BoardViewWidget.handle_task_drop`, evitando el off-by-one al soltar por
    debajo de la posición original dentro de la misma columna."""
    cards = [(tid, y, h) for (tid, y, h) in cards_geom if tid != dragged_id]
    for idx, (tid, y, h) in enumerate(cards):
        if drop_y < y + h / 2:
            return idx
    return len(cards)


class TaskCard(QFrame):
    # Emitido cuando se hace click en la tarjeta (y no se ha arrastrado)
    clicked = Signal(int)  # task_id

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data["id"]
        self.drag_start_position = QPoint()
        self.board_color_hex = "#3b82f6"
        
        self.setObjectName("TaskCardFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.init_ui()

    def set_card_style(self, board_color_hex):
        """Aplica dinámicamente el estilo a la tarjeta basándose en el color de fondo del tablero."""
        self.board_color_hex = board_color_hex
        
        # Color base Slate 900 de la ventana (#0f172a)
        base_r, base_g, base_b = 15, 23, 42
        try:
            r, g, b = hex_to_rgb(board_color_hex)
        except Exception:
            r, g, b = 59, 130, 246
            
        alpha = 0.06
        blend_r = int(base_r * (1 - alpha) + r * alpha)
        blend_g = int(base_g * (1 - alpha) + g * alpha)
        blend_b = int(base_b * (1 - alpha) + b * alpha)
        
        # Marco sólido Slate 600 y fondo idéntico al fondo del tablero
        self.setStyleSheet(f"""
            #TaskCardFrame {{
                background-color: rgb({blend_r}, {blend_g}, {blend_b});
                border: 1.5px solid #475569;
                border-radius: 8px;
            }}
            #TaskCardFrame:hover {{
                border: 1.5px solid #3b82f6;
                background-color: rgb({min(255, blend_r + 12)}, {min(255, blend_g + 12)}, {min(255, blend_b + 16)});
            }}
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Título de la tarea
        self.title_label = QLabel(self.task_data["title"])
        self.title_label.setObjectName("TaskCardTitle")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Layout vertical para la metadata (Etiquetas y Fecha)
        self.meta_layout = QVBoxLayout()
        self.meta_layout.setContentsMargins(0, 4, 0, 0)
        self.meta_layout.setSpacing(6)

        # Contenedor para múltiples etiquetas (Fila 1)
        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background: transparent; border: none;")
        self.tags_layout = FlowLayout(self.tags_container, margin=0, spacing=4)
        self.meta_layout.addWidget(self.tags_container)

        # Contenedor para fecha de vencimiento (Fila 2)
        self.due_container = QWidget()
        self.due_container.setStyleSheet("background: transparent; border: none;")
        self.due_layout = QHBoxLayout(self.due_container)
        self.due_layout.setContentsMargins(0, 0, 0, 0)
        self.due_layout.setSpacing(6)

        # La fecha se estiliza en línea (según esté vencida o no), así que no lleva
        # objectName: no existe regla QSS para #TaskCardDueDate.
        self.due_label = QLabel()
        self.due_layout.addWidget(self.due_label)
        self.due_layout.addStretch()  # Empuja la fecha a la izquierda
        self.meta_layout.addWidget(self.due_container)

        layout.addLayout(self.meta_layout)

        # Actualizar las etiquetas y vencimiento
        self.update_tags_and_due(self.task_data.get("tags", []), self.task_data.get("due_date"))

    def update_tags_and_due(self, tags, due_date):
        """Limpia y dibuja las etiquetas actuales y la fecha de vencimiento."""
        # Limpiar etiquetas anteriores
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Añadir las nuevas etiquetas, con formato "Categoría: Valor"
        if tags:
            for tag in tags:
                lbl = QLabel(f"{tag['category']}: {tag['value']}".upper())
                lbl.setStyleSheet(
                    f"background-color: {tag['color']}; color: #ffffff; font-size: 9px; font-weight: bold; border-radius: 4px; padding: 2px 5px;"
                )
                self.tags_layout.addWidget(lbl)
            self.tags_container.show()
        else:
            self.tags_container.hide()

        # Mostrar/Ocultar fecha de vencimiento
        if due_date:
            try:
                dt = datetime.strptime(due_date, "%Y-%m-%d")
                formatted = dt.strftime("%d %b")  # Ej: "09 Jul"

                today = datetime.now().date()
                is_overdue = dt.date() < today

                recurring = self.task_data.get("recurrence", "none") not in (None, "", "none")
                time_txt = f" {self.task_data['due_time']}" if self.task_data.get("due_time") else ""
                n_links = len(self.task_data.get("links", []))
                extra = ("  🔁" if recurring else "") + (f"  🔗{n_links}" if n_links else "")
                self.due_label.setText(f"📅 {formatted}{time_txt}{extra}")
                if is_overdue:
                    self.due_label.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 10px; background-color: rgba(239, 68, 68, 0.15); border-radius: 4px; padding: 2px 4px;")
                else:
                    self.due_label.setStyleSheet("color: #94a3b8; font-size: 10px; background-color: rgba(148, 163, 184, 0.15); border-radius: 4px; padding: 2px 4px;")
            except Exception:
                self.due_label.setText(f"📅 {due_date}")
                self.due_label.setStyleSheet("color: #94a3b8; font-size: 10px;")
            self.due_container.show()
        else:
            self.due_container.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Iniciamos el arrastre (Drag)
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Codificamos el ID de la tarea en formato binario
        mime_data.setData("application/x-ekin-task-id", str(self.task_id).encode("utf-8"))
        # Guardamos el ID de la columna origen
        mime_data.setData("application/x-ekin-source-column-id", str(self.task_data["column_id"]).encode("utf-8"))
        
        drag.setMimeData(mime_data)

        # Generamos una vista preliminar (pixmap) de la tarjeta para mostrarla mientras se arrastra
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        
        # Renderizar directamente sobre el pixmap (es un QPaintDevice)
        self.render(pixmap)
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.position().toPoint())

        # Ocultar la tarjeta original mientras arrastramos
        self.hide()
        
        # Ejecutar la acción drag-and-drop
        drop_action = drag.exec(Qt.MoveAction)
        
        # Si la tarea no se colocó en ningún lado (fue cancelada), volvemos a mostrarla
        if drop_action == Qt.IgnoreAction:
            self.show()

    def mouseReleaseEvent(self, event):
        # Si se soltó el click izquierdo y no se inició drag, se considera un click normal
        if event.button() == Qt.LeftButton:
            click_dist = (event.position().toPoint() - self.drag_start_position).manhattanLength()
            if click_dist < QApplication.startDragDistance():
                self.clicked.emit(self.task_id)
        super().mouseReleaseEvent(event)


class TaskListArea(QWidget):
    # Se emite cuando se completa el drop de una tarea
    # Parámetros: (task_id, target_column_id, position)
    task_dropped = Signal(int, int, int)
    # Se emite cuando una tarea arrastrada entra en esta área
    drag_entered = Signal()
    # Se emite cuando el arrastre sale del área
    drag_left = Signal()

    def __init__(self, column_id, parent=None):
        super().__init__(parent)
        self.column_id = column_id
        self.setAcceptDrops(True)

        # Nota: no llamar a este atributo `layout`; ensombrecería QWidget.layout().
        self.list_layout = QVBoxLayout(self)
        self.list_layout.setContentsMargins(4, 4, 4, 10)
        self.list_layout.setSpacing(8)
        self.list_layout.setAlignment(Qt.AlignTop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
            self.drag_entered.emit()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drag_left.emit()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if mime.hasFormat("application/x-ekin-task-id"):
            task_id = int(mime.data("application/x-ekin-task-id").data().decode("utf-8"))
            event.acceptProposedAction()
            self.drag_left.emit()

            # Calcular la posición de inserción en base al eje Y. La lógica (excluyendo la
            # tarjeta arrastrada, que está oculta) vive en compute_drop_index para poder
            # probarla de forma determinista.
            drop_y = event.position().y()
            cards_geom = []
            for i in range(self.list_layout.count()):
                w = self.list_layout.itemAt(i).widget()
                if isinstance(w, TaskCard):
                    cards_geom.append((w.task_id, w.y(), w.height()))

            target_pos = compute_drop_index(cards_geom, drop_y, task_id)
            self.task_dropped.emit(task_id, self.column_id, target_pos)
        else:
            event.ignore()


class DraggableColumnTitle(QLabel):
    """QLabel del título de columna que permite iniciar un arrastre para reordenarla o moverla a otro tablero."""
    def __init__(self, text, column_widget, parent=None):
        super().__init__(text, parent)
        self.column_widget = column_widget
        self.drag_start_position = QPoint()
        self.setCursor(Qt.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData("application/x-ekin-column-id", str(self.column_widget.column_id).encode("utf-8"))
        mime_data.setData(
            "application/x-ekin-column-source-board-id",
            str(self.column_widget.column_data["board_id"]).encode("utf-8")
        )
        drag.setMimeData(mime_data)

        pixmap = QPixmap(self.column_widget.size())
        pixmap.fill(Qt.transparent)
        self.column_widget.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.mapTo(self.column_widget, event.position().toPoint()))

        self.column_widget.hide()
        drop_action = drag.exec(Qt.MoveAction)

        if drop_action == Qt.IgnoreAction:
            self.column_widget.show()


class VerticalLabel(QLabel):
    """Etiqueta con el texto girado 90° (nombre de una columna plegada)."""
    def __init__(self, text="", color=None, parent=None):
        super().__init__(text, parent)
        self._color = color or "#e2e8f0"
        self.setStyleSheet("background: transparent; border: none;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(self._color))
        painter.setFont(self.font())
        painter.translate(self.width(), 0)
        painter.rotate(90)
        painter.drawText(QRect(0, 0, self.height(), self.width()),
                         int(Qt.AlignLeft | Qt.AlignVCenter), self.text())
        painter.end()

    def sizeHint(self):
        s = super().sizeHint()
        return QSize(s.height(), s.width())

    def minimumSizeHint(self):
        s = super().minimumSizeHint()
        return QSize(s.height(), s.width())


class ColumnWidget(QFrame):
    # Señales reenviadas
    task_dropped = Signal(int, int, int) # task_id, column_id, position
    add_task_requested = Signal(int)     # column_id
    edit_column_requested = Signal(int) # column_id
    delete_column_requested = Signal(int) # column_id
    copy_column_requested = Signal(int)  # column_id
    collapse_toggle_requested = Signal(int)  # column_id (plegar/desplegar)
    collapsed_card_drop = Signal(int, int)   # task_id, column_id (soltar tarjeta en columna plegada)

    COLLAPSED_WIDTH = 46
    EXPANDED_WIDTH = 280

    def __init__(self, column_data, parent=None):
        super().__init__(parent)
        self.column_data = column_data
        self.column_id = column_data["id"]
        self.collapsed = bool(column_data.get("collapsed", 0))

        self.setObjectName("ColumnContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(self.COLLAPSED_WIDTH if self.collapsed else self.EXPANDED_WIDTH)
        self.init_ui()

    def _column_icon_button(self, kind, tooltip):
        """Pequeño botón cuadrado con un icono PINTADO (left/right/pencil) a juego con
        el color de la columna. Se pinta a mano para no depender de glifos de fuente."""
        btn = QPushButton()
        btn.setFixedSize(24, 24)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        try:
            r, g, b = hex_to_rgb(self.column_data["color"])
        except Exception:
            r, g, b = 59, 130, 246
        color = self.column_data["color"]
        btn.setIcon(make_glyph_icon(kind, color, 16))
        btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, 0.1);
                border: 1.2px solid rgba({r}, {g}, {b}, 0.45);
                border-radius: 4px;
                color: {color};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba({r}, {g}, {b}, 0.25);
                border-color: {color};
                color: #ffffff;
            }}
            QPushButton:pressed {{ background-color: rgba({r}, {g}, {b}, 0.4); }}
        """)
        return btn

    def init_ui(self):
        if self.collapsed:
            self._init_collapsed_ui()
        else:
            self._init_expanded_ui()

    def _init_collapsed_ui(self):
        """Columna plegada: tira estrecha con botón de desplegar, contador y nombre vertical.
        Acepta soltar una tarjeta encima: se despliega y recibe la tarjeta."""
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        expand_btn = self._column_icon_button("right", "Desplegar columna")
        expand_btn.clicked.connect(lambda: self.collapse_toggle_requested.emit(self.column_id))
        layout.addWidget(expand_btn, 0, Qt.AlignHCenter)

        count = self.column_data.get("task_count", 0)
        count_label = QLabel(str(count))
        count_label.setAlignment(Qt.AlignHCenter)
        count_label.setToolTip(f"{count} tarea(s)")
        count_label.setStyleSheet(
            f"color: {styles.COLORS['text_muted']}; font-size: 12px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(count_label, 0, Qt.AlignHCenter)

        name_label = VerticalLabel(self.column_data["name"], self.column_data["color"])
        f = name_label.font()
        f.setBold(True)
        name_label.setFont(f)
        layout.addWidget(name_label, 1, Qt.AlignHCenter)

        self.set_column_style(dragging=False)

    def _init_expanded_ui(self):
        # Layout principal de la columna (Vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # 1. Cabecera de la columna
        header_widget = QWidget()
        header_widget.setObjectName("ColumnHeaderBar")
        # Aplicamos el color de borde superior correspondiente al color de la columna
        header_widget.setStyleSheet(
            f"#ColumnHeaderBar {{ border-bottom: 3px solid {self.column_data['color']}; padding-bottom: 4px; }}"
        )

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(4)

        # Nombre de la columna (arrastrable para reordenar o mover a otro tablero)
        self.title_label = DraggableColumnTitle(self.column_data["name"], self)
        self.title_label.setObjectName("ColumnTitle")
        self.title_label.setToolTip("Arrastra para reordenar o mover esta columna a otro tablero")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Botón para plegar la columna (triángulo hacia la izquierda, pintado)
        collapse_btn = self._column_icon_button("left", "Plegar columna")
        collapse_btn.clicked.connect(lambda: self.collapse_toggle_requested.emit(self.column_id))
        header_layout.addWidget(collapse_btn)

        # Botón de edición/opciones de la columna (lápiz pintado)
        self.menu_btn = self._column_icon_button("pencil", "Editar columna (opciones: editar, copiar, eliminar)")
        self.menu_btn.clicked.connect(self.show_column_menu)
        header_layout.addWidget(self.menu_btn)

        main_layout.addWidget(header_widget)

        # 2. Área scrollable para las tareas
        scroll_area = QScrollArea()
        scroll_area.setObjectName("TaskListArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # El contenedor interno que acepta drops
        self.list_area = TaskListArea(self.column_id)
        self.list_area.task_dropped.connect(self.task_dropped.emit)

        # Aplicar el estilo dinámico inicial a la columna
        self.set_column_style(dragging=False)

        # Efecto visual al arrastrar sobre esta columna usando su propio color
        self.list_area.drag_entered.connect(lambda: self.set_column_style(dragging=True))
        self.list_area.drag_left.connect(lambda: self.set_column_style(dragging=False))

        scroll_area.setWidget(self.list_area)
        main_layout.addWidget(scroll_area)

        # 3. Botón para añadir una nueva tarea
        self.add_task_btn = QPushButton("➕ Añadir Tarea")
        self.add_task_btn.setObjectName("AddTaskButton")
        self.add_task_btn.setCursor(Qt.PointingHandCursor)
        self.add_task_btn.clicked.connect(lambda: self.add_task_requested.emit(self.column_id))
        main_layout.addWidget(self.add_task_btn)

    # --- Soltar una tarjeta sobre una columna PLEGADA (solo activo si collapsed) ---
    def dragEnterEvent(self, event):
        if self.collapsed and event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
            self.set_column_style(dragging=True)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if self.collapsed and event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        if self.collapsed:
            self.set_column_style(dragging=False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if self.collapsed and mime.hasFormat("application/x-ekin-task-id"):
            task_id = int(mime.data("application/x-ekin-task-id").data().decode("utf-8"))
            event.acceptProposedAction()
            self.set_column_style(dragging=False)
            self.collapsed_card_drop.emit(task_id, self.column_id)
        else:
            event.ignore()

    def set_column_style(self, dragging=False):
        """Establece el diseño de la columna (borde y fondo) basado en su color."""
        try:
            r, g, b = hex_to_rgb(self.column_data["color"])
        except Exception:
            r, g, b = 59, 130, 246  # Azul por defecto
            
        if dragging:
            # Fondo más iluminado y borde discontinuo más grueso
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: rgba({r}, {g}, {b}, 0.12);
                    border: 2px dashed rgba({r}, {g}, {b}, 0.8);
                }}
            """)
        else:
            # Fondo muy sutil y borde semi-transparente que enmarca la columna
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: rgba({r}, {g}, {b}, 0.04);
                    border: 1.5px solid rgba({r}, {g}, {b}, 0.3);
                }}
            """)

    def show_column_menu(self):
        """Muestra el menú contextual de la columna para editarla, moverla, copiarla o borrarla."""
        menu = QMenu(self)
        # Aplicar el tema oscuro al menú
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {styles.COLORS['bg_sidebar']};
                border: 1px solid {styles.COLORS['border']};
                border-radius: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
                color: {styles.COLORS['text_main']};
            }}
            QMenu::item:selected {{
                background-color: {styles.COLORS['accent_blue']};
            }}
        """)
        
        edit_action = menu.addAction("✏️ Editar Columna")
        copy_action = menu.addAction("📋 Copiar a otro tablero...")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Eliminar Columna")

        action = menu.exec(QCursor.pos())
        if action == edit_action:
            self.edit_column_requested.emit(self.column_id)
        elif action == copy_action:
            self.copy_column_requested.emit(self.column_id)
        elif action == delete_action:
            self.delete_column_requested.emit(self.column_id)

    def clear_tasks(self):
        """Elimina todos los widgets de tarea de la columna."""
        # Limpiar el layout
        while self.list_area.list_layout.count():
            item = self.list_area.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_task_card(self, card_widget):
        """Añade una tarjeta de tarea a la columna (no-op si está plegada)."""
        if not hasattr(self, "list_area"):
            return
        self.list_area.list_layout.addWidget(card_widget)
