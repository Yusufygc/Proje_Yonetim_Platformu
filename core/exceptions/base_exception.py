"""Base exception classes for application-specific errors."""


class AppBaseException(Exception):
    """Base class for all application-specific errors."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class DatabaseConnectionError(AppBaseException):
    """Raised when database startup, connection, or migration fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="DATABASE_CONNECTION_ERROR")
