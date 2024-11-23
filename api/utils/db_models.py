from utils.config import flask_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM, BYTEA

database = SQLAlchemy(flask_app)

asset_status_type = ENUM("active", "pending", name="asset_status_type")
asset_category_type = ENUM("stock", "bond", "forex", "crypto", name="asset_category_type")
data_source_type = ENUM("yahoo_finance", "alpha_vantage", name="data_source_type")
prediction_type_enum = ENUM(
    "open_price", "high_price", "low_price", "close_price", "adjusted_close", "volume",
    name="prediction_type_enum"
)

class CurrenciesDbTable(database.Model):
    """
    Represents a currency in the system.

    Attributes:
        id (int): Primary key, unique identifier for the currency.
        symbol (str): Unique symbol representing the currency (e.g., "USD").
        description (str): Description of the currency (e.g., "US Dollar").
    """
    __tablename__ = "currencies"

    id = database.Column(database.Integer, primary_key=True)  # Unique identifier for the currency
    symbol = database.Column(database.String(10), unique=True, nullable=False)  # Currency symbol
    description = database.Column(database.String(50))  # Description of the currency

class AssetsDbTable(database.Model):
    """
    Represents a financial asset in the system.

    Attributes:
        id (int): Primary key, unique identifier for the asset.
        symbol (str): Unique symbol for the asset (e.g., "AAPL").
        description (str): Optional description of the asset.
        processing_status (str): Status of the asset ("active" or "pending").
        category (str): The category of the asset ("stock", "bond", "forex", "crypto").
        currency_medium (str): Symbol of the currency used for this asset (foreign key to currencies.symbol).
    """
    __tablename__ = "assets"

    id = database.Column(database.Integer, primary_key=True)  # Unique identifier for the asset
    symbol = database.Column(database.String(15), unique=True, nullable=False)  # Asset symbol
    description = database.Column(database.String(50))  # Optional description of the asset
    processing_status = database.Column(asset_status_type, nullable=False, default="pending")  # Status of the asset
    category = database.Column(asset_category_type)  # Category of the asset
    currency_medium = database.Column(database.String(10), database.ForeignKey("currencies.symbol"))  # Currency used for this asset

class PricePointsDbTable(database.Model):
    """
    Represents a price point for a financial asset.

    Attributes:
        id (int): Primary key, unique identifier for the price point.
        asset_id (int): Foreign key linking to an asset.
        date (date): Date of the price point.
        open_price (Decimal): Opening price of the asset.
        close_price (Decimal): Closing price of the asset.
        high_price (Decimal): Highest price of the asset during the day.
        low_price (Decimal): Lowest price of the asset during the day.
        adjusted_close (Decimal): Adjusted closing price.
        volume (int): Trading volume.
        source (str): Source of the data ("yahoo_finance", "alpha_vantage").
    """
    __tablename__ = "price_points"

    id = database.Column(database.Integer, primary_key=True)  # Unique identifier for the price point
    asset_id = database.Column(database.Integer, database.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)  # Linked asset ID
    date = database.Column(database.Date, nullable=False)  # Date of the price point
    open_price = database.Column(database.Numeric(12, 4), nullable=False)  # Opening price
    close_price = database.Column(database.Numeric(12, 4), nullable=False)  # Closing price
    high_price = database.Column(database.Numeric(12, 4), nullable=False)  # Highest price
    low_price = database.Column(database.Numeric(12, 4), nullable=False)  # Lowest price
    adjusted_close = database.Column(database.Numeric(12, 4))  # Adjusted closing price
    volume = database.Column(database.BigInteger)  # Trading volume
    source = database.Column(data_source_type, nullable=False)  # Source of the data

    __table_args__ = (
        database.UniqueConstraint("asset_id", "date", "source", name="unique_asset_date_source"),
    )

class AIModelsDbTable(database.Model):
    """
    Represents an AI model used for predictions.

    Attributes:
        id (int): Primary key, unique identifier for the AI model.
        model_name (str): Unique name for the model.
        model_type (str): Type of the model (e.g., "LSTM").
        created_at (datetime): Timestamp when the model was created.
        model_data (bytes): Serialized model data.
        last_trained (datetime): Timestamp of the last training session.
    """
    __tablename__ = "ai_models"

    id = database.Column(database.Integer, primary_key=True)  # Unique identifier for the AI model
    model_name = database.Column(database.String(100), unique=True, nullable=False)  # Name of the model
    model_type = database.Column(database.String(100), nullable=False)  # Type of the model
    created_at = database.Column(database.DateTime, server_default=database.func.current_timestamp())  # Creation timestamp
    model_data = database.Column(BYTEA, nullable=False)  # Serialized model data
    last_trained = database.Column(database.DateTime)  # Timestamp of the last training

class PredictionsDbTable(database.Model):
    """
    Represents a prediction made by an AI model.

    Attributes:
        id (int): Primary key, unique identifier for the prediction.
        date (date): Date of the prediction.
        model_id (int): Foreign key linking to an AI model.
        prediction_type (str): Type of the prediction ("open_price", "high_price", etc.).
        prediction (Decimal): Predicted value.
        created_at (datetime): Timestamp when the prediction was created.
        retrained (bool): Indicates whether the prediction was retrained.
    """
    __tablename__ = "predictions"

    id = database.Column(database.Integer, primary_key=True)  # Unique identifier for the prediction
    asset_id = database.Column(database.Integer, database.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)  # Linked asset ID
    model_id = database.Column(database.Integer, database.ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False)  # Linked AI model ID
    date = database.Column(database.Date, nullable=False)  # Date of the prediction
    prediction_type = database.Column(prediction_type_enum, nullable=False)  # Type of the prediction
    prediction = database.Column(database.Numeric, nullable=False)  # Predicted value
    created_at = database.Column(database.DateTime, server_default=database.func.current_timestamp())  # Creation timestamp
    retrained = database.Column(database.Boolean, default=False)  # Indicates if retrained

    __table_args__ = (
        database.UniqueConstraint("asset_id", "model_id", "date", "prediction_type", name="unique_price_prediction"),
    )

def setup_database():
    """Sets up the database by creating all tables and pre-populating data.
    """

    with flask_app.app_context():
        database.create_all() # Create tables

        # List of currencies to populate
        currencies_data = [
            {"symbol": "USD", "description": "US Dollar"},
            {"symbol": "EUR", "description": "Euro"},
            {"symbol": "JPY", "description": "Japanese Yen"},
            {"symbol": "GBP", "description": "British Pound"},
            {"symbol": "AUD", "description": "Australian Dollar"},
            {"symbol": "CAD", "description": "Canadian Dollar"},
            {"symbol": "CHF", "description": "Swiss Franc"},
            {"symbol": "CNY", "description": "Chinese Yuan Renminbi"},
            {"symbol": "NZD", "description": "New Zealand Dollar"},
            {"symbol": "SEK", "description": "Swedish Krona"},
            {"symbol": "NOK", "description": "Norwegian Krone"},
            {"symbol": "MXN", "description": "Mexican Peso"},
            {"symbol": "SGD", "description": "Singapore Dollar"},
            {"symbol": "HKD", "description": "Hong Kong Dollar"},
            {"symbol": "KRW", "description": "South Korean Won"},
            {"symbol": "TRY", "description": "Turkish Lira"},
            {"symbol": "INR", "description": "Indian Rupee"},
            {"symbol": "RUB", "description": "Russian Ruble"},
            {"symbol": "ZAR", "description": "South African Rand"},
            {"symbol": "BRL", "description": "Brazilian Real"},
            {"symbol": "PHP", "description": "Philippine Peso"},
            {"symbol": "SAR", "description": "Saudi Riyal"},
        ]

        # Check and insert currencies only if table is empty
        for currency in currencies_data:
            if not database.session.query(CurrenciesDbTable.symbol).\
                    filter_by(symbol=currency["symbol"]).first():
                database.session.add(CurrenciesDbTable(**currency))
        database.session.commit()