"""
financial_data.py
~~~~~~~~~~~~~~~~~~
This module contains utility functions used to load, extract, transform. and store financial data.

Functions
---------

"""

# Create an ETL that downlaods all the stock data into pandas dataframes in a Data folder, until a better solution can be resolved.

import pandas as pd
import numpy as np
import yfinance as yf

import os
import sys
