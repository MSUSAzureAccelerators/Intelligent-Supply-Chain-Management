# Azure Machine Learning Configuration Guide

> **Note**
> Estimated time to complete the steps ~ 40 minutes

In this guide, you will perform the following actions:

1) Create a _conda_ virtual environment called *supplychainray377* and register it into Azure Machine Learning.
2) Connect to your AKS instance from Azure Machine Learning studio.
3) Deploy the simulation code file (score.py) on a Kubernetes pod, running the conda environment created on step 1. 

> **Note** Now is the time to upload the copy of this github repository on your AML workspace. 

## Step 1: Create a Conda virtual environment

The conda virtual environment that we are going to create and register in Azure Machine Learning contains the same python libraries that are used to run the score.py file on your local machine, in Jupyter, Visual Studio Code or wherever you run and test your code. The virtual environment is necessary for the AKS pod to run the containerized version of your simulation code and not fail. 

Please follow these steps:

1) Upload this github repository or alternatively clone this repository in your Azure Machine Learning workspace. 
2) Using the Azure Compute Instance that we provided you during the Resource group deployment phase, go inside the folder source, and you will see two notebooks. 
3) Run the first notebook called [1.RegisterAMLEnvironment.ipynb].

Once the process is completed, you should see the newly registered conda environment in your AML studio:

![](../../assets/images/Conda.png)

## Step 2: Connect to your AKS instance from AML and deploy the simulation code on a Kubernetes Pod. 

The last step is for you to run the [2.AKS_Deployment_Notebook.ipynb](Deploy\AML\AKS_Deployment_Notebook.ipynb) notebook. Once you are done running the last cell of the notebook, you will see something similar to these messages below on your terminal. The Keywords to look for are "Ready" and "Healthy". 


![](../../assets/images/DeploymentSuccess.png)

You can also follow the deployment process and check the status of your online endpoint from the Azure Portal.

![](../../assets/images/endpoint.png)

Click on the name of your online endpoint to see the details about the deployment

![](../../assets/images/AMLHealthy.png)


> **Note** 
> Remember to save the API URL key from your endpoint deployment, which will be necessary for launching your inventory simulation from the Power App.

Next, you are going to setup your Power App to connect to your Ray Cluster and your Azure Resources. Follow the guide [here](../PowerApp/README.md)

