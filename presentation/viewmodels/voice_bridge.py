"""QML Sesli Metin Tanıma Köprüsü (VoiceBridge)."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from presentation.utils.i18n import tr

if TYPE_CHECKING:
    from app.di_container import DIContainer
    from core.workers.transcription_worker import TranscriptionWorker

logger = logging.getLogger(__name__)


class VoiceBridge(QObject):
    """QML kontrolleri için Vosk ses tanıma köprüsü."""

    listeningChanged = Signal(bool)
    textTranscribed = Signal(str)
    partialChanged = Signal(str)
    activeOwnerChanged = Signal(str)

    def __init__(self, container: DIContainer, parent: Optional[QObject] = None) -> None:
        super().__init__(parent=parent)
        self._container = container
        self._event_bus = container.event_bus
        self._worker: Optional[TranscriptionWorker] = None
        self._is_listening: bool = False
        self._partial_text: str = ""
        self._active_owner: str = ""

    @Property(bool, notify=listeningChanged)
    def isListening(self) -> bool:
        return self._is_listening

    @Property(str, notify=partialChanged)
    def partialText(self) -> str:
        return self._partial_text

    @Property(str, notify=activeOwnerChanged)
    def activeOwner(self) -> str:
        """Dinlemeyi başlatan mikrofon düğmesinin kimliği; metni yalnızca o düğme alır."""
        return self._active_owner

    @Slot(str)
    def toggleListeningFor(self, owner: str) -> None:
        """Dinleme açıksa durdurur; kapalıysa `owner` düğmesi adına başlatır.

        Sonuç sinyali tüm mikrofon düğmelerine ulaşır; sahip kimliği olmadan her açık alan
        (arama kutusu dahil) aynı metni yazıyordu.
        """
        if self._is_listening:
            self.stopListening()
            return
        self._active_owner = owner
        self.activeOwnerChanged.emit(owner)
        self.startListening()

    @Slot()
    def startListening(self) -> None:
        if self._is_listening:
            return
        try:
            from core.workers.transcription_worker import TranscriptionWorker  # noqa: PLC0415
            service = self._container.speech_service
            self._worker = TranscriptionWorker(service)
            self._worker.signals.final.connect(self._on_final)
            self._worker.signals.partial.connect(self._on_partial)
            self._worker.signals.error.connect(self._on_error)
            self._worker.signals.finished.connect(self._on_finished)
            self._worker.start()
            self._is_listening = True
            self.listeningChanged.emit(True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Ses dinleme başlatılamadı: %s", exc)  # l10n: log
            self._on_error(str(exc))

    @Slot()
    def stopListening(self) -> None:
        if not self._is_listening or not self._worker:
            return
        self._worker.stop()
        self._is_listening = False
        self.listeningChanged.emit(False)

    def _on_final(self, text: str) -> None:
        cleaned = text.strip()
        if cleaned:
            self.textTranscribed.emit(cleaned)

    def _on_partial(self, text: str) -> None:
        self._partial_text = text
        self.partialChanged.emit(text)

    def _on_finished(self) -> None:
        self._is_listening = False
        self._worker = None
        self.listeningChanged.emit(False)

    def _on_error(self, message: str) -> None:
        self._is_listening = False
        self._worker = None
        self.listeningChanged.emit(False)
        if self._event_bus:
            self._event_bus.publish(
                "toast.show",
                message=tr(
                    "voice_error_toast",
                    "Ses tanıma hatası: {msg}",
                ).format(msg=message),
                type_="error",
            )
