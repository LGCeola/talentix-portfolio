"""Monitoramento com o Azure Monitor (Application Insights), via OpenTelemetry.

Ligado só quando APPLICATIONINSIGHTS_CONNECTION_STRING está configurada, ou seja, nos ambientes da Azure.
Envia requisições HTTP (rota, status, duração), exceções, consultas ao PostgreSQL, chamadas externas
(como o Jev) e os logs da aplicação. Localmente e nos testes, não faz nada.

Privacidade: os dados enviados descrevem as requisições (método, rota, status, tempo), não o conteúdo
dos currículos. Os logs da aplicação não registram texto de currículo.
"""
import logging

from fastapi import FastAPI

from apps.backend.core.config import settings

logger = logging.getLogger(__name__)

# A checagem de saúde roda a cada poucos segundos e só geraria ruído (e custo) no monitoramento.
_EXCLUDED_URLS = "api/health"


def setup_monitoring(app: FastAPI) -> bool:
  if not settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
    return False

  from azure.monitor.opentelemetry import configure_azure_monitor
  from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
  from opentelemetry.sdk.resources import Resource

  configure_azure_monitor(
    connection_string=settings.APPLICATIONINSIGHTS_CONNECTION_STRING,
    # Só os logs da aplicação (apps.backend.*), sem o ruído das bibliotecas.
    logger_name="apps.backend",
    resource=Resource.create({
      "service.name": "talentix-api",
      "service.version": settings.APP_VERSION,
      "deployment.environment": settings.ENVIRONMENT,
    }),
    # O app já foi criado: a instrumentação automática do FastAPI não o alcançaria, então é feita abaixo.
    instrumentation_options={"fastapi": {"enabled": False}},
  )
  FastAPIInstrumentor.instrument_app(app, excluded_urls=_EXCLUDED_URLS)
  logging.getLogger("apps.backend").setLevel(logging.INFO)
  logger.info("Monitoramento ligado (ambiente %s)", settings.ENVIRONMENT)
  return True
