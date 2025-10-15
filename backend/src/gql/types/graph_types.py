"""
GraphQL type definitions using Graphene.
Defines the core types for the generic graph schema.
"""

import graphene
from datetime import datetime


class NodeStatus(graphene.Enum):
    """Node status values"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LISTED = "LISTED"
    DELISTED = "DELISTED"
    UNKNOWN = "UNKNOWN"


class KeyValuePair(graphene.ObjectType):
    """Represents a key-value pair in dynamic fields"""

    key = graphene.String(required=True)
    value = graphene.String()


class GraphNode(graphene.ObjectType):
    """
    A generic node in the reference data graph.
    All entities (Stock, Listing, Exchange, etc.) use this structure.
    """

    id = graphene.String(required=True)
    title_line1 = graphene.String(required=True)
    title_line2 = graphene.String()
    status = graphene.Field(NodeStatus, required=True)
    additional_lines = graphene.List(KeyValuePair, required=True)
    ref_data_type = graphene.String(required=True)
    id_type = graphene.String(required=True)
    id_value = graphene.List(KeyValuePair, required=True)
    as_of = graphene.DateTime()
    source = graphene.String()
    # Payload: arbitrary string attached to the node
    payload = graphene.String()
    expandable = graphene.Boolean(required=True)
    display_type = graphene.String()
    expandTo = graphene.String(default_value="graph-node")  # or tree-list


class GraphEdge(graphene.ObjectType):
    """An edge/relationship between two nodes in the graph"""

    source = graphene.String(required=True)
    target = graphene.String(required=True)
    relationship = graphene.String(required=True)
    metadata = graphene.List(KeyValuePair)


class GraphMetadata(graphene.ObjectType):
    """Metadata about a graph query"""

    node_count = graphene.Int(required=True)
    edge_count = graphene.Int(required=True)
    max_depth = graphene.Int(required=True)
    execution_time_ms = graphene.Float()


class GraphResult(graphene.ObjectType):
    """Complete graph result with nodes and edges"""

    nodes = graphene.List(GraphNode, required=True)
    edges = graphene.List(GraphEdge, required=True)
    metadata = graphene.Field(GraphMetadata)


# currently not used
class NodeSearchResult(graphene.ObjectType):
    """Result of a node search operation"""

    nodes = graphene.List(GraphNode, required=True)
    total_count = graphene.Int(required=True)
    has_more = graphene.Boolean(required=True)


class TypeResolutionResult(graphene.ObjectType):
    """Result of type resolution"""

    generic_type = graphene.String(required=True)
    specific_type = graphene.String()
    resolved = graphene.Boolean(required=True)


class ColumnDefinition(graphene.ObjectType):
    """Column definition for tree list"""

    key = graphene.String(required=True)
    label = graphene.String(required=True)
    sortable = graphene.Boolean(required=True)
    filterable = graphene.Boolean(required=True)
    width = graphene.Int()


class ColumnGroup(graphene.ObjectType):
    """Column grouping for tree list"""

    label = graphene.String(required=True)
    columns = graphene.List(graphene.String, required=True)


class TreeListMeta(graphene.ObjectType):
    """Metadata for tree list rendering"""

    columns = graphene.List(ColumnDefinition, required=True)
    column_groups = graphene.List(ColumnGroup)


class TreeListRow(graphene.ObjectType):
    """A single row in a tree list"""

    id = graphene.String(required=True)
    columns = graphene.List(KeyValuePair, required=True)
    expandable = graphene.Boolean(required=True)
    ref_data_type = graphene.String(required=True)
    id_type = graphene.String(required=True)
    id_value = graphene.List(KeyValuePair, required=True)
    # Payload: additional string payload for the row
    payload = graphene.String()


class TreeListResult(graphene.ObjectType):
    """Paginated tree-list result"""

    data = graphene.List(TreeListRow, required=True)
    page = graphene.Int(required=True)
    size = graphene.Int(required=True)
    total_items = graphene.Int(required=True)
    total_pages = graphene.Int(required=True)
    has_next = graphene.Boolean(required=True)
    has_previous = graphene.Boolean(required=True)
    meta = graphene.Field(TreeListMeta, required=True)


class InputFieldKind(graphene.Enum):
    """Input field types"""

    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    SELECT = "SELECT"


class InputFieldDefinition(graphene.ObjectType):
    """Definition of an input field"""

    id = graphene.String(required=True)
    label = graphene.String(required=True)
    kind = graphene.Field(InputFieldKind, required=True)
    required = graphene.Boolean(required=True)
    options = graphene.List(graphene.String)
    validation = graphene.String()


class IdTypeDefinition(graphene.ObjectType):
    """Definition of an ID type"""

    type = graphene.String(required=True)
    inputs = graphene.List(InputFieldDefinition, required=True)


class ReferenceDataType(graphene.ObjectType):
    """Reference data type definition"""

    ref_data_type = graphene.String(required=True)
    description = graphene.String()
    id_types = graphene.List(IdTypeDefinition, required=True)


class ReferenceDataMetadata(graphene.ObjectType):
    """Metadata about available reference data types"""

    reference_data_types = graphene.List(ReferenceDataType, required=True)


class GraphUpdateType(graphene.Enum):
    """Type of graph update"""

    NODE_ADDED = "NODE_ADDED"
    NODE_UPDATED = "NODE_UPDATED"
    NODE_REMOVED = "NODE_REMOVED"
    EDGE_ADDED = "EDGE_ADDED"
    EDGE_REMOVED = "EDGE_REMOVED"


class GraphUpdateEvent(graphene.ObjectType):
    """Event for graph subscription updates"""

    update_type = graphene.Field(GraphUpdateType, required=True)
    node = graphene.Field(GraphNode)
    edges = graphene.List(GraphEdge)
    timestamp = graphene.DateTime(required=True)
