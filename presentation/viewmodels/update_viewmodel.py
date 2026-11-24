"""QML güncelleme penceresi ViewModel'i: denetim, indirme, kurulum ve SAC engeli bekleme/yeniden deneme."""
from __future__ import annotations

import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from app import config
from core.exceptions.update_exceptions import InstallerBlockedError, UpdateError
from presentation.utils.i18n import tr
from services.update_service import UpdateInfo

if TYPE_CHECKING:
    from app.di_container import DIContainer
    from controllers.update_controller import UpdateController

logger = logging.getLogger(__name__)

RETRY_INTERVAL_MS = 15_000
MAX_RETRIES = 40
QUIT_DELAY_MS = 1_000

STATE_IDLE = "idle"
STATE_CHECKING = "checking"
STATE_UP_TO_DATE = "uptodate"
STATE_AVAILABLE = "available"
STATE_DOWNLOADING = "downloading"
STATE_INSTALLING = "installing"
STATE_WAITING = "waiting"
STATE_BLOCKED = "blocked"
STATE_ERROR = "error"


class UpdateViewModel(QObject):
    """Yeni sürüm denetimi, SHA-256 doğrulamalı indirme ve SAC engel kurtarma akışını QML'e açar."""

    stateChanged = Signal()
    quitRequested = Signal()

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._controller: UpdateController = container.update_controller
        self._info: UpdateInfo | None = None
        self._installer: Path | None = None
        self._state = STATE_IDLE
        self._is_open = False
        self._progress = 0
        self._status = ""
        self._attempt = 0
        self._silent = False
        self._retry_timer = QTimer(self)
        self._retry_timer.setInterval(RETRY_INTERVAL_MS)
        self._retry_timer.timeout.connect(self._retry_launch)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._controller.update_found.connect(self._on_update_found)
        self._controller.up_to_date.connect(self._on_up_to_date)
        self._controller.check_failed.connect(self._on_check_failed)
        self._controller.download_progress.connect(self._on_progress)
        self._controller.download_finished.connect(self._on_download_finished)
        self._controller.download_failed.connect(self._on_download_failed)

    # ── Properties ──────────────────────────────────────────────────────────

    @Property(str, notify=stateChanged)
    def state(self) -> str:
        """Güncelleme akışının mevcut durum adı."""
        return self._state

    @Property(bool, notify=stateChanged)
    def isDialogOpen(self) -> bool:
        """Güncelleme penceresinin görünürlük durumu."""
        return self._is_open

    @Property(str, notify=stateChanged)
    def latestVersion(self) -> str:
        """Bulunan yeni sürüm numarası."""
        return self._info.version if self._info else ""

    @Property(str, constant=True)
    def currentVersion(self) -> str:
        """Yüklü uygulama sürümü."""
        return config.APP_VERSION

    @Property(str, notify=stateChanged)
    def releaseNotes(self) -> str:
        """Yeni sürümün düz metin sürüm notları."""
        return self._info.notes if self._info else ""

    @Property(int, notify=stateChanged)
    def downloadProgress(self) -> int:
        """İndirme yüzdesi (0–100)."""
        return self._progress

    @Property(str, notify=stateChanged)
    def statusMessage(self) -> str:
        """Kullanıcıya gösterilen durum, bekleme veya hata iletisi."""
        return self._status

    @Property(bool, notify=stateChanged)
    def checkOnStartup(self) -> bool:
        """Açılışta otomatik güncelleme kontrolü tercihi."""
        return self._controller.update_check_allowed()

    # ── Slots ───────────────────────────────────────────────────────────────

    @Slot()
    @Slot(bool)
    def checkForUpdates(self, silent: bool = False) -> None:
        """Yeni sürüm denetler; `silent=True` açılışta, `False` Ayarlar üzerinden çağrılır."""
        if self._state in (STATE_CHECKING, STATE_DOWNLOADING, STATE_INSTALLING):
            return
        if silent and not self._controller.update_check_allowed():
            return
        self._silent = silent
        if not silent:
            self._is_open = True
        self._set_state(STATE_CHECKING, tr("update_checking", "Güncellemeler denetleniyor..."))
        self._controller.check(respect_skipped=silent)

    @Slot()
    def startUpdate(self) -> None:
        """Bulunan güncellemenin indirme ve kurulum akışını başlatır."""
        if self._info is None or self._state in (STATE_CHECKING, STATE_DOWNLOADING, STATE_INSTALLING):
            return
        self._progress = 0
        msg = tr(
            "update_downloading_version",
            "v{version} indiriliyor... Kurulum sırasında uygulama kapanıp yeniden açılır.",
        ).format(version=self._info.version)
        self._set_state(STATE_DOWNLOADING, msg)
        self._controller.download(self._info)

    @Slot()
    def dismiss(self) -> None:
        """İndirme ve kurulum dışında güncelleme penceresini kapatır."""
        if self._state in (STATE_CHECKING, STATE_DOWNLOADING, STATE_INSTALLING):
            return
        self._retry_timer.stop()
        self._is_open = False
        if self._state != STATE_AVAILABLE:
            self._state = STATE_IDLE
            self._status = ""
        self.stateChanged.emit()

    @Slot()
    def stopWaitingForBlock(self) -> None:
        """SAC engel beklemesini durdurup dosyayı Gezgin'de seçili gösterir."""
        self._give_up_waiting()

    @Slot()
    def skipVersion(self) -> None:
        """Mevcut yeni sürümü atlanan olarak işaretleyip pencereyi kapatır."""
        if self._info is not None:
            self._controller.skip_version(self._info.version)
        self.dismiss()

    @Slot(bool)
    def setCheckOnStartup(self, enabled: bool) -> None:
        """Açılışta otomatik güncelleme denetimi tercihini kaydeder."""
        self._controller.set_check_on_startup(bool(enabled))
        self.stateChanged.emit()

    @Slot()
    def openReleasePage(self) -> None:
        """GitHub Releases sayfasını varsayılan tarayıcıda açar."""
        url = self._info.html_url if self._info and self._info.html_url else self._controller.release_page_url()
        webbrowser.open(url)

    # ── Dahili Yardımcılar ──────────────────────────────────────────────────

    def _set_state(self, state: str, message: str = "") -> None:
        self._state = state
        self._status = message
        self.stateChanged.emit()

    def _on_update_found(self, info: UpdateInfo) -> None:
        self._info = info
        self._is_open = True
        self._set_state(STATE_AVAILABLE, "")

    def _on_up_to_date(self) -> None:
        if self._silent:
            self._set_state(STATE_IDLE, "")
            return
        msg = tr("update_up_to_date", "Güncelsiniz (sürüm v{version}).").format(version=config.APP_VERSION)
        self._set_state(STATE_UP_TO_DATE, msg)

    def _on_check_failed(self, message: str) -> None:
        if self._silent:
            logger.info("Startup update check skipped silently: %s", message)
            self._set_state(STATE_IDLE, "")
            return
        msg = tr("update_check_failed", "Denetlenemedi: {error}").format(error=message)
        self._set_state(STATE_ERROR, msg)

    def _on_progress(self, percent: int) -> None:
        self._progress = percent
        self.stateChanged.emit()

    def _on_download_finished(self, installer_path: str) -> None:
        self._installer = Path(installer_path)
        self._attempt = 0
        self._launch_installer()

    def _on_download_failed(self, message: str) -> None:
        logger.warning("Update download failed: %s", message)
        msg = tr("update_download_failed", "İndirme başarısız: {error}").format(error=message)
        self._set_state(STATE_ERROR, msg)

    def _launch_installer(self) -> None:
        if self._installer is None:
            return
        self._set_state(STATE_INSTALLING, tr("update_installing", "Kurulum başlatılıyor..."))
        try:
            self._controller.launch(str(self._installer))
        except InstallerBlockedError:
            self._handle_installer_blocked()
            return
        except UpdateError as exc:
            msg = tr("update_install_failed", "Kurulum başlatılamadı: {error}").format(error=str(exc))
            self._set_state(STATE_ERROR, msg)
            return
        self._retry_timer.stop()
        self._set_state(
            STATE_INSTALLING,
            tr("update_install_started", "Kurulum başladı; uygulama kapanıyor ve yeni sürüm kendiliğinden açılacak."),
        )
        QTimer.singleShot(QUIT_DELAY_MS, self.quitRequested.emit)

    def _handle_installer_blocked(self) -> None:
        self._attempt += 1
        if self._attempt > MAX_RETRIES:
            self._give_up_waiting()
            return
        msg = tr(
            "update_waiting_block",
            "Windows kurulum dosyasını şimdilik engelledi; bekleniyor ({attempt}/{max_attempts}). "
            "Engel kalkınca kurulum kendiliğinden başlayacak.",
        ).format(attempt=self._attempt, max_attempts=MAX_RETRIES)
        self._set_state(STATE_WAITING, msg)
        self._retry_timer.start()

    def _retry_launch(self) -> None:
        if self._state == STATE_WAITING:
            self._launch_installer()

    def _give_up_waiting(self) -> None:
        self._retry_timer.stop()
        self._reveal_installer()
        self._set_state(
            STATE_BLOCKED,
            tr(
                "update_blocked_manual",
                "Windows kurulum dosyasını şimdilik engelledi. Dosya Gezgin'de seçili; çift tıklayarak kurabilirsiniz, "
                "olmazsa birkaç dakika sonra yeniden deneyin.",
            ),
        )

    def _reveal_installer(self) -> None:
        if self._installer is None or not self._installer.is_file():
            return
        try:
            subprocess.Popen(["explorer.exe", f"/select,{self._installer}"])  # noqa: S603, S607
        except OSError as exc:
            logger.warning("Could not open Windows Explorer: %s", exc)
