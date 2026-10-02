"""QML Proje Yönetimi ViewModel'i (ProjectViewModel)."""
from __future__ import annotations

import logging
import os
import webbrowser
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.di_container import DIContainer
from controllers.project_controller import ProjectController
from controllers.stage_controller import StageController
from core.events.app_events import NEW_PROJECT_REQUESTED, PROJECT_DETAIL_REQUESTED
from core.events.event_bus import EventBus
from domain.models.attachment import Attachment
from domain.models.project import Project
from domain.models.project_stage import ProjectStage
from presentation.viewmodels.project_list_model import ProjectListModel

logger = logging.getLogger(__name__)


class ProjectViewModel(QObject):
    """QML Projeler ekranı ve detay paneli için iş mantığı ve reaktif state köprüsü."""

    selectedProjectChanged = Signal()
    stagesChanged = Signal()
    outputsChanged = Signal()
    decisionsChanged = Signal()
    notesChanged = Signal()
    resourcesChanged = Signal()
    dialogStateChanged = Signal()

    def __init__(
        self,
        di: DIContainer,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._di = di
        self._controller: ProjectController = di.project_controller
        self._stage_controller: StageController = di.stage_controller
        self._decision_controller = di.decision_controller
        self._note_controller = di.note_controller
        self._resource_controller = di.resource_controller
        self._event_bus: EventBus = di.event_bus
        self._model = ProjectListModel(parent=self)

        self._selected_project_id: int = 0
        self._selected_project_data: dict[str, Any] = {}
        self._stages_data: list[dict[str, Any]] = []
        self._outputs_data: list[dict[str, Any]] = []
        self._decisions_data: list[dict[str, Any]] = []
        self._notes_data: list[dict[str, Any]] = []
        self._resources_data: list[dict[str, Any]] = []

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
        self._stage_controller.stages_loaded.connect(self._on_stages_loaded)
        self._stage_controller.stage_updated.connect(lambda _s: self._reload_current_stages())
        self._decision_controller.decisions_loaded.connect(self._on_decisions_loaded)
        self._decision_controller.decision_created.connect(lambda _d: self._reload_project_subitems())
        self._decision_controller.decision_deleted.connect(lambda _d: self._reload_project_subitems())
        self._note_controller.notes_loaded.connect(self._on_notes_loaded)
        self._note_controller.note_created.connect(lambda _n: self._reload_project_subitems())
        self._note_controller.note_deleted.connect(lambda _n: self._reload_project_subitems())
        self._resource_controller.resources_loaded.connect(self._on_resources_loaded)
        self._resource_controller.resource_created.connect(lambda _r: self._reload_project_subitems())
        self._resource_controller.resource_deleted.connect(lambda _r: self._reload_project_subitems())

    def _subscribe_events(self) -> None:
        self._event_bus.subscribe(NEW_PROJECT_REQUESTED, self._on_new_project_requested)
        self._event_bus.subscribe(PROJECT_DETAIL_REQUESTED, self._on_detail_requested)
        for evt in ("project.archived", "project.restored", "project.deleted"):
            self._event_bus.subscribe(evt, lambda **_kw: self.loadProjects())

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

    @Property("QVariantMap", notify=selectedProjectChanged)
    def selectedProject(self) -> dict[str, Any]:
        return self._selected_project_data

    @Property("QVariantList", notify=stagesChanged)
    def selectedStages(self) -> list[dict[str, Any]]:
        return self._stages_data

    @Property("QVariantList", notify=outputsChanged)
    def selectedOutputs(self) -> list[dict[str, Any]]:
        return self._outputs_data

    @Property("QVariantList", notify=decisionsChanged)
    def selectedDecisions(self) -> list[dict[str, Any]]:
        return self._decisions_data

    @Property("QVariantList", notify=notesChanged)
    def selectedNotes(self) -> list[dict[str, Any]]:
        return self._notes_data

    @Property("QVariantList", notify=resourcesChanged)
    def selectedResources(self) -> list[dict[str, Any]]:
        return self._resources_data

    @Property(bool, notify=dialogStateChanged)
    def isDialogOpen(self) -> bool:
        return self._dialog_open

    @Property(str, notify=dialogStateChanged)
    def dialogMode(self) -> str:
        return self._dialog_mode

    @Property(int, notify=dialogStateChanged)
    def dialogProjectId(self) -> int:
        return self._dialog_project_id

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
        self._load_outputs(project_id)
        self._reload_project_subitems()

    def _refresh_selected_project(self) -> None:
        if self._selected_project_id == 0:
            self._selected_project_data = {}
            self.selectedProjectChanged.emit()
            return
        proj = self._controller.get_project_sync(self._selected_project_id)
        if not proj:
            self._selected_project_data = {}
            self.selectedProjectChanged.emit()
            return
        self._selected_project_data = self._project_to_dict(proj)
        self.selectedProjectChanged.emit()

    def _project_to_dict(self, p: Project) -> dict[str, Any]:
        status_val = p.status.value if hasattr(p.status, "value") else str(p.status)
        priority_val = p.priority.value if hasattr(p.priority, "value") else str(p.priority)
        health_val = p.health.value if hasattr(p.health, "value") else str(p.health)
        return {
            "id": p.id,
            "title": p.title,
            "description": p.short_description or "",
            "status": str(status_val),
            "priority": str(priority_val),
            "health": str(health_val),
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
            {
                "id": s.id,
                "name": s.name,
                "status": str(s.status.value if hasattr(s.status, "value") else s.status),
                "order_index": s.order_index,
                "color": s.color or "#6366F1",
            }
            for s in stages
        ]
        self.stagesChanged.emit()

    def _reload_current_stages(self) -> None:
        if self._selected_project_id != 0:
            self._stage_controller.load_stages(self._selected_project_id)

    def _load_outputs(self, project_id: int) -> None:
        outputs = self._controller.get_attachments_sync(project_id)
        self._outputs_data = [
            {"id": o.id, "title": o.file_name, "file_path": o.file_path}
            for o in outputs
        ]
        self.outputsChanged.emit()

    def _reload_project_subitems(self) -> None:
        if self._selected_project_id != 0:
            self._decision_controller.load_project_decisions(self._selected_project_id)
            self._note_controller.load_project_notes(self._selected_project_id)
            self._resource_controller.load_project_resources(self._selected_project_id)

    def _on_decisions_loaded(self, decisions: list[Any]) -> None:
        self._decisions_data = [
            {"id": d.id, "title": d.title, "decision": d.decision, "status": d.status}
            for d in decisions
        ]
        self.decisionsChanged.emit()

    def _on_notes_loaded(self, notes: list[Any]) -> None:
        self._notes_data = [
            {"id": n.id, "title": n.title, "body": n.body, "note_type": getattr(n, "note_type", "GENERAL")}
            for n in notes
        ]
        self.notesChanged.emit()

    def _on_resources_loaded(self, resources: list[Any]) -> None:
        self._resources_data = [
            {"id": r.id, "title": r.title, "url": r.url, "resource_type": r.resource_type}
            for r in resources
        ]
        self.resourcesChanged.emit()

    @Slot(int)
    def completeStage(self, stage_id: int) -> None:
        self._stage_controller.complete_stage(stage_id)

    @Slot(int)
    def activateStage(self, stage_id: int) -> None:
        self._stage_controller.activate_stage(stage_id)

    @Slot(str, str)
    def addOutput(self, title: str, file_path: str) -> None:
        if self._selected_project_id == 0:
            return
        att = Attachment(
            project_id=self._selected_project_id,
            file_name=title,
            file_path=file_path,
        )
        self._controller.create_attachment_sync(att)
        self._load_outputs(self._selected_project_id)
        self._event_bus.publish("toast.show", message="Çıktı başarıyla eklendi", type_="success")  # l10n: data

    @Slot(str, str, str)
    def createDecision(self, title: str, decision: str, status: str = "APPROVED") -> None:
        if self._selected_project_id != 0 and title.strip():
            self._decision_controller.create_decision(
                self._selected_project_id, title.strip(), decision.strip(), status=status
            )

    @Slot(int)
    def deleteDecision(self, decision_id: int) -> None:
        self._decision_controller.delete_decision(decision_id)

    @Slot(str, str)
    def createNote(self, title: str, body: str) -> None:
        if self._selected_project_id != 0 and title.strip():
            self._note_controller.create_note(self._selected_project_id, title.strip(), body)

    @Slot(int)
    def deleteNote(self, note_id: int) -> None:
        self._note_controller.delete_note(note_id)

    @Slot(str, str, str)
    def createResource(self, title: str, url: str, resource_type: str = "DOCUMENT") -> None:
        if self._selected_project_id != 0 and title.strip():
            self._resource_controller.create_resource(
                self._selected_project_id, title.strip(), url.strip(), resource_type=resource_type
            )

    @Slot(int)
    def deleteResource(self, resource_id: int) -> None:
        self._resource_controller.delete_resource(resource_id)

    @Slot(str)
    def openUrlOrPath(self, target: str) -> None:
        if not target:
            return
        if target.startswith("http://") or target.startswith("https://"):
            webbrowser.open(target)
            return
        if os.path.exists(target):
            os.startfile(target)  # type: ignore[attr-defined]

    @Slot()
    def openCreateDialog(self) -> None:
        self._dialog_mode = "create"
        self._dialog_project_id = 0
        self._dialog_open = True
        self.dialogStateChanged.emit()

    @Slot(int)
    def openEditDialog(self, project_id: int) -> None:
        self._dialog_mode = "edit"
        self._dialog_project_id = project_id
        self._dialog_open = True
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
