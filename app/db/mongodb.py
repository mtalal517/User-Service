from typing import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.config.config import Settings


class MongoConnectionManager:
    """Wraps a Motor client for explicit lifecycle management."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None

    async def connect(self) -> AsyncIterator[AsyncIOMotorClient]:
        self._client = AsyncIOMotorClient(self._settings.mongodb_uri)
        try:
            yield self._client
        finally:
            if self._client is not None:
                self._client.close()

    def collection(self) -> AsyncIOMotorCollection:
        if self._client is None:
            raise RuntimeError("Mongo client is not initialized; did you set up lifespan?")
        return self._client[self._settings.mongodb_db][self._settings.mongodb_collection]
