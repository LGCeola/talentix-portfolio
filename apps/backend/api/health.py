from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from apps.backend.core.config import settings
from apps.backend.database.connection import get_db

router = APIRouter(prefix="/api", tags=["Saúde"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> JSONResponse:
  """Usada pela Azure para saber se o contêiner pode receber tráfego e pelo alerta de disponibilidade."""
  try:
    db.execute(text("SELECT 1"))
  except SQLAlchemyError:
    return JSONResponse({"status": "unavailable", "database": "down"}, status_code=503)
  return JSONResponse({"status": "ok", "database": "up", "version": settings.APP_VERSION})
