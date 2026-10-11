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

## Currículos (somente candidatos)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/curriculos` | Envia um currículo (`multipart/form-data`, campo `file`). Aceita PDF ou TXT até `MAX_RESUME_SIZE_MB` (padrão 5 MB) e extrai o texto. |
| `GET` | `/api/curriculos` | Lista os currículos do candidato autenticado. |
| `GET` | `/api/curriculos/{id}` | Detalhe de um currículo próprio, incluindo o texto extraído. |
| `DELETE` | `/api/curriculos/{id}` | Exclui o currículo e o arquivo (bloqueado se houver candidaturas vinculadas). |

Os arquivos são gravados em `UPLOAD_DIR` (padrão `apps/backend/uploads/`, fora do git) com nome gerado pelo servidor. Recrutadores recebem `403`; um candidato que tenta acessar o currículo de outro recebe `404`.

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
