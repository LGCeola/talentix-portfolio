"""Monitoramento (Application Insights) e rota de saúde."""
import sys
import types

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from apps.backend.core import monitoring
from apps.backend.core.config import settings
from apps.backend.database.connection import get_db
from apps.backend.main import app


def test_monitoring_stays_off_without_connection_string(monkeypatch):
  monkeypatch.setattr(settings, "APPLICATIONINSIGHTS_CONNECTION_STRING", None)
  assert monitoring.setup_monitoring(FastAPI()) is False


def test_monitoring_sends_requests_and_logs_to_application_insights(monkeypatch):
  calls = {}
  fake_azure = types.SimpleNamespace(configure_azure_monitor=lambda **kwargs: calls.update(kwargs))

  class FakeInstrumentor:
    @staticmethod
    def instrument_app(instrumented, excluded_urls):
      calls["app"], calls["excluded_urls"] = instrumented, excluded_urls

  monkeypatch.setitem(sys.modules, "azure.monitor.opentelemetry", fake_azure)
  monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.fastapi", types.SimpleNamespace(FastAPIInstrumentor=FakeInstrumentor))
  monkeypatch.setattr(settings, "APPLICATIONINSIGHTS_CONNECTION_STRING", "InstrumentationKey=teste")
  monkeypatch.setattr(settings, "ENVIRONMENT", "dev")
  target = FastAPI()

  assert monitoring.setup_monitoring(target) is True

  assert calls["connection_string"] == "InstrumentationKey=teste"
  assert calls["logger_name"] == "apps.backend"
  assert calls["resource"].attributes["deployment.environment"] == "dev"
  assert calls["resource"].attributes["service.name"] == "talentix-api"
  assert calls["app"] is target
  assert calls["excluded_urls"] == "api/health"


def test_health_reports_the_database(api):
  response = api.request("GET", "/health")
  assert response.status_code == 200
  assert response.json()["status"] == "ok"
  assert response.json()["database"] == "up"


def test_health_returns_503_when_the_database_is_down(api):
  class BrokenSession:
    def execute(self, *args):
      raise OperationalError("SELECT 1", {}, Exception("banco fora do ar"))

  app.dependency_overrides[get_db] = lambda: BrokenSession()
  response = api.request("GET", "/health")
  assert response.status_code == 503
  assert response.json() == {"status": "unavailable", "database": "down"}
