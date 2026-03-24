from diskcache import Cache
from app.core.config import settings

cache = Cache(settings.CACHE_DIR)

def get_cache(query):

    return cache.get(query)

def set_cache(query, response):

    cache.set(query, response)

def close_cache():
    cache.close()