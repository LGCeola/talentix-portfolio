"""Add the required level (1-5) to each vacancy criterion; existing criteria get level 3.

Revision ID: 20261111_0007
Revises: 20261102_0006
"""
from alembic import op
import sqlalchemy as sa

revision = "20261111_0007"
down_revision = "20261102_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column("criterios_vaga", sa.Column("required_level", sa.Integer(), nullable=False, server_default="3"))
  op.create_check_constraint("ck_criterios_vaga_required_level_range", "criterios_vaga", "required_level BETWEEN 1 AND 5")


def downgrade() -> None:
  op.drop_constraint("ck_criterios_vaga_required_level_range", "criterios_vaga", type_="check")
  op.drop_column("criterios_vaga", "required_level")
