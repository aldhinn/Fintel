#!/usr/bin/python

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras import Model
from tensorflow.keras.callbacks import EarlyStopping, History
from pandas import DataFrame
import numpy as np
from numpy.typing import NDArray

def build_lstm_model(input_shape:tuple[int,int]) -> Model:
    """Builds and compiles an LSTM model.

    Args:
        input_shape (tuple[int,int]): The shape of the input data, typically (time_steps, features).

    Returns:
        Model: A compiled LSTM model.
    """

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=input_shape),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model

def train_lstm_model(model:Model, data:NDArray[np.float128], target:NDArray[np.float128],\
    batch_size:int=32, epochs:int=10, validation_split:float=0.2) -> History:
    """Trains the LSTM model on the provided data.

    Args:
        model (Model): The LSTM model to be trained.
        data (NDArray[np.float128]): The input data for training with shape\
            (samples, time_steps, features).
        target (NDArray[np.float128]): The target values for training.
        batch_size (int, optional): The size of batches for training. Default is 32.
        epochs (int, optional): The number of training epochs. Default is 10.
        validation_split (float, optional): The fraction of data to use for validation. Default is 0.2.

    Returns:
        History: Training history, including loss values per epoch.
    """

    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    history = model.fit(
        data, target,
        batch_size=batch_size,
        epochs=epochs,
        validation_split=validation_split,
        callbacks=[early_stopping],
        verbose=1
    )
    return history

def save_lstm_model(model:Model, filepath:str="lstm_model.h5") -> None:
    """Saves the trained LSTM model to a file.

    Args:
        model (Model): The trained LSTM model to be saved.
        filepath (str, optional): The path where the model will be saved. Default is 'lstm_model.h5'.
    """

    model.save(filepath)

def load_lstm_model(filepath:str="lstm_model.h5") -> Model:
    """Loads a trained LSTM model from a file.

    Args:
        filepath (str, optional): The path from where the model will be loaded. Default is 'lstm_model.h5'.

    Returns:
        Model: The loaded LSTM model.
    """

    return load_model(filepath)

def preprocess_lstm_data(df:DataFrame, target_column="price", lookback:int=60) -> tuple[NDArray[np.float128], NDArray[np.float128]]:
    """Preprocesses time-series data for LSTM input, including normalization and sequence creation.

    Args:
        df (DataFrame): The input data containing the time-series information.
        target_column (str, optional): The column in the DataFrame to be used as the target. Default is 'price'.
        lookback (int, optional): The number of past time steps to include in each input sample. Default is 60.

    Returns:
        tuple[NDArray[np.float128], NDArray[np.float128]]: x_data - Preprocessed\
            input data for LSTM with shape (samples, lookback, 1),\
            y_data - Target values for each sample.
    """

    data = df[target_column].values
    data_normalized = (data - np.mean(data)) / np.std(data)  # Standardize data

    x_data:list[np.float128] = []
    y_data:list[np.float128] = []
    for i in range(len(data_normalized) - lookback):
        x_data.append(data_normalized[i:i+lookback])
        y_data.append(data_normalized[i+lookback])

    x_data, y_data = np.array(x_data), np.array(y_data)
    return x_data.reshape(x_data.shape[0], x_data.shape[1], 1), y_data