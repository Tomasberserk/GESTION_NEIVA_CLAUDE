"""Internal domain queries and operations for auth_tenancy."""
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import models
from app.auth_tenancy.api.contracts import CompanySummaryDTO, UserSummaryDTO


def get_active_company_or_404(empresa_id: UUID, db: Session) -> CompanySummaryDTO:
    """Verify that a tenant company exists and is active, returning an immutable DTO."""
    empresa = (
        db.query(models.Empresa)
        .filter(
            models.Empresa.id == empresa_id,
            models.Empresa.is_active.is_(True),
        )
        .first()
    )
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empresa no encontrada",
        )
    return CompanySummaryDTO(
        id=empresa.id,
        nombre_comercial=empresa.nombre_comercial,
        nit_o_cedula=empresa.nit_o_cedula,
        plan=empresa.plan.value if empresa.plan else "basic",
        is_active=empresa.is_active,
    )


def get_company_seller_or_404(usuario_id: UUID, empresa_id: UUID, db: Session) -> UserSummaryDTO:
    """Verify that a seller user belongs to the specified company."""
    vendedor = (
        db.query(models.Usuario)
        .filter(
            models.Usuario.id == usuario_id,
            models.Usuario.empresa_id == empresa_id,
        )
        .first()
    )
    if not vendedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendedor no encontrado en esta empresa",
        )
    return UserSummaryDTO(
        id=vendedor.id,
        empresa_id=vendedor.empresa_id,
        email=vendedor.email,
        nombre=vendedor.nombre,
        rol=vendedor.rol.value if vendedor.rol else "tendero",
        is_active=vendedor.is_active,
    )
