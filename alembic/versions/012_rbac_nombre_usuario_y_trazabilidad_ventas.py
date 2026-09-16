"""rbac_nombre_usuario_y_trazabilidad_ventas

Revision ID: 012
Revises: 011
Create Date: 2026-09-16

Agrega columna 'nombre' a la tabla usuarios (nullable=True).
Agrega 'usuario_id' (FK con ON DELETE SET NULL) y 'vendedor_nombre_snapshot'
a la tabla ventas para trazabilidad historica inmutable.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Columna 'nombre' en usuarios
    op.add_column("usuarios", sa.Column("nombre", sa.String(length=100), nullable=True))

    # 2. Columnas en ventas para auditoria y snapshot
    op.add_column(
        "ventas",
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "ventas",
        sa.Column("vendedor_nombre_snapshot", sa.String(length=100), nullable=True),
    )

    # 3. Indice y FK hacia usuarios
    op.create_index("idx_ventas_usuario_id", "ventas", ["usuario_id"])
    op.create_foreign_key(
        "fk_ventas_usuario_id_usuarios",
        "ventas",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_ventas_usuario_id_usuarios", "ventas", type_="foreignkey")
    op.drop_index("idx_ventas_usuario_id", table_name="ventas")
    op.drop_column("ventas", "vendedor_nombre_snapshot")
    op.drop_column("ventas", "usuario_id")
    op.drop_column("usuarios", "nombre")
