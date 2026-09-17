from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class Score(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  review_id: Mapped[int] = mapped_column(Integer, ForeignKey("review.id"), nullable=False)
  criterion: Mapped[str] = mapped_column(String(255), nullable=False)
  ponderation: Mapped[int] = mapped_column(Integer, nullable=False)
  score_obtained: Mapped[int] = mapped_column(Integer, nullable=False)
  justification: Mapped[str] = mapped_column(String(255), nullable=False)
  