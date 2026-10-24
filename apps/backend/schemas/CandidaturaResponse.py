from datetime import datetime

from pydantic import BaseModel

from apps.backend.models.candidatura import ApplicationStatus
from apps.backend.models.vaga import VacancyStatus


class VagaResumidaResponse(BaseModel):
  id: int
  title: str
  status: VacancyStatus

  model_config = {"from_attributes": True}


class CurriculoResumidoResponse(BaseModel):
  id: int
  original_filename: str

  model_config = {"from_attributes": True}


class CandidatoResponse(BaseModel):
  id: int
  name: str
  email: str

  model_config = {"from_attributes": True}


class _CandidaturaBase(BaseModel):
  id: int
  status: ApplicationStatus
  # Preenchida pelo algoritmo de avaliação (M5); null enquanto a análise estiver pendente.
  overall_score: float | None
  applied_at: datetime
  resume: CurriculoResumidoResponse

  model_config = {"from_attributes": True}


class MinhaCandidaturaResponse(_CandidaturaBase):
  """Visão do candidato sobre as próprias candidaturas."""
  vacancy: VagaResumidaResponse


class CandidaturaRecebidaResponse(_CandidaturaBase):
  """Visão do recrutador sobre quem se candidatou à vaga."""
  candidate: CandidatoResponse
  consent_at: datetime
