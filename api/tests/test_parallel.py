#!/usr/bin/python

from datetime import date, timedelta
import time
from unittest.mock import MagicMock, patch
from pandas import DataFrame
import pytest
from utils.parallel import _BaseParallelTask, DataAndModelUpdater
from sqlalchemy.exc import IntegrityError

class MockImplParallelTask(_BaseParallelTask):
    """Create a concrete subclass of BaseParallelTask for testing purposes
    """
    def _run(self):
        """Runs nothing, just defined for testing."""

def test_parallel_task_run_method_called():
    """Examine if `_run` was ran during instantiation."""

    # Patch the _run method to track if it was called
    with patch.object(MockImplParallelTask, '_run', return_value=None) as mock_run:
        # Instantiate the TestParallelTask, which should start the thread
        _ = MockImplParallelTask(MagicMock(), MagicMock())

        # Verify that _run was called by the thread
        mock_run.assert_called_once()

@pytest.fixture
def fixture_price_point_updater() -> tuple[MagicMock, MagicMock]:
    """The fixture object for testing `PricePointUpdater`

    Returns:
        tuple[MagicMock, MagicMock]: (mock_db_session, mock_flask_app)
    """

    # Mock the database session.
    mock_db_session = MagicMock()
    # Mock the flask application.
    mock_flask_app = MagicMock()
    mock_flask_app.app_context = MagicMock()

    return mock_db_session, mock_flask_app

@patch("time.sleep", return_value=None)  # Mock time.sleep to avoid delays
@patch("yfinance.download")  # Mock yfinance download function
def test_run_single_iteration(mock_yf_download, _, fixture_price_point_updater):
    """Test a single iteration of the DataAndModelUpdater task."""

    # Set up the mock data returned by yfinance download
    mock_yf_download.return_value = DataFrame({
        "Date": [date.today()],
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0],
        "Adj Close": [101.0],
        "Volume": [1000]
    })

    # Get the mocks from the fixture
    mock_db_session, mock_flask_app = fixture_price_point_updater

    # Set up mock query result
    mock_assets = [(1, "AAPL")]
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = mock_assets

    # Instantiate DataAndModelUpdater with a single iteration
    _ = DataAndModelUpdater(db_session=mock_db_session, flask_app=mock_flask_app, iterations=1)

    # Give the thread time to run
    time.sleep(1)

    # Assertions
    mock_yf_download.assert_called_once_with("AAPL", (date.today() - timedelta(days=1)).\
        strftime("%Y-%m-%d"), date.today().strftime("%Y-%m-%d"))
    mock_db_session.query.assert_called_once()  # Ensure the query was made to fetch active assets
    mock_db_session.add.assert_called_once()  # Ensure at least one add call was made for a price point
    mock_db_session.commit.assert_called_once()  # Ensure commit was called to save price points
    mock_db_session.rollback.assert_not_called() # Ensure no rollbacks have been called.

@patch("time.sleep", return_value=None)  # Mock time.sleep
@patch("yfinance.download", return_value=DataFrame())  # Mock download to return an empty DataFrame
def test_run_no_data(mock_yf_download, _, fixture_price_point_updater):
    """Test the case where yfinance download returns no data, in the case of\
        trading floor closures.
    """

    # Get the mocks from the fixture
    mock_db_session, mock_flask_app = fixture_price_point_updater

    # Set up mock query result
    mock_assets = [(1, "AAPL")]
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = mock_assets

    # Instantiate DataAndModelUpdater with a single iteration
    DataAndModelUpdater(db_session=mock_db_session, flask_app=mock_flask_app, iterations=1)

    # Give the thread time to run
    time.sleep(1)

    # Assertions
    mock_yf_download.assert_called_once_with("AAPL", (date.today() - timedelta(days=1)).\
        strftime("%Y-%m-%d"), date.today().strftime("%Y-%m-%d"))
    mock_db_session.add.assert_not_called()  # No data should mean no calls to add any price points
    mock_db_session.commit.assert_not_called()  # No data should mean no commit

@patch("time.sleep", return_value=None)  # Mock time.sleep
@patch("yfinance.download", return_value=DataFrame())  # Mock download to return an empty DataFrame
def test_data_and_model_updater_unique_violation_handling(mock_yf_download, _, fixture_price_point_updater):
    """Tests that `DataAndModelUpdater` correctly handles a unique constraint violation\
        by calling `rollback()` when an `IntegrityError` occurs.
    """

    # Get the mocks from the fixture
    mock_db_session, mock_flask_app = fixture_price_point_updater
    # Mock the database query for active assets.
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = [
        (2, "GOOGL")
    ]
    # Mock the data frame returned by yf.download
    mock_yf_download.return_value = DataFrame({
        "Date": ["2024-11-14"],
        "Open": [100.0],
        "High": [105.0],
        "Low": [95.0],
        "Close": [102.0],
        "Adj Close": [101.0],
        "Volume": [1000]
    })
    # Simulate IntegrityError on db_session.commit
    integrity_error = IntegrityError(
        statement="INSERT INTO price_points ...",
        params=None,
        orig=Exception("unique constraint")
    )
    mock_db_session.commit.side_effect = integrity_error

    # Create an instance of DataAndModelUpdater with 1 iteration to avoid the infinite loop
    DataAndModelUpdater(db_session=mock_db_session, flask_app=mock_flask_app, iterations=1)

    # Give the thread time to run
    time.sleep(1)

    # Assert that add was attempted.
    mock_db_session.add.assert_called_once()
    # Assert that commit was attempted.
    mock_db_session.commit.assert_called_once()
    # Ensure rollback was called
    mock_db_session.rollback.assert_called_once()