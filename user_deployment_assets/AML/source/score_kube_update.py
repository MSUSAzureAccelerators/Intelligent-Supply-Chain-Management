import pickle 
import numpy as np
import pandas as pd
import ray
import os
import pyomo.environ as pe
import json
from datetime import datetime, timedelta
from time import sleep
import urllib.request
import pyodbc
from sqlalchemy import create_engine,text, insert, update,Table
from gluonts.dataset.common import  ListDataset
from gluonts.dataset.field_names import FieldName
from gluonts.evaluation.backtest import make_evaluation_predictions
from azureml.core import Workspace, Dataset
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.model import Model



#NOTE This model 'predictor' has to be registered before execution 
#predictorpcklpath =  Model.get_model_path('predictor')

np.random.seed(0)
#get the Azure ML workspace


#get the Azure ML workspace
def get_ws():


    subscription_id = '6a89c234-644a-42a1-a06b-433ce3030bb9'
    resource_group = 'MSUS_SA_SupplyChain'
    workspace_name = 'mlw-sa-httv3'

    tenant_id ='16b3c013-d300-468d-ac64-7eda0820b6d3'

    svc_pr_id = '65ca2d1a-85d3-4055-815e-5352e5770728' # client ID
    svc_pr_password = 'KCq8Q~uVs6miz-P~jpz0m1r3I9SZt0cxIg7KLc8a' # secret ID 
    

    print("Client ID: ",svc_pr_id)
    print("")
    print("Client Password: ",svc_pr_password)



    svc_pr = ServicePrincipalAuthentication(
        tenant_id=tenant_id,
        service_principal_id=svc_pr_id,
        service_principal_password=svc_pr_password)

    ws = Workspace.get(name=workspace_name,
                    subscription_id=subscription_id,
                    resource_group=resource_group,auth= svc_pr)

    return ws


#Database related funtions

# Get the backened database engine
def get_engine():
    
    # get the workspace in order to access the KeyVault


    ws = get_ws()
    
    #get the default KeyVault and acess the secrets
    # note: you need to set these secrets ahead of time 
    # as described in the documentation. Use secure
    #names for secrets, below is just an examples for clarity
    
    keyvault = ws.get_default_keyvault()
    user_value = keyvault.get_secret(name="sqlserverusername")
    pass_value = keyvault.get_secret(name="sqlpassword")
    db_value = keyvault.get_secret(name="sqldatabase")
    server = keyvault.get_secret(name="sqlserver")
    
    #example of connecting to SQL  Server db using pyodbc
    # Notes: make sure the packages are installed both in the the Azure ML environmnet
    # and Ray cluster as described in the documentaion
    quoted = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER='
                                +server+';DATABASE='+db_value+';UID='+user_value+';PWD='+ pass_value)
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
    print("CONNECTED TO THE DB SUCCESSFULY")
    
    return engine



# Quick overview of this function, it picks up the new datasets and puts in the format that you can generate the new demand forecast and
# the input format for the optimization function

def create_ensemble_test_ds(sales_data,item_to_class):

    ## create variables
    start = sales_data.Date.min()
    end = sales_data.Date.max()

    # create ensemble
    ensemble = []

    for item in set(sales_data.Item): 
        for location in set(sales_data.Location):
            sales = sales_data[(sales_data.Item == item) & (sales_data.Location == location)].Sales.values
            if len(sales): 
                scale = max(abs(sales))
                ensemble.append(
                    {
                        "class": item_to_class[item],
                        "item": item,
                        "sales": sales,
                        "start": start,
                        "end": end,
                        "total": sum(sales),
                        "scale": scale,
                        "location": location,
                        "sales_scaled": sales / scale,
                    }
                )
    ensemble = sorted(ensemble, key=lambda k: k["total"], reverse=True)
    # create test ds 
    static_cats = [(e["class"].strip(), e["item"].strip(), e["location"].strip()) for e in ensemble]
    test_target_values = np.array([np.array(e["sales_scaled"]) for e in ensemble])
    item_to_index = {item: idx for idx, item in enumerate(set([sc[0] for sc in static_cats]))}
    item_class_to_index = {item: idx for idx, item in enumerate(set([sc[1] for sc in static_cats]))}
    location_to_index = {loc: idx for idx, loc in enumerate(set([sc[2] for sc in static_cats]))}

    test_ds = ListDataset([
        {
            FieldName.TARGET: target,
            FieldName.START: start,
            FieldName.FEAT_STATIC_CAT: [
                item_to_index[sc_item], 
                item_class_to_index[sc_item_class], 
                location_to_index[sc_location]
            ],
        }
        for target, (sc_item, sc_item_class, sc_location) in zip(test_target_values, static_cats)
    ], freq="D")

    return ensemble, test_ds 

def generate_forecasts(dataset, predictor, num_samples):
        
        forecast_it, _ = make_evaluation_predictions(dataset=dataset, predictor=predictor, num_samples=num_samples)
        forecasts = [f for f in forecast_it]

        return forecasts

def get_params(location):

    engine = get_engine()

    sql = text('''Select class, item, Inventory_Capacity,	Max_Quantity,	Holding_Cost, Order_Cost,	Lead_Time,	
    Backlog_Cost,	Max_Backlogged,	Initial_Inventory, location from [dbo].[sc_params_table] where Location =:l
    '''
    )

    item_result = engine.execute(sql,l=location)

    item_params_list = []

    for item in item_result:
        temp_dict = {}
        temp_dict= {'class':item[0],
        'item':item[1],
        'Inventory_Capacity':int(float(item[2])),
        'Max_Quantity':int(float(item[3])),
        'Holding_Cost':int(float(item[4])),
        'Order_Cost':int(float(item[5])),
        'Lead_Time':int(float(item[6])),
        'Backlog_Cost':int(float(item[7])),
        'Max_Backlogged':int(float(item[8])),
        'Initial_Inventory':int(float(item[9])),
        'Location':item[10]
        }
        item_params_list.append(temp_dict)
    
    return item_params_list

    
def subset_sales_data(subset_sales_data_location,params):

    df_list = []
    items = []
    item_class=[]
    for param in params:

        items_ = param['item']
        item_class_= param['class'] 
        

        extract_df = subset_sales_data_location[    (subset_sales_data_location['Item'] == items_) &  (subset_sales_data_location['Item_Class'] == item_class_)]
        df_list.append(extract_df)
        items.append(items_)
        item_class.append(item_class_)

    sub_sales_data = pd.concat(df_list)
    item_to_class = {items[i]: item_class[i] for i in range(len(items))}

    subset_params = []

    for key in item_to_class: 

                for param in params:
        
                    items_ = param['item']
                    item_class_= param['class'] 

                    if (items_ == key) & (item_class_ == item_to_class[key]):
                          subset_params.append(param)
        
    return sub_sales_data, item_to_class, subset_params

#Save interval results
def save_res_interval(results_int_df,param,input_location):
    print("Inside function")
    res_temp_inv = []
    res_temp_rep = []
    res_temp_back = []
    res_temp_reor = []

    no_samples = 1

    for ii in range(0,no_samples):

            temp_col_inv =  results_int_df['Inventory_Level'][ii]
            temp_col_rep =  results_int_df['Replenish_Index'][ii]
            temp_col_back =  results_int_df['Backlog_Level'][ii]
            temp_col_reor =  results_int_df['Reorder_Index'][ii]
            
            
            
            res_temp_inv.extend(temp_col_inv)
            res_temp_rep.extend(temp_col_rep)
            res_temp_back.extend(temp_col_back)
            res_temp_reor.extend(temp_col_reor)


            
    res_temp = pd.DataFrame()

    res_temp['Item'] = [param['item'] for i in range(0,len(temp_col_inv))]
    res_temp['Class'] = [param['class'] for i in range(0,len(temp_col_inv))]
    res_temp['Location'] = [input_location for i in range(0,len(temp_col_inv))]
    res_temp['Inventory_Level'] = res_temp_inv
    res_temp['Replenish_Index'] = res_temp_rep
    res_temp['Backlog_Level'] = res_temp_back
    res_temp['Reorder_Index'] = res_temp_reor
    res_temp['timestamp'] =  results_int_df['timestamp'][ii]



    return res_temp



#@ray.remote(num_cpus=1)
def persist_results(result_df_full,demand_pd,result_df_parameters):

    
    # Convert the string values to number

    result_df_full = result_df_full.rename(columns={"timestamp": "Sim_Time"}, errors="raise")
    result_df_full['Sim_Time'] = result_df_full['Sim_Time'].apply(lambda x: x.strftime('%Y-%m-%d %I:%M:%S'))
    result_df_full['Q'] = result_df_full['Q'].str[0]
    result_df_full['R'] = result_df_full['R'].str[0]

    

    start_date = "2021-10-10" 
    end_date = "2022-02-08"


    start_date= datetime.strptime(start_date,'%Y-%m-%d')
    end_date = start_date+ timedelta(days=np.int(len(result_df_full)/len(result_df_parameters))-1)


    month_list = [month for month in pd.period_range(start=start_date, end=end_date, freq='D')] * len(result_df_parameters) 
    result_df_full['result_id'] = month_list 
    
    result_df_full['Demand'] = pd.concat([demand_pd] * len(result_df_parameters), ignore_index=True)

    engine = get_engine()
    try:
            result_df_full.astype(str).to_sql('sc_results_table_full', if_exists='append', schema='dbo', con = engine,index=False)
            print("persist Results successfully to the DB")
    except pyodbc.Error as err: 
            raise err
    
@ray.remote(num_returns=7)
def run_optimization(demand, sim_duration, invCap, maxQ,orderCost,holdCost,leadTime,backLogCost,maxBackLogged,initInv):

    #Create model
    invCap = 1000
    maxQ =  1000
    orderCost = 500
    holdCost =  2 
    leadTime =  10 
    backLogCost =  10 
    maxBackLogged = 1000

    model = pe.ConcreteModel(name='MIP_QR')
    #Define sets
    model.t = pe.Set(initialize=range(1, sim_duration))
    model.H = pe.Set(initialize=[0,maxQ])

    
    #Define parameters
    model.demand = pe.Param(model.t,initialize=demand,domain=pe.NonNegativeReals)
    model.initInv = pe.Param(model.t,domain=pe.NonNegativeReals,mutable=True)
    model.initInv[1].value = 500

    ## Define variables
    # Integer Variables
    model.inventory = pe.Var(model.t,bounds=(0,invCap), domain=pe.NonNegativeIntegers)
    model.backlogged = pe.Var(model.t,bounds=(0,maxBackLogged),domain=pe.NonNegativeIntegers)
    model.replenish = pe.Var(model.t,  bounds=(0,maxQ),domain=pe.NonNegativeIntegers)
    model.Q = pe.Var(within=model.H,bounds=(0,maxQ))
    model.Q.domain=pe.NonNegativeIntegers
    model.R = pe.Var(within=model.H,bounds=(0,maxQ))
    model.R.domain=pe.NonNegativeIntegers
 

    # Binary Variables
    model.xcompl = pe.Var(model.t, within=pe.Binary, initialize=0)
    model.reorder = pe.Var(model.t, within=pe.Binary,initialize=0)
    model.below = pe.Var(model.t, within=pe.Binary,initialize=0)


    def inv_bal(model, t):
                if t == 1:
                    return (
                        model.inventory[t] - model.backlogged[t] - model.replenish[t]
                        == - model.demand[t] + model.initInv[t]
                    )
                
                return (
                    model.inventory[t] - model.inventory[t-1] - model.backlogged[t] + model.backlogged[t-1] - model.replenish[t] == - model.demand[t]

                )


    model.inv_balance_c = pe.Constraint(model.t, rule=inv_bal)

    # 2b only one of these variables can be non-zero
    model.inv_backlog_excl_c1 = pe.Constraint(model.t, rule=lambda model, 
                                            t: model.inventory[t] <= invCap * model.xcompl[t])

    model.inv_backlog_excl_c2 = pe.Constraint(
                model.t,
                rule=lambda model, t: model.backlogged[t]
                <= maxBackLogged * (1 - model.xcompl[t])
            )

    # 3. detect low inventory
    model.low_inv_c1 = pe.Constraint(
                model.t,
                rule=lambda model, t: model.inventory[t]
                <= model.R+ invCap * (1 - model.below[t])
            )


    model.low_inv_c2 = pe.Constraint(
                model.t,
                rule=lambda model, t: model.inventory[t]
                >= model.R+ 1 - (invCap + 1) * model.below[t]
            )


    # 4. reorder event detection
    def order_event_c1(model, t):
        if t == 1:
                return model.reorder[t] <= 1
                
        return model.reorder[t] <= 1 - model.below[t - 1]

    model.order_event_c1 = pe.Constraint(model.t, rule=order_event_c1)


    def order_event_c3(model, t):
                if t == 1:
                    
                    return model.reorder[t] -  model.below[t] >= 0 
                
                return model.below[t] - model.below[t - 1] + model.reorder[t] >= 0

    model.order_event_c3 = pe.Constraint(model.t, rule=order_event_c3)

    model.order_event_c2 = pe.Constraint(
                model.t, rule=lambda model, t: model.reorder[t] <= model.below[t]
            )

    # 5. inventory replenishment takes place after an order was placed and when the lead time passed.
    def repl_c1(model, t):
                if t <= leadTime:
                    return model.replenish[t] <= 0
                
                return model.replenish[t] <= maxQ * model.reorder[t - leadTime]

    model.repl_c1 = pe.Constraint(model.t, rule=repl_c1)


    def repl_c3(model, t):
        
                if t <= leadTime:
                
                    return model.replenish[t] - model.Q >= - maxQ
                
                return model.replenish[t] - model.Q >= - maxQ * (1 - model.reorder[t - leadTime])

            
    model.repl_c3 = pe.Constraint(model.t, rule=repl_c3)

    model.repl_c2 = pe.Constraint(
                model.t, rule=lambda model, t: model.replenish[t] <= model.Q
            )

    model.q_c = pe.Constraint(model.t, rule=lambda model,t: model.Q <= maxQ)


    model.r_c = pe.Constraint(model.t, rule=lambda model, t: model.R <= invCap)
        

    model.inv_c = pe.Constraint(
                model.t, rule=lambda model, t: model.inventory[t] <= invCap
            )


    model.backlog_c = pe.Constraint(
                model.t, rule=lambda model, t: model.backlogged[t] <= maxBackLogged
            )

    model.repl_c = pe.Constraint(
                model.t, rule=lambda model, t: model.replenish[t] <= maxQ
            )

    #Set the objective function
    def objective_rule_1(model):
        
        return sum(orderCost * model.reorder[t] + holdCost * model.inventory[t] + backLogCost * model.backlogged[t] for t in model.t)


    model.cost = pe.Objective(rule=objective_rule_1, sense=pe.minimize)



    opt = pe.SolverFactory("cplex_direct")
    results = opt.solve(model, tee = False)
        
    inv_list = []
    back_list = []
    replenish_list = []
    reorder_list = []
    q_list = []
    r_list = []
   
    for i in model.inventory:
            inv_list.append(model.inventory[i].value)
    for i in model.backlogged:
        back_list.append(model.backlogged[i].value)
    for i in model.replenish:
            replenish_list.append(model.replenish[i].value)
    for i in model.reorder:
            reorder_list.append(model.reorder[i].value)
    for i in model.Q:
            q_list.append(model.Q[i].value)
    for i in model.R:
            r_list.append(model.R[i].value)

    return inv_list, reorder_list, replenish_list, back_list, q_list,r_list,model.cost()

  
def init():
    
    global sales_data, predictor, training_dataset, rayclusterip


    rayclusterip="10.0.237.243"

    training_dataset = 'training_sales_data_2'

    ws = get_ws()
    dataset = Dataset.get_by_name(ws, name='training_sales_data_2', version='latest')
    sales_data = dataset.to_pandas_dataframe() 

    
    print("##### Loaded sales data #####")
    

    absolute_path = os.path.dirname('2.AKS_Deployment_Notebook.ipynb')
    relative_path = "downloads/supply-chain-forecast-model/"
    full_path = os.path.join(absolute_path, relative_path)
    
    #predictor = pickle.load(open(full_path+'predictor.pkl', 'rb'))

    predictor = pickle.load(open(os.getcwd()+'/source/downloads/supply-chain-forecast-model/predictor.pkl', 'rb'))
  
    


    if ray.is_initialized() == False:
        print("Ray is not up!! We are starting it up right with the correct address")
        ray.init(address="ray://" + rayclusterip + ":10001")  ############################### DO this for deployment (head ip)

    else:
        ray.shutdown()
        print("We are shutting Ray down.")
        print("Now we get Ray back up.")
        ray.init(address="ray://"+ rayclusterip + ":10001") ############################### DO this for deployment (head ip)

def optimization(forecasts,ensemble,subset_params,sim_duration,input_location):
    
    
    items = []
    item_class=[]
    items_location =[]
    
    result_df_parameters = []
    result_df_interval = []

    for param in subset_params:
        print(param)

        inventory_results = []
        replenish_results = []
        reorder_results = []
        backlog_results = []
        Q_results = []
        R_results = []
        cost_results =[]

        #TODO : CHECK THIS with Giulia why this is static versus for i in range(0,len(ensemble)):
        for i in range(0,1): 
            samples = ensemble[i]
            #demand_forecast = forecasts[i].samples.mean(axis=0) * samples["scale"]
            demand_forecast = forecasts[i].samples.mean(axis=0) * 100 ##TODO: check the scale factor so that it's reasonable based on the MIP model formulation/values
            
            rounded = [np.round(x) for x in demand_forecast]
            demand = {k:rounded[k] for k in range(1, sim_duration)}

            inventory_levels,reorder_levels, replenish_level, backlog_levels, Q,R, optimal_cost = run_optimization.remote(demand, sim_duration,param['Inventory_Capacity'],
            param['Max_Quantity'],param['Holding_Cost'],param['Order_Cost'],param['Lead_Time'],param['Backlog_Cost'],param['Max_Backlogged'],param['Initial_Inventory'])



            inventory_results.append(inventory_levels)
            reorder_results.append(reorder_levels)
            replenish_results.append(replenish_level)
            backlog_results.append(backlog_levels)
            R_results.append(R) 
            Q_results.append(Q)
            cost_results.append(optimal_cost)  


        
        
        run_time = datetime.now()
        result_dict_parameters_ = {'Item':param['item'],'Class':param['class'], 'Location': input_location, 
                       'Q':ray.get(Q_results), 'R':ray.get(R_results),  'Optimal_Cost': ray.get(cost_results), 'timestamp':run_time}                       

        results_df = pd.DataFrame.from_dict(result_dict_parameters_)
        result_df_parameters.append(results_df)       
            
        
        result_dict_interval_ = {'Item':param['item'],'Class':param['class'], 'Location': input_location, 
                   'Inventory_Level':ray.get(inventory_results),
                   'Replenish_Index':ray.get(replenish_results),
                    'Backlog_Level':ray.get(backlog_results),
                   'Reorder_Index':ray.get(reorder_results),'timestamp':run_time}                  
        results_int_df = pd.DataFrame.from_dict(result_dict_interval_)
        #TODO
        saved_results_with_intervals_df = save_res_interval(results_int_df,param,input_location)
        result_df_interval.append(saved_results_with_intervals_df)


    result_df_interval_pd = pd.concat(result_df_interval)
    result_df_parameters_pd = pd.concat(result_df_parameters)
   
    result_df_full= result_df_interval_pd.merge(result_df_parameters_pd, on=['Item','Class','Location','timestamp'])

    # COMMENT THIS LINE IF YOU WANT TO RUN LOCAL
    #persist_results.remote(result_df_full,demand_pd,result_df_interval,result_df_parameters)
    demand_table_pd = pd.Series(demand).to_frame('Demand')

    persist_results(result_df_full,demand_table_pd,result_df_parameters)
    
    
    print("               ")
    print("The simulation is over")


import json
def run(Inputs):

    init()
    input_location= json.loads(Inputs)['Inputs']['Location']
    params = get_params(input_location)

    samples = 20
    sim_duration = 21

    sales_data_loc = sales_data[sales_data['Location']== input_location]
    sub_sales_data,item_to_class,subset_params = subset_sales_data(sales_data_loc,params)
    print("    ")
    print("These are the items/classes combinations extracted and that we are going to analyze per the location selected above ", input_location )
    print("    ")
    print(item_to_class)

    predictor = pickle.load(open(os.getcwd()+'/source/downloads/supply-chain-forecast-model/predictor.pkl', 'rb'))
    ensemble,test_ds = create_ensemble_test_ds(sub_sales_data,item_to_class)
    forecasts = generate_forecasts(test_ds, predictor, num_samples=samples)

    print("    ")

    
    try:
        result = optimization(forecasts,ensemble,subset_params,sim_duration,input_location)
        response = json.dumps(result, indent=4, sort_keys=False, default=str)
        return "Optimization done! \nResult: \n\n" + response
    except Exception as err:
        print(err)
        return "Error occurred in optimization"
    else:
        print("Nothing wrong in optimization")

