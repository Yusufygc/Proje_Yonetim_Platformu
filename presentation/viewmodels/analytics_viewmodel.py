"""QML Analitik Görünümü için ViewModel Köprüsü (AnalyticsViewModel)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from domain.models.project import Project
from presentation.utils.i18n import tr
from presentation.viewmodels.qt_properties import variant_list_property, variant_map_property

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

_PRIORITY_META = {
    "CRITICAL": {"key": "priority_critical", "default": "Kritik", "color": "#EF4444"},
    "HIGH": {"key": "priority_high", "default": "Yüksek", "color": "#F97316"},  # l10n: data
    "MEDIUM": {"key": "priority_medium", "default": "Orta", "color": "#3B82F6"},
    "LOW": {"key": "priority_low", "default": "Düşük", "color": "#10B981"},  # l10n: data
}

# Durum dağılımı halkasının sırası ve renkleri (grafik veri renkleri tema-bağımsızdır).
_STATUS_META = [
    ("TODO", "task_status_todo", "Yapılacak", "#8B5CF6"),  # l10n: data
    ("IN_PROGRESS", "task_status_in_progress", "Devam Ediyor", "#3B82F6"),  # l10n: data
    ("WAITING", "task_status_waiting", "Beklemede", "#F59E0B"),  # l10n: data
    ("BLOCKED", "task_status_blocked", "Engellendi", "#EF4444"),  # l10n: data
    ("DONE", "task_status_done", "Tamamlandı", "#10B981"),  # l10n: data
    ("CANCELLED", "task_status_cancelled", "İptal", "#6B7280"),  # l10n: data
]


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
        self._flow_series: list[dict[str, Any]] = []
        self._status_dist: list[dict[str, Any]] = []
        self._heatmap: dict[str, Any] = {"cells": [], "max": 0}
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
        self._flow_series = [
            {"label": str(f[0]), "created": int(f[1]), "completed": int(f[2])} for f in data.get("flow_series", [])
        ]
        self._status_dist = self._format_status_dist(data.get("status_distribution", {}))
        self._heatmap = data.get("heatmap", {"cells": [], "max": 0})
        self.dataChanged.emit()

    @staticmethod
    def _format_status_dist(raw: dict[str, int]) -> list[dict[str, Any]]:
        return [
            {"key": key, "label": tr(label_key, default), "value": int(raw.get(key, 0)), "color": color}
            for key, label_key, default, color in _STATUS_META
        ]

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

    @variant_map_property(notify=dataChanged)
    def kpis(self) -> dict[str, Any]:
        """Kart değerleri tek haritada: QML yalnızca `kpis.<ad>` okur."""
        k = self._kpis
        return {
            "totalCompleted": int(k.get("total_completed", 0)),
            "completionRate": float(k.get("completion_rate", 0.0)),
            "streakDays": int(k.get("streak_days", 0)),
            "avgCompletionDays": float(k.get("avg_completion_days", 0.0)),
            "bestPeriodLabel": str(k.get("best_period_label", "—")),
            "bestPeriodCount": int(k.get("best_period_count", 0)),
        }

    @variant_list_property(notify=dataChanged)
    def timeSeries(self) -> list[dict[str, Any]]:
        return self._time_series

    @variant_list_property(notify=dataChanged)
    def priorityDistribution(self) -> list[dict[str, Any]]:
        return self._priority_dist

    @variant_list_property(notify=dataChanged)
    def projectDistribution(self) -> list[dict[str, Any]]:
        return self._project_dist

    @variant_list_property(notify=dataChanged)
    def flowSeries(self) -> list[dict[str, Any]]:
        return self._flow_series

    @variant_list_property(notify=dataChanged)
    def statusDistribution(self) -> list[dict[str, Any]]:
        return self._status_dist

    @variant_map_property(notify=dataChanged)
    def heatmap(self) -> dict[str, Any]:
        return self._heatmap
