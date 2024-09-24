"""
Functions
---------
smooth_lowess:
    A custom LOWESS (Locally Weighted Scatterplot Smoothing) implementation that "smooths" discrete stock price data to produce a trend. 
calculate_confidence_region:
    Calculates the confidence region around the smoothed values.
calculate_prediction_region:
    Calculates the prediction intervals around the smoothed values.   
"""

import pandas as pd
import numpy as np
import os
import sys

import statsmodels.api as sm
from scipy import stats


current_dir = os.path.abspath(os.getcwd())
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

# Get the absolute path to the parent directory
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))

# Add the parent directory to the system path
sys.path.append(parent_dir)

# Monkey patch paths to see other parts of the Condor package.
sys.path.append("..")  

from typing import List, Tuple, Union, Optional


def smooth_lowess(
    y_series: pd.Series, smoothing_window: int = 15, smoothing_iterations: int = 2
) -> pd.Series:
    """
    A custom LOWESS (Locally Weighted Scatterplot Smoothing) implementation that "smooths" discrete stock price data
    to produce a trend. It uses a continuous weighted linear least squares regression in a window as passed over the
    range of ordered stock values. The stock prices are initially log-transformed to prevent the occurrence of negative
    numbers during smoothing. Execution stops and throws a value error if the window length is greater than the series it's 
    supposed to smooth or less than 3.

    Parameters
    ----------
    y_series: pandas.Series
        Discrete price points as the input variable.
    smoothing_window: int, default = 15
        Window length used to pass through the data set as it's smoothed. It can't be less than three.
    smoothing_iterations: int, default = 2
        The number of residual-based reweightings to perform.

    Returns
    -------
    pandas.Series
        A pandas Series of LOWESS smoothed values.

    Raises
    ------
    ValueError
        If the smoothing window 'smoothing_window' is less than 3 or if it's greater than the length of the time series 'y_series'.
    ValueError
        If 'y_series' contains NaNs or zeros.
    Examples
    --------
    >>> s = pd.Series([1, 2, np.nan, 2.5, 6.6, np.nan])
    >>> result = cd.smooth_lowess(y_series=s, smoothing_window=4, smoothing_iterations=1)
    >>> print(result)
    """

    # Check input types
    if not isinstance(y_series, pd.Series):
        raise TypeError("y_series must be a pandas Series.")

    if not isinstance(smoothing_window, int):
        raise TypeError("smoothing_window must be an integer.")
    if not isinstance(smoothing_iterations, int):
        raise TypeError("smoothing_iterations must be an integer.")

    if smoothing_window < 3 or smoothing_window > len(y_series):
        raise ValueError(
            f"Error: 'smoothing_window' should be between 3 and the length of 'y_series'. "
            f"Got 'smoothing_window'={smoothing_window}, 'y_series' length={len(y_series)}."
        )

    if y_series.isnull().values.any() or (y_series == 0).any():
        raise ValueError("The series contains NaNs or zeros!")

    # Create a copy of the input Series to avoid modifying it
    y_series = y_series.copy()

    # Execute LOWESS smoother
    y_smooth = np.expm1(  # the inverse transform log(x+1)
        np.transpose(  # transpose resulting array to separate the values
            sm.nonparametric.lowess(
                endog=np.log1p(y_series),  # log (x+1) to transform prices
                exog=np.arange(len(y_series)),
                frac=smoothing_window
                / len(
                    y_series
                ),  # the fraction of the window to the length of the series
                it=smoothing_iterations,
            )
        )[1]
    )

    return pd.Series(y_smooth)


def calculate_confidence_region(
    y_series: pd.Series, y_smooth: pd.Series, alpha: Optional[float] = 0.05
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculates the confidence region around the smoothed values.

    Parameters
    ----------
    y_series : pandas.Series
        The original data values.
    y_smooth : pandas.Series
        The smoothed data values.
    alpha : float, optional, default = 0.5
        The significance level

    Returns
    -------
    lower_bound, upper_bound : tuple of pandas Series.
        The lower and upper bounds of the confidence region.
    """
    # Transform the origianl and smoothed series to a numpy array
    y_array = y_series.to_numpy()
    smoothed_data = y_smooth.to_numpy()

    # Calculates the uppper and lower bounds by taking the standard deviation of the residuals and calculates the margins.
    residuals = y_array - smoothed_data
    std_residuals = np.std(residuals)
    z = stats.norm.ppf(1 - alpha / 2)
    margin = z * std_residuals
    lower_bound = smoothed_data - margin
    upper_bound = smoothed_data + margin

    # Return the upper and lower CI
    return (pd.Series(lower_bound), pd.Series(upper_bound))


def calculate_prediction_region(
    y_series: pd.Series, y_smooth: pd.Series, alpha: Optional[float] = 0.05
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculates the prediction intervals around the smoothed values.

    Parameters
    ----------
    y_smooth : pd.Series
        The original data values.
    y_smooth : pd.Series
        The smoothed data values.
    alpha : float, optional, default = 0.5
        The significance level

    Returns
    -------
    lower_bound, upper_bound : tuple of pandas Series
        The lower and upper bounds of the prediction interval.
    """

    # Transform the origianl and smoothed series to a numpy array
    y_array = y_series.to_numpy()
    smoothed_data = y_smooth.to_numpy()

    # Calculate the residuals
    residuals = y_array - smoothed_data
    std_residuals = np.std(residuals)
    z = stats.norm.ppf(1 - alpha / 2)

    # Calculate the prediction interval using the square root of the residuals' variance
    sqrt_n = np.sqrt(1 + 1 / len(residuals))
    margin = z * std_residuals * sqrt_n
    lower_bound = smoothed_data - margin
    upper_bound = smoothed_data + margin

    # Return the upper and lower PI
    return (pd.Series(lower_bound), pd.Series(upper_bound))
