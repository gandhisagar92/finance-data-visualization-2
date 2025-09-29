"""
Cache manager with decorators and key generation utilities.
Provides high-level cache operations and method caching decorators.
"""

from .cache_interface import CacheInterface
from .memory_cache import MemoryCache
from typing import Optional, Any, Dict, Callable
import hashlib
import json
from functools import wraps


class CacheManager:
    """Manages cache operations and provides decorators for caching"""
    
    def __init__(self, cache_impl: Optional[CacheInterface] = None):
        self._cache = cache_impl or MemoryCache()
        self._enabled = True
        self._default_ttl = 300  # 5 minutes
    
    def enable(self):
        """Enable caching"""
        self._enabled = True
    
    def disable(self):
        """Disable caching"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self._enabled
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if enabled"""
        if not self._enabled:
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache if enabled"""
        if self._enabled:
            self._cache.set(key, value, ttl or self._default_ttl)
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if self._enabled:
            self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear all cache"""
        self._cache.clear()
    
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create deterministic key from arguments
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def cached_method(self, ttl: Optional[int] = None, key_prefix: Optional[str] = None):
        """Decorator for caching method results"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)
                
                # Generate cache key
                prefix = key_prefix or f"{func.__module__}.{func.__name__}"
                cache_key = self.generate_key(prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                if result is not None:  # Only cache non-None results
                    self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern (basic implementation)"""
        # This would need more sophisticated implementation for Redis-like caches
        # For now, just clear all cache
        if pattern:
            self.clear()
            return 1
        return 0
