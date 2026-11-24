"""Uygulama güncelleme akışına özgü istisna sınıfları."""
from __future__ import annotations

from core.exceptions.base_exception import AppBaseException


class UpdateError(AppBaseException):
    """Güncelleme denetimi, indirme veya kurulum başlatma hatası."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="UPDATE_ERROR")

    def __str__(self) -> str:
        # Mesaj kullanıcıya olduğu gibi gösterilir; hata kodu öneki arayüzde anlamsız.
        return self.message


class InstallerBlockedError(UpdateError):
    """Windows kurulum dosyasını başlatmayı engelledi (Akıllı Uygulama Denetimi / grup ilkesi)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
