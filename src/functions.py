#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time
import yaml
import sqlite3
import datetime
import investpy
import numpy as np
import pandas as pd


# In[2]:


#Load Configuration
with open('./config/config.yaml') as file:
    config = yaml.safe_load(file)


# In[3]:


# Set Random Seed
ID = config['settings']['random_seed_ID']
np.random.seed(ID)


# In[4]:


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


# In[5]:


def process_data(display_charts, univariate, tech_disruptor=False):

    #Scope Relevant Data
    td = pd.Timestamp(round(datetime.datetime.now().timestamp(), 0), unit='s')
    end = td.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - pd.tseries.offsets.BusinessDay(n=181)
    
    end = end.date().strftime('%d/%m/%Y')
    start = start.date().strftime('%d/%m/%Y')
    
    
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

        
    print(" ")
    print(" ")
    print("Data Observation Period: {}".format(symbol))
    print("Start: " + str(start))
    print("End: " + str(end))
    print(" ")
    print(" ")
    

    #Get Data
    if (api == 0):

        df = investpy.get_stock_historical_data(stock=symbol, country=country, from_date=start, to_date=end)
        df1 = df.dropna().reset_index(drop=True)

    else:
        
        df1 = use_api(api)
        
    
    #Univariate Exploration
    if (univariate):
        
        number_of_lags = config['settings']['number_of_lags_univariate']
        small_gain = config['settings']['max_size_of_small_gain_or_loss']
        
        fit['Y'] = df1[target].shift(-1)
        fit['YR'] = np.log(fit['Y']/fit['Y'].shit(1))
        fit['YB'] = pd.cut(x=fit['YR'], bins=[fit['YR'].min(), -(small_gain), 0, small_gain, fit['YR'].max()], 
                           labels=['big loss', 'small loss', 'small gain', 'big gain'])
        
        for i in range(number_of_lags):
            if (i == 0):
                fit['X0'] = df1[target]
            else:
                column_name = 'X' + str(number_of_lags)
                fit[column_name] = df1[target].shift(i)
                
        fit1 = fit.dropna().reset_index(drop=True)
        
        fit_y = fit1['Y']
        fix_x = fit1.drop('Y', axis=1)
        fit_bins = fit['YB']
        
        
    else:
        
        print(" ")


    #Display Charts
    if (display_charts):

        print(" ")
    
    else:

        print(" ")


    return fit_x, fit_y, fit_bins


# In[6]:


def use_api(api):

    return df1


# In[ ]:




