"""QML Küresel Arama ViewModel'i (SearchViewModel)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from core.events.app_events import PROJECT_DETAIL_REQUESTED
from presentation.utils.i18n import tr
from presentation.viewmodels.qt_properties import variant_list_property
from presentation.viewmodels.navigation_bridge import NavigationBridge

if TYPE_CHECKING:
    from app.di_container import DIContainer

logger = logging.getLogger(__name__)

_TYPE_META = {
    "project": {"key": "type_project", "default": "Proje", "icon": "folder", "color": "#6366F1"},
    "task": {"key": "type_task", "default": "Görev", "icon": "check-square", "color": "#10B981"},  # l10n: data
    "idea": {"key": "type_idea", "default": "Fikir", "icon": "lightbulb", "color": "#F59E0B"},
}


class SearchViewModel(QObject):
    """Küresel tam metin arama köprüsü."""

    resultsChanged = Signal()
    queryChanged = Signal()

    def __init__(
        self,
        container: DIContainer,
        nav_bridge: NavigationBridge,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._controller = container.search_controller
        self._event_bus = container.event_bus
        self._nav_bridge = nav_bridge

        self._query: str = ""
        self._results: list[dict[str, Any]] = []
        self._is_searching: bool = False

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._controller.search_completed.connect(self._on_search_completed)
        self._controller.error_occurred.connect(self._on_error)

    # ── Slots ──────────────────────────────────────────────────────────────

    @Slot(str)
    def search(self, query: str) -> None:
        self._query = query
        self.queryChanged.emit()
        cleaned = query.strip()
        if len(cleaned) < 2:
            self._results.clear()
            self._is_searching = False
            self.resultsChanged.emit()
            return

        self._is_searching = True
        self.resultsChanged.emit()
        self._controller.perform_search(cleaned)

    @Slot()
    def clear(self) -> None:
        self._query = ""
        self._results.clear()
        self._is_searching = False
        self.queryChanged.emit()
        self.resultsChanged.emit()

    @Slot(str, int)
    def selectItem(self, type_str: str, item_id: int) -> None:
        self._nav_bridge.closeSearch()
        if type_str == "project":
            self._nav_bridge.navigateTo("projects")
            if self._event_bus:
                self._event_bus.publish(PROJECT_DETAIL_REQUESTED, project_id=item_id)
        elif type_str == "task":
            self._nav_bridge.navigateTo("tasks")
        elif type_str == "idea":
            self._nav_bridge.navigateTo("ideas")

    def _on_search_completed(self, raw_results: dict[str, list[dict[str, Any]]]) -> None:
        self._is_searching = False
        items: list[dict[str, Any]] = []

        for category, type_code in [("projects", "project"), ("tasks", "task"), ("ideas", "idea")]:
            meta = _TYPE_META.get(type_code, {"key": type_code, "default": type_code, "icon": "file", "color": "#6B7280"})
            for r in raw_results.get(category, []):
                items.append({
                    "id": r["id"],
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "type": type_code,
                    "typeLabel": tr(meta["key"], meta["default"]),
                    "icon": meta["icon"],
                    "color": meta["color"],
                })

        self._results = items
        self.resultsChanged.emit()

    def _on_error(self, message: str) -> None:
        self._is_searching = False
        self.resultsChanged.emit()
        if self._event_bus:
            self._event_bus.publish("toast.show", message=message, type_="error")

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(str, notify=queryChanged)
    def query(self) -> str:
        return self._query

    @variant_list_property(notify=resultsChanged)
    def results(self) -> list[dict[str, Any]]:
        return self._results

    @Property(int, notify=resultsChanged)
    def count(self) -> int:
        return len(self._results)

    @Property(bool, notify=resultsChanged)
    def isSearching(self) -> bool:
        return self._is_searching
