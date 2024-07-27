import json

import boto3
import pytest

from app.sqs import get_acknowledgement_queue_url, send_acknowledgement
from tests.data import ack


@pytest.mark.parametrize('status, expected_queue_url',
                         (
                                 ("success", "success_queue"),
                                 ("validation_error", "validation_error_queue"),
                                 ("db_error", "db_error_queue"),
                                 ("general_error", "general_error_queue"),
                                 ("unsupported", "default_queue")
                         ))
def test_get_acknowledgement_queue_url(status, expected_queue_url):
    assert get_acknowledgement_queue_url(status) == expected_queue_url


@pytest.fixture(scope="module")
def sqs_client():
    client = boto3.client(
        'sqs',
        region_name='us-east-1',
        endpoint_url='http://localstack:4566',
        aws_access_key_id='test',
        aws_secret_access_key='test'
    )
    return client


@pytest.mark.asyncio
async def test_sqs_send_message(sqs_client):
    response = sqs_client.create_queue(QueueName='success_queue')
    queue_url = response['QueueUrl']

    await send_acknowledgement(ack, queue_url, 'http://localstack:4566')

    messages = sqs_client.receive_message(QueueUrl=queue_url)

    assert ack.model_dump() == json.loads(messages['Messages'][0]['Body'])
