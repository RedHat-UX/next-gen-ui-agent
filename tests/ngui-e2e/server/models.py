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


class PrometheusTestRequest(BaseModel):
    prometheusData: str = Field(
        ..., description="Prometheus query_range result as JSON string"
    )
    userPrompt: str = Field(
        default="Show time-series data", description="User prompt for UI generation"
    )
    strategy: Optional[str] = Field(
        default="one-step",
        description="Component selection strategy: 'one-step' or 'two-step'",
    )
    downsample: Optional[int] = Field(
        default=1,
        description="Downsample factor: 1 = all points, 2 = every other point, etc.",
    )
