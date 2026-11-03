"""Store score_details as JSONB (RFC 5.4) and keep email uniqueness in a single index.

Revision ID: 20261102_0006
Revises: 20261102_0005
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261102_0006"
down_revision = "20261102_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.alter_column("candidaturas_ranking", "score_details", type_=postgresql.JSONB(), existing_type=sa.JSON(), existing_nullable=True, postgresql_using="score_details::jsonb")

  # O índice único é criado antes de remover a constraint, para o e-mail nunca ficar sem garantia de unicidade (RN06).
  op.drop_index("ix_usuarios_email", table_name="usuarios")
  op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
  op.drop_constraint("usuarios_email_key", "usuarios", type_="unique")


def downgrade() -> None:
  op.create_unique_constraint("usuarios_email_key", "usuarios", ["email"])
  op.drop_index("ix_usuarios_email", table_name="usuarios")
  op.create_index("ix_usuarios_email", "usuarios", ["email"])

  op.alter_column("candidaturas_ranking", "score_details", type_=sa.JSON(), existing_type=postgresql.JSONB(), existing_nullable=True, postgresql_using="score_details::json")
