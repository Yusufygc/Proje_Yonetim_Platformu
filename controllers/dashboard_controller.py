"""
DashboardController - UI ile DashboardService arasındaki haberleşmeyi sağlar.
"""
import logging
from typing import Any

from PySide6.QtCore import QObject, Signal

from core.events.event_bus import EventBus
from services.dashboard_service import DashboardService

logger = logging.getLogger(__name__)


class DashboardController(QObject):
    stats_loaded = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, service: DashboardService, event_bus: EventBus | None = None) -> None:
        super().__init__()
        self._service = service
        self._event_bus = event_bus
        if event_bus is not None:
            for event_name in (
                "project.created",
                "project.updated",
                "project.archived",
                "project.restored",
                "task.created",
                "task.updated",
                "task.completed",
                "task.deleted",
                "idea.created",
                "idea.converted",
            ):
                event_bus.subscribe(event_name, self._on_domain_changed)

    def _on_domain_changed(self, **_payload: Any) -> None:
        self.load_stats()

    def load_stats(self) -> None:
        try:
            stats = self._service.get_dashboard_stats()
            self.stats_loaded.emit(stats)
        except Exception as e:
            logger.exception("Dashboard istatistikleri yüklenirken hata: %s", e)
            self.error_occurred.emit(f"Dashboard yüklenemedi: {e}")
