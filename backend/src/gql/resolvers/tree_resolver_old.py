"""
Tree list query resolver.
Handles tree-list operations for expensive relationships.
"""

import strawberry
from typing import Optional

from src.graphql.types import (
    TreeListResult,
    TreeListRow,
    TreeListMeta,
    ColumnDefinition,
    BuildTreeListInput,
    ExpandTreeRowInput,
    GraphResult,
    GraphNode
)
from src.graphql.resolvers.utils import (
    convert_kv_list_to_dict,
    convert_tree_row_to_graphql,
    convert_node_dict_to_graphql,
    convert_edge_dict_to_graphql
)


@strawberry.type
class TreeQuery:
    """Tree list queries"""
    
    @strawberry.field
    def build_tree_list(self, info: strawberry.Info, input: BuildTreeListInput) -> TreeListResult:
        """
        Build a tree-list view for expensive relationships.
        Used when a node has displayType: "tree-list".
        """
        # Get services from context
        tree_service = info.context["tree_service"]
        
        # Convert input
        id_value_dict = convert_kv_list_to_dict(input.id_value)
        
        # Build kwargs
        kwargs = {}
        if input.effective_datetime:
            kwargs["effective_datetime"] = input.effective_datetime
        
        # Call existing service
        result = tree_service.build_tree_list(
            ref_data_type=input.ref_data_type,
            id_type=input.id_type,
            id_value=id_value_dict,
            page=input.page,
            page_size=input.size,
            filters=input.filters,
            sort_by=input.sort_by
        )
        
        # Convert rows
        rows = []
        for row_dict in result.get("data", []):
            row_data = convert_tree_row_to_graphql(row_dict)
            rows.append(TreeListRow(**row_data))
        
        # Convert meta
        meta_dict = result.get("meta", {})
        columns = []
        for col_dict in meta_dict.get("columns", []):
            columns.append(ColumnDefinition(
                key=col_dict.get("key", ""),
                label=col_dict.get("label", ""),
                sortable=col_dict.get("sortable", False),
                filterable=col_dict.get("filterable", False),
                width=col_dict.get("width")
            ))
        
        meta = TreeListMeta(
            columns=columns,
            column_groups=None  # TODO: Add support for column groups
        )
        
        return TreeListResult(
            data=rows,
            page=result.get("page", 1),
            size=result.get("size", 50),
            total_items=result.get("total_items", 0),
            total_pages=result.get("total_pages", 0),
            has_next=result.get("has_next", False),
            has_previous=result.get("has_previous", False),
            meta=meta
        )
    
    @strawberry.field
    def expand_tree_row(self, info: strawberry.Info, input: ExpandTreeRowInput) -> GraphResult:
        """
        Expand a tree list row to show its relationships.
        Returns a mini-graph for the expanded row.
        """
        # Get services from context
        graph_service = info.context["graph_service"]
        
        # Convert input
        node_data = input.node_data
        id_value_dict = convert_kv_list_to_dict(node_data.id_value)
        
        # Call expand node
        result = graph_service.expand_node(
            node_id=node_data.node_id,
            ref_data_type=node_data.ref_data_type,
            id_type=node_data.id_type,
            id_value=id_value_dict
        )
        
        # Convert nodes and edges
        nodes = [
            GraphNode(**convert_node_dict_to_graphql(node))
            for node in result.get("nodes", [])
        ]
        
        edges = []
        for edge_dict in result.get("edges", []):
            edge_data = convert_edge_dict_to_graphql(edge_dict)
            edges.append(type('obj', (object,), edge_data)())
        
        return GraphResult(
            nodes=nodes,
            edges=edges,
            metadata=None
        )
