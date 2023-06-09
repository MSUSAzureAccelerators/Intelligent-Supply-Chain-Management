## Deploy the architecture through Azure Portal by using pre-configured Azure Deployment

> **Warning**
> This template also deploys an Azure Compute Instance with a default size (Standard_F8s_v2), a region (East US) and node count (min 0, max 5) inside the Azure Machine Learning Workspace. Make sure that your Subscription and the quotas allow for this type of compute. If not, you will have to click on "Edit Template" and "Edit Parameters", prior to submitting the deployment. 

> **Note**
> Estimated time to complete the steps is between 12 and 15 minutes. The longest phase is the Deployment to Azure.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMSUSAzureAccelerators%2FIntelligent-Supply-Chain-Management%2Fmain%2Fdeployment%2Fazuredeploy.json)


>  **Note**
>  Clone this repository on your local machine, so you can access it during the later stages.


The files included in this project are an adaptation of [azure quickstart templates](https://github.com/Azure/azure-quickstart-templates/tree/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure)


### Next Steps: Configure the Azure Resources deployed by the Bicep Template in your Subscription

The next steps you will have to take consist of setting up the Azure Resources that have been deployed into your subscription. Refer to the guide [here](user_deployment_assets/README.md).
