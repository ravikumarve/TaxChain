"""
Error handling utilities for TaxChain API.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response format for TaxChain API."""

    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.now().isoformat()


def create_error_response(
    error: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
):
    """Create a standardized error response."""
    error_response = ErrorResponse(error=error, message=message, details=details)

    return HTTPException(status_code=status_code, detail=error_response.model_dump())


def handle_database_error(exc, operation):
    logger.error(f"Database error during {operation}: {str(exc)}", exc_info=True)
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Database operation failed: {str(exc)}",
    )


def handle_external_api_error(exc, service):
    logger.error(f"External API error from {service}: {str(exc)}", exc_info=True)
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"{service} service is temporarily unavailable",
    )


def handle_permission_error():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to access this resource",
    )


def handle_not_found_error(resource):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found"
    )


def handle_general_error(exc, context):
    logger.error(f"Unexpected error in {context}: {str(exc)}", exc_info=True)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred",
    )


def log_request_info(user_id, endpoint, params, status_code):
    logger.info(
        f"Request: user_id={user_id}, endpoint={endpoint}, "
        f"params={params}, status={status_code}"
    )


def validate_financial_year_format(financial_year):
    if not financial_year or len(financial_year) != 7:
        return False

    try:
        if financial_year[4] != "-":
            return False

        start_year = int(financial_year[:4])
        end_suffix = financial_year[5:]

        if len(end_suffix) != 2 or not end_suffix.isdigit():
            return False

        expected_end_suffix = str(start_year + 1)[2:]
        return end_suffix == expected_end_suffix

    except (ValueError, IndexError):
        return False
