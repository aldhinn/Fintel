#!/usr/bin/python

from flask import Response, jsonify, request
from utils.flask_app import flask_app, AssetEntry, db, AssetsTable

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

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])