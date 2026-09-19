from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class UserType(str, Enum):
  CANDIDATE = "candidate"
  RECRUITER = "recruiter"

class User(Base):
  __tablename__ = "usuarios"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  name: Mapped[str] = mapped_column(String(100), nullable=False)
  email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
  password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
  user_type: Mapped[UserType] = mapped_column(SQLEnum(UserType, name="tipo_usuario"), nullable=False)
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  vacancies: Mapped[list["Vacancy"]] = relationship(back_populates="recruiter", foreign_keys="Vacancy.recruiter_id")
  resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", foreign_keys="Resume.candidate_id")
  applications: Mapped[list["Application"]] = relationship(back_populates="candidate", foreign_keys="Application.candidate_id")
