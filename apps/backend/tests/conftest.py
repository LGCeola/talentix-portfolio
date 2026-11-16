"""Infraestrutura dos testes de API.

Os testes usam o PostgreSQL configurado no .env, mas tudo roda dentro de uma transação desfeita ao final
de cada teste: nenhum dado fica no banco. Arquivos enviados vão para uma pasta temporária, e o Jev real
nunca é chamado. Sem banco disponível, os testes de API são pulados e os do algoritmo continuam rodando.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from apps.backend.api import candidaturas as candidaturas_api
from apps.backend.api import curriculos as curriculos_api
from apps.backend.api import usuarios as usuarios_api
from apps.backend.api import vagas as vagas_api
from apps.backend.database.connection import engine, get_db
from apps.backend.main import app

PASSWORD = "senha-teste-123"


class Api:
  """Atalhos para as chamadas que se repetem nos testes."""

  def __init__(self, client: TestClient, connection):
    self.client = client
    self.connection = connection

  def request(self, method: str, path: str, token: str | None = None, json: dict | None = None, file: tuple[str, str] | None = None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    files = {"file": (file[0], file[1].encode(), "text/plain")} if file else None
    return self.client.request(method, "/api" + path, headers=headers, json=json, files=files)

  def register(self, name: str, kind: str = "candidate", email: str | None = None):
    email = email or self.email(name)
    return self.request("POST", "/auth/register", json={"name": f"Teste {name}", "email": email, "password": PASSWORD, "user_type": kind})

  def login(self, email: str):
    return self.request("POST", "/auth/login", json={"email": email, "password": PASSWORD})

  def user(self, name: str, kind: str = "candidate") -> str:
    self.register(name, kind)
    return self.login(self.email(name)).json()["access_token"]

  def vacancy(self, token: str, criteria: list[dict], title: str = "Dev Python", status: str = "open") -> int:
    response = self.request("POST", "/vagas", token, {"title": title, "description": "Backend", "status": status, "criteria": criteria})
    assert response.status_code == 201, response.text
    return response.json()["id"]

  def resume(self, token: str, content: str, filename: str = "curriculo.txt") -> int:
    response = self.request("POST", "/curriculos", token, file=(filename, content))
    assert response.status_code == 201, response.text
    return response.json()["id"]

  def apply(self, token: str, vacancy: int, resume: int):
    return self.request("POST", "/candidaturas", token, {"vacancy_id": vacancy, "resume_id": resume, "consent": True})

  def count(self, table: str, where: str, **params) -> int:
    return self.connection.execute(text(f"select count(*) from {table} where {where}"), params).scalar()

  @staticmethod
  def email(name: str) -> str:
    return f"pytest-{name}@example.com"


@pytest.fixture
def connection():
  try:
    connection = engine.connect()
  except OperationalError:
    pytest.skip("PostgreSQL indisponível: os testes de API usam o banco configurado no .env")
  transaction = connection.begin()
  try:
    yield connection
  finally:
    transaction.rollback()
    connection.close()


@pytest.fixture
def uploads(tmp_path, monkeypatch):
  for service in (curriculos_api.service, candidaturas_api.service, usuarios_api.service, vagas_api.candidaturas):
    monkeypatch.setattr(service, "upload_dir", tmp_path)
  return tmp_path


@pytest.fixture
def api(connection, uploads, monkeypatch):
  # Mesmo com JEV_ENABLED=true no .env, os testes nunca enviam currículos ao Jev.
  monkeypatch.setattr(candidaturas_api.service, "detector", None)
  monkeypatch.setattr(vagas_api.candidaturas, "detector", None)

  def session_per_request():
    # Uma sessão por requisição, como na aplicação; os commits viram savepoints da transação do teste.
    session = Session(bind=connection, join_transaction_mode="create_savepoint", autoflush=False, expire_on_commit=False)
    try:
      yield session
    finally:
      session.close()

  app.dependency_overrides[get_db] = session_per_request
  try:
    with TestClient(app) as client:
      yield Api(client, connection)
  finally:
    app.dependency_overrides.pop(get_db, None)
