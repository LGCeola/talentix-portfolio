from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from apps.backend.core.config import settings

engine = create_engine(
  settings.DATABASE_URL,
  echo=False,
  pool_pre_ping=True
)

SessionLocal = sessionmaker(
  bind=engine,
  autocommit=False,
  autoflush=False,
  expire_on_commit=False,
)

class Base(DeclarativeBase):
  pass

def get_db():
  db = SessionLocal()

  try:
    yield db
  finally:
    db.close()
