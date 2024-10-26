#!/usr/bin/python

def test_fetch_from_yfinance():
    from utils.fetch_data import fetch_data

    ticker = "AAPL"
    start_date = "2024-10-1"
    end_date = "2024-10-26"

    data = fetch_data(name=ticker, start_date=start_date, end_date=end_date)
    print(data)

    assert data is not None