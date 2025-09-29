"""
Graph service with caching capabilities.
"""

from .graph_builder import GraphBuilder
from cache.cache_manager import CacheManager
from typing import Dict, Any


class GraphService:
    """Main service for graph operations"""

    def __init__(self, graph_builder: GraphBuilder, cache_manager: CacheManager):
        self.graph_builder = graph_builder
        self.cache_manager = cache_manager

    def build_initial_graph(
        self, ref_data_type: str, id_type: str, id_value: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Build initial 2-level graph with caching"""
        # Generate cache key
        cache_key = self.cache_manager.generate_key(
            "graph_build", ref_data_type, id_type, id_value, **kwargs
        )

        # Try cache first
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        # Build graph
        result = self.graph_builder.build_graph(
            ref_data_type, id_type, id_value, **kwargs
        )

        # Cache result
        self.cache_manager.set(
            cache_key, result, 300
        )  # 5 minutes TTL Sagar TODO: Implement cache invalidation strategy

        return result

    def expand_node(
        self, node_id: str, ref_data_type: str, id_type: str, id_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Expand specific node with caching"""
        # Generate cache key
        cache_key = self.cache_manager.generate_key(
            "node_expand", node_id, ref_data_type, id_type, id_value
        )

        # Try cache first
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        # Expand node
        result = self.graph_builder.expand_node(
            node_id, ref_data_type, id_type, id_value
        )

        # Cache result
        self.cache_manager.set(cache_key, result, 180)  # 3 minutes TTL

        return result

    def invalidate_node_cache(self, entity_type: str, entity_id: str) -> None:
        """Invalidate cache for specific entity"""
        self.cache_manager.invalidate_pattern(f"*:{entity_type}:*:{entity_id}:*")
