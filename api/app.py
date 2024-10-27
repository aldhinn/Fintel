#!/usr/bin/python

from flask import Flask, Blueprint

_main = Blueprint('main', __name__)

def main() -> None:
    """ The entry point of the application.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Register Blueprints
    app.register_blueprint(_main)
    app.run()

if __name__ == "__main__":
    main()