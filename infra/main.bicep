// Infraestrutura compartilhada do Talentix na Azure: grupos de recursos, PostgreSQL, logs e a identidade
// usada pelo GitHub Actions. Os ambientes (dev e prod) ficam em environment.bicep.
//   az deployment sub create -l brazilsouth -f infra/main.bicep -p postgresAdminPassword=<senha>
targetScope = 'subscription'

@description('Região de todos os recursos. Brazil South mantém os dados pessoais no Brasil (LGPD).')
param location string = 'brazilsouth'

@description('Repositório do GitHub autorizado a publicar nos ambientes (OIDC, sem senha).')
param githubRepository string = 'LGCeola/talentix-portfolio'

@secure()
@description('Senha do administrador do PostgreSQL. Usada só para criar os usuários de cada ambiente.')
param postgresAdminPassword string

var tags = { projeto: 'talentix' }

resource sharedGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-talentix-shared'
  location: location
  tags: tags
}

resource devGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-talentix-dev'
  location: location
  tags: union(tags, { ambiente: 'dev' })
}

resource prodGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-talentix-prod'
  location: location
  tags: union(tags, { ambiente: 'prod' })
}

module shared 'modules/shared.bicep' = {
  name: 'talentix-shared'
  scope: sharedGroup
  params: {
    location: location
    tags: tags
    githubRepository: githubRepository
    postgresAdminPassword: postgresAdminPassword
  }
}

output postgresHost string = shared.outputs.postgresHost
output logAnalyticsName string = shared.outputs.logAnalyticsName
output githubClientId string = shared.outputs.githubClientId
output githubPrincipalId string = shared.outputs.githubPrincipalId
