#!/usr/bin/python

from abc import ABC, abstractmethod
import threading
from typing import Any, Literal
from flask import Flask
import yfinance as yf
from yfinance import Ticker
from pandas import DataFrame
from sqlalchemy.orm import Session
from utils.constants import API_ENDPOINT_DATA, API_ENDPOINT_APPEND,\
    API_ENDPOINT_SYMBOLS
from utils.db_models import AssetsDbTable, PricePointsDbTable

class BaseRequestHandler(ABC):
    """The base request handler type.
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any) -> None:
        """Default constructor.

        Args:
            db_session (Session | Any): The object that manages the database session.
            flask_app (Flask | Any): The flask application reference.
        """

        self._db_session = db_session
        self._flask_app = flask_app

    @abstractmethod
    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"] = "GET",\
            request:dict|list={}) -> tuple[dict|list, int]:
        """Process the request provided.

        Args:
            method:Literal["GET", "POST", "PUT", "DELETE"]: The Rest API\
                request method.
            request (dict | list, optional): The object containing the\
                request information.

        Returns:
            tuple[dict | list, int]: The tuple of response object and the\
                status code.
        """

class _SymbolsHandler(BaseRequestHandler):
    """Get request handler for route `API_ENDPOINT_SYMBOLS`
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any) -> None:
        super().__init__(db_session=db_session, flask_app=flask_app)

    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"],\
            _:dict|list = {}) -> tuple[dict|list, int]:

        if method == "GET":
            # Query only the "symbol" column with active processing status.
            asset_symbols = self._db_session.query(AssetsDbTable.symbol).\
                filter_by(processing_status="active").all()
            # Format the result as a list of asset symbols
            asset_symbols_list = [symbol[0] for symbol in asset_symbols]

            return {"symbols": asset_symbols_list}, 200

        else:
            return {}, 204 # Returning an empty response.

class _AppendHandler(BaseRequestHandler):
    """Get request handler for route `API_ENDPOINT_APPEND`
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any) -> None:
        super().__init__(db_session=db_session, flask_app=flask_app)

    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"],\
            request:dict|list) -> tuple[dict|list, int]:

        if method == "POST":
            if isinstance(request, list): # Check if this is a list object.
                if not request:
                    return {
                        "error": "Provided empty asset symbols list."
                    }, 400

                asset_symbols_to_be_analyzed:list[str] = []

                # Iterate over the asset symbols to check for invalid values.
                for requested_asset_symbol in request:
                    if not isinstance(requested_asset_symbol, str):
                        self._db_session.rollback()
                        return {
                            "error": f"Invalid asset symbol value: {requested_asset_symbol}"
                        }, 400

                    # Check if the asset symbol already exists
                    queried_symbol_entry = self._db_session.query(AssetsDbTable).\
                        filter_by(symbol=requested_asset_symbol).first()
                    if queried_symbol_entry:
                        # Continue to the next entry.
                        continue

                    # Construct the database model.
                    new_asset_symbol_entry = AssetsDbTable(\
                        symbol=requested_asset_symbol, processing_status="pending")
                    # Add to the database.
                    self._db_session.add(new_asset_symbol_entry)
                    # Add to the list to be analyzed.
                    asset_symbols_to_be_analyzed.append(requested_asset_symbol)

                try:
                    # Commit everything that was just done to the live database.
                    self._db_session.commit()
                    # Run on the background.
                    threading.Thread(target=self._analyze_symbols_from_list,\
                        args=(asset_symbols_to_be_analyzed,)).run()

                    return {}, 204

                except Exception as e:
                    self._db_session.rollback()
                    return {
                        "error": f"Registration failed with error: {e}"
                    }, 500

            else:
                return {
                    "error": "The requested asset symbols must be sent via a list of strings."
                }, 400

        else:
            return {}, 204 # Returning an empty response.

    def _analyze_symbols_from_list(self, asset_symbols_list:list[str]) -> None:
        """Analyze the list of symbol names specified.

        Args:
            asset_symbols_list (list[str]): The list of asset symbols to be analyzed.
        """

        for asset_symbol in asset_symbols_list:
            self._fetch_from_yahoo_finance(asset_symbol=asset_symbol)

    def _fetch_from_yahoo_finance(self, asset_symbol:str) -> None:
        """Fetch data from yahoo finance and store in the database.

        Args:
            asset_symbol (str): The symbol of the asset to be retrieved online.
        """

        with self._flask_app.app_context():
            try:
                # Retrieve the asset id from the database.
                asset_id = self._db_session.query(AssetsDbTable.id).\
                    filter_by(symbol=asset_symbol).first().id
            except Exception as e:
                print(f"Failed to retrieve asset id with message: {e}")
                return

            try:
                # Fetch all historical data.
                data:DataFrame|None = yf.download(asset_symbol)
            except Exception as e:
                print(f"Failed to download from yahoo finance with message: {e}")
                return

            # Halt from here on if retrieved nothing.
            if data is None:
                return

            # Reset index to turn the date into a column
            data.reset_index(inplace=True)
            # Prepare the DataFrame
            df_price_history = data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]].copy()
            df_price_history.columns = ["date", "open_price", "high_price", "low_price", "close_price", "adjusted_close", "volume"]

            try:
                # Iterate over the data frame to be stored in the database.
                for _, row in df_price_history.iterrows():
                    price_record = PricePointsDbTable(
                        asset_id=asset_id,
                        date=row["date"],
                        open_price=row["open_price"],
                        close_price=row["close_price"],
                        high_price=row["high_price"],
                        low_price=row["low_price"],
                        adjusted_close=row["adjusted_close"],
                        volume=row["volume"],
                        source="yahoo_finance",
                    )
                    self._db_session.add(price_record)
                self._db_session.commit()
            except Exception as e:
                print(f"Error in submitting price point entries: {e}")
                self._db_session.rollback()
                return

            try:
                # Fetch metadata.
                metadata:dict = Ticker(asset_symbol).info
                # The reference to the asset entry in the database.
                ref_asset_entry = self._db_session.query(AssetsDbTable).get(asset_id)
                description = metadata.get("longName", "Description not available")

                # Update asset entry.
                ref_asset_entry.processing_status = "active"
                ref_asset_entry.description = description

                self._db_session.commit()
            except Exception as e:
                self._db_session.rollback()
                print(f"Failed to update asset entry with exception: {e}")

class _DataHandler(BaseRequestHandler):
    """Get request handler for route `API_ENDPOINT_DATA`
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any) -> None:
        super().__init__(db_session=db_session, flask_app=flask_app)

    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"],\
            request:dict|list) -> tuple[dict|list, int]:

        if method == "GET":
            # The request should be an object.
            if isinstance(request, list):
                return {
                    "error": "Request should be an object."
                }, 400

            symbol = request.get('symbol')
            start_date = request.get('start_date')
            end_date = request.get('end_date')

            # Validate the required fields
            if symbol is None or start_date is None or end_date is None:
                return {
                    "error": "The fields symbol, start_date, and end_date are required."
                }, 400

            try:
                # Collect all columns from PricePointsDbTable except `source`
                price_point_columns = [col for col in PricePointsDbTable.__table__.columns\
                    if col.name != "source"]
                joint_entries = self._db_session.\
                    query(AssetsDbTable.id, AssetsDbTable.description, *price_point_columns).\
                    join(AssetsDbTable, PricePointsDbTable.asset_id == AssetsDbTable.id).\
                        filter(AssetsDbTable.symbol==symbol,\
                            PricePointsDbTable.date >= start_date,\
                            PricePointsDbTable.date <= end_date\
                    ).all()

                # Convert prices to an array of dictionaries
                price_data = [
                    {
                        "date": record.date.strftime("%Y-%m-%d"),
                        "open_price": record.open_price,
                        "close_price": record.close_price,
                        "high_price": record.high_price,
                        "low_price": record.low_price,
                        "adjusted_close": record.adjusted_close,
                        "volume": record.volume
                    } for record in joint_entries
                ]

                return {
                    "description": joint_entries[0].description,
                    "prices": price_data
                }, 200

            except Exception as e:
                self._db_session.rollback()
                return {
                    "error": f"Failed to retrieve price point entries with exception: {e}"
                }, 500
        else:
            return {}, 204 # Returning an empty response.

class RequestHandlerFactory:
    """The object that creates a request handler.
    """

    @staticmethod
    def create_handler(end_point:str, db_session:Session|Any, flask_app:Flask|Any) -> BaseRequestHandler:
        """Creates a handler based on the route.

        Args:
            end_point (str): The name of the API route endpoint.
            db_session (Session | Any): The object that manages\
                the database session.

        Returns:
            BaseRequestHandler: The instance to a request handler object.
        """

        handlerTypeDict = {
            API_ENDPOINT_SYMBOLS: _SymbolsHandler,
            API_ENDPOINT_APPEND: _AppendHandler,
            API_ENDPOINT_DATA: _DataHandler
        }

        try:
            # Attempt instantiating handler.
            handler = handlerTypeDict[end_point](db_session, flask_app)
            return handler
        except Exception:
            # Return the base class if `endpoint` is invalid.
            return BaseRequestHandler()