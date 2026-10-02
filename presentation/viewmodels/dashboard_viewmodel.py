"""QML Dashboard Ekranı ViewModel'i (DashboardViewModel)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from controllers.dashboard_controller import DashboardController
from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task

logger = logging.getLogger(__name__)


class DashboardViewModel(QObject):
    """Dashboard istatistikleri ve özet listeleri için QML reaktif köprüsü."""

    statsChanged = Signal()

    def __init__(
        self,
        controller: DashboardController,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._controller = controller
        self._stats: dict[str, Any] = {}
        self._controller.stats_loaded.connect(self._on_stats_loaded)
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._controller.load_stats()

    def _on_stats_loaded(self, stats: dict[str, Any]) -> None:
        self._stats = stats
        self.statsChanged.emit()

    @Property(int, notify=statsChanged)
    def totalProjects(self) -> int:
        return int(self._stats.get("total_projects", 0))

    @Property(int, notify=statsChanged)
    def activeProjects(self) -> int:
        return int(self._stats.get("active_projects", 0))

    @Property(int, notify=statsChanged)
    def completedProjects(self) -> int:
        return int(self._stats.get("completed_projects", 0))

    @Property(int, notify=statsChanged)
    def totalTasks(self) -> int:
        return int(self._stats.get("total_tasks", 0))

    @Property(int, notify=statsChanged)
    def openTasks(self) -> int:
        return int(self._stats.get("open_tasks", 0))

    @Property(int, notify=statsChanged)
    def completedTasks(self) -> int:
        total = self.totalTasks
        opened = self.openTasks
        return max(0, total - opened)

    @Property(int, notify=statsChanged)
    def totalIdeas(self) -> int:
        return int(self._stats.get("total_ideas", 0))

    @Property(int, notify=statsChanged)
    def rawIdeas(self) -> int:
        return int(self._stats.get("raw_ideas", 0))

    @Property(int, notify=statsChanged)
    def blockedCount(self) -> int:
        return int(self._stats.get("blocked_count", 0))

    @Property("QVariantList", notify=statsChanged)
    def recentTasks(self) -> list[dict[str, Any]]:
        raw_list = self._stats.get("recent_tasks", [])
        return [self._task_to_dict(t) for t in raw_list]

    @Property("QVariantList", notify=statsChanged)
    def highPriorityTasks(self) -> list[dict[str, Any]]:
        raw_list = self._stats.get("high_priority_tasks", [])
        return [self._task_to_dict(t) for t in raw_list]

    @Property("QVariantList", notify=statsChanged)
    def recentIdeas(self) -> list[dict[str, Any]]:
        raw_list = self._stats.get("recent_ideas", [])
        return [
            {
                "id": i.id,
                "title": i.title,
                "status": str(i.status.value if hasattr(i.status, "value") else i.status),
                "created_at": i.created_at.strftime("%d.%m.%Y") if i.created_at else "",
            }
            for i in raw_list
            if isinstance(i, Idea)
        ]

    def _task_to_dict(self, t: Any) -> dict[str, Any]:
        if not isinstance(t, Task):
            return {}
        return {
            "id": t.id,
            "title": t.title,
            "status": str(t.status.value if hasattr(t.status, "value") else t.status),
            "priority": str(t.priority.value if hasattr(t.priority, "value") else t.priority),
            "progress": int(t.progress or 0),
        }
