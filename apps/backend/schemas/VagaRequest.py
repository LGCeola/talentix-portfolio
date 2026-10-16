from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from apps.backend.models.criterio import CriterionType
from apps.backend.models.vaga import VacancyStatus


class CriterioRequest(BaseModel):
  name: str = Field(min_length=2, max_length=50)
  criterion_type: CriterionType
  weight: int = Field(ge=1, le=100, description="Percentual da nota final")

  @field_validator("name")
  @classmethod
  def strip_name(cls, value: str) -> str:
    return value.strip()


class VagaRequest(BaseModel):
  """Conteúdo da vaga. Rascunhos podem estar incompletos; a publicação é validada no service."""
  title: str = Field(min_length=3, max_length=100)
  description: str = Field(default="", max_length=10000)
  criteria: list[CriterioRequest] = Field(default_factory=list, max_length=30)
  status: Literal[VacancyStatus.DRAFT, VacancyStatus.OPEN] = VacancyStatus.DRAFT

  @field_validator("title", "description")
  @classmethod
  def strip_text(cls, value: str) -> str:
    return value.strip()

  @model_validator(mode="after")
  def validate_criteria(self) -> "VagaRequest":
    names = [criterion.name.lower() for criterion in self.criteria]
    if len(names) != len(set(names)):
      raise ValueError("Existem critérios com o mesmo nome")
    if sum(criterion.weight for criterion in self.criteria) > 100:
      raise ValueError("A soma dos pesos não pode passar de 100%")
    return self


class VagaStatusRequest(BaseModel):
  status: Literal[VacancyStatus.OPEN, VacancyStatus.CLOSED]
