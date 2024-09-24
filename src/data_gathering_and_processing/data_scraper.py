"""
data_scraper.py .py
~~~~~~~~~~~~~~~~~~
This module contains utility functions used to load, extract, transform data needed for the project.

Functions
---------
lookback_window:
    Calculates n days in the past from today and returns the given datetime in a string format.
pull_list_of_available_stocks:
    Get updated stock information for a list of exchanges and ETFs.
pull_stock_price_history:
    Downloads historical stock data from Yahoo Finance.
"""

import pandas as pd
import numpy as np
import os
import datetime as dt
import yfinance as yf
import sys

# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)

# Monkey patch paths to see other parts of the Condor package.
sys.path.append("..")  

from typing import List, Tuple, Union, Optional

from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
from src.data_gathering_and_processing.data_preprocessing import (
    interpolate_stock_prices,
    process_missing_dates
)

def lookback_window(n: int) -> str:
    """
    Calculates n days in the past from today and returns the given datetime in a string format.

    Parameters
    ----------
    n : int
        Number of days to look back. Must be a positive integer.

    Returns
    -------
    str
        A string representing the date n days in the past from today, formatted as 'YYYY-MM-DD'.

    Raises
    ------
    ValueError
        If n is not a positive integer.

    Examples
    --------
    >>> lookback_window(7)
    '2023-03-20'

    >>> lookback_window(14)
    '2023-03-13'
    """
    # Checks data type - raises value errro if not an integer
    if n <= 0:
        raise ValueError("n must be a positive integer")

    # Calculates n days in the past from today
    date_n_days_ago = dt.now() - dt.timedelta(days=n)

    # Returns the given datetime in a string format
    return date_n_days_ago.strftime("%Y-%m-%d")


def pull_list_of_available_stocks(
    exchanges: list[str] = ["Q", "N", "P", "S", "V", "Z"], is_etf: bool = False
) -> pd.DataFrame:
    """
    Get updated stock information for a list of exchanges and ETFs.

    Parameters
    ----------
        exchanges: list[str] , default = ['Q', 'N', 'P', 'S', 'V', 'Z']
        A list of strings representing the exchanges to include.
            Valid options are 'Q', 'N', 'P', 'S', 'V', and 'Z'.
        is_etf: bool, default = False
            A boolean indicating whether to include only ETFs or not.

    Returns
    -------
        pd.Dataframe
            A Pandas DataFrame containing updated information for the selected
            exchanges and ETFs. The DataFrame has columns 'symbol', 'cqs_symbol',
            'nasdaq_symbol', 'security_name', 'market_category', 'listing_exchange',
            and 'is_etf'.
    """
    # Get a list of all the stocks on the selected exchanges
    stocks_data = get_nasdaq_symbols()

    # Select information needed and cast into a dataframe
    df = pd.DataFrame(
        {
            "symbol": list(stocks_data.index.to_series()),
            "cqs_symbol": stocks_data["CQS Symbol"],
            "nasdaq_symbol": stocks_data["NASDAQ Symbol"],
            "security_name": stocks_data["Security Name"],
            "market_category": stocks_data["Market Category"],
            "listing_exchange": stocks_data["Listing Exchange"],
            "is_etf": stocks_data["ETF"],
        }
    ).reset_index(drop=True)

    # Make sure the list is returned with stocks in the correct list of exchanges that are either ETFs or not
    df = df[df["listing_exchange"].isin(exchanges)]
    df = df[df["is_etf"] == is_etf]

    return df



def pull_stock_price_history(
        ticker: str, 
        start_date: Optional[Union[str, dt.datetime]] = None, 
        end_date: Union[str, dt.datetime] = None, 
        lookback_window: Optional[int] = None,
        interpolate_missing_dates: bool = True, 
        interpolate_missing_vals: bool = True,
        stock_columns=['Open', 'High', 'Low', 'Close', 'Volume']
        ) -> pd.DataFrame:
    """
    Downloads historical stock data from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol.
    start_date : str or datetime, optional, default = None
        The start date for historical data in the format 'YYYY-MM-DD' or a datetime object.
    end_date : str or datetime, default = None
        The end date for historical data in the format 'YYYY-MM-DD' or a datetime object.
    lookback_window : int, optional, default = None
        The number of days to look back from the end date. If the end date is not provided, the today's date is used.
        If both the start date and the lookback window are not provided, a lookback window of 100 days is used.
    interpolate_missing_dates : bool, default = True
        Whether to interpolate missing dates in the stock data.
    interpolate_missing_vals : bool, default = True
        Whether to interpolate missing values in the stock data.
    stock_columns : list[str], default = ['Open', 'High', 'Low', 'Close', 'Volume']
        A list of strings representing the stock columns to include in the returned DataFrame.
    Returns
    -------
    stock_data : pd.DataFrame
        A pandas DataFrame containing the historical stock data.
    Examples
    --------
    >>> stock_data = pull_stock_data('AAPL', start_date='2022-01-01', end_date='2022-01-10')
    >>> print(stock_data)
    """

    # Convert end_date to string format if datetime object
    if isinstance(end_date, dt.datetime):
        end_date = end_date.strftime('%Y-%m-%d')
    if end_date is None:
        end_date = dt.datetime.today().strftime('%Y-%m-%d')

    # Check if the end date is in the past
    if end_date > dt.datetime.today().strftime('%Y-%m-%d'):
        raise ValueError("End date must be in the past")

    # Compute start_date based on lookback_window if start_date is not provided
    if start_date is None and lookback_window is None:
        lookback_window = 100
    if start_date is None:
        if not isinstance(lookback_window, int) or lookback_window <= 0:
            raise ValueError("Lookback window must be a positive integer")
        start_date = (dt.datetime.strptime(end_date, '%Y-%m-%d') - dt.timedelta(days=lookback_window)).strftime('%Y-%m-%d')

    # Check if the start date is in the past and convert to string format if datetime object
    if isinstance(start_date, dt.datetime):
        start_date = start_date.strftime('%Y-%m-%d')
    if start_date > dt.datetime.today().strftime('%Y-%m-%d'):
        raise ValueError("Start date must be in the past")

    # Check if the start date is before the end date
    if start_date > end_date:
        raise ValueError("Start date must be before end date")
    
    # Download the stock data by ticker symbol
    stock = yf.Ticker(ticker)
    stock_data = stock.history(start=start_date, end=end_date)

    # Interpolate missing dates if interpolate_missing_dates is True
    if interpolate_missing_dates:
        original_dates = stock_data.index
        stock_data = process_missing_dates(stock_data)
        stock_data.loc[~stock_data.index.isin(original_dates), 'interpolated_data'] = True

    # Iterate through stock columns and interpolate missing values if interpolate_missing_vals is True
    if interpolate_missing_vals:
        for column in stock_columns:
            if stock_data[column].dtype == "float64":
                original_values = stock_data[column].copy()
                stock_data[column] = interpolate_stock_prices(stock_data[column])
                stock_data.loc[stock_data[column] != original_values, 'interpolated_data'] = True

    return stock_data

