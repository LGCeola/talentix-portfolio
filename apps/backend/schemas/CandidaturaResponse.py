from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from apps.backend.models.candidatura import ApplicationStatus
from apps.backend.models.criterio import CriterionType
from apps.backend.models.vaga import VacancyStatus


class ConsentimentoResponse(BaseModel):
  """Indica se o consentimento precisa informar o envio do currículo a um modelo externo."""
  external_analysis: bool


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


class CriterioAnaliseResponse(BaseModel):
  name: str
  criterion_type: CriterionType
  weight: int
  status: Literal["present", "absent", "review"]
  points: float
  source: str
  evidence: str | None = None
  # Versão 3 do algoritmo: nível exigido pela vaga e nível estimado pelo Jev (0 a 5).
  required_level: int | None = None
  level: int | None = None
  confidence: float | None = None
  # Versão 2: probabilidade de o critério estar presente. Mantida para candidaturas antigas.
  probability: float | None = None
  model_version: str | None = None


class AnaliseDetalhesResponse(BaseModel):
  algorithm_version: str
  # "levels" (nível estimado pelo Jev) ou "keywords" (só busca por termos); nulo em versões antigas.
  analysis_mode: str | None = None
  criteria: list[CriterioAnaliseResponse]


class CompatibilidadeResponse(BaseModel):
  """Simulação do candidato antes de se candidatar; nada é gravado nem compartilhado."""
  score: float
  analysis_mode: str
  criteria: list[CriterioAnaliseResponse]
  suggestions: list[str]


class _CandidaturaBase(BaseModel):
  id: int
  status: ApplicationStatus
  # Null apenas em candidaturas anteriores à análise automática.
  overall_score: float | None
  score_details: AnaliseDetalhesResponse | None
  improvement_suggestions: str | None
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
