#!/usr/bin/python

import pytest
from pandas import DataFrame
from utils.data import handle_missing_values, remove_outliers,\
    normalize_columns, preprocess_dataframe
import numpy as np

def test_fetch_from_yfinance() -> None:
    """Test whether we have successfully fetched data from Yahoo Finance.
    """

    from utils.data import fetch_data

    ticker = "AAPL"
    start_date = "2024-10-1"
    end_date = "2024-10-26"

    data = fetch_data(tickerName=ticker, start_date=start_date, end_date=end_date)
    print(data)

    assert data is not None
    assert isinstance(data, DataFrame)

# Sample data for testing
@pytest.fixture
def sample_data() -> DataFrame:
    return DataFrame({
        "price": [100, 102, None, 105, 107, 2000, 110, 108, None, 112],
        "volume": [300, 320, 350, 330, 340, 20000, 310, 300, 320, 310]
    })

def test_handle_missing_values_drop(sample_data) -> None:
    """Test if rows with missing values are removed correctly.
    """

    result = handle_missing_values(sample_data, strategy='drop')
    print("\nResult after drop missing values:\n", result)

    assert result.isna().sum().sum() == 0  # No missing values
    assert len(result) == 8  # Rows with missing values dropped

def test_handle_missing_values_fill(sample_data) -> None:
    """Test if missing values are filled correctly with the specified fill_value.
    """

    result = handle_missing_values(sample_data, strategy='fill', fill_value=0)
    print("\nResult after filling missing values:\n", result)

    assert result.isna().sum().sum() == 0  # No missing values
    assert result.loc[2, "price"] == 0  # Missing values filled with 0

def test_remove_outliers(sample_data) -> None:
    """Test if outliers are removed correctly based on IQR method for 'price' column.
    """

    result = remove_outliers(sample_data, column='price', threshold=1.5)
    print("\nResult after removing outliers:\n", result)

    assert result["price"].max() < 2000  # Outlier removed
    assert len(result) < len(sample_data)  # Some rows removed

def test_normalize_columns(sample_data) -> None:
    """Test if specified columns are normalized to range [0, 1] correctly.
    """

    # Filling missing values to prevent issues during normalization
    result = normalize_columns(sample_data.fillna(0), ["price", "volume"])
    print("\nResult after normalization:\n", result)

    assert np.isclose(result["price"].min(), 0)  # Normalized minimum
    assert np.isclose(result["price"].max(), 1)  # Normalized maximum
    assert np.isclose(result["volume"].min(), 0)  # Normalized minimum
    assert np.isclose(result["volume"].max(), 1)  # Normalized maximum

def test_preprocess_data(sample_data) -> None:
    """Test the full preprocessing pipeline for handling missing values,\
        removing outliers, and normalizing.
    """

    result = preprocess_dataframe(
        df=sample_data,
        columns_to_normalize=["price", "volume"],
        missing_value_strategy="fill",
        fill_value=0,
        outlier_column="price",
        outlier_threshold=1.5
    )
    print("\nResult after full preprocessing:\n", result)

    # Validate no missing values
    assert result.isna().sum().sum() == 0

    # Validate normalization
    assert result["price"].min() == 0
    assert result["price"].max() == 1
    assert result["volume"].min() == 0
    assert result["volume"].max() == 1