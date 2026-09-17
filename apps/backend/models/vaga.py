from enum import Enum
from sqlalchemy import Integer, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class VacancyStatus(str, Enum):
  OPEN = "open"
  CLOSED = "closed"

class Vacancy(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  recruiter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  title: Mapped[str] = mapped_column(String(255), nullable=False)
  description: Mapped[str] = mapped_column(String(255), nullable=False)
  requirements: Mapped[str] = mapped_column(String(255), nullable=False)
  status: Mapped[VacancyStatus] = mapped_column(SQLEnum(VacancyStatus), nullable=False)