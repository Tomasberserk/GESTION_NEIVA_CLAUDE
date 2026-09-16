"""remover_modulos_erp

Revision ID: 011
Revises: 010
Create Date: 2026-09-15

Elimina las tablas del módulo ERP (abonos, cuentas por pagar, compras, proveedores)
y añade el valor 'pro' al tipo enum planempresa.
"""
from alembic import op
import sqlalchemy as sa


revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Eliminar tablas ERP en orden de dependencia FK
    op.execute("DROP TABLE IF EXISTS abonos_cuentas_por_pagar CASCADE")
    op.execute("DROP TABLE IF EXISTS cuentas_por_pagar CASCADE")
    op.execute("DROP TABLE IF EXISTS detalle_compras CASCADE")
    op.execute("DROP TABLE IF EXISTS compras CASCADE")
    op.execute("DROP TABLE IF EXISTS proveedores CASCADE")

    # 2. Agregar 'pro' al enum planempresa si no existe
    op.execute("ALTER TYPE planempresa ADD VALUE IF NOT EXISTS 'pro'")


def downgrade() -> None:
    # No se restaura el ERP obsoleto de forma automática
    pass
