import redis.asyncio as redis
import json
import asyncio
from typing import Optional , Dict
from app.core.config import settings
from datetime import datetime

redis_client = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT,
    decode_responses=True
)

DEFAULT_TTL = 60 

def make_cache_key(namespace: str, *parts) -> str:
    """
    Build a consistent cache key, e.g.:
    make_cache_key("event", 42) -> "event:42"
    make_cache_key("user", "profile", 99) -> "user:profile:99"
    """
    return ":".join([namespace, *map(str, parts)])


async def get_cache(key: str):
    data = await redis_client.get(key)
    return json.loads(data) if data else None

async def set_cache(key: str, value, ttl: int = DEFAULT_TTL):
    print(value)
    await redis_client.set(key, json.dumps(value), ex=ttl)

async def delete_cache(key: str):
    await redis_client.delete(key)

async def delete_cache_with_prefix(prefix: str):
    keys = []
    # async for key in redis_client.scan_iter():
    #     print(key)
    async for key in redis_client.scan_iter(match=f"{prefix}*"):
        keys.append(key)
    if keys:
        await redis_client.delete(*keys)

async def delete_booking_cache(event_id: int, user_id: int):
    await asyncio.gather(
        delete_cache_with_prefix(f"user:bookings:{user_id}"),
        delete_cache_with_prefix(f"event:{event_id}"),
        delete_cache_with_prefix(f"event:bookings:{event_id}"),
        delete_cache_with_prefix(f"event:seats:{event_id}")
    )

async def delete_event_cache(event_id):
    await asyncio.gather(
        delete_cache_with_prefix(f"event:{event_id}"),
        delete_cache_with_prefix(f"event:bookings:{event_id}"),
        delete_cache_with_prefix(f"event:seats:{event_id}")
    )

async def insert_in_waitlist(list_key: str, value: dict, score: float, expire_at: int):
    """Insert value into waitlist (ZSET) with score and expire_at timestamp"""
    resp = await redis_client.zadd(list_key, {json.dumps(value): score})
    await redis_client.expireat(list_key, expire_at)

async def fetch_from_waitlist(list_key: str, start: int = 0, end: int = 0) :
    """Fetch items from waitlist (ZSET)"""
    items = await redis_client.zrange(list_key, start, end)
    # print(items)
    return [json.loads(val) for val in items]

async def delete_from_waitlist(list_key: str, value: dict):
    """Delete a value from waitlist (ZSET)"""
    await redis_client.zrem(list_key, json.dumps(value))