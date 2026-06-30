"""
Uygulama modüllerinin ModuleRegistry'ye kaydedildiği merkezi kurulum dosyası.
Her FeaturePlugin: sayfa anahtarı, navigasyon meta-verisi ve sayfa fabrikasını barındırır.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from core.module_registry import FeaturePlugin, ModuleRegistry

if TYPE_CHECKING:
    from app.di_container import DIContainer


def setup_modules(di: DIContainer) -> None:
    """Tüm Feature Plugin'leri ModuleRegistry'ye kayıt eder. QApplication'dan sonra çağrılmalıdır."""
    from presentation.pages.analytics_page import AnalyticsPage
    from presentation.pages.archive_page import ArchivePage
    from presentation.pages.dashboard_page import DashboardPage
    from presentation.pages.ideas_page import IdeasPage
    from presentation.pages.info_page import InfoPage
    from presentation.pages.memo_page import MemoPage
    from presentation.pages.projects_page import ProjectsPage
    from presentation.pages.settings_page import SettingsPage
    from presentation.pages.tasks import TasksPage

    registry = ModuleRegistry.instance()

    registry.register(FeaturePlugin(
        page_key="dashboard",
        nav_label_key="nav_dashboard",
        nav_label_default="Dashboard",
        nav_icon="house",
        factory=lambda parent: DashboardPage(
            parent=parent,
            controller=di.dashboard_controller,
            idea_controller=di.idea_controller,
            theme=di.theme,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="projects",
        nav_label_key="nav_projects",
        nav_label_default="Projeler",
        nav_icon="folder",
        factory=lambda parent: ProjectsPage(
            parent=parent,
            di_container=di,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="ideas",
        nav_label_key="nav_ideas",
        nav_label_default="Fikirler",
        nav_icon="lightbulb",
        factory=lambda parent: IdeasPage(
            parent=parent,
            idea_controller=di.idea_controller,
            project_controller=di.project_controller,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="tasks",
        nav_label_key="nav_tasks",
        nav_label_default="Görevler",  # l10n: data — nav_tasks anahtarının fallback'i
        nav_icon="square-check",
        factory=lambda parent: TasksPage(
            parent=parent,
            controller=di.task_controller,
            project_controller=di.project_controller,
            theme=di.theme,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="memo",
        nav_label_key="nav_memo",
        nav_label_default="Notlarım",
        nav_icon="note-sticky",
        factory=lambda parent: MemoPage(
            parent=parent,
            controller=di.memo_controller,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="analytics",
        nav_label_key="nav_analytics",
        nav_label_default="Analitik",
        nav_icon="chart-bar",
        factory=lambda parent: AnalyticsPage(
            parent=parent,
            controller=di.analytics_controller,
            project_controller=di.project_controller,
            theme=di.theme,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="archive",
        nav_label_key="nav_archive",
        nav_label_default="Arşiv",
        nav_icon="archive",
        factory=lambda parent: ArchivePage(
            parent=parent,
            controller=di.project_controller,
        ),
    ))
    registry.register(FeaturePlugin(
        page_key="info",
        nav_label_key="nav_info",
        nav_label_default="Bilgilendirme",
        nav_icon="circle-info",
        factory=lambda parent: InfoPage(parent=parent, theme=di.theme, icons=di.icons),
    ))
    registry.register(FeaturePlugin(
        page_key="settings",
        nav_label_key="nav_settings",
        nav_label_default="Ayarlar",
        nav_icon="settings",
        factory=lambda parent: SettingsPage(
            parent=parent,
            controller=di.settings_controller,
            strings=di.strings,
            prefs=di.prefs,
            theme=di.theme,
        ),
    ))
