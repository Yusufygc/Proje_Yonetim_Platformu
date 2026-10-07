"""QML Köprüleri (Theme, I18n, Navigation, Project, Dashboard) Birim Testleri."""
from __future__ import annotations

import os
import sys
from pathlib import Path

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
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from app.di_container import DIContainer
from domain.models.idea import Idea
from domain.models.memo import Memo
from domain.models.project import Project
from domain.models.task import Task
from infrastructure.database.db_manager import DatabaseManager
from presentation.modules import setup_modules
from presentation.viewmodels.analytics_viewmodel import AnalyticsViewModel
from presentation.viewmodels.archive_viewmodel import ArchiveViewModel
from presentation.viewmodels.dashboard_viewmodel import DashboardViewModel
from presentation.viewmodels.i18n_bridge import I18nBridge
from presentation.viewmodels.icon_provider import IconImageProvider
from presentation.viewmodels.idea_dialog_viewmodel import IdeaDialogViewModel
from presentation.viewmodels.idea_list_model import IdeaListModel
from presentation.viewmodels.idea_viewmodel import IdeaViewModel
from presentation.viewmodels.memo_list_model import MemoListModel
from presentation.viewmodels.memo_viewmodel import MemoViewModel
from presentation.viewmodels.navigation_bridge import NavigationBridge
from presentation.viewmodels.project_list_model import ProjectListModel
from presentation.viewmodels.project_subitems_viewmodel import ProjectSubitemsViewModel
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.viewmodels.search_viewmodel import SearchViewModel
from presentation.viewmodels.settings_viewmodel import SettingsViewModel
from presentation.viewmodels.task_dialog_viewmodel import TaskDialogViewModel
from presentation.viewmodels.task_list_model import TaskListModel
from presentation.viewmodels.task_viewmodel import TaskViewModel
from presentation.viewmodels.update_viewmodel import UpdateViewModel
from presentation.viewmodels.theme_bridge import ThemeBridge
from presentation.viewmodels.voice_bridge import VoiceBridge


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
    assert isinstance(bridge.currentTheme, str) and len(bridge.currentTheme) > 0
    assert isinstance(bridge.isDark, bool)
    assert bridge.background.startswith("#")
    assert bridge.surface.startswith("#")
    assert bridge.surfaceAlt.startswith("#")
    assert bridge.hoverOverlay.startswith("#")

    initial_dark = bridge.isDark
    bridge.toggleTheme()
    assert bridge.isDark != initial_dark
    assert bridge.surfaceAlt.startswith("#")
    assert bridge.hoverOverlay.startswith("#")
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


def test_project_viewmodel_add_output_when_title_given_should_list_it_by_caption(
    qapp: QApplication, container: DIContainer
) -> None:
    from PySide6.QtCore import QThreadPool

    project = container.services.project.create_project(title="Çıktı projesi")
    pvm = ProjectViewModel(container, parent=qapp)
    subitems = ProjectSubitemsViewModel(container, pvm, parent=qapp)
    pvm.selectProject(project.id)
    QThreadPool.globalInstance().waitForDone(2000)

    subitems.addOutput("Sürüm notları", "C:/docs/notes.md")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert [o["title"] for o in subitems.selectedOutputs] == ["Sürüm notları"]
    assert subitems.selectedOutputs[0]["file_path"] == "C:/docs/notes.md"


def test_project_viewmodel_update_note_when_edited_should_reload_notes(
    qapp: QApplication, container: DIContainer
) -> None:
    from PySide6.QtCore import QThreadPool

    project = container.services.project.create_project(title="Not projesi")
    pvm = ProjectViewModel(container, parent=qapp)
    subitems = ProjectSubitemsViewModel(container, pvm, parent=qapp)
    pvm.selectProject(project.id)
    subitems.createNote("Eski başlık", "İçerik")
    for _ in range(2):
        QThreadPool.globalInstance().waitForDone(2000)
        qapp.processEvents()
    note_id = subitems.selectedNotes[0]["id"]

    subitems.updateNote(note_id, "Yeni başlık", "Yeni içerik")
    for _ in range(2):
        QThreadPool.globalInstance().waitForDone(2000)
        qapp.processEvents()

    assert [(n["title"], n["body"]) for n in subitems.selectedNotes] == [("Yeni başlık", "Yeni içerik")]


def test_dashboard_viewmodel_stats(qapp: QApplication, container: DIContainer) -> None:
    dvm = DashboardViewModel(container.dashboard_controller, parent=qapp)
    assert isinstance(dvm.activeProjects, int)
    assert isinstance(dvm.totalTasks, int)
    assert isinstance(dvm.openTasks, int)


def test_dashboard_viewmodel_when_data_exists_should_expose_task_and_idea_titles(
    qapp: QApplication, container: DIContainer
) -> None:
    from PySide6.QtCore import QThreadPool

    project = container.services.project.create_project(title="Pano projesi")
    container.services.task.create_task(project.id, "Acil görev", priority="CRITICAL")
    container.services.idea.create_idea("Pano fikri", problem="Sorun")

    dvm = DashboardViewModel(container.dashboard_controller, parent=qapp)
    QThreadPool.globalInstance().waitForDone(3000)
    qapp.processEvents()

    assert [t["title"] for t in dvm.highPriorityTasks] == ["Acil görev"]
    idea = dvm.recentIdeas[0]
    assert idea["title"] == "Pano fikri"
    assert idea["created_at"] != ""


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

    # Tamamlanmış alt görev ağacı testi: kendisi dahil tüm alt görevler DONE ise kapalı kalmalı
    t1_done = Task(id=10, project_id=1, parent_task_id=None, order_index=0, title="Biten Ana Görev", status="DONE", priority="HIGH", task_type="TASK")
    t11_done = Task(id=11, project_id=1, parent_task_id=10, order_index=0, title="Biten Alt Görev 1", status="DONE", priority="MEDIUM", task_type="TASK")
    t12_done = Task(id=12, project_id=1, parent_task_id=10, order_index=1, title="Biten Alt Görev 2", status="DONE", priority="LOW", task_type="TASK")
    t20_active = Task(id=20, project_id=1, parent_task_id=None, order_index=1, title="Aktif Ana Görev", status="IN_PROGRESS", priority="MEDIUM", task_type="TASK")

    model.set_tasks([t1_done, t11_done, t12_done, t20_active])
    # Biten dal varsayılan olarak kapalı olmalı: t1_done ve t20_active görünür (2 satır)
    assert model.rowCount() == 2
    # Kullanıcı elle açmak isterse açılabilmeli
    model.toggleExpanded(10)
    assert model.rowCount() == 4
    # Tekrar basarsa kapanmalı
    model.toggleExpanded(10)
    assert model.rowCount() == 2


def test_task_viewmodel_crud_and_dialog_state(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    proj = container.project_controller._service.create_project("Görev Test Projesi")
    tvm = TaskViewModel(container, parent=qapp)
    dialog = TaskDialogViewModel(container, tvm, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)

    tvm.selectProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)

    assert not dialog.isDialogOpen
    dialog.openCreateDialog()
    assert dialog.isDialogOpen
    assert dialog.dialogMode == "create"

    task_title = f"Test Görev {os.getpid()}"
    dialog.saveTask({
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

    # Panoya kopyalama testi
    tvm.copyTaskToClipboard(created_task.id)
    clipboard_text = qapp.clipboard().text()
    assert task_title in clipboard_text
    assert "Adım 1" in clipboard_text

    # Görevi çoğaltma (Duplicate) testi
    tvm.duplicateTask(created_task.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    tasks_after_dup = container.task_controller._service.get_tasks(proj.id)
    duplicated_task = next((t for t in tasks_after_dup if t.title == f"{task_title} (Kopya)"), None)
    assert duplicated_task is not None
    assert len(duplicated_task.checklist_items) == 2

    tvm.deleteTask(created_task.id)
    tvm.deleteTask(duplicated_task.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert container.task_controller.get_task_sync(created_task.id) is None
    assert container.task_controller.get_task_sync(duplicated_task.id) is None


def test_collect_task_copy_lines_when_tree_has_checklist_should_indent_children() -> None:
    from domain.models.checklist_item import ChecklistItem
    from presentation.viewmodels.task_clipboard import collect_task_copy_lines

    root = Task(id=1, project_id=1, parent_task_id=None, order_index=0, title="Ana", status="TODO", priority="LOW", task_type="TASK")
    child = Task(id=2, project_id=1, parent_task_id=1, order_index=0, title="Alt", status="DONE", priority="LOW", task_type="TASK")
    root.checklist_items = [ChecklistItem(task_id=1, text="Madde", is_done=True)]
    child.checklist_items = []

    assert collect_task_copy_lines([root, child], 1) == ["[TODO] Ana", "  [x] Madde", "  [DONE] Alt"]
    assert collect_task_copy_lines([root, child], 99) == []


def test_task_dialog_viewmodel_when_parent_saved_with_auto_status_should_keep_derived_status(
    qapp: QApplication, container: DIContainer
) -> None:
    from PySide6.QtCore import QThreadPool

    project = container.services.project.create_project(title="Otomatik durum projesi")
    parent = container.services.task.create_task(project.id, "Üst görev")
    container.services.task.create_task(project.id, "Alt görev", parent_task_id=parent.id)
    tvm = TaskViewModel(container, parent=qapp)
    dialog = TaskDialogViewModel(container, tvm, parent=qapp)
    tvm.selectProject(project.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    dialog.openEditDialog(parent.id)
    assert dialog.dialogInitialData["has_children"] is True

    dialog.saveTask({"title": "Üst görev (yeni ad)", "status": "AUTO", "priority": "MEDIUM", "task_type": "TASK"})
    QThreadPool.globalInstance().waitForDone(2000)

    saved = container.services.task.get_task(parent.id)
    assert saved.title == "Üst görev (yeni ad)"
    assert saved.status == "TODO"
    assert not dialog.isDialogOpen


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

    dialog = IdeaDialogViewModel(container, ivm, parent=qapp)
    assert not dialog.isDialogOpen
    dialog.openCreateDialog()
    assert dialog.isDialogOpen
    assert dialog.dialogMode == "create"
    dialog.closeDialog()
    assert not dialog.isDialogOpen

    idea_title = f"Test Fikir {os.getpid()}"
    dialog.saveIdea({
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


def test_memo_list_model_and_search(qapp: QApplication) -> None:
    model = MemoListModel(parent=qapp)
    m1 = Memo(id=1, title="Toplantı Notları", body="Sprint planlama detayları")
    m2 = Memo(id=2, title="Alışveriş Listesi", body="Ekipman ve kablo")
    model.set_memos([m1, m2])

    assert model.rowCount() == 2
    model.setSearchQuery("Sprint")
    assert model.rowCount() == 1
    model.setSearchQuery("")
    assert model.rowCount() == 2


def test_memo_viewmodel_crud(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    mvm = MemoViewModel(container, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    initial_count = mvm.totalMemos
    memo_title = f"Test Memo {os.getpid()}"
    mvm.createMemo(memo_title)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert mvm.totalMemos >= initial_count + 1
    memo_id = mvm.selectedMemoId
    assert memo_id != 0

    mvm.saveMemo(memo_id, memo_title, "Not gövdesi", '[{"color":"#FFFFFF"}]')
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert mvm.selectedMemo.get("body") == "Not gövdesi"

    # Görsel metodları testi
    from PySide6.QtGui import QImage  # noqa: PLC0415
    assert isinstance(mvm.hasClipboardImage(), bool)
    dummy_img = QImage(32, 32, QImage.Format.Format_RGB32)
    dummy_img.fill(0xFF0000)
    qapp.clipboard().setImage(dummy_img)
    assert mvm.hasClipboardImage() is True
    saved_url = mvm.saveClipboardImage()
    assert saved_url.startswith("file://")
    assert saved_url.endswith(".png")

    mvm.deleteMemo(memo_id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert container.memo_controller.get_sync(memo_id) is None


def test_project_subitems_viewmodel_decisions_notes_resources(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    proj = container.project_controller._service.create_project("Alt Öğeler Test Projesi")
    pvm = ProjectViewModel(container, parent=qapp)
    subitems = ProjectSubitemsViewModel(container, pvm, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    pvm.selectProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    # Karar Ekleme
    subitems.createDecision("Mimari Karar", "QML Kullanımı", "ACCEPTED")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert len(subitems.selectedDecisions) >= 1

    # Not Ekleme
    subitems.createNote("Teknik Not", "Test not içeriği")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert len(subitems.selectedNotes) >= 1

    # Kaynak Ekleme
    subitems.createResource("Qt Docs", "https://doc.qt.io", "DOCUMENT")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert len(subitems.selectedResources) >= 1

    # Karar Silme
    dec_id = subitems.selectedDecisions[0]["id"]
    subitems.deleteDecision(dec_id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    # Not Silme
    note_id = subitems.selectedNotes[0]["id"]
    subitems.deleteNote(note_id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    # Kaynak Silme
    res_id = subitems.selectedResources[0]["id"]
    subitems.deleteResource(res_id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()


def test_analytics_viewmodel(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    avm = AnalyticsViewModel(container, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert avm.period == "weekly"
    assert avm.projectId == 0
    assert isinstance(avm.totalCompleted, int)
    assert isinstance(avm.completionRate, float)
    assert isinstance(avm.streakDays, int)
    assert isinstance(avm.onTimeRate, float)
    assert isinstance(avm.timeSeries, list)
    assert isinstance(avm.priorityDistribution, list)
    assert isinstance(avm.projectDistribution, list)

    avm.setPeriod("monthly")
    assert avm.period == "monthly"

    avm.setProjectId(1)
    assert avm.projectId == 1
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()


def test_archive_viewmodel(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    proj = container.project_controller._service.create_project("Arşivlenecek Test Projesi")
    container.project_controller.archive_project(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    arch_vm = ArchiveViewModel(container, parent=qapp)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    assert arch_vm.count >= 1
    target = next((p for p in arch_vm.archivedProjects if p["id"] == proj.id), None)
    assert target is not None
    assert target["title"] == "Arşivlenecek Test Projesi"

    # Geri yükleme
    arch_vm.restoreProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    # Kalıcı silme testi
    container.project_controller.archive_project(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    arch_vm.deleteProject(proj.id)
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()


def test_settings_viewmodel(qapp: QApplication, container: DIContainer) -> None:
    svm = SettingsViewModel(container, parent=qapp)
    assert isinstance(svm.isDark, bool)
    assert len(svm.themePackages) == 6
    assert len(svm.fontFamilies) >= 5
    assert svm.appName != ""
    assert svm.appVersion != ""

    svm.setMode(True)
    assert svm.isDark is True
    svm.setMode(False)
    assert svm.isDark is False

    svm.setThemePackage("indigo")
    assert svm.activePackage == "indigo"

    svm.setFontFamily("Inter")
    assert svm.fontFamily == "Inter"

    svm.setLanguage("en")
    assert svm.currentLanguage == "en"
    svm.setLanguage("tr")
    assert svm.currentLanguage == "tr"

    exp_path = svm.getDefaultExportPath()
    assert exp_path.endswith(".json")


def test_search_viewmodel(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool

    nb = NavigationBridge(container.prefs, container.event_bus, parent=qapp)
    svm = SearchViewModel(container, nb, parent=qapp)

    svm.search("al")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()

    svm.clear()
    assert svm.query == ""
    assert svm.count == 0

    # Navigasyon çağrıları
    svm.selectItem("project", 1)
    assert nb.currentPage == "projects"
    svm.selectItem("task", 1)
    assert nb.currentPage == "tasks"
    svm.selectItem("idea", 1)
    assert nb.currentPage == "ideas"


def test_voice_bridge(qapp: QApplication, container: DIContainer) -> None:
    vb = VoiceBridge(container, parent=qapp)
    assert vb.isListening is False
    assert vb.partialText == ""

    # Sinyal tetikleme testi
    transcripts: list[str] = []
    vb.textTranscribed.connect(transcripts.append)
    vb._on_final("merhaba dünya")
    assert len(transcripts) == 1
    assert transcripts[0] == "merhaba dünya"


def test_qml_main_window_loads_successfully(qapp: QApplication, container: DIContainer) -> None:
    setup_modules(container)
    engine = QQmlApplicationEngine(parent=qapp)

    icon_provider = IconImageProvider(container.icons)
    engine.addImageProvider("icons", icon_provider)

    tb = ThemeBridge(container.theme, container.prefs, parent=qapp)
    ib = I18nBridge(container.strings, parent=qapp)
    nb = NavigationBridge(container.prefs, container.event_bus, parent=qapp)
    pv = ProjectViewModel(container, parent=qapp)
    psv = ProjectSubitemsViewModel(container, pv, parent=qapp)
    dv = DashboardViewModel(container.dashboard_controller, parent=qapp)
    tv = TaskViewModel(container, parent=qapp)
    tdv = TaskDialogViewModel(container, tv, parent=qapp)
    iv = IdeaViewModel(container, parent=qapp)
    idv = IdeaDialogViewModel(container, iv, parent=qapp)
    mv = MemoViewModel(container, parent=qapp)
    anv = AnalyticsViewModel(container, parent=qapp)
    arv = ArchiveViewModel(container, parent=qapp)
    stv = SettingsViewModel(container, parent=qapp)
    scv = SearchViewModel(container, nb, parent=qapp)
    vb = VoiceBridge(container, parent=qapp)
    uv = UpdateViewModel(container, parent=qapp)

    qapp._test_tb = tb  # type: ignore[attr-defined]
    qapp._test_ib = ib  # type: ignore[attr-defined]
    qapp._test_nb = nb  # type: ignore[attr-defined]
    qapp._test_pv = pv  # type: ignore[attr-defined]
    qapp._test_psv = psv  # type: ignore[attr-defined]
    qapp._test_dv = dv  # type: ignore[attr-defined]
    qapp._test_tv = tv  # type: ignore[attr-defined]
    qapp._test_tdv = tdv  # type: ignore[attr-defined]
    qapp._test_iv = iv  # type: ignore[attr-defined]
    qapp._test_idv = idv  # type: ignore[attr-defined]
    qapp._test_mv = mv  # type: ignore[attr-defined]
    qapp._test_anv = anv  # type: ignore[attr-defined]
    qapp._test_arv = arv  # type: ignore[attr-defined]
    qapp._test_stv = stv  # type: ignore[attr-defined]
    qapp._test_scv = scv  # type: ignore[attr-defined]
    qapp._test_vb = vb  # type: ignore[attr-defined]
    qapp._test_uv = uv  # type: ignore[attr-defined]

    engine.rootContext().setContextProperty("themeBridge", tb)
    engine.rootContext().setContextProperty("i18nBridge", ib)
    engine.rootContext().setContextProperty("navBridge", nb)
    engine.rootContext().setContextProperty("projectViewModel", pv)
    engine.rootContext().setContextProperty("projectSubitemsViewModel", psv)
    engine.rootContext().setContextProperty("dashboardViewModel", dv)
    engine.rootContext().setContextProperty("taskViewModel", tv)
    engine.rootContext().setContextProperty("taskDialogViewModel", tdv)
    engine.rootContext().setContextProperty("ideaViewModel", iv)
    engine.rootContext().setContextProperty("ideaDialogViewModel", idv)
    engine.rootContext().setContextProperty("memoViewModel", mv)
    engine.rootContext().setContextProperty("analyticsViewModel", anv)
    engine.rootContext().setContextProperty("archiveViewModel", arv)
    engine.rootContext().setContextProperty("settingsViewModel", stv)
    engine.rootContext().setContextProperty("searchViewModel", scv)
    engine.rootContext().setContextProperty("voiceBridge", vb)
    engine.rootContext().setContextProperty("updateViewModel", uv)

    qml_file = Path("presentation/qml/main.qml")
    engine.load(str(qml_file))

    assert len(engine.rootObjects()) > 0

    # Tüm sayfalar arası geçiş testi
    for page_key in ["dashboard", "projects", "ideas", "tasks", "memo", "analytics", "archive", "info", "settings"]:
        nb.navigateTo(page_key)
        qapp.processEvents()

    from PySide6.QtQml import QQmlComponent  # noqa: PLC0415
    for view_file in [
        "presentation/qml/views/DashboardView.qml",
        "presentation/qml/views/ProjectsView.qml",
        "presentation/qml/views/IdeasView.qml",
        "presentation/qml/views/TasksView.qml",
        "presentation/qml/views/MemoView.qml",
        "presentation/qml/views/AnalyticsView.qml",
        "presentation/qml/views/ArchiveView.qml",
        "presentation/qml/views/InfoView.qml",
        "presentation/qml/views/SettingsView.qml",
        "presentation/qml/dialogs/ProjectDialog.qml",
        "presentation/qml/dialogs/TaskDialog.qml",
        "presentation/qml/dialogs/IdeaDialog.qml",
        "presentation/qml/components/GlobalSearchModal.qml",
    ]:
        comp = QQmlComponent(engine, view_file)
        errs = [e.toString() for e in comp.errors()]
        assert comp.isReady(), f"Bileşen yüklenemedi {view_file}: {errs}"
        obj = comp.create()
        assert obj is not None
        qapp.processEvents()


def test_window_geometry_persistence_and_centering(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtQuick import QQuickWindow  # noqa: PLC0415

    from presentation.window_geometry import setup_window_geometry  # noqa: PLC0415

    prefs = container.prefs

    # 1. Konum kaydetme ve okuma doğrulaması
    prefs.save_window_rect(100, 80, 600, 500, False)
    assert prefs.load_window_rect() == (100, 80, 600, 500, False)

    # 2. Geçerli kayıtlı konumun pencereye uygulanması
    win = QQuickWindow()
    setup_window_geometry(win, prefs, qapp)
    assert win.x() == 100
    assert win.y() == 80
    assert win.width() == 600
    assert win.height() == 500

    # 3. Ekran dışı (offscreen) geçersiz koordinatların güvenli şekilde aktif ekranda kurtarılması
    prefs.save_window_rect(-9999, -9999, 1200, 800, False)
    win_recovered = QQuickWindow()
    setup_window_geometry(win_recovered, prefs, qapp)
    assert win_recovered.x() != -9999
    assert win_recovered.y() != -9999
    assert any(s.availableGeometry().contains(win_recovered.geometry()) for s in qapp.screens())

    prefs.save_window_rect(0, 0, 0, 0, False)
    prefs._settings.remove("window/rect")


def test_fit_rect_to_screen_when_saved_at_screen_top_should_leave_room_for_title_bar() -> None:
    from PySide6.QtCore import QRect  # noqa: PLC0415

    from presentation.window_geometry import fit_rect_to_screen  # noqa: PLC0415

    avail = QRect(0, 0, 1920, 1040)

    fitted = fit_rect_to_screen(QRect(0, 0, 1920, 1040), avail, top_margin=31)

    assert fitted.top() >= 31
    assert fitted.bottom() <= avail.bottom()
    assert fitted.width() <= avail.width()


def test_fit_rect_to_screen_when_saved_below_screen_should_pull_back_inside() -> None:
    from PySide6.QtCore import QRect  # noqa: PLC0415

    from presentation.window_geometry import fit_rect_to_screen  # noqa: PLC0415

    avail = QRect(0, 0, 1366, 728)

    fitted = fit_rect_to_screen(QRect(1300, 700, 800, 600), avail, top_margin=31)

    assert avail.contains(fitted)
    assert fitted.top() >= 31


def test_project_viewmodel_tasks_and_stage_progress(qapp: QApplication, container: DIContainer) -> None:
    from PySide6.QtCore import QThreadPool
    pvm = ProjectViewModel(container, parent=qapp)
    proj = container.project_controller._service.create_project("Görev ve Aşama Testi")
    QThreadPool.globalInstance().waitForDone(2000)
    pvm.selectProject(proj.id)
    assert pvm.selectedProjectId == proj.id
    assert len(pvm.selectedTasks) == 0

    pvm.addTask("İlk Görev")
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert len(pvm.selectedTasks) == 1
    t = pvm.selectedTasks[0]
    assert t["title"] == "İlk Görev"
    assert not t["is_done"]

    pvm.toggleTaskStatus(t["id"])
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert pvm.selectedTasks[0]["is_done"]
    assert pvm.selectedProject["progress"] == 100

    pvm.deleteTask(t["id"])
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()
    assert len(pvm.selectedTasks) == 0


def test_qml_drawing_canvas_operations(qapp: QApplication, container: DIContainer) -> None:
    import json

    from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

    from presentation.viewmodels.i18n_bridge import I18nBridge
    from presentation.viewmodels.theme_bridge import ThemeBridge

    engine = QQmlApplicationEngine(parent=qapp)
    tb = ThemeBridge(container.theme, container.prefs, parent=qapp)
    ib = I18nBridge(container.strings, parent=qapp)
    engine.rootContext().setContextProperty("themeBridge", tb)
    engine.rootContext().setContextProperty("i18nBridge", ib)

    comp = QQmlComponent(engine, "presentation/qml/views/memo/DrawingCanvas.qml")
    assert comp.isReady(), f"DrawingCanvas yüklenemedi: {[e.toString() for e in comp.errors()]}"
    canvas = comp.create()
    assert canvas is not None

    # 1. Eski format yükleme geriye dönük uyumluluk testi
    legacy_json = json.dumps([{"points": [{"x": 10, "y": 10}, {"x": 20, "y": 20}], "color": "#EF4444", "width": 3}])
    canvas.loadDrawingJson(legacy_json)
    items = json.loads(canvas.getDrawingJson())
    assert len(items) == 1
    assert items[0]["type"] == "pen"
    assert items[0]["color"] == "#EF4444"

    # 2. Yeni şekiller yükleme ve getDrawingJson testi
    shapes = [
        {"type": "line", "x1": 0, "y1": 0, "x2": 50, "y2": 50, "color": "#3B82F6", "width": 2},
        {"type": "arrow", "x1": 10, "y1": 20, "x2": 80, "y2": 90, "color": "#10B981", "width": 4},
        {"type": "rect", "x": 10, "y": 20, "w": 100, "h": 50, "color": "#F59E0B", "width": 2, "fill": ""},
        {"type": "round_rect", "x": 15, "y": 25, "w": 90, "h": 40, "r": 8, "color": "#8B5CF6", "width": 2, "fill": ""},
        {"type": "circle", "cx": 100, "cy": 100, "rx": 30, "ry": 20, "color": "#EF4444", "width": 3, "fill": ""}
    ]
    canvas.loadDrawingJson(json.dumps(shapes))
    loaded = json.loads(canvas.getDrawingJson())
    assert len(loaded) == 5
    assert loaded[1]["type"] == "arrow"
    assert loaded[2]["type"] == "rect"

    # 3. Temizle ve Geri Al (Undo/Redo) testi
    canvas.clearCanvas()
    assert len(json.loads(canvas.getDrawingJson())) == 0
    assert canvas.property("canUndo") is True

    # 4. Mod ve renk seçimi: mod değişince uyumsuz araç sıfırlanır, renk seçmek silgiden çıkarır
    canvas.selectMode("flowchart")
    assert canvas.property("activeTool") == "flow_process"
    canvas.selectMode("draw")
    assert canvas.property("activeTool") == "pen"
    canvas.setProperty("activeTool", "eraser")
    canvas.selectColor("#3B82F6")
    assert canvas.property("activeTool") == "pen"
    assert canvas.property("currentColor") == "#3B82F6"

    canvas.undo()
    assert len(json.loads(canvas.getDrawingJson())) == 5
    assert canvas.property("canRedo") is True

    canvas.redo()
    assert len(json.loads(canvas.getDrawingJson())) == 0

    # 4. Akış şeması şablonu (Flowchart Template) ve blok metinleri testi
    canvas.insertFlowchartTemplate()
    template_items = json.loads(canvas.getDrawingJson())
    assert len(template_items) >= 10
    types = [it["type"] for it in template_items]
    assert "flow_start" in types
    assert "flow_process" in types
    assert "flow_decision" in types
    assert "flow_io" in types
    assert "arrow" in types

    # 5. Blok metni güncelleme ve etiket testi
    canvas.openTextEditor(0)
    canvas.applyBlockText("Program Başlangıcı")
    updated = json.loads(canvas.getDrawingJson())
    assert updated[0]["text"] == "Program Başlangıcı"

    # 6. Arka plan görseli testi
    test_img_url = "file:///C:/path/to/test.png"
    canvas.setBackgroundImage(test_img_url)
    assert canvas.property("backgroundImage") == test_img_url
    data_with_img = json.loads(canvas.getDrawingJson())
    assert isinstance(data_with_img, dict)
    assert data_with_img.get("backgroundImage") == test_img_url

    # Geri alma ile görselin temizlenmesi
    canvas.undo()
    assert canvas.property("backgroundImage") == ""

    # Yükleme ile görselin geri gelmesi
    canvas.loadDrawingJson(json.dumps(data_with_img))
    assert canvas.property("backgroundImage") == test_img_url





