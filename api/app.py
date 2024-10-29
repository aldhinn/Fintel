#!/usr/bin/python

from flask import Flask
import os

# Create the flask application instance.
flask_app = Flask(__name__)

# The directory of this file.
app_dirpath = os.path.dirname(os.path.abspath(__file__))

# Configure the flask app.
from config import Config
flask_app.config.from_object(Config)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])