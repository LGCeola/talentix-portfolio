"""Fórmula da nota: cada critério presente soma o seu peso; os demais somam zero."""

from dataclasses import dataclass
from enum import Enum


class CriterionStatus(str, Enum):
  PRESENT = "present"
  ABSENT = "absent"
  REVIEW = "review"  # Inconclusivo: não pontua e fica destacado para o recrutador.


@dataclass(frozen=True)
class CriterionInput:
  name: str
  criterion_type: str
  weight: int


@dataclass(frozen=True)
class CriterionResult:
  name: str
  criterion_type: str
  weight: int
  status: CriterionStatus
  source: str
  evidence: str | None = None
  probability: float | None = None
  model_version: str | None = None

  @property
  def points(self) -> int:
    return self.weight if self.status == CriterionStatus.PRESENT else 0


def calculate_score(results: list[CriterionResult]) -> float:
  total_weight = sum(result.weight for result in results)
  if not total_weight:
    return 0.0
  return round(100 * sum(result.points for result in results) / total_weight, 2)
