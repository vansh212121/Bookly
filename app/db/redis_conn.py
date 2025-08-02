# In app/db/redis_conn.py
import redis.asyncio as redis
from app.core.config import settings

# Create an asynchronous Redis client instance
# This will be our connection to the running Redis server
redis_client = redis.from_url(
    # f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    f"{settings.REDIS_URL}",
    encoding="utf-8",
    decode_responses=True
)