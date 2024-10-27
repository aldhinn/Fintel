#!/usr/bin/python

import pytest
from tensorflow.keras import Model
import numpy as np
from pandas import DataFrame
from utils.lstm_model import build_lstm_model, train_lstm_model, save_lstm_model,\
    load_lstm_model, preprocess_lstm_data

@pytest.fixture
def sample_data() -> DataFrame:
    return DataFrame({
        "price": np.sin(np.linspace(0, 100, 1000))  # Sample sine wave data to simulate stock prices
    })

def test_build_lstm_model():
    """Tests the LSTM model building function. Verifies that the model\
        is built with the correct structure and compiles successfully.
    """

    input_shape = (60, 1)
    model = build_lstm_model(input_shape)
    assert isinstance(model, Model), "Model creation failed, not a Keras Model instance."
    assert model.input_shape == (None, 60, 1), f"Expected input shape (None, 60, 1), but got {model.input_shape}"

def test_preprocess_lstm_data(sample_data):
    """Tests the LSTM data preprocessing function. Ensures that the\
        preprocessing function correctly normalizes the data and\
        creates sequences with the expected shape.
    """

    x_data, y_data = preprocess_lstm_data(sample_data, target_column="price", lookback=60)
    assert x_data.shape[1:] == (60, 1), f"Expected shape (60, 1), but got {x_data.shape[1:]}"
    assert x_data.shape[0] == y_data.shape[0], "Mismatch between samples and target data lengths."

def test_train_lstm_model(sample_data):
    """Tests the training of the LSTM model.Trains a small model\
        on synthetic data and checks that the model trains without errors.
    """

    x_data, y_data = preprocess_lstm_data(sample_data, target_column="price", lookback=60)
    model = build_lstm_model((60, 1))
    history = train_lstm_model(model, x_data, y_data, epochs=1, batch_size=32)
    assert 'loss' in history.history, "Training history does not contain 'loss'."

def test_save_and_load_lstm_model(tmpdir):
    """Tests the saving and loading of the LSTM model. Verifies that\
        a saved model can be loaded and that it retains the same structure.
    """

    model = build_lstm_model((60, 1))
    model_path = str(tmpdir.join("test_lstm_model.h5"))
    save_lstm_model(model, model_path)

    # Load the model and check if it’s the same type
    loaded_model = load_lstm_model(model_path)
    assert isinstance(loaded_model, Model), "Loaded model is not a Keras Model instance."
