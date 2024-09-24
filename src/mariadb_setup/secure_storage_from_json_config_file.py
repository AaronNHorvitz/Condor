"""
This Python module contains the classes and functions for managing and using encrypted credentials.

Classes
-------
DBConnect:
    A class that handles connection to a database using provided credentials.

CredentialsManager:
    A class that manages encryption, storage, retrieval, and deletion of credentials.

Functions
---------
derive_key(encryption_key: str, salt: bytes) -> bytes:
    Derive a cryptographic key from a password and a salt using PBKDF2HMAC.

encrypt(encryption_key: str, data: str) -> str:
    Encrypt the provided data using AES encryption and GCM mode.

decrypt(encryption_key: str, token: str) -> str:
    Decrypt the provided data using AES encryption and GCM mode.
"""

import os
import json
import getpass
import secrets
import string
import pyodbc
import pandas as pd
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class DBConnect:
    def __init__(self, credentials):

        """
        Constructs the necessary attributes for the DBConnect object.

        Parameters
        ----------
        credentials : dict
            The credentials used to establish the connection. This should include keys for 'configuration', 'uid', and 'password'.
        """
        self.credentials = credentials

    def connect(self) -> pyodbc.connect:
        """
        Establishes a connection to the database using the provided credentials.

        Returns
        -------
        pyodbc.connect
            The connection object to the database.

        Raises
        ------
        ValueError
            If any necessary keys are missing in the credentials dictionary.
        """
        # Check for necessary keys in credentials
        necessary_keys = ["configuration", "uid", "password"]
        for key in necessary_keys:
            if key not in self.credentials:
                raise ValueError(f"Key '{key}' not found in credentials")

        configuration = self.credentials["configuration"]
        if "0" not in configuration:
            raise ValueError("Key '0' not found in configuration")

        config_keys = ["driver", "commlinks", "server_name", "database", "autoc/ommit"]
        for key in config_keys:
            if key not in configuration["0"]:
                raise ValueError(f"Key '{key}' not found in configuration['0']")

        # Connection Info
        driver = configuration["0"]["driver"]
        commlinks = configuration["0"]["commlinks"]
        server_name = configuration["0"]["server_name"]
        database_name = configuration["0"]["database"]
        autocommit = configuration["0"]["autocommit"]
        user_name = self.credentials["uid"]
        password = self.credentials["password"]

        # Connection String
        connection_info = (
            f"DRIVER={driver};"
            f"SERVER={server_name};"
            f"DATABASE={database_name};"
            f"UID={user_name};"
            f"PWD={password};"
            f"autocommit={autocommit}"
        )

        return pyodbc.connect(connection_info)


class CredentialsManager:
    def __init__(self, app_name):
        self.app_name = app_name
        self.encryption_key = None
        self.config_file = f"{self.app_name}_config.json"
        self.generate_key()

    @staticmethod
    def generate_random_string(length: int = 50) -> str:
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(characters) for _ in range(length))

    def generate_key(self):
        self.encryption_key = self.generate_random_string()
        print(
            f"Please store your encryption key in a safe place. Here is the key: {self.encryption_key}"
        )

    def add_key(self):
        new_key = getpass.getpass("Enter a new encryption key: ")
        if self.encryption_key is not None:
            print("Existing encryption key has been replaced.")
        else:
            print("Encryption key has been added.")
        self.encryption_key = new_key

    def store_credentials(self, credentials):
        encrypted_auth = encrypt(self.encryption_key, json.dumps(credentials))
        with open(self.config_file, "w") as f:
            f.write(encrypted_auth)

    def delete_credentials(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
            print(f"Deleted stored authentication for {self.app_name}.")
        else:
            print(f"No stored authentication found for {self.app_name}.")

    def get_credentials(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                encrypted_auth = f.read()

            decrypted_auth = json.loads(decrypt(self.encryption_key, encrypted_auth))

            return decrypted_auth
        else:
            return None


backend = default_backend()


def derive_key(encryption_key: str, salt: bytes) -> bytes:
    """
    Derive a cryptographic key from a password and a salt using PBKDF2HMAC.

    Parameters
    ----------
    encryption_key : str
        The encryption key to be used.
    salt : bytes
        The salt to be used in the key derivation function.

    Returns
    -------
    bytes
        The derived cryptographic key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=backend,
    )

    return kdf.derive(encryption_key.encode())


def encrypt(encryption_key: str, data: str) -> str:
    """
    Encrypt the provided data using AES encryption and GCM mode.

    Parameters
    ----------
    encryption_key : str
        The encryption key to be used.
    data : str
        The data to be encrypted.

    Returns
    -------
    str
        The encrypted data encoded as a URL-safe base64 string.
    """
    salt = os.urandom(16)
    key = derive_key(encryption_key, salt)
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data.encode()) + encryptor.finalize()

    # Get the authentication tag
    tag = encryptor.tag

    return base64.urlsafe_b64encode(salt + iv + tag + ct).decode()


def decrypt(encryption_key: str, token: str) -> str:
    """
    Decrypt the provided data using AES encryption and GCM mode.

    Parameters
    ----------
    encryption_key : str
        The encryption key to be used.
    token : str
        The encrypted data encoded as a URL-safe base64 string.

    Returns
    -------
    str
        The decrypted data.
    """
    data = base64.urlsafe_b64decode(token.encode())
    salt, iv, tag, ct = data[:16], data[16:28], data[28:44], data[44:]
    key = derive_key(encryption_key, salt)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    return (decryptor.update(ct) + decryptor.finalize()).decode()
