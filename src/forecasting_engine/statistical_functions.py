"""
Functions
---------
neg_log_likelihood:
    Calculate the negative log-likelihood of the data given the parameters of a normal distribution.
estimate_normal_params:
    Estimate the parameters of a normal distribution using maximum likelihood estimation.
"""

import pandas as pd
import numpy as np

from typing import List, Tuple, Union, Optional
from scipy.optimize import minimize
from scipy.stats import norm
import ruptures as rpt


def neg_log_likelihood(params: tuple[float, float], y_array: np.array) -> float:
    """
    Calculate the negative log-likelihood of the data given the parameters of a normal distribution.

    Parameters
    ----------
    params : array-like
        An array containing the values of the mean and standard deviation parameters of a normal distribution.
    y_array : array-like
        An array of data.

    Returns
    -------
    nll : float
        The value of the negative log-likelihood.

    Examples
    --------
    >>> params = [2.3, 0.88]
    >>> data = [1.2, 2.3, 3.4]
    >>> nll = neg_log_likelihood(params,data)
    >>> print(f"Negative log-likelihood: {nll:.2f}")
    Negative log-likelihood: 1.56
    """
    mu, sigma = params
    nll = -np.sum(norm.logpdf(y_array, mu, sigma))
    return nll


def estimate_normal_params(y_series: pd.Series) -> tuple[float, float]:
    """
    Estimate the parameters of a normal distribution using Maximum Likelihood Estimation (MLE).

    Parameters
    ----------
    y_series : pandas Series
        A pandas Series that may contain missing values (represented by np.nan) or zeros.
    log_transorm: bool, default = True
        True to log transform the series
    Returns
    -------
    mu_estimated : float
        The estimated value of the mean parameter.
    sigma_estimated : float
        The estimated value of the standard deviation parameter.
    References
    ----------
    Nelder, J A, and R Mead. 1965. A Simplex Method for Function Minimization. The Computer Journal 7: 308-13.

    Examples
    --------
    >>> data = [1.2, np.nan, 2.3, 3.4, np.nan]
    >>> mu_estimated,sigma_estimated = estimate_normal_params(data)
    >>> print(f"Estimated mu: {mu_estimated:.2f}")
    Estimated mu: 2.30
    >>> print(f"Estimated sigma: {sigma_estimated:.2f}")
    Estimated sigma: 0.88
    """

    # Create a copy of the input Series to avoid modifying it
    y_series = y_series.copy()

    # Remove missing values and zeros before passing the series to the neg_log_likelihood function
    y_series = y_series[y_series.notna() & (y_series != 0)]

    # Define initial guesses for the parameters
    mu_guess = np.mean(y_series)
    sigma_guess = np.std(y_series)

    # Minimize the negative log-likelihood
    result = minimize(
        lambda params: neg_log_likelihood(params=params, y_array=y_series.values),
        x0=[mu_guess, sigma_guess],
        method="Nelder-Mead",
    )

    mu_estimated, sigma_estimated = result.x

    return mu_estimated, sigma_estimated


def level_shifts(
    y_series: Union[List[float], np.ndarray, pd.Series],
    model: str = "rbf",
    min_size: int = 1,
    jump: int = 10,
    pen: float = 2,
) -> Tuple[List[int], List[float]]:
    """
    Detect level shifts in a given time series using the PELT algorithm.

    Parameters
    ----------
    y_series : list, numpy.ndarray, pandas.Series
        Input time series data.
    model : str, optional
        Model to be used in PELT algorithm. Defaults to "rbf".
    min_size : int, optional
        Minimum size parameter in PELT algorithm. Defaults to 1.
    jump : int, optional
        Jump size parameter in PELT algorithm. Defaults to 10.
    pen : float, optional
        Penalty value parameter in PELT algorithm. Defaults to 2.

    Returns
    -------
    tuple
        A tuple containing a list of level shift indices and a list of corresponding values.

    Raises
    ------
    TypeError
        If y_series is not a list, numpy array, or pandas Series.
    ValueError
        If y_series is empty.
    Examples
    --------
    >>> time_series_data = pd.Series([1, 1, 1, 1, 1, 5, 5, 5, 5, 5])
    >>> level_shifts(time_series_data)
    ([5], [5.0])
    """

    if isinstance(y_series, (list, np.ndarray)):
        signal = np.array(y_series)
    elif isinstance(y_series, pd.Series):
        signal = y_series.values
    else:
        raise TypeError("y_series must be a list, numpy array, or pandas Series.")

    if signal.size == 0:
        raise ValueError("y_series must not be empty.")

    algo = rpt.Pelt(model=model, min_size=min_size, jump=jump).fit(signal)
    result = algo.predict(pen=pen)

    level_shift_indices = [i for i in result if i < len(signal)]
    level_shift_values = [signal[i] for i in level_shift_indices]

    return level_shift_indices, level_shift_values
