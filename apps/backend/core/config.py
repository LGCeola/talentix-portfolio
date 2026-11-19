from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings

# Resolve o .env sempre relativo a este arquivo (apps/backend/.env),
# independentemente do diretório de trabalho em que o processo for iniciado.
_BACKEND_DIR = Path(__file__).parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
  APP_NAME: str = "Talentix"
  APP_VERSION: str = "1.0.0"

  DATABASE_URL: str

  JWT_SECRET_KEY: str
  JWT_ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
  REFRESH_TOKEN_EXPIRE_DAYS: int = 7

  UPLOAD_DIR: Path = _BACKEND_DIR / "uploads"
  MAX_RESUME_SIZE_MB: int = 5

  # Produção (Azure): com a URL da conta de armazenamento, os currículos vão para o Blob Storage em vez de UPLOAD_DIR.
  AZURE_STORAGE_ACCOUNT_URL: str | None = None
  AZURE_STORAGE_CONTAINER: str = "curriculos"

  # Produção (Azure): com a connection string, requisições, erros, consultas ao banco e logs vão para o Application Insights.
  APPLICATIONINSIGHTS_CONNECTION_STRING: str | None = None
  # Nome do ambiente (dev, prod) nos dados de monitoramento.
  ENVIRONMENT: str = "local"

  # Desligado por padrão: ligar envia currículos anonimizados à TypeSafe, nos EUA, e exige consentimento específico.
  JEV_ENABLED: bool = False
  JEV_SECRET_KEY: SecretStr | None = None
  JEV_MODEL: str = "jev-1.14.0"
  JEV_TIMEOUT_SECONDS: float = 1.5

  class Config:
    env_file = str(_ENV_FILE)


settings = Settings()