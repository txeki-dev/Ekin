"""board_mixins.py - Mixins modulares para BoardViewWidget.

Separa la gestión de UI de sincronización (OneDrive / archivos compartidos)
y la lógica de selección múltiple de tarjetas.
"""

import os
from PySide6.QtCore import Qt, QSize, QUrl, QTimer
from PySide6.QtWidgets import QDialog, QMessageBox, QMenu, QFileDialog
from PySide6.QtGui import QDesktopServices

import database
import styles
import board_sync
from strings import t
from icons import lucide_icon
from cloud_sync_dialog import CloudSyncInfoDialog
from widgets import TaskCard


class BoardSyncUiMixin:
    """Manejo de la interfaz de sincronización con OneDrive/archivos compartidos para BoardViewWidget."""

    def _on_sync_status_changed(self, sync_info):
        """Actualiza el botón y estado de sincronización con OneDrive/archivo compartido."""
        if sync_info and sync_info.get("sync_path"):
            path = sync_info["sync_path"]
            self.sync_btn.setText(t("sync.synced_badge"))
            last_sync = sync_info.get("last_synced_at") or "-"
            tooltip = f"Synced with:\n{path}\nLast sync: {last_sync}"
            if self.sync_controller.last_sync_summary:
                tooltip += f"\n{self.sync_controller.last_sync_summary}"
            self.sync_btn.setToolTip(tooltip)
            self.sync_btn.setIcon(lucide_icon("cloud", styles.COLORS['accent_2'], 15))
            self.sync_btn.setIconSize(QSize(15, 15))
            self.sync_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLORS['accent_2_tint']};
                    border: none;
                    border-radius: 999px;
                    color: {styles.COLORS['accent_2_ink']};
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}
            """)
        else:
            self.sync_btn.setText(t("sync.link_btn"))
            self.sync_btn.setToolTip(t("sync.link_tooltip"))
            self.sync_btn.setIcon(lucide_icon("cloud", styles.COLORS['text_muted'], 15))
            self.sync_btn.setIconSize(QSize(15, 15))
            self.sync_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {styles.COLORS['border']};
                    border-radius: 999px;
                    color: {styles.COLORS['text_muted']};
                    padding: 6px 14px;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {styles.COLORS['bg_hover']};
                    color: {styles.COLORS['text_main']};
                }}
            """)

    def _update_sync_ui(self, board_id=None):
        """Compatibilidad hacia atrás: actualiza el controlador de sincronización."""
        target_id = board_id if board_id is not None else self.board_id
        if target_id is not None:
            self.sync_controller.set_board(target_id, self.db_path)

    def _setup_file_watcher(self, path):
        """Compatibilidad hacia atrás: delega en sync_controller."""
        self.sync_controller.setup_file_watcher(path)

    def _ensure_watcher_path_active(self):
        """Compatibilidad hacia atrás: delega en sync_controller."""
        self.sync_controller.ensure_watcher_path_active()

    def _run_async_sync(self, user_initiated: bool = False, file_path: str = None):
        """Ejecuta la sincronización en segundo plano delegando en el controlador."""
        self.sync_controller.sync_now(user_initiated=user_initiated, blocking=False, file_path=file_path)

    def _on_sync_finished(self, res, user_initiated: bool = False):
        """Gestiona el diálogo de resultado cuando la sincronización es manual."""
        if res.status == "error":
            if user_initiated:
                QMessageBox.warning(self, t("sync.error_title"), res.message)
        elif user_initiated and res.status != "not_linked":
            QMessageBox.information(
                self, t("sync.success_title"), self.sync_controller.last_sync_summary
            )

    def _trigger_auto_sync_export(self):
        """Exporta cambios locales en segundo plano delegando en el controlador."""
        self.sync_controller.trigger_auto_sync_export()

    def _on_sync_btn_clicked(self):
        """Maneja el clic en el botón de sincronización de la cabecera."""
        if not self.board_id or self.board_id == -1:
            return
        sync_info = database.get_board_sync_info(self.board_id, self.db_path)
        if not sync_info or not sync_info.get("sync_path"):
            menu = QMenu(self)
            styles.style_menu(menu)
            link_act = menu.addAction(t("sync.link_btn"))
            connect_act = menu.addAction(t("sync.menu_open_shared"))

            chosen = menu.exec(self.sync_btn.mapToGlobal(self.sync_btn.rect().bottomLeft()))
            if chosen == link_act:
                self._link_board_new_file()
            elif chosen == connect_act:
                self._connect_shared_board_file()
        else:
            # Menú de opciones del tablero ya vinculado
            menu = QMenu(self)
            styles.style_menu(menu)
            sync_now_act = menu.addAction(t("sync.menu_sync_now"))
            open_loc_act = menu.addAction(t("sync.menu_open_location"))
            menu.addSeparator()
            unlink_act = menu.addAction(t("sync.menu_unlink"))

            chosen = menu.exec(self.sync_btn.mapToGlobal(self.sync_btn.rect().bottomLeft()))
            if chosen == sync_now_act:
                self.sync_current_board_now()
            elif chosen == open_loc_act:
                folder = os.path.dirname(os.path.abspath(sync_info["sync_path"]))
                if os.path.exists(folder):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
            elif chosen == unlink_act:
                reply = QMessageBox.question(
                    self,
                    t("sync.unlink_confirm_title"),
                    t("sync.unlink_confirm_body"),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.sync_controller.unlink_current_board()
                    self.load_board(self.board_id)
                    parent_win = self.window()
                    if hasattr(parent_win, "sidebar"):
                        parent_win.sidebar.reload_boards()

    def _link_board_new_file(self):
        """Crea un nuevo archivo .ekboard compartido para el tablero actual."""
        board_name = self.board_title_label.text().strip().replace(" ", "_")
        info_dlg = CloudSyncInfoDialog(board_name=board_name, parent=self.window())
        if info_dlg.exec() != QDialog.Accepted:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            t("sync.dialog_title_link"),
            f"{board_name}.ekboard",
            t("sync.dialog_filter")
        )
        if file_path:
            res = board_sync.sync_board_with_file(self.board_id, file_path, self.db_path)
            if res.status != "error":
                self.load_board(self.board_id)
                parent_win = self.window()
                if hasattr(parent_win, "sidebar"):
                    parent_win.sidebar.reload_boards(select_board_id=self.board_id)
            else:
                QMessageBox.warning(self, t("sync.error_title"), res.message)

    def _connect_shared_board_file(self):
        """Conecta un archivo .ekboard existente y cambia la vista a dicho tablero."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            t("sync.open_shared_title"),
            "",
            t("sync.dialog_filter")
        )
        if not file_path:
            return

        try:
            board_id, res = board_sync.connect_shared_board_from_file(file_path, self.db_path)
            if res.status != "error":
                self.load_board(board_id)
                parent_win = self.window()
                if hasattr(parent_win, "sidebar"):
                    parent_win.sidebar.reload_boards(select_board_id=board_id)
                board_info = database.get_board(board_id, self.db_path)
                name = board_info["name"] if board_info else ""
                QMessageBox.information(
                    self,
                    t("sync.success_title"),
                    t("sync.open_shared_success", name=name)
                )
            else:
                QMessageBox.warning(self, t("sync.error_title"), res.message)
        except Exception as exc:
            QMessageBox.warning(self, t("sync.error_title"), str(exc))

    def sync_current_board_now(self, blocking: bool = False):
        """Sincroniza el tablero actual inmediatamente y notifica si hubo fusión."""
        if not self.board_id or self.board_id == -1:
            return
        self.sync_controller.sync_now(user_initiated=True, blocking=blocking)


class BoardSelectionMixin:
    """Manejo de selección múltiple de tarjetas para operaciones grupales (p. ej. arrastre en lote)."""

    def _handle_task_ctrl_clicked(self, task_id, column_id):
        """Alterna el estado de selección múltiple de una tarjeta mediante Ctrl+Clic."""
        self._set_last_active_column(column_id)
        if task_id in self.selected_task_ids:
            self.selected_task_ids.remove(task_id)
        else:
            self.selected_task_ids.add(task_id)
        self._update_cards_selection_ui()

    def _update_cards_selection_ui(self):
        """Actualiza el estado visual de selección en todas las tarjetas y la barra inferior."""
        for col_widget in self.column_widgets.values():
            for card in col_widget.findChildren(TaskCard):
                card.set_selected(card.task_id in self.selected_task_ids)

        count = len(self.selected_task_ids)
        if count > 0:
            self.selection_bar.show()
            self.selection_bar_label.setText(t("ai_spec.selection_count", count=count))
        else:
            self.selection_bar.hide()

    def clear_task_selection(self):
        """Deselecciona todas las tareas activas."""
        self.selected_task_ids.clear()
        self._update_cards_selection_ui()

    def get_selected_task_ids_ordered(self) -> list[int]:
        """Devuelve los IDs de las tareas seleccionadas en el orden visual del tablero."""
        if not self.selected_task_ids:
            return []
        ordered = []
        for col_widget in self.column_widgets.values():
            for card in col_widget.findChildren(TaskCard):
                if card.task_id in self.selected_task_ids and card.task_id not in ordered:
                    ordered.append(card.task_id)
        for tid in self.selected_task_ids:
            if tid not in ordered:
                ordered.append(tid)
        return ordered

    def keyPressEvent(self, event):
        """Escape deselecciona tarjetas múltiples."""
        if event.key() == Qt.Key_Escape and self.selected_task_ids:
            self.clear_task_selection()
            event.accept()
            return
        super().keyPressEvent(event)


class BoardMcpUiMixin:
    """Manejo de la interfaz del botón de integración MCP en la cabecera del tablero."""

    def _update_mcp_btn_ui(self):
        """Actualiza el estado visual del botón MCP en la cabecera del tablero."""
        if not hasattr(self, "mcp_btn"):
            return
        if not self.board_id or self.board_id == -1:
            self.mcp_btn.hide()
            return
        self.mcp_btn.show()

        board_info = database.get_board(self.board_id, self.db_path)
        is_mcp_active = bool(board_info and board_info.get("mcp_enabled", 0))

        if is_mcp_active:
            self.mcp_btn.setText(t("mcp.board_btn_active"))
            self.mcp_btn.setToolTip(t("mcp.board_btn_tooltip_active"))
            self.mcp_btn.setIcon(lucide_icon("sparkles", styles.COLORS['accent'], 15))
            self.mcp_btn.setIconSize(QSize(15, 15))
            self.mcp_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {styles.COLORS['accent_tint']};
                    border: none;
                    border-radius: 999px;
                    color: {styles.COLORS['accent_ink']};
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}
            """)
        else:
            self.mcp_btn.setText(t("mcp.board_btn_inactive"))
            self.mcp_btn.setToolTip(t("mcp.board_btn_tooltip_inactive"))
            self.mcp_btn.setIcon(lucide_icon("sparkles", styles.COLORS['text_muted'], 15))
            self.mcp_btn.setIconSize(QSize(15, 15))
            self.mcp_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {styles.COLORS['border']};
                    border-radius: 999px;
                    color: {styles.COLORS['text_muted']};
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background-color: {styles.COLORS['bg_hover']}; }}
            """)

    def _open_mcp_sync_dialog(self):
        """Abre el diálogo modal de configuración MCP para el tablero actual."""
        if not self.board_id or self.board_id == -1:
            return
        from mcp_sync_dialog import McpSyncDialog
        dlg = McpSyncDialog(self.board_id, parent=self.window(), db_path=self.db_path)
        if dlg.exec() == QDialog.Accepted:
            self._update_mcp_btn_ui()

    def _flash_mcp_activity_indicator(self):
        """Muestra un indicador visual temporal en el botón MCP cuando la IA modifica el tablero."""
        if not hasattr(self, "mcp_btn") or not self.mcp_btn.isVisible():
            return

        self.mcp_btn.setText(t("mcp.board_btn_updated"))
        self.mcp_btn.setIcon(lucide_icon("sparkles", "#ffffff", 15))
        self.mcp_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {styles.COLORS['accent']};
                border: none;
                border-radius: 999px;
                color: #ffffff;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 700;
            }}
        """)

        # Revertir al estado estándar tras 1800ms
        QTimer.singleShot(1800, self._update_mcp_btn_ui)


