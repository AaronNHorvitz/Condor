"""
opening_spot_prices_tables.py

This module contains a function to create the opening_spot_prices table in the database.
"""
from pymysql.connections import Connection

def create_tables(connection : Connection)-> None:
    """
    Create the opening_spot_prices table in the database using the provided connection.

    The opening_spot_prices table stores the next day's opening prices, which will be queried in the morning.

    Parameters
    ----------
    connection : Connection
        A database connection object.

    Returns
    -------
    None
    """

    # Define the SQL queries
    create_opening_spot_prices = """
    CREATE TABLE IF NOT EXISTS opening_spot_prices.opening_spot_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT,
    date_time DATETIME,  -- This column now stores both date and time for the opening spot price.
    price DECIMAL(15, 4),
    FOREIGN KEY (asset_id) REFERENCES asset_info(id)
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
    print('INFO: Creating the OPENING_SPOT_PRICES table under the OPENING_SPOT_PRICES schema.')
    try: 
        print('INFO: Created the OPENING_SPOT_PRICES.')
        cursor.execute(create_opening_spot_prices)
    except Exception as e:
        print("ERROR: Failed to create the OPENING_SPOT_PRICES table.")
        print(e)
    
    # Commit the changes
    connection.commit()