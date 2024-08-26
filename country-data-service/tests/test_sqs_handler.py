import json
import pytest
from unittest.mock import Mock, patch
from chalice import BadRequestError
from app import handle_sqs_message

@pytest.fixture
def mock_country_service():
    with patch('app.country_service') as mock:
        yield mock

@pytest.fixture
def mock_logger():
    with patch('app.logger') as mock:
        yield mock

@pytest.fixture
def mock_context():
    return Mock()

def create_sqs_event(messages):
    return {
        'Records': [
            {
                'body': message,
                'receiptHandle': f'receipt{i}'
            }
            for i, message in enumerate(messages, 1)
        ]
    }

def test_handle_sqs_message_success(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"country": "france"}, {"country": "germany"}])
    mock_country_service.fetch_and_save_country_data.return_value = True

    handle_sqs_message(event, mock_context)

    assert mock_country_service.fetch_and_save_country_data.call_count == 2
    mock_logger.info.assert_any_call("Processing SQS message for country: france")
    mock_logger.info.assert_any_call("Successfully processed data for france")
    mock_logger.info.assert_any_call("Processing SQS message for country: germany")
    mock_logger.info.assert_any_call("Successfully processed data for germany")

def test_handle_sqs_message_partial_failure(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"country": "france"}, {"country": "germany"}])
    mock_country_service.fetch_and_save_country_data.side_effect = [True, False]

    with pytest.raises(BadRequestError) as excinfo:
        handle_sqs_message(event, mock_context)

    assert "Failed to process 1 messages" in str(excinfo.value)
    mock_country_service.queue_service.delete_message.assert_called_once_with("receipt1")
    mock_logger.error.assert_called_with("Failed to process data for germany")

def test_handle_sqs_message_json_decode_error(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event(["invalid json"])

    with pytest.raises(BadRequestError) as excinfo:
        handle_sqs_message(event, mock_context)

    assert "Failed to process 1 messages" in str(excinfo.value)
    assert "Invalid JSON" in str(excinfo.value)
    mock_logger.error.assert_called_with("Invalid JSON in message: Expecting value: line 1 column 1 (char 0)")

def test_handle_sqs_message_missing_key(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"not_country": "france"}])

    with pytest.raises(BadRequestError) as excinfo:
        handle_sqs_message(event, mock_context)

    assert "Failed to process 1 messages" in str(excinfo.value)
    assert "Missing 'country' key in message" in str(excinfo.value)
    mock_logger.error.assert_called_with("Missing 'country' key in message")

def test_handle_sqs_message_unexpected_error(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"country": "france"}])
    mock_country_service.fetch_and_save_country_data.side_effect = Exception("Unexpected error")

    with pytest.raises(BadRequestError) as excinfo:
        handle_sqs_message(event, mock_context)

    assert "Failed to process 1 messages" in str(excinfo.value)
    assert "Unexpected error" in str(excinfo.value)
    mock_logger.error.assert_called_with("Unexpected error processing message: Unexpected error")