import pytest
from unittest.mock import Mock, patch
from chalice import NotFoundError
from chalicelib.country_service import CountryService


class TestCountryService:
    @pytest.fixture
    def mock_db_service(self):
        with patch('chalicelib.country_service.DynamoDBService') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_queue_service(self):
        with patch('chalicelib.country_service.QueueService') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_country_data_fetcher(self):
        with patch('chalicelib.country_service.CountryDataFetcher') as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def country_service(self, mock_db_service, mock_queue_service, mock_country_data_fetcher):
        with patch('chalicelib.country_service.DynamoDBService', return_value=mock_db_service), \
             patch('chalicelib.country_service.QueueService', return_value=mock_queue_service), \
             patch('chalicelib.country_service.CountryDataFetcher', return_value=mock_country_data_fetcher):
            return CountryService("http://fake-queue-url")

    def test_standardize_country_identifier(self, country_service):
        assert country_service.standardize_country_identifier("United States") == "united-states"
        assert country_service.standardize_country_identifier("North Korea") == "north-korea"

    def test_fetch_country_data_new_country(self, country_service, mock_db_service, mock_queue_service):
        mock_db_service.get_country_data.return_value = None
        mock_db_service.is_operation_in_progress.return_value = False
        
        result = country_service.fetch_country_data("France")
        
        assert result == {"country": "france", "status": "PENDING"}
        mock_db_service.save_operation_status.assert_called_once_with("france", "PENDING")
        mock_queue_service.send_message.assert_called_once()

    def test_fetch_country_data_existing_country(self, country_service, mock_db_service):
        mock_db_service.get_country_data.return_value = {"name": "France"}
        
        result = country_service.fetch_country_data("France")
        
        assert result == {"country": "france", "status": "COMPLETED"}

    def test_fetch_country_data_operation_in_progress(self, country_service, mock_db_service):
        mock_db_service.get_country_data.return_value = None
        mock_db_service.is_operation_in_progress.return_value = True
        
        result = country_service.fetch_country_data("France")
        
        assert result == {"country": "france", "status": "PENDING"}

    @patch('chalicelib.country_service.CountryDataFetcher')
    def test_fetch_and_save_country_data_success(self, mock_fetcher, country_service, mock_db_service):
        country_service.country_data_fetcher.fetch_country_data.return_value = {"name": "France"}
        mock_db_service.save_country_data.return_value = True
        
        result = country_service.fetch_and_save_country_data("France")
        
        assert result == True
        mock_db_service.save_operation_status.assert_called_with("france", "COMPLETED")

    @patch('chalicelib.country_service.CountryDataFetcher')
    def test_fetch_and_save_country_data_failure(self, MockCountryDataFetcher, country_service, mock_db_service):
        country_service.country_data_fetcher.fetch_country_data.side_effect = Exception("API Error")
        
        result = country_service.fetch_and_save_country_data("France")
        
        assert result == False
        mock_db_service.save_operation_status.assert_called_with("france", "FAILED", "API Error")

    def test_get_country_data_success(self, country_service, mock_db_service):
        mock_db_service.get_country_data.return_value = {"name": "France"}
        
        result = country_service.get_country_data("France")
        
        assert result == {"name": "France"}

    def test_get_country_data_not_found(self, country_service, mock_db_service):
        mock_db_service.get_country_data.return_value = None
        
        with pytest.raises(NotFoundError):
            country_service.get_country_data("Nonexistent")

    def test_check_operation_status_success(self, country_service, mock_db_service):
        mock_db_service.get_operation_status.return_value = {"status": "COMPLETED"}
        
        result = country_service.check_operation_status("France")
        
        assert result == {"status": "COMPLETED"}

    def test_check_operation_status_not_found(self, country_service, mock_db_service):
        mock_db_service.get_operation_status.return_value = None
        
        with pytest.raises(NotFoundError):
            country_service.check_operation_status("Nonexistent")