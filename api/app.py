#!/usr/bin/python

from flask import Response, jsonify, request
from utils.data import analyze_symbols_from_list
from utils.flask_app import flask_app, AssetDbEntry, db, AssetsDbTable
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

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])