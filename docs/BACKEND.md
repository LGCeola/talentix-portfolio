# Backend Talentix

## Configuração

Todos os comandos partem da **raiz do repositório** (`talentix-portfolio/`).

1. Crie e ative o ambiente virtual:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   O terminal deve exibir `(.venv)`. Se o PowerShell bloquear o script, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
2. Instale as dependências: `pip install -r apps/backend/requirements.txt`.
3. Copie `apps/backend/.env.example` para `apps/backend/.env` e preencha a URL do PostgreSQL e uma chave JWT forte.
4. Aplique as migrações (o Alembic roda de dentro de `apps/backend/`):
   ```powershell
   cd apps/backend; alembic upgrade head; cd ../..
   ```
5. Inicie a API: `uvicorn apps.backend.main:app --reload`. Ela sobe em `http://localhost:8000` (documentação interativa em `/docs`).

Envie o token retornado pelo login no header `Authorization: Bearer <token>` para as rotas protegidas.

## Autenticação

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

## Currículos (somente candidatos)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/curriculos` | Envia um currículo (`multipart/form-data`, campo `file`). Aceita PDF ou TXT até `MAX_RESUME_SIZE_MB` (padrão 5 MB) e extrai o texto. |
| `GET` | `/api/curriculos` | Lista os currículos do candidato autenticado. |
| `GET` | `/api/curriculos/{id}` | Detalhe de um currículo próprio, incluindo o texto extraído. |
| `DELETE` | `/api/curriculos/{id}` | Exclui o currículo e o arquivo (bloqueado se houver candidaturas vinculadas). |

Os arquivos são gravados em `UPLOAD_DIR` (padrão `apps/backend/uploads/`, fora do git) com nome gerado pelo servidor. Recrutadores recebem `403`; um candidato que tenta acessar o currículo de outro recebe `404`.

## Vagas

### Recrutador

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/api/vagas/minhas` | Lista as vagas do recrutador com contagem de critérios e candidaturas. |
| `POST` | `/api/vagas` | Cria uma vaga com critérios. `status`: `draft` (padrão) ou `open` (publicar). |
| `GET` | `/api/vagas/{id}` | Detalhe de uma vaga própria, em qualquer status. |
| `PUT` | `/api/vagas/{id}` | Substitui conteúdo e critérios. Bloqueado para vagas encerradas ou que já têm candidaturas. |
| `PATCH` | `/api/vagas/{id}/status` | Publica (`open`) ou encerra (`closed`) a vaga. |
| `DELETE` | `/api/vagas/{id}` | Exclui a vaga — apenas rascunhos. |
| `GET` | `/api/vagas/{id}/candidaturas` | Lista quem se candidatou à vaga (nome, e-mail, currículo e data do consentimento). |

### Candidato

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/api/vagas` | Lista as vagas publicadas, com critérios e pesos visíveis e o campo `already_applied`. |
| `GET` | `/api/vagas/{id}` | Detalhe de uma vaga publicada. Rascunhos e vagas encerradas respondem `404`. |

### Regras dos critérios

- Cada critério tem nome (2–50 caracteres, sem repetir na vaga), tipo (`habilidade`, `experiencia` ou `formacao`) e peso inteiro de 1 a 100, que representa o percentual da nota final (0–100).
- A soma dos pesos nunca passa de 100%. Rascunhos podem estar incompletos.
- Para publicar, a vaga precisa de descrição, ao menos um critério (RN03) e pesos somando exatamente 100%.
- Ciclo de vida: `draft` → `open` ⇄ `closed`. Rascunhos não podem ser encerrados, apenas excluídos.

## Candidaturas (somente candidatos)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/candidaturas` | Candidata-se a uma vaga: `{"vacancy_id", "resume_id", "consent": true}`. |
| `GET` | `/api/candidaturas/minhas` | Lista as candidaturas do candidato, com status e pontuação. |
| `DELETE` | `/api/candidaturas/{id}` | Desiste da candidatura — apenas enquanto estiver `pending`. |

Regras:

- `consent: true` é obrigatório: o currículo só é compartilhado com o recrutador mediante autorização explícita (LGPD, RFC 6.1). O momento do aceite é gravado em `consent_at`.
- A vaga precisa estar publicada; vagas encerradas respondem `409`. Um candidato só pode se candidatar uma vez por vaga (`409`).
- `overall_score` fica `null` até o algoritmo de avaliação (M5) ser executado.

## Erros

Os services lançam exceções de domínio (`core/exceptions.py`) sem conhecer HTTP. Um handler central (`core/exception_handlers.py`) converte cada categoria em status code, sempre no formato `{"detail": "mensagem"}`:

| Exceção | Status |
| --- | --- |
| `NaoEncontrado` (`VagaNaoEncontrada`, `CurriculoNaoEncontrado`, ...) | `404` |
| `CredenciaisInvalidas` | `401` |
| `AcessoNegado` | `403` |
| `Conflito` (`EmailJaCadastrado`, `CandidaturaDuplicada`, ...) | `409` |
| `FormatoNaoSuportado` | `415` |
| `ArquivoMuitoGrande` | `413` |
| `RegraDeNegocioViolada` (`VagaNaoPublicavel`, `CurriculoInvalido`, ...) | `422` |

## Arquitetura em camadas

Uma requisição percorre `api → services → repositories → models`:

- `api/`: controllers HTTP — rotas, autenticação/perfil e status de resposta.
- `schemas/`: contratos Pydantic de entrada e saída (o que o cliente envia e recebe).
- `services/`: regras de negócio, independentes de HTTP.
- `repositories/`: consultas e gravação no banco.
- `models/`: entidades SQLAlchemy (tabelas).
- `core/`: configuração, segurança, dependências e exceções.
- `algorithm/`: análise determinística do currículo, sem depender do HTTP.
