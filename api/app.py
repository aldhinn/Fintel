#!/usr/bin/python

from flask import Response, jsonify, request
from utils.data import analyze_symbols_from_list
from utils.flask_app import flask_app, AssetDbEntry, db, AssetsDbTable, PricePointsDbTable
import threading

@flask_app.route("/symbols", methods=["GET"])
def get_symbols() -> Response:
    """Get the list of financial asset symbols to be analyzed.

    Returns:
        Response: The response json containing the list of asset symbols analyzed.
    """

    # Query only the "symbol" column with active processing status.
    asset_symbols = AssetsDbTable.query.with_entities(AssetDbEntry.symbol).filter_by(processing_status="active").all()
    # Format the result as a list of asset symbols
    asset_symbols_list = [symbol[0] for symbol in asset_symbols]
    return jsonify({"symbols": asset_symbols_list})

@flask_app.route("/request", methods=["POST"])
def post_request() -> Response:
    """Request for a asset symbol to be analyzed.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful.
    """

    # Retrieve the json request object.
    requested_asset_symbols_list = request.get_json()

    if isinstance(requested_asset_symbols_list, list): # Check if this is a list object.
        if not requested_asset_symbols_list:
            return jsonify({
                "success": False,
                "message": "Provided empty asset symbols list."
            })

        asset_symbols_to_be_analyzed:list[str] = []

        # Iterate over the asset symbols to check for invalid values.
        for requested_asset_symbol in requested_asset_symbols_list:
            if not isinstance(requested_asset_symbol, str):
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Invalid asset symbol value: {requested_asset_symbol}"
                })

            # Check if the asset symbol already exists
            queried_symbol_entry = AssetsDbTable.query.filter_by(symbol=requested_asset_symbol).first()
            if queried_symbol_entry:
                # Continue to the next entry.
                continue

            # Construct the database model.
            new_asset_symbol_entry = AssetDbEntry(symbol=requested_asset_symbol, processing_status="pending")
            # Add to the database.
            db.session.add(new_asset_symbol_entry)
            # Add to the list to be analyzed.
            asset_symbols_to_be_analyzed.append(requested_asset_symbol)

        try:
            # Commit everything that was just done to the live database.
            db.session.commit()
            # Run on the background.
            threading.Thread(target=analyze_symbols_from_list, args=(asset_symbols_to_be_analyzed,)).run()

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
            "message": "The requested asset symbols must be sent via a list of strings."
        })

@flask_app.route("/data", methods=["POST"])
def post_data() -> Response:
    """The endpoint to obtain price data of the asset symbol.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful. It also contains\
            the array of price points.
    """

    data = request.get_json()
    # The request should come as an object.
    if isinstance(data, list):
        return jsonify({
            "success": False,
            "message": "Request should come as an object."
        })

    symbol = data.get('symbol')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    # Validate the required fields
    if symbol is None or start_date is None or end_date is None:
        return jsonify({
            "success": False,
            "message": "The fields symbol, start_date, and end_date are required."
        })

    # The data should come as strings.
    if not isinstance(symbol, str) or not isinstance(start_date, str) or not isinstance(end_date, str):
        return jsonify({
            "success": False,
            "message": "Data provided should all be strings."
        })

    try:
        # Retrieve the asset id from the database.
        asset_entry = AssetsDbTable.query.with_entities(AssetDbEntry.id).filter_by(symbol=symbol).first()
        if asset_entry is None:
            return jsonify({
                "success": False,
                "message": "The symbol does not exist in the database."
            })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve asset entries with exception: {e}"
        })

    try:
        price_point_entries = PricePointsDbTable.query.filter(
            PricePointsDbTable.asset_id==asset_entry.id,
            PricePointsDbTable.date >= start_date,
            PricePointsDbTable.date <= end_date
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

        return jsonify({
            "success": True,
            "prices": price_data
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve price point entries with exception: {e}"
        })

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])