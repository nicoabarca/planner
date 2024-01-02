from __future__ import annotations

import contextlib
from typing import Any

from redis.asyncio import BlockingConnectionPool, Redis

from app.settings import settings


def init_redis_pool() -> BlockingConnectionPool:
    pool: BlockingConnectionPool = BlockingConnectionPool.from_url(  # type: ignore
        settings.redis_uri,
        decode_responses=True,
        encoding="utf-8",
    )
    return pool


connection_pool = init_redis_pool()


@contextlib.asynccontextmanager
async def get_redis():
    """
    Get a Redis connection from the pool.

    Use with `async with` in order to close the connection at the end of the scope.
    """
    redis: Redis[Any] = Redis(
        connection_pool=connection_pool,
        auto_close_connection_pool=False,
        decode_responses=True,
        encoding="utf-8",
    )
    try:
        yield redis
    finally:
        await redis.close()
