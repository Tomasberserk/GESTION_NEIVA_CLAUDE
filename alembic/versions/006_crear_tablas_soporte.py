"""crear_tablas_soporte

Revision ID: 006
Revises: 005
Create Date: 2026-05-26

Crea las tablas soporte_tickets y soporte_mensajes con sus índices y relaciones.
"""
from alembic import op
import sqlalchemy as sa


revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Create enums safely (ignore if they already exist)
    try:
        conn.execute(sa.text(
            "CREATE TYPE estadoticket AS ENUM ('abierto', 'respondido', 'cerrado')"
        ))
    except Exception:
        pass  # Type already exists

    try:
        conn.execute(sa.text(
            "CREATE TYPE remitenterol AS ENUM ('superadmin', 'usuario')"
        ))
    except Exception:
        pass  # Type already exists

    # Create soporte_tickets table using raw SQL to avoid enum auto-creation
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS soporte_tickets (
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone NOT NULL DEFAULT now(),
            is_active boolean NOT NULL DEFAULT true,
            id uuid NOT NULL,
            empresa_id uuid NOT NULL,
            usuario_id uuid NOT NULL,
            asunto varchar(150) NOT NULL,
            estado estadoticket NOT NULL DEFAULT 'abierto',
            PRIMARY KEY (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
        )
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_soporte_tickets_empresa ON soporte_tickets (empresa_id)"
    ))

    # Create soporte_mensajes table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS soporte_mensajes (
            id uuid NOT NULL,
            ticket_id uuid NOT NULL,
            remitente_rol remitenterol NOT NULL,
            remitente_email varchar(255) NOT NULL,
            mensaje text NOT NULL,
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            PRIMARY KEY (id),
            FOREIGN KEY (ticket_id) REFERENCES soporte_tickets(id) ON DELETE CASCADE
        )
    """))

    conn.execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_soporte_mensajes_ticket ON soporte_mensajes (ticket_id)"
    ))


def downgrade() -> None:
    conn = op.get_bind()

    # Drop tables
    conn.execute(sa.text("DROP TABLE IF EXISTS soporte_mensajes"))
    conn.execute(sa.text("DROP TABLE IF EXISTS soporte_tickets"))

    # Drop types
    conn.execute(sa.text("DROP TYPE IF EXISTS remitenterol"))
    conn.execute(sa.text("DROP TYPE IF EXISTS estadoticket"))
