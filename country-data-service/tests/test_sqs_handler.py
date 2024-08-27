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

    result = handle_sqs_message(event, mock_context)

    assert result == {"batchItemFailures": []}
    assert mock_country_service.fetch_and_save_country_data.call_count == 2
    mock_logger.info.assert_any_call("Processing SQS message for country: france")
    mock_logger.info.assert_any_call("Successfully processed data for france")
    mock_logger.info.assert_any_call("Processing SQS message for country: germany")
    mock_logger.info.assert_any_call("Successfully processed data for germany")
    mock_logger.info.assert_called_with("Successfully processed 2 messages")

def test_handle_sqs_message_partial_failure(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"country": "france"}, {"country": "germany"}])
    mock_country_service.fetch_and_save_country_data.side_effect = [True, False]

    result = handle_sqs_message(event, mock_context)

    assert result == {"batchItemFailures": [{"itemIdentifier": "Failed to process data for germany"}]}
    mock_logger.error.assert_called_with('Failed to process 1 messages: [{"error": "Failed to process data for germany"}]')
    mock_logger.info.assert_called_with("Successfully processed 1 messages")

def test_handle_sqs_message_json_decode_error(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event(["invalid json"])

    result = handle_sqs_message(event, mock_context)

    assert len(result["batchItemFailures"]) == 1
    assert "Invalid JSON" in result["batchItemFailures"][0]["itemIdentifier"]
    mock_logger.error.assert_called_with('Failed to process 1 messages: [{"error": "Invalid JSON: Expecting value: line 1 column 1 (char 0)"}]')

def test_handle_sqs_message_missing_key(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"not_country": "france"}])

    result = handle_sqs_message(event, mock_context)

    assert result == {"batchItemFailures": [{"itemIdentifier": "Missing 'country' key in message"}]}
    mock_logger.error.assert_called_with('Failed to process 1 messages: [{"error": "Missing \'country\' key in message"}]')

def test_handle_sqs_message_unexpected_error(mock_country_service, mock_logger, mock_context):
    event = create_sqs_event([{"country": "france"}])
    mock_country_service.fetch_and_save_country_data.side_effect = Exception("Unexpected error")

    result = handle_sqs_message(event, mock_context)

    assert result == {"batchItemFailures": [{"itemIdentifier": "Unexpected error: Unexpected error"}]}
    mock_logger.error.assert_called_with('Failed to process 1 messages: [{"error": "Unexpected error: Unexpected error"}]')