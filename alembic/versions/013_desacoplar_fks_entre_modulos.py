"""desacoplar_fks_entre_modulos

Revision ID: 013
Revises: 012
Create Date: 2026-11-07

Drops physical cross-module foreign keys in PostgreSQL per ADR-004 and DAT-03:
- ventas.usuario_id -> usuarios.id (pos_ventas -> auth_tenancy)
- detalles_venta.producto_id -> productos.id (pos_ventas -> inventario)
- soporte_tickets.usuario_id -> usuarios.id (soporte_crm -> auth_tenancy)
Adds explicit indexes on producto_id and usuario_id columns to preserve join performance.
"""
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop cross-module foreign keys and add explicit UUID lookup indexes."""
    op.execute(
        "ALTER TABLE ventas DROP CONSTRAINT IF EXISTS fk_ventas_usuario_id_usuarios"
    )
    op.execute(
        "ALTER TABLE detalles_venta DROP CONSTRAINT IF EXISTS fk_detalles_producto_id"
    )
    op.execute(
        "ALTER TABLE soporte_tickets DROP CONSTRAINT IF EXISTS soporte_tickets_usuario_id_fkey"
    )

    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_detalles_venta_producto_id ON detalles_venta (producto_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_soporte_tickets_usuario ON soporte_tickets (usuario_id)"
    )


def downgrade() -> None:
    """Restore cross-module foreign keys and drop added indexes."""
    op.execute("DROP INDEX IF EXISTS idx_soporte_tickets_usuario")
    op.execute("DROP INDEX IF EXISTS idx_detalles_venta_producto_id")

    op.create_foreign_key(
        "soporte_tickets_usuario_id_fkey",
        "soporte_tickets",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_detalles_producto_id",
        "detalles_venta",
        "productos",
        ["producto_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_ventas_usuario_id_usuarios",
        "ventas",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="SET NULL",
    )
