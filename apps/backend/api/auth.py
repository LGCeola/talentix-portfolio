from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import get_current_user
from apps.backend.core.security import create_access_token
from apps.backend.database.connection import get_db
from apps.backend.models.usuario import User
from apps.backend.schemas.LoginRequest import LoginRequest
from apps.backend.schemas.LoginResponse import LoginResponse
from apps.backend.schemas.usuario import UserCreate, UserResponse
from apps.backend.services.AuthService import AuthService

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])
service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
  return service.register(db, payload)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
  user = service.authenticate(db, payload.email, payload.password)
  token = create_access_token(user.id, user.user_type.value)
  return LoginResponse(access_token=token, user=user)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
  return current_user
