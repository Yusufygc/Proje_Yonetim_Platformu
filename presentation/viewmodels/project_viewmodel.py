"""QML Proje Yönetimi ViewModel'i (ProjectViewModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.di_container import DIContainer
from controllers.project_controller import ProjectController
from controllers.stage_controller import StageController
from core.events.app_events import NEW_PROJECT_REQUESTED, PROJECT_DETAIL_REQUESTED
from core.events.event_bus import EventBus
from domain.models.project import Project
from domain.models.project_stage import ProjectStage
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.project_list_model import ProjectListModel
from presentation.viewmodels.qt_properties import variant_list_property, variant_map_property

logger = logging.getLogger(__name__)


class ProjectViewModel(QObject):
    """QML Projeler ekranı ve detay paneli için iş mantığı ve reaktif state köprüsü."""

    selectedProjectChanged = Signal()
    stagesChanged = Signal()
    tasksChanged = Signal()
    dialogStateChanged = Signal()

    def __init__(
        self,
        di: DIContainer,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller: ProjectController = di.project_controller
        self._stage_controller: StageController = di.stage_controller
        self._task_controller = di.task_controller
        self._event_bus: EventBus = di.event_bus
        self._model = ProjectListModel(parent=self)

        self._selected_project_id: int = 0
        self._selected_project_data: dict[str, Any] = {}
        self._stages_data: list[dict[str, Any]] = []
        self._tasks_data: list[dict[str, Any]] = []

        self._dialog_open: bool = False
        self._dialog_mode: str = "create"  # "create" veya "edit"
        self._dialog_project_id: int = 0

        self._connect_signals()
        self._subscribe_events()
        self.loadProjects()

    def _connect_signals(self) -> None:
        self._controller.projects_loaded.connect(self._on_projects_loaded)
        self._controller.project_created.connect(lambda _p: self.loadProjects())
        self._controller.project_updated.connect(self._on_project_updated)
        self._controller.project_deleted.connect(lambda _id: self.loadProjects())
        # project_controller hatalarını ArchiveViewModel zaten toast'a çeviriyor; çift bildirim olmasın.
        forward_errors_to_toast(self._event_bus, self._stage_controller)
        self._stage_controller.stages_loaded.connect(self._on_stages_loaded)
        self._stage_controller.stage_updated.connect(self._on_stage_updated)
        self._task_controller.tasks_loaded.connect(self._on_tasks_loaded)

    def _subscribe_events(self) -> None:
        self._event_bus.subscribe(NEW_PROJECT_REQUESTED, self._on_new_project_requested)
        self._event_bus.subscribe(PROJECT_DETAIL_REQUESTED, self._on_detail_requested)
        for evt in ("project.archived", "project.restored", "project.deleted"):
            self._event_bus.subscribe(evt, lambda **_kw: self.loadProjects())
        for evt in ("task.created", "task.updated", "task.completed", "task.reopened", "task.deleted", "task.moved"):
            self._event_bus.subscribe(evt, self._on_task_event)

    def _on_new_project_requested(self, **_kw: Any) -> None:
        self.openCreateDialog()

    def _on_detail_requested(self, project_id: int, **_kw: Any) -> None:
        self.selectProject(project_id)

    @Property(QObject, constant=True)
    def model(self) -> ProjectListModel:
        return self._model

    @Property(int, notify=selectedProjectChanged)
    def selectedProjectId(self) -> int:
        return self._selected_project_id

    def current_project_id(self) -> int:
        """Python tarafı için tipli erişim; QML `selectedProjectId` kullanır."""
        return self._selected_project_id

    @variant_map_property(notify=selectedProjectChanged)
    def selectedProject(self) -> dict[str, Any]:
        return self._selected_project_data

    @variant_list_property(notify=stagesChanged)
    def selectedStages(self) -> list[dict[str, Any]]:
        return self._stages_data

    @variant_list_property(notify=tasksChanged)
    def selectedTasks(self) -> list[dict[str, Any]]:
        return self._tasks_data

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._dialog_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._dialog_mode

    @Slot()
    def loadProjects(self) -> None:
        self._controller.load_projects(include_archived=False)

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        self._model.set_projects(projects)
        if projects and self._selected_project_id == 0:
            self.selectProject(projects[0].id)
        elif self._selected_project_id != 0:
            self._refresh_selected_project()

    @Slot(int)
    def selectProject(self, project_id: int) -> None:
        self._selected_project_id = project_id
        self._refresh_selected_project()
        self._stage_controller.load_stages(project_id)
        self._request_tasks()

    def _refresh_selected_project(self) -> None:
        proj = self._controller.get_project_sync(self._selected_project_id) if self._selected_project_id else None
        self._selected_project_data = self._project_to_dict(proj) if proj else {}
        self.selectedProjectChanged.emit()

    def _project_to_dict(self, p: Project) -> dict[str, Any]:
        return {
            "id": p.id,
            "title": p.title,
            "description": p.short_description or "",
            "status": str(getattr(p.status, "value", p.status)),
            "priority": str(getattr(p.priority, "value", p.priority)),
            "health": str(getattr(p.health, "value", p.health)),
            "progress": int(p.progress_percent or 0),
            "project_type": p.project_type or "",
            "target_date": p.completed_at.strftime("%d.%m.%Y") if p.completed_at else "",
            "start_date": p.start_date.strftime("%d.%m.%Y") if p.start_date else "",
            "target_audience": p.target_outcome or "",
            "problem_statement": p.problem_statement or "",
            "github_repo": p.github_url or "",
            "local_path": p.docs_url or "",
            "is_archived": bool(p.is_archived),
        }

    def _on_stages_loaded(self, stages: list[ProjectStage]) -> None:
        self._stages_data = [
            {"id": s.id, "name": s.name, "status": str(getattr(s.status, "value", s.status)),
             "order_index": s.order_index, "color": s.color or "#6366F1"}
            for s in stages
        ]
        self.stagesChanged.emit()

    def _reload_current_stages(self) -> None:
        if self._selected_project_id != 0:
            self._stage_controller.load_stages(self._selected_project_id)

    def _on_stage_updated(self, _stage: Any = None) -> None:
        self._reload_current_stages()
        self._refresh_selected_project()
        self.loadProjects()

    def _on_task_event(self, **_kw: Any) -> None:
        if self._selected_project_id != 0:
            self._request_tasks()
            self._refresh_selected_project()
        self.loadProjects()

    def _request_tasks(self) -> None:
        if self._selected_project_id == 0:
            self._on_tasks_loaded(0, [])
            return
        self._task_controller.load_tasks(self._selected_project_id)

    def _on_tasks_loaded(self, project_id: int, tasks: list[Any]) -> None:
        if project_id != self._selected_project_id:
            return
        self._tasks_data = [
            {
                "id": t.id,
                "title": t.title,
                "status": str(getattr(t.status, "value", t.status)),
                "priority": str(getattr(t.priority, "value", t.priority)),
                "is_done": str(getattr(t.status, "value", t.status)) == "DONE",
                "parent_id": t.parent_task_id or 0,
                "due_date": t.due_date.strftime("%d.%m.%Y") if t.due_date else "",
            }
            for t in tasks
        ]
        self.tasksChanged.emit()

    @Slot(int)
    def toggleTaskStatus(self, task_id: int) -> None:
        self._task_controller.toggle_status(task_id)

    @Slot(str)
    def addTask(self, title: str) -> None:
        if self._selected_project_id != 0 and title.strip():
            self._task_controller.create_task(self._selected_project_id, title.strip())

    @Slot(int)
    def deleteTask(self, task_id: int) -> None:
        self._task_controller.delete_task(task_id)

    @Slot(int)
    def completeStage(self, stage_id: int) -> None:
        self._stage_controller.complete_stage(stage_id)

    @Slot(int)
    def activateStage(self, stage_id: int) -> None:
        self._stage_controller.activate_stage(stage_id)

    @Slot()
    def openCreateDialog(self) -> None:
        self._dialog_mode, self._dialog_project_id, self._dialog_open = "create", 0, True
        self.dialogStateChanged.emit()

    @Slot(int)
    def openEditDialog(self, project_id: int) -> None:
        self._dialog_mode, self._dialog_project_id, self._dialog_open = "edit", project_id, True
        self.dialogStateChanged.emit()

    @Slot()
    def closeDialog(self) -> None:
        self._dialog_open = False
        self.dialogStateChanged.emit()

    @Slot("QVariantMap")
    def saveProject(self, data: dict[str, Any]) -> None:
        title = data.get("title", "").strip()
        if not title:
            self._event_bus.publish("toast.show", message="Proje başlığı boş olamaz", type_="danger")  # l10n: data
            return

        kwargs = {
            "short_description": data.get("description", ""),
            "status": data.get("status", "PLANNED"),
            "priority": data.get("priority", "MEDIUM"),
            "health": data.get("health", "GOOD"),
            "project_type": data.get("project_type", ""),
            "target_outcome": data.get("target_audience", ""),
            "problem_statement": data.get("problem_statement", ""),
            "github_url": data.get("github_repo", ""),
            "docs_url": data.get("local_path", ""),
        }

        if self._dialog_mode == "edit" and self._dialog_project_id != 0:
            self._controller.update_project(self._dialog_project_id, title=title, **kwargs)
            self._event_bus.publish("toast.show", message="Proje güncellendi", type_="success")  # l10n: data
        else:
            self._controller.create_project(title=title, **kwargs)
            self._event_bus.publish("toast.show", message="Proje oluşturuldu", type_="success")  # l10n: data

        self.closeDialog()
        self.loadProjects()

    @Slot(int)
    def deleteProject(self, project_id: int) -> None:
        self._controller.delete_project(project_id)
        if self._selected_project_id == project_id:
            self._selected_project_id = 0
            self._refresh_selected_project()
        self._event_bus.publish("toast.show", message="Proje silindi", type_="info")  # l10n: data
        self.loadProjects()

    @Slot(int)
    def archiveProject(self, project_id: int) -> None:
        self._controller.archive_project(project_id)
        self._event_bus.publish("toast.show", message="Proje arşivlendi", type_="info")  # l10n: data
        self.loadProjects()

    def _on_project_updated(self, proj: Project) -> None:
        self.loadProjects()
        if self._selected_project_id == proj.id:
            self._refresh_selected_project()
