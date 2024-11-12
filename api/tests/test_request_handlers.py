#!/usr/bin/python

from datetime import date
import pytest
from utils.constants import API_ENDPOINT_DATA,\
    API_ENDPOINT_APPEND, API_ENDPOINT_SYMBOLS
from utils.request_handlers import RequestHandlerFactory
from unittest.mock import MagicMock

def test_invalid_api_endpoint_name():
    """Attempt to create an request handler to an invalid API endpoint.
    """
    fake_api_endpoint = "oawihergpa9ehr0wf0few"
    assert fake_api_endpoint != API_ENDPOINT_SYMBOLS
    assert fake_api_endpoint != API_ENDPOINT_APPEND
    assert fake_api_endpoint != API_ENDPOINT_DATA

    # This is expected to raise a TypeError exception.
    with pytest.raises(TypeError):
        RequestHandlerFactory.create_handler(fake_api_endpoint)

@pytest.fixture
def fixture_api_symbols():
    """Fixture for API endpoint `API_ENDPOINT_SYMBOLS`
    """
    # The expected 'active' list of asset symbols.
    expected_active_list = ["AAPL", "GOOGL"]
    # Mock database session.
    mock_db_session = MagicMock()
    # Mock database query when we query for 'active' assets.
    mock_all_active_query = MagicMock(\
        return_value=[(value,) for value in expected_active_list])
    mock_db_session.query.return_value.\
        filter_by.return_value.all = mock_all_active_query

    return expected_active_list, mock_db_session, mock_all_active_query

def test_retrieve_symbols(fixture_api_symbols):
    """Retrieve asset symbols that are 'active'.
    """
    # Mock database interactions.
    expected_active_list, mock_db_session,\
        mock_all_active_query = fixture_api_symbols

    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_SYMBOLS, mock_db_session)
    # Get method at the endpoint.
    response, status_code = handler.process(method="GET")

    assert status_code == 200
    assert response["symbols"] == expected_active_list
    # It's important that we do one batch database queries, not multiple small queries.
    mock_all_active_query.assert_called_once()

def test_non_get_methods_symbols(fixture_api_symbols):
    """Attempt to do non-get requests.
    """
    # Mock database interactions.
    _, mock_db_session, mock_all_active_query = fixture_api_symbols
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_SYMBOLS, mock_db_session)
    # For other methods, there should be no response.
    for api_method in ["POST", "PUT", "DELETE"]:
        response, status_code = handler.process(method=api_method)

        assert status_code == 204
        assert response == {}
        mock_all_active_query.assert_not_called()

@pytest.fixture
def fixture_api_append():
    """Fixture for API endpoint `API_ENDPOINT_APPEND`
    """
    # Mock database session.
    mock_db_session = MagicMock()
    # The rollback call of the database session.
    mock_db_session_rollback_call = MagicMock()
    mock_db_session.rollback = mock_db_session_rollback_call
    # Database session add
    mock_db_session_add_call = MagicMock()
    mock_db_session.add = mock_db_session_add_call

    return mock_db_session, mock_db_session_rollback_call,\
        mock_db_session_add_call

def test_track_add_calls(fixture_api_append):
    """Track the number of add calls to the database.
    """
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)

    # Mock a return value for this query.
    mock_db_session.query.return_value.\
        filter_by.return_value.first = MagicMock(return_value=None)

    request = ["asset1", "asset2"]
    response, status_code = handler.process(method="POST", request=request)

    assert status_code == 200
    assert len(request) == mock_db_session_add_call.call_count
    assert response.get("error") is None

def test_exceptions_raised_during_commit(fixture_api_append):
    """Expected to rollback database session if exception is raised.
    """
    # Mock database interactions.
    mock_db_session, mock_db_session_rollback_call, _ = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)

    # Mock raising an exception.
    mock_db_session.commit.side_effect = Exception()

    request = ["asset1", "asset2"]
    response, status_code = handler.process(method="POST", request=request)

    assert status_code == 500
    mock_db_session_rollback_call.assert_called_once()
    assert isinstance(response.get("error"), str)

def test_posting_with_list_with_non_string_element(fixture_api_append):
    """ Attempt to add an asset symbol of which value is not a string.
    """
    # Mock database interactions.
    mock_db_session, mock_db_session_rollback_call,\
        mock_db_session_add_call = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)

    # Request with a list with non string element.
    request = ["some_string", {"property": "Some_non_str_obj"}]
    assert isinstance(request, list)
    assert isinstance(request[0], str)
    assert not isinstance(request[1], str)
    response, status_code = handler.process(method="POST", request=request)

    assert status_code == 400
    mock_db_session_rollback_call.assert_called_once()
    mock_db_session_add_call.assert_not_called()
    assert isinstance(response.get("error"), str)

def test_posting_with_empty_list(fixture_api_append):
    """Examining behaviours when requesting with an empty list request body.
    """
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)

    # Request with an object, not a list.
    request_obj:list = []
    assert isinstance(request_obj, list)
    response, status_code = handler.process(method="POST", request=request_obj)

    assert status_code == 400
    mock_db_session_add_call.assert_not_called()
    assert isinstance(response.get("error"), str)

def test_posting_with_non_list(fixture_api_append):
    """Examining behaviours when requesting with a non-list type request body.
    """
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)

    # Request with an object, not a list.
    request_obj = {}
    assert not isinstance(request_obj, list)
    response, status_code = handler.process(method="POST", request=request_obj)

    assert status_code == 400
    mock_db_session_add_call.assert_not_called()
    assert isinstance(response.get("error"), str)

def test_non_post_methods_append(fixture_api_append):
    """Attempt to do non-post requests.
    """
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_append
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_APPEND, mock_db_session)
    # For other methods, there should be no response.
    for api_method in ["GET", "PUT", "DELETE"]:
        result, status_code = handler.process(method=api_method, request={})

        assert status_code == 204
        assert result == {}
        mock_db_session_add_call.assert_not_called()

@pytest.fixture
def fixture_api_data():
    """Fixture for API endpoint `API_ENDPOINT_DATA`
    """
    # Mock database session.
    mock_db_session = MagicMock()

    return mock_db_session

def test_data_querying_for_asset(fixture_api_data):
    """Demonstrate data querying for an asset.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)

    # Simulate query return.
    mock_db_session.query.return_value.join.return_value.\
        filter.return_value.all.return_value = [\
            MagicMock(date=date(2023, 1, 1), description="Some description",\
            open_price=102.1, close_price=23.1, high_price=102.1, low_price=10.1,\
            adjusted_close=95.7, volume=29193)\
        ]

    request = {"symbol": "AAPL", "start_date": "2024-01-01", "end_date": "2024-02-02"}
    assert isinstance(request.get("symbol"), str)
    assert isinstance(request.get("start_date"), str)
    assert isinstance(request.get("end_date"), str)
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    print(response)
    assert status_code == 200
    assert response.get("error") is None
    assert isinstance(response.get("description"), str)
    assert isinstance(response.get("prices"), list)

def test_exception_raised_during_db_session_query(fixture_api_data):
    """Examine the behaviours during events when exceptions are raised when querying the database.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)

    # The database session rollback call.
    mock_db_session_rollback_call = MagicMock()
    mock_db_session.rollback = mock_db_session_rollback_call

    # Simulate throwing an exception during query.
    mock_db_session.query.side_effect = Exception()

    request = {"symbol": "AAPL", "start_date": "2024-01-01", "end_date": "2024-02-02"}
    assert isinstance(request.get("symbol"), str)
    assert isinstance(request.get("start_date"), str)
    assert isinstance(request.get("end_date"), str)
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 500
    assert isinstance(response.get("error"), str)
    mock_db_session_rollback_call.assert_called_once()

def test_non_string_values(fixture_api_data):
    """Examine what happens if one of the values is not a string.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)

    # Symbol is not as string.
    request = {"symbol": {}, "start_date": "2024-01-01", "end_date": "2024-02-02"}
    assert not request.get("symbol") is None
    assert not isinstance(request.get("symbol"), str)
    assert isinstance(request.get("start_date"), str)
    assert isinstance(request.get("end_date"), str)
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

    # start_date is not as string.
    request = {"symbol": "AAPL", "start_date": {}, "end_date": "2024-02-02"}
    assert not request.get("start_date") is None
    assert not isinstance(request.get("start_date"), str)
    assert isinstance(request.get("symbol"), str)
    assert isinstance(request.get("end_date"), str)
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

    # end_date is not as string.
    request = {"symbol": "AAPL", "start_date": "2024-02-02", "end_date": {}}
    assert not request.get("end_date") is None
    assert not isinstance(request.get("end_date"), str)
    assert isinstance(request.get("symbol"), str)
    assert isinstance(request.get("start_date"), str)
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

def test_posting_incomplete_keys(fixture_api_data):
    """Examine what happens if either symbol, start_date or end_date are unspecified.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)

    # Request doesn't have end_date.
    request = {"symbol": "AAPL", "start_date": "2024-01-01"}
    assert request.get("end_date") is None
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

    # Request doesn't have start_date.
    request = {"symbol": "AAPL", "end_date": "2024-01-01"}
    assert request.get("start_date") is None
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

    # Request doesn't have symbol.
    request = {"start_date": "2024-01-01", "end_date": "2024-01-05"}
    assert request.get("symbol") is None
    response, status_code = handler.process(method="POST", request=request)
    # Expected behaviours.
    assert status_code == 400
    assert isinstance(response.get("error"), str)

def test_posting_with_list(fixture_api_data):
    """Examine the behaviours requesting data using list.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)

    request:list = []
    assert isinstance(request, list)
    response, status_code = handler.process(method="POST", request=request)

    assert status_code == 400
    assert isinstance(response.get("error"), str)

def test_non_post_methods_data(fixture_api_data):
    """Attempt to do non-post requests.
    """
    # Mock database interactions.
    mock_db_session = fixture_api_data
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_DATA, mock_db_session)
    # For other methods, there should be no response.
    for api_method in ["GET", "PUT", "DELETE"]:
        result, status_code = handler.process(method=api_method, request={})

        assert status_code == 204
        assert result == {}