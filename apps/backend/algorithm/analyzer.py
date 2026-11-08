"""Compara o texto de um currículo com os critérios de uma vaga."""

import logging
from dataclasses import dataclass
from typing import Protocol

from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.report_generator import build_suggestions
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionResult, CriterionStatus, calculate_score

logger = logging.getLogger(__name__)

ALGORITHM_VERSION = "2"
PRESENT_THRESHOLD = 0.7
ABSENT_THRESHOLD = 0.3


@dataclass(frozen=True)
class SemanticAnswer:
  probability: float
  model_version: str


class SemanticDetectorError(Exception):
  """O detector externo não respondeu; a análise continua sem ele."""


class SemanticDetector(Protocol):
  """Ponto de conexão de um modelo externo (ex.: Jev), que avalia todos os critérios junto com a busca."""
  source: str

  def detect(self, resume_text: str, criteria: list[CriterionInput]) -> dict[str, SemanticAnswer]:
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


def analyze(
  resume_text: str,
  criteria: list[CriterionInput],
  detector: SemanticDetector | None = None,
  private_terms: tuple[str, ...] = (),
) -> Analysis:
  evidences = {criterion.name: find_evidence(resume_text, criterion.name) for criterion in criteria}
  answers = _ask_detector(resume_text, criteria, detector, private_terms)

  results = [_evaluate(criterion, evidences[criterion.name], answers.get(criterion.name), detector) for criterion in criteria]
  return Analysis(score=calculate_score(results), results=results, suggestions=build_suggestions(results))


def _ask_detector(
  resume_text: str,
  criteria: list[CriterionInput],
  detector: SemanticDetector | None,
  private_terms: tuple[str, ...],
) -> dict[str, SemanticAnswer]:
  if detector is None or not criteria:
    return {}
  try:
    # Único ponto em que o currículo sai do sistema: sempre sem os dados pessoais.
    return detector.detect(redact(resume_text, private_terms), criteria)
  except SemanticDetectorError as error:
    logger.warning("Análise sem detector externo: %s", error)
    return {}


def _evaluate(
  criterion: CriterionInput,
  evidence: str | None,
  answer: SemanticAnswer | None,
  detector: SemanticDetector | None,
) -> CriterionResult:
  base = {"name": criterion.name, "criterion_type": criterion.criterion_type, "weight": criterion.weight}

  if answer is None:
    if evidence:
      return CriterionResult(**base, status=CriterionStatus.PRESENT, source="keyword", evidence=evidence)
    if detector is None:
      return CriterionResult(**base, status=CriterionStatus.ABSENT, source="keyword")
    # Sem resposta do modelo, o sistema não afirma que o critério falta: destaca para o recrutador.
    return CriterionResult(**base, status=CriterionStatus.REVIEW, source=detector.source)

  status = _classify(answer.probability)
  source = detector.source
  if evidence:
    # Regra de conflito: termo encontrado só deixa de pontuar se o modelo indicar ausência.
    status = CriterionStatus.REVIEW if status == CriterionStatus.ABSENT else CriterionStatus.PRESENT
    source = "keyword" if status == CriterionStatus.PRESENT else detector.source
  return CriterionResult(
    **base,
    status=status,
    source=source,
    evidence=evidence,
    probability=answer.probability,
    model_version=answer.model_version,
  )


def _classify(probability: float) -> CriterionStatus:
  if probability >= PRESENT_THRESHOLD:
    return CriterionStatus.PRESENT
  if probability <= ABSENT_THRESHOLD:
    return CriterionStatus.ABSENT
  return CriterionStatus.REVIEW
