import asyncio
import json
import os
import asyncpg
from asyncpg import ConnectionDoesNotExistError, ConnectionFailureError, TooManyConnectionsError

from app.logging import logger
from app.schemas import Telemetry


async def _init_connection(conn):
    await conn.set_type_codec(
        "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


# Generic DB interface, will sit in a shared codebase and provide basic DB utilities to reduce boilerplate code
class DBInterface:
    @classmethod
    async def init_db(
            cls,
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            name=os.getenv("DB_NAME", "postgres"),
    ):
        db = cls()
        await db.init(host, port, user, password, name)
        return db

    def __init__(self):
        self._connection_pool = None

    async def init(self, host: str, port: int, user: str, password: str, name: str):
        # In case we have a warm start, reuse existing connection pool
        if self._connection_pool is not None:
            return

        self._connection_pool = await asyncpg.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            database=name,
            init=_init_connection,
        )

    async def _close(self, timeout=60.0):
        await asyncio.wait_for(self._connection_pool.close(), timeout=timeout)
        self._connection_pool = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._close()


class TelemetryDB(DBInterface):
    async def insert_telemetry(self, telemetry: Telemetry):
        try:
            # Use upsert to update existing data in case it is needed
            await self._connection_pool.execute(
                """
                INSERT INTO telemetry (source, timestamp, data)
                VALUES ($1, $2, $3)
                ON CONFLICT (source, timestamp) DO UPDATE SET data = $3, updated_at = now()
                """,
                telemetry.source, telemetry.timestamp, telemetry.data
            )
        except (ConnectionDoesNotExistError, ConnectionFailureError, TooManyConnectionsError) as conn_err:
            logger.warning(f"Connection error: {conn_err}")
