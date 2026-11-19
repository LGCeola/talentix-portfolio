# Imagem da API (FastAPI). Construída a partir da raiz do repositório:
#   docker build -f apps/backend/Dockerfile -t talentix-api .
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependências primeiro: a camada só é refeita quando o requirements.txt muda.
# Mesma regra do CI: só pacotes já compilados e conferidos pelos hashes.
COPY apps/backend/requirements.txt apps/backend/requirements.txt
RUN pip install --require-hashes --only-binary :all: -r apps/backend/requirements.txt

COPY apps/backend apps/backend

# A aplicação não roda como root: um usuário sem privilégios e sem acesso de escrita ao código.
RUN useradd --system --no-create-home --uid 10001 talentix
USER 10001

EXPOSE 8000

# Aplica as migrações pendentes e sobe a API. O ambiente roda uma única réplica, então não há
# duas migrações ao mesmo tempo. --proxy-headers: a Azure termina o HTTPS antes do contêiner.
WORKDIR /app/apps/backend
CMD ["sh", "-c", "python -m alembic upgrade head && exec uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'"]
