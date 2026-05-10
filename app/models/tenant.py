import uuid

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(String(50), nullable=False, server_default="free")
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Tenant {self.slug!r} plan={self.plan}>"
