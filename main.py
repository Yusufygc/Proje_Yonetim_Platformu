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

    # Fontları yükle ve uygula
    from PySide6.QtGui import QFont
    font_mgr = container.fonts
    font_mgr.load_all()
    if font_mgr.loaded_families:
        app.setFont(QFont(font_mgr.loaded_families[0], 10))
    else:
        app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
