from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, JSON, Numeric, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class ApplicationStatus(str, Enum):
  PENDING = "pending"
  APPROVED = "approved"
  REJECTED = "rejected"

class Application(Base):
  __tablename__ = "candidaturas_ranking"
  __table_args__ = (UniqueConstraint("candidate_id", "vacancy_id", name="uq_candidatura_candidato_vaga"),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
  vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vagas.id"), nullable=False, index=True)
  resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("curriculos.id"), nullable=False)
  status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus, name="status_candidatura"), default=ApplicationStatus.PENDING, nullable=False)
  overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
  score_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  improvement_suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
  applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  candidate: Mapped["User"] = relationship(back_populates="applications", foreign_keys=[candidate_id])
  vacancy: Mapped["Vacancy"] = relationship(back_populates="applications")
  resume: Mapped["Resume"] = relationship(back_populates="applications")
