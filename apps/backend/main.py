from fastapi import FastAPI

from apps.backend.api.auth import router as auth_router

app = FastAPI(
  title = "Talentix",
  version = "1.0.0"
)

app.include_router(auth_router)

@app.get("/")
def root():
  return { "message": "Talentix API funcionando!" }
