from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from apps.backend.database.connection import Base

class Resume(Base):
  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  candidate_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
  file: Mapped[str] = mapped_column(String(255), nullable=False)
  extract_text: Mapped[str] = mapped_column(String(255), nullable=False)
  send_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
