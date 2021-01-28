
# %%
import os
import time
import yaml
import sqlite3
import datetime
import investpy
import numpy as np
import pandas as pd


# %%
#Load Configuration
with open('./config/config.yml') as file:
    config = yaml.safe_load(file)


# %%
# Set Random Seed
ID = config['settings']['random_seed_ID']
np.random.seed(ID)


# %%
def get_eda(dashboard_required=False, univariate=True):
    
    TD = config['settings']['tech_disruptor']

    if (TD == True):
        
        features, target, bins = process_data(dashboard_required, univariate, TD)
    else:

        print(" ")
        print(" ")
        print("Sell Side Quantative Research (SSQR)")
        print("Next Business Day Outlook, 0.0.1")
        features, target, bins = process_data(dashboard_required, univariate)
    
    return features, target, bins


# %%
def process_data(display_charts, univariate, tech_disruptor=False):

    #Scope Relevant Data
    td = pd.Timestamp(round(datetime.datetime.now().Timestamp(), 0), unit='s')
    end = td.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - pd.tseries.offsets.BusinessDay(n=181)
    

    #Get Query Details
    if (tech_disruptor == False):
        
        country = config['configuration']['default_country_of_exchange']
        symbol = config['configuration']['default_stock_symbol']
        target = config['configuration']['default_stock_price']
        api = 0

    else:
        
        conn = sqlite3.connect(config['settings']['db_path'])
        query = pd.read_sql_query('SELECT * FROM [CDB-QUERY]', conn)

        country = query['country'].iloc[-1]
        symbol = query['symbol'].iloc[-1]
        target = query['target'].iloc[-1]
        api = query['api'].iloc[-1]


    #Get Data
    if (api == 0):

        df = investpy.get_stock_historical_data(stock=symbol, country=country, from_date=start, to_date=end)
        df1 = df.dropna().reset_index(drop=True)
    
    else:

        df1 = use_api(api)


    #Univariate Exploration
    if (univariate):

        print(" ")

    else:

        print(" ")


    #Display Charts
    if (display_charts):

        print(" ")
    
    else:

        print(" ")


    return fit_x, fit_y, fit_bins


# %%
def use_api(api):

    return df1


# %%



