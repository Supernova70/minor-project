import json
import logging
from functools import lru_cache

import redis as redis_lib

from app.config import get_settings

logger = logging.getLogger(__name__)

@lru_cache
def get_redis():
    settings = get_settings()
    try:
        r = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        # Test connection
        r.ping()
        return r
    except Exception as e:
        logger.warning(f"Could not connect to Redis at {settings.REDIS_URL}: {e}")
        return None
