// Creates a machine learning workspace, private endpoints and compute resources
// Compute resources include a GPU cluster, CPU cluster, compute instance and attached private AKS cluster

@description('Prefix for all resource names.')
param prefix string

@description('Azure region of the deployment')
param location string

@description('Tags to add to the resources')
param tags object

@description('Machine learning workspace name')
param machineLearningName string 

@description('Machine learning workspace display name')
param machineLearningFriendlyName string = machineLearningName

@description('Machine learning workspace description')
param machineLearningDescription string

@description('Name of the Azure Kubernetes services resource to create and attached to the machine learning workspace')
param mlAksName string

@description('Resource ID of the application insights resource')
param applicationInsightsId string

@description('Resource ID of the container registry resource')
param containerRegistryId string

@description('Resource ID of the key vault resource')
param keyVaultId string

@description('Resource ID of the storage account resource')
param storageAccountId string

@description('Enable public IP for Azure Machine Learning compute nodes')
param amlComputePublicIp bool = true

@description('VM size for the default compute cluster')
param vmSizeParam string

@description('Kubernetes version of the Azure Kubernetes Service cluster')
param kubernetesVersion string 
 
resource machineLearning 'Microsoft.MachineLearningServices/workspaces@2022-05-01' = {
  name: machineLearningName
  location: location
  tags: tags
  identity: {
    type: 'systemAssigned'
  }
  properties: {
    // workspace organization
    friendlyName: machineLearningFriendlyName
    description: machineLearningDescription

    // dependent resources
    applicationInsights: applicationInsightsId
    containerRegistry: containerRegistryId
    keyVault: keyVaultId
    storageAccount: storageAccountId

    imageBuildCompute: 'cluster001'
    publicNetworkAccess: 'Enabled'
  }
}

module machineLearningCompute 'machinelearningcompute.bicep' = {
  name: 'machineLearningComputes'
  scope: resourceGroup()
  params: {
    machineLearning: machineLearningName
    location: location
    aksName: mlAksName
    prefix: prefix
    tags: tags
    amlComputePublicIp: amlComputePublicIp
    vmSizeParam: vmSizeParam
    kubernetesVersion: kubernetesVersion
  }
  dependsOn: [
    machineLearning
  ]
}

output machineLearningId string = machineLearning.id
