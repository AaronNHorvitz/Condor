"""
asset_price_history_tables.py

This module contains the create_asset_price_history_tables function that creates
the historical_asset_prices table in the ASSET_PRICE_HISTORY schema.

Functions:
----------
create_historical_asset_prices(connection: Connection) -> None
    Creates the historical_asset_prices table in the ASSET_PRICE_HISTORY schema.

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
    Creates the historical_asset_prices table in the ASSET_PRICE_HISTORY schema.
    
    Parameters
    ----------
    connection : Connection
        A pymysql.connections.Connection object representing a connection to a MariaDB server.
    
    Returns
    -------
    None
    """

    # Define the SQL queries
    create_historical_asset_prices = """
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
    """

    # Create a cursor for the connection
    try:
        cursor = connection.cursor()
    except Exception as e:
        print("Error: Unable to create a cursor for the connection.")
        print(e)
        return

    # Execute the queries
    print('INFO: Creating the HISTORICAL_ASSET_PRICES table under the ASSET_PRICE_HISTORY schema.')
    try: 
        cursor.execute(create_historical_asset_prices)
        print('INFO: Created the HISTORICAL_ASSET_PRICES table.')
    except Exception as e:
        print('ERROR: Failed to create the HISTORICAL_ASSET_PRICES table.')
        print(e)
    
    # Commit the changes
    connection.commit()

