## Azure SQL Deployment Guide


In this guide, you will perform the following actions:

-
-
-

### Upload the SQL bacpac file to your Azure storage account

Select the SQL bacpac file here, and upload it to a new container in your Azure storage account

### Import the supplychain SQL database to your Azure SQL db

Follow the steps in this video, on how to create a new SQL database using a baccpack file. 

> [Guide + video](https://learn.microsoft.com/en-us/azure/azure-sql/database/database-import?view=azuresql&tabs=azure-powershell)

> **Note**
> feel free to remove/delete any existing databases that you see in the Resource Group. 

### Add your IP to the Azure SQL server firewall

Once you have successfully imported the Supply Chain Azure SQL database into your SQL server, before you will be able to connect to it, you will have to add your local machine's IP to the Azure SQL server firewall, as shown in the image here below. 

![SQL Server Add IP](../../assets/images/SQL_server.png)

