# Backend Talentix

## Configuração

1. Copie `apps/backend/.env.example` para `apps/backend/.env` e preencha a URL do PostgreSQL e uma chave JWT forte.
2. Instale as dependências com `pip install -r requirements.txt`.
3. Entre em `apps/backend/` e aplique o schema com `alembic upgrade head`.
4. Inicie a API com `uvicorn apps.backend.main:app --reload`.

## Primeiro fluxo disponível

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Cria candidato ou recrutador. |
| `POST` | `/api/auth/login` | Autentica e devolve um access token JWT. |
| `GET` | `/api/auth/me` | Obtém o usuário autenticado. |

Exemplo de cadastro:

```json
{
  "name": "Ana Silva",
  "email": "ana@example.com",
  "password": "uma-senha-com-pelo-menos-8-caracteres",
  "user_type": "candidate"
}
```

Envie o token retornado no header `Authorization: Bearer <token>` para rotas protegidas.

## Organização MVC

- `api/`: controllers HTTP e rotas.
- `schemas/`: contratos Pydantic de entrada e saída.
- `services/`: regras de negócio.
- `repositories/`: acesso aos dados.
- `models/`: entidades SQLAlchemy.
- `algorithm/`: análise determinística do currículo, sem depender do HTTP.
