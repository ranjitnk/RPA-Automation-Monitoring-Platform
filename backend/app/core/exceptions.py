"""Application exceptions and HTTP mapping."""

from typing import Any


class AppException(Exception):
    """Base domain exception."""

    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code or self.code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class UnauthorizedError(AppException):
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"


class ConflictError(AppException):
    status_code = 409
    code = "CONFLICT"


class ValidationError(AppException):
    status_code = 422
    code = "VALIDATION_ERROR"


class ExternalServiceError(AppException):
    status_code = 502
    code = "EXTERNAL_SERVICE_ERROR"
