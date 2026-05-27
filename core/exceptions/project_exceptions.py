"""
Proje iş kurallarına özgü hata sınıfları.
"""
from core.exceptions.base_exception import AppBaseException


class ProjectValidationError(AppBaseException):
    """Proje verisi iş kurallarını ihlal ettiğinde fırlatılır."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="PROJECT_VALIDATION_ERROR")


class ProjectNotFoundError(AppBaseException):
    """Belirtilen ID'ye sahip proje bulunamadığında fırlatılır."""

    def __init__(self, project_id: int) -> None:
        super().__init__(f"Proje bulunamadı (id={project_id})", code="PROJECT_NOT_FOUND")
