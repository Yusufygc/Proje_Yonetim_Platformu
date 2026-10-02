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
from domain.models.idea import Idea
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager
from presentation.modules import setup_modules
from presentation.viewmodels.dashboard_viewmodel import DashboardViewModel
from presentation.viewmodels.i18n_bridge import I18nBridge
from presentation.viewmodels.icon_provider import IconImageProvider
from presentation.viewmodels.idea_list_model import IdeaListModel
from presentation.viewmodels.idea_viewmodel import IdeaViewModel
from presentation.viewmodels.navigation_bridge import NavigationBridge
from presentation.viewmodels.project_list_model import ProjectListModel
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.viewmodels.task_list_model import TaskListModel
from presentation.viewmodels.task_viewmodel import TaskViewModel
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


def test_task_list_model_wbs_hierarchy_and_collapse(qapp: QApplication) -> None:
    model = TaskListModel(parent=qapp)
    t1 = Task(id=1, project_id=1, parent_task_id=None, order_index=0, title="Ana Görev 1", status="TODO", priority="HIGH", task_type="TASK")
    t2 = Task(id=2, project_id=1, parent_task_id=1, order_index=0, title="Alt Görev 1.1", status="IN_PROGRESS", priority="MEDIUM", task_type="TASK")
    t3 = Task(id=3, project_id=1, parent_task_id=2, order_index=0, title="Alt Görev 1.1.1", status="DONE", priority="LOW", task_type="BUG")
    t4 = Task(id=4, project_id=1, parent_task_id=None, order_index=1, title="Ana Görev 2", status="WAITING", priority="CRITICAL", task_type="RESEARCH")
    model.set_tasks([t1, t2, t3, t4])

    assert model.rowCount() == 4
    idx0 = model.index(0, 0)
    idx1 = model.index(1, 0)
    idx2 = model.index(2, 0)
    idx3 = model.index(3, 0)
    assert model.data(idx0, TaskListModel.WbsCodeRole) == "1"
    assert model.data(idx1, TaskListModel.WbsCodeRole) == "1.1"
    assert model.data(idx2, TaskListModel.WbsCodeRole) == "1.1.1"
    assert model.data(idx3, TaskListModel.WbsCodeRole) == "2"

    # Daraltma
    model.toggleExpanded(1)
    assert model.rowCount() == 2

    # Tekrar açma
    model.toggleExpanded(1)
    assert model.rowCount() == 4

    # Filtreleme
    model.setSearchQuery("1.1.1")
    assert model.rowCount() == 3
    model.setSearchQuery("")
    assert model.rowCount() == 4


def test_task_viewmodel_crud_and_dialog_state(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    proj = container.project_controller._service.create_project("Görev Test Projesi")
    tvm = TaskViewModel(container, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)

    tvm.selectProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)

    assert not tvm.isDialogOpen
    tvm.openCreateDialog()
    assert tvm.isDialogOpen
    assert tvm.dialogMode == "create"

    task_title = f"Test Görev {os.getpid()}"
    tvm.saveTask({
        "title": task_title,
        "description": "Görev açıklaması",
        "status": "TODO",
        "priority": "HIGH",
        "task_type": "TASK",
        "checklist_items": ["Adım 1", "Adım 2"],
    })
    QThreadPool.globalInstance().waitForDone(2000)

    tasks = container.task_controller._service.get_tasks(proj.id)
    created_task = next((t for t in tasks if t.title == task_title), None)
    assert created_task is not None
    assert len(created_task.checklist_items) == 2

    tvm.toggleTaskStatus(created_task.id)
    QThreadPool.globalInstance().waitForDone(2000)
    updated_task = container.task_controller._service.get_task(created_task.id)
    assert updated_task is not None
    assert updated_task.status != "TODO"

    chk_id = created_task.checklist_items[0].id
    tvm.toggleChecklistItem(chk_id, created_task.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    tvm.deleteTask(created_task.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert container.task_controller.get_task_sync(created_task.id) is None


def test_idea_list_model_and_filters(qapp: QApplication) -> None:
    model = IdeaListModel(parent=qapp)
    i1 = Idea(id=1, title="Yapay Zeka Asistanı", problem="Zaman kaybı", status="RAW", priority="HIGH")
    i2 = Idea(id=2, title="Mobil Barkod Okuyucu", problem="Stok takibi", status="REVIEWING", priority="MEDIUM")
    model.set_ideas([i1, i2])

    assert model.rowCount() == 2
    model.setSearchQuery("Barkod")
    assert model.rowCount() == 1
    model.setSearchQuery("")
    assert model.rowCount() == 2

    model.setStatusFilter("RAW")
    assert model.rowCount() == 1
    model.setStatusFilter("ALL")
    assert model.rowCount() == 2


def test_idea_viewmodel_crud_and_convert(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    ivm = IdeaViewModel(container, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert not ivm.isDialogOpen
    ivm.openCreateDialog()
    assert ivm.isDialogOpen
    assert ivm.dialogMode == "create"
    ivm.closeDialog()
    assert not ivm.isDialogOpen

    idea_title = f"Test Fikir {os.getpid()}"
    ivm.saveIdea({
        "title": idea_title,
        "problem": "Otomasyon eksikliği",
        "solution": "QML arayüzü",
        "target_user": "Geliştiriciler",
        "status": "RAW",
        "priority": "HIGH",
    })
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    ideas = container.idea_controller._service.get_all_ideas()
    created_idea = next((i for i in ideas if i.title == idea_title), None)
    assert created_idea is not None

    ivm.selectIdea(created_idea.id)
    assert ivm.selectedIdeaId == created_idea.id
    assert ivm.selectedIdea.get("title") == idea_title

    ivm.convertToProject(created_idea.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    converted_idea = container.idea_controller._service.get_idea(created_idea.id)
    assert converted_idea is not None
    assert converted_idea.status == "CONVERTED"
    assert converted_idea.converted_project_id is not None

    ivm.deleteIdea(created_idea.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert container.idea_controller.get_idea_sync(created_idea.id) is None


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
    tv = TaskViewModel(container, parent=qapp)
    iv = IdeaViewModel(container, parent=qapp)

    qapp._test_tb = tb  # type: ignore[attr-defined]
    qapp._test_ib = ib  # type: ignore[attr-defined]
    qapp._test_nb = nb  # type: ignore[attr-defined]
    qapp._test_pv = pv  # type: ignore[attr-defined]
    qapp._test_dv = dv  # type: ignore[attr-defined]
    qapp._test_tv = tv  # type: ignore[attr-defined]
    qapp._test_iv = iv  # type: ignore[attr-defined]

    engine.rootContext().setContextProperty("themeBridge", tb)
    engine.rootContext().setContextProperty("i18nBridge", ib)
    engine.rootContext().setContextProperty("navBridge", nb)
    engine.rootContext().setContextProperty("projectViewModel", pv)
    engine.rootContext().setContextProperty("dashboardViewModel", dv)
    engine.rootContext().setContextProperty("taskViewModel", tv)
    engine.rootContext().setContextProperty("ideaViewModel", iv)

    qml_file = Path("presentation/qml/main.qml")
    engine.load(str(qml_file))

    assert len(engine.rootObjects()) > 0
