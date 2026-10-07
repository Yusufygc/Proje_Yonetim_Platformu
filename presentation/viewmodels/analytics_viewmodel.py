"""QML Analitik Görünümü için ViewModel Köprüsü (AnalyticsViewModel)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from domain.models.project import Project
from presentation.utils.i18n import tr
from presentation.viewmodels.qt_properties import variant_list_property

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

_PRIORITY_META = {
    "CRITICAL": {"key": "priority_critical", "default": "Kritik", "color": "#EF4444"},
    "HIGH": {"key": "priority_high", "default": "Yüksek", "color": "#F97316"},  # l10n: data
    "MEDIUM": {"key": "priority_medium", "default": "Orta", "color": "#3B82F6"},
    "LOW": {"key": "priority_low", "default": "Düşük", "color": "#10B981"},  # l10n: data
}


class AnalyticsViewModel(QObject):
    """Görev tamamlama analitiği ve KPI istatistik köprüsü."""

    dataChanged = Signal()
    projectsChanged = Signal()
    periodChanged = Signal()
    selectedProjectChanged = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._analytics_ctrl = container.analytics_controller
        self._project_ctrl = container.project_controller

        self._period: str = "weekly"
        self._project_id: int = 0  # 0: all projects
        self._is_loading: bool = False

        self._kpis: dict[str, Any] = {}
        self._time_series: list[dict[str, Any]] = []
        self._priority_dist: list[dict[str, Any]] = []
        self._project_dist: list[dict[str, Any]] = []
        self._projects_list: list[dict[str, Any]] = []

        self._connect_signals()
        self._project_ctrl.load_projects()
        self.refresh()

    def _connect_signals(self) -> None:
        self._analytics_ctrl.analytics_loaded.connect(self._on_analytics_loaded)
        self._project_ctrl.projects_loaded.connect(self._on_projects_loaded)

    @Slot()
    def refresh(self) -> None:
        self._is_loading = True
        self.dataChanged.emit()
        pid = None if self._project_id == 0 else self._project_id
        self._analytics_ctrl.load_analytics(self._period, pid)

    @Slot(str)
    def setPeriod(self, period: str) -> None:
        if self._period != period:
            self._period = period
            self.periodChanged.emit()
            self.refresh()

    @Slot(int)
    def setProjectId(self, project_id: int) -> None:
        if self._project_id != project_id:
            self._project_id = project_id
            self.selectedProjectChanged.emit()
            self.refresh()

    def _on_projects_loaded(self, projects: list[Project]) -> None:
        items = [{"id": 0, "title": tr("analytics_all_projects", "Tüm Projeler")}]
        for p in projects:
            items.append({"id": p.id, "title": p.title})
        self._projects_list = items
        self.projectsChanged.emit()

    def _on_analytics_loaded(self, data: dict[str, Any]) -> None:
        self._is_loading = False
        self._kpis = data.get("kpis", {})
        raw_ts = data.get("time_series", [])
        self._time_series = [{"label": str(t[0]), "value": int(t[1])} for t in raw_ts]
        self._priority_dist = self._format_priority_dist(data.get("priority_distribution", {}))
        raw_proj = data.get("project_distribution", [])
        self._project_dist = [{"title": str(p[0]), "count": int(p[1])} for p in raw_proj]
        self.dataChanged.emit()

    def _format_priority_dist(self, raw: dict[str, int]) -> list[dict[str, Any]]:
        result = []
        for key in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            val = int(raw.get(key, 0))
            meta = _PRIORITY_META.get(key, {"key": key, "default": key, "color": "#6B7280"})
            result.append({
                "key": key,
                "label": tr(meta["key"], meta["default"]),
                "value": val,
                "color": meta["color"],
            })
        return result

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(str, notify=periodChanged)
    def period(self) -> str:
        return self._period

    @Property(int, notify=selectedProjectChanged)
    def projectId(self) -> int:
        return self._project_id

    @Property(bool, notify=dataChanged)
    def isLoading(self) -> bool:
        return self._is_loading

    @variant_list_property(notify=projectsChanged)
    def projects(self) -> list[dict[str, Any]]:
        return self._projects_list

    @Property(int, notify=dataChanged)
    def totalCompleted(self) -> int:
        return int(self._kpis.get("total_completed", 0))

    @Property(float, notify=dataChanged)
    def completionRate(self) -> float:
        return float(self._kpis.get("completion_rate", 0.0))

    @Property(int, notify=dataChanged)
    def streakDays(self) -> int:
        return int(self._kpis.get("streak_days", 0))

    @Property(float, notify=dataChanged)
    def onTimeRate(self) -> float:
        return float(self._kpis.get("on_time_rate", 0.0))

    @Property(str, notify=dataChanged)
    def bestPeriodLabel(self) -> str:
        return str(self._kpis.get("best_period_label", "—"))

    @Property(int, notify=dataChanged)
    def bestPeriodCount(self) -> int:
        return int(self._kpis.get("best_period_count", 0))

    @variant_list_property(notify=dataChanged)
    def timeSeries(self) -> list[dict[str, Any]]:
        return self._time_series

    @variant_list_property(notify=dataChanged)
    def priorityDistribution(self) -> list[dict[str, Any]]:
        return self._priority_dist

    @variant_list_property(notify=dataChanged)
    def projectDistribution(self) -> list[dict[str, Any]]:
        return self._project_dist
