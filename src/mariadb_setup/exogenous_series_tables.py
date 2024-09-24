from pymysql.connections import Connection

def create_tables(connection : Connection)-> None:

# Define the SQL queries
    exogenous_series_history = """
    USE EXOGENOUS_SERIES;

    CREATE TABLE IF NOT EXISTS exogenous_series_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exogenous_series_id INT NOT NULL,
    date DATE NOT NULL,
    value DECIMAL(15, 4),
    FOREIGN KEY (exogenous_series_id) REFERENCES exogenous_series_info(id),
    UNIQUE KEY (exogenous_series_id, date)
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
    print('INFO: Creating databasse tables under the info_tables schema.')
    try: 
        cursor.execute(exogenous_series_history)
        print('INFO: Created asset_price_forecasts table.')
    except Exception as e:
        print('Error: Unable to create asset_price_forecasts table.')
        print(e)

    # Commit the changes
    connection.commit()

