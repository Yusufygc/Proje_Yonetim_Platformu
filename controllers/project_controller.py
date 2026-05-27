"""
Proje ekranı için PySide6 sinyal/slot köprüsü.
UI katmanı ile servis katmanı arasındaki iletişimi Signal/Slot mekanizmasıyla sağlar.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.exceptions.base_exception import AppBaseException
from domain.models.project import Project
from services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ProjectController(QObject):
    """Proje CRUD işlemlerini sinyal tabanlı olarak yönetir."""

    projects_loaded = Signal(list)
    project_created = Signal(object)
    project_updated = Signal(object)
    project_deleted = Signal(int)
    project_archived = Signal(int)
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

    def load_projects(self, include_archived: bool = False) -> None:
        try:
            projects = self._service.get_all_projects(include_archived=include_archived)
            self.projects_loaded.emit(projects)
        except AppBaseException as exc:
            logger.error("Projeler yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def get_project_sync(self, project_id: int) -> Optional[Project]:
        """Senkron proje sorgulama — yalnızca UI thread'inden küçük veri seti için çağrılır."""
        try:
            return self._service.get_project(project_id)
        except AppBaseException:
            return None

    def create_project(self, title: str, **kwargs: Any) -> None:
        try:
            project = self._service.create_project(title, **kwargs)
            self.project_created.emit(project)
            self._event_bus.publish("project.created", project_id=project.id)
        except AppBaseException as exc:
            logger.error("Proje oluşturulamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def update_project(self, project_id: int, **kwargs: Any) -> None:
        try:
            project = self._service.update_project(project_id, **kwargs)
            self.project_updated.emit(project)
            self._event_bus.publish("project.updated", project_id=project.id)
        except AppBaseException as exc:
            logger.error("Proje güncellenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def archive_project(self, project_id: int) -> None:
        try:
            self._service.archive_project(project_id)
            self.project_archived.emit(project_id)
            self._event_bus.publish("project.archived", project_id=project_id)
        except AppBaseException as exc:
            logger.error("Proje arşivlenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def delete_project(self, project_id: int) -> None:
        try:
            self._service.delete_project(project_id)
            self.project_deleted.emit(project_id)
            self._event_bus.publish("project.deleted", project_id=project_id)
        except AppBaseException as exc:
            logger.error("Proje silinemedi: %s", exc)
            self.error_occurred.emit(str(exc))
