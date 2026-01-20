"""Pydantic models for API requests and responses."""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """API Error Codes"""

    INVALID_INPUT = "INVALID_INPUT"
    NO_DATA_PROVIDED = "NO_DATA_PROVIDED"
    INVALID_JSON = "INVALID_JSON"
    DATA_TOO_LARGE = "DATA_TOO_LARGE"
    NGUI_AGENT_ERROR = "NGUI_AGENT_ERROR"
    NO_COMPONENTS_GENERATED = "NO_COMPONENTS_GENERATED"
    COMPONENT_PARSING_ERROR = "COMPONENT_PARSING_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    LLM_CONNECTION_ERROR = "LLM_CONNECTION_ERROR"
    DATA_FILTER_ERROR = "DATA_FILTER_ERROR"


class GenerateRequest(BaseModel):
    """Request model for generate endpoint."""

    prompt: str
    data: Optional[Any] = Field(
        default=None,
        description="Optional data payload in any format (JSON, CSV, plain text, XML, etc.). When provided, uses this data directly.",
    )
    data_type: Optional[str] = Field(
        default=None,
        description="Optional identifier for the provided data (e.g., 'movies.detail', 'cost.analysis').",
    )
    skip_filtering: bool = Field(
        default=False,
        description="Skip intelligent data filtering if True",
    )


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error_code: ErrorCode
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None


class DataFilterResult(BaseModel):
    """Result from generic data filtering agent."""

    query_type: str = Field(
        description="Type of query: 'specific' (looking for specific item(s)) or 'all' (wanting all items)"
    )
    filter_instructions: str = Field(
        description="Instructions on how to filter the data"
    )
    should_filter: bool = Field(description="Whether filtering should be applied")
    explanation: str = Field(
        description="Brief explanation of what was understood from the query"
    )
