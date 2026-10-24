from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import require_role
from apps.backend.database.connection import get_db
from apps.backend.models.curriculo import Resume
from apps.backend.models.usuario import User, UserType
from apps.backend.schemas.CurriculoResponse import CurriculoDetailResponse, CurriculoResponse
from apps.backend.services.CurriculoService import CurriculoService

router = APIRouter(prefix="/api/curriculos", tags=["Currículos"])
service = CurriculoService()
candidate_only = require_role(UserType.CANDIDATE)


@router.post("", response_model=CurriculoResponse, status_code=status.HTTP_201_CREATED)
def upload(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> Resume:
  return service.upload(db, current_user, file.filename, file.file)


@router.get("", response_model=list[CurriculoResponse])
def list_mine(db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> list[Resume]:
  return service.list_mine(db, current_user)


@router.get("/{resume_id}", response_model=CurriculoDetailResponse)
def get_mine(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> Resume:
  return service.get_mine(db, current_user, resume_id)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(resume_id: int, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> None:
  service.delete(db, current_user, resume_id)
