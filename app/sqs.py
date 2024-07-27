import os

import aioboto3
from botocore.exceptions import ClientError

from app.logging import logger
from app.schemas import Acknowledgement
from app.utils import async_retry_on_exception


def get_acknowledgement_queue_url(status: str) -> str:
    """
    Map statuses to specific queue URLs
    :param status: Depending on the processing status, can be either success, or [db|validation|general]_error
    :return:
    """
    queue_mapping = {
        "success": os.getenv("success_sqs_queue", ""),
        "validation_error": os.getenv("validation_error_sqs_queue", ""),
        "db_error": os.getenv("db_error_sqs_queue", ""),
        "general_error": os.getenv("general_error_sqs_queue", ""),
    }
    return queue_mapping.get(status, os.getenv("default_sqs_queue", ""))


@async_retry_on_exception(max_retries=5, initial_delay=1, exceptions=(ClientError, TimeoutError))
async def send_acknowledgement(ack: Acknowledgement):
    """
    Handles sending acknowledgements to SQS queues, depending on the acknowledgement status
    :param ack: Object of type Acknowledgement which holds the status and the details to be sent
    :return:
    """
    queue_url = get_acknowledgement_queue_url(ack.status)
    logger.debug(f"sending message {ack.json()} to queue {queue_url}")
    async with aioboto3.client('sqs') as client:
        response = await client.send_message(
            QueueUrl=queue_url,
            MessageBody=ack.json()
        )
        return response
