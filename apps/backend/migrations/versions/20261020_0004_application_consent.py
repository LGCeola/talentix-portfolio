"""Add consent_at to candidaturas_ranking (LGPD).

Revision ID: 20261020_0004
Revises: 20261012_0003
"""
from alembic import op
import sqlalchemy as sa

revision = "20261020_0004"
down_revision = "20261012_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
  # Candidaturas anteriores a esta migração recebem a data da própria candidatura.
  op.add_column("candidaturas_ranking", sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True))
  op.execute("UPDATE candidaturas_ranking SET consent_at = applied_at")
  op.alter_column("candidaturas_ranking", "consent_at", nullable=False)


def downgrade() -> None:
  op.drop_column("candidaturas_ranking", "consent_at")
