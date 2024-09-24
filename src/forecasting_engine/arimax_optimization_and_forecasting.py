"""
Functions
---------
generate_auto_arimax_test_params:
    Generates an array consisting of a combination of all possible test parameters (p,d,q) to conduct on a grid search to opimize an 
    Autoregressive Integrated Moving Average (ARIMA) model.
check_generated_arimax_params:
    Tests the given (p,d,q) test parameters using the normalized AIC or BIC value to use as a benchmark after fitting them to an Autoregressive Integrated 
    Moving Average (ARIMA) model to find the lowest value. 
optimize_arimax_params:
    Worker function to optimize ARIMA parameters for a chunk of parameter combinations.
auto_arimax_optimizer:
    Finds the optimal ARIMA model parameters (p, d, q) by testing a list of all possible parameter combinations.
arimax_forecast:
    Forecast a time series using an optimized parameters for an Autoregressive Integrated Moving Average (ARIMA) model.
calculate_forecast_prediction_interval:
    Calculates the prediction interval around the forecast values.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
import multiprocessing as mp

from itertools import product
from typing import List, Tuple, Union, Optional
from scipy import stats
from tqdm import tqdm


def generate_auto_arimax_test_params(
    max_p: int = 4,
    max_d: int = 2,
    max_q: int = 4,
    d: Optional[int] = None,
    generate_seasonal_params: bool = False,
    max_P: int = 2,
    max_D: int = 1,
    max_Q: int = 2,
    seasonality_trend: Optional[int] = None,
) -> List[Tuple[int, int, int]] or List[Tuple[int, int, int, int, int, int, int]]:
    """
    Generates an array consisting of a combination of all possible test parameters (p, d, q) and optional seasonal parameters (P, D, Q, s) to conduct on a grid search to optimize an
    Autoregressive Integrated Moving Average with Exogenous Variables (ARIMAX) model.

    Parameters
    ----------
    max_p : int, default=3
        Maximum value for the autoregressive (AR) parameter p.
    max_d : int, default=2
        Maximum value for the differencing parameter d.
    max_q : int, default=3
        Maximum value for the moving average (MA) parameter q.
    d : int, optional
        Value for the differencing parameter d. If None (default), all values from 0 to max_d will be used.
    generate_seasonal_params : bool, default=False
        Whether to generate seasonal parameters (P, D, Q, s) for the model.
    max_P : int, default=2
        Maximum value for the seasonal autoregressive (SAR) parameter P.
    max_D : int, default=2
        Maximum value for the seasonal differencing parameter D.
    max_Q : int, default=2
        Maximum value for the seasonal moving average (SMA) parameter Q.
    seasonality_trend : int, optional
        The periodicity of the seasonality component. Required when generate_seasonal_params is set to True.

    Returns
    -------
    List[Tuple[int, int, int]] or List[Tuple[int, int, int, int, int, int, int]]
        List of tuples representing all combinations of p, d, q values and optional seasonal P, D, Q, s values to test.

    Examples
    --------
    >>> generate_auto_arimax_test_params()
    [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3), ...]

    >>> generate_auto_arimax_test_params(max_p=2)
    [(0, 0, 0), (0, 0, 1), (0, 0, 2), (0, 0, 3), ...]

    >>> generate_auto_arimax_test_params(generate_seasonal_params=True, seasonality_trend=12)
    [(0, 0, 0, 0, 0, 0, 12), (0, 0, 0, 0, 0, 1, 12), ...]
    """

    # Check input types
    if generate_seasonal_params and seasonality_trend is None:
        raise ValueError(
            "You must provide 'seasonality_trend' when 'generate_seasonal_params' is True."
        )

    if d is None:
        non_seasonal_params = list(
            product(range(max_p + 1), range(max_d + 1), range(max_q + 1))
        )
    else:
        non_seasonal_params = list(product(range(max_p + 1), [d], range(max_q + 1)))

    if generate_seasonal_params:
        seasonal_params = list(
            product(
                range(max_P + 1),
                range(max_D + 1),
                range(max_Q + 1),
                [seasonality_trend],
            )
        )
        arimax_test_params = list(product(non_seasonal_params, seasonal_params))
        arimax_test_params = [
            (p, d, q, P, D, Q, s) for ((p, d, q), (P, D, Q, s)) in arimax_test_params
        ]
    else:
        arimax_test_params = non_seasonal_params

    return arimax_test_params


def check_generated_arimax_params(
    y_array: np.ndarray,
    params: Tuple[int, int, int],
    exog_array: Optional[np.ndarray] = None,
    trend_params: Optional[Union[str, Tuple]] = None,
    seasonal_params: Optional[Tuple[int, int, int, int]] = None,
    penalty_criteria: str = "AIC",
) -> Union[float, float]:
    """
    Tests the given (p, d, q) test parameters using the normalized AIC or BIC value to use as a benchmark after fitting them to an Autoregressive Integrated
    Moving Average (ARIMA) model to find the lowest value.

    Parameters
    ----------
    y_array : np.ndarray
        A numpy array containing the properly ordered time series data.
    params : tuple
        (p, d, q) values. The (p, d, q) order of the model for the autoregressive, differences, and moving average components.
    exog_array: np.ndarray, optional
        A numpy array of exogenous regressors.
    trend_params: str{'n','c','t','ct'} or iterable, optional
        Parameter controlling the deterministic trend. Can be specified as a string where 'c' indicates a constant term, 't'
        indicates a linear trend in time, and 'ct' includes both. Can also be specified as an iterable defining a polynomial,
        as in numpy.poly1d, where [1,1,0,1] would denote a + bt + ct^3. Default is 'c' for models without integration, and no
        trend for models with integration. Note that all trend terms are included in the model as exogenous regressors.
    seasonal_params: tuple, optional
        (P, D, Q, s) values. The (P, D, Q) order of the seasonal component of the model for the AR, I, and MA components. 's'
        is the periodicity (number of periods in season). Default is None (no seasonal component).
    penalty_criteria : str, default='AIC'
        Normalized BIC or AIC measure.
        'BIC' - Bayesian Information Criterion
        'AIC' - Akaike Information Criterion

    Returns
    -------
    float or np.inf
        Returns the normalized AIC or BIC value as rounded float values to 5 significant digits or an infinite value (np.inf) if
        the ARIMA model fails due to an error. A printed message accompanies the np.inf value stating that the proper penalty_criteria
        was not selected to measure the model.

    Raises
    ------
    ValueError
        If trend variables are provided without exogenous variables.
    """

    # Check input types
    if exog_array is None and trend_params is not None:
        raise ValueError(
            "You must provide exogenous variables (exog_array) with trend parameters (trend_params)."
        )

    arimax_model = sm.tsa.arima.ARIMA(
        endog=y_array,
        exog=exog_array,
        order=params,
        seasonal_order=seasonal_params,
        trend=trend_params,
        enforce_stationarity=True,
        enforce_invertibility=True,
    )

    try:
        model_fit = arimax_model.fit()
    except Exception as e:
        print(f"The params: {params} failed to fit the ARIMAX. Returning np.inf value.")
        return np.inf

    if penalty_criteria == "BIC":
        return round(model_fit.bic, 5)
    elif penalty_criteria == "AIC":
        return round(model_fit.aic, 5)
    else:
        raise ValueError(
            "Invalid penalty criteria provided. Choose either 'AIC' or 'BIC'."
        )


def optimize_arimax_params(
    params_chunk: List[Tuple[int, int, int]],
    y_array: np.ndarray,
    exog_array: Optional[np.ndarray],
    trend_params: Optional[Union[str, Tuple]],
    penalty_criteria: str,
) -> List[float]:
    """
    Worker function to optimize ARIMA parameters for a chunk of parameter combinations.

    Parameters
    ----------
    params_chunk : list of tuples
        A list of (p,d,q) tuples representing the ARIMA model parameters to test.
    y_array : np.ndarray
        A NumPy array representing the time series data.
    exog_array : np.ndarray, optional
        A numpy array containing exogenous regressors.
    trend_params : str{'n','c','t','ct'} or iterable, optional
        Parameter controlling the deterministic trend. Can be specified as a string where 'c' indicates a constant term,
        't' indicates a linear trend in time, and 'ct' includes both. Can also be specified as an iterable defining a polynomial,
         as in numpy.poly1d. Default is None.
    penalty_criteria : str
        The information criterion used to select the best model. Options are 'AIC' for Akaike Information Criterion and 'BIC'
         for Bayes Information Criterion.

    Returns
    -------
    list of floats
        A list of the information criterion scores for each tested set of ARIMA parameters in `params_chunk`.

    """
    results = []
    for params in params_chunk:
        result = check_generated_arimax_params(
            y_array,
            params=params,
            exog_array=exog_array,
            trend_params=trend_params,
            penalty_criteria=penalty_criteria,
        )
        results.append(result)
    return results


def auto_arimax_optimizer(
    y_series: pd.Series,
    arimax_test_params: List[Tuple[int, int, int]],
    exog_array: Optional[np.ndarray] = None,
    trend_params: Optional[Union[str, Tuple]] = None,
    penalty_criteria: str = "AIC",
    generate_seasonal_params: bool = False,
    seasonality_trend: Optional[str] = None,
    n_jobs: int = -1,
    max_cores: int = 8,
) -> Tuple[int, int, int]:
    """
    Finds the optimal ARIMA model parameters (p, d, q) by testing a list of all possible parameter combinations.

    Parameters
    ----------
    y_series : pd.Series
        A pandas Series containing the properly ordered time series data.
    arimax_test_params : list of tuples
        A list of (p,d,q) tuples representing the ARIMA model parameters to test.
    exog_array : np.ndarray, optional
        A numpy array containing exogenous regressors.
    trend_params : str{'n','c','t','ct'} or iterable, optional
        Parameter controlling the deterministic trend. Can be specified as a string where 'c' indicates a constant term,
        't' indicates a linear trend in time, and 'ct' includes both. Can also be specified as an iterable defining a polynomial,
         as in numpy.poly1d. Default is None.
    penalty_criteria : str, default='AIC'
        The information criterion used to select the best model. Options are 'AIC' for Akaike Information Criterion and 'BIC'
         for Bayes Information Criterion.
    generate_seasonal_params : bool, default=False
        Whether or not to generate and test seasonal parameters in addition to the (p,d,q) parameters.
    seasonality_trend : str, optional
        Optional trend parameter for seasonality. Can be specified as a string where 'c' indicates a constant term,
        't' indicates a linear trend in time, and 'ct' includes both. If None, the trend is automatically determined
        based on the data. Default is None.
    n_jobs : int, optional, default = -1
        Number of jobs to run in parallel. Default is -1, which means to use all available CPUs.
    max_cores: int, optoinal, default = 8
        The maximum number of cores to use on the processor.
    Returns
    -------
    tuple
        The optimal (p,d,q) values for the ARIMA model based on the given penalty criteria.
    """
    # Check input types
    if exog_array is None and trend_params is not None:
        raise ValueError(
            "You must provide exogenous variables (exog_array) with trend parameters (trend_params)."
        )

    # use all available cores up to the specified max_cores value
    if n_jobs < 1:
        n_jobs = min(mp.cpu_count(), max_cores)
    n_jobs = min(n_jobs, len(arimax_test_params))

    y_array = y_series.to_numpy()

    if generate_seasonal_params:
        seasonal_params = generate_seasonal_params(y_series, seasonality_trend)
        arimax_test_params = [
            (*params, *seasonal_params) for params in arimax_test_params
        ]
        print("Testing all possible (p, d, q, P, D, Q) combinations...")
    else:
        print("Testing all possible (p, d, q) combinations...")

    if n_jobs < 1:
        n_jobs = mp.cpu_count()
    n_jobs = min(n_jobs, len(arimax_test_params))

    chunks = np.array_split(arimax_test_params, n_jobs)
    pool = mp.Pool(processes=n_jobs)

    results = []
    for chunk_results in tqdm(
        pool.imap_unordered(
            optimize_arimax_params,
            [
                (chunk, y_array, exog_array, trend_params, penalty_criteria)
                for chunk in chunks
            ],
        ),
        total=n_jobs,
    ):
        results += chunk_results

    pool.close()
    pool.join()

    test_results = [result for chunk_results in results for result in chunk_results]
    min_score_index = test_results.index(min(test_results))
    optimal_params = arimax_test_params[min_score_index]

    return optimal_params


def arimax_forecast(
    y_series: Union[pd.Series, np.ndarray],
    forecast_length: int,
    arima_params: Tuple[int, int, int],
    seasonal_params: Tuple[int, int, int, int] = (0, 0, 0, 0),
    trend_params: str = "c",
    exog_array: Optional[np.ndarray] = None,
) -> pd.Series:
    """
    Forecast a time series using an ARIMA model.

    Parameters
    ----------
    y_series : Union[pd.Series, np.ndarray]
        The time series data to be forecasted.
    forecast_length : int
        The length of the forecast in days.
    arima_params : Tuple[int, int, int]
        The values for (p, d, q).
    seasonal_params : Tuple[int, int, int, int], optional
        The values for (P, D, Q, s). Default is (0, 0, 0, 0).
    trend_params : str, optional
        The trend specification. Default is 'c'.
    exog_array : np.ndarray, optional
        Exogenous variables. Default is None.

    Returns
    -------
    pd.Series
        A Pandas Series containing the forecasted values.

    Raises
    ------
    ValueError:
        If `y_series` is not a Pandas Series or a Numpy array or if `forecast_length` is not a positive integer.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> from arimax_forecast import arimax_forecast

    # Generate some example data
    >>> np.random.seed(0)
    >>> y_series = pd.Series(np.random.randn(100))

    # Forecast the next 10 values using an ARIMA(1, 0, 0) model
    >>> forecast = arimax_forecast(y_series, 10, (1, 0, 0))
    >>> print(forecast)
    """

    # Check input types
    if not isinstance(y_series, (pd.Series, np.ndarray)):
        raise ValueError("y must be either a Pandas Series or a Numpy array")

    if not isinstance(forecast_length, int) or forecast_length <= 0:
        raise ValueError("forecast_length must be a positive integer")

    y_array = y_series.to_numpy() if isinstance(y_series, pd.Series) else y_series

    model = sm.tsa.arima.ARIMA(
        endog=y_array,
        exog=exog_array,
        order=arima_params,
        seasonal_order=seasonal_params,
        trend=trend_params,
        enforce_stationarity=True,
        enforce_invertibility=True,
    )

    results = model.fit()
    forecast = results.get_forecast(steps=forecast_length)

    return forecast.predicted_mean


def calculate_forecast_prediction_interval(
    y_series: pd.Series, y_forecast: pd.Series, alpha: Optional[float] = 0.05
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculates the prediction interval around the forecast values.

    Parameters
    ----------
    y_series : pd.Series
        The residuals from the original data and smoothed values.
    y_forecast : pd.Series
        The forecast values.
    alpha : float, optional, default = 0.5
        The significance level

    Returns
    -------
    lower_bound, upper_bound : tuple of pandas.Series
        The lower and upper bounds of the forecast prediction interval.
    """

    # Transform the origianl and smoothed series to a numpy array
    y_array = y_series.to_numpy()
    forecast = y_forecast.to_numpy()

    # Calculate the residuals
    residuals = y_array[: -len(forecast)] - y_array[len(forecast) :]
    std_residuals = np.std(residuals)

    # Calculate the forecast prediction interval using the square root of the cumulative residuals' variance
    z = stats.norm.ppf(1 - alpha / 2)
    sqrt_n = np.sqrt(np.arange(1, len(forecast) + 1))
    margin = z * std_residuals * sqrt_n
    lower_bound = forecast - margin
    upper_bound = forecast + margin

    # Return the upper PI and lower PI
    return (pd.Series(lower_bound), pd.Series(upper_bound))
