"""
info_tables.py

This module contains the create_info_tables function that creates informational
tables in the database using the provided connection.

The following tables are created by the create_info_tables function:
1. database_updates: Records updates to the database.
2. asset_info: Contains information about each available stock ticker.
3. exogenous_series_info: Stores time series data downloaded daily for use as exogenous data.
4. market_closed_dates: Contains the dates when the market was closed.

Functions:
----------
create_info_tables(connection: Connection) -> None
    Creates the informational tables in the database using the provided connection.

Parameters
----------
connection : Connection
    A pymysql.connections.Connection object representing a connection to a MariaDB server.

Returns
-------
None

Raises
------
Exception
    If there is an error creating the cursor for the connection, executing SQL queries, or creating any of the tables.

"""

from pymysql.connections import Connection

def create_tables(connection : Connection)-> None:
    """
    Create informational tables in the database using the provided connection.

    This function creates the following tables:
    1. series_updates: Records updates to the database.
    2. asset_info: Contains information about each available stock ticker.
    3. exogenous_series_info: Stores time series data downloaded daily for use as exogenous data.
    4. market_closed_dates: Contains the dates when the market was closed.

    Parameters
    ----------
    connection : Connection
        A database connection object.

    Returns
    -------
    None
    """

    # Define the SQL queries
    create_database_updates = '''
    CREATE TABLE IF NOT EXISTS info_tables.database_updates(
    id INT AUTO_INCREMENT PRIMARY KEY,
    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
    );
    '''

    create_asset_info = '''
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
    '''

    create_exogenous_series_info = '''
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
    '''

    create_market_closed_dates = '''
    CREATE TABLE IF NOT EXISTS info_tables.market_closed_dates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    closed_date DATE NOT NULL UNIQUE,
    listing_exchange VARCHAR(50),
    reason VARCHAR(255)
    );
    '''

    # Create a cursor for the connection
    try:
        cursor = connection.cursor()
    except Exception as e:
        print("Error: Unable to create a cursor for the connection.")
        print(e)
        return

    # Execute the queries
    print('INFO: Creating the DATABASE_UPDATES table under the INFO_TABLES schema.')
    try: 
        cursor.execute(create_database_updates)
        print('INFO: Created DATABASE_UPDATES table.')
    except Exception as e:
        print('ERROR: Failed to create DATABASE_UPDATES table.')
        print(e)

    print('INFO: Creating the ASSET_INFO table under the INFO_TABLES schema.')
    try:
        cursor.execute(create_asset_info)
        print('INFO: Created ASSET_INFO table.')
    except Exception as e:
        print('ERROR: Failed to create the ASSET_INFO table.')
        print(e)
    print('INFO: Creating the EXOGENOUS_SERIES_INFO table under the INFO_TABLES schema.')
    try:
        cursor.execute(create_exogenous_series_info)
        print('INFO: Created EXOGENOUS_SERIES_INFO table.')
    except Exception as e:
        print('ERROR: Failed to create EXOGENOUS_SERIES_INFO table.')
        print(e)
    print('INFO: Creating the MARKET_CLOSED_DATES table under the INFO_TABLES schema.')
    try:
        cursor.execute(create_market_closed_dates)
        print('INFO: Created MARKET_CLOSED_DATES table.')
    except Exception as e:
        print('ERROR: Failed to create MARKET_CLOSED_DATES table.')
        print(e)

    # Commit the changes
    connection.commit()
