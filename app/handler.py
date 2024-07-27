import json
import asyncio

from pydantic import ValidationError

from app.db import TelemetryDB
from app.logging import logger
from app.schemas import Telemetry, Acknowledgement, DBError
from app.sqs import send_acknowledgement


def lambda_handler(event, context):
    logger.info("got new message!")
    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(process_data(event, context))
        logger.info("finished processing message!")
        return {
            'statusCode': 200,
            "headers": {"Content-Type": "application/json"},
            'body': json.dumps('Telemetry processed successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            "headers": {"Content-Type": "application/json"},
            'body': json.dumps('Had errors while processing telemetry')
        }


async def process_data(event, context):
    logger.debug(event)
    telemetries = event.get('telemetries', [])
    # Init the DB once for all telemetries insertions
    db = await TelemetryDB.init_db()

    await asyncio.gather(
        *(process_telemetry(telemetry_input, db) for telemetry_input in telemetries)
    )


async def process_telemetry(telemetry_input, db):
    ack = None
    try:
        telemetry = Telemetry(**telemetry_input)
        db_id = await db.insert_telemetry(telemetry)
        ack = Acknowledgement(status="success", details={"telemetry_id": db_id})
    except ValidationError as e:
        logger.error(f'Telemetry data is in invalid format: {e.json()}')
        ack = Acknowledgement(status="invalid_format", details={"message": e.json()})
    except DBError as e:
        logger.error(f"Database error: {e}")
        ack = Acknowledgement(status="db_error", details={"message": e})
    except Exception as e:
        logger.error(f'Unhandled exception has occurred: {e}')
        ack = Acknowledgement(status="general_error", details={"message": e})
    finally:
        await send_acknowledgement(ack)
        logger.debug("Finished processing message")
