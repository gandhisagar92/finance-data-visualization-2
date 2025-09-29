"""
Graph builder service for constructing relationship graphs.
"""

from typing import Dict, Any, List, Optional, Set
from entities.entity_types import BaseEntity, TreeListNode
from data_providers.base_provider import BaseDataProvider
from config.config_manager import ConfigurationManager


class GraphBuilder:
    """Builds relationship graphs with depth control"""

    def __init__(
        self,
        config_manager: ConfigurationManager,
        data_provider_registry: Dict[str, BaseDataProvider],
    ):
        self.config_manager = config_manager
        self.data_providers = data_provider_registry
        self.max_initial_depth = 2  # Always build to 2 levels initially

    def build_graph(
        self, root_entity_type: str, id_type: str, id_value: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Build initial graph to 2 levels"""

        # Resolve generic type to specific type
        specific_type = self._resolve_entity_type(root_entity_type, id_type, id_value)
        if not specific_type:
            raise ValueError(f"Cannot resolve entity type for {root_entity_type}")

        # Get root entity
        provider = self._get_data_provider(specific_type)
        root_entity = provider.get_entity_by_id(specific_type, id_type, id_value)
        if not root_entity:
            raise ValueError(f"Entity not found: {id_type}={id_value}")

        # Build graph breadth-first to specified depth
        nodes = []
        edges = []
        visited_entities = set()

        self._build_graph_recursive(
            root_entity,
            nodes,
            edges,
            visited_entities,
            current_depth=0,
            max_depth=self.max_initial_depth,
        )

        return {"nodes": [node.to_node_dict() for node in nodes], "edges": edges}

    def expand_node(
        self, node_id: str, ref_data_type: str, id_type: str, id_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Expand relationships from a specific node"""

        # Get the node entity
        provider = self._get_data_provider(ref_data_type)
        node_entity = provider.get_entity_by_id(ref_data_type, id_type, id_value)
        if not node_entity:
            raise ValueError(f"Node not found: {node_id}")

        # Get immediate relationships (1 level only)
        nodes = []
        edges = []
        visited_entities = {node_entity.id}  # Don't re-process the source node

        self._build_graph_recursive(
            node_entity,
            nodes,
            edges,
            visited_entities,
            current_depth=0,
            max_depth=1,  # Only 1 level for expansion
        )

        return {"nodes": [node.to_node_dict() for node in nodes], "edges": edges}

    def _build_graph_recursive(
        self,
        source_entity: BaseEntity,
        nodes: List[BaseEntity],
        edges: List[Dict[str, Any]],
        visited_entities: Set[str],
        current_depth: int,
        max_depth: int,
    ) -> None:
        """Recursively build graph to specified depth"""

        print(
            f"Building graph at depth {current_depth} for entity {source_entity.entity_type} - {source_entity.id}"
        )
        # Add current entity to nodes if not already added
        if source_entity.id not in visited_entities:
            nodes.append(source_entity)
            visited_entities.add(source_entity.id)

        # Stop if we've reached maximum depth
        if current_depth >= max_depth:
            return

        # Get all relationships for this entity type
        relationships = self.config_manager.get_entity_relationships(
            source_entity.entity_type
        )

        for relationship in relationships:
            if not relationship.get("display_in_graph", True):
                continue

            # Check if this is an expensive relationship
            if relationship.get("expensive", False):
                # Create tree-list placeholder node
                tree_node = self._create_tree_list_node(source_entity, relationship)
                if tree_node.id not in visited_entities:
                    nodes.append(tree_node)
                    visited_entities.add(tree_node.id)

                    edges.append(
                        {
                            "source": source_entity.id,
                            "target": tree_node.id,
                            "relationship": relationship["relationship_label"],
                        }
                    )
                continue

            # Get related entity IDs
            provider = self._get_data_provider(source_entity.entity_type)
            try:
                related_ids = provider.get_related_entity_ids(
                    source_entity, relationship["name"]
                )
            except Exception as e:
                # Log error and continue with other relationships
                print(f"Error getting related entities for {relationship['name']}: {e}")
                continue

            # Process each related entity
            for id_type, id_value in related_ids:
                try:
                    target_entity = self._get_related_entity(
                        relationship["target_type"],
                        id_type,
                        {id_type: id_value},
                        source_entity,
                    )

                    if target_entity and target_entity.id not in visited_entities:
                        # Add edge
                        edges.append(
                            {
                                "source": source_entity.id,
                                "target": target_entity.id,
                                "relationship": relationship["relationship_label"],
                            }
                        )

                        # Recursively process this entity
                        self._build_graph_recursive(
                            target_entity,
                            nodes,
                            edges,
                            visited_entities,
                            current_depth + 1,
                            max_depth,
                        )
                except Exception as e:
                    # Log error and continue with other entities
                    print(f"Error processing related entity {id_type}={id_value}: {e}")
                    continue

    def _create_tree_list_node(
        self, source_entity: BaseEntity, relationship: Dict[str, Any]
    ) -> BaseEntity:
        """Create a placeholder node for expensive relationships"""

        tree_node_data = {
            "id": f"{source_entity.id}_{relationship['name']}",
            "titleLine1": f"Click to view {relationship['target_type']}s",
            "titleLine2": "",
            "status": "ACTIVE",
            "totalCount": self._get_expensive_relationship_count(
                source_entity, relationship
            ),
            "sourceEntityId": source_entity.id,
            "relationshipName": relationship["name"],
            "targetType": relationship["target_type"],
        }

        return TreeListNode(tree_node_data)

    def _get_expensive_relationship_count(
        self, source_entity: BaseEntity, relationship: Dict[str, Any]
    ) -> int:
        """Get count for expensive relationship without loading all data"""
        provider = self._get_data_provider(source_entity.entity_type)

        try:
            # This would be optimized to get count only, not full data
            related_ids = provider.get_related_entity_ids(
                source_entity, relationship["name"]
            )
            return len(related_ids)
        except Exception:
            return 0  # Return 0 if count cannot be determined

    def _get_related_entity(
        self,
        target_type: str,
        id_type: str,
        id_value: Dict[str, Any],
        parent_entity: BaseEntity,
    ) -> Optional[BaseEntity]:
        """Get related entity with parent context"""
        provider = self._get_data_provider(target_type)
        return provider.get_entity_by_id(target_type, id_type, id_value, parent_entity)

    def _get_data_provider(self, entity_type: str) -> BaseDataProvider:
        """Get appropriate data provider for entity type"""
        # Map entity types to their providers
        provider_map = {
            "Stock": "InstrumentDataProvider",
            "Option": "InstrumentDataProvider",
            "Future": "InstrumentDataProvider",
            "Bond": "InstrumentDataProvider",
            "Listing": "ListingDataProvider",
            "Exchange": "ExchangeDataProvider",
            "InstrumentParty": "PartyDataProvider",
            "Client": "PartyDataProvider",
        }

        provider_name = provider_map.get(entity_type)
        if not provider_name:
            raise ValueError(f"No data provider found for entity type: {entity_type}")

        if provider_name not in self.data_providers:
            raise ValueError(f"Data provider not registered: {provider_name}")

        return self.data_providers[provider_name]

    def _resolve_entity_type(
        self, generic_type: str, id_type: str, id_value: Dict[str, Any]
    ) -> Optional[str]:
        """Resolve generic type to specific type"""
        # Try each registered data provider for type resolution
        for provider in self.data_providers.values():
            try:
                resolved_type = provider.resolve_entity_type(
                    generic_type, id_type, id_value
                )
                if resolved_type:
                    return resolved_type
            except Exception:
                continue  # Try next provider
        return None
