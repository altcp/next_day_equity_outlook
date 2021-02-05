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
import pmdarima as pm
import matplotlib.pyplot as plt
import pandas_datareader.data as web

from pmdarima.arima import ndiffs
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
    obs_end = end - pd.tseries.offsets.BusinessDay(n=1)
    
    end = end.date().strftime('%d/%m/%Y')
    start = start.date().strftime('%d/%m/%Y')
    obs_end = obs_end.date().strftime('%d/%m/%Y')

    pred_df = pd.DataFrame()
    outlook_df = pd.DataFrame()
    
    
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
    print("Data Observation: {}".format(symbol))
    print("Start: " + str(start))
    print("End: " + str(obs_end))
    print(" ")
    print(" ")
    

    #Get Data
    if (api == 0):
        
        try:
            
            #Use Yahoo Finance
            df = web.DataReader(symbol, 'yahoo', start=start, end=end)
            df1 = pd.DataFrame(df)
            pass
        
        except:
            
            #Use Investing.com thru Investpy
            try:
                df = investpy.get_stock_historical_data(stock=symbol, country=country, from_date=start, to_date=end)
                df1 = df.dropna().reset_index(drop=True)
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
        max_number_of_diff = config['settings']['max_number_of_diff']
        
        frequency = config['settings']['frequency']

        fit = pd.DataFrame()    
        fit[target] = df1[target].shift(-1)
        #print(df1)
        
        fit['Log Returns'] = np.log(fit[target]/fit[target].shift(1))
        fit['Outcome'] = pd.cut(x=fit['Log Returns'], bins=[fit['Log Returns'].min(), -(small_gain), 0, small_gain, fit['Log Returns'].max()], 
                           labels=['big loss', 'small loss', 'small gain', 'big gain'])
        
        #Dataframe For Visualization
        for i in range(max_number_of_lags):
            if(i == 0):
                fit['X0'] = df1[target]
            else:
                column_name = 'X' + str(i)
                fit[column_name] = df1[target].shift(i)
        
        fit1 = fit.dropna().reset_index(drop=True)
        fit_y = fit1[[target, 'Log Returns', 'Outcome']]
        fit_x = fit1.drop([target, 'Log Returns', 'Outcome'], axis=1)
        fit_bins = fit['Outcome']
        
        #Train-Test Split
        train_returns = fit_y['Log Returns'].head(int(len(fit_y) * (1 - test_size))) 
        test_returns = fit_y['Log Returns'].tail(int(len(fit_y) * test_size))
        
        #Call Baseline
        baseline_model, pred_df['Box-Jenkins'], outlook_df['SARIMAX'] = baseline_r_model(train_returns, test_returns, max_number_of_lags, 
                                                                                          max_number_of_diff, frequency, max_moving_average_window) 
        
        #Display 
        if (display_eda):
            print(" ")
            print(" ")
            print(fit1)
            print(" ")
            print(" ")
            print(baseline_model.summary())
            print(" ")
            print(" ")
            print("Outlook (Predicted Log Returns) for: {}".format(end))
            print(" ")
            print(outlook_df)
            print(" ")
            print(" ")
        
        else:

            print(" ")
        
        
    else:
        #Multivariate
        print(" ")

   
    return fit_x, fit_y, fit_bins



#Box-Jenkins Method, 1970
def baseline_r_model(train_set, test_set, p, d, m, q):
    seasonal = config['settings']['conduct_seasonal_test']
    
    #Estimating the Difference Term - alkaline-ml.com
    kpss_test = ndiffs(train_set, alpha=0.05, test='kpss', max_d=d)
    adf_test = ndiffs(train_set, alpha=0.05, test='adf', max_d=d)
    num_of_diffs = max(kpss_test, adf_test)
    
    optimized_model = pm.auto_arima(train_set, d=num_of_diffs, start_p=0, start_q=0, start_P=0, max_p=p, max_q=q, trace=False, 
                                    seasonal=seasonal, error_action='ignore', suppress_warnings=True)    
    
    predictions = []
    outlook = []
    
    #Measure the Performance
    for new_observation in test_set:
        pred_array = optimized_model.predict(n_periods=1)
        pred_list = pred_array.tolist()[0]
        predictions.append(pred_list)
        
        optimized_model.update(new_observation)
    
    #Make the Forecast
    outlook_array = optimized_model.predict(n_periods=1)
    outlook_list = outlook_array.tolist()[0]
    outlook.append(outlook_list)
    
    return optimized_model, predictions, outlook




