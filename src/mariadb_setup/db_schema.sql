/*
File Name: condor_database.sql
Description: SQL script to create the Condor database and its tables.
Author: Aaron Horvitz
Date Created: March 31, 2023
*/

-- Create the database and schemas:
CREATE DATABASE IF NOT EXISTS Condor;

CREATE SCHEMA IF NOT EXISTS INFO_TABLES; 
CREATE SCHEMA IF NOT EXISTS ASSET_PRICE_HISTORY; 
CREATE SCHEMA IF NOT EXISTS OPENING_SPOT_PRICES; 
CREATE SCHEMA IF NOT EXISTS FORECASTS; 
CREATE SCHEMA IF NOT EXISTS EXOGENOUS_SERIES;
CREATE SCHEMA IF NOT EXISTS BOOTY;
/* 
INFO_TABLES Schema -------------------------------------------------------------------------------------------------|
  The following tables are used to store information about the database and its contents. 
  The information in these tables is used to determine which data needs to be updated and which data can be used as is.
*/

-- Database Updates:
--    Records each time the ETL script updates the database and provides a description of the changes made.
CREATE TABLE IF NOT EXISTS info_tables.database_updates(
  id INT AUTO_INCREMENT PRIMARY KEY,
  update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description TEXT
);

-- Asset Information:
--    Contains information about each available stock ticker, including whether the ticker is new, delisted, and its date range.
CREATE TABLE IF NOT EXISTS info_tables.asset_info(
  id INT AUTO_INCREMENT PRIMARY KEY,
  symbol VARCHAR(50) NOT NULL UNIQUE,
  cqs_symbol VARCHAR(50) NOT NULL UNIQUE,
  nasdaq_symbol VARCHAR(50) NOT NULL UNIQUE,
  security_name VARCHAR(255),
  market_category VARCHAR(255),
  listing_exchange VARCHAR(50),
  earliest_date DATE,
  lastest_date DATE,
  last_date_of_record DATE, 
  is_etf BOOLEAN,
  is_delisted BOOLEAN
);

-- Exogenous Data Information:
--    Stores time series data downloaded daily for use as exogenous data. Each record contains a series identifier and a pointer to 
--    the location of the Feather files where the information is stored.
CREATE TABLE IF NOT EXISTS info_tables.exogenous_series_info(
  id INT AUTO_INCREMENT PRIMARY KEY,
  series_id VARCHAR(50) NOT NULL UNIQUE, -- This is usually a series code or symbol provided by the data source. You may need to make one up if the data source doesn't provide one.
  series_name VARCHAR(255) NOT NULL, -- This is usually the name of the series provided by the data source.
  series_description VARCHAR(510) NOT NULL, -- This is usually the description of the series provided by the data source.
  series_source VARCHAR(510), -- This is usually the source of the data where the series is pulled from. 
  series_release VARCHAR(255), 
  series_citations vARCHAR(510), 
  series_location VARCHAR(255) NOT NULL,
  series_frequency VARCHAR(50) NOT NULL,
  series_seasonality VARCHAR(50) NOT NULL,
  series_unit VARCHAR(50) NOT NULL,
  series_seasonal_adjustment VARCHAR(255) NOT NULL,
  series_last_updated_at_fed DATE NOT NULL,
  first_date_recorded DATE,
  last_date_recorded DATE,
  is_delisted BOOLEAN, 
);

-- Dates market was closed:
--    Stores dates when the market was closed for trading.
CREATE TABLE IF NOT EXISTS info_tables.market_closed_dates (
  id INT AUTO_INCREMENT PRIMARY KEY,
  closed_date DATE NOT NULL UNIQUE,
  listing_exchange VARCHAR(50),
  reason VARCHAR(255)
);

/*
ASSET_PRICE_HISTORY Schema ----------------------------------------------------------------------------------------|
  The following table is used to store the historical asset prices. 
  The historical asset prices are used to calculate the returns of the asset for the day.
*/

CREATE TABLE IF NOT EXISTS asset_price_history.historical_asset_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  date DATE NOT NULL,
  open DECIMAL(15, 4),
  high DECIMAL(15, 4),
  low DECIMAL(15, 4),
  close DECIMAL(15, 4),
  volume DECIMAL(15, 4),
  interpolated_value BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (asset_id) REFERENCES SERIES_INFORMATION.asset_info(id),
  UNIQUE KEY (asset_id, date)
);

/* 
OPENING_SPOT_PRICES Schema ---------------------------------------------------------------------------------------|
  The following table is used to store the opening spot prices for each asset. 
  The opening spot price is the price of the asset at the beginning of the trading day. 
  This is used to calculate the returns of the asset for the day.
*/

-- opening_spot_prices:
--    Stores the next day's opening prices, which will be queried in the morning.
CREATE TABLE IF NOT EXISTS open_spot_prices.opening_spot_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT,
  date_time DATETIME,  -- This column now stores both date and time for the opening spot price.
  price DECIMAL(15, 4),
  FOREIGN KEY (asset_id) REFERENCES asset_info(id)
);

/* 
FORECASTS Schema -------------------------------------------------------------------------------------------------|
  The following tables are used to store the forecasts for the next 15 days for each asset. 
  The forecasts are used to calculate the returns of the asset for the day.
*/

-- asset_price_forecasts
--   Stores the forecasts for the next 15 days for each asset.
CREATE TABLE IF NOT EXISTS forecasts.asset_price_forecasts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  asset_id INT NOT NULL,
  forecast_date DATE NOT NULL,
  day_1 DECIMAL(15, 4),
  day_2 DECIMAL(15, 4),
  day_3 DECIMAL(15, 4),
  day_4 DECIMAL(15, 4),
  day_5 DECIMAL(15, 4),
  day_6 DECIMAL(15, 4),
  day_7 DECIMAL(15, 4),
  day_8 DECIMAL(15, 4),
  day_9 DECIMAL(15, 4),
  day_10 DECIMAL(15, 4),
  day_11 DECIMAL(15, 4),
  day_12 DECIMAL(15, 4),
  day_13 DECIMAL(15, 4),
  day_14 DECIMAL(15, 4),
  day_15 DECIMAL(15, 4),
  FOREIGN KEY (asset_id) REFERENCES INFO_TABLES.asset_info(id),
  UNIQUE KEY (asset_id, forecast_date)
);

-- exogenous_series_forecasts
--   Stores the forecasts for the next 15 days for each exogenous series.
CREATE TABLE IF NOT EXISTS forecasts.exogenous_series_forecasts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  series_id INT NOT NULL,
  forecast_date DATE NOT NULL,
  day_1 DECIMAL(15, 4),
  day_2 DECIMAL(15, 4),
  day_3 DECIMAL(15, 4),
  day_4 DECIMAL(15, 4),
  day_5 DECIMAL(15, 4),
  day_6 DECIMAL(15, 4),
  day_7 DECIMAL(15, 4),
  day_8 DECIMAL(15, 4),
  day_9 DECIMAL(15, 4),
  day_10 DECIMAL(15, 4),
  day_11 DECIMAL(15, 4),
  day_12 DECIMAL(15, 4),
  day_13 DECIMAL(15, 4),
  day_14 DECIMAL(15, 4),
  day_15 DECIMAL(15, 4),
  FOREIGN KEY (series_id) REFERENCES INFO_TABLES.exogenous_series_info(id),
  UNIQUE KEY (series_id, forecast_date)
);

/* 
EXOGENOUS_SERIES Schema -------------------------------------------------------------------------------------------------|
  The following table is used to store the historical exogenous series data. 
  The historical exogenous series data is used to calculate the returns of the asset for the day.
*/

CREATE TABLE IF NOT EXISTS exogenous_series.exogenous_series_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  exogenous_series_id INT NOT NULL,
  date DATE NOT NULL,
  value DECIMAL(15, 4),
  FOREIGN KEY (exogenous_series_id) REFERENCES exogenous_series_info(id),
  UNIQUE KEY (exogenous_series_id, date)
);

/* 
BOOTY Schema ------------------------------------------------------------------------------------------------------------|
  The 'booty' schema is a collection of tables designed to store and manage information related to a trading 
  bot's operations. It includes tables to track orders, executed orders, cash transactions, asset holdings, 
  dividends, stock splits, historical asset balances, and daily cash summaries. This schema provides a comprehensive
  view of the trading bot's activities and the account's financial status, enabling efficient analysis and decision-making.
*/

-- orders table
--    This table stores information about all the orders placed by the trading bot, including the asset, 
--    order type, status, price, and quantity.
CREATE TABLE IF NOT EXISTS booty.orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    order_type ENUM('buy', 'sell', 'buy_limit', 'sell_limit', 'buy_stop', 'sell_stop') NOT NULL,
    status ENUM('pending', 'executed', 'cancelled', 'rejected') NOT NULL,
    price DECIMAL(15, 4) NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- executed_orders table
--    This table records the details of executed orders, including the execution price, execution time, and settlement date.
CREATE TABLE IF NOT EXISTS booty.executed_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    execution_price DECIMAL(15, 4) NOT NULL,
    execution_time TIMESTAMP NOT NULL,
    settlement_date DATE NOT NULL,
    transaction_fee DECIMAL(15, 4),
    FOREIGN KEY (order_id) REFERENCES booty.orders(id)
);

-- account_cash_transactions table
--    This table keeps track of all cash transactions in the account, such as deposits, withdrawals, dividends, and buy/sell 
--    transactions, including the transaction date, settlement date, amount, and fees.
CREATE TABLE IF NOT EXISTS booty.account_cash_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type ENUM('deposit', 'withdraw', 'dividend', 'buy', 'sell') NOT NULL,
    transaction_date DATE NOT NULL,
    settlement_date DATE NOT NULL,
    amount DECIMAL(15, 4) NOT NULL,
    fee DECIMAL(15, 4) DEFAULT 0,
    asset_id INT,
    asset_quantity DECIMAL(15, 4),
    balance DECIMAL(15, 4) NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- asset_holdings table
--    This table stores the current holdings of each asset in the account, including the quantity and current value.
CREATE TABLE IF NOT EXISTS booty.asset_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    current_value DECIMAL(15, 4) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- dividends table
--    This table records the dividend information for each asset, including the dividend amount, ex-dividend date, and payment date.
CREATE TABLE IF NOT EXISTS booty.dividends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    dividend_amount DECIMAL(15, 4) NOT NULL,
    ex_dividend_date DATE NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- stock_splits table
--    This table stores information about stock splits for each asset, including the split ratio and split date.
CREATE TABLE IF NOT EXISTS booty.stock_splits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    split_ratio DECIMAL(15, 4) NOT NULL,
    split_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- historical_asset_balances table
--    This table maintains a record of historical asset balances in the account, including the asset quantity and value at a specific date.
CREATE TABLE IF NOT EXISTS booty.historical_asset_balances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    value_at_date DECIMAL(15, 4) NOT NULL,
    balance_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
);

-- daily_cash_summary table
--    This table keeps a daily summary of the account's available and unsettled cash balances.
CREATE TABLE IF NOT EXISTS booty.daily_cash_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL UNIQUE,
    available_cash DECIMAL(15, 4) NOT NULL,
    unsettled_cash DECIMAL(15, 4) NOT NULL
);


