#!/usr/bin/python

from flask import Response, jsonify, request
from utils.data import analyze_tickers_from_list
from utils.flask_app import flask_app, TickerEntry, db, TickersTable
from concurrent.futures import ThreadPoolExecutor

# ThreadPoolExecutor instance for handling concurrent tasks
executor = ThreadPoolExecutor()

@flask_app.route("/tickers", methods=["GET"])
def get_tickers() -> Response:
    """Get the list of financial tickers to be analyzed.

    Returns:
        Response: The response json containing the list of tickers analyzed.
    """

    # Query only the "name" column with active status.
    ticker_names = TickersTable.query.with_entities(TickerEntry.name).filter_by(status="active").all()
    # Format the result as a list of names
    ticker_names_list = [name[0] for name in ticker_names]
    return jsonify({"tickers": ticker_names_list})

@flask_app.route("/request", methods=["POST"])
def post_request() -> Response:
    """Request for a ticker to be analyzed.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful.
    """

    # Retrieve the json request object.
    requested_ticker_names_list = request.get_json()

    if isinstance(requested_ticker_names_list, list): # Check if this is a list object.
        if not requested_ticker_names_list:
            return jsonify({
                "success": False,
                "message": "Provided empty tickers list."
            })

        ticker_names_to_be_analyzed:list[str] = []

        # Iterate over the tickers to check for invalid values.
        for requested_ticker_name in requested_ticker_names_list:
            if not isinstance(requested_ticker_name, str):
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Invalid ticker name value: {requested_ticker_name}"
                })

            # Check if the username already exists
            existing_user = TickersTable.query.filter_by(name=requested_ticker_name).first()
            if existing_user:
                # Continue to the next entry.
                continue

            # Construct the database model.
            new_ticker_entry = TickerEntry(name=requested_ticker_name, status="pending")
            # Add to the database.
            db.session.add(new_ticker_entry)
            # Add to the list to be analyzed.
            ticker_names_to_be_analyzed.append(requested_ticker_name)

        try:
            # Commit everything that was just done to the live database.
            db.session.commit()
            # Run on the background.
            executor.submit(analyze_tickers_from_list, ticker_names_to_be_analyzed)

            return jsonify({"success": True})

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"Registration failed with error: {e}"
            })

    else:
        return jsonify({
            "success": False,
            "message": "The requested tickers must be sent via a list of strings."
        })

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])