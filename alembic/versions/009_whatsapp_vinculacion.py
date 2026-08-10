"""whatsapp_vinculacion

Revision ID: 009
Revises: 008
Create Date: 2026-06-17

Agrega campo telefono_whatsapp a la tabla usuarios para vincular
cuentas con números de WhatsApp. Incluye índice único.
"""
from alembic import op
import sqlalchemy as sa


revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("telefono_whatsapp", sa.String(20), nullable=True),
    )
    op.create_index(
        "ix_usuarios_telefono_whatsapp",
        "usuarios",
        ["telefono_whatsapp"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_usuarios_telefono_whatsapp", table_name="usuarios")
    op.drop_column("usuarios", "telefono_whatsapp")
