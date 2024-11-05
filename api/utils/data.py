#!/usr/bin/python

import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from enum import Enum
from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler
from typing import Literal

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

def fetch_data(asset_symbol:str, start_date:str = "", end_date:str = "", \
    source:APISourceEnum = APISourceEnum.YAHOO_FINANCE, api_key:str = "") -> DataFrame | None:
    """Fetch asset symbol data from a specified API.

    Args:
        asset_symbol (str): The symbol for the asset.
        start_date (str, optional): The start date in 'YYYY-MM-DD' format.\
            If neither the start date nor the end date has been specified,\
            this method will fetch for all data for this asset symbol.
        end_date (str, optional): The end date in 'YYYY-MM-DD' format.\
            If neither the start date nor the end date has been specified,\
            this method will fetch for all data for this asset symbol.
        source (APISourceEnum, optional): The source for the finance data. \
            Defaults to APISourceEnum.YAHOO_FINANCE.
        api_key (str, optional): The api key for the API used to fetch financial data.

    Returns:
        DataFrame | None: The asset symbol data object. None if fetching failed or yielded no data.
    """

    if source == APISourceEnum.YAHOO_FINANCE:
        try:
            # Fetching all data if either of the dates is set to "".
            if start_date == "" or end_date == "":
                yfinance_data:DataFrame|None = yf.download(asset_symbol, period="max")
                return yfinance_data

            yfinance_data:DataFrame|None = yf.download(asset_symbol, start=start_date, end=end_date)
            return yfinance_data
        except Exception as e:
            print(f"Error fetching data for {asset_symbol} from Yahoo Finance: {e}")
            return None
    elif source == APISourceEnum.ALPHA_VANTAGE:
        ts = TimeSeries(key=api_key, output_format='pandas')
        try:
            data, _ = ts.get_daily_adjusted(symbol=asset_symbol, outputsize='full')
            data.index = pd.to_datetime(data.index)

            # Fetching all data if either of the dates is set to "".
            if start_date == "" or end_date == "":
                return data

            # Filter data within the specified date range
            data = data.loc[(data.index >= start_date) & (data.index <= end_date)]
            if data.empty:
                print("Returning None as data is empty.")
                return None
            return data
        except Exception as e:
            print(f"Error fetching data for {asset_symbol} from Alpha Vantage: {e}")
            return None

    return None

def handle_missing_values(df:DataFrame, strategy:Literal["fill", "drop"]='drop', fill_value:float=0) -> DataFrame:
    """Handle missing values in the DataFrame.

    Args:
        df (DataFrame): The DataFrame to process.
        strategy (Literal["fill", "drop"]): 'drop' to drop rows with missing values,\
            'fill' to fill them with a specific value. (Defaults to drop).
        fill_value (float): The value to fill missing data if strategy='fill'.

    Returns:
        DataFrame: DataFrame with missing values handled.
    """

    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill':
        df = df.fillna(fill_value)
    else:
        raise ValueError("Invalid strategy. Use 'drop' or 'fill'.")

    return df

def remove_outliers(df:DataFrame, column:str, threshold:float=1.5) -> DataFrame:
    """Remove outliers from a specific column in the DataFrame using the IQR method.

    Args:
        df (DataFrame): The DataFrame to process.
        column (str): Column to remove outliers from.
        threshold (float): Multiplier for the IQR (default is 1.5).

    Returns:
        DataFrame: DataFrame with outliers removed.
    """

    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - threshold * IQR
    upper_bound = Q3 + threshold * IQR

    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

def normalize_columns(df:DataFrame, columns:list[str]) -> DataFrame:
    """Normalize specified columns in the DataFrame to the range [0, 1].

    Args:
        df (DataFrame): The DataFrame to process.
        columns (list[str]): Columns to normalize.

    Returns:
        DataFrame: DataFrame with specified columns normalized.
    """

    scaler = MinMaxScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def preprocess_dataframe(df:DataFrame, columns_to_normalize:list[str],\
    missing_value_strategy:Literal['drop','fill']='drop', fill_value:float=0,\
    outlier_column:str|None=None, outlier_threshold=1.5) -> DataFrame:
    """Full data preprocessing pipeline, including handling missing values,\
        removing outliers, and normalizing specified columns.

    Parameters:
        df (DataFrame): The DataFrame to process.
        columns_to_normalize (list[str]): Columns to normalize.
        missing_value_strategy (Literal['drop','fill']): 'drop' to drop rows with \
            missing values, 'fill' to fill them with a specific value.
        fill_value (float): The value to fill missing data if strategy='fill'.
        outlier_column (str, optional): Column to remove outliers from.
        outlier_threshold (float): Threshold for outlier removal in IQR method.

    Returns:
        DataFrame: Cleaned and normalized DataFrame.
    """

    # Handle missing values
    df = handle_missing_values(df, strategy=missing_value_strategy, fill_value=fill_value)

    # Remove outliers if specified
    if outlier_column:
        df = remove_outliers(df, outlier_column, threshold=outlier_threshold)

    # Normalize specified columns
    df = normalize_columns(df, columns_to_normalize)

    return df

def _fetch_from_yahoo_finance(asset_symbol:str) -> None:
    """Fetch data from yahoo finance and store in the database.

    Args:
        asset_symbol (str): The symbol of the asset to be retrieved online.
    """

    from utils.flask_app import AssetsDbTable, AssetDbEntry, db, flask_app, PricePointDbEntry

    with flask_app.app_context():
        try:
            # Retrieve the asset id from the database.
            asset_id = AssetsDbTable.query.with_entities(AssetDbEntry.id).filter_by(symbol=asset_symbol).first().id
        except Exception as e:
            print(f"Failed to retrieve asset id with message: {e}")
            return None

        try:
            # Fetch all historical data
            data:DataFrame|None = yf.download(asset_symbol)
        except Exception as e:
            print(f"Failed to download from yahoo finance with message: {e}")

        # Halt from here on if retrieved nothing.
        if data is None:
            return

        # Reset index to turn the date into a column
        data.reset_index(inplace=True)
        # Prepare the DataFrame
        df_price_history = data[['Date', 'Open', 'Close', 'High', 'Low', 'Adj Close', 'Volume']].copy()
        df_price_history.columns = ['date', 'open_price', 'close_price', 'high_price', 'low_price', 'adjusted_close', 'volume']

        try:
            # Iterate over the data frame to be stored in the database.
            for _, row in df_price_history.iterrows():
                price_record = PricePointDbEntry(
                    asset_id=asset_id,
                    date=row['date'],
                    open_price=row['open_price'],
                    close_price=row['close_price'],
                    high_price=row['high_price'],
                    low_price=row['low_price'],
                    adjusted_close=row['adjusted_close'],
                    volume=row['volume'],
                    source='yahoo_finance',
                )
                db.session.add(price_record)
            db.session.commit()
        except Exception as e:
            print(f"Error in submitting price point entries: {e}")
            db.session.rollback()
            return

        try:
            # The reference to the asset entry in the database.
            ref_asset_entry = AssetsDbTable.query.get(asset_id)
            ref_asset_entry.processing_status = 'active'
            db.session.commit()
        except Exception as e:
            print(f"Failed to update asset entry with exception: {e}")

def analyze_symbols_from_list(asset_symbols_list:list[str]) -> None:
    """Analyze the list of symbol names specified.

    Args:
        asset_symbols_list (list[str]): The list of asset symbols to be analyzed.
    """

    for asset_symbol in asset_symbols_list:
        _fetch_from_yahoo_finance(asset_symbol=asset_symbol)

if __name__ == "__main__":
    for _, source in enumerate(APISourceEnum):
        print(f"APISourceEnum: {source}, Value: {source.value}, Description: {source.description}")