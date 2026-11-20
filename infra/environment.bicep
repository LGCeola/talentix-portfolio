// Um ambiente do Talentix (dev ou prod), no seu próprio grupo de recursos:
// frontend público (Nginx + Vue), API interna, armazenamento dos currículos e monitoramento.
//   az deployment group create -g rg-talentix-<env> -f infra/environment.bicep -p environmentName=<env> ...
// Depois da criação, o CD (GitHub Actions) só troca as imagens dos contêineres.

@allowed(['dev', 'prod'])
param environmentName string
param location string = resourceGroup().location

@description('Imagens publicadas pelo CD no GitHub Container Registry.')
param apiImage string
param webImage string

@description('Grupo e nome do Log Analytics compartilhado (infra/main.bicep).')
param sharedResourceGroup string = 'rg-talentix-shared'
param logAnalyticsName string = 'log-talentix'

@description('Identidade do GitHub Actions, que recebe permissão para atualizar este ambiente.')
param githubPrincipalId string

@description('Quem recebe o e-mail quando o site sai do ar (só em prod).')
param alertEmail string = ''

@secure()
@description('URL de conexão com o banco do ambiente, com o usuário próprio do ambiente e sslmode=require.')
param databaseUrl string

@secure()
param jwtSecretKey string

@secure()
param jevSecretKey string

param jevEnabled bool = true

var tags = { projeto: 'talentix', ambiente: environmentName }
var suffix = uniqueString(resourceGroup().id)
var isProd = environmentName == 'prod'
var apiName = 'talentix-api-${environmentName}'
var webName = 'talentix-web-${environmentName}'

// ---------- Monitoramento ----------

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: logAnalyticsName
  scope: resourceGroup(sharedResourceGroup)
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-talentix-${environmentName}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
    RetentionInDays: 30
  }
}

// ---------- Currículos (Blob Storage, sem chave de acesso) ----------

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: take('sttalentix${environmentName}${suffix}', 24)
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    // Só identidades do Entra ID acessam: nenhuma chave da conta pode ser usada.
    allowSharedKeyAccess: false
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
  properties: {
    // Arquivos apagados podem ser recuperados por 7 dias, em caso de exclusão por engano.
    deleteRetentionPolicy: { enabled: true, days: 7 }
  }
}

resource resumes 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'curriculos'
  properties: { publicAccess: 'None' }
}

// Identidade da API: lê e grava currículos, e nada além disso.
resource apiIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'id-${apiName}'
  location: location
  tags: tags
}

var storageBlobDataContributor = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource apiBlobAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, apiIdentity.id, storageBlobDataContributor)
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributor)
    principalId: apiIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// O GitHub Actions pode atualizar os recursos deste grupo (novas imagens), e de nenhum outro.
var contributor = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

resource githubAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, githubPrincipalId, contributor)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', contributor)
    principalId: githubPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// ---------- Contêineres ----------

resource containerEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-talentix-${environmentName}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${apiIdentity.id}': {} }
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      // Interna: só o frontend, dentro do mesmo ambiente, chama a API (por HTTPS, exigido pelo ambiente Express).
      ingress: {
        external: false
        targetPort: 8000
        transport: 'auto'
      }
      secrets: [
        { name: 'database-url', value: databaseUrl }
        { name: 'jwt-secret-key', value: jwtSecretKey }
        { name: 'jev-secret-key', value: jevSecretKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: apiImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'DATABASE_URL', secretRef: 'database-url' }
            { name: 'JWT_SECRET_KEY', secretRef: 'jwt-secret-key' }
            { name: 'JEV_ENABLED', value: string(jevEnabled) }
            { name: 'JEV_SECRET_KEY', secretRef: 'jev-secret-key' }
            { name: 'AZURE_STORAGE_ACCOUNT_URL', value: storage.properties.primaryEndpoints.blob }
            { name: 'AZURE_STORAGE_CONTAINER', value: resumes.name }
            // Faz o DefaultAzureCredential usar a identidade da API.
            { name: 'AZURE_CLIENT_ID', value: apiIdentity.properties.clientId }
            { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: insights.properties.ConnectionString }
            { name: 'ENVIRONMENT', value: environmentName }
          ]
          probes: [
            {
              type: 'Readiness'
              httpGet: { path: '/api/health', port: 8000 }
              initialDelaySeconds: 5
              periodSeconds: 10
              failureThreshold: 6
            }
          ]
        }
      ]
      // Sem acessos, a API desliga (custo zero) e liga de novo na próxima requisição.
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

resource web 'Microsoft.App/containerApps@2024-03-01' = {
  name: webName
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      // Público, só por HTTPS (certificado gerenciado pela Azure).
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: 'web'
          image: webImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            { name: 'API_URL', value: 'https://${api.properties.configuration.ingress.fqdn}' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: isProd ? 2 : 1
      }
    }
  }
}

// ---------- Alerta de disponibilidade (prod) ----------

resource alertGroup 'Microsoft.Insights/actionGroups@2023-01-01' = if (isProd && !empty(alertEmail)) {
  name: 'ag-talentix-${environmentName}'
  location: 'global'
  tags: tags
  properties: {
    groupShortName: 'talentix'
    enabled: true
    emailReceivers: [
      { name: 'responsavel', emailAddress: alertEmail, useCommonAlertSchema: true }
    ]
  }
}

// A cada 15 minutos, de duas regiões, abre o /api/health pelo frontend: testa site, API e banco juntos.
resource availabilityTest 'Microsoft.Insights/webtests@2022-06-15' = if (isProd) {
  name: 'webtest-talentix-${environmentName}'
  location: location
  tags: union(tags, { 'hidden-link:${insights.id}': 'Resource' })
  kind: 'standard'
  properties: {
    SyntheticMonitorId: 'webtest-talentix-${environmentName}'
    Name: 'Talentix ${environmentName} - /api/health'
    Kind: 'standard'
    Enabled: true
    Frequency: 900
    // Folga para o contêiner ligar quando estava desligado por falta de acessos.
    Timeout: 120
    RetryEnabled: true
    Locations: [
      { Id: 'latam-br-gru-edge' }
      { Id: 'us-va-ash-azr' }
    ]
    Request: {
      RequestUrl: 'https://${web.properties.configuration.ingress.fqdn}/api/health'
      HttpVerb: 'GET'
    }
    ValidationRules: {
      ExpectedHttpStatusCode: 200
      SSLCheck: true
      SSLCertRemainingLifetimeCheck: 7
    }
  }
}

resource availabilityAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = if (isProd && !empty(alertEmail)) {
  name: 'alert-talentix-${environmentName}-fora-do-ar'
  location: 'global'
  tags: tags
  properties: {
    description: 'O Talentix (${environmentName}) não respondeu ao /api/health nas duas regiões de teste.'
    severity: 1
    enabled: true
    scopes: [insights.id, availabilityTest.id]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.WebtestLocationAvailabilityCriteria'
      webTestId: availabilityTest.id
      componentId: insights.id
      failedLocationCount: 2
    }
    actions: [
      { actionGroupId: alertGroup.id }
    ]
  }
}

output webUrl string = 'https://${web.properties.configuration.ingress.fqdn}'
output apiName string = api.name
output webName string = web.name
output insightsName string = insights.name
output storageAccountName string = storage.name
