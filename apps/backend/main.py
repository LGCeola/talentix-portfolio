from fastapi import FastAPI

app = FastAPI(
  title = "Talentix",
  version = "1.0.0"
)

@app.get("/")
def root():
  return { "message": "Talentix API funcionando!" }