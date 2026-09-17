from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from apps.backend.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
  tokenUrl="/api/auth/login"
)


def get_current_user(
  token: str = Depends(oauth2_scheme)
):
  try:
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    user_type = payload.get("user_type")

    if not user_id or not user_type:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido"
      )

    return {
      "id": int(user_id),
      "user_type": user_type
    }

  except Exception:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Não foi possível autenticar o usuário"
    )