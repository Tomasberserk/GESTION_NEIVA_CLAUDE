"""add categoria producto

Revision ID: 005
Revises: 004
Create Date: 2026-05-12

Agrega el enum CategoriaProducto y la columna categoria (nullable) a la tabla productos.
Productos existentes quedan con categoria = NULL sin afectar el negocio.
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None

CATEGORIAS = ("Bebidas", "Snacks", "Aseo", "Lacteos", "Limpieza", "Panaderia")


def upgrade() -> None:
    categoriaproducto = sa.Enum(*CATEGORIAS, name="categoriaproducto")
    categoriaproducto.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "productos",
        sa.Column(
            "categoria",
            sa.Enum(*CATEGORIAS, name="categoriaproducto"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("productos", "categoria")
    op.execute("DROP TYPE IF EXISTS categoriaproducto")
