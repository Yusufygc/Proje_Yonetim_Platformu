"""Central logging and global exception handling."""
from __future__ import annotations

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

_FILE_HANDLER_MARKER = "_proje_takip_file_handler"
_CONSOLE_HANDLER_MARKER = "_proje_takip_console_handler"


def setup_logging(log_file: Path, max_bytes: int, backup_count: int) -> None:
    """Configure root logging once with rotating file and console handlers."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    existing_file = _find_marked_handler(root_logger, _FILE_HANDLER_MARKER)
    if existing_file is None:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        setattr(file_handler, _FILE_HANDLER_MARKER, True)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        existing_file.setFormatter(formatter)
        existing_file.setLevel(logging.DEBUG)

    existing_console = _find_marked_handler(root_logger, _CONSOLE_HANDLER_MARKER)
    if existing_console is None:
        console_handler = logging.StreamHandler(sys.stdout)
        setattr(console_handler, _CONSOLE_HANDLER_MARKER, True)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    else:
        existing_console.setFormatter(formatter)
        existing_console.setLevel(logging.WARNING)


def install_global_exception_hook(show_dialog: bool = True) -> None:
    """Install an exception hook that logs and optionally shows a user-facing dialog."""

    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger = logging.getLogger("global_exception_hook")
        logger.critical(
            "Unhandled exception:\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
        )
        if show_dialog:
            _show_unhandled_exception_dialog(exc_value)

    sys.excepthook = handle_exception


def _show_unhandled_exception_dialog(exc_value: BaseException) -> None:
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        if QApplication.instance() is None:
            return
        QMessageBox.critical(
            None,
            "Beklenmeyen Hata",
            f"Uygulamada beklenmeyen bir hata oluştu:\n\n{exc_value}\n\nDetaylar log dosyasına kaydedildi.",
        )
    except Exception:
        logging.getLogger("global_exception_hook").exception("Unexpected-error dialog could not be shown.")


def _find_marked_handler(logger: logging.Logger, marker: str) -> logging.Handler | None:
    for handler in logger.handlers:
        if getattr(handler, marker, False):
            return handler
    return None
