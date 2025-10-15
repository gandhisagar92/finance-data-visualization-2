"""
Graph builder service for constructing relationship graphs.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from entities.entity_types import Entity
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

        nodes = []
        edges = []
        visited = set()  # Track visited nodes to avoid duplicates

        # Get the root entity
        provider = self.data_providers.get(root_entity_type)
        if not provider:
            return {"nodes": [], "edges": []}

        root_entity = provider.get_entity_by_id(
            root_entity_type, id_type, id_value, **kwargs
        )

        if not root_entity:
            return {"nodes": [], "edges": []}

        # Add root node
        root_node = self._entity_to_node_dict(root_entity)
        nodes.append(root_node)
        visited.add(root_node["id"])

        # Build graph recursively up to max depth
        self._build_graph_recursive(
            root_entity,
            nodes,
            edges,
            visited,
            current_depth=0,
            max_depth=self.max_initial_depth,
            **kwargs,
        )

        return {"nodes": nodes, "edges": edges}

    def expand_node(
        self,
        node_id: str,
        ref_data_type: str,
        id_type: str,
        id_value: Dict[str, Any],
        **kwargs,
    ) -> Dict[str, Any]:
        """Expand relationships from a specific node"""

        nodes = []
        edges = []
        visited = set()

        # Get the entity to expand
        provider = self.data_providers.get(ref_data_type)
        if not provider:
            return {"nodes": [], "edges": []}

        entity = provider.get_entity_by_id(ref_data_type, id_type, id_value, **kwargs)

        if not entity:
            return {"nodes": [], "edges": []}

        # Add the source node
        source_node = self._entity_to_node_dict(entity)
        nodes.append(source_node)
        visited.add(source_node["id"])

        # Expand one level
        self._build_graph_recursive(
            entity, nodes, edges, visited, current_depth=0, max_depth=1, **kwargs
        )

        return {"nodes": nodes, "edges": edges}

    def _build_graph_recursive(
        self,
        source_entity: Entity,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        visited: Set[str],
        current_depth: int,
        max_depth: int,
        **kwargs,
    ):
        """Recursively build graph by traversing relationships"""

        if current_depth >= max_depth:
            return

        # Get relationships for this entity type
        relationships = self.config_manager.get_entity_relationships(
            source_entity.entity_type
        )

        for relationship in relationships:
            target_type = relationship.get("targetType", "ERROR")
            relationship_label = relationship.get("label", relationship.get("name"))

            # Get target provider
            target_provider = self.data_providers.get(target_type)
            if not target_provider:
                continue

            # Get related entity IDs
            try:
                source_provider = self.data_providers.get(source_entity.entity_type)
                if not source_provider:
                    continue
                related_ids = source_provider.get_related_entity_ids(
                    source_entity, relationship, **kwargs
                )
                print(
                    f"Related IDs for {source_entity.entity_type} via {relationship['name']}: {related_ids}"
                )
                # related_ids = source_entity.data.get(
                #     "_provider", target_provider
                # ).get_related_entity_ids(source_entity, relationship, **kwargs)
            except:
                # Fallback to using provider directly
                related_ids = target_provider.get_related_entity_ids(
                    source_entity, relationship, **kwargs
                )

            for target_id_type, target_id_value in related_ids:
                # Fetch the target entity
                target_entity = target_provider.get_entity_by_id(
                    target_type,
                    target_id_type,
                    target_id_value,
                    parent_node=source_entity,
                    relationship=relationship,
                    **kwargs,
                )
                print(
                    f"Fetched target entity: {target_entity.entity_type if target_entity else 'None'}"
                )

                if target_entity:
                    # Convert to node dict
                    target_node = self._entity_to_node_dict(target_entity)

                    print(f"Converted target entity to node dict: {target_node}")
                    # Add node if not visited
                    if target_node["id"] not in visited:
                        nodes.append(target_node)
                        visited.add(target_node["id"])

                        # Recursively build for non-expensive relationships
                        if not relationship.get("expensive", False):
                            self._build_graph_recursive(
                                target_entity,
                                nodes,
                                edges,
                                visited,
                                current_depth + 1,
                                max_depth,
                                **kwargs,
                            )

                    # Add edge
                    edge = {
                        "source": source_entity.data.get("id"),
                        "target": target_node["id"],
                        "relationship": relationship_label,
                    }
                    edges.append(edge)

    def _entity_to_node_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity to node dictionary for API response"""

        # Get entity definition
        entity_def = self.config_manager.get_entity_definition(entity.entity_type)

        if entity_def and entity.display_type == "graph-node":
            return entity.to_graph_node_dict(entity_def)
        elif entity_def and entity.display_type == "list-row":
            return entity.to_tree_list_row_dict(entity_def)
        else:
            # Fallback: return data as-is
            return entity.data
