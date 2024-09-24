"""
mariadb_connector.py
---------------------------

This module provides the MariaDBConnector class to securely store and retrieve login data for a MariaDB database.
It also establishes a connection to the MariaDB database using the decrypted credentials and the pymysql library.

The MariaDBConnector class includes the following methods:

- store_credentials(username: str, password: str) -> None:
    Store encrypted credentials using the keyring library.
- get_credentials() -> Tuple[str, str]:
    Retrieve and decrypt stored credentials.
- connect() -> Connection:
    Establish a connection to the MariaDB database using the decrypted credentials.

Example:

    app_name = "my_app"
    connector = MariaDBConnector(app_name)
    
    # Store encrypted credentials (only needed once)
    connector.store_credentials("your_db_user", "your_db_password")

    # Establish a connection to the MariaDB database
    connection = connector.connect()

    # Perform database operations using the `connection` object
    # ...

    # Close the connection when done
    connection.close()

Dependencies:
- pymysql
- secure_storage (local module)
"""

import pymysql
from typing import Tuple
from pymysql.connections import Connection

from src.mariadb_setup.secure_storage import encrypt, decrypt, store_password, get_password, generate_password

class MariaDBConnector:
    """
    A class to securely store and retrieve the login data for a MariaDB database
    and establish a connection using the pymysql library.

    Attributes
    ----------
    app_name : str
        A unique identifier for your application or script.

    Methods
    -------
    store_credentials(host: str, port: int, user: str, password: str) -> None:
        Store encrypted credentials using the keyring library.
    get_credentials() -> Tuple[str, int, str, str]:
        Retrieve and decrypt stored credentials.
    connect() -> Connection:
        Establish a connection to the MariaDB database using the decrypted credentials.
    """

    def __init__(self, app_name: str):
        """
        Initialize the MariaDBConnector class.

        Parameters
        ----------
        app_name : str
            A unique identifier for your application or script.
        """

        self.app_name = app_name

    def store_credentials(self, username: str, password: str) -> None:
        """
        Store encrypted credentials using the keyring library.

        Parameters
        ----------
        username : str
            The username to be stored.
        password : str
            The password to be stored.

        Notes
        -----
        This function encrypts the username and password using the secure_storage module,
        and then stores the encrypted credentials using the keyring library. It also stores
        the encryption password used for encrypting the credentials.
        """
        
        encryption_password = generate_password()  # You can set a fixed encryption_password or use generate_password()

        encrypted_username = encrypt(username, encryption_password)
        encrypted_password = encrypt(password, encryption_password)
        
        store_password(self.app_name, "username", encrypted_username)
        store_password(self.app_name, "password", encrypted_password)
        store_password(self.app_name, "encryption_password", encryption_password)

    def get_credentials(self) -> Tuple[str, str]:
        """
        Retrieve and decrypt stored credentials.

        Returns
        -------
        Tuple[str, str]
            A tuple containing the decrypted username and password.

        Notes
        -----
        This function retrieves the encrypted credentials and the encryption password
        from the keyring library, and then decrypts the credentials using the secure_storage
        module.
        """
        encrypted_username = get_password(self.app_name, "username")
        encrypted_password = get_password(self.app_name, "password")
        encryption_password = get_password(self.app_name, "encryption_password")

        username = decrypt(encrypted_username, encryption_password)
        password = decrypt(encrypted_password, encryption_password)
        
        return username, password


    def connect(self) -> Connection:
        """
        Establish a connection to the MariaDB database using the decrypted credentials.

        Returns
        -------
        Connection
            A pymysql connection object for the MariaDB database.
        """
        
        host, port, user, password = self.get_credentials()

        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection