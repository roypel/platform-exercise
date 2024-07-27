import json
import asyncio


async def lambda_handler(event, context):
    telemetries = event.get('telemetries', [])
    await asyncio.gather(
        *(process_telemetry(telemetry) for telemetry in telemetries)
    )
    return {
        'statusCode': 200,
        "headers": {"Content-Type": "application/json"},
        'body': json.dumps('Telemetry processed successfully')
    }


async def process_telemetry(telemetry):
    pass
