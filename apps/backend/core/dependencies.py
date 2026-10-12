from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from apps.backend.database.connection import get_db
from apps.backend.core.security import decode_access_token
from apps.backend.models.usuario import User, UserType


oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="/api/auth/login"
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
  try:
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    user_type = payload.get("user_type")

    if not user_id or not user_type:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido"
      )

    user = db.get(User, int(user_id))
    if not user or user.user_type.value != user_type:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido"
      )
    return user

  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Não foi possível autenticar o usuário"
    )


def require_role(*allowed: UserType):
  """Restringe a rota aos perfis informados (ex.: apenas candidatos)."""
  def checker(current_user: User = Depends(get_current_user)) -> User:
    if current_user.user_type not in allowed:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para acessar este recurso"
      )
    return current_user

  return checker
