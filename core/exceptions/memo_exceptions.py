"""Memo modülüne özgü uygulama istisnaları."""
from core.exceptions.base_exception import AppBaseException


class MemoNotFoundError(AppBaseException):
    def __init__(self, memo_id: int) -> None:
        super().__init__(f"Memo bulunamadı (id={memo_id})", code="MEMO_NOT_FOUND")


class MemoValidationError(AppBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="MEMO_VALIDATION_ERROR")
