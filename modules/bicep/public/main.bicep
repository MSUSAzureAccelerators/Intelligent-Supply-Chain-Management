// Execute this main file to configure Azure Machine Learning end-to-end in a moderately secure set up

// Parameters
@minLength(2)
@maxLength(10)
@description('Prefix for all resource names.')
param prefix string = 'opti1'

@description('Azure region used for the deployment of all resources.')
param location string = resourceGroup().location

@description('Set of tags to apply to all resources.')
param tags object = {}

@description('Enable public IP for Azure Machine Learning compute nodes')
param amlComputePublicIp bool = true

@description('VM size for the default compute cluster')
param amlComputeDefaultVmSize string = 'Standard_F8s_v2' // TBD - review size dependently on workload/needs

// Variables
var name = toLower('${prefix}')

// Create a short, unique suffix, that will be unique to each resource group
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 4)

@description('Kubernetes version of the Azure Kubernetes Service cluster')
param kubernetesVersion string = '1.24.6' // https://docs.microsoft.com/en-us/azure/aks/supported-kubernetes-versions

// Dependent resources for the Azure Machine Learning workspace
module keyvault 'resources/keyvault.bicep' = {
  name: 'kv-${name}-${uniqueSuffix}-deployment'
  params: {
    location: location
    keyvaultName: 'kv-${name}-${uniqueSuffix}'
    tags: tags
  }
} 
output keyvaultName string = keyvault.outputs.keyvaultName

module storage 'resources/storage.bicep' = {
  name: 'st${name}${uniqueSuffix}-deployment'
  params: {
    location: location
    storageName: 'st${name}${uniqueSuffix}'
    storageSkuName: 'Standard_LRS'
    tags: tags
  }
}

module containerRegistry 'resources/containerregistry.bicep' = {
  name: 'cr${name}${uniqueSuffix}-deployment'
  params: {
    location: location
    containerRegistryName: 'cr${name}${uniqueSuffix}'
    tags: tags
  }
}

module applicationInsights 'resources/applicationinsights.bicep' = {
  name: 'appi-${name}-${uniqueSuffix}-deployment'
  params: {
    location: location
    applicationInsightsName: 'appi-${name}-${uniqueSuffix}'
    tags: tags
  }
}

module azuremlWorkspace 'resources/machinelearning.bicep' = {
  name: 'mlw-${name}-${uniqueSuffix}-deployment'
  params: {
    // workspace organization
    machineLearningName: 'mlw-${name}-${uniqueSuffix}'
    machineLearningFriendlyName: 'Sample workspace'
    machineLearningDescription: 'This is an example workspace.'
    location: location
    prefix: name
    tags: tags
    kubernetesVersion: kubernetesVersion

    // dependent resources
    applicationInsightsId: applicationInsights.outputs.applicationInsightsId
    containerRegistryId: containerRegistry.outputs.containerRegistryId
    keyVaultId: keyvault.outputs.keyvaultId
    storageAccountId: storage.outputs.storageId

    // compute
    amlComputePublicIp: amlComputePublicIp
    mlAksName: 'aks-${name}-${uniqueSuffix}'
    vmSizeParam: amlComputeDefaultVmSize
  }
  dependsOn: [
    keyvault
    containerRegistry
    applicationInsights
    storage
  ]
}

resource kv 'Microsoft.KeyVault/vaults@2022-11-01' existing= {
  name: keyvault.outputs.keyvaultName
  scope: resourceGroup()
}

// Note: you are invited to change sql admin login and password in your enviroment
module sql 'resources/sql.bicep' = {
  name: 'sqlsrvsa-${name}-${uniqueSuffix}-deployment'
  params: {
    location: location
    sqlServerName: 'sql-${name}-${uniqueSuffix}'
    administratorLogin: 'sasqladmin'
    administratorLoginPassword: kv.getSecret('sqlpassword')
    tags: tags
    sqlDBName: 'sqldbsa-${name}-${uniqueSuffix}'
    allowAzureIPs: true
    enableSqlDefender: false
    connectionType: 'Default'
  }
  dependsOn: [
    azuremlWorkspace
  ]
}
