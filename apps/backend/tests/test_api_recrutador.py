"""Decisão do recrutador (RN08), média do dashboard e download do currículo original."""

from sqlalchemy import text

CRITERIA = [{"name": "Python", "criterion_type": "habilidade", "weight": 60}, {"name": "SQL", "criterion_type": "habilidade", "weight": 40}]


def test_decision_does_not_change_score_or_ranking(api):
  c1, c2 = api.user("c1"), api.user("c2")
  recruiter, other = api.user("r1", "recruiter"), api.user("r2", "recruiter")
  vacancy = api.vacancy(recruiter, CRITERIA)
  res1 = api.resume(c1, "Python e SQL")
  app1 = api.apply(c1, vacancy, res1).json()["id"]
  app2 = api.apply(c2, vacancy, api.resume(c2, "Python")).json()["id"]

  def decide(token, application, status):
    return api.request("PATCH", f"/candidaturas/{application}/status", token, {"status": status})

  assert decide(c1, app1, "approved").status_code == 403
  assert api.request("PATCH", f"/candidaturas/{app1}/status", json={"status": "approved"}).status_code == 401
  assert decide(other, app1, "approved").status_code == 404
  assert decide(recruiter, 999999999, "approved").status_code == 404
  assert decide(recruiter, app1, "talvez").status_code == 422
  assert api.request("GET", "/candidaturas/minhas", c1).json()[0]["status"] == "pending"

  # O candidato de menor nota é aprovado e o de maior nota é rejeitado: o ranking não pode mudar.
  approved = decide(recruiter, app2, "approved")
  assert approved.status_code == 200
  assert approved.json()["status"] == "approved"
  assert approved.json()["candidate"]["name"] == "Teste c2"
  assert approved.json()["overall_score"] == 60
  assert decide(recruiter, app1, "rejected").json()["status"] == "rejected"

  ranking = api.request("GET", f"/vagas/{vacancy}/candidaturas", recruiter).json()
  assert [item["overall_score"] for item in ranking] == [100, 60]
  assert [item["status"] for item in ranking] == ["rejected", "approved"]
  assert api.request("GET", "/candidaturas/minhas", c2).json()[0]["status"] == "approved"

  # Depois da decisão, o candidato não desiste e o currículo fica preso à candidatura.
  assert api.request("DELETE", f"/candidaturas/{app1}", c1).status_code == 409
  assert api.request("DELETE", f"/curriculos/{res1}", c1).status_code == 409
  assert api.request("PUT", f"/vagas/{vacancy}", recruiter, {"title": "Outro", "description": "x", "status": "open", "criteria": CRITERIA}).status_code == 409

  # A decisão pode ser desfeita, inclusive com a vaga encerrada.
  api.request("PATCH", f"/vagas/{vacancy}/status", recruiter, {"status": "closed"})
  assert decide(recruiter, app2, "rejected").json()["status"] == "rejected"
  assert decide(recruiter, app1, "pending").json()["status"] == "pending"
  assert api.request("DELETE", f"/candidaturas/{app1}", c1).status_code == 204
  assert api.request("DELETE", f"/curriculos/{res1}", c1).status_code == 204


def test_dashboard_average_ignores_applications_without_score(api):
  a, b, c, recruiter = api.user("a"), api.user("b"), api.user("c"), api.user("r", "recruiter")
  criteria = [{"name": "Python", "criterion_type": "habilidade", "weight": 100}]
  vacancy_a, vacancy_b = api.vacancy(recruiter, criteria, "Vaga A"), api.vacancy(recruiter, criteria, "Vaga B")
  empty = api.vacancy(recruiter, criteria, "Vaga vazia")

  api.apply(a, vacancy_a, api.resume(a, "Python"))
  unscored = api.apply(b, vacancy_a, api.resume(b, "Python")).json()["id"]
  api.apply(c, vacancy_b, api.resume(c, "Vendas"))
  # Simula uma candidatura sem nota, como as anteriores à análise automática.
  api.connection.execute(text("update candidaturas_ranking set overall_score = null, score_details = null where id = :id"), {"id": unscored})

  vacancies = {item["id"]: item for item in api.request("GET", "/vagas/minhas", recruiter).json()}
  assert (vacancies[vacancy_a]["applications_count"], vacancies[vacancy_a]["scored_applications_count"]) == (2, 1)
  assert vacancies[vacancy_a]["average_score"] == 100
  assert vacancies[vacancy_b]["average_score"] == 0
  assert vacancies[empty]["applications_count"] == 0
  assert vacancies[empty]["average_score"] is None

  # Mesma conta do RecruiterDashboard.vue: média ponderada só pelas candidaturas com nota.
  scored = [item for item in vacancies.values() if item["average_score"] is not None]
  average = sum(item["average_score"] * item["scored_applications_count"] for item in scored) / sum(item["scored_applications_count"] for item in scored)
  assert round(average) == 50


def test_only_the_vacancy_recruiter_downloads_the_original_resume(api):
  candidate, owner, other = api.user("c1"), api.user("r1", "recruiter"), api.user("r2", "recruiter")
  vacancy = api.vacancy(owner, CRITERIA)
  content = "Currículo fictício: Python e SQL."
  application = api.apply(candidate, vacancy, api.resume(candidate, content, "meu-curriculo.txt")).json()["id"]
  path = f"/candidaturas/{application}/curriculo"

  response = api.request("GET", path, owner)
  assert response.status_code == 200
  assert response.text == content
  assert "meu-curriculo.txt" in response.headers["content-disposition"]
  assert response.headers["cache-control"] == "no-store"
  assert response.headers["content-type"].startswith("text/plain")

  assert api.request("GET", path, other).status_code == 404
  assert api.request("GET", path, candidate).status_code == 403
  assert api.request("GET", path).status_code == 401
  assert api.request("GET", "/candidaturas/999999999/curriculo", owner).status_code == 404
