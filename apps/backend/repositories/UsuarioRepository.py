from sqlalchemy import delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from apps.backend.core.exceptions import EmailJaCadastrado
from apps.backend.models.candidatura import Application
from apps.backend.models.criterio import Criterion
from apps.backend.models.curriculo import Resume
from apps.backend.models.usuario import User
from apps.backend.models.vaga import Vacancy


class UsuarioRepository:
  def get_by_email(self, db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))

  def get_by_id(self, db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

  def create(self, db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

  def save(self, db: Session, user: User) -> User:
    try:
      db.commit()
    except IntegrityError as error:
      # Duas requisições simultâneas podem passar pela checagem; o índice único é a garantia final (RN06).
      db.rollback()
      raise EmailJaCadastrado() from error
    db.refresh(user)
    return user

  def delete_with_data(self, db: Session, user: User) -> None:
    """Remove o usuário e tudo o que depende dele numa única transação, respeitando as chaves estrangeiras."""
    own_vacancies = select(Vacancy.id).where(Vacancy.recruiter_id == user.id)
    db.execute(delete(Application).where(or_(Application.candidate_id == user.id, Application.vacancy_id.in_(own_vacancies))))
    db.execute(delete(Criterion).where(Criterion.vacancy_id.in_(own_vacancies)))
    db.execute(delete(Vacancy).where(Vacancy.recruiter_id == user.id))
    db.execute(delete(Resume).where(Resume.candidate_id == user.id))
    db.delete(user)
    db.commit()
