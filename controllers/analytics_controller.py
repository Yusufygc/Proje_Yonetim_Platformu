"""
AnalyticsController — UI ile AnalyticsService arasındaki sinyal köprüsü.
"""
from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from core.workers.worker import Worker
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

_RELOAD_EVENTS = (
    "task.created",
    "task.updated",
    "task.completed",
    "task.deleted",
)


class AnalyticsController(QObject):
    analytics_loaded = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, service: AnalyticsService, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self._service = service
        self._last_period: str = "weekly"
        self._last_project_id: int | None = None
        if event_bus is not None:
            for event_name in _RELOAD_EVENTS:
                event_bus.subscribe(event_name, self._on_domain_changed)

    def _on_domain_changed(self, **_payload: Any) -> None:
        self.load_analytics(self._last_period, self._last_project_id)

    def load_analytics(self, period: str, project_id: int | None = None) -> None:
        self._last_period = period
        self._last_project_id = project_id

        def _fetch() -> dict[str, Any]:
            return self._service.get_analytics(period, project_id)

        def _on_error(err: str) -> None:
            logger.error("Analitik verisi yüklenirken hata: %s", err)
            self.error_occurred.emit(f"Analitik yüklenemedi: {err}")

        worker = Worker(_fetch)
        worker.signals.result.connect(self.analytics_loaded.emit)
        worker.signals.error.connect(_on_error)
        worker.start()
