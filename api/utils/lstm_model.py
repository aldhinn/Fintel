import os
import tempfile
import numpy as np
from numpy import ndarray
from pandas import DataFrame, Timestamp, Timedelta, Series, to_numeric
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Conv1D, BatchNormalization, Dropout, Input
from tensorflow.keras.regularizers import l2
from tensorflow.keras.losses import Huber
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sqlalchemy.orm import Session
from typing import Any
from utils.db_models import PricePointsDbTable, PredictionsDbTable, AIModelsDbTable
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

def _calculate_rsi(prices:Series, periods:int = 14) -> Series:
    """
    Calculate the Relative Strength Index (RSI) for a given price series.

    Args:
        prices (pd.Series): Time series of prices
        periods (int, optional): Number of periods for RSI calculation. Defaults to 14.

    Returns:
        pd.Series: RSI values
    """

    delta = prices.diff()

    # Make two series: one for lower closes and one for higher closes
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    # Calculate the EWMA
    roll_up = up.ewm(com=periods-1, adjust=False).mean()
    roll_down = down.ewm(com=periods-1, adjust=False).mean()
    # Calculate the RSI based on EWMA
    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi

def _create_advanced_features(price_points_df:DataFrame) -> DataFrame:
    """
    Create advanced technical features for time series analysis.

    Args:
        price_points_df (pd.DataFrame): DataFrame containing price information

    Returns:
        pd.DataFrame: DataFrame with additional technical features
    """

    # Create a copy to avoid modifying the original DataFrame
    data = price_points_df.copy()

    # Technical Indicators
    data["SMA_10"] = data["adjusted_close"].rolling(window=10).mean()
    data["EMA_10"] = data["adjusted_close"].ewm(span=10).mean()
    data["RSI"] = _calculate_rsi(data["adjusted_close"])
    # Percentage change features
    data["price_change_1d"] = data["adjusted_close"].pct_change()
    data["price_change_5d"] = data["adjusted_close"].pct_change(periods=5)
    # Volatility features
    data["volatility_10d"] = data["adjusted_close"].rolling(window=10, min_periods=1).std()

    return data

def _prepare_training_data(price_points:list, predictions:dict) -> tuple[ndarray, ndarray, MinMaxScaler]:
    """
    Prepares the training data for LSTM using price points and prediction errors.

    Args:
        price_points (list): List of price point dictionaries for the asset.
        predictions (dict): Dictionary mapping dates to prediction errors.

    Returns:
        tuple[ndarray, ndarray, MinMaxScaler]: Feature matrix (X) and target vector (y). The \
            target scaler to be used to inverse transformed predictions.
    """

    # Convert to DataFrame
    data = DataFrame(price_points)

    # Basic feature columns from input data
    base_columns = [
        "open_price", "high_price", "low_price",
        "close_price", "adjusted_close", "volume"
    ]

    # Ensure all base columns exist
    for col in base_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert to numeric, coercing errors to NaN
    for col in base_columns:
        data[col] = to_numeric(data[col], errors="coerce")

    # Apply advanced feature engineering
    data = _create_advanced_features(data)

    # Determine feature columns after feature engineering
    feature_columns = [
        "open_price", "high_price", "low_price",
        "close_price", "volume"
    ]

    # Add only the new features that were successfully created
    new_features = ["SMA_10', 'EMA_10', 'RSI', 'price_change_1d', 'price_change_5d', 'volatility_10d"]
    feature_columns.extend([f for f in new_features if f in data.columns])

    # Normalize features
    scaler = MinMaxScaler()

    # Safely normalize features
    try:
        # Select only existing columns
        existing_columns = [col for col in feature_columns if col in data.columns]

        # Normalize only existing columns
        data[existing_columns] = scaler.fit_transform(data[existing_columns])
    except Exception as e:
        print(f"Feature normalization error: {e}")
        raise

    # Normalize target variable
    target_scaler = MinMaxScaler()
    data["adjusted_close_normalized"] = target_scaler.fit_transform(data[["adjusted_close"]])

    # Create sequences
    X, y = [], []
    sequence_length = 10

    for i in range(len(data) - sequence_length):
        # Use only existing columns
        existing_columns = [col for col in feature_columns if col in data.columns]

        sequence = data.iloc[i:i+sequence_length][existing_columns].values
        target = data.iloc[i+sequence_length]["adjusted_close_normalized"]

        # Check for NaN in sequence or target
        if not (np.isnan(sequence).any() or np.isnan(target)):
            X.append(sequence)
            y.append(target)

    # Convert to numpy arrays
    X = np.array(X)
    y = np.array(y)

    # Final validation
    if X.shape[0] == 0 or y.shape[0] == 0:
        raise ValueError("No valid sequences could be created")

    return X, y, target_scaler

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

    # Prepare training data with normalization
    X, y, target_scaler = _prepare_training_data(price_points, prediction_errors)

    # Validate training data
    if X.shape[0] == 0 or y.shape[0] == 0:
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
            Input(shape=(X.shape[1], X.shape[2])),
            # Convolutional layer for feature extraction
            Conv1D(filters=64, kernel_size=3, activation="relu"),
            BatchNormalization(),
            # LSTM layers.
            LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.3),
            BatchNormalization(),
            LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),
            BatchNormalization(),
            LSTM(64, return_sequences=True, dropout=0.2, recurrent_dropout=0.2),
            BatchNormalization(),
            LSTM(64, dropout=0.2, recurrent_dropout=0.2),
            BatchNormalization(),
            # Additional dense layers with regularization
            Dense(32, activation="relu", kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            Dense(16, activation="relu", kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            Dense(16, activation="relu", kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            Dense(16, activation="relu", kernel_regularizer=l2(0.001)),
            Dropout(0.2),
            Dense(1)
        ])

        # Instantiate the Huber loss
        huber_loss = Huber(delta=5.0)
        # Compile the model
        model.compile(optimizer=Adam(learning_rate=0.001), loss=huber_loss, metrics=["mae"])

    # Early stopping and reduce learning rate
    early_stopping = EarlyStopping(
        monitor="val_loss",
        patience=10,
        restore_best_weights=True
    )
    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.1,
        patience=10,
        min_lr=1e-6
    )

    # Split data for validation
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, shuffle=False)

    # Train with validation
    model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=16,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping, reduce_lr],
        verbose=2
    )

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
        normalized_prediction = float(model.predict(last_sequence)[0][0])
        next_day_prediction = float(target_scaler.inverse_transform([[normalized_prediction]])[0][0])

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