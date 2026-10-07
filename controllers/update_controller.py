"""
UpdateController - güncelleme denetimi ve indirmesini arka planda yürütür, sonucu sinyallerle bildirir.
"""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from core.workers.worker import Worker
from services.update_service import ProgressCallback, UpdateInfo, UpdateService

logger = logging.getLogger(__name__)


class UpdateController(QObject):
    update_found = Signal(object)  # UpdateInfo
    up_to_date = Signal()
    check_failed = Signal(str)
    download_progress = Signal(int)
    download_finished = Signal(str)  # indirilen kurulum dosyasının yolu
    download_failed = Signal(str)

    def __init__(self, service: UpdateService) -> None:
        super().__init__()
        self._service = service

    def check(self) -> None:
        worker = Worker(self._service.check_for_update)
        worker.signals.result.connect(self._on_check_result)
        worker.signals.error.connect(self._on_check_error)
        worker.start()

    def download(self, info: UpdateInfo) -> None:
        def _download(progress_callback: ProgressCallback) -> str:
            return str(self._service.download_installer(info, progress_callback))

        worker = Worker(_download)
        worker.signals.progress.connect(self.download_progress.emit)
        worker.signals.result.connect(self.download_finished.emit)
        worker.signals.error.connect(self.download_failed.emit)
        worker.start()

    def launch(self, installer_path: str) -> None:
        self._service.launch_installer(Path(installer_path))

    def _on_check_result(self, info: UpdateInfo | None) -> None:
        if info is None:
            self.up_to_date.emit()
            return
        self.update_found.emit(info)

    def _on_check_error(self, message: str) -> None:
        logger.warning("Update check failed: %s", message)
        self.check_failed.emit(message)
