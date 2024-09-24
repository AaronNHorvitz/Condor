"""
create_database.py

This module contains the create_condor_db function that creates the 'Condor' database and
associated schema in the provided MariaDB server.

The following schema are created within the 'Condor' database:
1. INFO_TABLES
2. ASSET_PRICE_HISTORY
3. OPENING_SPOT_PRICES
4. FORECASTS
5. EXOGENOUS_SERIES

Functions
---------
create_condor_db(connection: Connection) -> None
    Creates the 'Condor' database and associated schema in the provided MariaDB server.

Parameters
----------
connection : Connection
    A pymysql.connections.Connection object representing a connection to a MariaDB server.

Returns
-------
None
"""

from pymysql.connections import Connection

def create_condor_db(connection : Connection)-> None:
    """
    Create the 'Condor' database and associated schema in the provided MariaDB server.
    
    This function creates the following schema within the 'Condor' database:
    1. INFO_TABLES
    2. ASSET_PRICE_HISTORY
    3. OPENING_SPOT_PRICES
    4. FORECASTS
    5. EXOGENOUS_SERIES

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

    # Define the SQL queries
    create_condor_db = """
    CREATE DATABASE IF NOT EXISTS Condor;

    CREATE SCHEMA IF NOT EXISTS INFO_TABLES; 
    CREATE SCHEMA IF NOT EXISTS ASSET_PRICE_HISTORY; 
    CREATE SCHEMA IF NOT EXISTS OPENING_SPOT_PRICES; 
    CREATE SCHEMA IF NOT EXISTS FORECASTS; 
    CREATE SCHEMA IF NOT EXISTS EXOGENOUS_SERIES;
    """

    # Create a cursor for the connection
    try:
        cursor = connection.cursor()
    except Exception as e:
        print("Error: Unable to create a cursor for the connection.")
        print(e)
        return

    # Execute the queries
    print('INFO: Creating the Condor database and associated schema.')
    try: 
        cursor.execute(create_condor_db)
        print('INFO: Created the Condor database and associated schema.')
    except Exception as e:
        print('Error: Unable to creat the Condor database.')
        print(e)

    # Commit the changes
    connection.commit()