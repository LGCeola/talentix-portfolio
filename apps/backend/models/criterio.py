from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class CriterionType(str, Enum):
  SKILL = "habilidade"
  EXPERIENCE = "experiencia"
  EDUCATION = "formacao"


class Criterion(Base):
  __tablename__ = "criterios_vaga"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vagas.id"), nullable=False, index=True)
  name: Mapped[str] = mapped_column(String(50), nullable=False)
  criterion_type: Mapped[CriterionType] = mapped_column(SQLEnum(CriterionType, name="tipo_criterio"), nullable=False)
  weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)

  vacancy: Mapped["Vacancy"] = relationship(back_populates="criteria")
