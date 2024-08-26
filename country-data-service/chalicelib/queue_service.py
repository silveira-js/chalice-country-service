import boto3
import json
import logging
import os
from botocore.exceptions import ClientError

logger = logging.getLogger()

sqs_client = None


def initialize_sqs_client(sqs_queue_url):
    global sqs_client
    if sqs_client is None:
        try:
            sqs_client = boto3.client('sqs', endpoint_url=sqs_queue_url)
        except ClientError as err:
            raise
    return sqs_client


class QueueService:
    def __init__(self, queue_url):
        self.queue_url = queue_url
        self.sqs = initialize_sqs_client(queue_url)

    def send_message(self, message_body):
        try:
            logger.info(f"Sending message to queue: {message_body}")
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body)
            )
            return response['MessageId']
        except ClientError as e:
            logger.error(f"Error sending message to SQS: {e}")
            raise

    def receive_message(self):
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=10
            )
            messages = response.get('Messages', [])
            if messages:
                return json.loads(messages[0]['Body']), messages[0]['ReceiptHandle']
            return None, None
        except ClientError as e:
            logger.error(f"Error receiving message from SQS: {e}")
            raise

    def delete_message(self, receipt_handle):
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        except ClientError as e:
            logger.error(f"Error deleting message from SQS: {e}")
            raise
