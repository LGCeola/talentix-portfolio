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

## Vagas (somente recrutadores)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/api/vagas/minhas` | Lista as vagas do recrutador com contagem de critérios e candidaturas. |
| `POST` | `/api/vagas` | Cria uma vaga com critérios. `status`: `draft` (padrão) ou `open` (publicar). |
| `GET` | `/api/vagas/{id}` | Detalhe de uma vaga própria com seus critérios. |
| `PUT` | `/api/vagas/{id}` | Substitui conteúdo e critérios. Bloqueado para vagas encerradas ou que já têm candidaturas. |
| `PATCH` | `/api/vagas/{id}/status` | Publica (`open`) ou encerra (`closed`) a vaga. |
| `DELETE` | `/api/vagas/{id}` | Exclui a vaga — apenas rascunhos. |

Regras dos critérios:

- Cada critério tem nome (2–50 caracteres, sem repetir na vaga), tipo (`habilidade`, `experiencia` ou `formacao`) e peso inteiro de 1 a 100, que representa o percentual da nota final (0–100).
- A soma dos pesos nunca passa de 100%. Rascunhos podem estar incompletos.
- Para publicar, a vaga precisa de descrição, ao menos um critério (RN03) e pesos somando exatamente 100%.
- Ciclo de vida: `draft` → `open` ⇄ `closed`. Rascunhos não podem ser encerrados, apenas excluídos.

Os arquivos de currículo são gravados em `UPLOAD_DIR` (padrão `apps/backend/uploads/`, fora do git) com nome gerado pelo servidor. Recrutadores recebem `403`; um candidato que tenta acessar o currículo de outro recebe `404`.

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
