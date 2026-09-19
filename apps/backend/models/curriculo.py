from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.backend.database.connection import Base

class Resume(Base):
  __tablename__ = "curriculos"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  candidate_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
  file_url: Mapped[str] = mapped_column(String(255), nullable=False)
  extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
  updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

  candidate: Mapped["User"] = relationship(back_populates="resumes", foreign_keys=[candidate_id])
  applications: Mapped[list["Application"]] = relationship(back_populates="resume")
