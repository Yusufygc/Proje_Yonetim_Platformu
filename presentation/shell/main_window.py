"""
Ana uygulama penceresi — sidebar + içerik alanı iskeletini kurar.
Koyu arka plan, köşe yumuşatma ve drop shadow ile premium his verilir.
"""
from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

import config
from core.managers.preference_manager import PreferenceManager
from core.managers.theme_manager import ThemeManager
from di_container import DIContainer
from presentation.pages.dashboard_page import DashboardPage
from presentation.pages.ideas_page import IdeasPage
from presentation.pages.projects_page import ProjectsPage
from presentation.pages.settings_page import SettingsPage
from presentation.pages.tasks_page import TasksPage
from presentation.shell.sidebar import Sidebar

from presentation.dialogs.search_dialog import SearchDialog

logger = logging.getLogger(__name__)

# Sayfa adı → QStackedWidget index eşlemesi
PAGE_INDEX: dict[str, int] = {
    "dashboard": 0,
    "projects": 1,
    "ideas": 2,
    "tasks": 3,
    "settings": 4,
}


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

        self._setup_window()
        self._setup_ui()
        self._setup_shortcuts()
        self._restore_geometry()
        self._navigate_to("dashboard")

    def _setup_window(self) -> None:
        self.setWindowTitle(config.APP_NAME)
        self.setMinimumSize(1024, 680)
        self.resize(1280, 800)
        self.setStyleSheet(self._theme.build_global_qss())

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

        # Sağ panel: Sayfalar
        self._stack = QStackedWidget(parent=central)
        _container = DIContainer.instance()
        self._stack.addWidget(
            DashboardPage(
                parent=self._stack,
                controller=_container.dashboard_controller
            )
        )   # 0
        self._projects_page = ProjectsPage(
            parent=self._stack,
            di_container=_container
        )
        self._stack.addWidget(self._projects_page)
        self._stack.addWidget(                                     # 2
            IdeasPage(
                parent=self._stack,
                idea_controller=_container.idea_controller,
                project_controller=_container.project_controller,
            )
        )
        self._stack.addWidget(                                     # 3
            TasksPage(
                parent=self._stack,
                controller=_container.task_controller,
                project_controller=_container.project_controller,
            )
        )
        self._stack.addWidget(
            SettingsPage(
                parent=self._stack,
                controller=_container.settings_controller
            )
        )   # 4
        root_layout.addWidget(self._stack)

    def _navigate_to(self, page_name: str) -> None:
        """Sidebar navigasyon sinyalini alarak ilgili sayfayı gösterir."""
        index = PAGE_INDEX.get(page_name, 0)
        self._stack.setCurrentIndex(index)
        self._sidebar.set_active_page(page_name)
        logger.debug("Sayfa değiştirildi: %s (index=%d)", page_name, index)

    def _setup_shortcuts(self) -> None:
        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self._open_search_dialog)

    def _open_search_dialog(self) -> None:
        dialog = SearchDialog(controller=self._di.search_controller, parent=self)
        dialog.item_selected.connect(self._on_search_item_selected)
        dialog.exec()

    def _on_search_item_selected(self, type_str: str, item_id: int) -> None:
        if type_str == "Proje":
            self._navigate_to("projects")
            # Proje detayını açmak için projeler sayfasına ID göndermeliyiz
            # Fakat şu an projects_page'e direct erişimimiz self._projects_page üzerinden var:
            self._projects_page._on_item_clicked(item_id)
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
