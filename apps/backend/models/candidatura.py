from datetime import datetime
from enum import Enum
from sqlalchemy import DateTime, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class ApplicationStatus(str, Enum):
  PENDING = "pending"
  APPROVED = "approved"
  REJECTED = "rejected"

class Application(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  candidate_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidate.id"), nullable=False)
  vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancy.id"), nullable=False)
  resume_id: Mapped[int] = mapped_column(Integer, ForeignKey("resume.id"), nullable=False)
  status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), nullable=False)
  applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
