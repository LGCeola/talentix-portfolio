from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from apps.backend.core.exceptions import CandidaturaDuplicada
from apps.backend.models.candidatura import Application


class CandidaturaRepository:
  def list_by_candidate(self, db: Session, candidate_id: int) -> list[Application]:
    query = (
      select(Application)
      .where(Application.candidate_id == candidate_id)
      .options(joinedload(Application.vacancy), joinedload(Application.resume))
      .order_by(Application.applied_at.desc(), Application.id.desc())
    )
    return list(db.scalars(query))

  def list_by_vacancy(self, db: Session, vacancy_id: int) -> list[Application]:
    query = (
      select(Application)
      .where(Application.vacancy_id == vacancy_id)
      .options(joinedload(Application.candidate), joinedload(Application.resume))
      .order_by(Application.applied_at.asc(), Application.id.asc())
    )
    return list(db.scalars(query))

  def vacancy_ids_applied_by(self, db: Session, candidate_id: int) -> set[int]:
    return set(db.scalars(select(Application.vacancy_id).where(Application.candidate_id == candidate_id)))

  def get_by_id_and_candidate(self, db: Session, application_id: int, candidate_id: int) -> Application | None:
    return db.scalar(select(Application).where(Application.id == application_id, Application.candidate_id == candidate_id))

  def create(self, db: Session, application: Application) -> Application:
    db.add(application)
    try:
      db.commit()
    except IntegrityError as error:
      # Duas requisições simultâneas podem passar pela checagem; a constraint do banco é a garantia final.
      db.rollback()
      raise CandidaturaDuplicada() from error
    db.refresh(application)
    return application

  def delete(self, db: Session, application: Application) -> None:
    db.delete(application)
    db.commit()
