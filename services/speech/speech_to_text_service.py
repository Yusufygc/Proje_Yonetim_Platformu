"""
Vosk tabanlı, çevrimdışı Türkçe konuşma-metin dönüştürme servisi.

Model, ilk kullanımda (ensure_loaded çağrısında) yüklenir; boot'ta yüklenmez.
Ağır işlem olduğu için ensure_loaded() her zaman bir Worker içinden çağrılmalıdır.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from core.exceptions.speech_exceptions import (
    SpeechModelNotFoundError,
)

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Vosk modelini yönetir ve KaldiRecognizer üretir.

    Tek sorumluluk: model yaşam döngüsü. Ses yakalamak bu sınıfın görevi değil;
    TranscriptionWorker bu servisi tüketerek ses döngüsünü yönetir.
    """

    def __init__(self, model_dir: Path) -> None:
        self._model_dir = model_dir
        self._model: Any | None = None
        self._load_lock = threading.Lock()

    def ensure_loaded(self) -> None:
        """
        Modeli belleğe yükler (idempotent, thread-safe).

        Klasör yoksa SpeechModelNotFoundError fırlatır.
        Bu metod ağır işlem içerdiğinden UI thread dışında çağrılmalıdır.
        """
        with self._load_lock:
            if self._model is not None:
                return
            self._load_model()

    def _load_model(self) -> None:
        """Vosk modelini diskten yükler; ensure_loaded kilit altında çağırır."""
        if not self._model_dir.exists():
            raise SpeechModelNotFoundError(
                f"Vosk Türkçe modeli bulunamadı: {self._model_dir}\n"
                "İndirme: https://alphacephei.com/vosk/models → vosk-model-small-tr-0.3\n"
                "Modeli resources/models/ dizinine çıkarın."
            )
        try:
            import vosk  # noqa: PLC0415
        except ImportError as exc:
            raise SpeechModelNotFoundError(
                "Vosk kütüphanesi kurulu değil. Çalıştırın: pip install vosk"
            ) from exc

        import sys  # noqa: PLC0415
        model_path_str = str(self._model_dir)
        if sys.platform == "win32":
            try:
                import ctypes  # noqa: PLC0415
                from ctypes import wintypes  # noqa: PLC0415
                _GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
                _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
                _GetShortPathNameW.restype = wintypes.DWORD

                buf_size = 256
                while True:
                    buf = ctypes.create_unicode_buffer(buf_size)
                    needed = _GetShortPathNameW(model_path_str, buf, buf_size)
                    if needed == 0:
                        break
                    if needed < buf_size:
                        model_path_str = buf.value
                        break
                    buf_size = needed
            except Exception as exc:
                logger.warning("Kısa dosya yolu alınamadı: %s", exc)

        logger.info("Vosk Türkçe modeli yükleniyor: %s (Kısa Yol: %s)", self._model_dir, model_path_str)
        vosk.SetLogLevel(-1)  # Vosk'un kendi dahili log çıktısını kapat
        self._model = vosk.Model(model_path_str)
        logger.info("Vosk modeli yüklendi.")


    def create_recognizer(self, sample_rate: int = 16000) -> Any:
        """
        KaldiRecognizer oluşturur.

        ensure_loaded() çağrılmadan kullanılırsa SpeechModelNotFoundError fırlatır.
        """
        if self._model is None:
            raise SpeechModelNotFoundError(
                "Model yüklenmemiş; create_recognizer() öncesinde ensure_loaded() çağrılmalı."
            )
        try:
            import vosk  # noqa: PLC0415
        except ImportError as exc:
            raise SpeechModelNotFoundError("Vosk kurulu değil.") from exc

        recognizer = vosk.KaldiRecognizer(self._model, float(sample_rate))
        recognizer.SetWords(False)
        return recognizer
