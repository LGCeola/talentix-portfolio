from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class Score(Base):
  __tablename__ = "pontuacoes"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  report_id: Mapped[int] = mapped_column(Integer, ForeignKey("relatorios.id"), nullable=False, index=True)
  criterion: Mapped[str] = mapped_column(String(255), nullable=False)
  weight: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
  score_obtained: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
  justification: Mapped[str] = mapped_column(Text, nullable=False)

  report: Mapped["Report"] = relationship()
