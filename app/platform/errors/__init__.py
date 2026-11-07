"""Standardized platform error contracts and domain exceptions."""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ErrorDetail:
    """Single validation or domain error item."""

    field: str
    message: str


@dataclass(frozen=True)
class StandardErrorPayload:
    """Canonical error response structure per 07-api/rest-conventions.md."""

    error: str
    message: str
    details: list[dict[str, Any]] = field(default_factory=list)
    correlation_id: str = ""
