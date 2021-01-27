# %%
import os
import yaml
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
        print("Sell Side Quantative Research Bot (SSQR)")
        print("Next Business Day Outlook, 0.0.1")
        features, target, bins = process_data(dashboard_required, univariate)
    
    return features, target, bins


# %%



# %%
def process_data(display_charts, univariate, tech_disruptor=False):

    country = config['configuration']['default_country_of_exchange']
    symbol = config['configuration']['default_stock_symbol']
    target = config['configuration']['default_stock_price']

    return fit_x, fit_y, fit_bins


