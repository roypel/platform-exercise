import asyncio
from random import randint
from functools import wraps

from app.logger import logger


def async_retry_on_exception(max_retries=5, initial_delay=1, exceptions=(Exception,)):
    """
    Wrapper to perform exponential backoff retry mechanism
    :param max_retries: Amount of times to retry operation
    :param initial_delay: Initial wait in seconds, that will be exponentially raised in each attempt
    :param exceptions: List of exceptions that will be caught and retried, other exceptions won't be retried but raise
    :return:
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    wait_time = initial_delay * (2 ** (attempt - 1)) + randint(0, 1000) / 1000
                    logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}. Retrying in {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            logger.error("Max retries exceeded. Operation failed.")
            raise
        return wrapper
    return decorator
