"""Compara o texto de um currículo com os critérios de uma vaga."""

from dataclasses import dataclass
from typing import Protocol

from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.report_generator import build_suggestions
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionResult, CriterionStatus, calculate_score

ALGORITHM_VERSION = "1"
PRESENT_THRESHOLD = 0.7
ABSENT_THRESHOLD = 0.3


@dataclass(frozen=True)
class SemanticAnswer:
  probability: float
  model_version: str


class SemanticDetector(Protocol):
  """Ponto de conexão de um modelo externo (ex.: Jev), consultado só quando a busca não encontra o termo."""
  source: str

  def detect(self, resume_text: str, criterion: CriterionInput) -> SemanticAnswer:
    ...


@dataclass(frozen=True)
class Analysis:
  score: float
  results: list[CriterionResult]
  suggestions: list[str]

  def to_details(self) -> dict:
    return {
      "algorithm_version": ALGORITHM_VERSION,
      "criteria": [
        {
          "name": result.name,
          "criterion_type": result.criterion_type,
          "weight": result.weight,
          "status": result.status.value,
          "points": result.points,
          "source": result.source,
          "evidence": result.evidence,
          "probability": result.probability,
          "model_version": result.model_version,
        }
        for result in self.results
      ],
    }


def analyze(resume_text: str, criteria: list[CriterionInput], detector: SemanticDetector | None = None) -> Analysis:
  results = [_evaluate(resume_text, criterion, detector) for criterion in criteria]
  return Analysis(score=calculate_score(results), results=results, suggestions=build_suggestions(results))


def _evaluate(resume_text: str, criterion: CriterionInput, detector: SemanticDetector | None) -> CriterionResult:
  base = {"name": criterion.name, "criterion_type": criterion.criterion_type, "weight": criterion.weight}

  evidence = find_evidence(resume_text, criterion.name)
  if evidence:
    return CriterionResult(**base, status=CriterionStatus.PRESENT, source="keyword", evidence=evidence)
  if detector is None:
    return CriterionResult(**base, status=CriterionStatus.ABSENT, source="keyword")

  answer = detector.detect(resume_text, criterion)
  return CriterionResult(
    **base,
    status=_classify(answer.probability),
    source=detector.source,
    probability=answer.probability,
    model_version=answer.model_version,
  )


def _classify(probability: float) -> CriterionStatus:
  if probability >= PRESENT_THRESHOLD:
    return CriterionStatus.PRESENT
  if probability <= ABSENT_THRESHOLD:
    return CriterionStatus.ABSENT
  return CriterionStatus.REVIEW
