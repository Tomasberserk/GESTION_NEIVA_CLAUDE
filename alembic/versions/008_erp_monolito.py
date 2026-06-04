"""erp_monolito

Revision ID: 008
Revises: 007
Create Date: 2026-06-03

Integra ERP Distribuidora en monolito SaaS:
- Elimina tabla sso_tokens y campos factory_launcher de empresas
- Extiende enum unidadmedida con unidades de distribuidora (caja, bulto, kg, litro, metro)
- Crea tablas: proveedores, compras, detalle_compras, cuentas_por_pagar, abonos_cuentas_por_pagar
"""
from alembic import op
import sqlalchemy as sa


revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Eliminar infraestructura SSO/Factory Launcher
    conn.execute(sa.text("DROP TABLE IF EXISTS sso_tokens CASCADE"))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_upgrade_solicitado"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_url"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_trial_expires_at"
    ))

    # 2. Extender enum unidadmedida con unidades ERP
    # En PostgreSQL 16, ALTER TYPE ADD VALUE IF NOT EXISTS puede ejecutarse
    # dentro de una transacción; los nuevos valores son visibles tras el COMMIT.
    for valor in ("caja", "bulto", "kg", "litro", "metro"):
        conn.execute(sa.text(
            f"ALTER TYPE unidadmedida ADD VALUE IF NOT EXISTS '{valor}'"
        ))

    # 3. Tabla proveedores
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            nit_o_cedula varchar(50) NOT NULL,
            razon_social varchar(150) NOT NULL,
            contacto_nombre varchar(100),
            telefono varchar(50),
            email varchar(255),
            direccion varchar(255),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            UNIQUE (empresa_id, nit_o_cedula),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_proveedores_empresa ON proveedores (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_proveedores_razon_social ON proveedores (razon_social)"
    ))

    # 4. Tabla compras
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS compras (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            proveedor_id uuid NOT NULL,
            usuario_id uuid,
            numero_factura varchar(100),
            fecha_compra timestamptz NOT NULL DEFAULT now(),
            metodo_pago varchar(50) NOT NULL DEFAULT 'EFECTIVO',
            fecha_vencimiento timestamptz,
            estado varchar(50) NOT NULL DEFAULT 'PAGADA',
            total numeric(12, 2) NOT NULL DEFAULT 0.00,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE RESTRICT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_empresa ON compras (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_proveedor ON compras (proveedor_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras (fecha_compra)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_compras_estado ON compras (estado)"
    ))

    # 5. Tabla detalle_compras
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS detalle_compras (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            compra_id uuid NOT NULL,
            producto_id uuid NOT NULL,
            cantidad numeric(10, 3) NOT NULL,
            precio_costo numeric(12, 2) NOT NULL,
            subtotal numeric(12, 2) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compra_compra ON detalle_compras (compra_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_detalle_compra_producto ON detalle_compras (producto_id)"
    ))

    # 6. Tabla cuentas_por_pagar
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            empresa_id uuid NOT NULL,
            compra_id uuid NOT NULL,
            proveedor_id uuid NOT NULL,
            monto_total numeric(12, 2) NOT NULL,
            saldo_pendiente numeric(12, 2) NOT NULL,
            fecha_vencimiento timestamptz NOT NULL,
            estado varchar(50) NOT NULL DEFAULT 'PENDIENTE',
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (compra_id) REFERENCES compras(id) ON DELETE CASCADE,
            FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE RESTRICT
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_empresa ON cuentas_por_pagar (empresa_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_proveedor ON cuentas_por_pagar (proveedor_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_estado ON cuentas_por_pagar (estado)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_cuentas_pagar_vencimiento ON cuentas_por_pagar (fecha_vencimiento)"
    ))

    # 7. Tabla abonos_cuentas_por_pagar
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS abonos_cuentas_por_pagar (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            cuenta_por_pagar_id uuid NOT NULL,
            monto numeric(12, 2) NOT NULL,
            fecha_abono timestamptz NOT NULL DEFAULT now(),
            metodo_pago varchar(50) NOT NULL DEFAULT 'EFECTIVO',
            nota varchar(500),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            PRIMARY KEY (id),
            FOREIGN KEY (cuenta_por_pagar_id) REFERENCES cuentas_por_pagar(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_abonos_cxp ON abonos_cuentas_por_pagar (cuenta_por_pagar_id)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_abonos_fecha ON abonos_cuentas_por_pagar (fecha_abono)"
    ))


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DROP TABLE IF EXISTS abonos_cuentas_por_pagar CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS cuentas_por_pagar CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS detalle_compras CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS compras CASCADE"))
    conn.execute(sa.text("DROP TABLE IF EXISTS proveedores CASCADE"))

    # PostgreSQL no soporta DROP VALUE en enums — los nuevos valores quedan tras downgrade.

    # Restaurar infraestructura SSO/Factory Launcher
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_upgrade_solicitado boolean NOT NULL DEFAULT false"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS factory_url varchar(500)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_trial_expires_at timestamp with time zone"
    ))
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS sso_tokens (
            id uuid NOT NULL,
            empresa_id uuid NOT NULL,
            usuario_id uuid NOT NULL,
            token varchar(64) NOT NULL,
            expires_at timestamp with time zone NOT NULL,
            usado boolean NOT NULL DEFAULT false,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            UNIQUE (token),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_sso_tokens_token ON sso_tokens (token)"
    ))
    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_sso_tokens_empresa ON sso_tokens (empresa_id)"
    ))
