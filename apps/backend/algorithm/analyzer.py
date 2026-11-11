"""Compara o texto de um currículo com os critérios de uma vaga."""

import logging
from dataclasses import dataclass
from typing import Protocol

from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.keyword_matcher import find_evidence
from apps.backend.algorithm.report_generator import build_suggestions
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionResult, CriterionStatus, calculate_score

logger = logging.getLogger(__name__)

ALGORITHM_VERSION = "3"
# Abaixo desta confiança o nível estimado não pontua: o critério fica "a revisar".
MIN_CONFIDENCE = 0.8

MODE_LEVELS = "levels"  # Nível estimado pelo Jev.
MODE_KEYWORDS = "keywords"  # Só busca por termos: Jev desligado ou fora do ar.


@dataclass(frozen=True)
class LevelAnswer:
  level: int  # 0 = não encontrado; 1 a 5 = nível de evidência no currículo.
  confidence: float
  model_version: str


class SemanticDetectorError(Exception):
  """O detector externo não respondeu; a análise continua só com a busca por termos."""


class SemanticDetector(Protocol):
  """Ponto de conexão de um modelo externo (ex.: Jev), que estima o nível do candidato em cada critério."""
  source: str

  def detect(self, resume_text: str, criteria: list[CriterionInput]) -> dict[str, LevelAnswer]:
    ...


@dataclass(frozen=True)
class Analysis:
  score: float
  results: list[CriterionResult]
  suggestions: list[str]
  mode: str

  def to_details(self) -> dict:
    return {
      "algorithm_version": ALGORITHM_VERSION,
      "analysis_mode": self.mode,
      "criteria": [
        {
          "name": result.name,
          "criterion_type": result.criterion_type,
          "weight": result.weight,
          "required_level": result.required_level,
          "status": result.status.value,
          "points": result.points,
          "source": result.source,
          "evidence": result.evidence,
          "level": result.level,
          "confidence": result.confidence,
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

  if answers is None:
    results = [_by_keyword(criterion, evidences[criterion.name]) for criterion in criteria]
    mode = MODE_KEYWORDS
  else:
    results = [_by_level(criterion, evidences[criterion.name], answers.get(criterion.name), detector.source) for criterion in criteria]
    mode = MODE_LEVELS
  return Analysis(score=calculate_score(results), results=results, suggestions=build_suggestions(results), mode=mode)


def _ask_detector(
  resume_text: str,
  criteria: list[CriterionInput],
  detector: SemanticDetector | None,
  private_terms: tuple[str, ...],
) -> dict[str, LevelAnswer] | None:
  """Devolve None quando a análise deve ser só por termos."""
  if detector is None or not criteria:
    return None
  try:
    # Único ponto em que o currículo sai do sistema: sempre sem os dados pessoais.
    return detector.detect(redact(resume_text, private_terms), criteria)
  except SemanticDetectorError as error:
    logger.warning("Análise só por termos, sem detector externo: %s", error)
    return None


def _base(criterion: CriterionInput) -> dict:
  return {
    "name": criterion.name,
    "criterion_type": criterion.criterion_type,
    "weight": criterion.weight,
    "required_level": criterion.required_level,
  }


def _by_keyword(criterion: CriterionInput, evidence: str | None) -> CriterionResult:
  status = CriterionStatus.PRESENT if evidence else CriterionStatus.ABSENT
  return CriterionResult(**_base(criterion), status=status, source="keyword", evidence=evidence)


def _by_level(criterion: CriterionInput, evidence: str | None, answer: LevelAnswer | None, source: str) -> CriterionResult:
  if answer is None:
    return CriterionResult(**_base(criterion), status=CriterionStatus.REVIEW, source=source, evidence=evidence)

  if answer.confidence < MIN_CONFIDENCE:
    status = CriterionStatus.REVIEW
  elif answer.level == 0:
    # Regra de conflito: termo encontrado, mas o modelo não reconhece o critério (ex.: negação).
    status = CriterionStatus.REVIEW if evidence else CriterionStatus.ABSENT
  else:
    status = CriterionStatus.PRESENT
  return CriterionResult(
    **_base(criterion),
    status=status,
    source=source,
    evidence=evidence,
    level=answer.level,
    confidence=answer.confidence,
    model_version=answer.model_version,
  )
