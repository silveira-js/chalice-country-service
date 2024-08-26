import pytest
from chalice.test import Client
from app import app
from unittest.mock import patch
from chalice import NotFoundError, BadRequestError
import json

@pytest.fixture
def test_client():
    return Client(app)

def test_index_route(test_client):
    response = test_client.http.get("/")
    assert response.status_code == 200
    assert response.json_body == {
        'service': 'Country Data API',
        'version': '1.0.0',
        'description': 'Provides information about countries, including fetching and storing country data.',
        'endpoints': {
            '/fetch/{country}': 'GET - Fetch country data from external API',
            '/country/{country}': 'GET - Retrieve stored country data',
            '/status/{country}': 'GET - Check operation status for a country'
        },
        'usage': 'Replace {country} with a country name. For multi-word country names, use dashes (e.g., "united-states").',
        'examples': [
            '/fetch/france',
            '/country/united-kingdom',
            '/status/new-zealand'
        ],
        'rate_limits': 'API calls are subject to rate limiting',
        'documentation': 'For full API documentation, visit https://api-docs.example.com'
    }

@patch('app.country_service.fetch_country_data')
def test_initiate_country_fetch(mock_fetch, test_client):
    mock_fetch.return_value = {"country": "france", "status": "PENDING"}
    response = test_client.http.get("/fetch/france")
    assert response.status_code == 200
    assert response.json_body == {"country": "france", "status": "PENDING"}

def test_initiate_fetch_invalid_country(test_client):
    response = test_client.http.get("/fetch/123")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

@patch('app.country_service.get_country_data')
def test_retrieve_country_info(mock_get_data, test_client):
    mock_get_data.return_value = {"name": "France", "capital": "Paris"}
    response = test_client.http.get("/country/france")
    assert response.status_code == 200
    assert response.json_body == {"name": "France", "capital": "Paris"}

@patch('app.country_service.get_country_data')
def test_retrieve_nonexistent_country(mock_get_data, test_client):
    mock_get_data.side_effect = NotFoundError("Country not found")
    response = test_client.http.get("/country/narnia")
    assert response.status_code == 404
    assert "Country not found" in response.json_body["Message"]

@patch('app.country_service.check_operation_status')
def test_check_fetch_status(mock_check_status, test_client):
    mock_check_status.return_value = {"status": "COMPLETED"}
    response = test_client.http.get("/status/france")
    assert response.status_code == 200
    assert response.json_body == {"status": "COMPLETED"}

@patch('app.country_service.check_operation_status')
def test_check_status_no_operation(mock_check_status, test_client):
    mock_check_status.side_effect = NotFoundError("No operation found")
    response = test_client.http.get("/status/narnia")
    assert response.status_code == 404
    assert "No operation found" in response.json_body["Message"]

@patch('app.country_service.fetch_and_save_country_data')
def test_fetch_and_save_country_data(mock_fetch_and_save, test_client):
    mock_fetch_and_save.return_value = True
    event = test_client.events.generate_sqs_event([json.dumps({"country": "france"})])
    response = test_client.lambda_.invoke("handle_sqs_message", event)
    assert response.payload is None
    mock_fetch_and_save.assert_called_once_with("france")

@patch('app.country_service.fetch_and_save_country_data')
def test_fetch_and_save_country_data_failure(mock_fetch_and_save, test_client):
    mock_fetch_and_save.return_value = False
    event = test_client.events.generate_sqs_event([json.dumps({"country": "france"})])
    with pytest.raises(BadRequestError, match="Failed to process 1 messages"):
        test_client.lambda_.invoke("handle_sqs_message", event)

def test_fetch_invalid_country_name_too_short(test_client):
    response = test_client.http.get("/fetch/ab")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

def test_fetch_invalid_country_name_with_numbers(test_client):
    response = test_client.http.get("/fetch/france123")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

def test_fetch_invalid_country_name_with_special_characters(test_client):
    response = test_client.http.get("/fetch/france!")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

def test_retrieve_country_info_invalid_name(test_client):
    response = test_client.http.get("/country/fr")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

def test_check_fetch_status_invalid_name(test_client):
    response = test_client.http.get("/status/12")
    assert response.status_code == 400
    assert "Invalid country name" in response.json_body["Message"]

def test_fetch_valid_country_name_with_hyphen(test_client):
    with patch('app.country_service.fetch_country_data') as mock_fetch:
        mock_fetch.return_value = {"country": "costa-rica", "status": "PENDING"}
        response = test_client.http.get("/fetch/costa-rica")
        assert response.status_code == 200
        assert response.json_body == {"country": "costa-rica", "status": "PENDING"}
