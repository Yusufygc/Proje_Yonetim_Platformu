"""QML proje detay paneli alt kayıtları ViewModel'i (karar, not, kaynak, çıktı, etkinlik geçmişi)."""
from __future__ import annotations

import logging
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal, Slot

from app.di_container import DIContainer
from domain.models.attachment import Attachment
from presentation.viewmodels.error_reporting import forward_errors_to_toast
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.viewmodels.qt_properties import variant_list_property

logger = logging.getLogger(__name__)

# QML'in eski sürümü DecisionStatus enum'unda olmayan değerler yazıyordu; gösterimde enum'a çevrilir.
_LEGACY_DECISION_STATUS = {"APPROVED": "ACCEPTED", "PROPOSED": "DRAFT", "REJECTED": "CANCELLED"}
_TASK_EVENTS = ("task.created", "task.updated", "task.completed", "task.reopened", "task.deleted", "task.moved")


class ProjectSubitemsViewModel(QObject):
    """Seçili projenin karar, not, kaynak, çıktı ve etkinlik kayıtlarını QML'e sunar.

    Proje seçimi `ProjectViewModel`'de yaşar; bu sınıf yalnızca seçim değişince alt kayıtları yükler.
    """

    outputsChanged = Signal()
    activityChanged = Signal()
    decisionsChanged = Signal()
    notesChanged = Signal()
    resourcesChanged = Signal()

    def __init__(self, di: DIContainer, project_viewmodel: ProjectViewModel, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._project_vm = project_viewmodel
        self._project_controller = di.project_controller
        self._decision_controller = di.decision_controller
        self._note_controller = di.note_controller
        self._resource_controller = di.resource_controller
        self._event_bus = di.event_bus

        self._project_id: int = 0
        self._outputs: list[dict[str, Any]] = []
        self._activity: list[dict[str, Any]] = []
        self._decisions: list[dict[str, Any]] = []
        self._notes: list[dict[str, Any]] = []
        self._resources: list[dict[str, Any]] = []

        self._connect_signals()
        for event_name in _TASK_EVENTS:
            self._event_bus.subscribe(event_name, self._on_task_event)
        self._on_selection_changed()

    def _connect_signals(self) -> None:
        self._project_vm.selectedProjectChanged.connect(self._on_selection_changed)
        forward_errors_to_toast(
            self._event_bus, self._decision_controller, self._note_controller, self._resource_controller
        )
        self._project_controller.activity_loaded.connect(self._on_activity_loaded)
        self._project_controller.attachments_loaded.connect(self._on_outputs_loaded)
        self._project_controller.attachment_created.connect(lambda _a: self._load_outputs())
        self._decision_controller.decisions_loaded.connect(self._on_decisions_loaded)
        self._note_controller.notes_loaded.connect(self._on_notes_loaded)
        self._resource_controller.resources_loaded.connect(self._on_resources_loaded)
        for signal in (
            self._decision_controller.decision_created,
            self._decision_controller.decision_updated,
            self._decision_controller.decision_deleted,
            self._note_controller.note_created,
            self._note_controller.note_updated,
            self._note_controller.note_deleted,
            self._resource_controller.resource_created,
            self._resource_controller.resource_updated,
            self._resource_controller.resource_deleted,
        ):
            signal.connect(lambda _item: self._reload_all())

    # ── Yükleme ─────────────────────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        new_id = self._project_vm.current_project_id()
        if new_id == self._project_id:
            return
        self._project_id = new_id
        self._reload_all()

    def _on_task_event(self, **_kw: Any) -> None:
        self._load_activity()

    def _reload_all(self) -> None:
        self._load_activity()
        self._load_outputs()
        if self._project_id == 0:
            self._on_decisions_loaded([])
            self._on_notes_loaded([])
            self._on_resources_loaded([])
            return
        self._decision_controller.load_project_decisions(self._project_id)
        self._note_controller.load_project_notes(self._project_id)
        self._resource_controller.load_project_resources(self._project_id)

    def _load_activity(self) -> None:
        if self._project_id == 0:
            self._on_activity_loaded(0, [])
            return
        self._project_controller.load_activity_logs(self._project_id)

    def _load_outputs(self) -> None:
        if self._project_id == 0:
            self._on_outputs_loaded(0, [])
            return
        self._project_controller.load_attachments(self._project_id)

    def _on_activity_loaded(self, project_id: int, logs: list[Any]) -> None:
        if project_id != self._project_id:
            return
        self._activity = [
            {"summary": log.summary, "created_at": log.created_at.strftime("%d.%m.%Y %H:%M")} for log in logs
        ]
        self.activityChanged.emit()

    def _on_outputs_loaded(self, project_id: int, outputs: list[Any]) -> None:
        if project_id != self._project_id:
            return
        self._outputs = [
            {"id": o.id, "title": o.caption or Path(o.file_path).name or o.file_path, "file_path": o.file_path}
            for o in outputs
        ]
        self.outputsChanged.emit()

    def _on_decisions_loaded(self, decisions: list[Any]) -> None:
        self._decisions = [
            {"id": d.id, "title": d.title, "decision": d.decision, "status": _LEGACY_DECISION_STATUS.get(d.status, d.status)}
            for d in decisions
        ]
        self.decisionsChanged.emit()

    def _on_notes_loaded(self, notes: list[Any]) -> None:
        self._notes = [
            {"id": n.id, "title": n.title, "body": n.body, "note_type": getattr(n, "note_type", "GENERAL")}
            for n in notes
        ]
        self.notesChanged.emit()

    def _on_resources_loaded(self, resources: list[Any]) -> None:
        self._resources = [
            {"id": r.id, "title": r.title, "url": r.url, "resource_type": r.resource_type} for r in resources
        ]
        self.resourcesChanged.emit()

    # ── Properties ──────────────────────────────────────────────────────────

    @variant_list_property(notify=outputsChanged)
    def selectedOutputs(self) -> list[dict[str, Any]]:
        return self._outputs

    @variant_list_property(notify=activityChanged)
    def selectedActivity(self) -> list[dict[str, Any]]:
        return self._activity

    @variant_list_property(notify=decisionsChanged)
    def selectedDecisions(self) -> list[dict[str, Any]]:
        return self._decisions

    @variant_list_property(notify=notesChanged)
    def selectedNotes(self) -> list[dict[str, Any]]:
        return self._notes

    @variant_list_property(notify=resourcesChanged)
    def selectedResources(self) -> list[dict[str, Any]]:
        return self._resources

    # ── Slots ───────────────────────────────────────────────────────────────

    @Slot(str, str)
    def addOutput(self, title: str, file_path: str) -> None:
        if self._project_id == 0:
            return
        attachment = Attachment(
            project_id=self._project_id, file_path=file_path, caption=title, attachment_type="OUTPUT"
        )
        self._project_controller.create_attachment(attachment)
        self._event_bus.publish("toast.show", message="Çıktı başarıyla eklendi", type_="success")  # l10n: data

    @Slot(str, str, str)
    def createDecision(self, title: str, decision: str, status: str = "ACCEPTED") -> None:
        if self._project_id != 0 and title.strip():
            self._decision_controller.create_decision(self._project_id, title.strip(), decision.strip(), status=status)

    @Slot(int, str, str, str)
    def updateDecision(self, decision_id: int, title: str, decision: str, status: str) -> None:
        self._decision_controller.update_decision(
            decision_id, title=title.strip(), decision=decision.strip(), status=status
        )

    @Slot(int)
    def deleteDecision(self, decision_id: int) -> None:
        self._decision_controller.delete_decision(decision_id)

    @Slot(str, str)
    def createNote(self, title: str, body: str) -> None:
        if self._project_id != 0 and title.strip():
            self._note_controller.create_note(self._project_id, title.strip(), body)

    @Slot(int, str, str)
    def updateNote(self, note_id: int, title: str, body: str) -> None:
        self._note_controller.update_note(note_id, title=title.strip(), body=body)

    @Slot(int)
    def deleteNote(self, note_id: int) -> None:
        self._note_controller.delete_note(note_id)

    @Slot(str, str, str)
    def createResource(self, title: str, url: str, resource_type: str = "DOCUMENT") -> None:
        if self._project_id != 0 and title.strip():
            self._resource_controller.create_resource(
                self._project_id, title.strip(), url.strip(), resource_type=resource_type
            )

    @Slot(int, str, str, str)
    def updateResource(self, resource_id: int, title: str, url: str, resource_type: str) -> None:
        self._resource_controller.update_resource(
            resource_id, title=title.strip(), url=url.strip(), resource_type=resource_type
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
        if os.path.exists(target) and sys.platform == "win32":
            os.startfile(target)
