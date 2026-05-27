import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from core.exceptions.project_exceptions import AppBaseException
from domain.models.idea import Idea
from services.idea_service import IdeaService

logger = logging.getLogger(__name__)


class IdeaController(QObject):
    """Fikir Havuzu olaylarını (sinyallerini) ve UI isteklerini yönetir."""

    ideas_loaded = Signal(list)
    idea_created = Signal(object)
    idea_updated = Signal(object)
    idea_deleted = Signal(int)
    idea_converted = Signal(int, int) # (idea_id, project_id)
    error_occurred = Signal(str)

    def __init__(self, service: IdeaService) -> None:
        super().__init__()
        self._service = service

    def load_ideas(self, include_converted: bool = False) -> None:
        try:
            ideas = self._service.get_all_ideas(include_converted)
            self.ideas_loaded.emit(ideas)
        except Exception as exc:
            logger.error("Fikirler yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def create_idea(self, title: str, **kwargs: Any) -> None:
        try:
            idea = self._service.create_idea(title, **kwargs)
            self.idea_created.emit(idea)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Fikir oluşturulamadı: %s", exc)
            self.error_occurred.emit("Fikir oluşturulurken beklenmeyen bir hata oluştu.")

    def update_idea(self, idea_id: int, **kwargs: Any) -> None:
        try:
            idea = self._service.update_idea(idea_id, **kwargs)
            self.idea_updated.emit(idea)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Fikir güncellenemedi: %s", exc)
            self.error_occurred.emit("Fikir güncellenirken beklenmeyen bir hata oluştu.")

    def delete_idea(self, idea_id: int) -> None:
        try:
            self._service.delete_idea(idea_id)
            self.idea_deleted.emit(idea_id)
        except Exception as exc:
            logger.error("Fikir silinemedi: %s", exc)
            self.error_occurred.emit("Fikir silinirken hata oluştu.")

    def convert_to_project(self, idea_id: int) -> None:
        try:
            project_id = self._service.convert_idea_to_project(idea_id)
            self.idea_converted.emit(idea_id, project_id)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Fikir projeye dönüştürülemedi: %s", exc)
            self.error_occurred.emit("Fikir projeye dönüştürülürken hata oluştu.")

    def get_idea_sync(self, idea_id: int) -> Optional[Idea]:
        return self._service.get_idea(idea_id)
