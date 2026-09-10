"""crear_tabla_agent_commands

Revision ID: 010
Revises: 009
Create Date: 2026-09-09

Crea la tabla agent_commands para idempotencia transaccional persistente y auditoría
de las operaciones ejecutadas por el agente de IA.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_commands",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("empresa_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", sa.String(100), nullable=False),
        sa.Column("command_id", sa.String(100), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDIENTE"),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.UniqueConstraint("empresa_id", "command_id", name="uq_empresa_command_id"),
    )
    op.create_index("idx_agent_commands_empresa", "agent_commands", ["empresa_id"])
    op.create_index("idx_agent_commands_command", "agent_commands", ["command_id"])
    op.create_index("idx_agent_commands_conversation", "agent_commands", ["conversation_id"])


def downgrade() -> None:
    op.drop_index("idx_agent_commands_conversation", table_name="agent_commands")
    op.drop_index("idx_agent_commands_command", table_name="agent_commands")
    op.drop_index("idx_agent_commands_empresa", table_name="agent_commands")
    op.drop_table("agent_commands")
