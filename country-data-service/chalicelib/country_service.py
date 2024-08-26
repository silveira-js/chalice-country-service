import requests
import logging
from chalice import NotFoundError
from .queue_service import QueueService
from .db_service import DynamoDBService

logger = logging.getLogger()

class CountryService:
    def __init__(self, queue_url):
        self.db_service = DynamoDBService()
        self.queue_service = QueueService(queue_url)
        self.country_data_fetcher = CountryDataFetcher()

    def standardize_country_identifier(self, country: str) -> str:
        return country.lower().replace(' ', '-')

    # TODO: Future Improvement
    # - Update database schema to include ISO alpha-2 and alpha-3 codes
    # - Modify db_service to support querying by ISO codes
    # - Update this method to handle ISO code inputs and check existence using multiple identifiers
    def fetch_country_data(self, country):
        country = self.standardize_country_identifier(country)
        existing_data = self.db_service.get_country_data(country)
        if existing_data:
            logger.info(f"Data already exists for country: {country}")
            return {"country": country, "status": "COMPLETED"}

        if self.db_service.is_operation_in_progress(country):
            logger.info(f"Operation already in progress for country: {country}")
            return {"country": country, "status": "PENDING"}

        logger.info(f"Fetching data for country: {country}")

        self.db_service.save_operation_status(country, "PENDING")

        message_body = {
            'country': country
        }
        self.queue_service.send_message(message_body)

        logger.info(f"Sent message to queue for country: {country}")

        return {"country": country, "status": "PENDING"}
    
    # TODO: Future Improvement
    # - Update this method to extract and save ISO codes when storing country data
    def fetch_and_save_country_data(self, country: str) -> bool:
        try:
            country = self.standardize_country_identifier(country)
            logger.info(f"Fetching and saving data for country: {country}")

            country_data = self.country_data_fetcher.fetch_country_data(country)
            saved = self.db_service.save_country_data(country, country_data)
            
            self.db_service.save_operation_status(country, "COMPLETED")
            logger.info(f"Successfully fetched and saved new data for country: {country}")

            return True
        except Exception as e:
            logger.error(f"Failed to fetch and save data for country: {country}, error: {str(e)}")
            self.db_service.save_operation_status(country, "FAILED", str(e))
            return False

    def get_country_data(self, country):
        country = self.standardize_country_identifier(country)
        logger.info(f"Getting data for country: {country}")

        country_data = self.db_service.get_country_data(country)

        if not country_data:
            raise NotFoundError(f"Country data for '{country}' not found")

        logger.info(f"Successfully retrieved data for country: {country}")
        return country_data

    def check_operation_status(self, country):
        country = self.standardize_country_identifier(country)
        logger.info(f"Checking operation status for country: {country}")
        status = self.db_service.get_operation_status(country)
        if not status:
            raise NotFoundError(f"No operation found for country '{country}'")
        logger.info(f"Operation status for country: {country} is: {status['status']}")
        return status

    def validate_country_name(self, country: str) -> bool:
        # Country name should be more than 3 letters and only contain letters and hyphens
        return len(country) > 3 and all(c.isalpha() or c == '-' for c in country)

class CountryDataFetcher:
    def __init__(self):
        self.base_url = "https://restcountries.com/v3.1"

    def fetch_country_data(self, country: str):
        logger.info(f"Fetching data for country: {country}")

        country = country.replace('-', ' ').strip()
        url = f"{self.base_url}/name/{country}?fullText=true"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            logger.info(f"Successfully fetched data for country: {country}")
            return data[0]  # Return only the first match
        else:
            raise ValueError(f"No data found for country: {country}")
