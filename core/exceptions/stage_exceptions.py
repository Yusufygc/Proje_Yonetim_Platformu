"""Aşama iş kurallarına özgü hata sınıfları."""
from core.exceptions.base_exception import AppBaseException


class StageNotFoundError(AppBaseException):
    """Belirtilen ID'ye sahip aşama bulunamadığında fırlatılır."""

    def __init__(self, stage_id: int) -> None:
        super().__init__(f"Aşama bulunamadı (id={stage_id})", code="STAGE_NOT_FOUND")


class StageValidationError(AppBaseException):
    """Aşama iş kuralları ihlal edildiğinde fırlatılır."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="STAGE_VALIDATION_ERROR")
