#!/usr/bin/python

from abc import ABC, abstractmethod
import threading
from typing import Any, Literal

from flask_sqlalchemy import SQLAlchemy

from utils.constants import API_ENDPOINT_DATA, API_ENDPOINT_APPEND,\
    API_ENDPOINT_SYMBOLS
from utils.data import analyze_symbols_from_list
from utils.db_models import AssetsDbTable, PricePointsDbTable

class BaseRequestHandler(ABC):
    """The base request handler type.
    """

    def __init__(self, db_session:SQLAlchemy|Any) -> None:
        """Default constructor.

        Args:
            db_session (SQLAlchemy | Any): The object that manages\
                the database session.
        """

        self._db_session = db_session

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

    def __init__(self, db_session:SQLAlchemy|Any) -> None:
        super().__init__(db_session=db_session)

    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"],\
            request:dict|list = {}) -> tuple[dict|list, int]:

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

    def __init__(self, db_session:SQLAlchemy|Any) -> None:
        super().__init__(db_session=db_session)

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
                            "error": f"Invalid asset symbol value:\
                                {requested_asset_symbol}"
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
                    threading.Thread(target=analyze_symbols_from_list,\
                        args=(asset_symbols_to_be_analyzed,)).run()

                    return {"success": True}, 200

                except Exception as e:
                    self._db_session.rollback()
                    return {
                        "error": f"Registration failed with error: {e}"
                    }, 500

            else:
                return {
                    "error": "The requested asset symbols must be sent\
                        via a list of strings."
                }, 400

        else:
            return {}, 204 # Returning an empty response.

class _DataHandler(BaseRequestHandler):
    """Get request handler for route `API_ENDPOINT_DATA`
    """

    def __init__(self, db_session:SQLAlchemy|Any) -> None:
        super().__init__(db_session=db_session)

    def process(self, method:Literal["GET", "POST", "PUT", "DELETE"],\
            request:dict|list) -> tuple[dict|list, int]:

        if method == "POST":
            # The request should come as an object.
            if isinstance(request, list):
                return {
                    "error": "Request should come as an object."
                }, 400

            symbol = request.get('symbol')
            start_date = request.get('start_date')
            end_date = request.get('end_date')

            # Validate the required fields
            if symbol is None or start_date is None or end_date is None:
                return {
                    "error": "The fields symbol, start_date, and end_date are required."
                }, 400

            # The data should come as strings.
            if not isinstance(symbol, str) or not isinstance(start_date, str)\
                    or not isinstance(end_date, str):
                return {
                    "error": "Data provided should all be strings."
                }, 400

            try:
                # Retrieve the asset entry from the database.
                asset_entry = AssetsDbTable.query.filter_by(symbol=symbol).first()
                if asset_entry is None:
                    return {
                        "error": "The symbol does not exist in the database."
                    }, 404

            except Exception as e:
                self._db_session.rollback()
                return {
                    "error": f"Failed to retrieve asset entries with exception: {e}"
                }, 500

            try:
                price_point_entries = self._db_session.\
                    query(PricePointsDbTable).filter(\
                    PricePointsDbTable.asset_id==asset_entry.id,\
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
                    } for record in price_point_entries
                ]

                return {
                    "description": asset_entry.description,
                    "prices": price_data
                }, 200

            except Exception as e:
                self._db_session.rollback()
                return {
                    "error": f"Failed to retrieve price point\
                        entries with exception: {e}"
                }, 500
        else:
            return {}, 204 # Returning an empty response.

class RequestHandlerFactory:
    """The object that creates a request handler.
    """

    @staticmethod
    def create_handler(end_point:str, db_session:SQLAlchemy|Any) -> BaseRequestHandler:
        """Creates a handler based on the route.

        Args:
            end_point (str): The name of the API route endpoint.
            db_session (SQLAlchemy | Any): The object that manages\
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
            handler = handlerTypeDict[end_point](db_session)
            return handler
        except Exception:
            # Return the base class if `endpoint` is invalid.
            return BaseRequestHandler()