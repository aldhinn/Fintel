#!/usr/bin/python

from flask import Flask, Blueprint

_main = Blueprint('main', __name__)

def create_app():
    """Create the Flask application.

    Returns:
        Flask: The application object.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Register Blueprints
    app.register_blueprint(_main)

    return app