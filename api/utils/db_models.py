#!/usr/bin/python

from flask_sqlalchemy import SQLAlchemy

# The interface to the database session.
database = SQLAlchemy()

class AssetsDbTable(database.Model):
    """The model to the assets table.
    """

    __tablename__ = "assets"
    id = database.Column(database.Integer, primary_key=True)
    symbol = database.Column(database.String(15), nullable=False)
    processing_status = database.Column(database.Enum('active',\
        'pending', name='asset_status_type'), nullable=False)
    description = database.Column(database.String(50), nullable=True)

class PricePointsDbTable(database.Model):
    """The model to the price_points table.
    """

    __tablename__ = "price_points"
    id = database.Column(database.Integer, primary_key=True)
    asset_id = asset_id = database.Column(database.Integer,\
        database.ForeignKey('assets.id'), nullable=False)
    date = database.Column(database.Date, nullable=False)
    open_price = database.Column(database.Float, nullable=False)
    close_price = database.Column(database.Float, nullable=False)
    high_price = database.Column(database.Float, nullable=False)
    low_price = database.Column(database.Float, nullable=False)
    adjusted_close = database.Column(database.Float, nullable=True)
    volume = database.Column(database.BigInteger, nullable=True)
    source = database.Column(database.Enum('yahoo_finance',\
        'alpha_vantage', name='data_source_type'), nullable=False)