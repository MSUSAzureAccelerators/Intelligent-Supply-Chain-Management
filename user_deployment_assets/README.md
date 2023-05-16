# Deployment Assets and Configuration Guide

Once you have deployed the Azure Resource Group and Azure resources in your subscription, you will need to follow the guides below to complete the SA installation.

---

# Step: AKS and Ray Configuration

In this guide, you will install a few tools on your local machine to complete the installation and configuration of the SA. 
There are a few necessary requirements that you'll have to meet in order to proceed and not encounter issues.
A summary of what will happen during this step is below:

- configure your local machine to deploy a KubeRay Operator on your AKS instance
- build a custom Docker image for your KubeRay Operator

Follow the steps [here](RayCluster/README.md).


# Step: Azure SQL Database

In this guide, you will perform the following operations:

- import the Azure SQL database with pre-existing tables to your Azure SQL server instance.
- allow the server's firewall to grant access to your local machine's IP

Follow the steps [here](SQL/README.md).


# Step: AML Studio Configuration

In this guide, you will run two jupyter notebooks on your Azure Compute Instance in sequence:

- you will register a conda virtual environment to deploy an AML pod to your AKS instance
- you will deploy the score file to your AKS instance

Follow the steps [here](AML/README.md).


# Step: PowerBI Configuration

In this guide, you will configure and install the PowerBI dashboard that will allow you to visualize the results of the inventory simulation and connect to your SQL database for any other analysis. 

A summary of what will happen during this step is below:

- import the PowerBI dashboard and report to your own PowerBI tenant
- create necessary connections to your Azure SQL database
- visualize the PowerBI dashboard on your PowerBI desktop application on the web.

Follow the steps [here](PowerBI/PowerBI.md).

# Step: Power Apps Configuration

In this guide, you will configure and install the Power Apps application that will allow you to launch the inventory simulations.

A summary of what will happen during this step is below:

- create necessary connections, objects to properly configure the Power Apps application
- create a connection between Power Apps and your KubeRay Operator on the AKS configured at Step 2
- visualize the Power Apps deployment from your browser and test running simulations
 
Follow the steps [here](PowerApp/README.md).


# Bonus Content

In the folder called "bonus_assets" you will find three modules that we are making available to you:

- The module AzureSQLDatabase provides you with an explanation of how we prepopulated the SQL database and created the synthetic data provided to you. See [here](../bonus_assets/AzureSQLDatabase/README.md) for more information.

- The module ForecastModule provides you with a walkthru of the forecasting module developed for this solution accelerator. Refer to the [README.md](../bonus_assets/ForecastModel/README.md) file for more information on the module and how to reproduce it in your environment.

- The module OptimizationModel contains a description of the inventory policy algorithm developed for this solution accelerator. Refer to the [README.md](../bonus_assets/OptimizationModel/README.md) file for more information on the model. 

