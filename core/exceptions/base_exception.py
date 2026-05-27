"""
Tüm uygulama hatalarının türetileceği temel istisna sınıfları.
"""


class AppBaseException(Exception):
    """Uygulamaya özgü tüm hataların türetildiği taban sınıf."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(AppBaseException):
    """Girdi doğrulama başarısız olduğunda fırlatılır."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundError(AppBaseException):
    """İstenen kayıt veritabanında bulunamadığında fırlatılır."""

    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(f"{entity} bulunamadı (id={entity_id})", code="NOT_FOUND")
