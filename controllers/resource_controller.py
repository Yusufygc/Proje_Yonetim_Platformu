import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from domain.models.resource import Resource
from services.resource_service import ResourceService

logger = logging.getLogger(__name__)


class ResourceController(QObject):
    """Proje Kaynakları için olay ve sinyal yönetimi."""

    resources_loaded = Signal(list)
    resource_created = Signal(object)
    resource_updated = Signal(object)
    resource_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, service: ResourceService) -> None:
        super().__init__()
        self._service = service

    def load_project_resources(self, project_id: int) -> None:
        try:
            resources = self._service.get_project_resources(project_id)
            self.resources_loaded.emit(resources)
        except Exception as exc:
            logger.error("Kaynaklar yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def create_resource(self, project_id: int, title: str, url: str, **kwargs: Any) -> None:
        try:
            resource = self._service.create_resource(project_id, title, url, **kwargs)
            self.resource_created.emit(resource)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Kaynak oluşturulamadı: %s", exc)
            self.error_occurred.emit("Kaynak oluşturulurken hata oluştu.")

    def update_resource(self, resource_id: int, **kwargs: Any) -> None:
        try:
            resource = self._service.update_resource(resource_id, **kwargs)
            self.resource_updated.emit(resource)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Kaynak güncellenemedi: %s", exc)
            self.error_occurred.emit("Kaynak güncellenirken hata oluştu.")

    def delete_resource(self, resource_id: int) -> None:
        try:
            self._service.delete_resource(resource_id)
            self.resource_deleted.emit(resource_id)
        except Exception as exc:
            logger.error("Kaynak silinemedi: %s", exc)
            self.error_occurred.emit("Kaynak silinirken hata oluştu.")

    def get_resource_sync(self, resource_id: int) -> Optional[Resource]:
        return self._service.get_resource(resource_id)
