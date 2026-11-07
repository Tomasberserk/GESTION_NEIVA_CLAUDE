"""remover_modulos_erp

Revision ID: 011
Revises: 010
Create Date: 2026-09-15

Drops deprecated ERP tables (abonos_cuentas_por_pagar, cuentas_por_pagar,
detalle_compras, compras, proveedores) and adds 'pro' to planempresa enum.
"""
from alembic import op

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop deprecated ERP monolith tables and add 'pro' enum value."""
    op.execute("DROP TABLE IF EXISTS abonos_cuentas_por_pagar CASCADE")
    op.execute("DROP TABLE IF EXISTS cuentas_por_pagar CASCADE")
    op.execute("DROP TABLE IF EXISTS detalle_compras CASCADE")
    op.execute("DROP TABLE IF EXISTS compras CASCADE")
    op.execute("DROP TABLE IF EXISTS proveedores CASCADE")
    op.execute("ALTER TYPE planempresa ADD VALUE IF NOT EXISTS 'pro'")


def downgrade() -> None:
    """Recreate empty ERP tables to guarantee reversible migration chain (DAT-07)."""
    op.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id uuid PRIMARY KEY,
            empresa_id uuid NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            nombre varchar(150) NOT NULL,
            nit_o_cedula varchar(50),
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id uuid PRIMARY KEY,
            empresa_id uuid NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            proveedor_id uuid REFERENCES proveedores(id) ON DELETE RESTRICT,
            total numeric(12, 2) NOT NULL DEFAULT 0.00,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id uuid PRIMARY KEY,
            compra_id uuid NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
            producto_id uuid NOT NULL,
            cantidad numeric(10, 3) NOT NULL,
            precio_unitario numeric(12, 2) NOT NULL,
            subtotal numeric(12, 2) NOT NULL
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
            id uuid PRIMARY KEY,
            empresa_id uuid NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
            proveedor_id uuid REFERENCES proveedores(id) ON DELETE RESTRICT,
            compra_id uuid REFERENCES compras(id) ON DELETE SET NULL,
            monto_total numeric(12, 2) NOT NULL DEFAULT 0.00,
            saldo_pendiente numeric(12, 2) NOT NULL DEFAULT 0.00,
            estado varchar(30) NOT NULL DEFAULT 'PENDIENTE',
            fecha_vencimiento timestamp with time zone,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now()
        )
    """)
    op.execute("""
        CREATE TABLE IF NOT EXISTS abonos_cuentas_por_pagar (
            id uuid PRIMARY KEY,
            cuenta_por_pagar_id uuid NOT NULL REFERENCES cuentas_por_pagar(id) ON DELETE CASCADE,
            monto numeric(12, 2) NOT NULL,
            metodo_pago varchar(50) NOT NULL,
            nota text,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now()
        )
    """)
