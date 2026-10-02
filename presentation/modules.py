"""Uygulama modüllerinin ModuleRegistry'ye kaydedildiği merkezi kurulum dosyası.

Her FeaturePlugin: sayfa anahtarı, navigasyon meta-verisi ve sayfa fabrikasını barındırır.
Sayfa fabrikaları lazy import kullanır; böylece gereksiz modüller açılışta yüklenmez.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.module_registry import FeaturePlugin, ModuleRegistry

if TYPE_CHECKING:
    from app.di_container import DIContainer


def _create_dashboard(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.dashboard_page import DashboardPage
    return DashboardPage(
        parent=parent,
        controller=di.dashboard_controller,
        idea_controller=di.idea_controller,
        theme=di.theme,
    )


def _create_projects(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.projects_page import ProjectsPage
    return ProjectsPage(parent=parent, di_container=di)


def _create_ideas(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.ideas_page import IdeasPage
    return IdeasPage(
        parent=parent,
        idea_controller=di.idea_controller,
        project_controller=di.project_controller,
    )


def _create_tasks(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.tasks import TasksPage
    return TasksPage(
        parent=parent,
        controller=di.task_controller,
        project_controller=di.project_controller,
        theme=di.theme,
    )


def _create_memo(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.memo_page import MemoPage
    return MemoPage(parent=parent, controller=di.memo_controller)


def _create_analytics(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.analytics_page import AnalyticsPage
    return AnalyticsPage(
        parent=parent,
        controller=di.analytics_controller,
        project_controller=di.project_controller,
        theme=di.theme,
    )


def _create_archive(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.archive_page import ArchivePage
    return ArchivePage(parent=parent, controller=di.project_controller)


def _create_info(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.info_page import InfoPage
    return InfoPage(parent=parent, theme=di.theme, icons=di.icons)


def _create_settings(parent: Any, di: DIContainer) -> Any:
    from presentation.pages.settings_page import SettingsPage
    return SettingsPage(
        parent=parent,
        controller=di.settings_controller,
        strings=di.strings,
        prefs=di.prefs,
        theme=di.theme,
    )


def setup_modules(di: DIContainer) -> None:
    """Tüm Feature Plugin'leri ModuleRegistry'ye kayıt eder."""
    registry = ModuleRegistry.instance()
    if registry.plugins():
        return

    registry.register(FeaturePlugin(
        page_key="dashboard",
        nav_label_key="nav_dashboard",
        nav_label_default="Dashboard",
        nav_icon="house",
        factory=lambda parent: _create_dashboard(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="projects",
        nav_label_key="nav_projects",
        nav_label_default="Projeler",
        nav_icon="folder",
        factory=lambda parent: _create_projects(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="ideas",
        nav_label_key="nav_ideas",
        nav_label_default="Fikirler",
        nav_icon="lightbulb",
        factory=lambda parent: _create_ideas(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="tasks",
        nav_label_key="nav_tasks",
        nav_label_default="Görevler",  # l10n: data — nav_tasks anahtarının fallback'i
        nav_icon="square-check",
        factory=lambda parent: _create_tasks(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="memo",
        nav_label_key="nav_memo",
        nav_label_default="Notlarım",  # l10n: data — nav_memo anahtarının fallback'i
        nav_icon="note-sticky",
        factory=lambda parent: _create_memo(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="analytics",
        nav_label_key="nav_analytics",
        nav_label_default="Analitik",
        nav_icon="chart-bar",
        factory=lambda parent: _create_analytics(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="archive",
        nav_label_key="nav_archive",
        nav_label_default="Arşiv",  # l10n: data — nav_archive anahtarının fallback'i
        nav_icon="archive",
        factory=lambda parent: _create_archive(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="info",
        nav_label_key="nav_info",
        nav_label_default="Bilgilendirme",
        nav_icon="circle-info",
        factory=lambda parent: _create_info(parent, di),
    ))
    registry.register(FeaturePlugin(
        page_key="settings",
        nav_label_key="nav_settings",
        nav_label_default="Ayarlar",
        nav_icon="settings",
        factory=lambda parent: _create_settings(parent, di),
    ))
