import pytest
from unittest.mock import Mock, patch
from chalicelib.db_service import DynamoDBService
from botocore.exceptions import ClientError


class TestDynamoDBService:
    @pytest.fixture
    def dynamodb_service(self):
        with patch('chalicelib.db_service.boto3.resource') as mock_resource:
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table
            service = DynamoDBService()
            service.country_table = mock_table
            service.operation_table = mock_table
            yield service
            mock_table.reset_mock()

    def test_save_country_data_success(self, dynamodb_service):
        dynamodb_service.country_table.put_item.return_value = {}
        
        result = dynamodb_service.save_country_data("france", {"name": "France"})
        
        assert result == True
        dynamodb_service.country_table.put_item.assert_called_once()

    def test_save_country_data_already_exists(self, dynamodb_service):
        dynamodb_service.country_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ConditionalCheckFailedException'}},
            'PutItem'
        )
        
        result = dynamodb_service.save_country_data("france", {"name": "France"})
        
        assert result == False

    def test_get_country_data_success(self, dynamodb_service):
        dynamodb_service.country_table.get_item.return_value = {'Item': {'data': {'name': 'France'}}}
        
        result = dynamodb_service.get_country_data("france")
        
        assert result == {'name': 'France'}

    def test_get_country_data_not_found(self, dynamodb_service):
        dynamodb_service.country_table.get_item.return_value = {}
        
        result = dynamodb_service.get_country_data("nonexistent")
        
        assert result == None

    def test_save_operation_status(self, dynamodb_service):
        dynamodb_service.operation_table.put_item.return_value = {}
        
        dynamodb_service.save_operation_status("france", "PENDING")
        
        dynamodb_service.operation_table.put_item.assert_called_once()

    def test_get_operation_status_success(self, dynamodb_service):
        dynamodb_service.operation_table.query.return_value = {'Items': [{'status': 'COMPLETED'}]}
        
        result = dynamodb_service.get_operation_status("france")
        
        assert result == {'status': 'COMPLETED'}

    def test_get_operation_status_not_found(self, dynamodb_service):
        dynamodb_service.operation_table.query.return_value = {'Items': []}
        
        result = dynamodb_service.get_operation_status("nonexistent")
        
        assert result == None

    def test_is_operation_in_progress_true(self, dynamodb_service):
        dynamodb_service.get_operation_status = Mock(return_value={'status': 'PENDING'})
        
        result = dynamodb_service.is_operation_in_progress("france")
        
        assert result == True

    def test_is_operation_in_progress_false(self, dynamodb_service):
        dynamodb_service.get_operation_status = Mock(return_value={'status': 'COMPLETED'})
        
        result = dynamodb_service.is_operation_in_progress("france")
        
        assert result == False

