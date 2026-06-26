"""Compatibility wrapper for central logging APIs."""
from __future__ import annotations

from types import TracebackType

from app import config
from core.managers.log_manager import install_global_exception_hook
from core.managers.log_manager import setup_logging as _setup_logging


def setup_logging() -> None:
    config.ensure_data_dirs()
    _setup_logging(config.LOG_FILE, config.LOG_MAX_BYTES, config.LOG_BACKUP_COUNT)


def global_exception_hook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    install_global_exception_hook(show_dialog=True)
    import sys

    sys.excepthook(exc_type, exc_value, exc_traceback)


def setup_global_exception_handler() -> None:
    install_global_exception_hook(show_dialog=True)
