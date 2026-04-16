import json
import hashlib
from upstash_redis import Redis
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

redis = Redis(
    url=settings.upstash_redis_url,
    token=settings.upstash_redis_token
)

CACHE_TTL = 60 * 60 * 24 * 7

def _make_key(question: str) -> str:
    normalized = question.lower().strip()
    return f"cache:{hashlib.md5(normalized.encode()).hexdigest()}"

async def get_from_cache(question: str) -> dict | None:
    try:
        key = _make_key(question)
        cached = redis.get(key)
        if cached:
            logger.info("cache_hit", extra={"extra": {"question": question}})
            return json.loads(cached)
        return None
    except Exception as e:
        logger.error("cache_get_error", extra={"extra": {"error": str(e)}})
        return None

async def save_to_cache(question: str, response: dict) -> None:
    try:
        key = _make_key(question)
        redis.setex(key, CACHE_TTL, json.dumps(response, ensure_ascii=False))
        logger.info("cache_saved", extra={"extra": {"question": question}})
    except Exception as e:
        logger.error("cache_save_error", extra={"extra": {"error": str(e)}})