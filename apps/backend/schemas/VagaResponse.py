from datetime import datetime

from pydantic import BaseModel

from apps.backend.models.criterio import CriterionType
from apps.backend.models.vaga import VacancyStatus


class CriterioResponse(BaseModel):
  id: int
  name: str
  criterion_type: CriterionType
  weight: int

  model_config = {"from_attributes": True}


class VagaResponse(BaseModel):
  id: int
  title: str
  description: str
  status: VacancyStatus
  created_at: datetime
  criteria: list[CriterioResponse]

  model_config = {"from_attributes": True}


class VagaPublicaResponse(BaseModel):
  """Vaga publicada, como o candidato a vê: critérios e pesos visíveis (transparência, RNF06)."""
  id: int
  title: str
  description: str
  created_at: datetime
  criteria: list[CriterioResponse]
  already_applied: bool


class VagaResumoResponse(BaseModel):
  id: int
  title: str
  status: VacancyStatus
  created_at: datetime
  criteria_count: int
  applications_count: int
