# Deploy do Talentix (Azure)

O Talentix roda na Azure, na região **Brazil South** (São Paulo), o que mantém os dados pessoais no Brasil. A infraestrutura é criada por código (Bicep, pasta `infra/`), e cada versão é publicada automaticamente pelo GitHub Actions. Não há deploy manual por SSH, FTP ou portal.

## Arquitetura

```
Navegador ──HTTPS──▶ talentix-web-<env>  (Nginx + Vue, público)
                          │ /api (rede interna da Azure)
                          ▼
                     talentix-api-<env>  (FastAPI, interno)
                      │        │         │
                      ▼        ▼         ▼
              PostgreSQL   Blob Storage   Application Insights
            (banco do env) (currículos)   (monitoramento)
```

| Grupo de recursos | Conteúdo |
| --- | --- |
| `rg-talentix-shared` | PostgreSQL Flexible Server 18 (B1ms), com um banco e um usuário por ambiente; Log Analytics; identidade do GitHub Actions (`id-talentix-github`). |
| `rg-talentix-dev` | Ambiente de desenvolvimento: Container Apps (`talentix-web-dev`, `talentix-api-dev`), Storage Account e Application Insights. |
| `rg-talentix-prod` | Ambiente de produção, separado do dev, com os mesmos recursos, mais o teste de disponibilidade e o alerta por e-mail. |

**Ambientes:** um push na `develop` publica em **dev**; um push na `main`, feito só por pull request aprovado no CI, publica em **prod**. Cada ambiente tem o próprio banco, usuário, armazenamento, chave JWT e monitoramento: a API de dev não consegue ler os dados de prod.

## Segurança

- **Sem senhas no repositório.** O GitHub entra na Azure por OIDC: a identidade `id-talentix-github` só aceita tokens deste repositório, nos ambientes `dev` e `prod`, e só pode alterar os grupos `rg-talentix-dev` e `rg-talentix-prod`.
- **Segredos** (URL do banco, chave JWT, chave do Jev) ficam nos *secrets* de cada Container App.
- **Currículos:** a conta de armazenamento não aceita chaves (`allowSharedKeyAccess: false`); a API acessa com a própria identidade gerenciada, com permissão apenas de ler e gravar blobs.
- **Rede:** só o frontend é público, e só por HTTPS. A API é interna. O PostgreSQL aceita apenas conexões vindas da Azure, com TLS e usuário próprio de cada ambiente.
- **Contêineres** rodam sem usuário root.

## Pipeline (GitHub Actions)

A cada push em `develop` ou `main`, o workflow `CI` (`.github/workflows/ci.yml`):

1. Roda os testes do backend (cobertura ≥ 75%) e do frontend (cobertura ≥ 25%).
2. Envia a análise estática e de segurança ao SonarQube Cloud.
3. Constrói as imagens Docker e testa API e frontend juntos.
4. Se tudo passar, chama `deploy.yml`, que:
   - publica as imagens no GitHub Container Registry (`ghcr.io/lgceola/talentix-api` e `talentix-web`), com o commit como tag;
   - atualiza a API e depois o frontend do ambiente (a API aplica as migrações ao subir);
   - confere que `https://<frontend>/api/health` e a tela de login respondem.

O histórico de cada publicação fica na aba **Actions** e em **Environments** (`dev` e `prod`) do repositório.

## Criar a infraestrutura do zero

Só é necessário uma vez (ou para recriar tudo). Requisitos: [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) com Bicep (`az bicep install`) e Python com as dependências do backend.

1. Entre na Azure: `az login` (a conta precisa ser dona da assinatura).
2. Crie a parte compartilhada, informando uma senha forte para o administrador do PostgreSQL:
   ```powershell
   az deployment sub create -l brazilsouth -f infra/main.bicep -p postgresAdminPassword=<senha-admin>
   ```
   As saídas mostram o endereço do PostgreSQL e o `githubClientId`/`githubPrincipalId`.
3. Crie os bancos e usuários de cada ambiente, liberando o seu IP só enquanto o script roda:
   ```powershell
   az postgres flexible-server firewall-rule create -g rg-talentix-shared --server-name <servidor> --name temp-setup --start-ip-address <seu-ip>
   python infra/setup_databases.py <servidor>.postgres.database.azure.com <senha-admin> <senha-dev> <senha-prod>
   az postgres flexible-server firewall-rule delete -g rg-talentix-shared --server-name <servidor> --name temp-setup --yes
   ```
4. Publique as imagens (um push na `develop` faz isso) e crie cada ambiente:
   ```powershell
   az deployment group create -g rg-talentix-dev -f infra/environment.bicep -p `
     environmentName=dev githubPrincipalId=<githubPrincipalId> `
     apiImage=ghcr.io/lgceola/talentix-api:<commit> webImage=ghcr.io/lgceola/talentix-web:<commit> `
     databaseUrl="postgresql+psycopg2://talentix_dev:<senha-dev>@<servidor>.postgres.database.azure.com:5432/talentix_dev?sslmode=require" `
     jwtSecretKey=<chave-aleatoria> jevSecretKey=<chave-do-jev>
   ```
   Para prod, use `rg-talentix-prod`, `environmentName=prod`, o banco e o usuário `talentix_prod` e `alertEmail=<e-mail>`.
5. No GitHub, em *Settings → Environments*, crie `dev` (branch `develop`) e `prod` (branch `main`). Em *Settings → Secrets and variables → Actions → Variables*, crie `AZURE_CLIENT_ID` (o `githubClientId`), `AZURE_TENANT_ID` e `AZURE_SUBSCRIPTION_ID`. Esses valores identificam a conta, mas não dão acesso sem o token OIDC do GitHub.

A partir daí, todo push publica sozinho.

## Operação

**Custo:** os contêineres desligam quando não há acesso (custo zero) e ligam na próxima visita, que leva alguns segundos a mais. Para uma apresentação, deixe a produção sempre ligada e volte ao normal depois:

```powershell
az containerapp update -g rg-talentix-prod -n talentix-api-prod --min-replicas 1
az containerapp update -g rg-talentix-prod -n talentix-web-prod --min-replicas 1
# depois da apresentação:
az containerapp update -g rg-talentix-prod -n talentix-api-prod --min-replicas 0
az containerapp update -g rg-talentix-prod -n talentix-web-prod --min-replicas 0
```

**Trocar um segredo** (por exemplo, a chave do Jev), sem novo deploy:

```powershell
az containerapp secret set -g rg-talentix-prod -n talentix-api-prod --secrets jev-secret-key=<nova-chave>
az containerapp revision restart -g rg-talentix-prod -n talentix-api-prod --revision <revisao-ativa>
```

**Voltar para a versão anterior:** reverta o commit na branch (`git revert`) e faça push; o pipeline publica a versão anterior com os mesmos testes. Em emergência, `az containerapp update --image ghcr.io/lgceola/talentix-api:<commit-anterior>`.

**Logs e monitoramento:** no portal da Azure, em `appi-talentix-<env>` (Application Insights): *Failures* (erros), *Performance* (tempo de resposta por rota), *Availability* (teste do `/api/health` a cada 15 minutos, em prod), *Logs* (consultas KQL) e *Live Metrics*. Os logs dos contêineres ficam no Log Analytics `log-talentix`.
