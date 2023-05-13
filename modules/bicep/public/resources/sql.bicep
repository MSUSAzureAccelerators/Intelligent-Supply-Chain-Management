@description('The name of the SQL logical server.')
param sqlServerName string

@description('The name of the SQL Database')
param sqlDBName string

@description('Tags to add to the resources')
param tags object

@description('Location for all resources.')
param location string 

@description('The administrator username of the SQL logical server.')
param administratorLogin string

@description('The administrator password of the SQL logical server.')
@secure()
param administratorLoginPassword string

@description('Enable Microsoft Defender for SQL, the user deploying the template must have an administrator or owner permissions.')
param enableSqlDefender bool = false

@description('Allow Azure services to access server.')
param allowAzureIPs bool = true

@description('SQL logical server connection type.')
@allowed([
  'Default'
  'Redirect'
  'Proxy'
])
param connectionType string = 'Default'

resource sqlServer 'Microsoft.Sql/servers@2022-05-01-preview' = {
  name: sqlServerName
  location: location
  tags: tags
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    minimalTlsVersion: '1.2'
  }    
}

resource firewallRule 'Microsoft.Sql/servers/firewallRules@2022-05-01-preview' = if (allowAzureIPs) {
  parent: sqlServer
  name: 'AllowAllWindowsAzureIps'
  properties: {
    endIpAddress: '0.0.0.0'
    startIpAddress: '0.0.0.0'
  }
}

resource protectionSetting 'Microsoft.Sql/servers/advancedThreatProtectionSettings@2022-05-01-preview' = if (enableSqlDefender) {
  parent: sqlServer
  name: 'Default'
  properties: {
    state: 'Enabled'
  }
}

resource assessment 'Microsoft.Sql/servers/sqlVulnerabilityAssessments@2022-05-01-preview' = if (enableSqlDefender) {
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
    connectionType: connectionType
  }
}

resource sqlDB 'Microsoft.Sql/servers/databases@2022-05-01-preview' = {
    parent: sqlServer
    name: sqlDBName
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
