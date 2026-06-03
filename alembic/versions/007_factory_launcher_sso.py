"""factory_launcher_sso

Revision ID: 007
Revises: 006
Create Date: 2026-06-02

Añade campos de Factory Launcher a la tabla empresas y crea la tabla sso_tokens
para el flujo de login automático de un solo uso.
"""
from alembic import op
import sqlalchemy as sa


revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Nuevos campos en empresas para el launcher de factory
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_upgrade_solicitado boolean NOT NULL DEFAULT false"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_url varchar(500)"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas ADD COLUMN IF NOT EXISTS "
        "factory_trial_expires_at timestamp with time zone"
    ))

    # 2. Tabla sso_tokens para login automático de un solo uso
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


def downgrade() -> None:
    conn = op.get_bind()

    conn.execute(sa.text("DROP TABLE IF EXISTS sso_tokens"))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_upgrade_solicitado"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_url"
    ))
    conn.execute(sa.text(
        "ALTER TABLE empresas DROP COLUMN IF EXISTS factory_trial_expires_at"
    ))
