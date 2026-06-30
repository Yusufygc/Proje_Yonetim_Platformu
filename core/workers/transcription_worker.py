"""
Sürekli mikrofon dinleme ve Vosk tabanlı konuşma tanıma iş parçacığı.

Worker tek seferlik değil; stop() çağrılana kadar ses döngüsünde kalır.
UI thread'i bloke etmemek için QThreadPool üzerinde çalışır.
"""
from __future__ import annotations

import json
import logging
import queue
import threading
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot

from core.exceptions.speech_exceptions import (
    MicrophoneUnavailableError,
    SpeechModelNotFoundError,
)

if TYPE_CHECKING:
    from services.speech.speech_to_text_service import SpeechToTextService

logger = logging.getLogger(__name__)


class TranscriptionSignals(QObject):
    """TranscriptionWorker → UI thread arası sinyal köprüsü."""

    started = Signal()
    partial = Signal(str)   # Ara (henüz tamamlanmamış) tanıma sonucu
    final = Signal(str)     # Tam cümle/ifade tanıma sonucu
    error = Signal(str)     # Kullanıcıya gösterilecek hata mesajı
    finished = Signal()


class TranscriptionWorker(QRunnable):
    """
    Mikrofon sesini yakalar ve Vosk ile metne çevirir.

    start() → ses açılır, tanıma başlar, final/partial sinyal atılır.
    stop()  → ses kapanır, kalan parça işlenir, finished sinyal atılır.
    """

    _active_workers: set[TranscriptionWorker] = set()

    def __init__(self, service: SpeechToTextService) -> None:
        super().__init__()
        self.setAutoDelete(False)
        self.signals = TranscriptionSignals()
        self._service = service
        self._stop_flag = threading.Event()
        self._audio_queue: queue.Queue[bytes] = queue.Queue()

    @Slot()
    def run(self) -> None:
        """Arka plan iş parçacığında çalışır; UI thread'i bloke etmez."""
        try:
            self._service.ensure_loaded()
            recognizer = self._service.create_recognizer()
            self._run_audio_loop(recognizer)
        except SpeechModelNotFoundError as exc:
            logger.error("STT model hatası: %s", exc)
            self.signals.error.emit(str(exc))
        except MicrophoneUnavailableError as exc:
            logger.error("Mikrofon hatası: %s", exc)
            self.signals.error.emit(str(exc))
        except Exception as exc:
            logger.exception("STT bilinmeyen hata")
            self.signals.error.emit(f"Sesli komut hatası: {exc}")
        finally:
            self.signals.finished.emit()
            TranscriptionWorker._active_workers.discard(self)

    def _run_audio_loop(self, recognizer: Any) -> None:
        """Ses akışını açar ve stop() çağrılana kadar tanıma döngüsünü yürütür."""
        try:
            import sounddevice as sd  # noqa: PLC0415
        except ImportError as exc:
            raise MicrophoneUnavailableError(
                "sounddevice kurulu değil. Çalıştırın: pip install sounddevice"
            ) from exc

        def _callback(indata: bytes, frames: int, time: Any, status: Any) -> None:
            if status:
                logger.warning("Ses akışı durumu: %s", status)
            self._audio_queue.put(bytes(indata))

        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=_callback,
            ):
                self.signals.started.emit()
                self._process_audio_queue(recognizer)
        except sd.PortAudioError as exc:
            raise MicrophoneUnavailableError(
                f"Mikrofon kullanılamıyor. Lütfen bağlantınızı kontrol edin. ({exc})"
            ) from exc

    def _process_audio_queue(self, recognizer: Any) -> None:
        """stop() set olana kadar ses verisi kuyruğunu işler."""
        while not self._stop_flag.is_set():
            try:
                data = self._audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            self._feed_recognizer(recognizer, data)

        # Döngü bitti; son parçacık varsa işle
        final = json.loads(recognizer.FinalResult())
        text: str = final.get("text", "").strip()
        if text:
            self.signals.final.emit(text)

    def _feed_recognizer(self, recognizer: Any, data: bytes) -> None:
        """Ses verisini tanıyıcıya gönderir ve sinyal atar."""
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text: str = result.get("text", "").strip()
            if text:
                self.signals.final.emit(text)
        else:
            partial = json.loads(recognizer.PartialResult())
            text = partial.get("partial", "").strip()
            if text:
                self.signals.partial.emit(text)

    def start(self) -> None:
        """Worker'i QThreadPool'a ekler ve GC'ye karşı referansı korur."""
        TranscriptionWorker._active_workers.add(self)
        QThreadPool.globalInstance().start(self)

    def stop(self) -> None:
        """Ses döngüsünü durdurma bayrağı set eder (thread-safe)."""
        self._stop_flag.set()
