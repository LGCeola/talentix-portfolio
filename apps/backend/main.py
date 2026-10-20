from fastapi import FastAPI

from apps.backend.api.auth import router as auth_router
from apps.backend.api.curriculos import router as curriculos_router
from apps.backend.api.vagas import router as vagas_router

app = FastAPI(
  title = "Talentix",
  version = "1.0.0"
)

app.include_router(auth_router)
app.include_router(curriculos_router)
app.include_router(vagas_router)

@app.get("/")
def root():
  return { "message": "Talentix API funcionando!" }
