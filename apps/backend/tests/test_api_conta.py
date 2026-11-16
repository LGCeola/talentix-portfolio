"""Edição e exclusão da conta (LGPD: direito ao esquecimento)."""

from apps.backend.tests.conftest import PASSWORD

CRITERIA = [{"name": "Python", "criterion_type": "habilidade", "weight": 100}]


def test_edit_account(api):
  candidate, _ = api.user("c1"), api.user("c2")
  edit = lambda body, token=candidate: api.request("PATCH", "/usuarios/me", token, body)

  updated = edit({"name": "  Novo Nome  ", "email": api.email("c1")})
  assert updated.status_code == 200
  assert updated.json()["name"] == "Novo Nome"
  assert "password_hash" not in updated.json()

  assert edit({"name": "   ", "email": api.email("c1")}).status_code == 422
  assert edit({"name": "Novo Nome", "email": "semarroba"}).status_code == 422
  # Trocar o e-mail exige a senha atual.
  assert edit({"name": "Novo Nome", "email": api.email("c1b")}).status_code == 422
  assert edit({"name": "Novo Nome", "email": api.email("c1b"), "current_password": "errada-123"}).status_code == 403
  assert edit({"name": "Novo Nome", "email": api.email("c2"), "current_password": PASSWORD}).status_code == 409
  assert api.request("GET", "/auth/me", candidate).json()["email"] == api.email("c1")

  changed = edit({"name": "Novo Nome", "email": api.email("C1B").upper(), "current_password": PASSWORD})
  assert changed.json()["email"] == api.email("c1b")
  assert api.request("GET", "/auth/me", candidate).status_code == 200
  assert api.login(api.email("c1b")).status_code == 200
  assert api.login(api.email("c1")).status_code == 401
  assert api.request("PATCH", "/usuarios/me", json={"name": "Xx", "email": api.email("x")}).status_code == 401


def test_delete_candidate_removes_everything(api, uploads):
  c1, c2 = api.user("c1"), api.user("c2")
  recruiter = api.user("r1", "recruiter")
  c1_id = api.request("GET", "/auth/me", c1).json()["id"]
  vacancy = api.vacancy(recruiter, CRITERIA)
  first = api.apply(c1, vacancy, api.resume(c1, "Python")).json()["id"]
  other = api.apply(c2, vacancy, api.resume(c2, "Python")).json()["id"]
  api.request("PATCH", f"/candidaturas/{first}/status", recruiter, {"status": "approved"})
  delete = lambda body, token=c1: api.request("POST", "/usuarios/me/exclusao", token, body)

  assert delete({"password": "errada-123"}).status_code == 403
  assert delete({}).status_code == 422
  assert api.request("POST", "/usuarios/me/exclusao", json={"password": PASSWORD}).status_code == 401
  assert api.count("candidaturas_ranking", "candidate_id = :i", i=c1_id) == 1

  assert delete({"password": PASSWORD}).status_code == 204
  assert api.count("usuarios", "id = :i", i=c1_id) == 0
  assert api.count("curriculos", "candidate_id = :i", i=c1_id) == 0
  # Inclui a candidatura já aprovada.
  assert api.count("candidaturas_ranking", "candidate_id = :i", i=c1_id) == 0
  assert not (uploads / str(c1_id)).exists()
  assert api.request("GET", "/auth/me", c1).status_code == 401
  assert api.login(api.email("c1")).status_code == 401

  # O outro candidato continua no ranking, e o e-mail fica livre para um novo cadastro.
  assert [item["id"] for item in api.request("GET", f"/vagas/{vacancy}/candidaturas", recruiter).json()] == [other]
  assert api.register("c1").status_code == 201


def test_delete_recruiter_removes_vacancies_but_keeps_candidates(api):
  candidate, recruiter, other = api.user("c1"), api.user("r1", "recruiter"), api.user("r2", "recruiter")
  recruiter_id = api.request("GET", "/auth/me", recruiter).json()["id"]
  removed, kept = api.vacancy(recruiter, CRITERIA, "Vaga R1"), api.vacancy(other, CRITERIA, "Vaga R2")
  resume = api.resume(candidate, "Python")
  api.apply(candidate, removed, resume)
  remaining = api.apply(candidate, kept, resume).json()["id"]

  assert api.request("POST", "/usuarios/me/exclusao", recruiter, {"password": PASSWORD}).status_code == 204
  assert api.count("vagas", "recruiter_id = :i", i=recruiter_id) == 0
  assert api.count("criterios_vaga", "vacancy_id = :i", i=removed) == 0
  assert api.count("candidaturas_ranking", "vacancy_id = :i", i=removed) == 0
  assert [item["id"] for item in api.request("GET", "/candidaturas/minhas", candidate).json()] == [remaining]
  assert [item["id"] for item in api.request("GET", "/curriculos", candidate).json()] == [resume]
  assert [item["id"] for item in api.request("GET", "/vagas/minhas", other).json()] == [kept]
  assert removed not in [item["id"] for item in api.request("GET", "/vagas", candidate).json()]
