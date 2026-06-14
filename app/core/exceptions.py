"""Custom application exceptions."""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""


class ValidationError(AppException):
    """Raised when business validation fails."""


class UnauthorizedError(AppException):
    """Raised when authentication is required or invalid."""


class UserAlreadyExistsError(AppException):
    """Raised when registering with an email that already exists."""


class LoginRequiredRedirect(Exception):
    """Raised to redirect unauthenticated users to the login page."""
