from sqlalchemy.orm import Session

from apps.backend.core.exceptions import CredenciaisInvalidas, EmailJaCadastrado
from apps.backend.core.security import hash_password, verify_password
from apps.backend.models.usuario import User
from apps.backend.repositories.UsuarioRepository import UsuarioRepository
from apps.backend.schemas.Usuario import UserCreate


class AuthService:
  def __init__(self, repository: UsuarioRepository | None = None):
    self.repository = repository or UsuarioRepository()

  def register(self, db: Session, payload: UserCreate) -> User:
    if self.repository.get_by_email(db, payload.email):
      raise EmailJaCadastrado()
    user = User(name=payload.name.strip(), email=payload.email, password_hash=hash_password(payload.password), user_type=payload.user_type)
    return self.repository.create(db, user)

  def authenticate(self, db: Session, email: str, password: str) -> User:
    user = self.repository.get_by_email(db, email.strip().lower())
    if not user or not verify_password(password, user.password_hash):
      raise CredenciaisInvalidas()
    return user
