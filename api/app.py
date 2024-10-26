#!/usr/bin/python

from utils.routes import create_app

def main() -> None:
    """ The entry point of the application.
    """

    app = create_app()
    app.run()

if __name__ == "__main__":
    main()