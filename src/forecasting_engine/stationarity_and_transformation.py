"""
Functions
---------
adf_test:
    Performs an Augmented Dickey-Fuller (ADF) unit root test for stationarity.
make_stationary:
    Makes a time series stationary by differencing and returns the number of differencing required to achieve stationarity.
transform_target:
    Transforms a target variable by optionally applying a natural logarithm transformation.
transform_predictors:
    Transforms predictor variables in a DataFrame by applying log transformation and/or differencing.
determine_optimal_degree:
    Determines the optimal degree for a polynomial transformation using cross-validation.   
generate_transfer_function:
    Generates a numpy.poly1d object representing a transfer function with the given optimal degree to use as input for the 'trend'
    parameter in statsmodels.tsa.arima.model.ARIMA
"""


import pandas as pd
import numpy as np

from typing import List, Tuple, Union, Optional
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
from statsmodels.tsa.stattools import adfuller


def adf_test(y_series: pd.Series, critical_val: float = 0.05) -> bool:
    """
    Performs an Augmented Dickey-Fuller (ADF) unit root test for stationarity.

    Parameters
    ----------
    y_series : pd.Series
        A pandas Series containing the time series data to be tested for stationarity.
    critical_val : float, default=0.5
        Critical value for the test statistic. Usually set at 0.1, 0.5, or 0.10 for the 1%, 5%, and 10% levels
        respectively.

    Returns
    -------
    bool
        A boolean value indicating whether the time series is stationary or not based on the ADF test result.

    Examples
    --------
    >>> dates = pd.date_range('2022-01-01', '2022-01-10')
    >>> data = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    >>> series = pd.Series(data=data, index=dates)
    >>> result = adf_test(series)
    >>> print(result)
    """

    result = adfuller(y_series)
    p_value = result[1]

    return p_value < critical_val


def make_stationary(
    y_series: pd.Series, max_diff: int = 2
) -> Tuple[pd.Series, Optional[int]]:
    """
    Makes a time series stationary by differencing and returns the number of differencing required to achieve stationarity.

    Parameters
    ----------
    y_series : pd.Series
        A pandas Series containing the time series data to be made stationary.
    max_diff : int, optional, default=2
        The maximum number of times to difference the time series data.

    Returns
    -------
    tuple(pd.Series, int)
        A tuple containing:
            - The resulting differenced time series data if it was made stationary or a copy of original input if it could not be made stationary.
            - The number of times that the time series was differenced.

    Examples
    --------
     >>> dates = pd.date_range('2022-01-01', '2022-01-10')
     >>> data = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
     >>> series = pd.Series(data=data, index=dates)
     >>> result = make_stationary(series)
     >>> print(result)
    """

    diff_series = y_series.copy()
    is_stationary = adf_test(diff_series)

    i = 0
    while not is_stationary and i < max_diff:
        diff_series = diff_series.diff().dropna()
        i += 1
        is_stationary = adf_test(diff_series)

    if not is_stationary:
        return (y_series, 0)

    return (diff_series, i)


def transform_target(
    y_series: pd.Series, log_transform: bool = False, difference: int = 0
) -> np.ndarray:
    """
    Transforms a target variable by optionally applying a natural logarithm transformation
    and/or differencing the data.

    Parameters
    ----------
    y_series : pd.Series
        The input Series containing the target variable to transform.
    log_transform : bool, optional
        Whether to apply a natural logarithm transformation log(x+1) to the data (default is False).
    difference : int, optional, default=0
        The number of differencing iterations to apply to the data.

    Returns
    -------
    np.ndarray
        A new NumPy array containing the transformed target variable.

    Examples
    --------
    >>> y_series = pd.Series(np.random.randn(100))
    >>> y_transformed = transform_target(y_series)

    # Apply log transform log(x+1) and first-order differencing
    >>> y_transformed = transform_target(y_series, log_transform=True, difference=1)

    # Apply second-order differencing only
    >>> y_transformed = transform_target(y_series, difference=2)
    """

    # Check input types
    if not isinstance(y_series, pd.Series):
        raise TypeError(f"y_series must be a pandas Series, but got {type(y_series)}")
    if not np.issubdtype(y_series.dtype, np.number):
        raise TypeError(f"y_series must contain only numeric data")

    if log_transform:
        y_series = np.log1p(y_series)

    for _ in range(difference):
        y_series = y_series.diff().dropna()

    return y_series.to_numpy()


def transform_predictors(
    X_df: pd.DataFrame, log_transform: bool = False, difference: int = 0
) -> np.ndarray:
    """
    Transforms predictor variables in a DataFrame by applying log transformation and/or differencing.

    Parameters
    ----------
    X_df : pd.DataFrame
        The input DataFrame containing the predictor variables to transform.
    log_transform : bool, optional, default = False
        Whether to apply a natural logarithm transformation log(x+1) to the data.
    difference : int, optional, default = 0
        The number of times to apply first-order differencing to the data.

    Returns
    -------
    np.ndarray
        The transformed predictor variables.
    """

    # Make a copy of X
    X_transformed = X_df.copy()

    # Apply log transformation if specified
    if log_transform:
        X_transformed = np.log1p(X_transformed)

    # Apply differencing if specified
    for _ in range(difference):
        X_transformed = X_transformed.diff().dropna()

    return X_transformed.values


def determine_optimal_degree(
    X_df: pd.DataFrame,
    y_array: np.ndarray,
    max_degree: int = 5,
    cv: int = 5,
    log_transform: bool = False,
    difference: int = 0,
) -> int:
    """
    Determines the optimal degree for a polynomial transformation using cross-validation.

    Parameters
    ----------
    X_df : pd.DataFrame
        The input DataFrame containing the predictor variables to transform.
    y_array : np.ndarray
        The target values corresponding to X.
    max_degree : int, optional, default = 5
        The maximum degree of polynomial transformation to consider.
    cv : int, optional, default = 5
        The number of folds in cross-validation.
    log_transform : bool, optional, default = False
        Whether to apply a natural logarithm transformation to the data.
    difference : int, optional, default = 0
        The number of times to apply first-order differencing to the data.

    Returns
    -------
    int
        The optimal degree for a polynomial transformation.

    """

    # Transform predictor variables
    X_transformed = transform_predictors(
        X_df, log_transform=log_transform, difference=difference
    )

    # Initialize variables to store the best degree and score
    best_degree = 0
    best_score = float("-inf")

    # Iterate over degrees from 1 to max_degree
    for degree in range(1, max_degree + 1):
        # Create a pipeline with a polynomial transformation and linear regression
        model = make_pipeline(PolynomialFeatures(degree), LinearRegression())

        # Compute the cross-validated score for this degree
        scores = cross_val_score(model, X_transformed, y_array, cv=cv)
        mean_score = scores.mean()

        # Update the best degree and score if necessary
        if mean_score > best_score:
            best_degree = degree
            best_score = mean_score

    return best_degree


def generate_transfer_function(
    X_df: pd.DataFrame,
    y_array: np.ndarray,
    degree: int,
    log_transform: bool = False,
    difference: int = 0,
) -> np.poly1d:
    """
    Generates a numpy.poly1d object representing a transfer function with the given optimal degree to use as input for the 'trend'
    parameter in statsmodels.tsa.arima.model.ARIMA

    Parameters
    ----------
    X_df : pd.DataFrame
        The input DataFrame containing the predictor variables to transform.
    y_array : np.ndarray
        The target variable.
    degree : int
        The degree of the polynomial transfer function to generate.
    log_transform : bool, optional
        Whether to apply a natural logarithm transformation to the data (default is False).
    difference : int, optional
        The number of times to apply first-order differencing to the data (default is 0).

    Returns
    -------
    np.poly1d
        A numpy.poly1d object representing the transfer function.

    Notes
    -----
    The iterable defining a polynomial in numpy.ply1d, where [1,1,0,1] would denote a + bt + ct^3 is the 'trend' parameter used by the 'statsmodels.tsa.arima.model.ARIMA model'.
    The 'exog' parameter in the 'statsmodels.tsa.arima.model.ARIMA' model is used to specify an array of exogenous regressors to include in the model.

    These variables are external to the time series and may impact the model's behavior. The transformed variables provided by the 'transform_predictors' function are used as input
    for the 'exog' parameter. The inclusion of the predictor variables in the ARIMA model will enable the use of the transfer function to generate forecasts.

    An important destinction needs to be made from using the transfer functions predictions as the exog paramter. The coefficients from the generate_transfer_function function
    represent a polynomial transfer function that models the relationship between the predictor variables and the target variable. These coefficients can be used to generate
    predictions for the target variable based on the predictor variables. However, these predictions would not consider any autoregressive or moving average components that may
    be present in your time series data. So to train an ARIMA model and use it to conduct a forecast, the transformed predictor variables from the transform_predictors function
    need to be used as input for the exog parameter.
    """

    # Transform predictor variables
    X_transformed = transform_predictors(
        X_df, log_transform=log_transform, difference=difference
    )

    # Fit a polynomial regression model with the given degree
    model = make_pipeline(PolynomialFeatures(degree), LinearRegression())
    model.fit(X_transformed, y_array)

    # Extract the coefficients of the fitted polynomial
    coefficients = model.named_steps["linearregression"].coef_

    # Create and return a numpy.poly1d object with the extracted coefficients
    return np.poly1d(coefficients[::-1])
