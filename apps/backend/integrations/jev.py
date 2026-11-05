"""Cliente da API System One da TypeSafe (Jev), usado como detector opcional do algoritmo."""

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable

from apps.backend.algorithm.analyzer import SemanticAnswer, SemanticDetector, SemanticDetectorError
from apps.backend.algorithm.score_calculator import CriterionInput
from apps.backend.core.config import settings

_ENDPOINT = "https://api.typesafe.ai/v1/systemone"

# O Jev foi treinado principalmente em inglês; a comparação em evaluation/ mede cada idioma.
INSTRUCTIONS = {
  "en": {
    "habilidade": 'The resume demonstrates this skill or knowledge: "{name}"',
    "experiencia": 'The resume demonstrates experience with: "{name}"',
    "formacao": 'The resume demonstrates this education or degree: "{name}"',
  },
  "pt": {
    "habilidade": 'O currículo demonstra esta habilidade ou conhecimento: "{name}"',
    "experiencia": 'O currículo demonstra experiência com: "{name}"',
    "formacao": 'O currículo demonstra esta formação: "{name}"',
  },
}


@dataclass(frozen=True)
class JevResult:
  answers: dict[str, SemanticAnswer]
  input_tokens: int


class JevDetector:
  source = "jev"

  def __init__(
    self,
    api_key: str,
    model: str,
    timeout_seconds: float,
    language: str = "en",
    opener: Callable = urllib.request.urlopen,
  ):
    self._api_key = api_key
    self._model = model
    self._timeout_seconds = timeout_seconds
    self._instructions = INSTRUCTIONS[language]
    self._opener = opener

  def detect(self, resume_text: str, criteria: list[CriterionInput]) -> dict[str, SemanticAnswer]:
    return self.ask(resume_text, criteria).answers

  def ask(self, resume_text: str, criteria: list[CriterionInput]) -> JevResult:
    """Faz uma única requisição com um Noul por critério: o texto do currículo é o mesmo para todos."""
    names = {f"c{index}": criterion.name for index, criterion in enumerate(criteria)}
    questions = {
      key: {"type": "noul", "instructions": self._instructions[criterion.criterion_type].format(name=criterion.name)}
      for key, criterion in zip(names, criteria)
    }
    data = self._post({"model": self._model, "state": {"resume": resume_text}, "questions": questions})

    try:
      version = data["model"]
      answers = {name: SemanticAnswer(probability=float(data["answers"][key]["noul"]), model_version=version) for key, name in names.items()}
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


def build_semantic_detector() -> SemanticDetector | None:
  if not settings.JEV_ENABLED or settings.JEV_SECRET_KEY is None:
    return None
  return JevDetector(settings.JEV_SECRET_KEY.get_secret_value(), settings.JEV_MODEL, settings.JEV_TIMEOUT_SECONDS)
