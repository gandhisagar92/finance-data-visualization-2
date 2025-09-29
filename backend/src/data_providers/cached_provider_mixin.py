"""
Caching mixin for data providers.
Adds caching capabilities to any data provider.
"""

from cache.cache_manager import CacheManager
from entities.entity_types import BaseEntity
from typing import Optional, List, Tuple, Dict, Any


class CachedProviderMixin:
    """Mixin to add caching capabilities to data providers"""
    
    def __init__(self, cache_manager: Optional[CacheManager] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_manager = cache_manager or CacheManager()
    
    def get_cached_entity(self, entity_type: str, id_type: str, 
                         id_value: Dict[str, Any], 
                         parent_node: Optional[BaseEntity] = None) -> Optional[BaseEntity]:
        """Get entity with caching"""
        cache_key = self._generate_entity_cache_key(entity_type, id_type, id_value)
        
        # Try cache first
        cached_entity = self.cache_manager.get(cache_key)
        if cached_entity:
            return cached_entity
        
        # Fetch from data source
        entity = self.get_entity_by_id(entity_type, id_type, id_value, parent_node)
        
        # Cache the result
        if entity:
            ttl = self._get_entity_cache_ttl(entity_type)
            self.cache_manager.set(cache_key, entity, ttl)
        
        return entity
    
    def get_cached_related_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs with caching"""
        cache_key = self._generate_relationship_cache_key(
            source_entity, relationship_name, **kwargs
        )
        
        # Try cache first
        cached_ids = self.cache_manager.get(cache_key)
        if cached_ids:
            return cached_ids
        
        # Fetch from data source
        related_ids = self.get_related_entity_ids(source_entity, relationship_name, **kwargs)
        
        # Cache the result
        if related_ids:
            ttl = self._get_relationship_cache_ttl(relationship_name)
            self.cache_manager.set(cache_key, related_ids, ttl)
        
        return related_ids
    
    def _generate_entity_cache_key(self, entity_type: str, id_type: str, 
                                  id_value: Dict[str, Any]) -> str:
        """Generate cache key for entity"""
        return self.cache_manager.generate_key(
            f"entity:{entity_type}", id_type, id_value
        )
    
    def _generate_relationship_cache_key(self, source_entity: BaseEntity, 
                                       relationship_name: str, **kwargs) -> str:
        """Generate cache key for relationship"""
        return self.cache_manager.generate_key(
            f"relationship:{relationship_name}", 
            source_entity.entity_type, 
            source_entity.id, 
            **kwargs
        )
    
    def _get_entity_cache_ttl(self, entity_type: str) -> int:
        """Get cache TTL for entity type"""
        # Different entities can have different cache durations
        ttl_map = {
            'Stock': 300,      # 5 minutes
            'Option': 180,     # 3 minutes
            'Future': 240,     # 4 minutes
            'Bond': 600,       # 10 minutes
            'Exchange': 3600,  # 1 hour
            'Listing': 600,    # 10 minutes
            'InstrumentParty': 1800,  # 30 minutes
            'Client': 1800     # 30 minutes
        }
        return ttl_map.get(entity_type, 300)
    
    def _get_relationship_cache_ttl(self, relationship_name: str) -> int:
        """Get cache TTL for relationship type"""
        # Expensive relationships can be cached longer
        ttl_map = {
            'IS_UNDERLYING_FOR': 600,  # 10 minutes for options
            'HAS_LISTING': 300,        # 5 minutes
            'HAS_EXCHANGE': 1800,      # 30 minutes
            'HAS_ISSUER': 3600,        # 1 hour
            'HAS_UNDERLYING': 300,     # 5 minutes
            'HAS_UNDERLYING_ASSET': 300  # 5 minutes
        }
        return ttl_map.get(relationship_name, 300)
