from pymysql.connections import Connection

def create_tables(connection : Connection)-> None:

    # Define the SQL queries
    asset_price_forecasts = """
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
    """

    exogenous_series_forecasts = """
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
    """

    # Create a cursor for the connection
    try:
        cursor = connection.cursor()
    except Exception as e:
        print("Error: Unable to create a cursor for the connection.")
        print(e)
        return
    
    # Execute the queries
    print('INFO: Creating ASSET_PRICE_FORECASTS tables under the FORECASTS schema.')
    try: 
        cursor.execute(asset_price_forecasts)
        print('INFO: Created ASSET_PRICE_FORECASTS table.')
    except Exception as e:
        print('Error: Unable to create ASSET_PRICE_FORECASTS table.')
        print(e)
    print('INFO: Creating the EXOGENOUS_SERIES_FORECASTS table under the FORECASTS schema.')
    try:
        cursor.execute(exogenous_series_forecasts)
        print('INFO: Created EXOGENOUS_SERIES_FORECASTS table.')
        print(e)
    except Exception as e:
        print('Error: Unable to create EXOGENOUS_SERIES_FORECASTS table.')
        print(e)

    # Commit the changes
    connection.commit()