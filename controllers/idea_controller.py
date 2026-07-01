"""Signal based controller for idea pool actions."""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.workers.worker import Worker
from domain.dtos.forms import IdeaCreateDTO, IdeaUpdateDTO
from domain.models.idea import Idea
from services.idea_service import IdeaService

logger = logging.getLogger(__name__)


class IdeaController(QObject):
    """Coordinates idea service calls and UI signals."""

    ideas_loaded = Signal(list)
    idea_created = Signal(object)
    idea_updated = Signal(object)
    idea_deleted = Signal(int)
    idea_converted = Signal(int, int)
    error_occurred = Signal(str)

    def __init__(self, service: IdeaService, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self._service = service
        self._event_bus = event_bus or EventBus.instance()

    def load_ideas(self, include_converted: bool = False) -> None:
        def _fetch() -> list[Idea]:
            return self._service.get_all_ideas(include_converted)

        def _on_error(err: str) -> None:
            logger.error("Ideas could not be loaded: %s", err)
            self.error_occurred.emit(str(err))

        worker = Worker(_fetch)
        worker.signals.result.connect(self.ideas_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def create_idea(self, title: str, **kwargs: Any) -> None:
        try:
            dto = IdeaCreateDTO(title=title, values=kwargs)
            idea = self._service.create_idea(dto.title, **dto.values)
            self.idea_created.emit(idea)
            self._event_bus.publish("idea.created", idea_id=idea.id, idea=idea)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Idea could not be created: %s", exc)
            self.error_occurred.emit("Fikir olusturulurken beklenmeyen bir hata olustu.")

    def update_idea(self, idea_id: int, **kwargs: Any) -> None:
        try:
            dto = IdeaUpdateDTO(values=kwargs)
            idea = self._service.update_idea(idea_id, **dto.values)
            self.idea_updated.emit(idea)
            self._event_bus.publish("idea.updated", idea_id=idea.id, idea=idea)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Idea could not be updated: %s", exc)
            self.error_occurred.emit("Fikir guncellenirken beklenmeyen bir hata olustu.")

    def delete_idea(self, idea_id: int) -> None:
        try:
            self._service.delete_idea(idea_id)
            self.idea_deleted.emit(idea_id)
            self._event_bus.publish("idea.deleted", idea_id=idea_id)
        except Exception as exc:
            logger.error("Idea could not be deleted: %s", exc)
            self.error_occurred.emit("Fikir silinirken hata olustu.")

    def convert_to_project(self, idea_id: int, **project_overrides: Any) -> None:
        try:
            project_id = self._service.convert_idea_to_project(idea_id, project_overrides or None)
            self.idea_converted.emit(idea_id, project_id)
            self._event_bus.publish("idea.converted", idea_id=idea_id, project_id=project_id)
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Idea could not be converted: %s", exc)
            self.error_occurred.emit("Fikir projeye donusturulurken hata olustu.")

    def get_idea_sync(self, idea_id: int) -> Idea | None:
        return self._service.get_idea(idea_id)

    def reorder(self, ordered_ids: list[int]) -> None:
        try:
            self._service.reorder(ordered_ids)
            self._event_bus.publish("idea.reordered", ordered_ids=ordered_ids)
        except Exception as exc:
            logger.error("Ideas could not be reordered: %s", exc)
            self.error_occurred.emit("Fikirler sıralanırken hata oluştu.")
