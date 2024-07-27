import pytest
from unittest.mock import patch

from app.schemas import DBError
from app.utils import async_retry_on_exception


@async_retry_on_exception(max_retries=3, initial_delay=0.1, exceptions=(DBError,))
async def faulty_function():
    raise DBError("Simulated DB error")

@pytest.mark.asyncio
async def test_retry_mechanism():
    with patch('app.utils.logger.warning') as mock_warning:
        with pytest.raises(DBError):
            await faulty_function()
        assert mock_warning.call_count == 3
