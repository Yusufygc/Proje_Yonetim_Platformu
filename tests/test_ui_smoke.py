from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("pytestqt")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog

from app import config
from core.managers.font_manager import FontManager
from core.managers.icon_manager import IconManager
from core.managers.string_manager import StringManager
from core.managers.theme_manager import ThemeManager
from domain.enums.task_type import TaskType
from domain.models.project import Project
from domain.models.task import Task
from presentation.pages.tasks import TasksPage
from presentation.shell import main_window as main_window_module
from presentation.shell.main_window import MainWindow


class FakeProjectController(QObject):
    projects_loaded = Signal(list)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.project = Project(id=1, title="UI Proje", slug="ui-proje")

    def load_projects(self, include_archived: bool = False, limit=None, offset: int = 0) -> None:
        self.projects_loaded.emit([self.project])

    def get_project_stages_sync(self, project_id: int):
        return []


class FakeTaskController(QObject):
    tasks_loaded = Signal(list)
    all_tasks_loaded = Signal(list)
    task_created = Signal(object)
    task_updated = Signal(object)
    task_deleted = Signal(int)
    error_occurred = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.created: list[tuple[int, str, dict[str, object]]] = []

    def load_tasks(self, project_id: int) -> None:
        parent = Task(id=1, project_id=project_id, title="Ana", task_type=TaskType.GROUP.value)
        child = Task(id=2, project_id=project_id, title="Alt", parent_task_id=1)
        self.tasks_loaded.emit([parent, child])

    def create_task(self, project_id: int, title: str, **kwargs: object) -> None:
        self.created.append((project_id, title, kwargs))

    def get_task_sync(self, task_id: int):
        return None

    def move_task(self, task_id: int, new_parent_task_id: int | None, new_order_index: int) -> None:
        pass

    def get_descendant_count(self, task_id: int) -> int:
        return 0


def _init_managers() -> None:
    try:
        ThemeManager.instance(config.THEMES_DIR, config.STYLES_DIR)
    except RuntimeError:
        pass
    try:
        IconManager.instance(config.ICONS_DIR)
    except RuntimeError:
        pass
    try:
        StringManager.instance(config.LOCALES_DIR)
    except RuntimeError:
        pass
    try:
        FontManager.instance(config.FONTS_DIR)
    except RuntimeError:
        pass


def test_tasks_page_renders_parent_child_tree(qtbot):
    _init_managers()
    task_controller = FakeTaskController()
    project_controller = FakeProjectController()
    page = TasksPage(None, task_controller, project_controller)  # type: ignore[arg-type]
    qtbot.addWidget(page)

    assert page._tree.topLevelItemCount() == 1
    assert page._tree.topLevelItem(0).childCount() == 1


def test_tasks_page_quick_add_uses_selected_parent(qtbot):
    _init_managers()
    task_controller = FakeTaskController()
    project_controller = FakeProjectController()
    page = TasksPage(None, task_controller, project_controller)  # type: ignore[arg-type]
    qtbot.addWidget(page)

    parent_item = page._tree.topLevelItem(0)
    page._tree.setCurrentItem(parent_item)
    page._quick_add_edit.setText("Yeni alt")
    page._on_quick_add_task()

    assert task_controller.created[-1] == (1, "Yeni alt", {"parent_task_id": 1})


def test_main_window_ctrl_n_opens_project_dialog(monkeypatch, qtbot):
    _init_managers()
    opened: list[bool] = []

    class FakeDI:
        dashboard_controller = object()
        idea_controller = object()
        project_controller = FakeProjectController()
        task_controller = FakeTaskController()
        settings_controller = object()
        search_controller = object()

    class FakeDIContainer:
        @staticmethod
        def instance():
            return FakeDI()

    from core.events.app_events import NEW_PROJECT_REQUESTED
    from core.events.event_bus import EventBus

    class FakeProjectsPage(QDialog):
        def __init__(self, parent, di_container):
            super().__init__(parent)
            EventBus.instance().subscribe(NEW_PROJECT_REQUESTED, self.open_new_project_dialog)

        def open_new_project_dialog(self, *args, **kwargs):
            opened.append(True)

    from core.module_registry import FeaturePlugin, ModuleRegistry

    fake_plugins = [
        FeaturePlugin(
            page_key="dashboard",
            nav_label_key="nav_dashboard",
            nav_label_default="Dashboard",
            nav_icon="house",
            factory=lambda parent: QDialog(parent),
        ),
        FeaturePlugin(
            page_key="projects",
            nav_label_key="nav_projects",
            nav_label_default="Projeler",
            nav_icon="folder",
            factory=lambda parent: FakeProjectsPage(parent, None),
        )
    ]

    monkeypatch.setattr(main_window_module, "DIContainer", FakeDIContainer)
    monkeypatch.setattr(ModuleRegistry.instance(), "plugins", lambda: fake_plugins)
    monkeypatch.setattr(main_window_module, "Toast", lambda parent, event_bus: QDialog(parent))

    window = MainWindow()
    qtbot.addWidget(window)
    window._create_new_project()

    assert opened == [True]
