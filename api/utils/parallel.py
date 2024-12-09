#!/usr/bin/python

from abc import ABC, abstractmethod
from datetime import date, timedelta
import threading
import time
from typing import Any
from flask import Flask
from pandas import DataFrame
from sqlalchemy.orm import Session
import yfinance as yf
from sqlalchemy.exc import IntegrityError

from utils.db_models import AssetsDbTable, PricePointsDbTable
from utils.lstm_model import train_lstm_model

class _BaseParallelTask(ABC):
    """The base type for a parallel task container.
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any) -> None:
        """Default constructor.

        Args:
            db_session (Session | Any): The object that manages the database session.
            flask_app (Flask | Any): The flask application reference.
        """

        self._db_session = db_session
        self._flask_app = flask_app
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True  # Ensures thread exits when the main program exits
        self._thread.start()

    @abstractmethod
    def _run(self):
        """The function containing the rask to run.
        """

class DataAndModelUpdater(_BaseParallelTask):
    """Updates the price points of all registered asset symbols.
    """

    def __init__(self, db_session:Session|Any, flask_app:Flask|Any, iterations:int|None = None) -> None:
        self._iterations = iterations
        super().__init__(db_session=db_session, flask_app=flask_app)

    def _run(self):
        count = 0
        while self._iterations is None or count < self._iterations:
            if self._iterations is not None:
                count += 1

            with self._flask_app.app_context():
                # Query only the "id" column with active processing status.
                active_assets = self._db_session.query(AssetsDbTable.id, AssetsDbTable.symbol).\
                    filter_by(processing_status="active").all()

                # Iterate over asset symbols.
                for asset_id, asset_symbol in active_assets:
                    today = date.today().strftime("%Y-%m-%d")
                    yesterday_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

                    self._fetch_from_yfinance(asset_id, asset_symbol, yesterday_date, today)
                    train_lstm_model(asset_id, self._db_session)

            print("Successfully updated price points. Updating again in the next 8 hours.")
            # Sleep the thread for the next 8 hours, which is:
            # 8 hours = 8 hours * (60 minutes / 1 hour) * (60 seconds / 1 minute) = 28800 seconds
            time.sleep(28800)

    def _fetch_from_yfinance(self, asset_id:int, asset_symbol:str, yesterday_date:str, today:str) -> None:
        try:
            asset_data:DataFrame = yf.download(asset_symbol, yesterday_date, today)
        except Exception:
            return # Simply iterate over to the next asset symbol.

        if asset_data is None or asset_data.empty:
            return # Nothing to store to the database so we'll continue to the next asset.

        # Reset index to turn the date into a column
        asset_data.reset_index(inplace=True)
        # Prepare the DataFrame
        df_price_history = asset_data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]].copy()
        df_price_history.columns = ["date", "open_price", "high_price", "low_price", "close_price", "adjusted_close", "volume"]

        try:
            # Iterate over the data frame to be stored in the database.
            for _, row in df_price_history.iterrows():
                price_record = PricePointsDbTable(
                    asset_id=asset_id,
                    date=row["date"],
                    open_price=row["open_price"],
                    close_price=row["close_price"],
                    high_price=row["high_price"],
                    low_price=row["low_price"],
                    adjusted_close=row["adjusted_close"],
                    volume=row["volume"],
                    source="yahoo_finance",
                )
                self._db_session.add(price_record)
            self._db_session.commit()
        except IntegrityError:
            self._db_session.rollback()
            print("It looks like we've updated the data already. We'll do nothing.")
        except Exception as e:
            self._db_session.rollback()
            print(f"Error in submitting price point entries: {e}")