from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class Report(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  candidature_id: Mapped[int] = mapped_column(Integer, ForeignKey("application.id"), nullable=False)
  final_score: Mapped[float] = mapped_column(Float, nullable=False)
  resume: Mapped[str] = mapped_column(String(255), nullable=False)
  strong_points: Mapped[str] = mapped_column(String(255), nullable=False)
  recomendation_points: Mapped[str] = mapped_column(String(255), nullable=False)
  suggestions: Mapped[str] = mapped_column(String(255), nullable=False)
  generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
