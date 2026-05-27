"""
Aşama ekranı için PySide6 sinyal/slot köprüsü.
EventBus üzerinden proje oluşturma olayını dinler ve otomatik varsayılan aşamaları üretir.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.exceptions.base_exception import AppBaseException
from domain.models.project_stage import ProjectStage
from services.stage_service import StageService

logger = logging.getLogger(__name__)


class StageController(QObject):
    """Proje aşaması işlemlerini sinyal tabanlı olarak yönetir."""

    stages_loaded = Signal(list)
    stage_updated = Signal(object)
    error_occurred = Signal(str)

    def __init__(
        self,
        service: StageService,
        event_bus: EventBus,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._service = service
        self._event_bus = event_bus
        # Yeni proje oluşturulunca otomatik varsayılan aşamaları üret
        self._event_bus.subscribe("project.created", self._on_project_created)

    def load_stages(self, project_id: int) -> None:
        try:
            stages = self._service.get_stages(project_id)
            self.stages_loaded.emit(stages)
        except AppBaseException as exc:
            logger.error("Aşamalar yüklenemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def complete_stage(self, stage_id: int) -> None:
        try:
            stage = self._service.complete_stage(stage_id)
            self.stage_updated.emit(stage)
            self._event_bus.publish("stage.completed", stage_id=stage_id)
        except AppBaseException as exc:
            logger.error("Aşama tamamlanamadı: %s", exc)
            self.error_occurred.emit(str(exc))

    def activate_stage(self, stage_id: int) -> None:
        try:
            stage = self._service.activate_stage(stage_id)
            self.stage_updated.emit(stage)
            self._event_bus.publish("stage.activated", stage_id=stage_id)
        except AppBaseException as exc:
            logger.error("Aşama aktif edilemedi: %s", exc)
            self.error_occurred.emit(str(exc))

    def _on_project_created(self, **kwargs: Any) -> None:
        project_id = kwargs.get("project_id")
        if project_id is None:
            return
        try:
            self._service.create_default_stages(project_id)
        except AppBaseException as exc:
            logger.error("Varsayılan aşamalar oluşturulamadı (proje %s): %s", project_id, exc)
