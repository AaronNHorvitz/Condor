"""
secure_storage.py
-----------------

This module provides functions to securely store and manage sensitive information, such as passwords and login data,
by encrypting and decrypting data using the cryptography library and storing encrypted data using the keyring library.

Functions:

- encrypt(plaintext: str, password: str) -> str:
    Encrypt a given plaintext using a password and return the encrypted data as a base64-encoded string.
- decrypt(ciphertext: str, password: str) -> str:
    Decrypt a base64-encoded ciphertext using a password and return the decrypted data as a string.
- store_password(app_name: str, key: str, password: str) -> None:
    Store a password securely using the keyring library, associated with a given application name and key.
- get_password(app_name: str, key: str) -> Optional[str]:
    Retrieve a stored password using the keyring library, associated with a given application name and key.
- generate_password(length: int = 50) -> str:
    Generate a secure random password with the given length.

Classes:

- CredentialsManager:
    A class for storing and managing database connection information securely using the keyring library.
- DatabaseManager: 
    A class for managing database connections and executing SQL queries using stored credentials. 
Example:

    from src.secure_storage import encrypt, decrypt, store_password, get_password, generate_password, CredentialsManager
    
    app_name = "my_app"
    key = "my_key"
    plaintext = "sensitive_data"
    password = generate_password()  # Generate a random encryption password

    # Encrypt and store sensitive data
    encrypted_data = encrypt(plaintext, password)
    store_password(app_name, key, encrypted_data)

    # Retrieve and decrypt sensitive data
    stored_encrypted_data = get_password(app_name, key)
    decrypted_data = decrypt(stored_encrypted_data, password)

    # Store and manage database connection information
    cm = CredentialsManager(app_name)
    cm.store_credentials(
        driver="sybase",
        tcpip_commlinks="hostname:port",
        database_name="mydb",
        autocommit=True,
        username="myusername",
        password="mypassword"
    )
    credentials = cm.get_credentials()
    print(credentials)

Dependencies:
- cryptography
- keyring
- secrets
- string
"""

import os
import keyring
import string
import secrets
import pyodbc

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Union, Optional
from base64 import b64encode, b64decode


def encrypt(plaintext: str, password: str) -> str:
    """
    Encrypt the provided plaintext using the given password.

    Parameters
    ----------
    plaintext : str
        The text to be encrypted.
    password : str
        The password that will be used to encrypt the plaintext.

    Returns
    -------
    str
        The encrypted ciphertext, encoded as a base64 string.

    Notes
    -----
    The plaintext is encrypted using AES-256 in CBC mode. A random
    16-byte salt and a random 16-byte initialization vector (IV) are
    generated for each encryption process. The salt is used to derive
    the encryption key from the given password. The encrypted data,
    the salt, and the IV are then combined and encoded as a base64
    string for the final output.

    Examples
    --------
    >>> from src.secure_storage import encrypt

    >>> plaintext = "sensitive_data"
    >>> password = "my_password"

    >>> encrypted_data = encrypt(plaintext, password)
    >>> print(encrypted_data)

    """
    salt = os.urandom(16)
    backend = default_backend()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend,
    )
    key = kdf.derive(password.encode())

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_data = salt + iv + ciphertext
    return b64encode(encrypted_data).decode()


def decrypt(encrypted: str, password: str) -> str:
    """
    Decrypt the provided encrypted text using the given password.

    Parameters
    ----------
    encrypted : str
        The encrypted text to be decrypted.
    password : str
        The password used for decryption.

    Returns
    -------
    str
        The decrypted text.

    Notes
    -----
    The decrypt() function uses AES-256 in CBC mode to decrypt the given encrypted text.
    The password parameter must match the password used to encrypt the data with the encrypt() function.
    The encrypted text must be a base64-encoded string.
    The decrypt() function automatically derives the encryption key from the password and the salt included in the encrypted text.
    If the given password is incorrect, the decryption process will fail and an error will be raised.

    Examples
    --------
    >>> from src.secure_storage import decrypt

    >>> encrypted_data = "ILt9OuVJFbG+LUQO7RNOZozMknru7Jm3q+GpY+w8X9GJjAj1DvIg/ziN8+J0AKQ"
    >>> password = "my_password"

    >>> decrypted_data = decrypt(encrypted_data, password)
    >>> print(decrypted_data)
    """
    backend = default_backend()
    decoded_data = b64decode(encrypted)
    salt, iv, ciphertext = decoded_data[:16], decoded_data[16:32], decoded_data[32:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend,
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plaintext.decode()


def store_password(app_name: str, key: str, password: str) -> None:
    """
    Store a password securely using the keyring library.

    Parameters
    ----------
    app_name : str
        A unique identifier for your application or script.
    key : str
        A unique key to identify the stored password.
    password : str
        The password to be stored.

    Notes
    -----
    The store_password() function uses the keyring library to store a password securely in the
    underlying operating system's native key store or an external credential storage service.
    The app_name parameter is a unique identifier for your application or script. The key parameter
    is a unique key to identify the stored password. The password parameter is the password to be stored.
    The actual encryption method and level of security used to store the password depend on the operating
    system or external service. To retrieve the stored password later, use the get_password() function.

    Examples
    --------
    >>> from src.secure_storage import store_password
    >>> app_name = "my_app"
    >>> key = "my_key"
    >>> password = "my_password"
    >>> store_password(app_name, key, password)
    """

    keyring.set_password(app_name, key, password)


def get_password(app_name: str, key: str) -> str:
    """
    Retrieve a stored password using the keyring library.

    Parameters
    ----------
    app_name : str
        A unique identifier for your application or script.
    key : str
        The unique key used to identify the stored password.

    Returns
    -------
    str
        The retrieved password.

    Notes
    -----
    This function uses the keyring library to retrieve the password securely from the
    underlying operating system's native key store or an external credential storage
    service. The actual password is decrypted and returned by the keyring library, with
    the method of decryption depending on the operating system or external service.
    """
    return keyring.get_password(app_name, key)


def generate_password(length: int = 50) -> str:
    """
    Generate a secure random password with the given length.

    Parameters
    ----------
    length : int, optional, default = 50.
        The length of the generated password.

    Returns
    -------
    str
        The generated secure random password.

    Notes
    -----
    The get_password() function uses the keyring library to retrieve a stored password securely from the
    underlying operating system's native key store or an external credential storage service. The app_name
    parameter is a unique identifier for your application or script. The key parameter is the unique key
    used to identify the stored password.The actual decryption method and level of security used to
    retrieve the password depend on the operating system or external service.

    Example
    -------
    >>> password = generate_password()
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


class CredentialsManager:
    """
    A class to securely store and manage sensitive database connection information using the keyring and cryptography libraries.

    This class provides methods to securely store, retrieve, and delete database authentication information using the keyring and cryptography libraries. The `store_credentials()` method can be used to store database connection information as a dictionary containing the driver, tcpip_commlinks, database_name, autocommit, username, and password. The password is encrypted using AES-256 in CBC mode, and the encryption key is stored in the keyring. The `get_credentials()` method retrieves the stored authentication information and decrypts the password using the stored encryption key. The `delete_credentials()` method deletes the stored authentication information from the keyring.

    Attributes
    ----------
    app_name : str
        A unique identifier for your application or script.
    encryption_key : str
        A password used to encrypt and decrypt sensitive data.

    Methods
    -------
    store_credentials(**kwargs) -> None:
        Store the database connection information securely.
    delete_credentials() -> None:
        Delete the stored database connection information.
    get_credentials() -> dict or None:
        Retrieve the stored database connection information.

    Example
    -------
    >>> from secure_storage import CredentialsManager

    >>> # Create a CredentialsManager instance with app_name "my_app"
    >>> credentials_manager = CredentialsManager("my_app")

    >>> # Store database connection information securely
    >>> credentials_manager.store_credentials(
            driver="ODBC Driver 17 for SQL Server",
            tcpip_commlinks="host=example.com,port=1433",
            database_name="my_database",
            autocommit=True,
            username="my_username",
            password="my_password"
        )

    >>> # Retrieve the stored database connection information
    >>> connection_info = credentials_manager.get_credentials()
    >>> print(connection_info)

    >>> # Delete the stored database connection information
    >>> credentials_manager.delete_credentials()

    Dependencies
    ------------
    - cryptography
    - keyring
    """

    def __init__(self, app_name, encryption_key=None):
        self.app_name = app_name
        self.encryption_key = encryption_key

        # If no encryption key is provided, generate a random one
        if self.encryption_key is None:
            self.encryption_key = generate_password()
            print(f"Generated encryption key: {self.encryption_key}")

        # Store the encryption key in the keyring
        keyring.set_password(self.app_name, "encryption_key", self.encryption_key)

    def store_credentials(self, **kwargs):
        """
        Store the database connection information securely.

        Parameters
        ----------
        **kwargs : keyword arguments
            Keyword arguments containing the connection information for the database.
            The keyword arguments should have the following keys: driver, tcpip_commlinks,
            database_name, autocommit, username, and password.

        Returns
        -------
        None

        """
        # Check if database authentication is already saved
        if keyring.get_password(self.app_name, "connection_info") is not None:
            print("Database authentication already saved.")
            delete_auth = input("Do you want to delete and save again? (y/n): ")
            if delete_auth.lower() == "y":
                # Delete the saved authentication
                keyring.delete_password(self.app_name, "connection_info")
            else:
                return

        # Encrypt and store the database authentication
        encrypted_auth = {}
        for key, value in kwargs.items():
            if key == "password":
                encrypted_auth[key] = encrypt(value, self.encryption_key)
            else:
                encrypted_auth[key] = value

        keyring.set_password(self.app_name, "connection_info", str(encrypted_auth))

    def delete_credentials(self):
        """
        Delete the stored database connection information.

        Returns
        -------
        None

        """
        keyring.delete_password(self.app_name, "connection_info")
        print(f"Deleted stored authentication for {self.app_name}.")

    def get_credentials(self):
        """
        Retrieve the stored database connection information.

        Returns
        -------
        dict or None
            The decrypted connection information as a dictionary with keys: driver, tcpip_commlinks,
            database_name, autocommit, username, and password, or None if no stored authentication is found.

        """
        encrypted_auth = keyring.get_password(self.app_name, "connection_info")
        if encrypted_auth is not None:
            decrypted_auth = {}
            for key, value in eval(encrypted_auth).items():
                if key == "password":
                    decrypted_auth[key] = decrypt(value, self.encryption_key)
                else:
                    decrypted_auth[key] = value
            return decrypted_auth
        else:
            return None


class DatabaseManager:
    """
    A class to manage database connections and securely execute SQL queries using stored credentials.

    This class provides a simple interface for connecting to a database using credentials managed by
    the `CredentialsManager` class. The `connect()` method establishes a connection to the database
    using the stored credentials, and the `execute_query()` method allows you to execute SQL queries
    and retrieve results. The `close()` method closes the active database connection. The
    `execute_query()` method can return results as a list of tuples or as a Pandas DataFrame,
    depending on the value of the `dataframe_output` parameter.

    Attributes
    ----------
    credentials_manager : CredentialsManager
        An instance of the CredentialsManager class used to securely manage database connection
        credentials.
    connection : pyodbc.Connection or None
        The active database connection, or None if no connection is established.

    Methods
    -------
    connect() -> None:
        Connect to the database using the stored credentials.
    execute_query(query: str, dataframe_output: bool = False) -> Union[List[Dict], pd.DataFrame, None]:
        Execute a SQL query using the open database connection and return the results either as a
        list of tuples or as a Pandas DataFrame, depending on the value of `dataframe_output`.
    close() -> None:
        Close the open database connection.

    Example
    -------
    >>> from secure_storage import DatabaseManager

    >>> # Create a DatabaseManager instance with app_name "my_app"
    >>> db_manager = DatabaseManager("my_app")

    >>> # Connect to the database
    >>> db_manager.connect()

    >>> # Execute a SQL query and return the results as a list of tuples
    >>> query = "SELECT * FROM my_table"
    >>> results = db_manager.execute_query(query)
    >>> print(results)

    >>> # Execute a SQL query and return the results as a Pandas DataFrame
    >>> query = "SELECT * FROM my_table"
    >>> results = db_manager.execute_query(query, dataframe_output=True)
    >>> print(results)

    >>> # Close the database connection
    >>> db_manager.close()

    Dependencies
    ------------
    - pyodbc
    - pandas

    Notes
    -----
    - The `execute_query()` method should be used for SELECT queries. For other types of queries
      (INSERT, UPDATE, DELETE), consider using other methods or libraries specifically designed for
      handling those operations.
    - The `execute_query()` method should not be used to execute potentially unsafe SQL queries,
      especially if the query is constructed using user-provided input. Always validate and sanitize
      user input to prevent SQL injection attacks.
    - The `connect()` method will raise an exception if the stored credentials are incorrect or if
      the database is not accessible. Make sure to handle these exceptions in your application code.
    """

    def __init__(self, app_name: str, encryption_key: Optional[str] = None):
        self.credentials_manager = CredentialsManager(app_name, encryption_key)
        self.connection = None

    def connect(self):
        """
        Connect to the database using the stored credentials.

        Returns
        -------
        None

        """
        credentials = self.credentials_manager.get_credentials()

        if credentials is None:
            raise ValueError("No stored credentials found.")

        driver = credentials.get("driver")
        tcpip_commlinks = credentials.get("tcpip_commlinks")
        database_name = credentials.get("database_name")
        autocommit = credentials.get("autocommit")
        username = credentials.get("username")
        password = credentials.get("password")

        connection_string = f"{driver}={tcpip_commlinks};DatabaseName={database_name};autocommit={autocommit}"
        self.connection = pyodbc.connect(connection_string, uid=username, pwd=password)

    def execute_query(
        self, query: str, dataframe_output: bool = True
    ) -> Union[List[Tuple], pd.DataFrame]:
        """
        Execute a SQL query using the open database connection and return the results as a list of tuples
        or a Pandas DataFrame.

        Parameters
        ----------
        query : str
            The SQL query to be executed.
        dataframe_output : bool, optional
            If True, the results will be returned as a Pandas DataFrame. Otherwise, the results will be
            returned as a list of tuples. Default is True.

        Returns
        -------
        Union[List[Tuple], pd.DataFrame]
            The results of the query as a list of tuples or a Pandas DataFrame, depending on the
            dataframe_output parameter.

        """
        if self.connection is None:
            raise ValueError(
                "No open connection found. Please connect to the database first."
            )

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            column_names = [column[0] for column in cursor.description]
            rows = cursor.fetchall()

        if dataframe_output:
            return pd.DataFrame(rows, columns=column_names)
        else:
            return rows

    def close(self):
        """
        Close the open database connection.

        Returns
        -------
        None

        """
        if self.connection is not None:
            self.connection.close()
            self.connection = None
