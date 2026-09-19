from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.backend.models.usuario import User


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
