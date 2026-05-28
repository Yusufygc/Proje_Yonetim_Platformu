"""Signal based controller for decision records."""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.workers.worker import Worker
from domain.dtos.forms import DecisionCreateDTO, DecisionUpdateDTO
from domain.models.decision_record import DecisionRecord
from services.decision_service import DecisionService

logger = logging.getLogger(__name__)


class DecisionController(QObject):
    """Coordinates decision service calls and UI signals."""

    decisions_loaded = Signal(list)
    decision_created = Signal(object)
    decision_updated = Signal(object)
    decision_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self, service: DecisionService) -> None:
        super().__init__()
        self._service = service

    def load_project_decisions(self, project_id: int) -> None:
        def _fetch() -> list[DecisionRecord]:
            return self._service.get_project_decisions(project_id)

        def _on_error(err: str) -> None:
            logger.error("Decisions could not be loaded: %s", err)
            self.error_occurred.emit(str(err))

        worker = Worker(_fetch)
        worker.signals.result.connect(self.decisions_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()

    def create_decision(self, project_id: int, title: str, decision: str, **kwargs: Any) -> None:
        try:
            dto = DecisionCreateDTO(
                project_id=project_id,
                title=title,
                decision=decision,
                values=kwargs,
            )
            record = self._service.create_decision(
                dto.project_id,
                dto.title,
                dto.decision,
                **dto.values,
            )
            self.decision_created.emit(record)
            EventBus.instance().publish(
                "decision.created",
                decision_id=record.id,
                project_id=record.project_id,
                decision=record,
            )
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Decision could not be created: %s", exc)
            self.error_occurred.emit("Karar olusturulurken hata olustu.")

    def update_decision(self, decision_id: int, **kwargs: Any) -> None:
        try:
            dto = DecisionUpdateDTO(values=kwargs)
            record = self._service.update_decision(decision_id, **dto.values)
            self.decision_updated.emit(record)
            EventBus.instance().publish(
                "decision.updated",
                decision_id=record.id,
                project_id=record.project_id,
                decision=record,
            )
        except ValueError as exc:
            self.error_occurred.emit(str(exc))
        except Exception as exc:
            logger.error("Decision could not be updated: %s", exc)
            self.error_occurred.emit("Karar guncellenirken hata olustu.")

    def delete_decision(self, decision_id: int) -> None:
        try:
            self._service.delete_decision(decision_id)
            self.decision_deleted.emit(decision_id)
            EventBus.instance().publish("decision.deleted", decision_id=decision_id)
        except Exception as exc:
            logger.error("Decision could not be deleted: %s", exc)
            self.error_occurred.emit("Karar silinirken hata olustu.")

    def get_decision_sync(self, decision_id: int) -> DecisionRecord | None:
        return self._service.get_decision(decision_id)
