"""
Functions
---------
process_missing_dates:
    Process the DataFrame with a date column, check for duplicate dates, find missing dates, 
    replace missing dates with correct dates, and fill in the missing data with NaN values.
interpolate_stock_prices:
    Interpolates missing values in a time series of stock prices using Maximum Likelihood Estimation (MLE).
check_nans_and_zeros:
    Checks if a pandas Series contains any NaN values or zeros.
"""


import pandas as pd
import numpy as np

from typing import List, Tuple, Union, Optional

from forecasting_engine.time_series_smoothing import smooth_lowess
from forecasting_engine.statistical_functions import estimate_normal_params
from forecasting_engine.stationarity_and_transformation import (
    make_stationary
)

def process_missing_dates(df: pd.DataFrame, date_column: str = None) -> pd.DataFrame:
    """
    Process the DataFrame with a date column, check for duplicate dates, find missing dates, 
    replace missing dates with correct dates, and fill in the missing data with NaN values.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with a date column or index in datetime64 format.
    date_column : str, optional
        The name of the date column, by default None.

    Returns
    -------
    processed_df : pd.DataFrame
        The processed DataFrame with missing dates filled and duplicate dates removed.

    Raises
    ------
    ValueError
        If duplicate dates are found in the index.
    """

    # Set the date column as the index if provided
    if date_column is not None:
        df = df.set_index(date_column)

    # Check for duplicate dates and raise a ValueError if any duplicates are found
    if df.index.duplicated().any():
        raise ValueError("Duplicate dates found in the index")
    
    # Find the min and max dates
    min_date = df.index.min()
    max_date = df.index.max()
    
    # Create a date range with daily increments
    date_range = pd.date_range(min_date, max_date, freq='D')
    
    # Reindex the DataFrame with the complete date range
    processed_df = df.reindex(date_range)
    
    # Reset the index and rename the date column
    processed_df = processed_df.reset_index().rename(columns={'index': 'date'})
    
    return processed_df

def interpolate_stock_prices(
    y_series: pd.Series, log_transform: bool = True, allow_negative_values: bool = False
) -> pd.Series:
    """
    Interpolates missing values in a time series of stock prices using Maximum Likelihood Estimation (MLE).

    This function takes in a Pandas Series representing a time series of stock prices and interpolates any missing values using MLE. The function first
    makes the series stationary by differencing it up to two times. Then it estimates the parameters of the normal distribution that best fits the
    stationary series using MLE. The missing values are then filled in with the estimated mean of this distribution.

    If `log_transform` is set to `True`, the function will apply a log transformation to the input series before making it stationary and estimating its
    parameters. This can help stabilize variance and make the data more normally distributed. After filling in the missing values, the function applies
    a LOWESS smoother to re-estimate any duplicated MLE values.

    Finally, it reverses any differencing and log transformations that were applied to return a series with interpolated values.

    Parameters
    ----------
    y_series : pd.Series
        A Pandas Series representing a time series of stock prices.
    log_transform : bool, optional, default = True
        Whether or not to apply a log transformation to the input series before making it stationary and estimating its parameters.
    allow_negative_values: bool, optional, default = False
        Whether or not to allow negative falues to the input series before making it stationary and estimating its aprameters.
    Returns
    -------
    pd.Series
        A Pandas Series with interpolated values for any missing data in `y_series`.
    Raises
    ------
    ValueError
        If negative values are present in the input series when allow_negative_values is set to False.

    Examples
    --------
    >>> y_series = pd.Series([100, np.nan, 102, 0, 0, 103, np.nan, 105, 0.0, 106, np.nan, 108, 109])
    >>> interpolated_series = interpolate_stock_prices(y_series, log_transform=True)
    >>> print(interpolated_series)
    """
    # Create a copy of the input Series to avoid modifying it
    y_series = y_series.copy()
    y_nan = y_series.copy()

    # Replace 0 values with NaN
    y_nan[y_nan == 0] = np.nan

    # Remove NaNs and zeros
    no_nan_y = y_series[(y_series != 0) & (y_series.notnull())]

    # If Log transform series
    if log_transform:
        no_nan_y = np.log1p(no_nan_y)

    # Captures any negative values if the log transform is set to False, and throws a value error.
    elif not allow_negative_values and any(x < 0 for x in no_nan_y):
        raise ValueError(
            "Input series contains negative values while allow_negative_values is set to False. Consider setting log_transform to True if the series contains negative values."
        )

    # Make the series stationary
    stationary_series, num_diff = make_stationary(y_series=no_nan_y, max_diff=2)

    # Use Maximum Likelihood Estimation (MLE) to estimate the parameters
    mu_estimated, sigma_estimated = estimate_normal_params(y_series=stationary_series)

    # Replace values in y with stationary values
    y = y_nan.where(y_nan.notna(), stationary_series)

    # Use the estimated parameters to fill in missing values with the estimated values for mu.
    series_filled = [x if not pd.isna(x) else mu_estimated for x in y]

    # Reverse differencing
    for _ in range(num_diff):
        series_filled = np.cumsum(series_filled)

    # Inverse-transform Log transform
    if log_transform:
        series_filled = np.expm1(series_filled)

    # Lowess smoothed series to re-estimate duplicated MLE values
    filled_smooth = smooth_lowess(
        y_series=pd.Series(series_filled), smoothing_window=4, smoothing_iterations=3
    )

    # Replace MLE values in NaN's place with smoothed values
    return y_nan.fillna(filled_smooth)


def check_nans_and_zeros(y_series: pd.Series) -> bool:
    """
    Checks if a pandas Series contains any NaN values or zeros.

    Parameters
    ----------
    y_series : pandas.Series
        A pandas Series to check for NaN values or zeros.

    Returns
    -------
    bool
        True if the input Series contains any NaN values or zeros, False otherwise.

    Examples
    --------
    >>> s = pd.Series([1, 2, np.nan])
    >>> result = contains_nan_or_zero(s)
    >>> print(result)
    True
    """

    # Check for NaN values or zeros in the input Series
    return y_series.isnull().any() or (y_series == 0).any()

