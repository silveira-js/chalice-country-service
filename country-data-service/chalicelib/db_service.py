import boto3
import os
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import json
import logging
from .utils import float_to_decimal, DecimalEncoder


logger = logging.getLogger()

dynamo_db_client = None

def initialize_dynamodb_client():
    global dynamo_db_client

    if dynamo_db_client is None:
        try:
            dynamo_db_client = boto3.resource('dynamodb')
        except ClientError as err:
            raise

    return dynamo_db_client


class DynamoDBService:
    def __init__(self):
        self.dynamodb = initialize_dynamodb_client()
        self.country_table = self.dynamodb.Table('country-data-service-country-data')
        self.operation_table = self.dynamodb.Table('country-data-service-operation-status')

    def save_country_data(self, country, data):
        try:
            decimal_data = float_to_decimal(data)
            self.country_table.put_item(
                Item={'country': country, 'data': decimal_data},
                ConditionExpression='attribute_not_exists(country)'
            )
            logger.info(f"Saved new data for country: {country}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                logger.info(f"Data already exists for country: {country}")
                return False
            else:
                logger.error(f"Error saving country data: {e}")
                raise

    def get_country_data(self, country):
        try:
            response = self.country_table.get_item(Key={'country': country})
            item = response.get('Item', {})
            if 'data' in item:
                logger.info(f"Retrieved data for country: {country}")
                return json.loads(json.dumps(item['data'], cls=DecimalEncoder))

            logger.info(f"No data found for country: {country}")
            return None
        except ClientError as e:
            logger.error(f"Error getting country data: {e}")
            raise

    def save_operation_status(self, country, status, error=None):
        try:
            timestamp = int(time.time() * 1000)
            item = {
                'country': country,
                'timestamp': timestamp,
                'status': status
            }
            if error:
                item['error'] = error
            self.operation_table.put_item(Item=item)
            logger.info(f"Saved operation status for country: {country}, status: {status}, timestamp: {timestamp}")
            return True
        except ClientError as e:
            logger.error(f"Error saving operation status: {e}")
            raise

    def get_operation_status(self, country):
        try:
            response = self.operation_table.query(
                KeyConditionExpression=Key('country').eq(country),
                ScanIndexForward=False,
                Limit=1
            )
            items = response.get('Items', [])
            if items:
                logger.info(f"Retrieved latest operation status for country: {country}")
                return items[0]
            else:
                logger.info(f"No operation status found for country: {country}")
                return None
        except ClientError as e:
            logger.error(f"Error getting operation status: {e}")
            raise

    def is_operation_in_progress(self, country):
        status = self.get_operation_status(country)
        return status and status['status'] == 'PENDING'