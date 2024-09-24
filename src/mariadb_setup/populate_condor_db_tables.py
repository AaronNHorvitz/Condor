import os
import sys
from pathlib import Path

# Get the current working directory
current_dir = Path(os.getcwd())

# Get the parent directory (Condor)
parent_dir = current_dir.parent

# Get the src directory
src_dir = parent_dir / "src"

# Add the src directory to the system path
sys.path.append(str(src_dir))

# Import modules and libraries from the data_gathering_and_processing directory
from data_gathering_and_processing.secure_storage import (
    encrypt,
    decrypt,
    store_password,
    get_password,
    generate_password
    )
from data_gathering_and_processing.mariadb_connector import MariaDBConnector


def main():
    # Establish a connection to the MariaDB localhost
    app_name = "condor"
    connector = MariaDBConnector(app_name)
    connection = connector.connect()
        
    # Create the database and schemas
    create_database.create_condor_db(connection)
    
    # Create the tables in the various schemas
    series_information_tables.create_tables(connection)
    asset_price_history_tables.create_tables(connection)
    opening_prices_tables.create_tables(connection)
    price_forecasts_tables.create_tables(connection)
    exogenous_series_tables.create_tables(connection)
    exogenous_forecasts_tables.create_tables(connection)
    
    # Close the connection
    db_connection.close(connection)

if __name__ == '__main__':
    main()


def create_tables(connection):
    cursor = connection.cursor()

    # Define the SQL queries
    create_historical_stock_prices = '''
    USE ASSET_PRICE_HISTORY;

    CREATE TABLE IF NOT EXISTS historical_stock_prices (
      id INT AUTO_INCREMENT PRIMARY KEY,
      asset_id INT NOT NULL,
      date DATE NOT NULL,
      open DECIMAL(15, 4),
      high DECIMAL(15, 4),
      low DECIMAL(15, 4),
      close DECIMAL(15, 4),
      volume DECIMAL(15, 4),
      interpolated BOOLEAN DEFAULT FALSE,
      FOREIGN KEY (asset_id) REFERENCES SERIES_INFORMATION.asset_info(id),
      UNIQUE KEY (asset_id, date)
    );
    '''

    # Execute the queries
    cursor.execute(create_historical_stock_prices)

    # Commit the changes
    connection.commit()

    
