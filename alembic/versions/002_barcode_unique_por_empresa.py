"""barcode unique por empresa

Revision ID: 002
Revises: 001
Create Date: 2026-05-11

Cambia el constraint de codigo_barras de único global a único por empresa.
Esto permite que dos tiendas distintas tengan productos con el mismo barcode.
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Eliminar unique constraint global (nombre real en la BD)
    op.drop_constraint("uq_productos_codigo_barras", "productos", type_="unique")

    # 2. Ampliar columna de 20 a 50 chars (barcodes EAN-128 pueden ser largos)
    op.alter_column("productos", "codigo_barras",
                    existing_type=sa.String(20),
                    type_=sa.String(50),
                    existing_nullable=False)

    # 3. Agregar constraint compuesto (empresa_id, codigo_barras)
    op.create_unique_constraint(
        "uq_producto_empresa_barras",
        "productos",
        ["empresa_id", "codigo_barras"],
    )

    # 4. Índice para queries por empresa
    op.create_index("idx_productos_empresa", "productos", ["empresa_id"])


def downgrade() -> None:
    op.drop_index("idx_productos_empresa", table_name="productos")
    op.drop_constraint("uq_producto_empresa_barras", "productos", type_="unique")
    op.alter_column("productos", "codigo_barras",
                    existing_type=sa.String(50),
                    type_=sa.String(20),
                    existing_nullable=False)
    op.create_unique_constraint("uq_productos_codigo_barras", "productos", ["codigo_barras"])
