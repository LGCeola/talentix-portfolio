"""Vagas, simulação de compatibilidade, candidatura com nota e ranking (RF04–RF08, RF12–RF14)."""

import time

from apps.backend.algorithm.analyzer import LevelAnswer
from apps.backend.api import candidaturas as candidaturas_api

CRITERIA = [
  {"name": "Python", "criterion_type": "habilidade", "weight": 50},
  {"name": "APIs REST", "criterion_type": "experiencia", "weight": 30},
  {"name": "Graduação em TI", "criterion_type": "formacao", "weight": 20},
]
FULL = "Dev PYTHON, construí apis-rest em produção. Graduacao em TI pela UFSC."
HALF = "Experiência com Python em automação."
NONE = "Experiência com JavaScript e vendas."


def test_compatibility_preview_is_private_and_scoped(api):
  candidate, other, recruiter = api.user("c1"), api.user("c2"), api.user("r1", "recruiter")
  vacancy = api.vacancy(recruiter, CRITERIA)
  draft = api.vacancy(recruiter, [], title="Rascunho", status="draft")
  mine, theirs = api.resume(candidate, HALF), api.resume(other, FULL)

  response = api.request("GET", f"/vagas/{vacancy}/compatibilidade?resume_id={mine}", candidate)
  assert response.status_code == 200
  preview = response.json()
  assert preview["score"] == 50
  assert preview["analysis_mode"] == "keywords"
  assert len(preview["suggestions"]) == 2

  # A simulação não cria candidatura nem aparece para o recrutador.
  assert api.request("GET", "/candidaturas/minhas", candidate).json() == []
  assert api.request("GET", f"/vagas/{vacancy}/candidaturas", recruiter).json() == []

  assert api.request("GET", f"/vagas/{vacancy}/compatibilidade?resume_id={theirs}", candidate).status_code == 404
  assert api.request("GET", f"/vagas/{draft}/compatibilidade?resume_id={mine}", candidate).status_code == 404
  assert api.request("GET", f"/vagas/{vacancy}/compatibilidade?resume_id={mine}", recruiter).status_code == 403


def test_application_scores_and_ranking_orders_candidates(api):
  c1, c2, c3 = api.user("c1"), api.user("c2"), api.user("c3")
  recruiter, other_recruiter = api.user("r1", "recruiter"), api.user("r2", "recruiter")
  vacancy = api.vacancy(recruiter, CRITERIA)

  # A ordem de envio é a inversa da nota, para o ranking precisar reordenar.
  assert api.apply(c3, vacancy, api.resume(c3, NONE)).status_code == 201
  assert api.apply(c2, vacancy, api.resume(c2, HALF)).status_code == 201
  started = time.perf_counter()
  response = api.apply(c1, vacancy, api.resume(c1, FULL))
  elapsed = time.perf_counter() - started

  assert response.status_code == 201
  application = response.json()
  assert application["overall_score"] == 100
  assert application["status"] == "pending"
  assert application["score_details"]["algorithm_version"] == "3"
  assert application["score_details"]["analysis_mode"] == "keywords"
  assert "PYTHON" in application["score_details"]["criteria"][0]["evidence"]
  assert application["improvement_suggestions"] == ""
  assert elapsed < 2  # RNF01, só com a busca por termos.

  ranking = api.request("GET", f"/vagas/{vacancy}/candidaturas", recruiter).json()
  assert [item["overall_score"] for item in ranking] == [100, 50, 0]
  assert ranking[1]["score_details"]["criteria"][1]["status"] == "absent"
  assert api.request("GET", f"/vagas/{vacancy}/candidaturas", other_recruiter).status_code == 404

  mine = api.request("GET", "/candidaturas/minhas", c2).json()
  assert mine[0]["overall_score"] == 50
  assert mine[0]["improvement_suggestions"].count("\n") == 1


def test_application_rules(api):
  candidate, recruiter = api.user("c1"), api.user("r1", "recruiter")
  vacancy = api.vacancy(recruiter, CRITERIA)
  resume = api.resume(candidate, FULL)

  without_consent = api.request("POST", "/candidaturas", candidate, {"vacancy_id": vacancy, "resume_id": resume, "consent": False})
  assert without_consent.status_code == 422
  assert api.apply(candidate, vacancy, resume).status_code == 201
  assert api.apply(candidate, vacancy, resume).status_code == 409
  assert api.apply(recruiter, vacancy, resume).status_code == 403

  closed = api.vacancy(recruiter, CRITERIA, title="Encerrada")
  api.request("PATCH", f"/vagas/{closed}/status", recruiter, {"status": "closed"})
  assert api.apply(candidate, closed, resume).status_code == 409


def test_same_input_gives_same_result(api):
  candidate, recruiter = api.user("c1"), api.user("r1", "recruiter")
  vacancy = api.vacancy(recruiter, CRITERIA)
  resume = api.resume(candidate, FULL)
  path = f"/vagas/{vacancy}/compatibilidade?resume_id={resume}"
  assert api.request("GET", path, candidate).json() == api.request("GET", path, candidate).json()


def test_required_level_is_saved_validated_and_public(api):
  candidate, recruiter = api.user("c1"), api.user("r1", "recruiter")
  criteria = [
    {"name": "Python", "criterion_type": "habilidade", "weight": 60, "required_level": 5},
    {"name": "Computação", "criterion_type": "formacao", "weight": 40},
  ]
  vacancy = api.vacancy(recruiter, criteria)
  saved = api.request("GET", f"/vagas/{vacancy}", recruiter).json()
  assert [item["required_level"] for item in saved["criteria"]] == [5, 3]

  invalid = [{"name": "Python", "criterion_type": "habilidade", "weight": 10, "required_level": 6}]
  assert api.request("POST", "/vagas", recruiter, {"title": "Inválida", "criteria": invalid}).status_code == 422

  public = api.request("GET", "/vagas", candidate).json()
  assert next(item for item in public if item["id"] == vacancy)["criteria"][0]["required_level"] == 5


def test_levels_from_detector_reach_the_score(api, monkeypatch):
  class FakeDetector:
    source = "fake"

    def detect(self, resume_text, criteria):
      assert "Teste" not in resume_text  # O nome do candidato não sai do sistema.
      return {criterion.name: LevelAnswer(level=2, confidence=0.95, model_version="fake-1") for criterion in criteria}

  monkeypatch.setattr(candidaturas_api.service, "detector", FakeDetector())
  candidate, recruiter = api.user("c1"), api.user("r1", "recruiter")
  vacancy = api.vacancy(recruiter, [{"name": "Python", "criterion_type": "habilidade", "weight": 100, "required_level": 4}])

  application = api.apply(candidate, vacancy, api.resume(candidate, "Teste c1. Curso de Python.")).json()
  assert application["overall_score"] == 50
  details = application["score_details"]
  assert details["analysis_mode"] == "levels"
  assert details["criteria"][0]["level"] == 2
  assert details["criteria"][0]["required_level"] == 4
  assert details["criteria"][0]["points"] == 50


def test_consent_terms_follow_the_detector(api, monkeypatch):
  candidate, recruiter = api.user("c1"), api.user("r1", "recruiter")
  assert api.request("GET", "/candidaturas/consentimento", candidate).json() == {"external_analysis": False}
  monkeypatch.setattr(candidaturas_api.service, "detector", object())
  assert api.request("GET", "/candidaturas/consentimento", candidate).json() == {"external_analysis": True}
  assert api.request("GET", "/candidaturas/consentimento", recruiter).status_code == 403
  assert api.request("GET", "/candidaturas/consentimento").status_code == 401
