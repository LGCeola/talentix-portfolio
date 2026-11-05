from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import get_current_user
from apps.backend.database.connection import get_db
from apps.backend.models.usuario import User
from apps.backend.schemas.Usuario import AccountDeleteRequest, UserResponse, UserUpdate
from apps.backend.services.UsuarioService import UsuarioService

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])
service = UsuarioService()


@router.patch("/me", response_model=UserResponse)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
  return service.update(db, current_user, payload)


@router.post("/me/exclusao", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(payload: AccountDeleteRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
  service.delete_account(db, current_user, payload.password)
