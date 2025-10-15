"""
Main GraphQL query resolver.
Integrates with existing service layer.
"""

import graphene
from typing import List, Optional
import time
from datetime import datetime

from src.graphql.types import (
    GraphResult,
    GraphNode,
    GraphMetadata,
    NodeSearchResult,
    TypeResolutionResult,
    ReferenceDataMetadata,
    InputFieldKind
)
from src.graphql.types.input_types import (
    BuildGraphInput,
    ExpandNodeInput
)
from src.graphql.resolvers.utils import (
    convert_kv_list_to_dict,
    convert_node_dict_to_graphql,
    convert_edge_dict_to_graphql
)


class Query(graphene.ObjectType):
    """Root Query type for GraphQL schema"""
    
    build_graph = graphene.Field(GraphResult, input=graphene.Argument(BuildGraphInput, required=True))
    
    def resolve_build_graph(self, info, input):
        """
        Build a relationship graph starting from a specific entity.
        Returns nodes and edges up to the specified depth.
        """
        start_time = time.time()
        
        # Get services from context
        graph_service = info.context["graph_service"]
        
        # Convert input
        id_value_dict = convert_kv_list_to_dict(input.id_value)
        
        # Build kwargs
        kwargs = {
            "source": input.source
        }
        if input.effective_datetime:
            kwargs["effective_datetime"] = input.effective_datetime
        
        # Call existing service
        result = graph_service.build_initial_graph(
            ref_data_type=input.ref_data_type,
            id_type=input.id_type,
            id_value=id_value_dict,
            **kwargs
        )
        
        # Convert nodes
        nodes = [
            GraphNode(**convert_node_dict_to_graphql(node))
            for node in result.get("nodes", [])
        ]
        
        # Convert edges
        edges = []
        for edge_dict in result.get("edges", []):
            edge_data = convert_edge_dict_to_graphql(edge_dict)
            edges.append(type('obj', (object,), edge_data)())
        
        # Build metadata
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        metadata = GraphMetadata(
            node_count=len(nodes),
            edge_count=len(edges),
            max_depth=input.max_depth,
            execution_time_ms=execution_time
        )
        
        return GraphResult(
            nodes=nodes,
            edges=edges,
            metadata=metadata
        )
    
    @strawberry.field
    def expand_node(self, info: strawberry.Info, input: ExpandNodeInput) -> GraphResult:
        """
        Expand a specific node to reveal its immediate relationships.
        Returns additional nodes and edges connected to the specified node.
        """
        start_time = time.time()
        
        # Get services from context
        graph_service = info.context["graph_service"]
        
        # Convert input
        id_value_dict = convert_kv_list_to_dict(input.id_value)
        
        # Call existing service
        result = graph_service.expand_node(
            node_id=input.node_id,
            ref_data_type=input.ref_data_type,
            id_type=input.id_type,
            id_value=id_value_dict
        )
        
        # Convert nodes
        nodes = [
            GraphNode(**convert_node_dict_to_graphql(node))
            for node in result.get("nodes", [])
        ]
        
        # Convert edges
        edges = []
        for edge_dict in result.get("edges", []):
            edge_data = convert_edge_dict_to_graphql(edge_dict)
            edges.append(type('obj', (object,), edge_data)())
        
        # Build metadata
        execution_time = (time.time() - start_time) * 1000
        metadata = GraphMetadata(
            node_count=len(nodes),
            edge_count=len(edges),
            max_depth=input.max_depth,
            execution_time_ms=execution_time
        )
        
        return GraphResult(
            nodes=nodes,
            edges=edges,
            metadata=metadata
        )
    
    @strawberry.field
    def get_node(self, info: strawberry.Info, node_id: str) -> Optional[GraphNode]:
        """
        Get a single node by its ID without relationships.
        Useful for refreshing node data without rebuilding the graph.
        """
        # Get data providers from context
        providers = info.context["providers"]
        
        # Parse node_id to extract entity type and ID
        # For now, we'll need to search through providers
        # In production, you might want a node registry
        
        for provider in providers.values():
            try:
                # This is a simplified implementation
                # You might want to add a get_by_node_id method to providers
                pass
            except:
                continue
        
        return None
    
    @strawberry.field
    def get_nodes(self, info: strawberry.Info, node_ids: List[str]) -> List[GraphNode]:
        """
        Get multiple nodes by their IDs.
        Efficient way to fetch specific nodes in batch.
        """
        nodes = []
        for node_id in node_ids:
            node = self.get_node(info, node_id)
            if node:
                nodes.append(node)
        return nodes
    
    @strawberry.field
    def search_nodes(
        self,
        info: strawberry.Info,
        ref_data_type: Optional[str] = None,
        title_search: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> NodeSearchResult:
        """
        Search for nodes matching criteria.
        Returns matching nodes without edges.
        """
        # This would require adding search capability to data providers
        # For now, return empty result
        return NodeSearchResult(
            nodes=[],
            total_count=0,
            has_more=False
        )
    
    @strawberry.field
    def get_node_payload(
        self,
        info: strawberry.Info,
        node_id: str,
        ref_data_type: str,
        id_type: str,
        id_value: List[strawberry.scalars.JSON]
    ) -> strawberry.scalars.JSON:
        """
        Get the full payload/details for a specific node.
        Returns raw data including fields not in the graph node structure.
        """
        providers = info.context["providers"]
        
        # Convert id_value
        id_value_dict = {}
        for item in id_value:
            if isinstance(item, dict) and "key" in item and "value" in item:
                id_value_dict[item["key"]] = item["value"]
        
        # Get provider
        provider = providers.get(ref_data_type)
        if not provider:
            return {}
        
        # Get entity
        entity = provider.get_entity_by_id(
            ref_data_type,
            id_type,
            id_value_dict
        )
        
        if entity:
            return entity.data
        
        return {}
    
    @strawberry.field
    def get_metadata(self, info: strawberry.Info) -> ReferenceDataMetadata:
        """
        Get available reference data types and their queryable ID types.
        Returns metadata for building the query UI.
        """
        config_manager = info.context["config_manager"]
        
        # Get metadata from config manager
        metadata_dict = config_manager.get_metadata_for_api()
        
        # Convert to GraphQL types
        ref_data_types = []
        for ref_type_dict in metadata_dict.get("referenceDataTypes", []):
            id_types = []
            for id_type_dict in ref_type_dict.get("idTypes", []):
                inputs = []
                for input_dict in id_type_dict.get("inputs", []):
                    # Map kind string to enum
                    kind_str = input_dict.get("kind", "text").upper()
                    try:
                        kind = InputFieldKind[kind_str]
                    except KeyError:
                        kind = InputFieldKind.TEXT
                    
                    inputs.append(type('obj', (object,), {
                        "id": input_dict.get("id"),
                        "label": input_dict.get("label"),
                        "kind": kind,
                        "required": input_dict.get("required", False),
                        "options": input_dict.get("options"),
                        "validation": input_dict.get("validation")
                    })())
                
                id_types.append(type('obj', (object,), {
                    "type": id_type_dict.get("type"),
                    "inputs": inputs
                })())
            
            ref_data_types.append(type('obj', (object,), {
                "ref_data_type": ref_type_dict.get("refDataType"),
                "description": ref_type_dict.get("description"),
                "id_types": id_types
            })())
        
        return ReferenceDataMetadata(reference_data_types=ref_data_types)
    
    @strawberry.field
    def resolve_type(
        self,
        info: strawberry.Info,
        generic_type: str,
        id_type: str,
        id_value: List[strawberry.scalars.JSON]
    ) -> TypeResolutionResult:
        """
        Resolve a generic type to its specific type.
        Example: "Instrument" -> "Stock"
        """
        providers = info.context["providers"]
        
        # Convert id_value
        id_value_dict = {}
        for item in id_value:
            if isinstance(item, dict) and "key" in item and "value" in item:
                id_value_dict[item["key"]] = item["value"]
        
        # Try each provider for type resolution
        resolved_type = None
        for provider in providers.values():
            try:
                resolved_type = provider.resolve_entity_type(
                    generic_type,
                    id_type,
                    id_value_dict
                )
                if resolved_type:
                    break
            except:
                continue
        
        return TypeResolutionResult(
            generic_type=generic_type,
            specific_type=resolved_type,
            resolved=resolved_type is not None
        )
