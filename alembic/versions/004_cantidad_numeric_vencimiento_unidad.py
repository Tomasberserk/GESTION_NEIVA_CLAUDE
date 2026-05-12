"""cantidad numeric, vencimiento y unidad medida

Revision ID: 004
Revises: 003
Create Date: 2026-05-12

- productos.cantidad_actual: Integer → Numeric(10,3) para soportar granel
- detalles_venta.cantidad:   Integer → Numeric(10,3) para soportar fracciones
- productos.fecha_vencimiento: Date nullable
- productos.unidad_medida: Enum(unidad, gramo, libra, kilo) default 'unidad'
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Crear tipo enum unidadmedida
    unidadmedida = sa.Enum("unidad", "gramo", "libra", "kilo", name="unidadmedida")
    unidadmedida.create(op.get_bind(), checkfirst=True)

    # 2. productos.cantidad_actual: Integer → Numeric(10,3)
    op.alter_column(
        "productos", "cantidad_actual",
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 3),
        existing_nullable=False,
        existing_server_default="0",
        server_default="0.000",
        postgresql_using="cantidad_actual::numeric(10,3)",
    )

    # 3. detalles_venta.cantidad: Integer → Numeric(10,3)
    op.alter_column(
        "detalles_venta", "cantidad",
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 3),
        existing_nullable=False,
        postgresql_using="cantidad::numeric(10,3)",
    )

    # 4. productos.unidad_medida
    op.add_column(
        "productos",
        sa.Column(
            "unidad_medida",
            sa.Enum("unidad", "gramo", "libra", "kilo", name="unidadmedida"),
            nullable=False,
            server_default="unidad",
        ),
    )

    # 5. productos.fecha_vencimiento
    op.add_column(
        "productos",
        sa.Column("fecha_vencimiento", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("productos", "fecha_vencimiento")
    op.drop_column("productos", "unidad_medida")
    op.alter_column(
        "detalles_venta", "cantidad",
        existing_type=sa.Numeric(10, 3),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="cantidad::integer",
    )
    op.alter_column(
        "productos", "cantidad_actual",
        existing_type=sa.Numeric(10, 3),
        type_=sa.Integer(),
        existing_nullable=False,
        server_default="0",
        postgresql_using="cantidad_actual::integer",
    )
    op.execute("DROP TYPE IF EXISTS unidadmedida")
