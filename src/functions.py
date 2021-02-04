#!/usr/bin/env python
# coding: utf-8


import os
import time
import yaml
import sqlite3
import datetime
import investpy
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pandas_datareader.data as web
import pmdarima as pm

from statsmodels.tsa.arima_model import ARIMA


#Load Configuration
with open('./config/config.yaml') as file:
    config = yaml.safe_load(file)

    
# Set Random Seed
ID = config['settings']['random_seed_ID']
np.random.seed(ID)



def use_api(api):

    return df1



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



def process_data(display_eda, univariate, tech_disruptor=False):

    #Scope Relevant Data
    td = pd.Timestamp(round(datetime.datetime.now().timestamp(), 0), unit='s')
    end = td.replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - pd.tseries.offsets.BusinessDay(n=181)
    
    end = end.date().strftime('%d/%m/%Y')
    start = start.date().strftime('%d/%m/%Y')
    pred_df = pd.DataFrame()
    
    
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
        
        try:
            
            #Use Investing.com thru Investpy
            df = investpy.get_stock_historical_data(stock=symbol, country=country, from_date=start, to_date=end)
            df1 = df.dropna().reset_index(drop=True)
            pass
        
        except:
            
            #Use Yahoo Finance
            try:
                df = web.DataReader(symbol, 'yahoo', start=start, end=end)
                df1 = pd.DataFrame(df)
                #print(df1)
                pass
                
            except:
                print("SSQR: Symbol Not Available or Public Website Down or Blocked.")
            
    else:
        
        df1 = use_api(api)
        
    
    #Univariate Exploration
    if (univariate):
        
        small_gain = config['settings']['max_size_of_small_gain_or_loss']
        test_size = config['settings']['test_size']
        
        max_number_of_lags = config['settings']['max_number_of_lags']
        max_moving_average_window = config['settings']['max_ma_term']
        frequency = config['settings']['frequency']

        fit = pd.DataFrame()    
        fit[target] = df1[target].shift(-1)
        #print(df1)
        
        fit['Returns'] = np.log(fit[target]/fit[target].shift(1))
        fit['Outcome'] = pd.cut(x=fit['Returns'], bins=[fit['Returns'].min(), -(small_gain), 0, small_gain, fit['Returns'].max()], 
                           labels=['big loss', 'small loss', 'small gain', 'big gain'])
        
        #Dataframe For Visualization
        for i in range(max_number_of_lags):
            if(i == 0):
                fit['X0'] = df1[target]
            else:
                column_name = 'X' + str(i)
                fit[column_name] = df1[target].shift(i)
        
        fit1 = fit.dropna().reset_index(drop=True)
        fit_y = fit1[[target, 'Returns', 'Outcome']]
        fit_x = fit1.drop([target, 'Returns', 'Outcome'], axis=1)
        fit_bins = fit['Outcome']
        
        #Train-Test Split
        train_returns = fit_y['Returns'].head(int(len(fit_y) * (1 - test_size))) 
        test_returns = fit_y['Returns'].tail(int(len(fit_y) * test_size))
        
        #Call Baseline
        baseline_model = baseline_r_model(train_returns, max_number_of_lags, frequency, max_moving_average_window)

        
        #Display 
        if (display_eda):
        
            print(baseline_model.summary())
            print(" ")
            print(" ")
            print(fit1)
        
        else:

            print(" ")
        
        
    else:
        #Multivariate
        print(" ")

   
    return fit_x, fit_y, fit_bins



#Box-Jenkins Method, 1970
def baseline_r_model(series, p, m, q):
    
    optimized_model = pm.auto_arima(series, start_p=1, start_q=1, test='adf', max_p=p, max_q=q, m=m, d=None, seasonal=False, start_P=0, D=0, 
    trace=False, error_action='ignore', suppress_warnings=True, stepwise=True)
      
    return optimized_model




