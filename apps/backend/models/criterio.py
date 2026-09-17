from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class Criterion(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  vacancy_id: Mapped[int] = mapped_column(Integer, ForeignKey("vacancy.id"), nullable=False)
  name: Mapped[str] = mapped_column(String(255), nullable=False)
  description: Mapped[str] = mapped_column(String(255), nullable=False)
  ponderation: Mapped[int] = mapped_column(Integer, nullable=False)
  