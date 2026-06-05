import os
import redis

CACHE_KEY = "products"
CACHE_TTL = 60  # seconds


def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=True,
    )


def get_cached_products():
    # ✅ TODO Uppgift 12 & 15 - Read from Redis, return string or None
    return get_redis_client().get(CACHE_KEY)


def set_cached_products(json_data):
    # ✅ TODO Uppgift 14 - Write JSON string to Redis with a TTL
    get_redis_client().set(CACHE_KEY, json_data, ex=CACHE_TTL)


def clear_products_cache():
    # ✅ TODO Uppgift 17 - Delete the cache key after POST /products
    get_redis_client().delete(CACHE_KEY)