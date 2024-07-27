import json
import asyncio

from pydantic import ValidationError

from app.db import TelemetryDB
from app.logging import logger
from app.schemas import Telemetry


async def lambda_handler(event, context):
    telemetries = event.get('telemetries', [])
    # Init the DB once for all telemetries insertions
    db = await TelemetryDB.init_db()

    await asyncio.gather(
        *(process_telemetry(telemetry_input, db) for telemetry_input in telemetries)
    )
    return {
        'statusCode': 200,
        "headers": {"Content-Type": "application/json"},
        'body': json.dumps('Telemetry processed successfully')
    }


async def process_telemetry(telemetry_input, db):
    try:
        telemetry = Telemetry(**telemetry_input)
        await db.insert_telemetry(telemetry)
    except ValidationError as e:
        logger.error(f'Telemetry data is in invalid format: {e.json()}')
