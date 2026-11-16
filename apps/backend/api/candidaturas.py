from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import require_role
from apps.backend.database.connection import get_db
from apps.backend.models.candidatura import Application
from apps.backend.models.usuario import User, UserType
from apps.backend.schemas.CandidaturaRequest import CandidaturaRequest, CandidaturaStatusRequest
from apps.backend.schemas.CandidaturaResponse import CandidaturaRecebidaResponse, ConsentimentoResponse, MinhaCandidaturaResponse
from apps.backend.services.CandidaturaService import CandidaturaService

router = APIRouter(prefix="/api/candidaturas", tags=["Candidaturas"])
service = CandidaturaService()
candidate_only = require_role(UserType.CANDIDATE)
recruiter_only = require_role(UserType.RECRUITER)


@router.post("", response_model=MinhaCandidaturaResponse, status_code=status.HTTP_201_CREATED)
def apply(payload: CandidaturaRequest, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> Application:
  return service.apply(db, current_user, payload)


@router.get("/consentimento", response_model=ConsentimentoResponse)
def consent_terms(_: User = Depends(candidate_only)) -> ConsentimentoResponse:
  return ConsentimentoResponse(external_analysis=service.uses_external_analysis())


@router.get("/minhas", response_model=list[MinhaCandidaturaResponse])
def list_mine(db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> list[Application]:
  return service.list_mine(db, current_user)


@router.patch("/{application_id}/status", response_model=CandidaturaRecebidaResponse)
def decide(application_id: int, payload: CandidaturaStatusRequest, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> Application:
  return service.decide(db, current_user, application_id, payload.status)


_MEDIA_TYPES = {".pdf": "application/pdf", ".txt": "text/plain; charset=utf-8"}


@router.get("/{application_id}/curriculo", response_class=FileResponse)
def download_resume(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> FileResponse:
  path, filename = service.received_resume(db, current_user, application_id)
  return FileResponse(
    path,
    media_type=_MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream"),
    filename=filename,
    # Dados pessoais: o navegador não deve guardar cópia em cache.
    headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
  )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def withdraw(application_id: int, db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> None:
  service.withdraw(db, current_user, application_id)
