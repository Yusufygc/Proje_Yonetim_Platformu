"""Uygulama ana giriş noktası (main.py).

Varsayılan olarak modern QML arayüzünü (main_qml.py) başlatır.
İsteğe bağlı olarak --legacy veya --widgets parametresiyle eski Qt Widgets
arayüzünü de çalıştırabilir.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Proje kökünü import path'e ekle
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


def _run_legacy_app(container: DIContainer) -> int:
    """Eski Qt Widgets tabanlı arayüzü başlatır."""
    from PySide6.QtCore import QTimer  # noqa: PLC0415
    from PySide6.QtGui import QFont, QIcon  # noqa: PLC0415
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    from presentation.dimensions import FontFamily  # noqa: PLC0415
    from presentation.modules import setup_modules  # noqa: PLC0415
    from presentation.shell.main_window import MainWindow  # noqa: PLC0415
    from presentation.utils.scroll_filter import WheelEventFilter  # noqa: PLC0415

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.APP_ORGANIZATION)

    icon_path = Path(__file__).parent / "icons" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    font_mgr = container.fonts
    font_mgr.load_all()
    saved = container.prefs.load_font_family()
    app.setFont(QFont(saved or font_mgr.ui_font, FontFamily.DEFAULT_SIZE))

    app.installEventFilter(WheelEventFilter(app))
    setup_modules(container)

    window = MainWindow()
    window.show()

    QTimer.singleShot(200, container.run_deferred_startup_tasks)
    return app.exec()


def main() -> None:
    """Uygulamayı başlatan ana fonksiyon."""
    if "--legacy" in sys.argv or "--widgets" in sys.argv:
        config.migrate_legacy_data_dir()
        setup_logging()
        setup_global_exception_handler()
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ProjeTakip.ProjeTakipPlatformu.0.1.0"
            )
        container = DIContainer.instance()
        container.bootstrap()
        OnboardingService(container).run_if_needed()
        sys.exit(_run_legacy_app(container))

    from main_qml import run_qml_app  # noqa: PLC0415
    sys.exit(run_qml_app())


if __name__ == "__main__":
    main()
