from fastapi import FastAPI

from apps.backend.api.auth import router as auth_router
from apps.backend.api.candidaturas import router as candidaturas_router
from apps.backend.api.curriculos import router as curriculos_router
from apps.backend.api.vagas import router as vagas_router
from apps.backend.core.exception_handlers import register_exception_handlers

app = FastAPI(
  title = "Talentix",
  version = "1.0.0"
)

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(curriculos_router)
app.include_router(vagas_router)
app.include_router(candidaturas_router)

@app.get("/")
def root():
  return { "message": "Talentix API funcionando!" }
