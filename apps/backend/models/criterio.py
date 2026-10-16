from enum import Enum

from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class CriterionType(str, Enum):
  SKILL = "habilidade"
  EXPERIENCE = "experiencia"
  EDUCATION = "formacao"


class Criterion(Base):
  __tablename__ = "criterios_vaga"
  __table_args__ = (CheckConstraint("weight BETWEEN 1 AND 100", name="ck_criterios_vaga_weight_range"),)

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vagas.id"), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  criterion_type: Mapped[CriterionType] = mapped_column(SQLEnum(CriterionType, name="tipo_criterio", values_callable=lambda enum: [member.value for member in enum]), nullable=False)
  # Percentual da nota final (1–100); os pesos de uma vaga publicada somam 100.
  weight: Mapped[int] = mapped_column(Integer, nullable=False)

  vacancy: Mapped["Vacancy"] = relationship(back_populates="criteria")
