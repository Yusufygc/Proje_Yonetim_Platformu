"""Sesli komut (STT) bileşenine özgü istisna sınıfları."""

from core.exceptions.base_exception import AppBaseException


class SpeechRecognitionError(AppBaseException):
    """Sesli komut sisteminde genel hata."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="SPEECH_ERROR")


class SpeechModelNotFoundError(SpeechRecognitionError):
    """Vosk model dizini bulunamadı veya geçersiz."""

    def __init__(self, message: str) -> None:
        # AppBaseException.__init__ çağrısı üst sınıf zinciri üzerinden yapılır;
        # code farklılaştırılır ki log filtrelemesi kolaylaşsın.
        AppBaseException.__init__(self, message, code="SPEECH_MODEL_NOT_FOUND")


class MicrophoneUnavailableError(SpeechRecognitionError):
    """Ses giriş cihazı açılamadı veya kullanılamıyor."""

    def __init__(self, message: str) -> None:
        AppBaseException.__init__(self, message, code="MICROPHONE_UNAVAILABLE")
