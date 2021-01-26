# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
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
def univariate_eda(dashboard=False):

    # What is AI?
    if (dashboard == False):
        features, target, bins = process_data(False)

        return None

    else:
        
        if (config['settings']['tech_disruptor'] == True):
            features, target, bins = process_data(False)

        else:

            print(" ")
            print(" ")
            print("Sell Side Quantative Research Bot (SSQR)")
            print("Next Business Day Outlook, 0.0.1")
            print(" ")
            print(" ")
            features, target, bins = process_data(True)

        return features, target, bins


# %%
def process_data(display=True, univariate=True):

    symbol = config['configuration']['default_stock_symbol']
    country = config['configuration']['default_country_of_exchange']
    target = config['configuration']['default_stock_price']

    return fit_x, fit_y, fit_bins