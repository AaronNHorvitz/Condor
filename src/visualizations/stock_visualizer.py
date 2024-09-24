"""
stock_visualizer.py
~~~~~~~~~~~~~~~~~~
This module contains utility functions used to visualize condor data.

Class
---------
StockVisualizer:
    A class for visualizing historical stock price data.
"""
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from typing import List, Tuple, Union, Optional

sys.path.append("..")  # monkey patch paths to see other parts of the Condor package.

from data_gathering_and_processing.data_scraper import pull_stock_price_history


class StockVisualizer:

    """
    A class for visualizing historical stock price data.

    Parameters
    ----------
    ticker_symbol : str
        The stock ticker symbol.
    start_date : str
        The start date of the historical data in the format "YYYY-MM-DD".
    end_date : str
        The end date of the historical data in the format "YYYY-MM-DD".
    price_type : str, optional, default = 'close'
        The type of price to plot. Valid options are "open", "close", "high", and "low".

    Attributes
    ----------
    ticker_symbol : str
        The stock ticker symbol.
    start_date : str
        The start date of the historical data in the format "YYYY-MM-DD".
    end_date : str
        The end date of the historical data in the format "YYYY-MM-DD".
    price_type : str
        The type of price to plot.
    stock_data : pd.DataFrame
        The historical stock data for the specified stock ticker and date range.

    Methods
    -------
    plot_prices()
        Plots the historical stock prices for the specified stock ticker and date range.
    get_price_plot_ax() -> plt.Axes
        Returns an Axes object with the historical stock prices plotted.
    """

    def __init__(
        self,
        ticker_symbol: str,
        start_date: str,
        end_date: str,
        price_type: str = "close",
    ):
        """
        Initializes a new StockVisualizer object.

        Parameters
        ----------
        ticker_symbol : str
            The stock ticker symbol.
        start_date : str
            The start date of the historical data in the format "YYYY-MM-DD".
        end_date : str
            The end date of the historical data in the format "YYYY-MM-DD".
        price_type : str, optional
            The type of price to plot. Valid options are "open", "close", "high", and "low".
            Defaults to "close".
        """
        self.ticker_symbol = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date
        self.price_type = price_type
        self.stock_data = pull_stock_price_history(ticker_symbol, start_date, end_date)

    def plot_prices(self):
        """
        Plots the historical stock prices for the specified stock ticker and date range.
        """
        # Plot the prices using Matplotlib
        ax = self._init_plot()
        ax.scatter(
            self.stock_data.index,
            self.stock_data[self.price_type],
            facecolors="none",
            edgecolors="black",
            linewidth=1,
            s=35,
            label=f"{self.price_type.capitalize()} Prices",
        )

        plt.legend(loc=2, fontsize=18)
        plt.show()

    def get_price_plot_ax(self) -> plt.Axes:
        """
        Returns an Axes object with the historical stock prices plotted.

        Returns
        -------
        ax : plt.Axes
            The Axes object with the historical stock prices plotted.
        """
        # Plot the prices using Matplotlib and return the Axes object
        ax = self._init_plot()
        ax.plot(
            self.stock_data.index,
            self.stock_data[self.price_type],
            color="dodgerblue",
            linewidth=1,
            alpha=1,
            label="Actual",
        )
        plt.legend(loc=2, fontsize=18)
        return ax

    def _init_plot(self) -> Tuple[plt.Figure, plt.Axes]:
        """
        Initializes the plot with the stock prices.

        Returns
        -------
        fig : plt.Figure
            The Figure object of the plot.
        ax : plt.Axes
            The Axes object of the plot.
        """
        dates = self.stock_data.index
        prices = self.stock_data[self.price_type]

        plt.style.context("ggplot")
        fig, ax = plt.subplots(figsize=(15, 7), dpi=200)

        fmt = "${x:,.0f}"
        tick = ticker.StrMethodFormatter(fmt)
        ax.yaxis.set_major_formatter(tick)
        ax.tick_params(axis="y", labelsize=14)
        ax.tick_params(axis="x", labelsize=14)

        ax.set_title(
            f"\n{self.price_type.capitalize()} Prices for {self.ticker_symbol}\n",
            fontsize=25,
        )
        ax.set_xlabel("\nDate\n", fontsize=20)
        ax.set_ylabel(f"\n{self.price_type.capitalize()} Price\n", fontsize=20)

        ax.plot(dates, prices, color="dodgerblue", linewidth=1, alpha=1, label="Actual")

        ax.grid(which="major")

        return fig, ax
