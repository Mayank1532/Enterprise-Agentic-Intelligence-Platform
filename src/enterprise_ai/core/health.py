"""Core API health models."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Application health response."""

    service: str
    status: Literal["ok"]
    environment: str


class ReadinessResponse(BaseModel):
    """Application readiness response."""

    service: str
    status: Literal["ready"]
    environment: str
