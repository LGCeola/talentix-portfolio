import io
import json
import urllib.error

import pytest

from apps.backend.algorithm.analyzer import SemanticAnswer, SemanticDetectorError, analyze
from apps.backend.algorithm.anonymizer import redact
from apps.backend.algorithm.score_calculator import CriterionInput, CriterionStatus
from apps.backend.integrations.jev import JevDetector

CRITERIA = [CriterionInput("Python", "habilidade", 60), CriterionInput("Liderança", "experiencia", 40)]
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


VALID = {
  "model": "jev-1.14.0",
  "answers": {"c0": {"type": "noul", "noul": 0.91}, "c1": {"type": "noul", "noul": 0.12}},
  "usage": {"input_tokens": 80, "output_tokens": 2},
}


def test_request_uses_one_call_with_one_question_per_criterion():
  captured = {}
  result = detector(opener_returning(VALID, captured)).ask("Texto", CRITERIA)

  assert captured["url"] == "https://api.typesafe.ai/v1/systemone"
  assert captured["headers"]["Authorization"] == f"Bearer {SECRET}"
  assert captured["timeout"] == 3.0
  assert captured["body"]["model"] == "jev-1.14.0"
  assert captured["body"]["state"] == {"resume": "Texto"}
  assert [question["type"] for question in captured["body"]["questions"].values()] == ["noul", "noul"]
  assert result.answers["Python"] == SemanticAnswer(0.91, "jev-1.14.0")
  assert result.input_tokens == 80


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


def test_unexpected_payload_becomes_detector_error():
  with pytest.raises(SemanticDetectorError):
    detector(opener_returning({"model": "x", "answers": {}})).ask("Texto", CRITERIA)


def test_failure_marks_only_unmatched_criteria_for_review():
  def opener(request, timeout):
    raise TimeoutError()

  analysis = analyze("Dev Python", CRITERIA, detector(opener))
  assert analysis.score == 60
  assert analysis.results[0].status == CriterionStatus.PRESENT
  assert analysis.results[1].status == CriterionStatus.REVIEW
  assert analysis.results[1].source == "jev"


def test_detector_is_skipped_when_keywords_match_everything():
  calls = []

  def opener(request, timeout):
    calls.append(request)
    return FakeResponse(b"{}")

  analysis = analyze("Python e Liderança", CRITERIA, detector(opener))
  assert analysis.score == 100
  assert calls == []


def test_only_redacted_text_and_unmatched_criteria_leave_the_system():
  captured = {}
  payload = {"model": "jev-1.14.0", "answers": {"c0": {"noul": 0.9}}, "usage": {"input_tokens": 10}}
  text = "João da Silva, joao@exemplo.com, (48) 99999-1234. Dev Python. Coordenei equipes."

  analysis = analyze(text, CRITERIA, detector(opener_returning(payload, captured)), private_terms=("João da Silva",))

  sent = captured["body"]["state"]["resume"]
  assert "João" not in sent and "Silva" not in sent and "joao@" not in sent and "99999" not in sent
  assert "Coordenei equipes" in sent
  assert len(captured["body"]["questions"]) == 1
  assert "Liderança" in captured["body"]["questions"]["c0"]["instructions"]
  assert analysis.results[1].status == CriterionStatus.PRESENT
  assert analysis.results[1].model_version == "jev-1.14.0"
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
