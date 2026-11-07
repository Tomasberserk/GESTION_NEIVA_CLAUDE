"""Immutable DTO contracts exposed by auth_tenancy."""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompanySummaryDTO:
    """Public company snapshot exposed across module boundaries."""

    id: UUID
    nombre_comercial: str
    nit_o_cedula: str
    plan: str
    is_active: bool


@dataclass(frozen=True)
class UserSummaryDTO:
    """Public user snapshot exposed across module boundaries."""

    id: UUID
    empresa_id: UUID
    email: str
    nombre: str | None
    rol: str
    is_active: bool
