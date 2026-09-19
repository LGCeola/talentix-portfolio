from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class VacancyStatus(str, Enum):
  OPEN = "open"
  CLOSED = "closed"

class Vacancy(Base):
  __tablename__ = "vagas"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  recruiter_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
  title: Mapped[str] = mapped_column(String(100), nullable=False)
  description: Mapped[str] = mapped_column(Text, nullable=False)
  status: Mapped[VacancyStatus] = mapped_column(SQLEnum(VacancyStatus, name="status_vaga"), default=VacancyStatus.OPEN, nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  recruiter: Mapped["User"] = relationship(back_populates="vacancies", foreign_keys=[recruiter_id])
  criteria: Mapped[list["Criterion"]] = relationship(back_populates="vacancy", cascade="all, delete-orphan")
  applications: Mapped[list["Application"]] = relationship(back_populates="vacancy", cascade="all, delete-orphan")
