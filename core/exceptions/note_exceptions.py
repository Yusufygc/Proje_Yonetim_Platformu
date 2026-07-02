"""Not modülüne özgü uygulama istisnaları."""
from core.exceptions.base_exception import AppBaseException


class NoteNotFoundError(AppBaseException):
    def __init__(self, note_id: int) -> None:
        super().__init__(f"Not bulunamadı (id={note_id})", code="NOTE_NOT_FOUND")


class NoteValidationError(AppBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="NOTE_VALIDATION_ERROR")
