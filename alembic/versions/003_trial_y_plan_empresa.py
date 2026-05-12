"""trial y plan empresa

Revision ID: 003
Revises: 002
Create Date: 2026-05-11

Agrega trial_expires_at y plan a la tabla empresas.
- trial_expires_at: NULL para empresas existentes (no se bloquean)
- plan: default 'basic' para todos
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear el tipo enum planempresa
    planempresa = sa.Enum("basic", "medium", "premium", name="planempresa")
    planempresa.create(op.get_bind(), checkfirst=True)

    # 2. Agregar columna plan con default 'basic'
    op.add_column(
        "empresas",
        sa.Column(
            "plan",
            sa.Enum("basic", "medium", "premium", name="planempresa"),
            nullable=False,
            server_default="basic",
        ),
    )

    # 3. Agregar columna trial_expires_at (NULL = sin límite de trial)
    op.add_column(
        "empresas",
        sa.Column("trial_expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("empresas", "trial_expires_at")
    op.drop_column("empresas", "plan")
    op.execute("DROP TYPE IF EXISTS planempresa")
