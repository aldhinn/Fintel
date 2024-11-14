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
    processing_status = database.Column(database.Enum("active",\
        "pending", name="asset_status_type"), nullable=False)
    description = database.Column(database.String(50), nullable=True)

class PricePointsDbTable(database.Model):
    """The model to the price_points table.
    """

    __tablename__ = "price_points"
    id = database.Column(database.Integer, primary_key=True)
    asset_id = asset_id = database.Column(database.Integer,\
        database.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    date = database.Column(database.Date, nullable=False)
    open_price = database.Column(database.Float, nullable=False)
    close_price = database.Column(database.Float, nullable=False)
    high_price = database.Column(database.Float, nullable=False)
    low_price = database.Column(database.Float, nullable=False)
    adjusted_close = database.Column(database.Float, nullable=True)
    volume = database.Column(database.BigInteger, nullable=True)
    source = database.Column(database.Enum("yahoo_finance",\
        "alpha_vantage", name="data_source_type"), nullable=False)

class PredictionTypeEnum(database.Enum):
    open_price = "open_price"
    high_price = "high_price"
    low_price = "low_price"
    close_price = "close_price"
    adjusted_close = "adjusted_close"
    volume = "volume"

class AIModel(database.Model):
    """Model for ai_models table
    """
    __tablename__ = "ai_models"

    id = database.Column(database.Integer, primary_key=True)
    model_name = database.Column(database.String(100), nullable=False, unique=True)
    model_type = database.Column(database.String(100), nullable=False)
    created_at = database.Column(database.TIMESTAMP, default="CURRENT_TIMESTAMP")
    model_data = database.Column(database.LargeBinary, nullable=False)  # Stores serialized model data
    last_trained = database.Column(database.TIMESTAMP)

class Prediction(database.Model):
    __tablename__ = "predictions"

    id = database.Column(database.Integer, primary_key=True)
    date = database.Column(database.Date, nullable=False)
    model_id = database.Column(database.Integer, database.ForeignKey("ai_models.id",\
        ondelete="CASCADE"), nullable=False)
    prediction_type = database.Column(database.Enum("high_price", "high_price",\
        "low_price", "close_price", "adjusted_close", "volume", name="prediction_type_enum"),\
        nullable=False)  # Enum type for prediction_type
    prediction = database.Column(database.Numeric, nullable=False)
    created_at = database.Column(database.TIMESTAMP, default="CURRENT_TIMESTAMP")
    retrained = database.Column(database.Boolean, default=False)