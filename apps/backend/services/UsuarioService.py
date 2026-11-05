import logging
import shutil
from pathlib import Path

from sqlalchemy.orm import Session

from apps.backend.core.config import settings
from apps.backend.core.exceptions import EmailJaCadastrado, RegraDeNegocioViolada, SenhaIncorreta
from apps.backend.core.security import verify_password
from apps.backend.models.usuario import User
from apps.backend.repositories.UsuarioRepository import UsuarioRepository
from apps.backend.schemas.Usuario import UserUpdate

logger = logging.getLogger(__name__)


class UsuarioService:
  def __init__(self, repository: UsuarioRepository | None = None, upload_dir: Path | None = None):
    self.repository = repository or UsuarioRepository()
    self.upload_dir = upload_dir or settings.UPLOAD_DIR

  def update(self, db: Session, user: User, payload: UserUpdate) -> User:
    if payload.email != user.email:
      # O e-mail é o login da conta: trocá-lo exige confirmar que é mesmo o dono.
      if not payload.current_password:
        raise RegraDeNegocioViolada("Informe sua senha atual para alterar o e-mail")
      self._ensure_password(user, payload.current_password)
      if self.repository.get_by_email(db, payload.email):
        raise EmailJaCadastrado()
    user.name = payload.name
    user.email = payload.email
    return self.repository.save(db, user)

  def delete_account(self, db: Session, user: User, password: str) -> None:
    """Exclusão definitiva (LGPD, RFC 6.1): dados do banco e arquivos, inclusive candidaturas já avaliadas."""
    self._ensure_password(user, password)
    user_uploads = self.upload_dir / str(user.id)
    self.repository.delete_with_data(db, user)

    # O banco vem primeiro: se o arquivo falhar, a conta já foi removida e o resto fica registrado para limpeza manual.
    try:
      if user_uploads.exists():
        shutil.rmtree(user_uploads)
    except OSError:
      logger.exception("Falha ao remover os arquivos da conta excluída: %s", user_uploads)

  def _ensure_password(self, user: User, password: str) -> None:
    if not verify_password(password, user.password_hash):
      raise SenhaIncorreta()
