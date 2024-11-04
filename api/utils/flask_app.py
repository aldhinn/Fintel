#!/usr/bin/python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from utils.config import Config
from concurrent.futures import ThreadPoolExecutor

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
    AssetDbEntry = Base.classes.assets
    PricePointDbEntry = Base.classes.price_points

class AssetsDbTable(db.Model):
    """The model to the assets table.
    """

    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(100), nullable=False)

class PricePointsDbTable(db.Model):
    """The model to the price_points table.
    """

    __tablename__ = "price_points"
    id = db.Column(db.Integer, primary_key=True)

# ThreadPoolExecutor instance for handling concurrent tasks
threadExecutor = ThreadPoolExecutor()