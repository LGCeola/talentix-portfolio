from fastapi import FastAPI

from apps.backend.api.auth import router as auth_router
from apps.backend.api.candidaturas import router as candidaturas_router
from apps.backend.api.curriculos import router as curriculos_router
from apps.backend.api.health import router as health_router
from apps.backend.api.usuarios import router as usuarios_router
from apps.backend.api.vagas import router as vagas_router
from apps.backend.core.config import settings
from apps.backend.core.exception_handlers import register_exception_handlers
from apps.backend.core.monitoring import setup_monitoring

app = FastAPI(
  title = "Talentix",
  version = settings.APP_VERSION
)

register_exception_handlers(app)
setup_monitoring(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(curriculos_router)
app.include_router(vagas_router)
app.include_router(candidaturas_router)
app.include_router(usuarios_router)

@app.get("/")
def root():
  return { "message": "Talentix API funcionando!" }
