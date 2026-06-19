"""
Async cache utilities for TaxChain
"""

from typing import Dict, Any, Callable, Optional
import asyncio
from datetime import datetime, timedelta


class AsyncCache:
    """Simple async cache implementation"""

    def __init__(self, max_size: int = 10000, ttl: Optional[timedelta] = None):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key not in self.cache:
            return None

        if self.ttl and datetime.now() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None

        return self.cache[key]

    def set(self, key: str, value: Any):
        """Set cached value"""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.timestamps))
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]

        self.cache[key] = value
        self.timestamps[key] = datetime.now()

    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.timestamps.clear()


# Global price cache instance
price_cache = AsyncCache(max_size=10000, ttl=timedelta(hours=24))


def async_lru_cache(maxsize: int = 128):
    """Async LRU cache decorator"""
    cache = AsyncCache(max_size=maxsize)

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            cached = cache.get(key)
            if cached is not None:
                return cached

            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result

        return wrapper

    return decorator
