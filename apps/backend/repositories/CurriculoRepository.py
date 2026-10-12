from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from apps.backend.models.candidatura import Application
from apps.backend.models.curriculo import Resume


class CurriculoRepository:
  def list_by_candidate(self, db: Session, candidate_id: int) -> list[Resume]:
    query = select(Resume).where(Resume.candidate_id == candidate_id).order_by(Resume.updated_at.desc(), Resume.id.desc())
    return list(db.scalars(query))

  def get_by_id_and_candidate(self, db: Session, resume_id: int, candidate_id: int) -> Resume | None:
    return db.scalar(select(Resume).where(Resume.id == resume_id, Resume.candidate_id == candidate_id))

  def has_applications(self, db: Session, resume_id: int) -> bool:
    return db.scalar(select(exists().where(Application.resume_id == resume_id)))

  def create(self, db: Session, resume: Resume) -> Resume:
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume

  def delete(self, db: Session, resume: Resume) -> None:
    db.delete(resume)
    db.commit()
