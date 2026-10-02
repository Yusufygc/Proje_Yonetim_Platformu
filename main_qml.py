"""QML Arayüz Giriş Noktası (main_qml.py).

DI Container'ı başlatır, QML Engine'i kurar, tema/dil/navigasyon
köprülerini ve SVG ikon sağlayıcısını bağlayarak uygulamayı açar.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Proje kökünü import yoluna ekle
sys.path.insert(0, str(Path(__file__).parent))

# --- Windows DLL Arama Yolu Düzeltmesi (Python 3.8+) ---
if getattr(sys, "frozen", False) and sys.platform == "win32":
    _base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent
    _dll_dirs = [
        _base,
        _base / "vosk",
        _base / "_sounddevice_data" / "portaudio-binaries",
    ]
    for _d in _dll_dirs:
        if _d.exists():
            os.add_dll_directory(str(_d))

from app import config  # noqa: E402
from app.di_container import DIContainer, OnboardingService  # noqa: E402
from core.logger import setup_global_exception_handler, setup_logging  # noqa: E402

logger = logging.getLogger(__name__)


def run_qml_app() -> int:
    """QML tabanlı arayüzü başlatan ana fonksiyon."""
    config.migrate_legacy_data_dir()
    setup_logging()
    setup_global_exception_handler()

    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ProjeTakip.ProjeTakipPlatformu.0.1.0"
        )

    # DI Container ve veritabanı kurulumu
    container = DIContainer.instance()
    container.bootstrap()
    OnboardingService(container).run_if_needed()

    from PySide6.QtCore import QTimer  # noqa: PLC0415
    from PySide6.QtGui import QFont, QIcon  # noqa: PLC0415
    from PySide6.QtQml import QQmlApplicationEngine  # noqa: PLC0415
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    from presentation.dimensions import FontFamily  # noqa: PLC0415
    from presentation.modules import setup_modules  # noqa: PLC0415
    from presentation.viewmodels.i18n_bridge import I18nBridge  # noqa: PLC0415
    from presentation.viewmodels.icon_provider import IconImageProvider  # noqa: PLC0415
    from presentation.viewmodels.navigation_bridge import NavigationBridge  # noqa: PLC0415
    from presentation.viewmodels.theme_bridge import ThemeBridge  # noqa: PLC0415

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.APP_ORGANIZATION)

    icon_path = Path(__file__).parent / "icons" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Font yükleme
    font_mgr = container.fonts
    font_mgr.load_all()
    saved_family = container.prefs.load_font_family()
    effective_family = saved_family if saved_family else font_mgr.ui_font
    app.setFont(QFont(effective_family, FontFamily.DEFAULT_SIZE))

    # Modülleri ModuleRegistry'ye kaydet
    setup_modules(container)

    # QML Engine ve Köprü Nesneleri
    engine = QQmlApplicationEngine()
    icon_provider = IconImageProvider(container.icons)
    engine.addImageProvider("icons", icon_provider)

    from presentation.viewmodels.analytics_viewmodel import AnalyticsViewModel  # noqa: PLC0415
    from presentation.viewmodels.archive_viewmodel import ArchiveViewModel  # noqa: PLC0415
    from presentation.viewmodels.dashboard_viewmodel import DashboardViewModel  # noqa: PLC0415
    from presentation.viewmodels.idea_viewmodel import IdeaViewModel  # noqa: PLC0415
    from presentation.viewmodels.memo_viewmodel import MemoViewModel  # noqa: PLC0415
    from presentation.viewmodels.project_viewmodel import ProjectViewModel  # noqa: PLC0415
    from presentation.viewmodels.search_viewmodel import SearchViewModel  # noqa: PLC0415
    from presentation.viewmodels.settings_viewmodel import SettingsViewModel  # noqa: PLC0415
    from presentation.viewmodels.task_viewmodel import TaskViewModel  # noqa: PLC0415
    from presentation.viewmodels.voice_bridge import VoiceBridge  # noqa: PLC0415

    theme_bridge = ThemeBridge(container.theme, container.prefs, parent=app)
    i18n_bridge = I18nBridge(container.strings, parent=app)
    nav_bridge = NavigationBridge(container.prefs, container.event_bus, parent=app)
    project_viewmodel = ProjectViewModel(container, parent=app)
    dashboard_viewmodel = DashboardViewModel(container.dashboard_controller, parent=app)
    task_viewmodel = TaskViewModel(container, parent=app)
    idea_viewmodel = IdeaViewModel(container, parent=app)
    memo_viewmodel = MemoViewModel(container, parent=app)
    analytics_viewmodel = AnalyticsViewModel(container, parent=app)
    archive_viewmodel = ArchiveViewModel(container, parent=app)
    settings_viewmodel = SettingsViewModel(container, parent=app)
    search_viewmodel = SearchViewModel(container, nav_bridge, parent=app)
    voice_bridge = VoiceBridge(container, parent=app)

    # Python GC koruması için referansları sakla
    app._icon_provider = icon_provider  # type: ignore[attr-defined]
    app._theme_bridge = theme_bridge  # type: ignore[attr-defined]
    app._i18n_bridge = i18n_bridge  # type: ignore[attr-defined]
    app._nav_bridge = nav_bridge  # type: ignore[attr-defined]
    app._project_viewmodel = project_viewmodel  # type: ignore[attr-defined]
    app._dashboard_viewmodel = dashboard_viewmodel  # type: ignore[attr-defined]
    app._task_viewmodel = task_viewmodel  # type: ignore[attr-defined]
    app._idea_viewmodel = idea_viewmodel  # type: ignore[attr-defined]
    app._memo_viewmodel = memo_viewmodel  # type: ignore[attr-defined]
    app._analytics_viewmodel = analytics_viewmodel  # type: ignore[attr-defined]
    app._archive_viewmodel = archive_viewmodel  # type: ignore[attr-defined]
    app._settings_viewmodel = settings_viewmodel  # type: ignore[attr-defined]
    app._search_viewmodel = search_viewmodel  # type: ignore[attr-defined]
    app._voice_bridge = voice_bridge  # type: ignore[attr-defined]

    # QML global context erişimleri
    context = engine.rootContext()
    context.setContextProperty("themeBridge", theme_bridge)
    context.setContextProperty("i18nBridge", i18n_bridge)
    context.setContextProperty("navBridge", nav_bridge)
    context.setContextProperty("projectViewModel", project_viewmodel)
    context.setContextProperty("dashboardViewModel", dashboard_viewmodel)
    context.setContextProperty("taskViewModel", task_viewmodel)
    context.setContextProperty("ideaViewModel", idea_viewmodel)
    context.setContextProperty("memoViewModel", memo_viewmodel)
    context.setContextProperty("analyticsViewModel", analytics_viewmodel)
    context.setContextProperty("archiveViewModel", archive_viewmodel)
    context.setContextProperty("settingsViewModel", settings_viewmodel)
    context.setContextProperty("searchViewModel", search_viewmodel)
    context.setContextProperty("voiceBridge", voice_bridge)

    qml_file = Path(__file__).parent / "presentation" / "qml" / "main.qml"
    engine.load(str(qml_file))

    if not engine.rootObjects():
        logger.error("QML dosyası yüklenemedi: %s", qml_file)
        return -1

    QTimer.singleShot(200, container.run_deferred_startup_tasks)
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_qml_app())
