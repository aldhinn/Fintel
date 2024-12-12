from utils.lstm_model import _prepare_training_data

def test_prepare_training_data():
    price_points = [
        {
            'date': f"2024-01-{i+1:02d}",
            'open_price': 100 + i,
            'high_price': 110 + i,
            'low_price': 90 + i,
            'close_price': 105 + i,
            'adjusted_close': 106 + i,
            'volume': 1000 + i * 10
        } for i in range(25)
    ]
    predictions = {"2024-01-01": 2.5}

    X, _, _ = _prepare_training_data(price_points, predictions)
    assert X.shape[0] > 0, "No training sequences generated."
    assert X.shape[1] == 10, "Sequence length is incorrect."