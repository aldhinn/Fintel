import os
import tempfile
import numpy as np
from numpy import ndarray
from pandas import DataFrame, Timestamp, Timedelta
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sqlalchemy.orm import Session
from typing import Any
from utils.db_models import PricePointsDbTable, PredictionsDbTable, AIModelsDbTable

def _prepare_training_data(price_points:list, predictions:dict) -> tuple[ndarray, ndarray]:
    """
    Prepares the training data for LSTM using price points and prediction errors.

    Args:
        price_points (list): List of price point dictionaries for the asset.
        predictions (dict): Dictionary mapping dates to prediction errors.

    Returns:
        tuple[ndarray, ndarray]: Feature matrix (X) and target vector (y).
    """
    # Convert decimal.Decimal to float in price points and predictions
    for point in price_points:
        for key in ["open_price", "high_price", "low_price", "close_price", "adjusted_close", "volume"]:
            point[key] = float(point[key])

    predictions = {date: float(error) for date, error in predictions.items()}

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
    Trains or retrains an LSTM model for a given asset using its price point data.

    Args:
        asset_id (int): The identifier of the asset in the database.
        db_session (Session | Any): The object that manages the database session.
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
    prediction_errors = {}

    if predictions:
        for pred in predictions:
            corresponding_price_point = next((p for p in price_points if p["date"] == pred.date), None)
            if corresponding_price_point:
                prediction_errors[pred.date] = abs(pred.prediction - corresponding_price_point["adjusted_close"])

    # Prepare training data
    X, y = _prepare_training_data(price_points, prediction_errors)

    if X.shape[0] == 0:
        print(f"Skipping asset {asset_id} due to insufficient data.")
        return

    # Check if the model already exists
    existing_model = db_session.query(AIModelsDbTable).filter_by(asset_id=asset_id).first()

    if existing_model:
        # Load the existing model
        with tempfile.NamedTemporaryFile(delete=False, suffix=".keras") as tmp_file:
            temp_file_path = tmp_file.name
            tmp_file.write(existing_model.model_data)

        model = load_model(temp_file_path)

        os.remove(temp_file_path)

    else:
        # Build a new LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
            LSTM(50),
            Dense(1)
        ])

        model.compile(optimizer=Adam(learning_rate=0.001), loss="mean_squared_error")

    # Train or retrain the model
    model.fit(X, y, epochs=20, batch_size=32, verbose=2)
    # Retrieve timestamp as soon as it was trained.
    last_trained = Timestamp.now()

    # Save the updated model to a temporary file in .keras format
    with tempfile.NamedTemporaryFile(delete=False, suffix=".keras") as tmp_file:
        temp_file_path = tmp_file.name
        model.save(temp_file_path)

    try:
        # Read the file into binary data
        with open(temp_file_path, "rb") as f:
            model_data = f.read()

        if existing_model:
            # Update the existing model
            existing_model.model_data = model_data
            existing_model.last_trained = last_trained
        else:
            # Save the new model
            new_model = AIModelsDbTable(
                asset_id=asset_id,
                model_type="LSTM",
                model_data=model_data,
                last_trained=last_trained
            )
            db_session.add(new_model)

        db_session.commit()

        # Retrieve entry after commit.
        existing_model = db_session.query(AIModelsDbTable).filter_by(asset_id=asset_id).first()

        # Make a prediction for the next day
        last_sequence = X[-1].reshape(1, X.shape[1], X.shape[2])  # Use the last sequence in the training set.
        # Check if a prediction for the next day already exists
        next_day_date = price_points[-1]["date"] + Timedelta(days=1)
        # Calculate the next day prediction.
        next_day_prediction = float(model.predict(last_sequence)[0][0])

        # Attempt to read for an existing prediction entry.
        existing_prediction = db_session.query(PredictionsDbTable).filter_by(asset_id=asset_id, model_id=existing_model.id, date=next_day_date).first()

        if existing_prediction:
            # Update the existing prediction
            existing_prediction.prediction = next_day_prediction
        else:
            # Save the prediction to the database
            new_prediction = PredictionsDbTable(
                asset_id=asset_id,
                model_id=existing_model.id,
                date=next_day_date,
                prediction=next_day_prediction,
                prediction_type="adjusted_close"
            )
            db_session.add(new_prediction)

        db_session.commit()

    finally:
        # Delete the temporary file
        os.remove(temp_file_path)