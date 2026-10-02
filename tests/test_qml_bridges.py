"""QML Köprüleri (Theme, I18n, Navigation, Project, Dashboard) Birim Testleri."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    _python_base = Path(sys.executable).parent
    _qt_dll_dirs = [
        _python_base / "Library" / "bin",
        _python_base / "Library" / "lib" / "qt6" / "bin",
        _python_base / "Library" / "plugins",
    ]
    for _d in _qt_dll_dirs:
        if _d.exists():
            os.environ["PATH"] = str(_d) + os.pathsep + os.environ.get("PATH", "")
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(str(_d))
                except OSError:
                    pass

import pytest
from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app.di_container import DIContainer
from domain.models.project import Project
from infrastructure.database.db_manager import DatabaseManager
from presentation.modules import setup_modules
from presentation.viewmodels.dashboard_viewmodel import DashboardViewModel
from presentation.viewmodels.i18n_bridge import I18nBridge
from presentation.viewmodels.icon_provider import IconImageProvider
from presentation.viewmodels.navigation_bridge import NavigationBridge
from presentation.viewmodels.project_list_model import ProjectListModel
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.viewmodels.theme_bridge import ThemeBridge


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app  # type: ignore[return-value]


@pytest.fixture
def container(tmp_path: Path) -> DIContainer:
    DatabaseManager._instance = None
    DIContainer._instance = None
    db_file = tmp_path / "test_qml.db"
    db = DatabaseManager.instance(f"sqlite:///{db_file}")
    db.create_all_tables()
    c = DIContainer.instance()
    c.bootstrap()
    return c


def test_theme_bridge_properties_and_toggle(qapp: QApplication, container: DIContainer) -> None:
    bridge = ThemeBridge(container.theme, container.prefs, parent=qapp)
    assert bridge.currentTheme in ("dark", "light", "emerald_dark", "indigo_dark")
    assert isinstance(bridge.isDark, bool)
    assert bridge.background.startswith("#")
    assert bridge.surface.startswith("#")

    initial_dark = bridge.isDark
    bridge.toggleTheme()
    assert bridge.isDark != initial_dark
    bridge.toggleTheme()
    assert bridge.isDark == initial_dark


def test_i18n_bridge_translation_and_language_switch(qapp: QApplication, container: DIContainer) -> None:
    bridge = I18nBridge(container.strings, parent=qapp)
    assert bridge.currentLanguage in ("tr", "en")
    translated = bridge.tr("app_name", "Varsayilan")
    assert translated != ""

    bridge.setLanguage("en")
    assert bridge.currentLanguage == "en"
    bridge.setLanguage("tr")
    assert bridge.currentLanguage == "tr"


def test_navigation_bridge_routing_and_sidebar_toggle(qapp: QApplication, container: DIContainer) -> None:
    setup_modules(container)
    bridge = NavigationBridge(container.prefs, container.event_bus, parent=qapp)

    assert bridge.currentPage == "dashboard"
    bridge.navigateTo("projects")
    assert bridge.currentPage == "projects"

    initial_collapsed = bridge.sidebarCollapsed
    bridge.toggleSidebar()
    assert bridge.sidebarCollapsed != initial_collapsed
    bridge.toggleSidebar()
    assert bridge.sidebarCollapsed == initial_collapsed

    assert len(bridge.modules) >= 9
    keys = [m["page_key"] for m in bridge.modules]
    assert "dashboard" in keys
    assert "projects" in keys
    assert "tasks" in keys


def test_navigation_bridge_toast_event_handling(qapp: QApplication, container: DIContainer) -> None:
    bridge = NavigationBridge(container.prefs, container.event_bus, parent=qapp)
    received_toast: list[tuple[str, str, int]] = []

    def _on_toast(msg: str, t_type: str, duration: int) -> None:
        received_toast.append((msg, t_type, duration))

    bridge.toastRequested.connect(_on_toast)
    bridge.showToast("Test bildirim", "success", 2000)

    assert len(received_toast) == 1
    assert received_toast[0][0] == "Test bildirim"
    assert received_toast[0][1] == "success"
    assert received_toast[0][2] == 2000


def test_project_list_model_and_filters(qapp: QApplication) -> None:
    model = ProjectListModel(parent=qapp)
    p1 = Project(id=1, title="Alpha Projesi", short_description="Test aciklama", project_type="Yazilim")
    p2 = Project(id=2, title="Beta Projesi", short_description="Diger proje", project_type="Egitim")
    model.set_projects([p1, p2])

    assert model.rowCount() == 2
    model.setSearchQuery("Alpha")
    assert model.rowCount() == 1
    model.setSearchQuery("")
    assert model.rowCount() == 2

    model.setStatusFilter("COMPLETED")
    assert model.rowCount() == 0
    model.setStatusFilter("ALL")
    assert model.rowCount() == 2


def test_project_viewmodel_crud_and_dialog_state(qapp: QApplication, container: DIContainer) -> None:
    pvm = ProjectViewModel(container, parent=qapp)
    assert not pvm.isDialogOpen

    pvm.openCreateDialog()
    assert pvm.isDialogOpen
    assert pvm.dialogMode == "create"
    pvm.closeDialog()
    assert not pvm.isDialogOpen

    # Proje Kaydetme testi
    test_title = f"Test QML Projesi {os.getpid()}"
    pvm.openCreateDialog()
    pvm.saveProject({
        "title": test_title,
        "description": "Otomatik birim testi aciklamasi",
        "status": "ACTIVE",
        "priority": "HIGH",
    })
    from PySide6.QtCore import QThreadPool
    QThreadPool.globalInstance().waitForDone(2000)

    # Listede mevcut mu kontrol et
    proj = next((p for p in container.project_controller._service.get_all_projects() if p.title == test_title), None)
    assert proj is not None
    pvm.selectProject(proj.id)
    assert pvm.selectedProjectId == proj.id
    assert pvm.selectedProject.get("title") == test_title
    pvm.deleteProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)


def test_dashboard_viewmodel_stats(qapp: QApplication, container: DIContainer) -> None:
    dvm = DashboardViewModel(container.dashboard_controller, parent=qapp)
    assert isinstance(dvm.totalProjects, int)
    assert isinstance(dvm.activeProjects, int)
    assert isinstance(dvm.totalTasks, int)
    assert isinstance(dvm.openTasks, int)
    assert isinstance(dvm.recentTasks, list)


def test_qml_main_window_loads_successfully(qapp: QApplication, container: DIContainer) -> None:
    setup_modules(container)
    engine = QQmlApplicationEngine(parent=qapp)

    icon_provider = IconImageProvider(container.icons)
    engine.addImageProvider("icons", icon_provider)

    tb = ThemeBridge(container.theme, container.prefs, parent=qapp)
    ib = I18nBridge(container.strings, parent=qapp)
    nb = NavigationBridge(container.prefs, container.event_bus, parent=qapp)
    pv = ProjectViewModel(container, parent=qapp)
    dv = DashboardViewModel(container.dashboard_controller, parent=qapp)

    qapp._test_tb = tb  # type: ignore[attr-defined]
    qapp._test_ib = ib  # type: ignore[attr-defined]
    qapp._test_nb = nb  # type: ignore[attr-defined]
    qapp._test_pv = pv  # type: ignore[attr-defined]
    qapp._test_dv = dv  # type: ignore[attr-defined]

    engine.rootContext().setContextProperty("themeBridge", tb)
    engine.rootContext().setContextProperty("i18nBridge", ib)
    engine.rootContext().setContextProperty("navBridge", nb)
    engine.rootContext().setContextProperty("projectViewModel", pv)
    engine.rootContext().setContextProperty("dashboardViewModel", dv)

    qml_file = Path("presentation/qml/main.qml")
    engine.load(str(qml_file))

    assert len(engine.rootObjects()) > 0
