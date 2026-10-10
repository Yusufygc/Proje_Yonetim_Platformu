"""
Proje ekranı için PySide6 sinyal/slot köprüsü.
UI katmanı ile servis katmanı arasındaki iletişimi Signal/Slot mekanizmasıyla sağlar.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.exceptions.base_exception import AppBaseException
from core.workers.worker import Worker
from domain.dtos.forms import ProjectCreateDTO, ProjectUpdateDTO
from domain.models.attachment import Attachment
from domain.models.project import Project
from services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ProjectController(QObject):
    """Proje CRUD işlemlerini sinyal tabanlı olarak yönetir."""

    projects_loaded = Signal(list)
    archived_projects_loaded = Signal(list)
    project_created = Signal(object)
    project_updated = Signal(object)
    project_deleted = Signal(int)
    project_archived = Signal(int)
    project_restored = Signal(int)
    activity_loaded = Signal(int, list)  # (project_id, logs) — stale sonuçları ayırt etmek için
    attachments_loaded = Signal(int, list)  # (project_id, attachments)
    attachment_created = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        service: ProjectService,
        event_bus: EventBus,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._service = service
        self._event_bus = event_bus

    def load_projects(
        self,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> None:
        def _fetch() -> list[Project]:
            return self._service.get_all_projects(
                include_archived=include_archived,
                limit=limit,
                offset=offset,
            )
            
        def _on_error(err: str) -> None:
            logger.error("Projeler yüklenemedi: %s", err)
            self.error_occurred.emit(str(err))
            
        worker = Worker(_fetch)
        worker.signals.result.connect(self.projects_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def load_archived_projects(self) -> None:
        def _fetch() -> list[Project]:
            if hasattr(self._service, "get_archived_projects"):
                return self._service.get_archived_projects()
            return [p for p in self._service.get_all_projects(include_archived=True) if p.is_archived]

        def _on_error(err: str) -> None:
            logger.error("Arşivlenen projeler yüklenemedi: %s", err)
            self.error_occurred.emit(str(err))

        worker = Worker(_fetch)
        worker.signals.result.connect(self.archived_projects_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def get_project_sync(self, project_id: int) -> Optional[Project]:
        """Senkron proje sorgulama — yalnızca UI thread'inden küçük veri seti için çağrılır."""
        try:
            return self._service.get_project(project_id)
        except AppBaseException:
            return None

    def load_activity_logs(self, project_id: int) -> None:
        self._run_in_background(
            lambda: self._service.get_activity_logs(project_id),
            lambda logs: self.activity_loaded.emit(project_id, logs),
            "Etkinlik geçmişi yüklenemedi",
        )

    def load_attachments(self, project_id: int) -> None:
        self._run_in_background(
            lambda: self._service.get_attachments(project_id),
            lambda items: self.attachments_loaded.emit(project_id, items),
            "Ekler yüklenemedi",
        )

    def create_attachment(self, attachment: Attachment) -> None:
        def _create() -> Attachment:
            self._service.create_attachment(attachment)
            return attachment

        self._run_in_background(_create, self.attachment_created.emit, "Çıktı eklenemedi")

    def _run_in_background(self, fetch: Callable[[], Any], on_result: Callable[[Any], None], error_prefix: str) -> None:
        def _on_error(err: str) -> None:
            logger.error("%s: %s", error_prefix, err)
            self.error_occurred.emit(f"{error_prefix}.")

        worker = Worker(fetch)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(_on_error)
        worker.start()

    def create_project(self, title: str, **kwargs: Any) -> None:
        try:
            dto = ProjectCreateDTO(title=title, values=kwargs)
            project = self._service.create_project(dto.title, **dto.values)
            self.project_created.emit(project)
            self._event_bus.publish("project.created", project_id=project.id, project=project)
        except (AppBaseException, ValueError) as exc:
            logger.error("Proje oluşturulamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def update_project(self, project_id: int, **kwargs: Any) -> None:
        try:
            dto = ProjectUpdateDTO(values=kwargs)
            project = self._service.update_project(project_id, **dto.values)
            self.project_updated.emit(project)
            self._event_bus.publish("project.updated", project_id=project.id, project=project)
        except (AppBaseException, ValueError) as exc:
            logger.error("Proje güncellenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def archive_project(self, project_id: int) -> None:
        try:
            self._service.archive_project(project_id)
            self.project_archived.emit(project_id)
            self._event_bus.publish("project.archived", project_id=project_id)
            self._event_bus.publish(
                "toast.show",
                message="Proje arsivlendi.",
                type_="info",
                undo_label="Geri Al",
                undo_callback=lambda: self.restore_archived_project(project_id),
            )
        except AppBaseException as exc:
            logger.error("Proje arşivlenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def restore_archived_project(self, project_id: int) -> None:
        try:
            self._service.restore_archived_project(project_id)
            self.project_restored.emit(project_id)
            self._event_bus.publish("project.restored", project_id=project_id)
            self.load_projects()
        except AppBaseException as exc:
            logger.error("Proje arsivden geri alinamadi: %s", exc)
            self.error_occurred.emit(str(exc))

    def reorder(self, ordered_ids: list[int]) -> None:
        try:
            self._service.reorder(ordered_ids)
            self._event_bus.publish("project.reordered", ordered_ids=ordered_ids)
        except Exception as exc:
            logger.error("Projeler yeniden siralanamadi: %s", exc)
            self.error_occurred.emit("Projeler sıralanırken hata oluştu.")

    def delete_project(self, project_id: int) -> None:
        try:
            self._service.delete_project(project_id)
            self.project_deleted.emit(project_id)
            self._event_bus.publish("project.deleted", project_id=project_id)
        except AppBaseException as exc:
            logger.error("Proje silinemedi: %s", exc)
            self.error_occurred.emit(str(exc))
