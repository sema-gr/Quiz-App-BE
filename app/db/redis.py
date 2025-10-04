import redis.asyncio as redis
from typing import Optional
from app.core.settings import settings


class RedisClient:
    def __init__(self, url: str):
        self._url = url
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        if not self._client:
            self._client = redis.from_url(self._url, decode_responses=True)
            try:
                await self._client.ping()
                print("Connect to Redis")
            except redis.ConnectionError as e:
                print(f"Connection error to Redis: {e}")
                self._client = None

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
            print("Disconnect from Redis")

    async def set(self, key, value, expire: Optional[int]):
        if not self._client:
            await self.connect()
        return await self._client.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        if not self._client:
            await self.connect()
        return await self._client.get(key)

    async def delete(self, key: str) -> int:
        if not self._client:
            await self.connect()
        return await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        if not self._client:
            await self.connect()
        return bool(await self._client.exists(key))


redis_client = RedisClient(settings.redis_url)
