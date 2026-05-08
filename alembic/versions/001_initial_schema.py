"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-05 00:00:00.000000 UTC

Crea las 5 tablas del esquema original (empresas, usuarios, productos,
ventas, detalles_venta) añadiendo los campos de auditoría del AuditMixin
(created_at, updated_at, is_active) y un trigger PostgreSQL que mantiene
updated_at sincronizado a nivel de base de datos.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Tablas para aplicar el trigger de updated_at (mismo orden que upgrade)
# ---------------------------------------------------------------------------
_TABLES = ["empresas", "usuarios", "productos", "ventas", "detalles_venta"]


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Extensión uuid-ossp (compatibilidad con legado)
    # ------------------------------------------------------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ------------------------------------------------------------------
    # 2. Función trigger para auto-actualizar updated_at en el servidor
    #    Esto cubre updates que NO pasan por el ORM de SQLAlchemy.
    # ------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE 'plpgsql';
    """)

    # ------------------------------------------------------------------
    # 3. empresas
    # ------------------------------------------------------------------
    op.create_table(
        "empresas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("nombre_comercial", sa.String(150), nullable=False),
        sa.Column("nit_o_cedula", sa.String(50), nullable=False),
        # AuditMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.UniqueConstraint("nit_o_cedula", name="uq_empresas_nit_o_cedula"),
    )

    # ------------------------------------------------------------------
    # 4. usuarios
    # ------------------------------------------------------------------
    # Verificación manual vía pg_type: idempotente en cualquier versión de PG
    bind = op.get_bind()
    tipo_existe = bind.execute(
        text("SELECT 1 FROM pg_type WHERE typname = 'rolusuario'")
    ).fetchone()
    if not tipo_existe:
        bind.execute(text("CREATE TYPE rolusuario AS ENUM ('admin', 'tendero')"))

    op.create_table(
        "usuarios",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "rol",
            # postgresql.ENUM con create_type=False es la única forma fiable en
            # SQLAlchemy 2.0 de evitar que op.create_table emita CREATE TYPE
            # automáticamente (sa.Enum delega en un objeto interno que ignora el flag)
            postgresql.ENUM("admin", "tendero", name="rolusuario", create_type=False),
            nullable=False,
            server_default="tendero",
        ),
        # AuditMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            ondelete="CASCADE",
            name="fk_usuarios_empresa_id",
        ),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("idx_usuarios_email", "usuarios", ["email"])

    # ------------------------------------------------------------------
    # 5. productos
    # ------------------------------------------------------------------
    op.create_table(
        "productos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("codigo_barras", sa.String(20), nullable=False),
        sa.Column("precio_costo", sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("precio_venta", sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("cantidad_actual", sa.Integer(), server_default="0", nullable=False),
        sa.Column("foto_url", sa.String(), nullable=True),
        # AuditMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            ondelete="CASCADE",
            name="fk_productos_empresa_id",
        ),
        sa.UniqueConstraint("codigo_barras", name="uq_productos_codigo_barras"),
    )

    # ------------------------------------------------------------------
    # 6. ventas
    # ------------------------------------------------------------------
    op.create_table(
        "ventas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fecha_venta",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("total", sa.Numeric(10, 2), server_default="0.00", nullable=False),
        # AuditMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresas.id"],
            ondelete="CASCADE",
            name="fk_ventas_empresa_id",
        ),
    )
    op.create_index("idx_ventas_empresa_fecha", "ventas", ["empresa_id", "fecha_venta"])

    # ------------------------------------------------------------------
    # 7. detalles_venta
    # ------------------------------------------------------------------
    op.create_table(
        "detalles_venta",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("venta_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("producto_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False),
        # AuditMixin
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(
            ["venta_id"],
            ["ventas.id"],
            ondelete="CASCADE",
            name="fk_detalles_venta_id",
        ),
        sa.ForeignKeyConstraint(
            ["producto_id"],
            ["productos.id"],
            ondelete="RESTRICT",       # Previene borrar productos ya vendidos
            name="fk_detalles_producto_id",
        ),
    )
    op.create_index("idx_detalles_venta_venta_id", "detalles_venta", ["venta_id"])

    # ------------------------------------------------------------------
    # 8. Triggers de updated_at para todas las tablas
    # ------------------------------------------------------------------
    for table in _TABLES:
        op.execute(f"""
            CREATE TRIGGER trigger_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Deshacer en orden inverso para respetar FK dependencies

    # 1. Eliminar triggers
    for table in reversed(_TABLES):
        op.execute(
            f"DROP TRIGGER IF EXISTS trigger_{table}_updated_at ON {table}"
        )

    # 2. Eliminar función trigger
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # 3. Eliminar tablas (orden: hijos primero)
    op.drop_index("idx_detalles_venta_venta_id", table_name="detalles_venta")
    op.drop_table("detalles_venta")

    op.drop_index("idx_ventas_empresa_fecha", table_name="ventas")
    op.drop_table("ventas")

    op.drop_table("productos")

    op.drop_index("idx_usuarios_email", table_name="usuarios")
    op.drop_table("usuarios")

    # 4. Eliminar tipo ENUM
    op.execute("DROP TYPE IF EXISTS rolusuario")

    op.drop_table("empresas")

    # 5. Extensión (comentada: puede estar usada por otras apps en la misma BD)
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
