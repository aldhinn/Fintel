#!/usr/bin/python

from sklearn.preprocessing import MinMaxScaler
from pandas import DataFrame
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

def preprocess_data(df:DataFrame, columns_to_normalize:list[str],\
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
