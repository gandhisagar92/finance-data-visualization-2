"""
GraphQL input types using Graphene.
"""

import graphene
from datetime import datetime
from .graph_types import NodeStatus


class KeyValueInput(graphene.InputObjectType):
    """Key-value pair input for dynamic fields"""

    key = graphene.String(required=True)
    value = graphene.String(required=True)


class GraphFilters(graphene.InputObjectType):
    """Filters for graph building"""

    statuses = graphene.List(NodeStatus)
    ref_data_types = graphene.List(graphene.String)
    relationships = graphene.List(graphene.String)
    expandable_only = graphene.Boolean()


class BuildGraphInput(graphene.InputObjectType):
    """Input for building a graph from a starting point"""

    ref_data_type = graphene.String(required=True)
    id_type = graphene.String(required=True)
    id_value = graphene.List(KeyValueInput, required=True)
    max_depth = graphene.Int(default_value=2)
    source = graphene.String(default_value="Athena")
    effective_datetime = graphene.DateTime()
    filters = graphene.Field(GraphFilters)


class ExpandNodeInput(graphene.InputObjectType):
    """Input for expanding a specific node"""

    node_id = graphene.String(required=True)
    ref_data_type = graphene.String(required=True)
    id_type = graphene.String(required=True)
    id_value = graphene.List(KeyValueInput, required=True)
    max_depth = graphene.Int(default_value=1)
    source = graphene.String(default_value="Athena")


class BuildTreeListInput(graphene.InputObjectType):
    """Input for building a tree-list view of expensive relationships"""

    ref_data_type = graphene.String(required=True)
    id_type = graphene.String(required=True)
    id_value = graphene.List(KeyValueInput, required=True)
    page = graphene.Int(default_value=1)
    size = graphene.Int(default_value=50)
    filters = graphene.JSONString()
    sort_by = graphene.String()
    source = graphene.String(default_value="Athena")
    effective_datetime = graphene.DateTime()


class ExpandTreeRowInput(graphene.InputObjectType):
    """Input for expanding a tree list row"""

    node_data = graphene.Field(ExpandNodeInput, required=True)
