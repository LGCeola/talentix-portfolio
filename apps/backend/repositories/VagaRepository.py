from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, selectinload

from apps.backend.models.candidatura import Application
from apps.backend.models.vaga import Vacancy


class VagaRepository:
  def list_by_recruiter_with_counts(self, db: Session, recruiter_id: int) -> list[tuple[Vacancy, int]]:
    applications_count = select(func.count(Application.id)).where(Application.vacancy_id == Vacancy.id).correlate(Vacancy).scalar_subquery()
    query = (
      select(Vacancy, applications_count)
      .where(Vacancy.recruiter_id == recruiter_id)
      .options(selectinload(Vacancy.criteria))
      .order_by(Vacancy.created_at.desc(), Vacancy.id.desc())
    )
    return [(vacancy, count) for vacancy, count in db.execute(query)]

  def get_by_id_and_recruiter(self, db: Session, vacancy_id: int, recruiter_id: int) -> Vacancy | None:
    query = select(Vacancy).where(Vacancy.id == vacancy_id, Vacancy.recruiter_id == recruiter_id).options(selectinload(Vacancy.criteria))
    return db.scalar(query)

  def has_applications(self, db: Session, vacancy_id: int) -> bool:
    return db.scalar(select(exists().where(Application.vacancy_id == vacancy_id)))

  def save(self, db: Session, vacancy: Vacancy) -> Vacancy:
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy

  def delete(self, db: Session, vacancy: Vacancy) -> None:
    db.delete(vacancy)
    db.commit()
