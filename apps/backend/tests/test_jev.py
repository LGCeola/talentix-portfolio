import io
import json
import urllib.error

import pytest

from apps.backend.algorithm.analyzer import MODE_KEYWORDS, LevelAnswer, SemanticDetectorError, analyze
from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionStatus
from apps.backend.integrations.jev import EDUCATION_LEVELS, PRACTICE_LEVELS, JevDetector

CRITERIA = [CriterionInput("Python", "habilidade", 60, required_level=4), CriterionInput("Computação", "formacao", 40, required_level=3)]
SECRET = "chave-de-teste-nao-real"


class FakeResponse(io.BytesIO):
  def __enter__(self):
    return self

  def __exit__(self, *args):
    self.close()


def opener_returning(payload, captured=None):
  def opener(request, timeout):
    if captured is not None:
      captured.update(body=json.loads(request.data), headers=dict(request.headers), timeout=timeout, url=request.full_url)
    return FakeResponse(json.dumps(payload).encode())
  return opener


def detector(opener):
  return JevDetector(SECRET, "jev-1.14.0", 3.0, opener=opener)


def score_answer(peak: int, confidence: float = 0.95) -> dict:
  probabilities = {str(level): (0.9 if level == peak else 0.02) for level in range(6)}
  return {"type": "score", "probabilities": probabilities, "score": float(peak), "confidence": confidence}


VALID = {
  "model": "jev-1.14.0",
  "answers": {"c0": score_answer(4), "c1": score_answer(3, confidence=0.6)},
  "usage": {"input_tokens": 80, "output_tokens": 2},
}


def test_request_uses_one_score_question_per_criterion():
  captured = {}
  result = detector(opener_returning(VALID, captured)).ask("Texto", CRITERIA)

  assert captured["url"] == "https://api.typesafe.ai/v1/systemone"
  assert captured["headers"]["Authorization"] == f"Bearer {SECRET}"
  assert captured["timeout"] == 3.0
  assert captured["body"]["model"] == "jev-1.14.0"
  assert captured["body"]["state"] == {"resume": "Texto"}
  questions = captured["body"]["questions"]
  assert [question["type"] for question in questions.values()] == ["score", "score"]
  assert len(questions["c0"]["criteria"]) == len(PRACTICE_LEVELS) == 6
  assert "Python" in questions["c0"]["instructions"]
  assert all("Python" in level for level in questions["c0"]["criteria"])
  # Formação usa a escala própria.
  assert questions["c1"]["criteria"][3] == EDUCATION_LEVELS[3].format(name="Computação")
  assert result.answers["Python"] == LevelAnswer(level=4, confidence=0.95, model_version="jev-1.14.0")
  assert result.input_tokens == 80


def test_low_confidence_answer_is_kept_for_the_analyzer_to_decide():
  analysis = analyze("Texto", CRITERIA, detector(opener_returning(VALID)))
  python, education = analysis.results
  assert python.status == CriterionStatus.PRESENT and python.points == 60
  assert education.status == CriterionStatus.REVIEW and education.level == 3


def test_http_error_does_not_leak_secret_or_body():
  def opener(request, timeout):
    raise urllib.error.HTTPError(request.full_url, 500, "erro", {}, io.BytesIO(SECRET.encode()))

  with pytest.raises(SemanticDetectorError) as error:
    detector(opener).ask("Currículo privado", CRITERIA)
  assert "500" in str(error.value)
  assert SECRET not in str(error.value)
  assert "privado" not in str(error.value)


@pytest.mark.parametrize("failure", [urllib.error.URLError("sem rede"), TimeoutError()])
def test_network_failure_becomes_detector_error(failure):
  def opener(request, timeout):
    raise failure

  with pytest.raises(SemanticDetectorError):
    detector(opener).ask("Texto", CRITERIA)


@pytest.mark.parametrize("payload", [
  {"model": "x", "answers": {}},
  {"model": "x", "answers": {"c0": {"probabilities": {"0": 1.0}, "confidence": 1.0}, "c1": score_answer(1)}, "usage": {"input_tokens": 1}},
])
def test_unexpected_payload_becomes_detector_error(payload):
  with pytest.raises(SemanticDetectorError):
    detector(opener_returning(payload)).ask("Texto", CRITERIA)


def test_failure_falls_back_to_keyword_analysis():
  def opener(request, timeout):
    raise TimeoutError()

  analysis = analyze("Dev Python", CRITERIA, detector(opener))
  assert analysis.mode == MODE_KEYWORDS
  assert analysis.score == 60
  assert analysis.results[0].source == "keyword"


def test_only_redacted_text_leaves_the_system():
  captured = {}
  text = "João da Silva, joao@exemplo.com, (48) 99999-1234. Dev Python. Bacharel em Ciência da Computação."

  analysis = analyze(text, CRITERIA, detector(opener_returning(VALID, captured)), private_terms=("João da Silva",))

  sent = captured["body"]["state"]["resume"]
  assert "João" not in sent and "Silva" not in sent and "joao@" not in sent and "99999" not in sent
  assert "Bacharel em Ciência da Computação" in sent
  # A evidência local continua vindo do texto original.
  assert "Python" in analysis.results[0].evidence


def test_redact_removes_contact_data():
  text = "maria.souza+cv@mail.com.br | +55 (48) 99123-4567 | 48 3222-1100 | CPF 123.456.789-09 | CEP 88010-000 | Nascida em 01/02/1990 | https://linkedin.com/in/maria | github.com/maria"
  redacted = redact(text)
  for private in ("maria.souza", "99123", "3222", "123.456", "88010", "01/02/1990", "linkedin", "github"):
    assert private not in redacted


def test_redact_names_ignores_accents_and_short_parts():
  redacted = redact("JOAO da Silva e Joãozinho estudaram na USP", ("João da Silva",))
  assert "JOAO" not in redacted
  assert "Silva" not in redacted
  assert " da " in redacted
  assert "Joãozinho" in redacted


def test_redact_keeps_professional_data():
  text = "Python desde 2019. 5 anos em 3 empresas. Atendi 1200 clientes."
  assert redact(text, ("Ana Lima",)) == text
