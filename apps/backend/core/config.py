from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve o .env sempre relativo a este arquivo (apps/backend/.env),
# independentemente do diretório de trabalho em que o processo for iniciado.
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
  APP_NAME: str = "Talentix"
  APP_VERSION: str = "1.0.0"

  DATABASE_URL: str

  JWT_SECRET_KEY: str
  JWT_ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
  REFRESH_TOKEN_EXPIRE_DAYS: int = 7

  class Config:
    env_file = str(_ENV_FILE)


settings = Settings()