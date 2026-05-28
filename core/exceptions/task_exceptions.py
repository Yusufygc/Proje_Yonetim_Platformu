"""
Görev iş kurallarına özgü hata sınıfları.
"""
from core.exceptions.base_exception import AppBaseException


class TaskValidationError(AppBaseException):
    """Görev verisi iş kurallarını ihlal ettiğinde fırlatılır."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="TASK_VALIDATION_ERROR")


class TaskHierarchyError(AppBaseException):
    """Görev hiyerarşisi kural ihlallerinde fırlatılır."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="TASK_HIERARCHY_ERROR")


class TaskNotFoundError(AppBaseException):
    """Belirtilen ID'ye sahip görev bulunamadığında fırlatılır."""

    def __init__(self, task_id: int) -> None:
        super().__init__(f"Görev bulunamadı (id={task_id})", code="TASK_NOT_FOUND")
