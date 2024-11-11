#!/usr/bin/python

def _get_secret(secret_name:str) -> str:
    """Read database credentials from Docker secrets files.

    Args:
        secret_name (str): The name of the secret to be obtained.

    Returns:
        str | None: The secret value in string.
    """

    try:
        # Attempt to open the file for the secret.
        with open(f"secrets/{secret_name}", "r") as secret_file:
            return secret_file.read().strip()
    except IOError:
        # Print error message.
        print(f"Failed to retrieve secret: {secret_name}")
        print(f"It is likely that the secret file secrets/{secret_name} doesn't exist.")
        return ""

# Configure SQLAlchemy with credentials from secrets
_db_user = _get_secret("db_user")
_db_password = _get_secret("db_password")
_db_host = _get_secret("db_host")
_db_port = 5432

import os

from flask import Flask

class Config:
    """The configuration class of the application.
    """
    SQLALCHEMY_DATABASE_URI:str = f"postgresql://{_db_user}:{_db_password}@{_db_host}:{_db_port}/fintel-db"
    SQLALCHEMY_TRACK_MODIFICATIONS:bool = False
    PORT:int = int(os.getenv("SERVICE_PORT", "61000"))


# Create the flask application instance.
flask_app = Flask(__name__)