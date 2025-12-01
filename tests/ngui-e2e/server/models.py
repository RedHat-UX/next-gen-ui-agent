"""Pydantic models for API requests."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str
    strategy: Optional[str] = Field(
        default="one-step",
        description="Component selection strategy: 'one-step' or 'two-step'",
    )
    data: Optional[Any] = Field(
        default=None,
        description="Optional JSON payload (dict/list/string). When provided, bypasses the movies agent and uses this data directly.",
    )
    data_type: Optional[str] = Field(
        default=None,
        description="Optional identifier for the provided data (e.g., 'movies.detail', 'cost.analysis').",
    )
