#!/usr/bin/python

from flask import Response, jsonify, request
from utils.data import analyze_assets_from_list
from utils.flask_app import flask_app, AssetEntry, db, AssetsTable
from concurrent.futures import ThreadPoolExecutor

# ThreadPoolExecutor instance for handling concurrent tasks
executor = ThreadPoolExecutor()

@flask_app.route("/assets", methods=["GET"])
def get_assets() -> Response:
    """Get the list of financial assets to be analyzed.

    Returns:
        Response: The response json containing the list of asset names analyzed.
    """

    # Query only the "name" column with active status.
    asset_names = AssetsTable.query.with_entities(AssetEntry.name).filter_by(status="active").all()
    # Format the result as a list of names
    asset_names_list = [name[0] for name in asset_names]
    return jsonify({"assets": asset_names_list})

@flask_app.route("/request", methods=["POST"])
def post_request() -> Response:
    """Request for an asset to be analyzed.

    Returns:
        Response: The response json containing whether the request was successful and\
            the accompanying error message when it's not successful.
    """

    # Retrieve the json request object.
    asset_names_list = request.get_json()

    if isinstance(asset_names_list, list): # Check if this is a list object.
        if not asset_names_list:
            return jsonify({
                "success": False,
                "message": "Provided empty asset names list."
            })

        # Iterate over the asset names to check for invalid values.
        for asset_name in asset_names_list:
            if not isinstance(asset_name, str):
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": f"Invalid asset name value: {asset_name}"
                })

            # Check if the username already exists
            existing_user = AssetsTable.query.filter_by(name=asset_name).first()
            if existing_user:
                # Continue to the next entry.
                continue

            # Construct the database model.
            new_asset_entry = AssetEntry(name=asset_name, status="pending")
            # Add to the database.
            db.session.add(new_asset_entry)

        try:
            # Commit everything that was just done to the live database.
            db.session.commit()
            # Run on the background.
            executor.submit(analyze_assets_from_list, asset_names_list)

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
            "message": "The requested asset names must be sent via a list of strings."
        })

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])