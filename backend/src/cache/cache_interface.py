"""
Cache interface and entry classes.
Provides abstract interface for cache implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timedelta


class CacheInterface(ABC):
    """Interface for cache implementations"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL in seconds"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all cache entries"""
        pass


class CacheEntry:
    """Cache entry with metadata"""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = None
        if ttl:
            self.expires_at = self.created_at + timedelta(seconds=ttl)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
