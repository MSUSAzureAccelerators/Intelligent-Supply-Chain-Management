// Creates a KeyVault with Private Link Endpoint

@description('The Azure Region to deploy the resources into')
param location string = resourceGroup().location

@description('Tags to apply to the Key Vault Instance')
param tags object = {}

@description('The name of the Key Vault')
param keyvaultName string 

resource keyVault 'Microsoft.KeyVault/vaults@2021-10-01' = {
  name: keyvaultName
  location: location
  tags: tags
  properties: {
    createMode: 'default'
    enableSoftDelete: true
    enablePurgeProtection: true
    enabledForDeployment: true
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableRbacAuthorization: true
    sku: {
      family: 'A'
      name: 'standard'
    }
    softDeleteRetentionInDays: 7
    tenantId: subscription().tenantId
  }
}

output keyvaultId string = keyVault.id
