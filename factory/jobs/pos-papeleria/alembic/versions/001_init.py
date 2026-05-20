"""initial schema — POS Papelería

Revision ID: 001
Revises:
Create Date: 2026-05-17 00:00:00.000000 UTC

Crea las 5 tablas del esquema de POS Papelería con todos sus índices y
constraints. Diferencias vs Gestión Neiva:
  - Empresa.plan es VARCHAR (no enum)
  - UnidadMedida: solo unidad/paquete (sin gramo/libra/kilo)
  - CategoriaProducto: 5 categorías de papelería
  - Producto: sin fecha_vencimiento, con stock_minimo INTEGER default 5
  - Producto.cantidad_actual: INTEGER (no Numeric)
  - Venta: usuario_id NOT NULL FK RESTRICT (trazabilidad de cajero)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

_TABLES = ["empresas", "usuarios", "productos", "ventas", "detalles_venta"]


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Extensión uuid-ossp
    # ------------------------------------------------------------------
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # ------------------------------------------------------------------
    # 2. Función trigger para auto-actualizar updated_at en el servidor
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
    #    plan: VARCHAR(50), no enum — más sencillo para tier basic
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
        sa.Column("nit_o_cedula",     sa.String(50),  nullable=False),
        sa.Column("plan",             sa.String(50),  nullable=False, server_default="basic"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active",  sa.Boolean(), server_default="true", nullable=False),
        sa.UniqueConstraint("nit_o_cedula", name="uq_empresas_nit_o_cedula"),
    )

    # ------------------------------------------------------------------
    # 4. Enums PostgreSQL (creación explícita e idempotente)
    # ------------------------------------------------------------------
    bind = op.get_bind()

    def _crear_enum_si_no_existe(nombre: str, valores: list[str]) -> None:
        existe = bind.execute(
            text("SELECT 1 FROM pg_type WHERE typname = :n"), {"n": nombre}
        ).fetchone()
        if not existe:
            vals = ", ".join(f"'{v}'" for v in valores)
            bind.execute(text(f"CREATE TYPE {nombre} AS ENUM ({vals})"))

    _crear_enum_si_no_existe("rolusuario",       ["admin", "tendero"])
    _crear_enum_si_no_existe("unidadmedida",     ["unidad", "paquete"])
    _crear_enum_si_no_existe("categoriaproducto", [
        "Utiles escolares",
        "Papel y resmas",
        "Tecnologia",
        "Servicios",
        "Miscelanea",
    ])

    # ------------------------------------------------------------------
    # 5. usuarios
    # ------------------------------------------------------------------
    op.create_table(
        "usuarios",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("email",           sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(),    nullable=False),
        sa.Column("empresa_id",      postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "rol",
            postgresql.ENUM("admin", "tendero", name="rolusuario", create_type=False),
            nullable=False,
            server_default="tendero",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active",  sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE",  name="fk_usuarios_empresa_id"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("idx_usuarios_email",   "usuarios", ["email"])
    op.create_index("idx_usuarios_empresa", "usuarios", ["empresa_id"])

    # ------------------------------------------------------------------
    # 6. productos
    #    - cantidad_actual: Integer (papelería opera en unidades enteras)
    #    - stock_minimo: nuevo campo, default 5
    #    - unidad_medida: enum unidadmedida (solo unidad/paquete)
    #    - categoria: enum categoriaproducto (NOT NULL)
    #    - sin fecha_vencimiento
    # ------------------------------------------------------------------
    op.create_table(
        "productos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("empresa_id",     postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre",         sa.String(255), nullable=False),
        sa.Column("codigo_barras",  sa.String(50),  nullable=False),
        sa.Column("precio_costo",   sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("precio_venta",   sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("cantidad_actual", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "unidad_medida",
            postgresql.ENUM("unidad", "paquete", name="unidadmedida", create_type=False),
            nullable=False,
            server_default="unidad",
        ),
        sa.Column(
            "categoria",
            postgresql.ENUM(
                "Utiles escolares", "Papel y resmas", "Tecnologia", "Servicios", "Miscelanea",
                name="categoriaproducto",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("stock_minimo", sa.Integer(), server_default="5", nullable=False),
        sa.Column("foto_url",     sa.String(), nullable=True),
        sa.Column("created_at",   sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",   sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active",    sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE", name="fk_productos_empresa_id"),
        sa.UniqueConstraint("empresa_id", "codigo_barras", name="uq_producto_empresa_barras"),
    )
    op.create_index("idx_productos_empresa",    "productos", ["empresa_id"])
    # cubre WHERE empresa_id=X AND cantidad_actual <= stock_minimo
    op.create_index("idx_productos_stock_bajo", "productos", ["empresa_id", "cantidad_actual", "stock_minimo"])

    # ------------------------------------------------------------------
    # 7. ventas
    #    usuario_id: FK RESTRICT — registra qué cajero hizo la venta
    # ------------------------------------------------------------------
    op.create_table(
        "ventas",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("empresa_id",  postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usuario_id",  postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fecha_venta", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("total",       sa.Numeric(10, 2), server_default="0.00", nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",  sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active",   sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE",  name="fk_ventas_empresa_id"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT", name="fk_ventas_usuario_id"),
    )
    op.create_index("idx_ventas_empresa_fecha", "ventas", ["empresa_id", "fecha_venta"])
    op.create_index("idx_ventas_usuario",       "ventas", ["usuario_id"])

    # ------------------------------------------------------------------
    # 8. detalles_venta
    #    cantidad: Integer (consistente con Producto.cantidad_actual)
    # ------------------------------------------------------------------
    op.create_table(
        "detalles_venta",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("venta_id",        postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("producto_id",     postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cantidad",        sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(10, 2), nullable=False),
        sa.Column("subtotal",        sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at",      sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active",       sa.Boolean(), server_default="true", nullable=False),
        sa.ForeignKeyConstraint(["venta_id"],    ["ventas.id"],    ondelete="CASCADE",  name="fk_detalles_venta_id"),
        sa.ForeignKeyConstraint(["producto_id"], ["productos.id"], ondelete="RESTRICT", name="fk_detalles_producto_id"),
    )
    op.create_index("idx_detalles_venta_venta_id", "detalles_venta", ["venta_id"])

    # ------------------------------------------------------------------
    # 9. Triggers updated_at para todas las tablas
    # ------------------------------------------------------------------
    for table in _TABLES:
        op.execute(f"""
            CREATE TRIGGER trigger_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # 1. Eliminar triggers (orden inverso)
    for table in reversed(_TABLES):
        op.execute(f"DROP TRIGGER IF EXISTS trigger_{table}_updated_at ON {table}")

    # 2. Función trigger
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # 3. Tablas (hijos primero)
    op.drop_index("idx_detalles_venta_venta_id", table_name="detalles_venta")
    op.drop_table("detalles_venta")

    op.drop_index("idx_ventas_usuario",       table_name="ventas")
    op.drop_index("idx_ventas_empresa_fecha", table_name="ventas")
    op.drop_table("ventas")

    op.drop_index("idx_productos_stock_bajo", table_name="productos")
    op.drop_index("idx_productos_empresa",    table_name="productos")
    op.drop_table("productos")

    op.drop_index("idx_usuarios_empresa", table_name="usuarios")
    op.drop_index("idx_usuarios_email",   table_name="usuarios")
    op.drop_table("usuarios")

    op.drop_table("empresas")

    # 4. Enums
    op.execute("DROP TYPE IF EXISTS categoriaproducto")
    op.execute("DROP TYPE IF EXISTS unidadmedida")
    op.execute("DROP TYPE IF EXISTS rolusuario")
