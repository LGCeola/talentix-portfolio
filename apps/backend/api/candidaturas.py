from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import require_role
from apps.backend.database.connection import get_db
from apps.backend.models.candidatura import Application
from apps.backend.models.usuario import User, UserType
from apps.backend.schemas.CandidaturaRequest import CandidaturaRequest
from apps.backend.schemas.CandidaturaResponse import MinhaCandidaturaResponse
from apps.backend.services.CandidaturaService import CandidaturaService

router = APIRouter(prefix="/api/candidaturas", tags=["Candidaturas"])
service = CandidaturaService()
candidate_only = require_role(UserType.CANDIDATE)


@router.post("", response_model=MinhaCandidaturaResponse, status_code=status.HTTP_201_CREATED)
def apply(payload: CandidaturaRequest, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> Application:
  return service.apply(db, current_user, payload)


@router.get("/minhas", response_model=list[MinhaCandidaturaResponse])
def list_mine(db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> list[Application]:
  return service.list_mine(db, current_user)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> None:
  service.withdraw(db, current_user, application_id)
