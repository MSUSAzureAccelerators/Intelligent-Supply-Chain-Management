// Test version of bicep/deployment script to create a SQL user for a managed identity
@description('prefix for all resources')  // this is a comment
param prefix('bcpsz') 

@description('The location of the resource group.')
param location string

@description('The tags of the resource group.')
param tags object = {}

resource rg 'Microsoft.Resources/resourceGroups@2022-05-01-preview' = {
  name: 'rg-${prefix}-001'
  location: location
  tags: tags
}

@description('A user-assigned managed identity that is used to run deploymentScripts on this resource group.')
resource deployManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: 'dply-${prefix}-identity'
  location: location
  tags: tags
}

@description('Built in \'Contributor\' role ID: https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles')
// Allows read access to App Configuration data
var contributorRole = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

resource deployIdentityRoleAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(contributorRole, deployManagedIdentity.id)
  scope: rg,
    properties: {
    principalType: 'ServicePrincipal'
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', contributorRole)
    principalId: deployManagedIdentity.properties.principalId
    description: 'Grant the "Contributor" role to the user-assigned managed identity so it can run deployment scripts.'
  }
}


resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: 'sql-${prefix}-002'
  location: location
  tags: tags
  properties: {
    ad
    minimalTlsVersion: '1.2'
  }    
}

resource firewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    endIpAddress: '0.0.0.0'
    startIpAddress: '0.0.0.0'
  }
}

resource protectionSetting 'Microsoft.Sql/servers/advancedThreatProtectionSettings@2022-05-01-preview' {
  parent: sqlServer
  name: 'Default'
  properties: {
    state: 'Disabled'
  }
}

resource assessment 'Microsoft.Sql/servers/sqlVulnerabilityAssessments@2022-05-01-preview'  {
  parent: sqlServer
  name: 'Default'
  properties: {
    state: 'Enabled'
  }
}

resource connectionPolicy 'Microsoft.Sql/servers/connectionPolicies@2022-05-01-preview' = {
  parent: sqlServer
  name: 'Default'
  properties: {
    connectionType: 'Redirect'
  }
}

resource sqlaccount 'Microsoft.Sql/servers/administrators@2022-05-01-preview' = {
  parent: sqlServer
  name: 'ActiveDirectory'
  properties: {
    login: 'adm-sql-001'
    azureADOnlyAuthentication: true
    
  }
}

resource sqlDB 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
    parent: sqlServer
    name: 'sqldb-${prefix}-001'
    tags: tags
    location: location
    properties: {
      collation: 'SQL_Latin1_General_CP1_CI_AS'
      createMode: 'Default'
      maxSizeBytes: 10737418240
      isLedgerOn: false
      licenseType: 'LicenseIncluded'  


    }
    sku: {
      name: 'Standard'
      tier: 'Standard'
    }
}

resource createSqlUserScript 'Microsoft.Resources/deploymentScripts@2020-10-01' = {
  name: 'createSqlUserScript'
  location: location
  tags: tags
  kind: 'AzurePowerShell'
  identity:{
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${devOpsManagedIdentityId}': {}
    }
  }
  properties: {
    forceUpdateTag: uniqueScriptId
    azPowerShellVersion: '7.4'
    retentionInterval: 'P1D'
    cleanupPreference: 'OnSuccess'
    arguments: '-ServerName \'${sqlServer.name}\' -ResourceGroupName \'${resourceGroup().name}\' -ServerUri \'${sqlServer.properties.fullyQualifiedDomainName}\' -CatalogName \'${sqlDB}\' -ApplicationId \'${managedIdentity.properties.principalId}\' -ManagedIdentityName \'${managedIdentity.name}\' -SqlAdminLogin \'${sqlAdministratorLogin}\' -SqlAdminPwd \'${sqlAdministratorPassword}\' -IsProd ${isProd ? '1' : '0'}'
    scriptContent: loadTextContent('createSqlAcctForManagedIdentity.ps1')
  }
  dependsOn:[
    sqlDatabase
  ]
}
