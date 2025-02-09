# UNDER DEVELOPMENT

# Condor

Condor is a comprehensive research project focused on the development and implementation of various trading, forecasting, and portfolio optimization algorithms. The objective is to create a versatile trading bot capable of operating across all asset classes, while incorporating a wide range of financial information and external pricing data from relevant sources.

The ultimate goal is to create an auto trader that identifies and statistically tests market signals, with the ability to either automate trades using an API or provide daily trading suggestions.

## Key Features

- Comprehensive library for downloading and processing various types of data (financial, textual, etc.).
- Robust storage schema for efficient data management using MariaDB and Feather file format for historical stock price data and price forecasts.
- Advanced variable selection algorithms and a series of forecast engines.
- Rigorous testing and evaluation of portfolio optimization algorithms.
- Exploration of reinforcement learning algorithms for executing trades.
- SQL tables for tracking database updates, next day's opening prices, and stock ticker availability.

## Project Status

The project is currently in the development phase. As we progress, new features and improvements will be added to enhance the capabilities of the trading bot.

## Project File Structure
```bash
Condor/
├── __init__.py
│ 
├── Notebooks/
│   │ 
│   └── 001 Demonstrate Database Connection
│   
├── src/
│   │ 
│   ├── __init__.py
│   │ 
│   ├── mariadb_setup/
│   │   ├── __init__.py
│   │   │ 
│   │   ├── secure_storage.py
│   │   │   ├── (function) encrypt
│   │   │   ├── (function) decrypt
│   │   │   ├── (function) store_password
│   │   │   ├── (function) get_password
│   │   │   ├── (function) generate_password
│   │   │   ├── (class) CredentialsManager
│   │   │   └── (class) DatabaseManager
│   │   │ 
│   │   │ 
│   │   ├── mariadb_connector.py
│   │   │   └── (class) MariaDBConnector
│   │   │ 
│   │   ├── populate_condor_db_tables.py
│   │   │   ├── (function) main
│   │   │   └── (function) create_tables
│   │   │ 
│   │   ├── initialize_condor_db.py
│   │   │   └── (function) create_condor_db
│   │   │ 
│   │   ├── info_tables.py
│   │   │   └── (function) create_tables
│   │   │ 
│   │   ├── asset_price_history_tables.py
│   │   │   └── (function) create_tables   
│   │   │ 
│   │   ├── opening_spot_price_history_tables.py
│   │   │   └── (function) create_tables
│   │   │ 
│   │   ├── forecast_tables.py
│   │   │   └── (function) create_tables
│   │   │ 
│   │   ├── exogenous_series_tables.py
│   │   │   └── (function) create_tables
│   │   │ 
│   │   ├── booty_tables.py
│   │   │   └── (function) create_tables
│   │   │ 
│   │   └── db_schema.sql
│   │
│   ├── data_gathering_and_processing/
│   │   ├── __init__.py
│   │   ├── financial_data.py
│   │   ├── etl_script.py
│   │   │ 
│   │   ├── data_preprocessing.py
│   │   │   ├── (function) process_missing_dates
│   │   │   ├── (function) interpolate_stock_prices
│   │   │   └── (function) check_nans_and_zeros
│   │   │ 
│   │   ├── data_scraper.py
│   │   │   ├── (function) lookback_window
│   │   │   ├── (function) pull_list_of_availble_stocks
│   │   │   └── (function) pull_stock_price_history
│   │   │ 
│   │   └──data_writer.py
│   │ 
│   ├── forecast_engine/
│   │   ├── __init__.py
│   │   │ 
│   │   ├── statistical_functions.py
│   │   │   ├── (function) neg_log_likelihood
│   │   │   ├── (function) estimate_normal_params
│   │   │   └── (function) level_shifts
│   │   │ 
│   │   ├── time_series_smoothing.py
│   │   │   ├── (function) smooth_lowess
│   │   │   ├── (function) calculate_confidence_region
│   │   │   └── (function) calculate_prediction_region
│   │   │ 
│   │   ├── stationarity_and_transformation.py
│   │   │   ├── (function) adf_test
│   │   │   ├── (function) make_stationary
│   │   │   ├── (function) transform_target
│   │   │   ├── (function) transform_predictors
│   │   │   ├── (function) determine_optimal_degree
│   │   │   └── (function) generate_transfer_function
│   │   │ 
│   │   ├── arimax_optimization_and_forecasting.py
│   │   │   ├── (function) generate_auto_arimax_test_params
│   │   │   ├── (function) check_generated_arimax_params
│   │   │   ├── (function) optimize_arimax_params
│   │   │   ├── (function) auto_arimax_optimizer
│   │   │   ├── (function) arimax_forecast
│   │   │   └── (function) calculate_forecast_prediction_interval
│   │   │ 
│   │   ├── time_series_classification_and_forecasting.py
│   │   │ 
│   │   └── classes.py
│   │       ├── (class) ForecastARIMAX
│   │       └── (class) StockDataForecast
│   │   
│   ├── trading_engine/
│   │   ├── __init__.py
│   │   └── trading_logic.py
│   │   
│   └── visualizations/
│       ├── __init__.py
│       └── viz.py
│           └── (class) StockVisualizer
│   
├── tests/
│   ├── __init__.py
│   ├── test_data_gathering_and_processing/
│   │   ├── __init__.py
│   │   ├── test_financial_data.py
│   │   ├── test_data_scraper.py
│   │   └── test_data_writer.py
│   │   
│   ├── test_forecast_engine/
│   │   ├── __init__.py
│   │   ├── test_data_preprocessing.py
│   │   ├── test_statistical_functions.py
│   │   ├── test_time_series_smoothing.py
│   │   ├── test_stationarity_and_transformation.py
│   │   ├── test_arimax_optimization_and_forecasting.py
│   │   └── test_time_series_classification_and_forecasting.py
│   │   
│   ├── test_trading_engine/
│   │   ├── __init__.py
│   │   └── test_trading_logic.py
│   │   
│   └── test_visualizations/
│       └── __init__.py
│       └── test_viz.py
│    
├── Notebooks/
│   └── 001 Demonstrate Database Connection.ipynb
│
├── Sandbox/
│   ├── experimental_feature_1/
│   └── experimental_feature_2/
│
├── .gitignore
├── README.md
├── environment.yml
└── setup.py
```
## Getting Started

### Prerequisites

- Git
- Anaconda or Miniconda

### Clone the Repository

To get a local copy of the repository, clone it using git:

```bash
git clone https://github.com/your_username/Condor.git
```
### Setting up a Conda Environment

The __environment.yml__ file contains the necessary dependencies for the project. To set up a conda environment on your local machine, follow the instructions below for your operating system. **This could take a considerable mount of time.**:

#### **If you are not using a GPU
You will need to go into the environment.yml file and remove the line that says `tensorflow-gpu=2.11.0` and replace it with `tensorflow=2.11.0`. This will ensure that the correct version of tensorflow is installed.

#### MacOS and Linux
```bash
cd Condor
conda env create -f environment.yml
```
#### Windows
```bash
cd Condor
conda env create -f environment.yml
```
#### Activate the environment: 
```bash
conda activate condor_env
```

## Installing MariaDB and setting up the database

We use MariaDB as our primary database to store metadata and relational information about the assets, forecasts, and other relevant data. To set up MariaDB on your local machine, follow the official installation guide [here](https://mariadb.com/kb/en/getting-installing-and-upgrading-mariadb/).

Once you have MariaDB installed, you can create the necessary tables by running the `populate_condor_db_tables.py` file located in the `src/mariadb_setup/` directory. 

## Data Storage and Management
The database is structured into several schemas, designed to store and manage asset information, price forecasts, historical prices, database updates, opening prices, and exogenous time-series data.
### Database Initialization
`initialize_condor_db.py`: Creates the necessary database and schemas for the Condor database. This script should be run before running the ETL script for the first time.

### Database Architecture

```bash
└── Condor (MariaDB)/
    ├── info_tables/
    │ ├── database_updates
    │ ├── asset_info
    │ ├── exogenous_series_info
    │ └── market_closed_dates
    │
    ├── asset_price_history/
    │ └── historical_prices
    │
    └── opening_spot_prices/
    │ └── opening_spot_prices
    │
    ├── forecasts/
    │ ├── asset_price_forecasts
    │ └── exongenous_series_forecasts
    │
    ├── exogenous_series/
    │ └── exogenous_series_history
    │
    └── booty/
      ├── orders
      ├── executed_orders
      ├── account_cash_transactions
      ├── asset_holdings
      ├── dividens
      ├── stock_splits
      ├── historical_asset_balances
      └── daily_cash_summary
```

## Condor Database Schema

### `info_tables`
The following tables are used to store information about the database and its contents. The information in these tables is used to determine which data needs to be updated and which data can be used
- `database_updates`: Records each time the ETL script updates the database and provides a description of the changes made.
- `asset_info`: Contains information about each available stock ticker, including whether the ticker is new, delisted, and its date range.
- `exogenous_series_info` : Contains information about each available exogenous time-series data, including whether the series is new, and its date range.
- `market_closed_dates` : Contains a list of dates when the market was closed.

### `asset_price_history`
Stores historical asset prices directly in the MariaDB database.
- `historical_asset_prices` : Stores historical asset prices directly in the MariaDB database.

### `opening_spot_prices`
Stores opening spot prices for each asset as the markets open. The opening spot price is the price of the asset at the beginning of the trading day. 
- `opening_spot_prices` : Stores the opening spot prices for each asset.

### `forecasts`
The following tables are used to store the forecasts for the next 15 days for each asset. 
- `asset_price_forecasts` : Stores the forecasts for the next 15 days for each asset.
- `exogenous_series_forecasts` : Stores the forecasts for the next 15 days for each exogenous series.

### `exogenous_series` 
Stores time series data downloaded daily for use as exogenous data, historical exogenous time-series data, and forecasts of exogenous time-series data directly in the MariaDB database.
- `exogenous_series_history` : Stores historical exogenous values directly in the MariaDB database.
### `booty` 
The 'booty' schema is a collection of tables designed to store and manage information related to a trading bot's operations. It includes tables to track orders, executed orders, cash transactions, asset holdings, dividends, stock splits, historical asset balances, and daily cash summaries. This schema provides a comprehensive view of the trading bot's activities and the account's financial status, enabling efficient analysis and decision-making.
- `orders` : Stores information about all the orders placed by the trading bot, including the asset, order type, status, price, and quantity.
- `executed_orders` : Records the details of executed orders, including the execution price, execution time, and settlement date.
- `account_cash_transactions` : Keeps track of all cash transactions in the account, such as deposits, withdrawals, dividends, and buy/sell transactions, including the transaction date, settlement date, amount, and fees.
- `asset_holdings` : Stores the current holdings of each asset in the account, including the quantity and current value.
- `dividens` : Records the dividend information for each asset, including the dividend amount, ex-dividend date, and payment date.
- `stock_splits` : Stores information about stock splits for each asset, including the split ratio and split date.
- `historical_asset_balances` : Maintains a record of historical asset balances in the account, including the asset quantity and value at a specific date.
- `daily_cash_summary` : Keeps a daily summary of the account's available and unsettled cash balances.

For more information on the SQL code used to create and set up these tables in the MariaDB database, refer to the ETL script or the SQL code provided in this documentation.


## ETL Script (UNDER CONSTRUCTION)

The ETL (Extract, Transform, Load) script is responsible for managing the process of downloading new data, updating the database, and saving the data as Feather files. You can find this script in the `src/data_gathering_and_processing/etl_script.py` file.

To run the ETL script, execute the following command from the project root directory:

```bash
python src/data_gathering_and_processing/etl_script.py
```


## Sandbox Directory
The __Sandbox__ directory should not be considered part of the main project.  It's a dedicated space for experimentation, testing new ideas, or working on features that are not yet ready for integration into the main project. When a feature or idea is mature and ready for integration, the relevant code should be moved from the "Sandbox" directory to the appropriate location within the main project. Here are some key featurs of the sanbox directory:
1. Isolation of experimental code from the main project: By keeping experimental code separate from the main project, you can ensure that the main codebase remains stable and reliable.
2. Easier collaboration: Team members can work on new features or ideas in the "Sandbox" without affecting the main project. This can help reduce merge conflicts and streamline the development process.
3. Encouraging innovation: A dedicated space for experimentation can encourage team members to explore new ideas and techniques without worrying about breaking the main project.


## Disclaimer

This platform is currently under active development and should not be considered stable for live trading. Never risk money you cannot afford to lose. Always test your strategies before taking them live.
Please feel free to let me know if you'd like any further adjustments or additional information.
