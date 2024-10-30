#!/usr/bin/python

from flask import Flask, Response, jsonify

# Create the flask application instance.
flask_app = Flask(__name__)

# Configure the flask app.
from config import Config
flask_app.config.from_object(Config)

from utils.db import Assets

@flask_app.route("/assets", methods=["GET"])
def get_assets() -> Response:
    """Get the list of financial assets to be analyzed.

    Returns:
        Response: The response json.
    """

    # Query only the 'name' column
    asset_names = Assets.query.with_entities(Assets.name).all()
    # Format the result as a list of names
    asset_names_list = [name[0] for name in asset_names]
    return jsonify({"assets": asset_names_list})

if __name__ == "__main__":
    from utils.db import db
    db.init_app(flask_app)
    flask_app.run(host="0.0.0.0", port=flask_app.config["PORT"])