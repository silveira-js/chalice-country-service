import os
import json
import logging
from chalice import Chalice, BadRequestError
from chalicelib.country_service import CountryService
from chalicelib.rate_limiter import RateLimiter
from chalicelib.rate_limit_config import RATE_LIMITS
from botocore.exceptions import ClientError
from chalicelib.utils import validate_country

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app_name = 'country-data-service'
sqs_queue_name = app_name + '-data-fetch-queue'
app = Chalice(app_name=app_name)

sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
country_service = CountryService(sqs_queue_url)

rate_limiter = RateLimiter(app, RATE_LIMITS)

@app.route('/')
def index():
    return {
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
        'rate_limits': 'API calls are subject to rate limiting'
    }

@app.route('/fetch/{country}', methods=['GET'])
@rate_limiter.limit()
@validate_country(country_service)
def fetch_country_data(country):
    logger.info(f"Fetching data for country: {country}")

    result = country_service.fetch_country_data(country)

    logger.info(f"Fetch result: {result}")
    return result

@app.route('/country/{country}', methods=['GET'])
@rate_limiter.limit()
@validate_country(country_service)
def get_country_data(country):
    return country_service.get_country_data(country)

@app.route('/status/{country}', methods=['GET'])
@rate_limiter.limit()
@validate_country(country_service)
def check_operation_status(country):
    return country_service.check_operation_status(country)

@app.on_sqs_message(queue=sqs_queue_name)
def handle_sqs_message(event):
    successful_messages = []
    failed_messages = []

    for record in event:
        try:
            if isinstance(record.body, dict):
                message_body = record.body
            else:
                message_body = json.loads(record.body)
            
            country = message_body.get('country')
            
            if not country:
                raise ValueError("Missing 'country' key in message")

            logger.info(f"Processing SQS message for country: {country}")
            
            if country_service.fetch_and_save_country_data(country):
                logger.info(f"Successfully processed data for {country}")
                successful_messages.append(record)
            else:
                logger.error(f"Failed to process data for {country}")
                failed_messages.append((record, f"Failed to process data for {country}"))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {str(e)}")
            failed_messages.append((record, f"Invalid JSON: {str(e)}"))
        except ValueError as e:
            logger.error(str(e))
            failed_messages.append((record, str(e)))
        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}")
            failed_messages.append((record, f"Unexpected error: {str(e)}"))

    if failed_messages:
        # Manually delete successful messages
        for record in successful_messages:
            try:
                country_service.queue_service.delete_message(record.receipt_handle)
            except ClientError as e:
                logger.error(f"Error deleting message: {e}")

        # Prepare error information for failed messages
        error_info = [
            {"error": error}
            for _, error in failed_messages
        ]

        # Throw an aggregate error
        raise BadRequestError(f"Failed to process {len(failed_messages)} messages: {json.dumps(error_info)}")

    # If all messages were processed successfully, do nothing
    # The poller will automatically delete the messages from the queue