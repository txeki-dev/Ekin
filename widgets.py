from PySide6.QtCore import Qt, QMimeData, QPoint, Signal, QRect, QSize, QTimer
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QMenu, QApplication, QLayout, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QDrag, QPixmap, QCursor, QPainter, QColor
from datetime import datetime
import styles
from strings import t
from icons import lucide_icon


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
    # Emitido al pulsar Ctrl + Clic para selección múltiple
    ctrl_clicked = Signal(int)  # task_id
    # Emitido al pulsar la pastilla de tablero enlazado (no abre el detalle de la tarea)
    board_link_clicked = Signal(int)  # linked_board_id
    # Emitido al terminar CUALQUIER arrastre de esta tarjeta (soltada donde sea, o cancelado):
    # única señal fiable para saber que QDrag.exec() ha devuelto el control.
    drag_ended = Signal()

    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.task_id = task_data["id"]
        self.drag_start_position = QPoint()
        self.board_color_hex = "#3b82f6"
        self._timer_alert_hours = 24
        self.is_selected = False

        self.setObjectName("TaskCardFrame")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.init_ui()

        # Sombra de elevación: la tarjeta no lleva borde; la profundidad la da la sombra
        # (sm en reposo, md en hover), tal como pide el diseño.
        self._shadow = QGraphicsDropShadowEffect(self)
        self._apply_shadow(hovered=False)
        self.setGraphicsEffect(self._shadow)

    def _apply_shadow(self, hovered):
        self._shadow.setBlurRadius(20 if hovered else 10)
        self._shadow.setXOffset(0)
        self._shadow.setYOffset(6 if hovered else 2)
        self._shadow.setColor(QColor(46, 43, 37, 60 if hovered else 40))

    def enterEvent(self, event):
        self._apply_shadow(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_shadow(hovered=False)
        super().leaveEvent(event)

    def set_card_style(self, board_color_hex=None):
        """Aplica el estilo de la tarjeta: crema plana sin borde (la profundidad la da la
        sombra) o, si está seleccionada, relleno tenue de acento con anillo de 2 px."""
        if board_color_hex is not None:
            self.board_color_hex = board_color_hex

        # Estilo inline (Qt solo pinta el fondo de estos QFrame vía stylesheet propio; la
        # QSS global por objectName no lo pinta). Se re-aplica en cada load_board, así que el
        # conmutador de tema lo reconstruye con la paleta nueva.
        card_bg = styles.COLORS['accent_tint'] if getattr(self, "is_selected", False) else styles.COLORS['bg_card']
        if getattr(self, "is_selected", False):
            self.setStyleSheet(f"""
                #TaskCardFrame {{
                    background-color: {card_bg};
                    border: 2px solid {styles.COLORS['accent']};
                    border-radius: 16px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #TaskCardFrame {{
                    background-color: {card_bg};
                    border: none;
                    border-radius: 16px;
                }}
            """)
        # El título (QLabel) sobre un padre con fondo estilado pinta el color de la ventana;
        # se fija su fondo al de la tarjeta para que integre (sin caja oscura).
        self.title_label.setStyleSheet(f"background-color: {card_bg};")

    def set_selected(self, selected: bool):
        """Activa o desactiva el estado visual de selección múltiple."""
        self.is_selected = selected
        if hasattr(self, "selection_badge"):
            self.selection_badge.setVisible(selected)
        self.set_card_style()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Cabecera de la tarjeta: Título + Badge de selección
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)

        # Título de la tarea
        self.title_label = QLabel(self.task_data["title"])
        self.title_label.setObjectName("TaskCardTitle")
        self.title_label.setWordWrap(True)
        title_row.addWidget(self.title_label, stretch=1)

        # Insignia de selección (visible cuando is_selected=True)
        self.selection_badge = QLabel("✓")
        self.selection_badge.setFixedSize(18, 18)
        self.selection_badge.setAlignment(Qt.AlignCenter)
        self.selection_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {styles.COLORS['accent']};
                color: {styles.COLORS['on_accent']};
                font-size: 11px;
                font-weight: bold;
                border-radius: 9px;
            }}
        """)
        self.selection_badge.hide()
        title_row.addWidget(self.selection_badge, alignment=Qt.AlignTop)

        layout.addLayout(title_row)

        # Metadata en 3 filas por orden de lectura (como el handoff):
        #   Fila 1 → etiquetas (categoría·valor, sin la de Prioridad), con salto de línea
        #   Fila 2 → Prioridad (su propia fila)
        #   Fila 3 → vencimiento + temporizador + tablero enlazado, en línea
        self.meta_layout = QVBoxLayout()
        self.meta_layout.setContentsMargins(0, 4, 0, 0)
        self.meta_layout.setSpacing(6)

        # --- Fila 1: etiquetas (excluye Prioridad) ---
        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background: transparent; border: none;")
        self.tags_layout = FlowLayout(self.tags_container, margin=0, spacing=4)
        self.meta_layout.addWidget(self.tags_container)

        # --- Fila 2: Prioridad ---
        self.priority_container = QWidget()
        self.priority_container.setStyleSheet("background: transparent; border: none;")
        priority_layout = QHBoxLayout(self.priority_container)
        priority_layout.setContentsMargins(0, 0, 0, 0)
        priority_layout.setSpacing(6)
        self.priority_label = QLabel()
        priority_layout.addWidget(self.priority_label)
        priority_layout.addStretch()
        self.meta_layout.addWidget(self.priority_container)

        # --- Fila 3: vencimiento + temporizador + tablero enlazado ---
        row3 = QWidget()
        row3.setStyleSheet("background: transparent; border: none;")
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(0, 0, 0, 0)
        row3_layout.setSpacing(6)

        self.due_container = QWidget()
        self.due_container.setStyleSheet("background: transparent; border: none;")
        self.due_layout = QHBoxLayout(self.due_container)
        self.due_layout.setContentsMargins(0, 0, 0, 0)
        self.due_layout.setSpacing(6)
        # La fecha se estiliza en línea (según esté vencida o no), así que no lleva objectName.
        self.due_label = QLabel()
        self.due_layout.addWidget(self.due_label)
        row3_layout.addWidget(self.due_container)

        self.timer_container = QWidget()
        self.timer_container.setStyleSheet("background: transparent; border: none;")
        timer_row_layout = QHBoxLayout(self.timer_container)
        timer_row_layout.setContentsMargins(0, 0, 0, 0)
        timer_row_layout.setSpacing(6)
        self.timer_badge_label = QLabel()
        timer_row_layout.addWidget(self.timer_badge_label)
        row3_layout.addWidget(self.timer_container)

        self.board_link_container = QWidget()
        self.board_link_container.setStyleSheet("background: transparent; border: none;")
        board_link_layout = QHBoxLayout(self.board_link_container)
        board_link_layout.setContentsMargins(0, 0, 0, 0)
        board_link_layout.setSpacing(6)
        self.board_link_btn = QPushButton()
        self.board_link_btn.setCursor(Qt.PointingHandCursor)
        self.board_link_btn.setToolTip(t("widgets.card.board_link_tooltip"))
        self.board_link_btn.clicked.connect(self._emit_board_link_clicked)
        board_link_layout.addWidget(self.board_link_btn)
        row3_layout.addWidget(self.board_link_container)
        row3_layout.addStretch()
        self.meta_layout.addWidget(row3)

        layout.addLayout(self.meta_layout)

        # Actualizar las etiquetas y vencimiento
        self.update_tags_and_due(self.task_data.get("tags", []), self.task_data.get("due_date"))
        self._update_board_link()
        self.update_timer_badge()

    def _emit_board_link_clicked(self):
        board_id = self.task_data.get("linked_board_id")
        if board_id:
            self.board_link_clicked.emit(board_id)

    def _update_board_link(self):
        """Dibuja (o esconde) la pastilla clicable hacia el tablero enlazado, si lo hay."""
        board_id = self.task_data.get("linked_board_id")
        if not board_id:
            self.board_link_container.hide()
            return

        name = self.task_data.get("linked_board_name") or "?"
        color = self.task_data.get("linked_board_color") or "#3b82f6"

        # Píldora neutra legible en ambos temas: fondo hover neutro, texto principal, y el
        # color del tablero solo en el icono de enlace (no como fondo/texto de bajo contraste).
        self.board_link_btn.setText(f" {name}")
        self.board_link_btn.setIcon(lucide_icon("link-2", color, 13))
        self.board_link_btn.setIconSize(QSize(13, 13))
        self.board_link_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLORS['bg_hover']};
                border: none;
                border-radius: 9px;
                color: {styles.COLORS['text_soft']};
                font-size: 11px;
                font-weight: 600;
                padding: 3px 9px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {styles.COLORS['bg_column']};
            }}
        """)
        self.board_link_container.show()

    def set_timer_alert_hours(self, hours):
        """Umbral (en horas) a partir del cual la insignia del temporizador se resalta en
        rojo. Se fija externamente tras construir la tarjeta -- TaskCard no tiene acceso
        directo a app_settings (ver BoardViewWidget._build_column_widget)."""
        self._timer_alert_hours = hours
        self.update_timer_badge()

    def update_timer_badge(self):
        """Dibuja (o esconde) la insignia de tiempo transcurrido del temporizador, en rojo
        si supera self._timer_alert_hours -- mismo patrón visual que la fecha de vencimiento
        vencida/no vencida en update_tags_and_due."""
        started_at = self.task_data.get("timer_started_at")
        if not started_at:
            self.timer_container.hide()
            return
        try:
            started = datetime.fromisoformat(started_at)
        except ValueError:
            self.timer_container.hide()
            return

        elapsed = datetime.now() - started
        elapsed_hours = elapsed.total_seconds() / 3600
        is_stale = elapsed_hours >= self._timer_alert_hours

        self.timer_badge_label.setText(styles.format_elapsed_time(elapsed.total_seconds()))
        if is_stale:
            self.timer_badge_label.setStyleSheet(
                f"color: {styles.COLORS['danger']}; font-weight: bold; font-size: 11px; "
                f"background-color: {styles.COLORS['accent_tint_2']}; border-radius: 9px; padding: 3px 9px;"
            )
        else:
            self.timer_badge_label.setStyleSheet(
                f"color: {styles.COLORS['text_muted']}; font-size: 11px; "
                f"background-color: {styles.COLORS['bg_hover']}; border-radius: 9px; padding: 3px 9px;"
            )
        self.timer_container.show()

    def update_tags_and_due(self, tags, due_date):
        """Limpia y dibuja las etiquetas actuales y la fecha de vencimiento."""
        # Limpiar etiquetas anteriores
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Separar la etiqueta de Prioridad (va en su propia fila) del resto de etiquetas.
        priority_names = {"priority", "prioridad"}
        regular_tags = [tg for tg in tags if tg["category"].lower() not in priority_names]
        priority_tag = next((tg for tg in tags if tg["category"].lower() in priority_names), None)

        # Fila 1: etiquetas normales (formato "Categoría · Valor")
        if regular_tags:
            for tag in regular_tags:
                lbl = QLabel(f"{tag['category']} · {tag['value']}")
                txt = styles.contrast_text(tag['color'])
                lbl.setStyleSheet(
                    f"{styles.tag_pill_css(tag['color'])} border-radius: 9px; color: {txt}; "
                    f"font-size: 10px; font-weight: 600; padding: 3px 9px;"
                )
                self.tags_layout.addWidget(lbl)
            self.tags_container.show()
        else:
            self.tags_container.hide()

        # Fila 2: Prioridad como píldora propia (icono de banderín + valor)
        if priority_tag:
            ptxt = styles.contrast_text(priority_tag['color'])
            self.priority_label.setText(f"{priority_tag['category']} · {priority_tag['value']}")
            self.priority_label.setStyleSheet(
                f"{styles.tag_pill_css(priority_tag['color'])} border-radius: 9px; color: {ptxt}; "
                f"font-size: 10px; font-weight: 600; padding: 3px 9px;"
            )
            self.priority_container.show()
        else:
            self.priority_container.hide()

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
                rec_word = {"daily": "Daily", "weekly": "Weekly", "monthly": "Monthly"}.get(
                    str(self.task_data.get("recurrence", "")).lower(), ""
                )
                extra = (f" · {rec_word}" if recurring and rec_word else "") + (f" · {n_links} link(s)" if n_links else "")
                self.due_label.setText(f"{formatted}{time_txt}{extra}")
                if is_overdue:
                    self.due_label.setStyleSheet(
                        f"color: {styles.COLORS['accent_ink']}; font-weight: 600; font-size: 11px; "
                        f"background-color: {styles.COLORS['accent_tint_2']}; border-radius: 9px; padding: 3px 9px;"
                    )
                else:
                    self.due_label.setStyleSheet(
                        f"color: {styles.COLORS['text_muted']}; font-size: 11px; padding: 3px 0px;"
                    )
            except Exception:
                self.due_label.setText(f"{due_date}")
                self.due_label.setStyleSheet(f"color: {styles.COLORS['text_muted']}; font-size: 11px;")
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

        # QDrag.exec() ha devuelto el control: el arrastre ha terminado del todo
        # (soltada en cualquier sitio, o cancelada). Único punto fiable para que
        # BoardViewWidget sepa que debe cerrar una posible expansión por hover.
        self.drag_ended.emit()

    def mouseReleaseEvent(self, event):
        # Si se soltó el click izquierdo y no se inició drag, se considera un click normal
        if event.button() == Qt.LeftButton:
            click_dist = (event.position().toPoint() - self.drag_start_position).manhattanLength()
            if click_dist < QApplication.startDragDistance():
                if event.modifiers() & Qt.ControlModifier:
                    self.ctrl_clicked.emit(self.task_id)
                else:
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
    hover_expand_requested = Signal(int)     # column_id (hover sostenido sobre columna plegada)
    column_activated = Signal(int)           # column_id (clic en cualquier parte "en blanco" de la columna)

    COLLAPSED_WIDTH = 56
    EXPANDED_WIDTH = 288
    HOVER_EXPAND_MS = 650

    def __init__(self, column_data, parent=None):
        super().__init__(parent)
        self.column_data = column_data
        self.column_id = column_data["id"]
        self.collapsed = bool(column_data.get("collapsed", 0))

        self.setObjectName("ColumnContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(self.COLLAPSED_WIDTH if self.collapsed else self.EXPANDED_WIDTH)

        self._hover_timer = QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.setInterval(self.HOVER_EXPAND_MS)
        self._hover_timer.timeout.connect(self._on_hover_timeout)

        self.init_ui()

    def _on_hover_timeout(self):
        """Se ha mantenido el hover de un drag sobre esta columna PLEGADA lo
        suficiente: pide que se despliegue para poder elegir posición."""
        if self.collapsed:
            self.hover_expand_requested.emit(self.column_id)

    def mousePressEvent(self, event):
        """Clic en cualquier parte de la columna no ya consumida por un botón/tarjeta
        hijo (los widgets internos consumen su propio click y no burbujean aquí):
        sirve de pista para "última columna activa" (ver BoardViewWidget.quick_add_task)."""
        self.column_activated.emit(self.column_id)
        super().mousePressEvent(event)

    def _column_icon_button(self, kind, tooltip):
        """Botón circular sin marco con un icono Lucide (chevron para plegar/desplegar,
        más-vertical para el menú) a juego con el color de la columna."""
        btn = QPushButton()
        btn.setFixedSize(26, 26)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        color = self.column_data["color"]
        icon_name = {"left": "chevron-left", "right": "chevron-right", "pencil": "more-vertical"}.get(kind, "chevron-right")
        btn.setIcon(lucide_icon(icon_name, color, 16))
        btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 13px;
            }}
            QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}
            QPushButton:pressed {{ background-color: {styles.COLORS['bg_hover']}; }}
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

        expand_btn = self._column_icon_button("right", t("widgets.column.expand_tooltip"))
        expand_btn.clicked.connect(lambda: self.collapse_toggle_requested.emit(self.column_id))
        layout.addWidget(expand_btn, 0, Qt.AlignHCenter)

        count = self.column_data.get("task_count", 0)
        count_label = QLabel(str(count))
        count_label.setAlignment(Qt.AlignHCenter)
        count_label.setToolTip(t("widgets.column.task_count_tooltip", count=count))
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
        # El interior de la columna (cabecera, área de tareas) se pinta explícitamente con
        # bg_column: una QScrollArea con hijos no deja ver el fondo del contenedor de forma
        # fiable, así que cada zona lleva su propio fondo para que TODA la columna sea del
        # mismo color que su marco. Se reconstruye en cada load_board (reactivo al tema).
        header_widget.setAttribute(Qt.WA_StyledBackground, True)
        header_widget.setStyleSheet(
            f"#ColumnHeaderBar {{ background-color: {styles.COLORS['bg_column']}; "
            f"border-top-left-radius: 16px; border-top-right-radius: 16px; }}"
        )

        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(6, 4, 6, 4)
        header_layout.setSpacing(8)

        # Punto de 8 px del color de la etapa (sustituye al subrayado de color)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color: {self.column_data['color']}; border-radius: 4px;")
        header_layout.addWidget(dot, 0, Qt.AlignVCenter)

        # Nombre de la columna (arrastrable para reordenar o mover a otro tablero)
        self.title_label = DraggableColumnTitle(self.column_data["name"], self)
        self.title_label.setObjectName("ColumnTitle")
        self.title_label.setToolTip(t("widgets.column.title_drag_tooltip"))
        # Fondo explícito: un QLabel sobre un padre con fondo estilado pinta el color de la
        # ventana (caja oscura) si no se le fija; se iguala al de la columna.
        self.title_label.setStyleSheet(f"background-color: {styles.COLORS['bg_column']};")
        header_layout.addWidget(self.title_label)

        # Límite WIP: muestra "n/límite" y avisa en color danger si se supera.
        wip = self.column_data.get("wip_limit")
        if wip:
            count = self.column_data.get("task_count", 0)
            over = count > wip
            self.wip_label = QLabel(f"{count}/{wip}")
            self.wip_label.setToolTip(t("widgets.column.wip_tooltip", count=count, limit=wip))
            color = styles.COLORS["danger"] if over else styles.COLORS["text_muted"]
            weight = "bold" if over else "normal"
            self.wip_label.setStyleSheet(
                f"color: {color}; font-size: 11px; font-weight: {weight}; background: transparent;"
            )
            header_layout.addWidget(self.wip_label)

        header_layout.addStretch()

        # Botón para plegar la columna (triángulo hacia la izquierda, pintado)
        collapse_btn = self._column_icon_button("left", t("widgets.column.collapse_tooltip"))
        collapse_btn.clicked.connect(lambda: self.collapse_toggle_requested.emit(self.column_id))
        header_layout.addWidget(collapse_btn)

        # Botón de edición/opciones de la columna (lápiz pintado)
        self.menu_btn = self._column_icon_button("pencil", t("widgets.column.edit_tooltip"))
        self.menu_btn.clicked.connect(self.show_column_menu)
        header_layout.addWidget(self.menu_btn)

        main_layout.addWidget(header_widget)

        # 2. Área scrollable para las tareas
        scroll_area = QScrollArea()
        scroll_area.setObjectName("TaskListArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"#TaskListArea {{ background-color: {styles.COLORS['bg_column']}; border: none; }}")
        scroll_area.viewport().setStyleSheet(f"background-color: {styles.COLORS['bg_column']};")

        # El contenedor interno que acepta drops
        self.list_area = TaskListArea(self.column_id)
        self.list_area.setAttribute(Qt.WA_StyledBackground, True)
        self.list_area.setStyleSheet(f"background-color: {styles.COLORS['bg_column']};")
        self.list_area.task_dropped.connect(self.task_dropped.emit)

        # Aplicar el estilo dinámico inicial a la columna
        self.set_column_style(dragging=False)

        # Efecto visual al arrastrar sobre esta columna usando su propio color
        self.list_area.drag_entered.connect(lambda: self.set_column_style(dragging=True))
        self.list_area.drag_left.connect(lambda: self.set_column_style(dragging=False))

        scroll_area.setWidget(self.list_area)
        main_layout.addWidget(scroll_area)

        # 3. Botón para añadir una nueva tarea. Fondo bg_column explícito (inline) para que
        # coincida con el interior de la columna: la QSS global por objectName no pinta el
        # fondo de este botón de forma fiable (quedaría transparente sobre el carril).
        self.add_task_btn = QPushButton(t("widgets.column.add_task_btn"))
        self.add_task_btn.setObjectName("AddTaskButton")
        self.add_task_btn.setCursor(Qt.PointingHandCursor)
        self.add_task_btn.setIcon(lucide_icon("plus", styles.COLORS['text_muted'], 16))
        self.add_task_btn.setIconSize(QSize(16, 16))
        self.add_task_btn.setStyleSheet(f"""
            #AddTaskButton {{
                background-color: {styles.COLORS['bg_column']};
                border: none;
                color: {styles.COLORS['text_muted']};
                border-radius: 19px;
                padding: 8px;
                font-weight: 600;
            }}
            #AddTaskButton:hover {{
                background-color: {styles.COLORS['accent_tint']};
                color: {styles.COLORS['accent_pressed']};
            }}
        """)
        self.add_task_btn.clicked.connect(lambda: self.add_task_requested.emit(self.column_id))
        main_layout.addWidget(self.add_task_btn)

    # --- Soltar una tarjeta sobre una columna PLEGADA (solo activo si collapsed) ---
    def dragEnterEvent(self, event):
        if self.collapsed and event.mimeData().hasFormat("application/x-ekin-task-id"):
            event.acceptProposedAction()
            self.set_column_style(dragging=True)
            self._hover_timer.start()
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
            self._hover_timer.stop()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        mime = event.mimeData()
        if self.collapsed and mime.hasFormat("application/x-ekin-task-id"):
            self._hover_timer.stop()
            task_id = int(mime.data("application/x-ekin-task-id").data().decode("utf-8"))
            event.acceptProposedAction()
            self.set_column_style(dragging=False)
            self.collapsed_card_drop.emit(task_id, self.column_id)
        else:
            event.ignore()

    def set_column_style(self, dragging=False):
        """La columna es una tarjeta crema plana (estilo inline: Qt solo pinta el fondo de
        estos QFrame vía stylesheet propio); al arrastrar una tarjeta encima muestra un anillo
        de acento. Se re-aplica en cada load_board, reactivo al conmutador de tema."""
        if dragging:
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: {styles.COLORS['bg_column']};
                    border: 2px solid {styles.COLORS['accent']};
                    border-radius: 28px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #ColumnContainer {{
                    background-color: {styles.COLORS['bg_column']};
                    border: none;
                    border-radius: 28px;
                }}
            """)

    def show_column_menu(self):
        """Muestra el menú contextual de la columna para editarla, moverla, copiarla o borrarla."""
        menu = QMenu(self)
        styles.style_menu(menu)

        edit_action = menu.addAction(t("widgets.column.menu_edit"))
        copy_action = menu.addAction(t("widgets.column.menu_copy"))
        menu.addSeparator()
        delete_action = menu.addAction(t("widgets.column.menu_delete"))

        action = menu.exec(QCursor.pos())
        if action == edit_action:
            self.edit_column_requested.emit(self.column_id)
        elif action == copy_action:
            self.copy_column_requested.emit(self.column_id)
        elif action == delete_action:
            self.delete_column_requested.emit(self.column_id)

    def add_task_card(self, card_widget):
        """Añade una tarjeta de tarea a la columna (no-op si está plegada)."""
        if not hasattr(self, "list_area"):
            return
        self.list_area.list_layout.addWidget(card_widget)
