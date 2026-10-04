from cachetools import TTLCache
from config import settings

# ключ -> значение (dict/list)
_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.cache_ttl)

def cache_get(key: str):
    return _cache.get(key)

def cache_set(key: str, value):
    _cache[key] = value