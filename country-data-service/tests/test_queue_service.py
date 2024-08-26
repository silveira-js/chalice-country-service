import pytest
from unittest.mock import Mock, patch
from chalice import NotFoundError
from chalicelib.country_service import CountryService, CountryDataFetcher
from chalicelib.db_service import DynamoDBService
from chalicelib.queue_service import QueueService
from chalicelib.rate_limiter import RateLimiter
from botocore.exceptions import ClientError


# QueueService tests
class TestQueueService:
    @pytest.fixture
    def queue_service(self):
        with patch('chalicelib.queue_service.boto3.client') as mock_client:
            mock_client.return_value = Mock()
            service = QueueService("http://fake-queue-url")
            service.sqs = mock_client.return_value
            yield service
            

    def test_send_message_success(self, queue_service):
        queue_service.sqs.send_message.return_value = {"MessageId": "123"}
        
        result = queue_service.send_message({"country": "france"})
        
        assert result == "123"
        queue_service.sqs.send_message.assert_called_once()

    def test_send_message_failure(self, queue_service):
        queue_service.sqs.send_message.side_effect = ClientError({}, 'SendMessage')
        
        with pytest.raises(ClientError):
            queue_service.send_message({"country": "france"})

    def test_receive_message_success(self, queue_service):
        queue_service.sqs.receive_message.return_value = {
            'Messages': [{'Body': '{"country": "france"}', 'ReceiptHandle': 'receipt123'}]
        }
        
        message, receipt = queue_service.receive_message()
        
        assert message == {"country": "france"}
        assert receipt == "receipt123"

    def test_receive_message_empty(self, queue_service):
        queue_service.sqs.receive_message.return_value = {}
        
        message, receipt = queue_service.receive_message()
        
        assert message == None
        assert receipt == None

    def test_delete_message_success(self, queue_service):
        queue_service.sqs.delete_message.return_value = {}
        
        queue_service.delete_message("receipt123")
        
        queue_service.sqs.delete_message.assert_called_once_with(
            QueueUrl="http://fake-queue-url",
            ReceiptHandle="receipt123"
        )

    def test_delete_message_failure(self, queue_service):
        queue_service.sqs.delete_message.side_effect = ClientError({}, 'DeleteMessage')
        
        with pytest.raises(ClientError):
            queue_service.delete_message("receipt123")
