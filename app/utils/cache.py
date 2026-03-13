from diskcache import Cache

cache = Cache("./cache")

def get_cache(query):

    return cache.get(query)

def set_cache(query, response):

    cache.set(query, response)