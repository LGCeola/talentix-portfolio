from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class Report(Base):
  __tablename__ = "relatorios"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  application_id: Mapped[int] = mapped_column(Integer, ForeignKey("candidaturas_ranking.id"), nullable=False, unique=True)
  final_score: Mapped[float] = mapped_column(Float, nullable=False)
  summary: Mapped[str] = mapped_column(Text, nullable=False)
  strong_points: Mapped[str] = mapped_column(Text, nullable=False)
  recommendation_points: Mapped[str] = mapped_column(Text, nullable=False)
  suggestions: Mapped[str] = mapped_column(Text, nullable=False)
  generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  application: Mapped["Application"] = relationship()
