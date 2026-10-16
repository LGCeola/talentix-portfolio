"""Add draft status to vagas and store criterion weights as integer percentages.

Revision ID: 20261012_0003
Revises: 20261011_0002
"""
from alembic import op
import sqlalchemy as sa

revision = "20261012_0003"
down_revision = "20261011_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
  # ALTER TYPE ... ADD VALUE não pode rodar dentro de uma transação junto com o uso do novo valor.
  with op.get_context().autocommit_block():
    op.execute("ALTER TYPE status_vaga ADD VALUE IF NOT EXISTS 'draft' BEFORE 'open'")

  op.alter_column("criterios_vaga", "weight", type_=sa.Integer(), existing_type=sa.Numeric(4, 2), existing_nullable=False, postgresql_using="round(weight)::integer")
  op.create_check_constraint("ck_criterios_vaga_weight_range", "criterios_vaga", "weight BETWEEN 1 AND 100")


def downgrade() -> None:
  op.drop_constraint("ck_criterios_vaga_weight_range", "criterios_vaga", type_="check")
  op.alter_column("criterios_vaga", "weight", type_=sa.Numeric(5, 2), existing_type=sa.Integer(), existing_nullable=False)

  # O Postgres não remove valores de enum: recria o tipo sem 'draft'.
  op.execute("UPDATE vagas SET status = 'closed' WHERE status = 'draft'")
  op.execute("ALTER TYPE status_vaga RENAME TO status_vaga_old")
  op.execute("CREATE TYPE status_vaga AS ENUM ('open', 'closed')")
  op.execute("ALTER TABLE vagas ALTER COLUMN status TYPE status_vaga USING status::text::status_vaga")
  op.execute("DROP TYPE status_vaga_old")
