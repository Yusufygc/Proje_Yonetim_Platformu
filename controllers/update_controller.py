"""UpdateController - güncelleme denetimi, indirme ve kurulum akışını servis üzerinden yürütür."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from core.workers.worker import Worker
from services.update_service import ProgressCallback, UpdateInfo, UpdateService

logger = logging.getLogger(__name__)


class UpdateController(QObject):
    """ViewModel ile `UpdateService` arasındaki ince koordinasyon köprüsü."""

    update_found = Signal(object)  # UpdateInfo
    up_to_date = Signal()
    check_failed = Signal(str)
    download_progress = Signal(int)
    download_finished = Signal(str)
    download_failed = Signal(str)

    def __init__(self, service: UpdateService) -> None:
        super().__init__()
        self._service = service

    def check(self, respect_skipped: bool = False) -> None:
        """Arka planda yeni sürüm denetimi başlatır."""
        worker = Worker(lambda: self._service.check_for_update(respect_skipped=respect_skipped))
        worker.signals.result.connect(self._on_check_result)
        worker.signals.error.connect(self._on_check_error)
        worker.start()

    def download(self, info: UpdateInfo) -> None:
        """Arka planda SHA-256 doğrulamalı kurulum dosyasını indirir."""
        def _download(progress_callback: ProgressCallback) -> str:
            return str(self._service.download_installer(info, progress_callback))

        worker = Worker(_download)
        worker.signals.progress.connect(self.download_progress.emit)
        worker.signals.result.connect(self.download_finished.emit)
        worker.signals.error.connect(self.download_failed.emit)
        worker.start()

    def launch(self, installer_path: str) -> None:
        """Kurulum dosyasını bağımsız süreç olarak başlatır; SAC engelinde InstallerBlockedError fırlatır."""
        self._service.launch_installer(Path(installer_path))

    def update_check_allowed(self) -> bool:
        """Açılışta otomatik denetim tercihinin ve ortam bayrağının açık olup olmadığını döndürür."""
        return self._service.update_check_allowed()

    def set_check_on_startup(self, enabled: bool) -> None:
        """Açılış denetim tercihini kaydeder."""
        self._service.set_check_on_startup(enabled)

    def skip_version(self, version: str) -> None:
        """Belirtilen sürümü atlanmış olarak kaydeder."""
        self._service.skip_version(version)

    def release_page_url(self) -> str:
        """GitHub Releases sayfasının URL'sini döndürür."""
        return self._service.release_page_url()

    def _on_check_result(self, info: UpdateInfo | None) -> None:
        if info is None:
            self.up_to_date.emit()
            return
        self.update_found.emit(info)

    def _on_check_error(self, message: str) -> None:
        logger.warning("Update check failed: %s", message)
        self.check_failed.emit(message)
