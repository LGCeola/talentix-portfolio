"""Initial Talentix schema.

Revision ID: 20260917_0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260917_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  user_type = sa.Enum("candidate", "recruiter", name="tipo_usuario")
  vacancy_status = sa.Enum("open", "closed", name="status_vaga")
  criterion_type = sa.Enum("habilidade", "experiencia", "formacao", name="tipo_criterio")
  application_status = sa.Enum("pending", "approved", "rejected", name="status_candidatura")

  op.create_table("usuarios", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("email", sa.String(100), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("user_type", user_type, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.UniqueConstraint("email"))
  op.create_index("ix_usuarios_email", "usuarios", ["email"])
  op.create_table("vagas", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("recruiter_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False), sa.Column("title", sa.String(100), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("status", vacancy_status, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
  op.create_index("ix_vagas_recruiter_id", "vagas", ["recruiter_id"])
  op.create_table("criterios_vaga", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("vacancy_id", sa.Integer(), sa.ForeignKey("vagas.id"), nullable=False), sa.Column("name", sa.String(50), nullable=False), sa.Column("criterion_type", criterion_type, nullable=False), sa.Column("weight", sa.Numeric(4, 2), nullable=False))
  op.create_index("ix_criterios_vaga_vacancy_id", "criterios_vaga", ["vacancy_id"])
  op.create_table("curriculos", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False), sa.Column("file_url", sa.String(255), nullable=False), sa.Column("extracted_text", sa.Text(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))
  op.create_index("ix_curriculos_candidate_id", "curriculos", ["candidate_id"])
  op.create_table("candidaturas_ranking", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("candidate_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False), sa.Column("vacancy_id", sa.Integer(), sa.ForeignKey("vagas.id"), nullable=False), sa.Column("resume_id", sa.Integer(), sa.ForeignKey("curriculos.id"), nullable=False), sa.Column("status", application_status, nullable=False), sa.Column("overall_score", sa.Numeric(5, 2)), sa.Column("score_details", sa.JSON()), sa.Column("improvement_suggestions", sa.Text()), sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.UniqueConstraint("candidate_id", "vacancy_id", name="uq_candidatura_candidato_vaga"))
  op.create_index("ix_candidaturas_ranking_candidate_id", "candidaturas_ranking", ["candidate_id"])
  op.create_index("ix_candidaturas_ranking_vacancy_id", "candidaturas_ranking", ["vacancy_id"])
  op.create_table("relatorios", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("application_id", sa.Integer(), sa.ForeignKey("candidaturas_ranking.id"), nullable=False), sa.Column("final_score", sa.Float(), nullable=False), sa.Column("summary", sa.Text(), nullable=False), sa.Column("strong_points", sa.Text(), nullable=False), sa.Column("recommendation_points", sa.Text(), nullable=False), sa.Column("suggestions", sa.Text(), nullable=False), sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False), sa.UniqueConstraint("application_id"))
  op.create_table("pontuacoes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("report_id", sa.Integer(), sa.ForeignKey("relatorios.id"), nullable=False), sa.Column("criterion", sa.String(255), nullable=False), sa.Column("weight", sa.Numeric(4, 2), nullable=False), sa.Column("score_obtained", sa.Numeric(5, 2), nullable=False), sa.Column("justification", sa.Text(), nullable=False))
  op.create_index("ix_pontuacoes_report_id", "pontuacoes", ["report_id"])


def downgrade() -> None:
  op.drop_index("ix_pontuacoes_report_id", table_name="pontuacoes")
  op.drop_table("pontuacoes")
  op.drop_table("relatorios")
  op.drop_index("ix_candidaturas_ranking_vacancy_id", table_name="candidaturas_ranking")
  op.drop_index("ix_candidaturas_ranking_candidate_id", table_name="candidaturas_ranking")
  op.drop_table("candidaturas_ranking")
  op.drop_index("ix_curriculos_candidate_id", table_name="curriculos")
  op.drop_table("curriculos")
  op.drop_index("ix_criterios_vaga_vacancy_id", table_name="criterios_vaga")
  op.drop_table("criterios_vaga")
  op.drop_index("ix_vagas_recruiter_id", table_name="vagas")
  op.drop_table("vagas")
  op.drop_index("ix_usuarios_email", table_name="usuarios")
  op.drop_table("usuarios")
