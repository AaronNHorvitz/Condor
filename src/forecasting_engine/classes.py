"""
Classes
-------
ForecastARIMAX: Automates the process of fitting an ARIMAX (Autoregressive Integrated Moving Average with Exogenous variables)
    model to a given time series data and exogenous variables, and then forecasting future values.

StockDataForecast:
    Generates a forecast using the ARIMAX model with specified steps and alpha level, and calculates the forecast prediction intervals. 
    It will also analyzing historical time series stock data, smoothing the trend, and forecasting future values using an ARIMAX model.
"""

import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import List, Tuple, Union, Optional
from forecasting_engine.arimax_optimization_and_forecasting import (
    generate_auto_arimax_test_params,
    auto_arimax_optimizer,
    calculate_forecast_prediction_interval,
    arimax_forecast,
)
from forecasting_engine.time_series_smoothing import (
    smooth_lowess,
    calculate_confidence_region,
    calculate_prediction_region,
)
from data_gathering_and_processing.data_scraper import pull_stock_price_history

class ForecastARIMAX:
    """
    The ForecastARIMAX class automates the process of fitting an ARIMAX (Autoregressive Integrated Moving Average with Exogenous variables)
    model to a given time series data and exogenous variables, and then forecasting future values.

    Parameters
    ----------
    y_series : pd.Series
        A pandas Series containing the properly ordered time series data.
    X_df : pd.DataFrame
        A pandas DataFrame containing exogenous regressors.
    max_p : int, default=5
        Maximum value for the autoregressive (AR) parameter p.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    max_d : int, default=2
        Maximum value for the differencing parameter d.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    max_q : int, default=5
        Maximum value for the moving average (MA) parameter q.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    d : int, optional
        Value for the differencing parameter d. If None (default), all values from 0 to max_d will be used.
    generate_seasonal_params : bool, default=False
        If True, generates and tests seasonal ARIMA parameters (P, D, Q, s) along with the regular parameters (p, d, q).
    max_P : int, default=0
        Maximum value for the seasonal autoregressive parameter P.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    max_D : int, default=0
        Maximum value for the seasonal differencing parameter D.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    max_Q : int, default=0
        Maximum value for the seasonal moving average parameter Q.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    seasonality_trend : int, optional
        The period of seasonality to use for generating seasonal parameters. Must be provided if 'generate_seasonal_params' is True.
        (Default setting ssumes no seasonality. See Recommended Parameter Settings for Different Types of Time Series)
    penalty_criteria : str, default='AIC'
        The information criterion used to select the best model. Options are 'AIC' for Akaike Information Criterion and 'BIC'
        for Bayes Information Criterion.

    Methods
    -------
    fit():
        Fits the ARIMAX model to the provided time series data and exogenous variables using the optimal parameters.

    forecast(steps: int, exog: Optional[pd.DataFrame] = None) -> np.ndarray:
        Generates a forecast for the specified number of steps using the fitted ARIMAX model. Optionally, exogenous variables can be provided for the forecast steps.

    Examples
    --------
    >>> # Assuming you have y_series and X_df as your target and predictor variables respectively
    >>> arimax_forecaster = ForecastARIMAX(y_series, X_df)
    >>> arimax_forecaster.fit()
    >>> forecast = arimax_forecaster.forecast(steps=10, exog=some_exog_data)  # Replace `some_exog_data` with your exogenous data for the forecast steps

    Recommended Parameter Settings for Different Types of Time Series
    -----------------------------------------------------------------
    Seconds Data:
        - No seasonality with seconds data: 'generate_seasonal_params' = False, 'seasonality_trend' = None, max arima_order = (4,2,4)
        - Minute seasonality with seconds data: 'generate_seasonal_params' = True, 'seasonality_trend' = 60, max arima_order = (4,2,4) max seasonal_order = (2, 1, 2)
        - Hourly seasonality wth seconds data: 'generate_seasonal_params' = True, 'seasonality_trend' = 3600, max arima_order = (24,2,24) max seasonal_order = (4, 1, 4)
        - Daily seasonality wth seconds data: 'generate_seasonal_params' = True, 'seasonality_trend' = 86400, max arima_order = (24,2,24) max seasonal_order = (4, 1, 4)
          * Note: Working with daily seasonal data at such a granular level (seconds) may not be appropriate for ARIMA modeling, as it can result in an overwhelming
            amount of data and noise.

    Minutes Data:
        - No seasonality with minutes data: 'generate_seasonal_params' = False, 'seasonality_trend' = None, max arima_order = (4,2,4)
        - Hourly seasonality with minutes data: 'generate_seasonal_params' = True, 'seasonality_trend' = 60, max arima_order = (4,2,4) max seasonal_order = (2, 1, 2)
        - Daily seasonality with minutes data: 'generate_seasonal_params' = True, 'seasonality_trend' = 1440, max arima_order = (12,2,12) max seasonal_order = (2, 1, 2)
        - Monthly seasonality with minutes data: 'generate_seasonal_params' = True, 'seasonality_trend' = 43200, max arima_order = (24,2,24) max seasonal_order = (2, 1, 2)
        - Yearly seasonality with minutes data: 'generate_seasonal_params' = True, 'seasonality_trend' = 525600, max arima_order = (24,2,12) max seasonal_order = (12, 2, 3)

    Hourly Data:
        - No seasonality with hourly data: 'generate_seasonal_params' = False, 'seasonality_trend' = None, max arima_order = (4,2,4)
        - Daily seasonality with hourly data: 'generate_seasonal_params' = True, 'seasonality_trend' = 24, max arima_order = (7,2,7) max seasonal_order = (4, 1, 4)
        - Weekly seasonality with hourly data: 'generate_seasonal_params' = True, 'seasonality_trend' = 168, max arima_order = (7,2,7) max seasonal_order = (4, 1, 4)
        - Monthly seasonality with hourly data: 'generate_seasonal_params' = True, 'seasonality_trend' = 720, max arima_order = (24,2,24) max seasonal_order = (4, 1, 4)
        - Yearly seasonality with hourly data: 'generate_seasonal_params' = True, 'seasonality_trend' = 8760, max arima_order = (24,2,24) max seasonal_order = (4, 1, 4)

    Daily Data:
        - No seasonality with daily data: 'generate_seasonal_params' = False, 'seasonality_trend' = None, max arima_order = (4,2,4)
        - Weekly seasonality with daily data: 'generate_seasonal_params' = True, 'seasonality_trend' = 7, max arima_order = (7,2,7) max seasonal_order = (2, 1, 2)
        - Monthly seasonality with daily data: 'generate_seasonal_params' = True, 'seasonality_trend' = 30, max arima_order = (12,2,12) max seasonal_order = (2, 1, 2)
        - Yearly seasonality with daily data: 'generate_seasonal_params' = True, 'seasonality_trend' = 365, max arima_order = (24,2,12) max seasonal_order = (2, 1, 2)

    Weekly Data:
        - No seasonality with weekly data: 'generate_seasonal_params' = False, 'seasonality_trend'=None, max arima_order = (4,2,4)
        - Montly seasonality with weekly data: 'generate_seasonal_params' = True, 'seasonality_trend'= 4, max arima_order = (4,2,4) max seasonal_order = (2, 1, 2)
        - Yearly seasonality with weekly data: 'generate_seasonal_params' = True, 'seasonality_trend'= 52, max arima_order(12,2,12) max seasonal_order = (4, 1, 4)

    Yearly Data:
        - No seasonality with yearly data: 'generate_seasonal_params'= False, 'seasonality_trend'= None, max arima_order = (4,2,4)
        - Five-year seasonality with yearly data: 'generate_seasonal_params'= True, 'seasonality_trend'= 5, max arima_order = (12,2,12) max seasonal_order = (2, 1, 2)
        - Decade seasonality with yearly data: 'generate_seasonal_params'= True, 'seasonality_trend'= 10, max arima_order = (12,2,12) max seasonal_order = (5, 1, 5)
    """

    def __init__(
        self,
        y_series: pd.Series,
        X_df: pd.DataFrame,
        max_p: int = 5,
        max_d: int = 2,
        max_q: int = 5,
        d: Optional[int] = None,
        generate_seasonal_params: bool = False,
        max_P: int = 0,
        max_D: int = 0,
        max_Q: int = 0,
        seasonality_trend: Optional[int] = None,
        penalty_criteria: str = "AIC",
    ):
        self.y_series = y_series
        self.X_df = X_df
        self.arimax_test_params = generate_auto_arimax_test_params(
            max_p=max_p,
            max_d=max_d,
            max_q=max_q,
            d=d,
            generate_seasonal_params=generate_seasonal_params,
            max_P=max_P,
            max_D=max_D,
            max_Q=max_Q,
            seasonality_trend=seasonality_trend,
        )
        self.penalty_criteria = penalty_criteria
        self.optimal_params = None
        self.model_fit = None

    def fit(self):
        self.optimal_params = auto_arimax_optimizer(
            self.y_series,
            self.arimax_test_params,
            exog_array=self.X_df.to_numpy(),
            penalty_criteria=self.penalty_criteria,
        )

        arimax_model = sm.tsa.arima.ARIMA(
            endog=self.y_series.to_numpy(),
            exog=self.X_df.to_numpy(),
            order=self.optimal_params[:3],
            seasonal_order=self.optimal_params[3:]
            if len(self.optimal_params) > 3
            else None,
            enforce_stationarity=True,
            enforce_invertibility=True,
        )

        self.model_fit = arimax_model.fit()

    def forecast(self, steps: int, exog: Optional[pd.DataFrame] = None) -> np.ndarray:
        if self.model_fit is None:
            raise ValueError(
                "The model has not been fitted yet. Please call the 'fit' method before forecasting."
            )

        exog_array = exog.to_numpy() if exog is not None else None
        forecast = self.model_fit.forecast(steps=steps, exog=exog_array)

        return forecast


class PriceForecast:
    def __init__(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        price_type: str = "close",
        exog_data: Optional[pd.DataFrame] = None,
    ):
        """
        Initializes the PriceForecast class with the specified parameters.

        Parameters
        ----------
        ticker : str
            The stock ticker.
        start_date : str
            The start date of the historical data in the format "YYYY-MM-DD".
        end_date : str
            The end date of the historical data in the format "YYYY-MM-DD".
        price_type : str, optional, default = "close"
            The type of price to forecast. Choices are 'open', 'close', 'high', 'low', and 'volume'.
        exog_data : pd.DataFrame, optional, default = None
            The exogenous data to be used as additional predictors in the ARIMAX model.
        """
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.price_type = price_type
        self.exog_data = exog_data
        self.stock_data = pull_stock_price_history(self.ticker, self.start_date, self.end_date)

    def trends(self) -> pd.DataFrame:
        """
        Analyzes the historical stock data and calculates the smoothed values, confidence region, and prediction intervals.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the original stock prices, smoothed values, confidence region bounds, and prediction interval bounds.
        """
        y_series = self.stock_data[self.price_type]
        y_smooth = smooth_lowess(y_series)

        # Calculate the confidence region
        lower_ci, upper_ci = calculate_confidence_region(y_series, y_smooth)

        # Calculate the prediction intervals
        lower_pi, upper_pi = calculate_prediction_region(y_series, y_smooth)

        trends_df = pd.DataFrame(
            {
                "stock_price": y_series,
                "smoothed": y_smooth,
                "lower_ci": lower_ci,
                "upper_ci": upper_ci,
                "lower_pi": lower_pi,
                "upper_pi": upper_pi,
            }
        )

        return trends_df

    def forecast(
        self, steps: int, alpha: float = 0.05
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Generates a forecast using the ARIMAX model with specified steps and alpha level.

        Parameters
        ----------
        steps : int
            The number of steps to forecast.
        alpha : float, optional, default = 0.05
            The significance level for the confidence and prediction intervals.

        Returns
        -------
        forecast, lower_bound, upper_bound : tuple of pandas.Series
            The forecast, lower bound, and upper bound of the forecast prediction interval.
        """
        y_series = self.stock_data[self.price_type]
        y_smooth = smooth_lowess(y_series)

        # Find the optimal ARIMAX model parameters
        optimal_params = auto_arimax_optimizer(y_series, self.exog_data)

        # Forecast the future values
        y_forecast = arimax_forecast(y_series, self.exog_data, steps, optimal_params)

        # Calculate the forecast prediction interval
        lower_bound, upper_bound = calculate_forecast_prediction_interval(
            y_series, y_forecast, alpha
        )

        return y_forecast, lower_bound, upper_bound
