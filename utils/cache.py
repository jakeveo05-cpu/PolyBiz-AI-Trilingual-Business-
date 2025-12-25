"""
Caching Layer - Redis with in-memory fallback
"""
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import asyncio

logger = logging.getLogger('polybiz.cache')

# Try to import redis, fallback to in-memory if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed, using in-memory cache")


class InMemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expires_at)
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        async with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if expires_at is None or datetime.utcnow() < expires_at:
                    return value
                else:
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: str, ttl_seconds: int = None):
        """Set value in cache with optional TTL"""
        async with self._lock:
            expires_at = None
            if ttl_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expires_at)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        async with self._lock:
            self._cache.pop(key, None)
    
    async def clear(self):
        """Clear all cache"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self):
        """Remove expired entries"""
        async with self._lock:
            now = datetime.utcnow()
            expired = [
                k for k, (v, exp) in self._cache.items()
                if exp and now >= exp
            ]
            for k in expired:
                del self._cache[k]
            return len(expired)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "type": "in_memory",
            "entries": len(self._cache)
        }


class RedisCache:
    """Redis-based cache"""
    
    def __init__(self, url: str = "redis://localhost:6379"):
        self._url = url
        self._client: Optional[redis.Redis] = None
    
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        try:
            client = await self._get_client()
            return await client.get(f"polybiz:{key}")
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl_seconds: int = None):
        """Set value in cache with optional TTL"""
        try:
            client = await self._get_client()
            if ttl_seconds:
                await client.setex(f"polybiz:{key}", ttl_seconds, value)
            else:
                await client.set(f"polybiz:{key}", value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            client = await self._get_client()
            await client.delete(f"polybiz:{key}")
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
    
    async def clear(self):
        """Clear all polybiz keys"""
        try:
            client = await self._get_client()
            keys = await client.keys("polybiz:*")
            if keys:
                await client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "type": "redis",
            "url": self._url
        }


class CacheManager:
    """
    Unified cache manager with Redis/in-memory fallback
    """
    
    def __init__(self, redis_url: str = None):
        self._redis_url = redis_url
        self._cache = None
    
    async def _get_cache(self):
        """Get or create cache instance"""
        if self._cache is None:
            if REDIS_AVAILABLE and self._redis_url:
                try:
                    self._cache = RedisCache(self._redis_url)
                    # Test connection
                    await self._cache.set("_test", "1", ttl_seconds=1)
                    logger.info("Using Redis cache")
                except Exception as e:
                    logger.warning(f"Redis connection failed: {e}, using in-memory cache")
                    self._cache = InMemoryCache()
            else:
                self._cache = InMemoryCache()
                logger.info("Using in-memory cache")
        return self._cache
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (auto-deserialize JSON)"""
        cache = await self._get_cache()
        value = await cache.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache (auto-serialize to JSON)"""
        cache = await self._get_cache()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await cache.set(key, str(value), ttl_seconds)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        cache = await self._get_cache()
        await cache.delete(key)
    
    async def clear(self):
        """Clear all cache"""
        cache = await self._get_cache()
        await cache.clear()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if self._cache:
            return self._cache.get_stats()
        return {"type": "not_initialized"}


# Global cache manager
_cache_manager: Optional[CacheManager] = None


def get_cache_manager(redis_url: str = None) -> CacheManager:
    """Get or create global cache manager"""
    global _cache_manager
    if _cache_manager is None:
        import os
        redis_url = redis_url or os.getenv("REDIS_URL")
        _cache_manager = CacheManager(redis_url)
    return _cache_manager


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """
    Decorator to cache async function results
    
    Usage:
        @cached(ttl_seconds=600, key_prefix="lesson")
        async def generate_lesson(topic: str, language: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cache = get_cache_manager()
            cached_value = await cache.get(key)
            
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Call function and cache result
            logger.debug(f"Cache miss: {key}")
            result = await func(*args, **kwargs)
            
            if result is not None:
                await cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator
