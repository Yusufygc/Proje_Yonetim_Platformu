"""QML için Navigasyon, Sayfa Yönetimi ve Bildirim Köprüsü."""
from __future__ import annotations

import logging
from typing import Any, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from core.events.app_events import NEW_PROJECT_REQUESTED
from core.events.event_bus import EventBus
from core.managers.preference_manager import PreferenceManager
from core.module_registry import ModuleRegistry

logger = logging.getLogger(__name__)


class NavigationBridge(QObject):
    """QML ana kabuğu için sayfa geçişleri, sidebar durumu ve bildirimleri yönetir."""

    currentPageChanged = Signal(str)
    sidebarCollapsedChanged = Signal(bool)
    searchModalOpenChanged = Signal(bool)
    toastRequested = Signal(str, str, int)  # message, type, duration_ms

    def __init__(
        self,
        prefs: PreferenceManager,
        event_bus: EventBus,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent=parent)
        self._prefs = prefs
        self._event_bus = event_bus
        self._current_page = "dashboard"
        self._sidebar_collapsed = self._prefs.load_sidebar_collapsed()
        self._search_modal_open = False

        self._event_bus.subscribe("toast.show", self._on_bus_toast)

    def _on_bus_toast(self, data: Any) -> None:
        """EventBus üzerinden gelen toast bildirimini QML sinyaline dönüştürür."""
        if isinstance(data, dict):
            msg = str(data.get("message", ""))
            toast_type = str(data.get("type", "info"))
            duration = int(data.get("duration", 3000))
        else:
            msg = str(data)
            toast_type = "info"
            duration = 3000
        self.toastRequested.emit(msg, toast_type, duration)

    @Property(str, notify=currentPageChanged)
    def currentPage(self) -> str:
        return self._current_page

    @Property(bool, notify=sidebarCollapsedChanged)
    def sidebarCollapsed(self) -> bool:
        return self._sidebar_collapsed

    @Property(bool, notify=searchModalOpenChanged)
    def searchModalOpen(self) -> bool:
        return self._search_modal_open

    @Property("QVariantList", constant=True)
    def modules(self) -> list[dict[str, str]]:
        """Kayıtlı tüm modüllerin navigasyon meta-verilerini döndürür."""
        result: list[dict[str, str]] = []
        for plugin in ModuleRegistry.instance().plugins():
            result.append({
                "page_key": plugin.page_key,
                "label_key": plugin.nav_label_key,
                "default_label": plugin.nav_label_default,
                "icon": plugin.nav_icon,
            })
        return result

    @Slot(str)
    def navigateTo(self, page_name: str) -> None:
        """Aktif sayfayı değiştirir."""
        if self._current_page == page_name:
            return
        self._current_page = page_name
        self.currentPageChanged.emit(page_name)
        logger.debug("QML Sayfa yönlendirildi: %s", page_name)  # l10n: log

    @Slot()
    def toggleSidebar(self) -> None:
        """Sidebar daraltma durumunu tersine çevirir."""
        self.setSidebarCollapsed(not self._sidebar_collapsed)

    @Slot(bool)
    def setSidebarCollapsed(self, collapsed: bool) -> None:
        if self._sidebar_collapsed == collapsed:
            return
        self._sidebar_collapsed = collapsed
        self._prefs.save_sidebar_collapsed(collapsed)
        self.sidebarCollapsedChanged.emit(collapsed)

    @Slot()
    def openSearch(self) -> None:
        self._search_modal_open = True
        self.searchModalOpenChanged.emit(True)

    @Slot()
    def closeSearch(self) -> None:
        self._search_modal_open = False
        self.searchModalOpenChanged.emit(False)

    @Slot()
    def createNewProject(self) -> None:
        """Yeni proje akışını tetikler."""
        self.navigateTo("projects")
        self._event_bus.publish(NEW_PROJECT_REQUESTED)

    @Slot(str, str, int)
    def showToast(self, message: str, toast_type: str = "info", duration_ms: int = 3000) -> None:
        """QML içinden manuel toast tetikleme."""
        self.toastRequested.emit(message, toast_type, duration_ms)
