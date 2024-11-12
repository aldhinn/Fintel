#!/usr/bin/python

from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler
from typing import Literal

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

    import yfinance as yf
    from yfinance import Ticker
    from utils.config import flask_app
    from utils.db_models import AssetsDbTable, database, PricePointsDbTable

    with flask_app.app_context():
        try:
            # Retrieve the asset id from the database.
            asset_id = AssetsDbTable.query.with_entities(AssetsDbTable.id).filter_by(symbol=asset_symbol).first().id
        except Exception as e:
            print(f"Failed to retrieve asset id with message: {e}")
            return None

        try:
            # Fetch all historical data.
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
                price_record = PricePointsDbTable(
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
                database.session.add(price_record)
            database.session.commit()
        except Exception as e:
            print(f"Error in submitting price point entries: {e}")
            database.session.rollback()
            return

        try:
            # Fetch metadata.
            metadata:dict = Ticker(asset_symbol).info
            # The reference to the asset entry in the database.
            ref_asset_entry = AssetsDbTable.query.get(asset_id)
            description = metadata.get('longName', 'Description not available')

            # Update asset entry.
            ref_asset_entry.processing_status = 'active'
            ref_asset_entry.description = description

            database.session.commit()
        except Exception as e:
            database.session.rollback()
            print(f"Failed to update asset entry with exception: {e}")

def analyze_symbols_from_list(asset_symbols_list:list[str]) -> None:
    """Analyze the list of symbol names specified.

    Args:
        asset_symbols_list (list[str]): The list of asset symbols to be analyzed.
    """

    for asset_symbol in asset_symbols_list:
        _fetch_from_yahoo_finance(asset_symbol=asset_symbol)