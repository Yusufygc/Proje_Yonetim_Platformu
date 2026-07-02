"""
Uygulama giriş noktası.
DI Container'ı kurar, global exception hook'u bağlar ve pencereyi açar.
"""
import sys
from pathlib import Path

# Proje kökünü import path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

# --- Windows DLL Arama Yolu Düzeltmesi (Python 3.8+) ---
# Python 3.8'den itibaren os.environ['PATH'] DLL aramada kullanılmıyor.
# Bunun yerine os.add_dll_directory() API'si ile dizinler kaydedilmelidir.
import os  # noqa: E402
if getattr(sys, "frozen", False) and sys.platform == "win32":
    _base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(__file__).parent

    _dll_dirs = [
        _base,                                                # _internal kökü
        _base / "vosk",                                       # libvosk.dll ve bağımlılıkları
        _base / "_sounddevice_data" / "portaudio-binaries",   # PortAudio DLL
    ]
    for _d in _dll_dirs:
        if _d.exists():
            os.add_dll_directory(str(_d))



from app import config  # noqa: E402
from core.logger import setup_global_exception_handler, setup_logging
from app.di_container import DIContainer, OnboardingService  # noqa: E402


def main() -> None:
    """Uygulamayı başlatan ana fonksiyon."""
    # Loglama dosyası açılınca yolu kalıcı olarak sabitlenir; bu yüzden veri
    # dizini taşıma her türlü loglama kurulumundan ÖNCE denenmelidir.
    config.migrate_legacy_data_dir()

    # 1. Loglama ve Hata Yönetimini Kur
    setup_logging()
    setup_global_exception_handler()

    # Windows görev çubuğunda doğru gruplama ve ikon için AppUserModelID zorunlu
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ProjeTakip.ProjeTakipPlatformu.0.1.0"
        )

    # DI Container yalnızca infrastructure'ı (DB, tema, font) başlatır
    container = DIContainer.instance()
    container.bootstrap()

    # İlk açılışta örnek veri oluştur (DI Container'dan ayrılmış iş mantığı)
    OnboardingService(container).run_if_needed()

    # PySide6'yı burada import ediyoruz; QApplication log kurulumundan sonra oluşmalı
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    from presentation.shell.main_window import MainWindow  # noqa: PLC0415

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.APP_ORGANIZATION)

    # Uygulama ve görev çubuğu ikonu — hem kaynak hem EXE modunda çalışır
    from PySide6.QtGui import QIcon  # noqa: PLC0415
    _icon_path = Path(__file__).parent / "icons" / "app_icon.ico"
    if _icon_path.exists():
        app.setWindowIcon(QIcon(str(_icon_path)))


    # Fontları yükle ve uygula (kullanıcı tercihi varsa önceliği alır)
    from PySide6.QtGui import QFont
    from presentation.dimensions import FontFamily
    font_mgr = container.fonts
    font_mgr.load_all()
    saved_family = container.prefs.load_font_family()
    effective_family = saved_family if saved_family else font_mgr.ui_font
    app.setFont(QFont(effective_family, FontFamily.DEFAULT_SIZE))

    # Global Scroll Event Filter'ı yükle
    from presentation.utils.scroll_filter import WheelEventFilter
    app.installEventFilter(WheelEventFilter(app))

    # Modülleri registry'ye kaydet; MainWindow'dan önce çağrılmalıdır
    from presentation.modules import setup_modules  # noqa: PLC0415
    setup_modules(container)

    window = MainWindow()
    window.show()

    # Pencere açıldıktan sonra ağır ama kritik-olmayan görevleri arka plana al
    from PySide6.QtCore import QTimer  # noqa: PLC0415

    QTimer.singleShot(200, container.run_deferred_startup_tasks)

    def _deferred_font_download() -> None:
        try:
            from scripts.download_fonts import ensure_fonts  # noqa: PLC0415
            ensure_fonts()
        except Exception:  # noqa: BLE001
            pass

    QTimer.singleShot(500, _deferred_font_download)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
