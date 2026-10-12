"""Add original_filename to curriculos.

Revision ID: 20261011_0002
Revises: 20260917_0001
"""
from alembic import op
import sqlalchemy as sa

revision = "20261011_0002"
down_revision = "20260917_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column("curriculos", sa.Column("original_filename", sa.String(255), nullable=False, server_default=""))
  op.alter_column("curriculos", "original_filename", server_default=None)


def downgrade() -> None:
  op.drop_column("curriculos", "original_filename")
