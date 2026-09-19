from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from apps.backend.models.usuario import UserType


class UserCreate(BaseModel):
  name: str = Field(min_length=2, max_length=100)
  email: str = Field(min_length=5, max_length=100)
  password: str = Field(min_length=8, max_length=128)
  user_type: UserType

  @field_validator("email")
  @classmethod
  def normalize_email(cls, value: str) -> str:
    normalized = value.strip().lower()
    if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
      raise ValueError("E-mail inválido")
    return normalized


class UserResponse(BaseModel):
  id: int
  name: str
  email: str
  user_type: UserType
  created_at: datetime

  model_config = {"from_attributes": True}
