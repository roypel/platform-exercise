import os

import aioboto3
from botocore.exceptions import ClientError

from app.logger import logger
from app.schemas import Acknowledgement
from app.utils import async_retry_on_exception

session = aioboto3.Session()


def get_acknowledgement_queue_url(status: str) -> str:
    """
    Map statuses to specific queue URLs
    :param status: Depending on the processing status, can be either success, or [db|validation|general]_error
    :return:
    """
    queue_mapping = {
        "success": os.getenv("success_sqs_queue", "success_queue"),
        "validation_error": os.getenv("validation_error_sqs_queue", "validation_error_queue"),
        "db_error": os.getenv("db_error_sqs_queue", "db_error_queue"),
        "general_error": os.getenv("general_error_sqs_queue", "general_error_queue"),
    }
    return queue_mapping.get(status, os.getenv("default_sqs_queue", "default_queue"))


@async_retry_on_exception(max_retries=5, initial_delay=1, exceptions=(ClientError, TimeoutError))
async def send_acknowledgement(ack: Acknowledgement, queue_url: str, endpoint_url=None):
    """
    Handles sending acknowledgements to SQS queues, depending on the acknowledgement status
    :param ack: Object of type Acknowledgement which holds the status and the details to be sent
    :param queue_url: The URL of the queue to send the message to
    :return:
    """
    logger.debug(f"sending message {ack.json()} to queue {queue_url}")
    async with session.client('sqs', region_name='us-east-1', endpoint_url=endpoint_url) as client:
        response = await client.send_message(
            QueueUrl=queue_url,
            MessageBody=ack.model_dump_json(),
        )
        return response
