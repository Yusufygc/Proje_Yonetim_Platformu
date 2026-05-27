"""
Uygulama giriş noktası.
DI Container'ı kurar, global exception hook'u bağlar ve pencereyi açar.
"""
import sys
from pathlib import Path

# Proje kökünü import path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

import config  # noqa: E402 — sys.path ayarından sonra import edilmeli
from di_container import DIContainer  # noqa: E402


def main() -> None:
    """Uygulamayı başlatan ana fonksiyon."""
    # DI Container tüm altyapıyı (log, DB, tema, font) başlatır
    container = DIContainer.instance()
    container.bootstrap()

    # PySide6'yı burada import ediyoruz; QApplication log kurulumundan sonra oluşmalı
    from PySide6.QtWidgets import QApplication  # noqa: PLC0415

    from presentation.shell.main_window import MainWindow  # noqa: PLC0415

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setOrganizationName(config.APP_ORGANIZATION)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
