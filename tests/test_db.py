import pytest

from app.db import TelemetryDB
from app.schemas import DBError
from tests.data import telemetry, broken_telemetry


@pytest.mark.asyncio
async def test_db_insertion():
    db = await TelemetryDB.init_db()
    db_id = await db.insert_telemetry(telemetry)
    result = await db._connection_pool.fetchrow('SELECT source, timestamp, data FROM telemetry WHERE id=$1', db_id)
    assert dict(result) == telemetry.model_dump()


@pytest.mark.asyncio
async def test_db_insertion_error():
    db = await TelemetryDB.init_db()
    with pytest.raises(DBError):
        db_id = await db.insert_telemetry(broken_telemetry)
