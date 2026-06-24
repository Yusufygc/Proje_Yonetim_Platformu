"""
Uygulama giriş noktası.
DI Container'ı kurar, global exception hook'u bağlar ve pencereyi açar.
"""
import sys
from pathlib import Path

# Proje kökünü import path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

import config  # noqa: E402 — sys.path ayarından sonra import edilmeli
from core.logger import setup_global_exception_handler, setup_logging
from di_container import DIContainer, OnboardingService  # noqa: E402


def main() -> None:
    """Uygulamayı başlatan ana fonksiyon."""
    # 1. Loglama ve Hata Yönetimini Kur
    setup_logging()
    setup_global_exception_handler()

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

    # Premium fontlar eksikse arka planda indir (hata olursa fallback devreye girer)
    try:
        from scripts.download_fonts import ensure_fonts  # noqa: PLC0415
        ensure_fonts()
    except Exception:  # noqa: BLE001
        pass

    # Fontları yükle ve uygula (kullanıcı tercihi varsa önceliği alır)
    from PySide6.QtGui import QFont
    font_mgr = container.fonts
    font_mgr.load_all()
    saved_family = container.prefs.load_font_family()
    saved_size = container.prefs.load_font_size()
    effective_family = saved_family if saved_family else font_mgr.ui_font
    app.setFont(QFont(effective_family, saved_size))

    # Global Scroll Event Filter'ı yükle
    from presentation.utils.scroll_filter import WheelEventFilter
    app.installEventFilter(WheelEventFilter(app))

    # Modülleri registry'ye kaydet; MainWindow'dan önce çağrılmalıdır
    from presentation.modules import setup_modules  # noqa: PLC0415
    setup_modules(container)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
