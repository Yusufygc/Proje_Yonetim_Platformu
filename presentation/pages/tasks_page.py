"""Tasks page with WBS tree, drag/drop moves, and quick child-task add."""
from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)

from controllers.project_controller import ProjectController
from controllers.task_controller import TaskController
from core.managers.string_manager import StringManager
from domain.enums.priority import Priority
from domain.enums.task_status import TaskStatus
from domain.enums.task_type import TaskType
from domain.models.project import Project
from domain.models.task import Task
from presentation.widgets.empty_state import EmptyState
from presentation.widgets.skeleton_loader import SkeletonLoader

_STATUS_THEME_KEYS: dict[str, str] = {
    "TODO": "text_secondary",
    "IN_PROGRESS": "accent_start",
    "WAITING": "warning",
    "BLOCKED": "danger",
    "DONE": "success",
    "CANCELLED": "text_muted",
}


def _tr(key: str, default: str) -> str:
    return StringManager.get(key, default)


class WBSTreeWidget(QTreeWidget):
    """QTreeWidget wrapper that reports internal task moves to the controller."""

    def __init__(self, parent: QWidget, on_task_moved: Callable[[int, int | None, int], None]) -> None:
        super().__init__(parent=parent)
        self._on_task_moved = on_task_moved
        self._drag_task_id: int | None = None

    def startDrag(self, supported_actions: object) -> None:  # type: ignore[override]
        item = self.currentItem()
        self._drag_task_id = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        super().startDrag(supported_actions)  # type: ignore[arg-type]

    def dropEvent(self, event: QDropEvent) -> None:
        dragged_id = self._drag_task_id
        super().dropEvent(event)
        self._drag_task_id = None
        if dragged_id is None:
            return
        moved_item = self._find_item_by_task_id(dragged_id)
        if moved_item is None:
            return
        parent_item = moved_item.parent()
        new_parent_id = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item else None
        new_order = parent_item.indexOfChild(moved_item) if parent_item else self.indexOfTopLevelItem(moved_item)
        self._on_task_moved(dragged_id, new_parent_id, new_order)

    def _find_item_by_task_id(self, task_id: int) -> QTreeWidgetItem | None:
        stack = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        while stack:
            item = stack.pop()
            if item is None:
                continue
            if item.data(0, Qt.ItemDataRole.UserRole) == task_id:
                return item
            stack.extend(item.child(i) for i in range(item.childCount()))
        return None


class TasksPage(QWidget):
    """Hierarchical WBS task tree."""

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
        self._project_controller.load_projects()

    def set_project(self, project_id: int) -> None:
        self._selected_project_id = project_id
        idx = self._project_combo.findData(project_id)
        if idx >= 0:
            self._project_combo.setCurrentIndex(idx)
        self._task_controller.load_tasks(project_id)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        layout.addWidget(self._build_header())

        self._tree = WBSTreeWidget(parent=self, on_task_moved=self._on_task_moved)
        self._tree.setHeaderLabels([
            _tr("task_tree_title", "Görev Başlığı"),
            _tr("task_tree_status", "Durum"),
            _tr("task_tree_priority", "Öncelik"),
            _tr("task_tree_type", "Tip"),
        ])
        self._tree.setColumnWidth(0, 400)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.setDragEnabled(True)
        self._tree.setAcceptDrops(True)
        self._tree.setDropIndicatorShown(True)
        self._tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._tree.setAlternatingRowColors(True)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree, 1)

        inline_row = QWidget(parent=self)
        inline_layout = QHBoxLayout(inline_row)
        inline_layout.setContentsMargins(0, 0, 0, 0)
        inline_layout.setSpacing(8)
        self._quick_add_edit = QLineEdit(parent=inline_row)
        self._quick_add_edit.setPlaceholderText(_tr("task_quick_add_placeholder", "Seçili görevin altına hızlı görev ekle..."))
        self._quick_add_edit.returnPressed.connect(self._on_quick_add_task)
        inline_layout.addWidget(self._quick_add_edit, 1)
        quick_add_btn = QPushButton(_tr("task_quick_add_button", "Hızlı Ekle"), parent=inline_row)
        quick_add_btn.setProperty("cssClass", "btn-secondary")
        quick_add_btn.clicked.connect(self._on_quick_add_task)
        inline_layout.addWidget(quick_add_btn)
        layout.addWidget(inline_row)

        self._empty_label = QLabel("", parent=self)
        self._empty_label.setProperty("cssClass", "text-secondary")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label, 1)

        self._empty_state = EmptyState(
            title=_tr("tasks_empty_title", "WBS bos"),
            message=_tr("tasks_empty_message", "Ilk ana gorevi ekleyerek WBS olusturun."),
            action_label=_tr("task_add_root_plain", "Ana Gorev Ekle"),
            action=self._on_add_root_task,
            parent=self,
        )
        self._empty_state.hide()
        layout.addWidget(self._empty_state, 1)

        self._skeleton = SkeletonLoader(parent=self)
        layout.addWidget(self._skeleton, 1)
        self._tree_opacity = QGraphicsOpacityEffect(self._tree)
        self._tree.setGraphicsEffect(self._tree_opacity)
        self._tree_fade = QPropertyAnimation(self._tree_opacity, b"opacity", self)
        self._tree_fade.setDuration(150)

    def _build_header(self) -> QWidget:
        header = QWidget(parent=self)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(_tr("tasks_wbs_title", "İş Kırılım Yapısı (WBS)"), parent=header)
        title.setProperty("cssClass", "title-medium")
        layout.addWidget(title)
        layout.addStretch()

        lbl = QLabel(_tr("label_project", "Proje:"), parent=header)
        lbl.setProperty("cssClass", "text-secondary")
        layout.addWidget(lbl)

        self._project_combo = QComboBox(parent=header)
        self._project_combo.setMinimumWidth(200)
        self._project_combo.setMinimumHeight(36)
        self._project_combo.currentIndexChanged.connect(self._on_project_changed)
        layout.addWidget(self._project_combo)

        self._status_filter = self._make_filter_combo(_tr("filter_status", "Durum"), [(s.value, s.value) for s in TaskStatus])
        layout.addWidget(self._status_filter)
        self._priority_filter = self._make_filter_combo(_tr("filter_priority", "Öncelik"), [(p.value, p.value) for p in Priority])
        layout.addWidget(self._priority_filter)
        self._type_filter = self._make_filter_combo(_tr("filter_type", "Tür"), [(t.value, t.value) for t in TaskType])
        layout.addWidget(self._type_filter)
        self._stage_filter = self._make_filter_combo(_tr("filter_stage", "Aşama"), [])
        layout.addWidget(self._stage_filter)

        add_btn = QPushButton(_tr("task_add_root", "+ Ana Görev Ekle"), parent=header)
        add_btn.setProperty("cssClass", "btn-primary")
        add_btn.setMinimumSize(140, 36)
        add_btn.clicked.connect(self._on_add_root_task)
        layout.addWidget(add_btn)

        return header

    def _make_filter_combo(self, label: str, values: list[tuple[str, str]]) -> QComboBox:
        combo = QComboBox(parent=self)
        combo.setMinimumHeight(36)
        combo.setMinimumWidth(110)
        combo.addItem(label, None)
        for text, value in values:
            combo.addItem(text, value)
        combo.currentIndexChanged.connect(lambda _idx: self._render_tree())
        return combo

    def _connect_signals(self) -> None:
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)
        self._task_controller.task_created.connect(self._on_task_changed)
        self._task_controller.task_updated.connect(self._on_task_changed)
        self._task_controller.task_deleted.connect(self._on_task_changed)
        self._task_controller.error_occurred.connect(self._on_error)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._project_combo.blockSignals(True)
        self._project_combo.clear()
        self._all_projects = projects

        if not projects:
            self._project_combo.addItem(_tr("project_not_found", "Proje Bulunamadı"))
            self._tree.hide()
            self._empty_state.hide()
            self._empty_label.setText(_tr("tasks_no_project_empty", "Görüntülenecek proje yok.\nÖnce 'Projeler' sayfasından yeni bir proje oluşturun."))
            self._empty_label.show()
        else:
            for project in projects:
                self._project_combo.addItem(project.title, project.id)
            if self._selected_project_id:
                idx = self._project_combo.findData(self._selected_project_id)
                if idx >= 0:
                    self._project_combo.setCurrentIndex(idx)
            else:
                self._selected_project_id = projects[0].id

        self._project_combo.blockSignals(False)

        if self._selected_project_id:
            self._tree.hide()
            self._empty_label.hide()
            self._empty_state.hide()
            self._skeleton.show()
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_project_changed(self, index: int) -> None:
        project_id = self._project_combo.itemData(index)
        self._selected_project_id = project_id
        if project_id:
            self._task_controller.load_tasks(project_id)
        else:
            self._tree.clear()

    def _on_tasks_loaded(self, tasks: list[Task]) -> None:
        self._skeleton.hide()
        self._tree.clear()
        self._tasks = tasks
        self._reload_stage_filter(tasks)

        if not tasks and self._selected_project_id:
            self._tree.hide()
            self._empty_label.setText(_tr("tasks_empty", "Bu projede henüz görev bulunmuyor.\nYeni Görev Ekle butonuyla WBS oluşturabilirsiniz."))
            self._empty_label.hide()
            self._empty_state.show()
            return

        self._empty_label.hide()
        self._empty_state.hide()
        self._tree.show()
        self._render_tree()

    def _on_task_changed(self, _task_or_id: object) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _render_tree(self) -> None:
        self._tree.clear()
        items_dict: dict[int, QTreeWidgetItem] = {}
        filtered_tasks = self._filtered_tasks()

        for task in filtered_tasks:
            item = QTreeWidgetItem([task.title, task.status, task.priority, task.task_type])
            item.setData(0, Qt.ItemDataRole.UserRole, task.id)
            item.setToolTip(0, task.title)
            if task.description:
                item.setToolTip(1, task.description)
            from core.managers.theme_manager import ThemeManager

            theme_mgr = ThemeManager.instance()
            color_str = theme_mgr.color(_STATUS_THEME_KEYS.get(task.status, "text_secondary"))
            item.setForeground(1, QColor(color_str))
            if task.status == TaskStatus.DONE.value:
                muted_color = QColor(theme_mgr.color("text_muted"))
                item.setForeground(0, muted_color)
                item.setForeground(1, muted_color)
            items_dict[task.id] = item

        root_items: list[QTreeWidgetItem] = []
        for task in filtered_tasks:
            item = items_dict[task.id]
            if task.parent_task_id and task.parent_task_id in items_dict:
                items_dict[task.parent_task_id].addChild(item)
            else:
                root_items.append(item)

        self._tree.addTopLevelItems(root_items)
        self._tree.expandAll()
        self._tree_opacity.setOpacity(0.0)
        self._tree_fade.stop()
        self._tree_fade.setStartValue(0.0)
        self._tree_fade.setEndValue(1.0)
        self._tree_fade.start()

    def _filtered_tasks(self) -> list[Task]:
        status = self._status_filter.currentData()
        priority = self._priority_filter.currentData()
        task_type = self._type_filter.currentData()
        stage_id = self._stage_filter.currentData()
        result = []
        for task in self._tasks:
            if status and task.status != status:
                continue
            if priority and task.priority != priority:
                continue
            if task_type and task.task_type != task_type:
                continue
            if stage_id is not None and task.stage_id != stage_id:
                continue
            result.append(task)
        return result

    def _reload_stage_filter(self, tasks: list[Task]) -> None:
        current = self._stage_filter.currentData()
        self._stage_filter.blockSignals(True)
        self._stage_filter.clear()
        self._stage_filter.addItem(_tr("filter_stage", "Aşama"), None)
        stage_ids = sorted({task.stage_id for task in tasks if task.stage_id is not None})
        for stage_id in stage_ids:
            self._stage_filter.addItem(f"Aşama #{stage_id}", stage_id)
        if current is not None:
            idx = self._stage_filter.findData(current)
            if idx >= 0:
                self._stage_filter.setCurrentIndex(idx)
        self._stage_filter.blockSignals(False)

    def _on_context_menu(self, pos: object) -> None:
        item = self._tree.itemAt(pos)
        menu = QMenu(self)

        if item:
            task_id = item.data(0, Qt.ItemDataRole.UserRole)
            add_sub_action = menu.addAction(_tr("task_add_child", "Alt Görev Ekle"))
            add_sub_action.triggered.connect(lambda: self._on_add_subtask(task_id))
            edit_action = menu.addAction(_tr("action_edit", "Düzenle"))
            edit_action.triggered.connect(lambda: self._on_edit_task(task_id))
            menu.addSeparator()
            delete_action = menu.addAction(_tr("action_delete", "Sil"))
            delete_action.triggered.connect(lambda: self._on_delete_task(task_id))
        else:
            add_root_action = menu.addAction(_tr("task_add_root_plain", "Ana Görev Ekle"))
            add_root_action.triggered.connect(self._on_add_root_task)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _on_add_root_task(self) -> None:
        if not self._selected_project_id:
            QMessageBox.warning(self, _tr("error_title", "Hata"), _tr("select_project_first", "Lütfen önce bir proje seçin."))
            return

        from presentation.dialogs.task_dialog import TaskDialog

        stages = self._project_controller.get_project_stages_sync(self._selected_project_id) if hasattr(self._project_controller, "get_project_stages_sync") else None
        dialog = TaskDialog(parent=self, task=None, stages=stages)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
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

    def _on_quick_add_task(self) -> None:
        if not self._selected_project_id:
            return
        title = self._quick_add_edit.text().strip()
        if not title:
            return
        data: dict[str, object] = {}
        current = self._tree.currentItem()
        if current is not None:
            data["parent_task_id"] = current.data(0, Qt.ItemDataRole.UserRole)
        self._task_controller.create_task(self._selected_project_id, title, **data)
        self._quick_add_edit.clear()

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
        count = self._task_controller.get_descendant_count(task_id)
        message = _tr("task_delete_confirm", "Bu görevi kalıcı olarak silmek istediğinizden emin misiniz?")
        if count:
            message = _tr("task_delete_confirm_with_children", "Bu görev ve altındaki {count} görev silinecek. Emin misiniz?").format(count=count)
        reply = QMessageBox.question(
            self,
            _tr("task_delete_title", "Görevi Sil"),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._task_controller.delete_task(task_id)

    def _on_task_moved(self, task_id: int, new_parent_task_id: int | None, new_order_index: int) -> None:
        self._task_controller.move_task(task_id, new_parent_task_id, new_order_index)

    def _on_error(self, message: str) -> None:
        QMessageBox.warning(self, _tr("error_title", "Hata"), message)
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        task_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._on_edit_task(task_id)
