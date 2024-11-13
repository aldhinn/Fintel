#!/usr/bin/python

from flask import Response, jsonify, request
from utils.config import flask_app
from utils.constants import API_ENDPOINT_DATA,\
    API_ENDPOINT_APPEND, API_ENDPOINT_SYMBOLS
from utils.db_models import database

from utils.request_handlers import RequestHandlerFactory

@flask_app.route(API_ENDPOINT_SYMBOLS, methods=["GET"])
def api_symbols() -> tuple[Response, int]:
    """Get the list of financial asset symbols to be analyzed.

    Returns:
        Response: The response json containing the list of asset symbols analyzed.
    """

    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_SYMBOLS, database.session, flask_app)
    response, status_code = handler.process(method=request.method)

    return jsonify(response), status_code

@flask_app.route(API_ENDPOINT_APPEND, methods=["POST"])
def api_request() -> tuple[Response, int]:
    """Request for a asset symbol to be analyzed.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful.
    """

    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, database.session, flask_app)
    response, status_code = handler.process(\
        method=request.method, request=request.get_json())

    return jsonify(response), status_code

@flask_app.route(API_ENDPOINT_DATA, methods=["POST"])
def api_data() -> Response:
    """The endpoint to obtain price data of the asset symbol.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful. It also contains\
            the array of price points.
    """

    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, database.session, flask_app)
    response, status_code = handler.process(\
        method=request.method, request=request.get_json())

    return jsonify(response), status_code

database.init_app(flask_app)

# Run only if this script is executed directly. You'd only do that when debugging.
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"], debug=True)