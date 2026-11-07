"""Public facade for auth_tenancy bounded context."""
from uuid import UUID
from sqlalchemy.orm import Session

from app.auth_tenancy.api.contracts import CompanySummaryDTO, UserSummaryDTO
from app.auth_tenancy.internal import service as _internal_service


class AuthTenancyFacade:
    """Entry point for cross-module tenant and user verification."""

    @staticmethod
    def ensure_active_company(empresa_id: UUID, db: Session) -> CompanySummaryDTO:
        """Validate and return active company summary DTO or raise 404."""
        return _internal_service.get_active_company_or_404(empresa_id=empresa_id, db=db)

    @staticmethod
    def ensure_company_seller(usuario_id: UUID, empresa_id: UUID, db: Session) -> UserSummaryDTO:
        """Validate that a seller belongs to the given tenant company or raise 404."""
        return _internal_service.get_company_seller_or_404(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            db=db,
        )
