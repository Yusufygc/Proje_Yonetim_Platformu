"""
Ana uygulama penceresi — sidebar + içerik alanı iskeletini kurar.
Koyu arka plan, köşe yumuşatma ve drop shadow ile premium his verilir.
"""
from __future__ import annotations

import logging

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

import config
from core.events.app_events import NEW_PROJECT_REQUESTED, PROJECT_DETAIL_REQUESTED
from core.events.event_bus import EventBus
from core.managers.preference_manager import PreferenceManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from core.module_registry import ModuleRegistry
from di_container import DIContainer
from presentation.dialogs.search_dialog import SearchDialog
from presentation.shell.sidebar import Sidebar
from presentation.widgets.toast import Toast

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Uygulamanın kök penceresi.
    Sidebar ve QStackedWidget içerik alanından oluşur.
    """

    def __init__(self) -> None:
        super().__init__()
        self._prefs = PreferenceManager.instance()
        self._theme = ThemeManager.instance()
        self._di = DIContainer.instance()
        self._page_index: dict[str, int] = {}

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._restore_geometry()
        self._navigate_to("dashboard")

    def _setup_window(self) -> None:
        self.setWindowTitle(StringManager.get("app_name", config.APP_NAME))
        self.setMinimumSize(1024, 680)
        self.resize(1280, 800)
        self.setStyleSheet(self._theme.build_global_qss())
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str) -> None:
        self.setStyleSheet(self._theme.build_global_qss())

    def resizeEvent(self, event: object) -> None:  # type: ignore[override]
        super().resizeEvent(event)  # type: ignore[arg-type]
        if hasattr(self, "_sidebar"):
            self._sidebar.set_collapsed(self.width() < 980, animate=True)

    def _setup_ui(self) -> None:
        central = QWidget(parent=self)
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sol panel: Sidebar
        self._sidebar = Sidebar(parent=central)
        self._sidebar.page_requested.connect(self._navigate_to)
        self._sidebar.search_requested.connect(self._open_search_dialog)
        root_layout.addWidget(self._sidebar)

        # Sağ panel: Sayfalar — ModuleRegistry'den dinamik yükleme
        self._stack = QStackedWidget(parent=central)
        registry = ModuleRegistry.instance()
        for i, plugin in enumerate(registry.plugins()):
            page = plugin.factory(self._stack)
            self._stack.addWidget(page)
            self._page_index[plugin.page_key] = i
        root_layout.addWidget(self._stack)
        
        # Toast bildirimleri pencerenin üstünde yer alır
        self._toast = Toast(parent=central)

    def _navigate_to(self, page_name: str) -> None:
        """Sidebar navigasyon sinyalini alarak ilgili sayfayı gösterir."""
        index = self._page_index.get(page_name, 0)
        self._stack.setCurrentIndex(index)
        self._sidebar.set_active_page(page_name)
        logger.debug("Sayfa değiştirildi: %s (index=%d)", page_name, index)

    def _setup_shortcuts(self) -> None:
        shortcut_f = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_f.activated.connect(self._open_search_dialog)
        
        shortcut_k = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut_k.activated.connect(self._open_search_dialog)
        
        shortcut_n = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_n.activated.connect(self._create_new_project)

    def _create_new_project(self) -> None:
        self._navigate_to("projects")
        EventBus.instance().publish(NEW_PROJECT_REQUESTED)

    def _open_search_dialog(self) -> None:
        dialog = SearchDialog(controller=self._di.search_controller, parent=self)
        dialog.item_selected.connect(self._on_search_item_selected)
        dialog.exec()

    def _on_search_item_selected(self, type_str: str, item_id: int) -> None:
        if type_str == "Proje":
            self._navigate_to("projects")
            EventBus.instance().publish(PROJECT_DETAIL_REQUESTED, project_id=item_id)
        elif type_str == "Görev":
            self._navigate_to("tasks")
        elif type_str == "Fikir":
            self._navigate_to("ideas")

    def _restore_geometry(self) -> None:
        geometry = self._prefs.load_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)

    def closeEvent(self, event: object) -> None:  # type: ignore[override]
        self._prefs.save_window_geometry(self.saveGeometry())
        logger.info("Uygulama kapatılıyor, geometri kaydedildi.")
        super().closeEvent(event)  # type: ignore[arg-type]
