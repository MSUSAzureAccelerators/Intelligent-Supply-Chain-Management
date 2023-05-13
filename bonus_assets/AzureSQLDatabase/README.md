# How we prepopulated the Azure SQL Database  

Based on customer experiences and project deployments, we have created a simplified and generic inventory dataset. We provide you with the table information and the data types down below for your reference.  


The tables that come prepopulated inside the Azure SQL Database and that are used by the SA code are the following:

- sc_sales_data
- sc_sales_data_training
- sc_params_table 
- sc_results_table_full

Full details for the tables are provided here.

### Sales Data Table

| Table Name | Variable Name | Data Type |
| ----------- | ------------ | ----------|
| sc_sales_data | id int IDENTITY(1,1) | PRIMARY KEY|
|                | Date | datetime|
|               | Item | varchar(255)|
|                | Location |  varchar(255)|
|                | Sales | int|
|                | Item_Class | varchar(255)|

### Sales Data Training Table

| Table Name | Variable Name | Data Type |
| ----------- | ------------ | ----------|
| sc_sales_data_training | id int IDENTITY(1,1) | PRIMARY KEY|
|               | Item | varchar(255)|
|                | Location |  varchar(255)|
|                | Sales | int|
|                | Item_Class | varchar(255)|
|                | Date | datetime|


### Parameters Table

| Table Name | Variable Name | Data Type |
| ----------- | ------------ | ----------|
| sc_params_table | id int IDENTITY(1,1) | PRIMARY KEY|
|                | class | varchar(255)|
|               | item | varchar(255)|
|                | location |  varchar(255)|
| |  Inventory_Capacity |int|
||    Max_Quantity |int|
||    Holding_Cost |int|
||    Order_Cost |int|
||    Lead_Time |int|
||    Backlog_Cost | int|
||    Max_Backlogged | int|  
||    Initial_Inventory | int|


## Results Table

| Table Name | Variable Name | Data Type |
| ----------- | ------------ | ----------|
| sc_results_table_full | id int IDENTITY(1,1) | PRIMARY KEY|
|| Item | varchar(255)|
|| Class | varchar(255)|
|| Location |  varchar(255)|
|| Inventory_Level | float|
||    Replenish_Index |float|
||    Backlog_Level |float|
||    Reorder_Index | float|
||    Q |float|
||    R | float|
||    Sim_Time |datetime|
||    result_id |int|

