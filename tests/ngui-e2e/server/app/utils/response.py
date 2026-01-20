"""Utilities for creating API responses."""

from typing import Optional

from app.models import ErrorCode, ErrorResponse
from fastapi.responses import JSONResponse


def create_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int,
    details: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> JSONResponse:
    """Helper function to create standardized error responses with proper HTTP status codes."""
    error_response = ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        suggestion=suggestion,
    )

    return JSONResponse(
        status_code=status_code, content=error_response.model_dump(exclude_none=True)
    )
