from pydantic import BaseModel

from apps.backend.schemas.Usuario import UserResponse


class LoginResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"
  user: UserResponse
