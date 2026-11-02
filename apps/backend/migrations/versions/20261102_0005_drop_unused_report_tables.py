"""Drop relatorios and pontuacoes: analysis results live in candidaturas_ranking.

Revision ID: 20261102_0005
Revises: 20261020_0004
"""
from alembic import op
import sqlalchemy as sa

revision = "20261102_0005"
down_revision = "20261020_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.drop_index("ix_pontuacoes_report_id", table_name="pontuacoes")
  op.drop_table("pontuacoes")
  op.drop_table("relatorios")


def downgrade() -> None:
  op.create_table("relatorios", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("application_id", sa.Integer(), sa.ForeignKey("candidaturas_ranking.id"), nullable=False), sa.Column("final_score", sa.Float(), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("strong_points", sa.Text(), nullable=False), sa.Column("recommendation_points", sa.Text(), nullable=False), sa.Column("suggestions", sa.Text(), nullable=False), sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.UniqueConstraint("application_id"))
  op.create_table("pontuacoes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("report_id", sa.Integer(), sa.ForeignKey("relatorios.id"), nullable=False), sa.Column("criterion", sa.String(255), nullable=False), sa.Column("weight", sa.Numeric(4, 2), nullable=False), sa.Column("score_obtained", sa.Numeric(5, 2), nullable=False), sa.Column("justification", sa.Text(), nullable=False))
  op.create_index("ix_pontuacoes_report_id", "pontuacoes", ["report_id"])
