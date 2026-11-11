"""Cliente da API System One da TypeSafe (Jev): estima o nível do candidato em cada critério com perguntas Score."""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from apps.backend.algorithm.analyzer import LevelAnswer, SemanticDetector, SemanticDetectorError
from apps.backend.algorithm.score_calculator import CriterionInput
from apps.backend.core.config import settings

_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

# O Jev avalia cada nível isoladamente, sem ver os vizinhos: cada descrição precisa fazer sentido sozinha
# e descrever uma evidência concreta, não um grau como "avançado" (docs.typesafe.ai/primitives/score).
# Em inglês, idioma principal de treino do modelo. O índice de cada item é o nível (0 = não encontrado).
PRACTICE_LEVELS = [
  'The resume does not mention "{name}" at all, or says the person has no experience with it.',
  'The strongest evidence of "{name}" is that it is only listed as a keyword or skill, with no course, project or job where it was used.',
  'The strongest evidence of "{name}" is a course, class, bootcamp or certification where it was studied, without applying it in a project or job.',
  'The strongest evidence of "{name}" is a personal, academic or volunteer project where it was applied, or helping classmates with it as a teaching assistant.',
  'The strongest evidence of "{name}" is professional work with it, in a job, internship or freelance.',
  'The resume shows the person led a team or project, taught classes as a teacher or instructor, or was technically responsible for work involving "{name}".',
]
EDUCATION_LEVELS = [
  'The resume shows no education in "{name}" or a closely related field.',
  'The highest education in "{name}" or a closely related field is a short, free or technical course, or an undergraduate degree that was interrupted or abandoned.',
  'The highest education in "{name}" or a closely related field is an undergraduate degree still in progress.',
  'The highest education in "{name}" or a closely related field is a completed undergraduate degree.',
  'The highest education in "{name}" or a closely related field is a completed postgraduate specialization or MBA.',
  'The highest education in "{name}" or a closely related field is a master\'s or doctoral degree.',
]
PRACTICE_INSTRUCTIONS = 'What is the strongest evidence in the resume of the person\'s level with "{name}"?'
EDUCATION_INSTRUCTIONS = 'What is the person\'s highest education in "{name}" or a closely related field?'


def build_question(criterion: CriterionInput) -> dict:
  education = criterion.criterion_type == "formacao"
  instructions = EDUCATION_INSTRUCTIONS if education else PRACTICE_INSTRUCTIONS
  levels = EDUCATION_LEVELS if education else PRACTICE_LEVELS
  return {
    "type": "score",
    "instructions": instructions.format(name=criterion.name),
    "criteria": [level.format(name=criterion.name) for level in levels],
  }


@dataclass(frozen=True)
class JevResult:
  answers: dict[str, LevelAnswer]
  input_tokens: int


class JevDetector:
  source = "jev"

  def __init__(self, api_key: str, model: str, timeout_seconds: float, opener: Callable = urllib.request.urlopen):
    self._api_key = api_key
    self._model = model
    self._timeout_seconds = timeout_seconds
    self._opener = opener

  def detect(self, resume_text: str, criteria: list[CriterionInput]) -> dict[str, LevelAnswer]:
    return self.ask(resume_text, criteria).answers

  def ask(self, resume_text: str, criteria: list[CriterionInput]) -> JevResult:
    """Faz uma única requisição com uma pergunta Score por critério: o texto do currículo é o mesmo para todas."""
    names = {f"c{index}": criterion.name for index, criterion in enumerate(criteria)}
    questions = {key: build_question(criterion) for key, criterion in zip(names, criteria)}
    data = self._post({"model": self._model, "state": {"resume": resume_text}, "questions": questions})

    try:
      version = data["model"]
      answers = {name: _parse(data["answers"][key], version) for key, name in names.items()}
      return JevResult(answers=answers, input_tokens=int(data["usage"]["input_tokens"]))
    except (KeyError, TypeError, ValueError) as error:
      raise SemanticDetectorError("Resposta inesperada da API do Jev") from error

  def _post(self, body: dict) -> dict:
    request = urllib.request.Request(
      _ENDPOINT,
      data=json.dumps(body).encode(),
      headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
      method="POST",
    )
    # As mensagens não incluem corpo nem cabeçalhos, para não levar a chave ou o currículo aos logs.
    try:
      with self._opener(request, timeout=self._timeout_seconds) as response:
        return json.loads(response.read())
    except urllib.error.HTTPError as error:
      raise SemanticDetectorError(f"A API do Jev respondeu com status {error.code}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
      raise SemanticDetectorError(f"Falha ao chamar a API do Jev: {type(error).__name__}") from None


def _parse(answer: dict, version: str) -> LevelAnswer:
  probabilities = {int(level): float(value) for level, value in answer["probabilities"].items()}
  if sorted(probabilities) != list(range(len(PRACTICE_LEVELS))):
    raise ValueError("Níveis inesperados na resposta do Jev")
  # O nível mais provável, arredondado, é mais fácil de explicar ao recrutador do que a média.
  level = max(sorted(probabilities), key=lambda key: probabilities[key])
  return LevelAnswer(level=level, confidence=float(answer["confidence"]), model_version=version)


def build_semantic_detector() -> SemanticDetector | None:
  if not settings.JEV_ENABLED or settings.JEV_SECRET_KEY is None:
    return None
  return JevDetector(settings.JEV_SECRET_KEY.get_secret_value(), settings.JEV_MODEL, settings.JEV_TIMEOUT_SECONDS)
