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

def fetch_data(tickerName:str, start_date:str, end_date:str, \
    source:APISourceEnum = APISourceEnum.YAHOO_FINANCE, api_key:str = "") -> DataFrame | None:
    """Fetch ticker data from a specified API.

    Args:
        name (str): The name of the ticker.
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        source (APISourceEnum, optional): The source for the finance data. \
            Defaults to APISourceEnum.YAHOO_FINANCE.
        api_key (str): The api key for the API used to fetch financial data.

    Returns:
        DataFrame | None: The ticker data object. None if fetching failed or yielded no data.
    """

    if source == APISourceEnum.YAHOO_FINANCE:
        try:
            yfinance_data:DataFrame|None = yf.download(tickers=tickerName, start=start_date, end=end_date)
            return yfinance_data
        except Exception as e:
            print(f"Error fetching data for {tickerName} from Yahoo Finance: {e}")
            return None
    elif source == APISourceEnum.ALPHA_VANTAGE:
        ts = TimeSeries(key=api_key, output_format='pandas')
        try:
            data, _ = ts.get_daily_adjusted(symbol=tickerName, outputsize='full')
            data.index = pd.to_datetime(data.index)
            
            # Filter data within the specified date range
            data = data.loc[(data.index >= start_date) & (data.index <= end_date)]
            if data.empty:
                print("Returning None as data is empty.")
                return None
            return data
        except Exception as e:
            print(f"Error fetching data for {tickerName} from Alpha Vantage: {e}")
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

def analyze_tickers_from_list(ticker_names_list:list[str]) -> None:
    """Analyze the list of ticker specified.

    Args:
        ticker_names_list (list[str]): The name of the ticker to be analyzed.
    """

    # TODO: Delete later upon implementation completion.
    for ticker_name in ticker_names_list:
        print(f"Analyzing ticker name: {ticker_name}")

    # TODO: Implement.

if __name__ == "__main__":
    for _, source in enumerate(APISourceEnum):
        print(f"APISourceEnum: {source}, Value: {source.value}, Description: {source.description}")