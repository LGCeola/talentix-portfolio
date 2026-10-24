from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.backend.core.dependencies import get_current_user, require_role
from apps.backend.database.connection import get_db
from apps.backend.models.candidatura import Application
from apps.backend.models.usuario import User, UserType
from apps.backend.models.vaga import Vacancy
from apps.backend.schemas.CandidaturaResponse import CandidaturaRecebidaResponse
from apps.backend.schemas.VagaRequest import VagaRequest, VagaStatusRequest
from apps.backend.schemas.VagaResponse import VagaPublicaResponse, VagaResponse, VagaResumoResponse
from apps.backend.services.CandidaturaService import CandidaturaService
from apps.backend.services.VagaService import VagaService

router = APIRouter(prefix="/api/vagas", tags=["Vagas"])
service = VagaService()
candidaturas = CandidaturaService()
recruiter_only = require_role(UserType.RECRUITER)
candidate_only = require_role(UserType.CANDIDATE)


@router.get("", response_model=list[VagaPublicaResponse])
def list_open(db: Session = Depends(get_db), current_user: User = Depends(candidate_only)) -> list[VagaPublicaResponse]:
  return service.list_open(db, current_user)


@router.get("/minhas", response_model=list[VagaResumoResponse])
def list_mine(db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> list[VagaResumoResponse]:
  return service.list_mine(db, current_user)


@router.post("", response_model=VagaResponse, status_code=status.HTTP_201_CREATED)
def create(payload: VagaRequest, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> Vacancy:
  return service.create(db, current_user, payload)


@router.get("/{vacancy_id}", response_model=VagaResponse)
def get_one(vacancy_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Vacancy:
  return service.get_visible(db, current_user, vacancy_id)


@router.get("/{vacancy_id}/candidaturas", response_model=list[CandidaturaRecebidaResponse])
def list_applications(vacancy_id: int, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> list[Application]:
  return candidaturas.list_received(db, current_user, vacancy_id)


@router.put("/{vacancy_id}", response_model=VagaResponse)
def update(vacancy_id: int, payload: VagaRequest, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> Vacancy:
  return service.update(db, current_user, vacancy_id, payload)


@router.patch("/{vacancy_id}/status", response_model=VagaResponse)
def change_status(vacancy_id: int, payload: VagaStatusRequest, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> Vacancy:
  return service.change_status(db, current_user, vacancy_id, payload.status)


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(vacancy_id: int, db: Session = Depends(get_db), current_user: User = Depends(recruiter_only)) -> None:
  service.delete(db, current_user, vacancy_id)
