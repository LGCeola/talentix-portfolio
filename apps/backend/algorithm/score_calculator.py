"""Fórmula da nota: cada critério soma o seu peso, proporcional ao nível do candidato até o nível exigido."""

from dataclasses import dataclass
from enum import Enum

DEFAULT_REQUIRED_LEVEL = 3


class CriterionStatus(str, Enum):
  PRESENT = "present"
  ABSENT = "absent"
  REVIEW = "review"  # Inconclusivo: não pontua e fica destacado para o recrutador.


@dataclass(frozen=True)
class CriterionInput:
  name: str
  criterion_type: str
  weight: int
  required_level: int = DEFAULT_REQUIRED_LEVEL


@dataclass(frozen=True)
class CriterionResult:
  name: str
  criterion_type: str
  weight: int
  status: CriterionStatus
  source: str
  required_level: int = DEFAULT_REQUIRED_LEVEL
  evidence: str | None = None
  # Preenchidos só quando o Jev estimou o nível; na busca por termos ficam nulos.
  level: int | None = None
  confidence: float | None = None
  model_version: str | None = None

  @property
  def points(self) -> float:
    if self.status != CriterionStatus.PRESENT:
      return 0.0
    # Sem nível estimado (busca por termos), a presença vale o peso inteiro.
    if self.level is None:
      return float(self.weight)
    # Acima do nível exigido não ganha mais: a nota mede a adequação à vaga.
    return round(self.weight * min(self.level / self.required_level, 1), 2)


def calculate_score(results: list[CriterionResult]) -> float:
  total_weight = sum(result.weight for result in results)
  if not total_weight:
    return 0.0
  return round(100 * sum(result.points for result in results) / total_weight, 2)
