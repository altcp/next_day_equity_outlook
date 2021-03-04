#!/usr/bin/env python
# coding: utf-8


import os
import time
import yaml
import random
import sqlite3
import datetime
import investpy
import numpy as np
import pandas as pd
import seaborn as sns
import pmdarima as pm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas_datareader.data as web

from pmdarima.arima import ndiffs
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR


#Load Configuration
with open('./config/config.yaml') as file:
    config = yaml.safe_load(file)

    
# Set Random Seed
ID = config['settings']['random_seed_ID']
os.environ['PYTHONHASHSEED']=str(ID)
np.random.seed(ID)
random.seed(ID)


def use_api(api):

    return df1


def check_symbol(input_symbol):
    
    #Check Case 
    required_symbol = input_symbol.upper()
    
    return None


def get_eda(dashboard_required=False, univariate=True):
    
    TD = config['settings']['tech_disruptor']

    if (TD == True):
        predictions, outlook, outcome = process_data(dashboard_required, univariate, TD)
    else:

        print(" ")
        print(" ")
        print("Sell Side Quantative Research (SSQR)")
        print("Next Period Outlook, 0.0.1")
        predictions, outlook, outcome = process_data(dashboard_required, univariate)
    
    return predictions, outlook, outcome



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
                print("ERR. Symbol Not Available or Public Website Down or Blocked.")
            
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
        fit['Date'] = df1.index
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
        fit2 = fit1[['Date', target, 'Log Returns', 'Outcome']] 
        fit_svr = fit1.drop(['Date', 'Outcome', target], axis=1)
        #print(fit_svr)
        
        
        #Baseline Model
        train_returns = fit2['Log Returns'].head(int(len(fit2) * (1 - test_size))) 
        test_returns = fit2['Log Returns'].tail(int(len(fit2) * test_size)).reset_index(drop=True)
        baseline_model, pred_df['SARIMAX'], outlook_df['SARIMAX'] = baseline_r_model(train_returns, test_returns, 
                                                                                     max_number_of_lags, max_number_of_diff, frequency, max_moving_average_window)
        
        #SVR
        train_returns = fit_svr.head(int(len(fit_svr) * (1 - test_size))) 
        test_returns = fit_svr.tail(int(len(fit_svr) * test_size)).reset_index(drop=True)
        pred_df['SVR'], outlook_df['SVR'] = svr_r_model(train_returns, test_returns, fit_svr)
        #print(pred_df)
    
    
        #Display 
        if (display_eda):
            print(" ")
            print(" ")
            print(fit2)
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

   
    return pred_df, outlook_df, fit2



#Box-Jenkins Method, 1970
def baseline_r_model(train_set, test_set, p, d, m, q):
    seasonal = config['settings']['conduct_seasonal_test']
    
    #Estimating the Difference Term - alkaline-ml.com
    kpss_test = ndiffs(train_set, alpha=0.05, test='kpss', max_d=d)
    adf_test = ndiffs(train_set, alpha=0.05, test='adf', max_d=d)
    num_of_diffs = max(kpss_test, adf_test)
    
    optimized_model = pm.auto_arima(train_set, d=num_of_diffs, start_p=0, start_q=0, start_P=0, max_p=p, max_q=q, trace=False, 
                                    seasonal=seasonal, error_action='ignore', random_state=ID, suppress_warnings=True)    
    
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



#Support Vector Regression, 1995 
def svr_r_model(train_set, test_set, full_set):
    
    #Preprocessing
    train_y = np.asarray(train_set['Log Returns']) 
    train_x = np.asarray(train_set.loc[:, train_set.columns.difference(['Log Returns', 'X0'])])
    
    test_y = np.asarray(test_set['Log Returns']) 
    test_x = np.asarray(test_set.loc[:, test_set.columns.difference(['Log Returns', 'X0'])])
    
    full_y = np.asarray(full_set['Log Returns']) 
    full_x = np.asarray(full_set.loc[:, full_set.columns.difference(['Log Returns', 'X0'])])
    
    column_name = 'X' + str(len(test_set.columns)-3) 
    outlook_x = np.asarray(test_set.loc[:, test_set.columns.difference(['Log Returns', column_name])])

    predictions = []
    outlook = []
    
    #Measure the Performance
    pipe = Pipeline(steps=[('scaler', StandardScaler()), ('svr', SVR())])
    param_grid={
            'svr__kernel':['rbf', 'poly'],
            'svr__C': [1, 100, 1000],
            'svr__epsilon': [0.0001, 0.0005, 0.001]
        }
    
    search = GridSearchCV(pipe, param_grid, n_jobs=-2, cv=3)
    search.fit(train_x, train_y)
    predictions = search.predict(test_x)
    
    #Make the Forecast
    search.fit(full_x, full_y)
    outlook = search.predict(outlook_x)
   
    return predictions, outlook[-1]
    


