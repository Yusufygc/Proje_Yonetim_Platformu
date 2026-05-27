"""
Merkezi Loglama ve Global Hata Yönetimi modülü.
"""
import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from typing import Any

from PySide6.QtWidgets import QMessageBox

import config

def setup_logging() -> None:
    """RotatingFileHandler ile loglama altyapısını kurar."""
    config.ensure_data_dirs()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Root logger tüm mesajları alsın

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )

    # Konsol Çıktısı (Sadece INFO ve üstü)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Dosya Çıktısı (Rotating, DEBUG dahil)
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info("Loglama altyapısı başarıyla başlatıldı.")


def global_exception_hook(exc_type: type, exc_value: BaseException, exc_traceback: Any) -> None:
    """Yakalanamayan hataları loglar ve kullanıcıya hata mesajı gösterir."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Hatayı logla
    logger = logging.getLogger("global_exception_hook")
    logger.critical("Yakalanamayan istisna:\n%s", "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

    # Arayüz açık ise hata mesajı göster
    try:
        from PySide6.QtWidgets import QApplication
        if QApplication.instance():
            QMessageBox.critical(
                None,
                "Beklenmeyen Hata",
                f"Uygulamada beklenmeyen bir hata oluştu:\n\n{exc_value}\n\nDetaylar log dosyasına kaydedildi.",
            )
    except Exception:
        pass


def setup_global_exception_handler() -> None:
    """Global hata yakalayıcıyı etkinleştirir."""
    sys.excepthook = global_exception_hook
