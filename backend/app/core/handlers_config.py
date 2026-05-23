"""
Global exception handlers for the FastAPI application.
Provides consistent error responses across all endpoints.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.core.exceptions import AppException
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.

    Returns error response with proper status code and details.
    """
    logger.warning(
        f"AppException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Returns validation error details.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {"errors": errors},
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected exceptions.

    Returns generic error response without exposing internal details.
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=exc,
        extra={
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {} if hasattr(exc, "debug") is False else {"debug": str(exc)},
        },
    )
