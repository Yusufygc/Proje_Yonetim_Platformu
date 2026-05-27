"""
Uygulama genelinde merkezi loglama altyapısı.
RotatingFileHandler ile 5 MB sınırında otomatik log rotasyonu sağlar.
"""
import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_file: Path, max_bytes: int, backup_count: int) -> None:
    """
    Root logger'ı dosya ve konsol çıktısıyla yapılandırır.

    Args:
        log_file: Log dosyasının tam yolu.
        max_bytes: Dosyanın ulaşabileceği maksimum boyut (bayt).
        backup_count: Saklanacak yedek log dosyası sayısı.
    """
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def install_global_exception_hook() -> None:
    """
    Yakalanmamış istisnaları sessizce kaybetmemek için sys.excepthook'u bağlar.
    PySide6 thread dışı çöküşlerini de loga düşürür.
    """
    logger = logging.getLogger("global_exception_hook")

    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: object,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical(
            "Yakalanmamış istisna:\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),  # type: ignore[arg-type]
        )

    sys.excepthook = handle_exception
