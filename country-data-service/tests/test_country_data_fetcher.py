import pytest
from unittest.mock import Mock, patch
from chalicelib.country_service import CountryDataFetcher


class TestCountryDataFetcher:
    @pytest.fixture
    def country_data_fetcher(self):
        return CountryDataFetcher()

    @patch('chalicelib.country_service.requests.get')
    def test_fetch_country_data_success(self, mock_get, country_data_fetcher):
        mock_response = Mock()
        mock_response.json.return_value = [{"name": "France"}]
        mock_get.return_value = mock_response
        
        result = country_data_fetcher.fetch_country_data("France")
        
        assert result == {"name": "France"}
        mock_get.assert_called_once_with("https://restcountries.com/v3.1/name/France?fullText=true")

    @patch('chalicelib.country_service.requests.get')
    def test_fetch_country_data_not_found(self, mock_get, country_data_fetcher):
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        with pytest.raises(ValueError):
            country_data_fetcher.fetch_country_data("Nonexistent")
