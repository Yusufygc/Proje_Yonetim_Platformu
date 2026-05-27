"""
Görevler sayfası — WBS ağaç görünümü.
QTreeWidget ile hiyerarşik görev ağacı oluşturur.
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.project_controller import ProjectController
from controllers.task_controller import TaskController
from domain.models.project import Project
from domain.models.task import Task

_STATUS_COLOR: dict[str, str] = {
    "TODO": "#4A4D5C",
    "IN_PROGRESS": "#6366F1",
    "WAITING": "#F59E0B",
    "BLOCKED": "#EF4444",
    "DONE": "#22C55E",
    "CANCELLED": "#6B7280",
}


class TasksPage(QWidget):
    """Hiyerarşik görev ağacını barındıran sayfa."""

    def __init__(
        self,
        parent: QWidget,
        controller: TaskController,
        project_controller: ProjectController,
    ) -> None:
        super().__init__(parent=parent)
        self._task_controller = controller
        self._project_controller = project_controller
        self._selected_project_id: Optional[int] = None
        self._all_projects: list[Project] = []
        self._tasks: list[Task] = []
        self._setup_ui()
        self._connect_signals()
        
        # Load projects to populate the combo box
        self._project_controller.load_projects()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        layout.addWidget(self._build_header())

        self._tree = QTreeWidget(parent=self)
        self._tree.setHeaderLabels(["Görev Başlığı", "Durum", "Öncelik", "Tip"])
        self._tree.setColumnWidth(0, 400)
        self._tree.setStyleSheet(
            "QTreeWidget { background: #161820; border: 1px solid #2A2D38; border-radius: 8px; color: #E8EAF0; font-size: 13px; }"
            "QTreeWidget::item { padding: 4px; }"
            "QHeaderView::section { background: #1E2130; color: #8B8FA8; border: none; padding: 8px; font-weight: bold; }"
        )
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree, 1)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("İş Kırılım Yapısı (WBS)", parent=header)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #E8EAF0;")
        layout.addWidget(title)
        
        layout.addStretch()

        lbl = QLabel("Proje:", parent=header)
        lbl.setStyleSheet("color: #8B8FA8; font-weight: 600;")
        layout.addWidget(lbl)

        self._project_combo = QComboBox(parent=header)
        self._project_combo.setMinimumWidth(200)
        self._project_combo.setMinimumHeight(36)
        self._project_combo.currentIndexChanged.connect(self._on_project_changed)
        layout.addWidget(self._project_combo)

        add_btn = QPushButton("+ Ana Görev Ekle", parent=header)
        add_btn.setObjectName("accent_button")
        add_btn.setMinimumSize(140, 36)
        add_btn.clicked.connect(self._on_add_root_task)
        layout.addWidget(add_btn)

        return header

    def _connect_signals(self) -> None:
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)
        self._task_controller.task_created.connect(self._on_task_changed)
        self._task_controller.task_updated.connect(self._on_task_changed)
        self._task_controller.task_deleted.connect(self._on_task_changed)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._all_projects = projects
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        if not projects:
            self._project_combo.addItem("Proje Bulunamadı", None)
            self._selected_project_id = None
            self._tree.clear()
        else:
            for p in projects:
                self._project_combo.addItem(p.title, p.id)
            if self._selected_project_id is None:
                self._selected_project_id = projects[0].id
                
            idx = self._project_combo.findData(self._selected_project_id)
            if idx >= 0:
                self._project_combo.setCurrentIndex(idx)
            self._task_controller.load_tasks(self._selected_project_id)
        self._project_combo.blockSignals(False)

    def _on_project_changed(self, index: int) -> None:
        project_id = self._project_combo.itemData(index)
        self._selected_project_id = project_id
        if project_id:
            self._task_controller.load_tasks(project_id)
        else:
            self._tree.clear()

    def _on_tasks_loaded(self, tasks: list[Task]) -> None:
        self._tasks = tasks
        self._render_tree()

    def _on_task_changed(self, _task_or_id: object) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _render_tree(self) -> None:
        self._tree.clear()
        if not self._tasks:
            return

        task_dict = {t.id: t for t in self._tasks}
        items_dict: dict[int, QTreeWidgetItem] = {}

        # First pass: create all items
        for t in self._tasks:
            item = QTreeWidgetItem([
                t.title,
                t.status,
                t.priority,
                t.task_type
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, t.id)
            
            # Styling status
            color = _STATUS_COLOR.get(t.status, "#8B8FA8")
            item.setForeground(1, QColor(color))
            
            if t.status == "DONE":
                item.setForeground(0, QColor("#6B7280"))
                item.setForeground(1, QColor("#6B7280"))
            
            items_dict[t.id] = item

        # Second pass: build hierarchy
        root_items = []
        for t in self._tasks:
            item = items_dict[t.id]
            if t.parent_task_id and t.parent_task_id in items_dict:
                parent_item = items_dict[t.parent_task_id]
                parent_item.addChild(item)
            else:
                root_items.append(item)

        self._tree.addTopLevelItems(root_items)
        self._tree.expandAll()

    def _on_context_menu(self, pos: object) -> None:
        item = self._tree.itemAt(pos)
        menu = QMenu(self)
        
        if item:
            task_id = item.data(0, Qt.ItemDataRole.UserRole)
            
            add_sub_action = menu.addAction("Alt Görev Ekle")
            add_sub_action.triggered.connect(lambda: self._on_add_subtask(task_id))
            
            edit_action = menu.addAction("Düzenle")
            edit_action.triggered.connect(lambda: self._on_edit_task(task_id))
            
            menu.addSeparator()
            
            delete_action = menu.addAction("Sil")
            delete_action.triggered.connect(lambda: self._on_delete_task(task_id))
        else:
            add_root_action = menu.addAction("Ana Görev Ekle")
            add_root_action.triggered.connect(self._on_add_root_task)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _on_add_root_task(self) -> None:
        if not self._selected_project_id:
            QMessageBox.warning(self, "Hata", "Lütfen önce bir proje seçin.")
            return
        
        from presentation.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(parent=self, task=None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            # parent_task_id = None is implicitly handled if not provided
            self._task_controller.create_task(self._selected_project_id, title, **data)

    def _on_add_subtask(self, parent_task_id: int) -> None:
        if not self._selected_project_id:
            return
            
        from presentation.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(parent=self, task=None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            data["parent_task_id"] = parent_task_id
            self._task_controller.create_task(self._selected_project_id, title, **data)

    def _on_edit_task(self, task_id: int) -> None:
        task = self._task_controller.get_task_sync(task_id)
        if not task:
            return
            
        from presentation.dialogs.task_dialog import TaskDialog
        dialog = TaskDialog(parent=self, task=task, task_controller=self._task_controller)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            self._task_controller.update_task(task_id, **dialog.get_data())
        elif result == 2:
            self._on_delete_task(task_id)

    def _on_delete_task(self, task_id: int) -> None:
        reply = QMessageBox.question(
            self,
            "Görevi Sil",
            "Bu görevi (ve varsa tüm alt görevlerini) kalıcı olarak silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._task_controller.delete_task(task_id)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._on_edit_task(task_id)

