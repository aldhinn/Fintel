#!/usr/bin/python

import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from enum import Enum
from pandas import DataFrame

class APISourceEnum(Enum):
    """An enum determining API source for the finance data.
    """

    # Fetching data from Yahoo Finance.
    YAHOO_FINANCE=(1, "Fetching data from Yahoo Finance.")
    # Fetching data from Alpha Vantage
    ALPHA_VANTAGE=(2, "Fetching data from Alpha Vantage")

    def __new__(self, value:int, description:str):
        """Constructs a new enum object.

        Args:
            value (int): The enum integer value.
            description (str): The description of the enum value.

        Returns:
            APISourceEnum: The enum object.
        """
        obj = object.__new__(self)
        obj._value_ = value
        obj.description = description
        return obj

def fetch_data(name:str, start_date:str, end_date:str, \
    source:APISourceEnum = APISourceEnum.YAHOO_FINANCE, api_key:str = "") -> DataFrame | None:
    """Fetch asset data from a specified API.

    Args:
        name (str): The name of the asset.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        source (APISourceEnum, optional): The source for the finance data. \
            Defaults to APISourceEnum.YAHOO_FINANCE.
        api_key (str): The api key for the API used to fetch financial data.

    Returns:
        DataFrame | None: The asset data object. None if fetching failed or yielded no data.
    """

    if source == APISourceEnum.YAHOO_FINANCE:
        try:
            yfinance_data:DataFrame|None = yf.download(tickers=name, start=start_date, end=end_date)
            return yfinance_data
        except Exception as e:
            print(f"Error fetching data for {name} from Yahoo Finance: {e}")
            return None
    elif source == APISourceEnum.YAHOO_FINANCE:
        ts = TimeSeries(key=api_key, output_format='pandas')
        try:
            data, _ = ts.get_daily_adjusted(symbol=name, outputsize='full')
            data.index = pd.to_datetime(data.index)
            
            # Filter data within the specified date range
            data = data.loc[(data.index >= start_date) & (data.index <= end_date)]
            if data.empty:
                print("Returning None as data is empty.")
                return None
            return data
        except Exception as e:
            print(f"Error fetching data for {name} from Alpha Vantage: {e}")
            return None

    return None

if __name__ == "__main__":
    for _, source in enumerate(APISourceEnum):
        print(f"APISourceEnum: {source}, Value: {source.value}, Description: {source.description}")