"""Görevler sayfası: WBS ağacı, filtre çubuğu ve görev CRUD akışlarının kompozisyonu."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from controllers.project_controller import ProjectController
from controllers.task_controller import TaskController
from core.managers.theme_manager import ThemeManager
from domain.models.project import Project
from domain.models.task import Task
from presentation.dimensions import Spacing
from presentation.pages.tasks.filter_bar import TaskFilterBar
from presentation.pages.tasks.wbs_tree import WBSTreeWidget
from presentation.utils.i18n import tr
from presentation.widgets.empty_state import EmptyState
from presentation.widgets.skeleton_loader import SkeletonLoader


class TasksPage(QWidget):
    """Hiyerarşik WBS görev ağacı sayfası."""

    # Uygulama oturumu boyunca son seçilen proje hatırlanır
    _last_selected_project_id: int | None = None

    def __init__(
        self,
        parent: QWidget,
        controller: TaskController,
        project_controller: ProjectController,
        theme: ThemeManager | None = None,
        embedded: bool = False,
    ) -> None:
        super().__init__(parent=parent)
        self._task_controller = controller
        self._project_controller = project_controller
        # Constructor injection tercih edilir; None ise singleton'a düşülür.
        self._theme = theme or ThemeManager.instance()
        # Gömülü mod: ProjectDetailPanel içinde kullanılır. Class var'ı kirletmez.
        self._embedded = embedded
        self._selected_project_id: Optional[int] = (
            None if embedded else TasksPage._last_selected_project_id
        )
        self._all_projects: list[Project] = []
        self._tasks: list[Task] = []
        self._setup_ui()
        self._connect_signals()
        self._project_controller.load_projects()

    def set_project(self, project_id: int) -> None:
        self._selected_project_id = project_id
        self._filter_bar.select_project(project_id)
        self._task_controller.load_tasks(project_id)

    # ── UI kurulumu ──────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.LG)

        self._filter_bar = TaskFilterBar(parent=self, embedded=self._embedded)
        layout.addWidget(self._filter_bar)

        self._tree = WBSTreeWidget(parent=self, theme=self._theme)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._tree, 1)

        layout.addWidget(self._build_quick_add_row())

        self._empty_label = QLabel("", parent=self)
        self._empty_label.setProperty("cssClass", "text-secondary")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label, 1)

        self._empty_state = EmptyState(
            title=tr("tasks_empty_title", "WBS bos"),
            message=tr("tasks_empty_message", "Ilk ana gorevi ekleyerek WBS olusturun."),
            action_label=tr("task_add_root_plain", "Ana Gorev Ekle"),
            action=self._on_add_root_task,
            parent=self,
        )
        self._empty_state.hide()
        layout.addWidget(self._empty_state, 1)

        self._skeleton = SkeletonLoader(parent=self, theme=self._theme)
        layout.addWidget(self._skeleton, 1)

    def _build_quick_add_row(self) -> QWidget:
        row = QWidget(parent=self)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(Spacing.MD)
        self._quick_add_edit = QLineEdit(parent=row)
        self._quick_add_edit.setPlaceholderText(
            tr("task_quick_add_placeholder", "Seçili görevin altına hızlı görev ekle...")
        )
        self._quick_add_edit.returnPressed.connect(self._on_quick_add_task)
        row_layout.addWidget(self._quick_add_edit, 1)
        quick_add_btn = QPushButton(tr("task_quick_add_button", "Hızlı Ekle"), parent=row)
        quick_add_btn.setProperty("cssClass", "btn-secondary")
        quick_add_btn.clicked.connect(self._on_quick_add_task)
        row_layout.addWidget(quick_add_btn)
        return row

    def _connect_signals(self) -> None:
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)
        self._task_controller.task_created.connect(self._on_task_changed)
        self._task_controller.task_updated.connect(self._on_task_changed)
        self._task_controller.task_deleted.connect(self._on_task_changed)
        self._task_controller.error_occurred.connect(self._on_error)
        self._filter_bar.project_changed.connect(self._on_project_changed)
        self._filter_bar.filters_changed.connect(self._render_tree)
        self._filter_bar.add_root_requested.connect(self._on_add_root_task)
        self._tree.task_moved.connect(self._on_task_moved)
        self._tree.itemChanged.connect(self._on_tree_item_changed)
        # Ağaç item renkleri QSS değil setForeground ile atanır; tema değişince
        # mevcut ağaç yeni paletle yeniden çizilmek zorundadır.
        self._theme.theme_changed.connect(self._on_theme_changed)

    # ── Veri olayları ────────────────────────────────────────────────────────

    def _on_theme_changed(self, _theme_name: str) -> None:
        if self._tasks:
            self._render_tree()

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._all_projects = projects
        self._filter_bar.set_projects(projects, self._selected_project_id)

        if not projects:
            # Önceki oturumdan kalan geçersiz proje ID'si temizlenir;
            # aksi hâlde silinmiş projeye görev ekleme denenebilir.
            self._selected_project_id = None
            if not self._embedded:
                TasksPage._last_selected_project_id = None
            self._tree.hide()
            self._empty_state.hide()
            self._empty_label.setText(
                tr(
                    "tasks_no_project_empty",
                    "Görüntülenecek proje yok.\nÖnce 'Projeler' sayfasından yeni bir proje oluşturun.",
                )
            )
            self._empty_label.show()
        elif not self._selected_project_id:
            self._selected_project_id = projects[0].id
            if not self._embedded:
                TasksPage._last_selected_project_id = self._selected_project_id

        if self._selected_project_id:
            self._tree.hide()
            self._empty_label.hide()
            self._empty_state.hide()
            self._skeleton.show()
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_project_changed(self, project_id: object) -> None:
        self._selected_project_id = project_id if isinstance(project_id, int) else None
        if not self._embedded:
            TasksPage._last_selected_project_id = self._selected_project_id
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)
        else:
            self._tree.clear()

    def _on_tasks_loaded(self, project_id: int, tasks: list[Task]) -> None:
        if project_id != self._selected_project_id:
            return  # stale sonuç — başka örneğin veya önceki seçimin yükü
        self._skeleton.hide()
        self._tree.clear()
        self._tasks = tasks

        if not tasks and self._selected_project_id:
            self._tree.hide()
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
        self._tree.render_tasks(self._filter_bar.apply(self._tasks))

    # ── Kullanıcı eylemleri ──────────────────────────────────────────────────

    def _on_context_menu(self, pos: object) -> None:
        item = self._tree.itemAt(pos)
        menu = QMenu(self)

        if item:
            item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
            if item_type == "checklist":
                task_id = item.data(0, Qt.ItemDataRole.UserRole + 2)
            else:
                task_id = item.data(0, Qt.ItemDataRole.UserRole)
                
            add_sub_action = menu.addAction(tr("task_add_child", "Alt Görev Ekle"))
            add_sub_action.triggered.connect(lambda: self._on_add_subtask(task_id))
            edit_action = menu.addAction(tr("action_edit", "Düzenle"))
            edit_action.triggered.connect(lambda: self._on_edit_task(task_id))
            menu.addSeparator()
            delete_action = menu.addAction(tr("action_delete", "Sil"))
            delete_action.triggered.connect(lambda: self._on_delete_task(task_id))
            menu.addSeparator()
            selected_task_ids = [
                i.data(0, Qt.ItemDataRole.UserRole)
                for i in self._tree.selectedItems()
                if i.data(0, Qt.ItemDataRole.UserRole + 1) == "task"
            ]
            if len(selected_task_ids) > 1:
                copy_label = tr(
                    "action_copy_selected", "Seçilileri Kopyala ({n})"
                ).format(n=len(selected_task_ids))
                copy_action = menu.addAction(copy_label)
                copy_action.triggered.connect(self._tree._copy_selected_to_clipboard)
            else:
                copy_action = menu.addAction(tr("action_copy", "Kopyala"))
                copy_action.triggered.connect(
                    lambda: self._tree.copy_items_to_clipboard({task_id})
                )
        else:
            add_root_action = menu.addAction(tr("task_add_root_plain", "Ana Görev Ekle"))
            add_root_action.triggered.connect(self._on_add_root_task)

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _on_add_root_task(self) -> None:
        if not self._selected_project_id:
            QMessageBox.warning(
                self,
                tr("error_title", "Hata"),
                tr("select_project_first", "Lütfen önce bir proje seçin."),
            )
            return

        from presentation.dialogs.task_dialog import TaskDialog

        dialog = TaskDialog(parent=self, task=None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            checklist_items: list[str] = data.pop("checklist_items", [])  # type: ignore[assignment]
            task = self._task_controller.create_task(self._selected_project_id, title, **data)
            if task and checklist_items:
                for text in checklist_items:
                    self._task_controller.add_checklist_item(task.id, text)

    def _on_add_subtask(self, parent_task_id: int) -> None:
        if not self._selected_project_id:
            return

        from presentation.dialogs.task_dialog import TaskDialog

        dialog = TaskDialog(parent=self, task=None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            title = str(data.pop("title"))
            checklist_items: list[str] = data.pop("checklist_items", [])  # type: ignore[assignment]
            data["parent_task_id"] = parent_task_id
            task = self._task_controller.create_task(self._selected_project_id, title, **data)
            if task and checklist_items:
                for text in checklist_items:
                    self._task_controller.add_checklist_item(task.id, text)

    def _on_quick_add_task(self) -> None:
        if not self._selected_project_id:
            return
        title = self._quick_add_edit.text().strip()
        if not title:
            return
        data: dict[str, object] = {}
        current = self._tree.currentItem()
        if current is not None:
            item_type = current.data(0, Qt.ItemDataRole.UserRole + 1)
            if item_type == "checklist":
                data["parent_task_id"] = current.data(0, Qt.ItemDataRole.UserRole + 2)
            else:
                data["parent_task_id"] = current.data(0, Qt.ItemDataRole.UserRole)
        data.update(self._filter_bar.filter_values())

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
        message = tr("task_delete_confirm", "Bu görevi kalıcı olarak silmek istediğinizden emin misiniz?")
        if count:
            message = tr(
                "task_delete_confirm_with_children",
                "Bu görev ve altındaki {count} görev silinecek. Emin misiniz?",
            ).format(count=count)
        reply = QMessageBox.question(
            self,
            tr("task_delete_title", "Görevi Sil"),
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._task_controller.delete_task(task_id)

    def _on_task_moved(self, task_id: int, new_parent_task_id: object, new_order_index: int) -> None:
        self._task_controller.move_task(
            task_id,
            new_parent_task_id if isinstance(new_parent_task_id, int) else None,
            new_order_index,
        )

    def _on_error(self, message: str) -> None:
        QMessageBox.warning(self, tr("error_title", "Hata"), message)
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == "checklist":
            task_id = item.data(0, Qt.ItemDataRole.UserRole + 2)
        else:
            task_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._on_edit_task(task_id)

    def _on_tree_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 0:
            return
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        if item_type == "checklist":
            parent_task_id = item.data(0, Qt.ItemDataRole.UserRole + 2)
            self._task_controller.toggle_checklist_item(item_id, parent_task_id)
        elif item_type == "task":
            self._task_controller.toggle_status(item_id)
