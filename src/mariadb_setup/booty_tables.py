"""
booty.py
This module contains a function that creates a set of tables under the 'BOOTY' schema in a given MySQL database.
The tables are designed to store and manage information related to a trading bot's operations, such as orders,
executed orders, cash transactions, asset holdings, dividends, stock splits, historical asset balances, and daily cash
summaries. This schema provides a comprehensive view of the trading bot's activities and the account's financial status,
enabling efficient analysis and decision-making.

"""


from pymysql.connections import Connection

def create_tables(connection : Connection)-> None:

    """

    This function creates the following tables:
        * orders
            - stores information about all the orders placed by the trading bot, including the asset, order type, status, price, and quantity.
        * executed_orders
            - records the details of executed orders, including the execution price, execution time, and settlement date.
        * account_cash_transactions
            - keeps track of all cash transactions in the account, such as deposits, withdrawals, dividends, and buy/sell transactions, including the transaction date, settlement date, amount, and fees.
        * asset_holdings
            - stores the current holdings of each asset in the account, including the quantity and current value.
        * dividends
            - records the dividend information for each asset, including the dividend amount, ex-dividend date, and payment date.
        * stock_splits
            - stores information about stock splits for each asset, including the split ratio and split date.
        * historical_asset_balances
            - maintains a record of historical asset balances in the account, including the asset quantity and value at a specific date.
        * daily_cash_summary
            - keeps a daily summary of the account's available and unsettled cash balances.

    Parameters
    ----------
    connection : pyconn.Connection
        A pymysql connection object connected to the target MySQL database.

    Returns
    -------
    None

    Raises
    ------
    Exception
        If there is an error creating the cursor for the connection, executing SQL queries, or creating any of the tables.
    """

    # Define the SQL queries to create tables under the 'BOOTY' schema
    create_orders_table = """
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
     """
    
    create_executed_orders_table = """
    CREATE TABLE IF NOT EXISTS booty.executed_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    execution_price DECIMAL(15, 4) NOT NULL,
    execution_time TIMESTAMP NOT NULL,
    settlement_date DATE NOT NULL,
    transaction_fee DECIMAL(15, 4),
    FOREIGN KEY (order_id) REFERENCES booty.orders(id)
    );
    """

    create_account_cash_transactions_table = """
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
    """

    create_asset_holdings_table = """
    CREATE TABLE IF NOT EXISTS booty.asset_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    quantity DECIMAL(15, 4) NOT NULL,
    current_value DECIMAL(15, 4) NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
    );
    """

    create_dividens_table =   """
    CREATE TABLE IF NOT EXISTS booty.dividends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    dividend_amount DECIMAL(15, 4) NOT NULL,
    ex_dividend_date DATE NOT NULL,
    payment_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
    );
    """

    create_stock_splits_table = """ 
    CREATE TABLE IF NOT EXISTS booty.stock_splits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    split_ratio DECIMAL(15, 4) NOT NULL,
    split_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
    );
    """

    create_historical_asset_balances_table = """
    CREATE TABLE IF NOT EXISTS booty.historical_asset_balances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    value_at_date DECIMAL(15, 4) NOT NULL,
    balance_date DATE NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES booty.asset_info(id)
    );
    """

    create_daily_cash_summary_table = """
    CREATE TABLE IF NOT EXISTS booty.daily_cash_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    summary_date DATE NOT NULL UNIQUE,
    available_cash DECIMAL(15, 4) NOT NULL,
    unsettled_cash DECIMAL(15, 4) NOT NULL
    );
    """

    # Create a cursor for the connection
    try:
        cursor = connection.cursor()
    except Exception as e:
        print("Error: Unable to create a cursor for the connection.")
        print(e)
        return

    # Create the 'orders' table
    print('INFO: Creating the CREATE_ORDERS table under the BOOTY schema.')
    try: 
        cursor.execute(create_orders_table)
        print('INFO: Created CREATE_ORDERS table.')
    except Exception as e:
        print('ERROR: Failed to create CREATE_ORDERS table.')
        print(e)

    # Create the 'executed_orders' table
    print('INFO: Creating the EXECUTED_ORDERS table under the BOOTY schema.')
    try:
        cursor.execute(create_executed_orders_table)
        print('INFO: Created EXECUTED_ORDERS table.')
    except Exception as e:
        print('ERROR: Failed to create the EXECUTED_ORDERS table.')
        print(e)

    # Create the 'account_cash_transactions' table
    print('INFO: Creating the ACCOUNT_CASH_TRANSACTIONS table under the BOOTY schema.')
    try:
        cursor.execute(create_account_cash_transactions_table)
        print('INFO: Created ACCOUNT_CASH_TRANSACTIONS table.')
    except Exception as e:
        print('ERROR: Failed to create ACCOUNT_CASH_TRANSACTIONS table.')
        print(e)

    # Create the 'asset_holdings' table
    print('INFO: Creating the ASSET_HOLDINGS table under the BOOTY schema.')
    try:
        cursor.execute(create_asset_holdings_table)
        print('INFO: Created ASSET_HOLDINGS table.')
    except Exception as e:
        print('ERROR: Failed to create ASSET_HOLDINGS table.')
        print(e)

    # Create the 'dividends' table
    print('INFO: Creating the DIVIDENS table under the BOOTY schema.')
    try:
        cursor.execute(create_dividens_table)
        print('INFO: Created DIVIDENS table.')
    except Exception as e:
        print('ERROR: Failed to create DIVIDENS table.')
        print(e)

    # Create the 'stock_splits' table
    print('INFO: Creating the STOCK_SPLITS table under the BOOTY schema.')
    try:
        cursor.execute(create_stock_splits_table)
        print('INFO: Created STOCK_SPLITS table.')
    except Exception as e:
        print('ERROR: Failed to create STOCK_SPLITS table.')
        print(e)

    # Create the 'historical_asset_balances' table
    print('INFO: Creating the HISTORICAL_ASSET_BALANCES table under the BOOTY schema.')
    try:
        cursor.execute(create_historical_asset_balances_table)
        print('INFO: Created HISTORICAL_ASSET_BALANCES table.')
    except Exception as e:
        print('ERROR: Failed to create HISTORICAL_ASSET_BALANCES table.')
        print(e)

    # Create the 'daily_cash_summary' table
    print('INFO: Creating the DAILY_CASH_SUMMARY table under the BOOTY schema.')
    try:
        cursor.execute(create_daily_cash_summary_table)
        print('INFO: Created DAILY_CASH_SUMMARY table.')
    except Exception as e:
        print('ERROR: Failed to create DAILY_CASH_SUMMARY table.')
        print(e)

    # Commit the changes to the database to finalize table creation
    connection.commit()






