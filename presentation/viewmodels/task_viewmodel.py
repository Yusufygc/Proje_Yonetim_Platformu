"""QML Görevler (WBS) Görünümü için ViewModel Köprüsü."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication

from domain.models.task import Task
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.qt_properties import variant_list_property
from presentation.viewmodels.task_clipboard import collect_task_copy_lines
from presentation.viewmodels.task_list_model import TaskListModel

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

class TaskViewModel(QObject):
    """Görevler (WBS) modülünün QML kullanıcı arayüzü ile iş katmanı arasındaki köprüsü."""

    selectedProjectChanged = Signal(int)
    selectedTaskChanged = Signal()
    projectsChanged = Signal()
    statsChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._task_controller = container.task_controller
        self._project_controller = container.project_controller
        self._event_bus = container.event_bus

        self._task_model = TaskListModel(parent=self)
        self._projects: list[dict[str, Any]] = []
        self._selected_project_id: int = 0
        self._selected_task_id: int = 0

        self._tasks_cache: list[Task] = []
        self._connect_signals()
        self._subscribe_events()
        self.loadProjects()

    def _connect_signals(self) -> None:
        forward_errors_to_toast(self._event_bus, self._task_controller)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)
        self._task_controller.task_created.connect(self._on_task_modified)
        self._task_controller.task_updated.connect(self._on_task_modified)
        self._task_controller.task_deleted.connect(self._on_task_deleted)
        self._project_controller.projects_loaded.connect(self._on_projects_loaded)

    def _subscribe_events(self) -> None:
        self._event_bus.subscribe("task.created", self._on_bus_task_changed)
        self._event_bus.subscribe("task.updated", self._on_bus_task_changed)
        self._event_bus.subscribe("task.deleted", self._on_bus_task_changed)
        self._event_bus.subscribe("project.created", self._on_bus_project_changed)
        self._event_bus.subscribe("project.deleted", self._on_bus_project_changed)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(QObject, constant=True)
    def taskModel(self) -> TaskListModel:
        return self._task_model

    @variant_list_property(notify=projectsChanged)
    def projects(self) -> list[dict[str, Any]]:
        return self._projects

    @Property(int, notify=selectedProjectChanged)
    def selectedProjectId(self) -> int:
        return self._selected_project_id

    @Property(int, notify=selectedTaskChanged)
    def selectedTaskId(self) -> int:
        return self._selected_task_id

    @Property(int, notify=statsChanged)
    def totalTasks(self) -> int:
        return len(self._tasks_cache)

    @Property(int, notify=statsChanged)
    def completedTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "DONE")

    @Property(int, notify=statsChanged)
    def inProgressTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "IN_PROGRESS")

    @Property(int, notify=statsChanged)
    def blockedTasks(self) -> int:
        return sum(1 for t in self._tasks_cache if t.status == "BLOCKED")

    # ── Controller & Event Callbacks ────────────────────────────────────────

    def _on_projects_loaded(self, projects: list[Any]) -> None:
        self._projects = [{"id": p.id, "title": p.title} for p in projects]
        self.projectsChanged.emit()

        if self._projects and self._selected_project_id == 0:
            self.selectProject(self._projects[0]["id"])
        elif not self._projects:
            self._selected_project_id = 0
            self.selectedProjectChanged.emit(0)
            self._tasks_cache = []
            self._task_model.set_tasks([])
            self.statsChanged.emit()

    def _on_tasks_loaded(self, project_id: int, tasks: list[Task]) -> None:
        if project_id != self._selected_project_id:
            return
        self._tasks_cache = list(tasks)
        self._task_model.set_tasks(tasks)
        self.statsChanged.emit()
        self._refresh_selected_task()

    def _on_task_modified(self, task: Any) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_task_deleted(self, task_id: int) -> None:
        if self._selected_task_id == task_id:
            self._selected_task_id = 0
            self._refresh_selected_task()
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_bus_task_changed(self, **kwargs: Any) -> None:
        if self._selected_project_id:
            self._task_controller.load_tasks(self._selected_project_id)

    def _on_bus_project_changed(self, **kwargs: Any) -> None:
        self.loadProjects()

    # ── Diğer ViewModel'ler için tipli erişim (QML kullanmaz) ───────────────

    def current_project_id(self) -> int:
        return self._selected_project_id

    def cached_tasks(self) -> list[Task]:
        return self._tasks_cache

    # ── Public Slots ────────────────────────────────────────────────────────

    @Slot()
    def loadProjects(self) -> None:
        self._project_controller.load_projects()

    @Slot(int)
    def selectProject(self, project_id: int) -> None:
        if self._selected_project_id == project_id:
            return
        self._selected_project_id = project_id
        self._task_model.clear_overrides()
        self.selectedProjectChanged.emit(project_id)
        if project_id != 0:
            self._task_controller.load_tasks(project_id)

    @Slot(int)
    def selectTask(self, task_id: int) -> None:
        self._selected_task_id = task_id
        self._refresh_selected_task()

    def _refresh_selected_task(self) -> None:
        self.selectedTaskChanged.emit()

    @Slot(int)
    def toggleTaskStatus(self, task_id: int) -> None:
        self._task_controller.toggle_status(task_id)

    @Slot(int, int)
    def toggleChecklistItem(self, item_id: int, task_id: int) -> None:
        self._task_controller.toggle_checklist_item(item_id, task_id)

    @Slot(int, str)
    def addChecklistItem(self, task_id: int, text: str) -> None:
        if text.strip():
            self._task_controller.add_checklist_item(task_id, text.strip())

    @Slot(int, int)
    def deleteChecklistItem(self, item_id: int, task_id: int) -> None:
        self._task_controller.delete_checklist_item(item_id, task_id)

    @Slot(str)
    def quickAddTask(self, title: str) -> None:
        t = title.strip()
        if not t or self._selected_project_id == 0:
            return
        parent_id = self._selected_task_id if self._selected_task_id != 0 else None
        created = self._task_controller.create_task(
            self._selected_project_id,
            t,
            parent_task_id=parent_id,
        )
        if created is not None:
            self._event_bus.publish("toast.show", message="Görev oluşturuldu", type_="success")  # l10n: data

    @Slot(int)
    def deleteTask(self, task_id: int) -> None:
        self._task_controller.delete_task(task_id)
        self._event_bus.publish("toast.show", message="Görev silindi", type_="info")  # l10n: data

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._task_model.setSearchQuery(query)

    @Slot(str)
    def setStatusFilter(self, status: str) -> None:
        self._task_model.setStatusFilter(status)

    @Slot(str)
    def setPriorityFilter(self, priority: str) -> None:
        self._task_model.setPriorityFilter(priority)

    @Slot(str)
    def setTypeFilter(self, task_type: str) -> None:
        self._task_model.setTypeFilter(task_type)

    # ── Kopyalama ve Çoğaltma İşlemleri ────────────────────────────────────

    @Slot(int)
    def copyTaskToClipboard(self, task_id: int) -> None:
        """Belirtilen görevi ve alt görevlerini metin (WBS) formatında panoya kopyalar."""
        t = next((x for x in self._tasks_cache if x.id == task_id), None)
        if not t:
            return

        lines = collect_task_copy_lines(self._tasks_cache, task_id)
        if lines:
            text = "\n".join(lines)
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)
            self._event_bus.publish(
                "toast.show",
                message="Görev panoya kopyalandı",  # l10n: data
                type_="success",
            )

    @Slot(int)
    def duplicateTask(self, task_id: int) -> None:
        """Görevi aynı proje ve üst görev altına yeni bir kopya olarak çoğaltır."""
        t = next((x for x in self._tasks_cache if x.id == task_id), None)
        if not t:
            return

        new_title = f"{t.title} (Kopya)"  # l10n: data
        created = self._task_controller.create_task(
            t.project_id,
            new_title,
            parent_task_id=t.parent_task_id,
            description=t.description or "",
            status="TODO",
            priority=t.priority,
            task_type=t.task_type,
        )
        if created and t.checklist_items:
            for item in t.checklist_items:
                if item.text.strip():
                    self._task_controller.add_checklist_item(created.id, item.text.strip())

        self._event_bus.publish(
            "toast.show",
            message="Görev çoğaltıldı",  # l10n: data
            type_="success",
        )

