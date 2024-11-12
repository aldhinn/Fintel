#!/usr/bin/python

import pytest
from utils.constants import API_ENDPOINT_DATA,\
    API_ENDPOINT_REQUEST, API_ENDPOINT_SYMBOLS
from utils.request_handlers import RequestHandlerFactory
from unittest.mock import MagicMock

def test_invalid_api_endpoint_name():
    """Attempt to create an request handler to an invalid API endpoint.
    """
    fake_api_endpoint = "oawihergpa9ehr0wf0few"
    assert fake_api_endpoint != API_ENDPOINT_SYMBOLS
    assert fake_api_endpoint != API_ENDPOINT_REQUEST
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
    result, status_code = handler.process(method="GET")

    assert status_code == 200
    assert result["symbols"] == expected_active_list
    # It's important that we do one batch database queries, not multiple small queries.
    mock_all_active_query.assert_called_once()

def test_non_get_methods_symbols(fixture_api_symbols):
    # Mock database interactions.
    _, mock_db_session, mock_all_active_query = fixture_api_symbols
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_SYMBOLS, mock_db_session)
    # For other methods, there should be no response.
    for api_method in ["POST", "PUT", "DELETE"]:
        result, status_code = handler.process(method=api_method)

        assert status_code == 204
        assert result == {}
        mock_all_active_query.assert_not_called()

@pytest.fixture
def fixture_api_request():
    """Fixture for API endpoint `API_ENDPOINT_REQUEST`
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

def test_track_add_calls(fixture_api_request):
    """"""
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)

    # Mock a return value for this query.
    mock_db_session.query.return_value.\
        filter_by.return_value.first = MagicMock(return_value=None)

    request = ["asset1", "asset2"]
    _, status_code = handler.process(method="POST", request=request)

    assert status_code == 200
    assert len(request) == mock_db_session_add_call.call_count

def test_exceptions_raised_during_commit(fixture_api_request):
    """"""
    # Mock database interactions.
    mock_db_session, mock_db_session_rollback_call, _ = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)

    # Mock raising an exception.
    mock_db_session.commit.side_effect = Exception()

    request = ["asset1", "asset2"]
    _, status_code = handler.process(method="POST", request=request)

    assert status_code == 500
    mock_db_session_rollback_call.assert_called_once()

def test_posting_with_list_with_non_string_element(fixture_api_request):
    """ Attempt to add an asset symbol of which value is not a string.
    """
    # Mock database interactions.
    mock_db_session, mock_db_session_rollback_call,\
        mock_db_session_add_call = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)

    # Request with a list with non string element.
    request = ["some_string", {"property": "Some_non_str_obj"}]
    assert isinstance(request, list)
    assert isinstance(request[0], str)
    assert not isinstance(request[1], str)
    _, status_code = handler.process(method="POST", request=request)

    assert status_code == 400
    mock_db_session_rollback_call.assert_called_once()
    mock_db_session_add_call.assert_not_called()

def test_posting_with_empty_list(fixture_api_request):
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)

    # Request with an object, not a list.
    request_obj:list = []
    assert isinstance(request_obj, list)
    _, status_code = handler.process(method="POST", request=request_obj)

    assert status_code == 400
    mock_db_session_add_call.assert_not_called()

def test_posting_with_non_list(fixture_api_request):
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)

    # Request with an object, not a list.
    request_obj = {}
    assert not isinstance(request_obj, list)
    _, status_code = handler.process(method="POST", request=request_obj)

    assert status_code == 400
    mock_db_session_add_call.assert_not_called()

def test_non_post_methods_request(fixture_api_request):
    # Mock database interactions.
    mock_db_session, _, mock_db_session_add_call = fixture_api_request
    # Create the handler instance, passing the mock db session
    handler = RequestHandlerFactory.create_handler(\
        API_ENDPOINT_REQUEST, mock_db_session)
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

def test_non_post_methods_data(fixture_api_data):
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