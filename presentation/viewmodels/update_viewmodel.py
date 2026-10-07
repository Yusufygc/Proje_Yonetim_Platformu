"""QML güncelleme penceresi ViewModel'i (UpdateViewModel)."""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from app import config
from app.di_container import DIContainer
from core.exceptions.update_exceptions import UpdateError
from services.update_service import UpdateInfo

logger = logging.getLogger(__name__)

# Kaynak koddan çalışırken (geliştirme) yayınlanmış sürümle kıyaslayıp popup göstermek anlamsız;
# yine de denemek için ortam değişkeniyle açılabilir.
_FORCE_CHECK_ENV = "PROJE_TAKIP_UPDATE_CHECK"


class UpdateViewModel(QObject):
    """Yeni sürüm denetimi, indirme ilerlemesi ve kurulum başlatma durumunu QML'e açar."""

    stateChanged = Signal()
    quitRequested = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._controller = container.update_controller
        self._event_bus = container.event_bus

        self._info: UpdateInfo | None = None
        self._is_open = False
        self._is_downloading = False
        self._progress = 0
        self._error = ""
        self._manual_check = False

        self._controller.update_found.connect(self._on_update_found)
        self._controller.up_to_date.connect(self._on_up_to_date)
        self._controller.check_failed.connect(self._on_check_failed)
        self._controller.download_progress.connect(self._on_progress)
        self._controller.download_finished.connect(self._on_download_finished)
        self._controller.download_failed.connect(self._on_download_failed)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(bool, notify=stateChanged)
    def isDialogOpen(self) -> bool:
        return self._is_open

    @Property(str, notify=stateChanged)
    def latestVersion(self) -> str:
        return self._info.version if self._info else ""

    @Property(str, notify=stateChanged)
    def releaseNotes(self) -> str:
        return self._info.notes if self._info else ""

    @Property(bool, notify=stateChanged)
    def isDownloading(self) -> bool:
        return self._is_downloading

    @Property(int, notify=stateChanged)
    def downloadProgress(self) -> int:
        return self._progress

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error

    @Property(str, constant=True)
    def currentVersion(self) -> str:
        return config.APP_VERSION

    # ── Slots ───────────────────────────────────────────────────────────────

    @Slot()
    def checkOnStartup(self) -> None:
        """Açılışta sessizce denetler; yalnızca paketlenmiş uygulamada (ya da env ile) çalışır."""
        if not (getattr(sys, "frozen", False) or os.environ.get(_FORCE_CHECK_ENV) == "1"):
            return
        self._manual_check = False
        self._controller.check()

    @Slot()
    def checkForUpdates(self) -> None:
        """Kullanıcı isteğiyle denetler; sonuç ne olursa olsun bildirim gösterir."""
        self._manual_check = True
        self._controller.check()

    @Slot()
    def startUpdate(self) -> None:
        if self._info is None or self._is_downloading:
            return
        self._error = ""
        self._progress = 0
        self._is_downloading = True
        self.stateChanged.emit()
        self._controller.download(self._info)

    @Slot()
    def dismiss(self) -> None:
        if self._is_downloading:
            return
        self._is_open = False
        self.stateChanged.emit()

    # ── Controller geri çağrıları ───────────────────────────────────────────

    def _on_update_found(self, info: UpdateInfo) -> None:
        self._info = info
        self._error = ""
        self._is_open = True
        self.stateChanged.emit()

    def _on_up_to_date(self) -> None:
        if self._manual_check:
            self._event_bus.publish("toast.show", message="Uygulama güncel", type_="success")  # l10n: data

    def _on_check_failed(self, message: str) -> None:
        # Açılışta ağ yoksa kullanıcıyı rahatsız etme; yalnızca elle istenen denetimde bildir.
        if self._manual_check:
            self._event_bus.publish("toast.show", message="Güncelleme denetlenemedi", type_="danger")  # l10n: data

    def _on_progress(self, percent: int) -> None:
        self._progress = percent
        self.stateChanged.emit()

    def _on_download_finished(self, installer_path: str) -> None:
        try:
            self._controller.launch(installer_path)
        except UpdateError as exc:
            self._on_download_failed(str(exc))
            return
        self.quitRequested.emit()

    def _on_download_failed(self, message: str) -> None:
        logger.warning("Update download failed: %s", message)
        self._is_downloading = False
        self._error = message
        self.stateChanged.emit()
