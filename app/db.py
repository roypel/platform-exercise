import asyncio
import json
import os
import asyncpg

from app.logger import logger
from app.schemas import Telemetry, DBError
from app.utils import async_retry_on_exception


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
            logger.info("db already initialized")
            return

        logger.info("initializing db")
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
    @async_retry_on_exception(max_retries=5, initial_delay=1,
                              exceptions=(DBError,))
    async def insert_telemetry(self, telemetry: Telemetry):
        """
        Insert telemetry data into the DB as a single row
        In case a similar row appears (with the same source and timestamp), update with the new data
        :param telemetry: An object with validated telemetry fields
        :return: The ID of the new added row
        """
        logger.debug(f"inserting data: {telemetry.dict}")
        try:
            # Use upsert to update existing data in case it is needed
            db_id = await self._connection_pool.execute(
                """
                INSERT INTO telemetry (source, timestamp, data)
                VALUES ($1, $2, $3)
                ON CONFLICT (source, timestamp) DO UPDATE SET data = $3, updated_at = now()
                RETURNING id
                """,
                telemetry.source, telemetry.timestamp, telemetry.data
            )
            return db_id
        except (asyncpg.PostgresConnectionError, asyncpg.PostgresError) as e:
            raise DBError("A database error occurred") from e
