![image](https://user-images.githubusercontent.com/21693360/236896617-57b9c503-9ac7-4ecf-9862-cb3728f222c2.png)

# Supply Chain Management Accelerator

Created to provide a customer interface by using Power BI and PowerApps from which users can launch simulations and determine the parameters of the simulation and data, access results. 

The Supply Chain Management Accelerator helps inventory managers to analyze their products portfolio, inventory systems quickly and proactively, using a practical, scalable, and manageable solution.

By leveraging the capabilities of the Supply Chain Management Accelerator, businesses and supply chain managers can overcome these challenges and drive operational excellence, improved customer satisfaction, and increased profitability.

For more information about potential customer scenarios and architecture references, please see the [customer pitch deck](WIP) and the [AAC article](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/analytics/optimize-inventory-forecast-demand) . 

# Challenges

Many businesses face significant challenges when their supply chain management systems do not leverage data science and machine learning. These challenges include:

- Inaccurate demand forecasting leading to overstocking or stockouts.
- Inefficient inventory management resulting in increased carrying costs and capital tied up in excess stock.
- Poor visibility into supply chain operations, hindering timely decision-making.
- Inability to adapt to changing market dynamics and customer demands.
- Inefficient production planning and scheduling, leading to production delays and increased costs.
- Lack of real-time insights into supplier performance, affecting supplier relationship management.
- Ineffective risk management, making businesses vulnerable to disruptions and supply chain bottlenecks.


# Benefits

The Supply Chain Management Accelerator is a powerful tool that addresses these challenges by utilizing machine learning, distributed computing, and deep learning forecasts to transform data. It leverages the capabilities of the Ray.io framework to enable users to:

- More accurately predict demand and optimize inventory management policies.
- Run numerous distributed simulations to evaluate different scenarios and make informed decisions.
- Gain actionable insights into supply chain operations and performance.
- Enhance production planning and scheduling for improved efficiency.
- Identify and mitigate supply chain risks proactively.
- Optimize supplier selection and performance management.
- Improve overall supply chain visibility and responsiveness.

# Architecture

![image](https://github.com/MSUSAzureAccelerators/Intelligent-Supply-Chain-Management/blob/07eeee94574e0a10045b6c8bb96088338a519bf7/assets/images/Picture1.png)


# Accelerator Solution Overview

![image](https://github.com/MSUSAzureAccelerators/Intelligent-Supply-Chain-Management/blob/a123b155f0c6123778fd1f8aee800298cebd4254/assets/images/Picture2.png)

The Intelligent Supply Chain Management Accelerator is practical, scalable, and manageable—and built on Azure Machine Learning and the Microsoft Power Platform. The data flow is as follows:

- Azure Data Factory ingests related data into Azure Data Lake Storage. The sources of this data can be enterprise resource planning (ERP) systems, SAP, and Azure SQL. Additional sources might include weather and economic data.
- Data Lake Storage stores raw data for further processing.
- Mapping data flows in Azure Data Factory produces curated data and stores it in a relational format in an Azure SQL database. Additionally, in this use case, the SQL database stores intermediate results, other run information, and simulation metrics. Alternatively, Azure Machine Learning can read the data directly from the Data Lake service.
- Use Azure Machine Learning to train the model by using data in Azure SQL Database and deploy the model and service to Kubernetes.
- Install the Ray framework on the same Kubernetes cluster to parallelize the execution of the scoring script during inferencing. Each execution runs the demand-forecasting module for specified locations and products over a given forecast period. The forecasting results are read by the optimization module, which calculates the optimal inventory levels. Finally, the results are stored in Azure SQL Database.
- Power Apps hosts a user interface for business users and analysts to collect parametric information, such as service level, product, and location. Users also use Power Apps to submit the collected parameters and to launch executions of the deployed machine learning module that is hosted in Kubernetes clusters.
- Power BI ingests data from Azure SQL Database and allows users to analyze results and perform sensitive analysis. All Power BI dashboards are integrated into Power Apps to have a unified UI for calling the API, reading results, and performing downstream analysis.

## Dashboard Examples
Power Apps
![image](https://github.com/MSUSAzureAccelerators/Intelligent-Supply-Chain-Management/blob/07eeee94574e0a10045b6c8bb96088338a519bf7/assets/images/Picture3.png)
Power BI
![image](https://github.com/MSUSAzureAccelerators/Intelligent-Supply-Chain-Management/blob/07eeee94574e0a10045b6c8bb96088338a519bf7/assets/images/Picture4.png)

## Prerequisites
To use this accelerator, you will need access to an [Azure subscription](https://azure.microsoft.com/en-us/free/), a Power Apps and a Power BI license. While not required, a prior understanding of Azure Machine Learning, Azure Kubernetes, Azure SQL Database, Docker, Time Series Forecasting, Power Apps and Power BI will be helpful.

For additional training and support, please see:

- [Azure Machine Learning](https://azure.microsoft.com/en-us/products/machine-learning/#product-overview)
- [Azure Kubernetes](https://azure.microsoft.com/en-us/products/kubernetes-service/)
- [Azure SQL](https://azure.microsoft.com/en-us/products/azure-sql/)
- [Power Apps](https://powerapps.microsoft.com/en-us/)
- [Docker](https://www.docker.com/)
- [Power BI](https://azure.microsoft.com/en-us/products/power-bi/)
 

## Deploy the Accelerator to Azure

Go to the [Deployment Guide](Deploy.md) to deploy the Azure Resources to your Azure subscription.


------

## License
Copyright (c) Microsoft Corporation

All rights reserved.

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the ""Software""), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the Microsoft Open Source Code of Conduct. For more information see the Code of Conduct FAQ or contact opencode@microsoft.com with any additional questions or comments.

Trademarks
This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft trademarks or logos is subject to and must follow Microsoft's Trademark & Brand Guidelines. Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship. Any use of third-party trademarks or logos are subject to those third-party's policies.
