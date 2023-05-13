# Solution Deployment
Organizations have different policies and processes in place which lead them to opt for a manual or automated deployment strategy.
We provide 2 different options to deploy the architecture and resources needed to run the solution.

Both options will help you deploying the following resources:
- Azure Key Vault
- Azure Storage (Standard LRS)
- Azure Container Registry
- Azure Application Insights
- Azure Machine Learning (with Azure Kubernetes Services Inferred Compute Instance - Default: Standard_F8s_v2)
- Azure SQL Database (with random credentials)

## Deploy the architecture through Azure Portal by using pre-configured Azure Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fgallogiulia%2FMSUS_SC_Accelerator%2Fmain%2Fdeployment%2Fazuredeploy.json)


### AML workspace

The files included in this project are an adaptation of [azure quickstart templates](https://github.com/Azure/azure-quickstart-templates/tree/master/quickstarts/microsoft.machinelearningservices/machine-learning-end-to-end-secure)

This screenshot below shows you the resources that will be deployed by the Azure Bicep template. Once you are in the Azure Portal, modify the parameters accordingly with your desired information.

![](assets/images/azure-deployment.png)


### Next Steps: Configure the Azure Resources deployed by the Bicep Template in your Subscription

The next steps you will have to take consist of setting up the Azure Resources that have been deployed into your subscription. Refer to the guide [here](user_deployment_assets\README.md).

Clone this repository on your local machine, so you can access it during the later stages.