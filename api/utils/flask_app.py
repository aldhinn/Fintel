#!/usr/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from utils.config import Config

# Create the flask application instance.
flask_app = Flask(__name__)
# Configure the flask app.
flask_app.config.from_object(Config)

# The database interface.
db = SQLAlchemy(flask_app)

# Reflect the existing database tables
Base = automap_base()
with flask_app.app_context():
    Base.prepare(db.engine, reflect=True)
    # Access reflected tables as classes
    TickerEntry = Base.classes.tickers

class TickersTable(db.Model):
    """The model to the tickers table.
    """
    __tablename__ = "tickers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)