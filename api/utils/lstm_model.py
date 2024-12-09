#!/usr/bin/python

import numpy as np
from numpy import ndarray
from pandas import DataFrame, Timestamp
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sqlalchemy.orm import Session
from typing import Any
from utils.db_models import PricePointsDbTable, PredictionsDbTable, AIModelsDbTable

def _prepare_training_data(price_points:list, predictions: dict) -> tuple[ndarray, ndarray]:
    """
    Prepares the training data for LSTM using price points and prediction errors.

    Args:
        price_points (list): List of price point dictionaries for the asset.
        predictions (dict): Dictionary mapping dates to prediction errors.

    Returns:
        tuple[ndarray, ndarray]: Feature matrix (X) and target vector (y).
    """
    data = DataFrame(price_points)
    data["error"] = data["date"].map(predictions).fillna(0.0)

    # Create features and target
    feature_columns = ["open_price", "high_price", "low_price", "close_price", "volume", "error"]
    target_column = "adjusted_close"

    X, y = [], []

    for i in range(len(data) - 10):  # Sequence length = 10
        sequence = data.iloc[i:i+10][feature_columns].values
        target = data.iloc[i+10][target_column]
        X.append(sequence)
        y.append(target)

    return np.array(X), np.array(y)

def train_lstm_model(asset_id: int, db_session:Session|Any) -> None:
    """
    Trains an LSTM model for each asset using price point data.
    """
    # Retrieve price points for the asset
    price_points = db_session.query(PricePointsDbTable).filter_by(asset_id=asset_id).order_by(PricePointsDbTable.date.asc()).all()
    price_points = [
        {
            "date": p.date,
            "open_price": p.open_price,
            "high_price": p.high_price,
            "low_price": p.low_price,
            "close_price": p.close_price,
            "adjusted_close": p.adjusted_close,
            "volume": p.volume
        } for p in price_points
    ]

    # Retrieve predictions and calculate errors
    predictions = db_session.query(PredictionsDbTable).filter_by(asset_id=asset_id).all()
    prediction_errors = {
        pred.date: abs(pred.prediction - pred.close_price) for pred in predictions
    } if predictions else {}

    # Prepare training data
    X, y = _prepare_training_data(price_points, prediction_errors)

    if X.shape[0] == 0:
        print(f"Skipping asset {asset_id} due to insufficient data.")
        return

    # Build the LSTM model
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        LSTM(50),
        Dense(1)
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")

    # Train the model
    model.fit(X, y, epochs=20, batch_size=32, verbose=2)

    # Save the model
    model_data = model.to_json()
    last_trained = Timestamp.now()

    # Check if the model already exists
    existing_model = db_session.query(AIModelsDbTable).filter_by(asset_id=asset_id).first()

    if existing_model:
        existing_model.model_data = model_data
        existing_model.last_trained = last_trained
    else:
        new_model = AIModelsDbTable(
            asset_id=asset_id,
            model_type="LSTM",
            model_data=model_data,
            last_trained=last_trained
        )
        db_session.add(new_model)

    db_session.commit()