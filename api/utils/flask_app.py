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
    AssetDbEntry = Base.classes.assets
    PricePointDbEntry = Base.classes.price_points

class AssetsDbTable(db.Model):
    """The model to the assets table.
    """

    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(15), nullable=False)
    processing_status = db.Column(db.Enum('active', 'pending', name='ASSET_STATUS_TYPE'), nullable=False)
    description = db.Column(db.String(50), nullable=True)

class PricePointsDbTable(db.Model):
    """The model to the price_points table.
    """

    __tablename__ = "price_points"
    id = db.Column(db.Integer, primary_key=True)
    asset_id = asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    adjusted_close = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Integer, nullable=True)