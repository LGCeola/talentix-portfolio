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

`GET /api/health` é pública e responde `200` com `{"status": "ok"}` quando a API e o banco estão no ar, ou `503` se o banco estiver fora. A Azure a usa para saber se o contêiner pode receber tráfego.

## Como rodar os testes

**Backend (pytest)**, a partir da raiz, com o ambiente virtual ativo (`.venv\Scripts\activate` no cmd, `.venv\Scripts\Activate.ps1` no PowerShell):

```powershell
python -m pytest apps/backend/tests                       # todos os testes
python -m pytest apps/backend/tests --cov --cov-report=term   # com cobertura (falha abaixo de 75%)
python -m pytest apps/backend/tests/test_storage.py -v    # um arquivo, listando cada teste
```

Os testes de API usam o PostgreSQL do `.env`. Com o banco desligado, eles aparecem como `skipped` e a cobertura cai.

**Frontend (Vitest)**, de dentro de `apps/web` (na primeira vez, rode `pnpm install`):

```powershell
pnpm test                 # todos os testes (arquivos *.spec.js)
pnpm test:coverage        # com cobertura (falha abaixo de 25%); relatório em coverage/index.html
pnpm test LoginPage       # só os testes cujo arquivo contém "LoginPage"
```

O CI (`.github/workflows/ci.yml`) roda esses mesmos comandos a cada push e pull request.

## Autenticação

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/auth/register` | Cria candidato ou recrutador. |
| `POST` | `/api/auth/login` | Autentica e devolve um access token JWT. |
| `GET` | `/api/auth/me` | Obtém o usuário autenticado. |

## Conta do usuário (LGPD, RFC 6.1)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `PATCH` | `/api/usuarios/me` | Atualiza nome e e-mail: `{"name", "email", "current_password"}`. A senha só é exigida ao trocar o e-mail. |
| `POST` | `/api/usuarios/me/exclusao` | Exclui a conta definitivamente: `{"password"}`. |

A exclusão não pode ser desfeita e remove, numa única transação:

- **Candidato:** currículos (também os arquivos em disco) e candidaturas, inclusive as já avaliadas. O candidato some do ranking das vagas.
- **Recrutador:** vagas, critérios e as candidaturas recebidas. Os candidatos perdem essas candidaturas, mas mantêm os próprios currículos.

Senha incorreta responde `403`, não `401`, porque a sessão continua válida. Se a remoção dos arquivos falhar, a conta já terá sido excluída e o erro fica no log para limpeza manual.

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

Os arquivos recebem um nome gerado pelo servidor (`<id do candidato>/<uuid>.pdf`) e são gravados por `integrations/storage.py`: localmente, em `UPLOAD_DIR` (padrão `apps/backend/uploads/`, fora do git); na Azure, quando `AZURE_STORAGE_ACCOUNT_URL` está configurada, no Blob Storage, acessado pela identidade gerenciada do contêiner, sem senha na aplicação. Recrutadores recebem `403`; um candidato que tenta acessar o currículo de outro recebe `404`.

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
| `GET` | `/api/vagas/{id}/candidaturas` | Ranking de candidatos da vaga, da maior para a menor nota, com o detalhe de cada critério. |
| `GET` | `/api/candidaturas/{id}/curriculo` | Baixa o arquivo original do currículo do candidato, só para o recrutador da vaga. |
| `PATCH` | `/api/candidaturas/{id}/status` | Registra a decisão sobre um candidato: `approved`, `rejected` ou `pending` (desfaz). |

### Candidato

| Método | Rota | Finalidade |
| --- | --- | --- |
| `GET` | `/api/vagas` | Lista as vagas publicadas, com critérios e pesos visíveis e o campo `already_applied`. |
| `GET` | `/api/vagas/{id}` | Detalhe de uma vaga publicada. Rascunhos e vagas encerradas respondem `404`. |
| `GET` | `/api/vagas/{id}/compatibilidade?resume_id=` | Simula a nota de um currículo próprio na vaga. Nada é gravado nem compartilhado (RF08). |

### Regras dos critérios

- Cada critério tem nome (2–50 caracteres, sem repetir na vaga), tipo (`habilidade`, `experiencia` ou `formacao`), peso inteiro de 1 a 100, que representa o percentual da nota final (0–100), e nível exigido (`required_level`, de 1 a 5, padrão 3).
- A soma dos pesos nunca passa de 100%. Rascunhos podem estar incompletos.
- Para publicar, a vaga precisa de descrição, ao menos um critério (RN03) e pesos somando exatamente 100%.
- Ciclo de vida: `draft` → `open` ⇄ `closed`. Rascunhos não podem ser encerrados, apenas excluídos.

## Candidaturas (somente candidatos)

| Método | Rota | Finalidade |
| --- | --- | --- |
| `POST` | `/api/candidaturas` | Candidata-se a uma vaga: `{"vacancy_id", "resume_id", "consent": true}`. |
| `GET` | `/api/candidaturas/consentimento` | Informa se o consentimento precisa citar o envio ao modelo externo: `{"external_analysis": bool}`. |
| `GET` | `/api/candidaturas/minhas` | Lista as candidaturas do candidato, com status e pontuação. |
| `DELETE` | `/api/candidaturas/{id}` | Desiste da candidatura — apenas enquanto estiver `pending`. |

Regras:

- `consent: true` é obrigatório: o currículo só é compartilhado com o recrutador mediante autorização explícita (LGPD, RFC 6.1). O momento do aceite é gravado em `consent_at`.
- A vaga precisa estar publicada; vagas encerradas respondem `409`. Um candidato só pode se candidatar uma vez por vaga (`409`).
- A decisão de aprovar ou rejeitar é sempre do recrutador dono da vaga (RN08), também depois de encerrada a vaga. Ela não altera nota nem ranking, e o sistema nunca a toma sozinho.
- A análise roda ao criar a candidatura e grava `overall_score`, `score_details` e `improvement_suggestions`. Só candidaturas anteriores a essa análise têm `overall_score` nulo.

## Análise de currículos

Código em `algorithm/`, sem dependência de HTTP ou banco. Testes: `python -m pytest apps/backend/tests`, a partir da raiz. Os testes de API (`test_api_*.py`) usam o PostgreSQL do `.env` dentro de uma transação desfeita ao final de cada teste, gravam arquivos numa pasta temporária e nunca chamam o Jev real. Sem banco disponível, eles são pulados.

**Cobertura:** `python -m pytest apps/backend/tests --cov`, a partir da raiz, usa o `.coveragerc` e falha abaixo de 75%. Ficam fora da conta os testes, as migrações (executadas pelo Alembic) e o script de `evaluation/`, que chama o Jev real. No frontend, `pnpm test:coverage` em `apps/web` faz o mesmo com Vitest e falha abaixo de 25% das linhas. O GitHub Actions (`.github/workflows/ci.yml`) roda os dois a cada push e pull request em `main` e `develop`, com um PostgreSQL criado do zero pelas migrações, e também faz o build do frontend.

**Análise estática:** com os testes aprovados, o job `sonarqube` envia o código e os dois relatórios de cobertura ao [SonarQube Cloud](https://sonarcloud.io/project/overview?id=LGCeola_talentix-portfolio), que aponta bugs, vulnerabilidades, código duplicado e problemas de manutenção. A configuração fica em `sonar-project.properties`, na raiz, e o token de acesso no secret `SONAR_TOKEN` do repositório.

**Dependências com hash:** o `requirements.txt` traz o hash SHA-256 de cada pacote, e o `pip` recusa qualquer arquivo diferente do publicado no PyPI. Para adicionar ou atualizar uma dependência, fixe a versão com `==` e inclua os hashes dela e de suas dependências (por exemplo, com `pip-compile --generate-hashes`, do pip-tools). Sem os hashes, a instalação falha.

- **Nota:** cada critério vale `peso × mínimo(nível ÷ nível exigido, 1)`, e a soma vai de 0 a 100. Acima do nível exigido não há pontos extras. Critérios ausentes ou a revisar não pontuam.
- **Níveis:** 0 = não encontrado; 1 = citado; 2 = estudou (curso ou disciplina); 3 = aplicou em projeto; 4 = uso profissional; 5 = referência (liderou, ensinou ou foi responsável técnico). Para formação: 1 = curso livre ou técnico (ou graduação trancada); 2 = graduação em andamento; 3 = concluída; 4 = pós-graduação; 5 = mestrado ou doutorado.
- **Busca (`keyword_matcher.py`):** procura o nome do critério no texto, ignorando caixa e acentos, e guarda o trecho como evidência. É sempre determinística.
- **Modelo externo (`analyzer.py`):** a interface `SemanticDetector` consulta um modelo sobre todos os critérios e recebe o nível mais provável e a confiança. Confiança abaixo de 0,7 deixa o critério "a revisar". O valor foi escolhido com os currículos fictícios de `evaluation/` e deve ser revisto com currículos reais. O Jev usa uma pergunta Score por critério, com as escalas descritas em `integrations/jev.py`. O cliente do Jev está em `integrations/jev.py` e fica **desligado por padrão no código** (`JEV_ENABLED=false`); nos ambientes da Azure está ligado. Com ele ligado, o consentimento da candidatura informa o envio à TypeSafe (RFC 6.1). A simulação de compatibilidade nunca usa o modelo, porque roda antes do consentimento.
- **Regra de conflito:** se a busca encontra o termo e o modelo responde nível 0, o critério fica "a revisar" e não pontua (ex.: "não tenho experiência com Python"). O recrutador vê o "a revisar" e pode baixar o currículo original para conferir antes de decidir. Confirmar o nível para somar pontos fica como trabalho futuro.
- **Só busca por termos:** com `JEV_ENABLED=false` ou com a API fora do ar, cada critério encontrado vale o peso inteiro, sem nível. `score_details.analysis_mode` registra `levels` ou `keywords`, e a tela avisa quando a análise foi só por termos.
- **Privacidade (`anonymizer.py`):** antes de sair do sistema, o texto perde e-mail, telefone, CPF, CEP, links de perfil, datas completas e o nome do candidato. É uma remoção por padrões: não garante eliminar qualquer dado pessoal escrito de outra forma, como um endereço.
- **Falha do modelo externo:** a candidatura continua válida e é analisada só pela busca por termos. Não há nova tentativa automática.
- **Versões:** `score_details.algorithm_version` é `3` a partir dos níveis. Candidaturas antigas mantêm a nota e os detalhes da versão em que foram analisadas.
- **Comparação (`evaluation/`):** `python -m apps.backend.evaluation.compare_levels --output resultado.json`, a partir da raiz, mede se o Jev estima o nível certo nos currículos fictícios de `levels.json` e calcula as notas em duas vagas de exemplo. Faz chamadas reais e pagas à API. Os currículos e rótulos foram escritos pela equipe do projeto.
- **Limitações:** só reconhece o termo exato, sem sinônimos (`APIs REST` não casa com `serviços web`), e não entende negação (`não tenho experiência com Python` conta como presente). Por isso o resultado apoia a triagem, e a decisão é do recrutador (RN08).

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
- `integrations/`: serviços externos — o Jev (`jev.py`) e o armazenamento dos arquivos (`storage.py`).

## Produção: Docker e monitoramento

**Imagens:** `apps/backend/Dockerfile` (API) e `apps/web/Dockerfile` (Vue compilado, servido pelo Nginx, que repassa `/api` para a API pelo endereço em `API_URL`). As duas rodam sem usuário root. Ao iniciar, a API aplica as migrações pendentes e sobe o Uvicorn. Arquivos `.env`, currículos, testes e scripts de avaliação ficam fora das imagens (`.dockerignore`).

```powershell
docker build -f apps/backend/Dockerfile -t talentix-api .
docker build -t talentix-web apps/web
```

O CI constrói as duas imagens e faz um teste de fumaça: sobe a API e o frontend com um PostgreSQL vazio e confere a tela e o `/api/health` pelo Nginx.

**Monitoramento:** com `APPLICATIONINSIGHTS_CONNECTION_STRING` configurada, `core/monitoring.py` liga o Azure Monitor (OpenTelemetry) e envia ao Application Insights as requisições (rota, status, duração), exceções, consultas ao PostgreSQL, chamadas externas e os logs de `apps.backend`, identificados pelo ambiente (`ENVIRONMENT`). O `/api/health` fica de fora, para não gerar ruído. Sem a variável, como localmente e nos testes, nada é enviado. Os dados descrevem as requisições, não o conteúdo dos currículos.
