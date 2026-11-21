// Recursos usados pelos dois ambientes: um servidor PostgreSQL (um banco e um usuário por ambiente,
// criados por infra/setup_databases.py), o Log Analytics e a identidade do GitHub Actions.
param location string
param tags object
param githubRepository string

@secure()
param postgresAdminPassword string

var suffix = uniqueString(resourceGroup().id)

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-talentix'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    // Teto diário de ingestão para o custo nunca fugir do controle.
    workspaceCapping: { dailyQuotaGb: 1 }
  }
}

// Um único ambiente de contêineres para dev e prod: a assinatura de estudante permite só um por região.
// Sem escolher o modo, a Azure cria o modo Express, que não tem rede interna entre os apps.
// O perfil Consumption cobra só pelo uso e desliga os contêineres sem acesso.
resource containerEnv 'Microsoft.App/managedEnvironments@2026-07-01' = {
  name: 'cae-talentix'
  location: location
  tags: tags
  properties: {
    environmentMode: 'WorkloadProfiles'
    workloadProfiles: [
      { name: 'Consumption', workloadProfileType: 'Consumption' }
    ]
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: 'psql-talentix-${suffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '18'
    administratorLogin: 'talentixadmin'
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 32
      autoGrow: 'Disabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
    highAvailability: { mode: 'Disabled' }
    network: { publicNetworkAccess: 'Enabled' }
  }
}

// Os Container Apps não têm IP de saída fixo; esta regra libera só o tráfego que vem de dentro da Azure.
// O acesso continua exigindo usuário, senha e TLS (require_secure_transport, padrão do servidor).
resource allowAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: postgres
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// Identidade do GitHub Actions: só o repositório, e só nos ambientes dev e prod, conseguem usá-la (OIDC).
resource github 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-talentix-github'
  location: location
  tags: tags
}

resource githubDev 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: github
  name: 'github-dev'
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubRepository}:environment:dev'
    audiences: ['api://AzureADTokenExchange']
  }
}

resource githubProd 'Microsoft.ManagedIdentity/userAssignedIdentities/federatedIdentityCredentials@2023-01-31' = {
  parent: github
  name: 'github-prod'
  // A Azure não aceita duas credenciais federadas sendo gravadas ao mesmo tempo.
  dependsOn: [githubDev]
  properties: {
    issuer: 'https://token.actions.githubusercontent.com'
    subject: 'repo:${githubRepository}:environment:prod'
    audiences: ['api://AzureADTokenExchange']
  }
}

output postgresHost string = postgres.properties.fullyQualifiedDomainName
output postgresName string = postgres.name
output logAnalyticsName string = logs.name
output githubClientId string = github.properties.clientId
output githubPrincipalId string = github.properties.principalId
