from app.core.logger import get_logger
import time

logger = get_logger(__name__)

TENANT_CONFIG = {
    "free": {
        "model": "llama-3.1-8b-instant",
        "max_requests_per_minute": 10,
        "max_tokens": 512,
        "rag_enabled": True,
        "cache_enabled": True,
    },
    "premium": {
        "model": "llama-3.3-70b-versatile",
        "max_requests_per_minute": 100,
        "max_tokens": 2048,
        "rag_enabled": True,
        "cache_enabled": True,
    },
    "enterprise": {
        "model": "llama-3.3-70b-versatile",
        "max_requests_per_minute": 1000,
        "max_tokens": 4096,
        "rag_enabled": True,
        "cache_enabled": True,
    }
}

request_counts: dict = {}

def get_tenant_config(tenant: str) -> dict:
    config = TENANT_CONFIG.get(tenant)
    if not config:
        logger.warning("unknown_tenant", extra={"extra": {"tenant": tenant}})
        return TENANT_CONFIG["free"]
    return config

def is_rate_limited(tenant: str) -> bool:
    now = int(time.time() / 60)
    key = f"{tenant}:{now}"

    request_counts[key] = request_counts.get(key, 0) + 1

    old_keys = [k for k in request_counts if k != key]
    for k in old_keys:
        del request_counts[k]

    limit = TENANT_CONFIG.get(tenant, TENANT_CONFIG["free"])["max_requests_per_minute"]
    return request_counts[key] > limit