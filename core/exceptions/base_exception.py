"""Base exception classes for application-specific errors."""


class AppBaseException(Exception):
    """Base class for all application-specific errors."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(AppBaseException):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundError(AppBaseException):
    """Raised when an entity cannot be found."""

    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(f"{entity} bulunamadi (id={entity_id})", code="NOT_FOUND")


class DatabaseConnectionError(AppBaseException):
    """Raised when database startup, connection, or migration fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DATABASE_CONNECTION_ERROR")
