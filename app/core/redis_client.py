from redis.asyncio import from_url
from app.core.config import settings

redis = from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,  # str en lugar de bytes
)