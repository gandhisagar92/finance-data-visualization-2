"""
Utility functions for GraphQL resolvers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from src.gql.types import KeyValuePair, KeyValueInput, NodeStatus, GraphEdge


def convert_kv_list_to_dict(kv_list: List[KeyValueInput]) -> Dict[str, Any]:
    """Convert list of KeyValueInput to dictionary"""
    return {item.key: item.value for item in kv_list}


def parse_datetime_string(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse datetime string to datetime object.
    Handles various datetime formats commonly used in the system.
    """
    if not date_str:
        return None

    # Try different datetime formats
    formats = [
        "%Y-%m-%dT%H:%M:%S",  # 2025-09-15T10:47:10
        "%Y-%m-%d %H:%M:%S",  # 2025-09-15 10:47:10
        "%Y-%m-%dT%H:%M:%S.%f",  # 2025-09-15T10:47:10.123456
        "%Y-%m-%d",  # 2025-09-15
        "%Y-%m-%dT%H:%M:%SZ",  # 2025-09-15T10:47:10Z
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    # If no format matches, log a warning and return None
    print(f"Warning: Unable to parse datetime string: {date_str}")
    return None


def convert_dict_to_kv_list(data_dict: Dict[str, Any]) -> List[KeyValuePair]:
    """Convert dictionary to list of KeyValuePair"""
    if not data_dict:
        return []
    return [
        KeyValuePair(key=str(k), value=str(v) if v is not None else None)
        for k, v in data_dict.items()
    ]


def convert_node_dict_to_graphql(node_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert node dictionary from service layer to GraphQL format.
    Handles field name mapping and type conversions.
    """
    # Convert additionalLines dict to list of KeyValuePair
    additional_lines = node_dict.get("additionalLines", {})
    if isinstance(additional_lines, dict):
        additional_lines = convert_dict_to_kv_list(additional_lines)
    elif not isinstance(additional_lines, list):
        additional_lines = []

    # Convert idValue dict to list of KeyValuePair
    id_value = node_dict.get("idValue", {})
    if isinstance(id_value, dict):
        id_value = convert_dict_to_kv_list(id_value)
    elif not isinstance(id_value, list):
        id_value = []

    # Map status string to enum
    status_str = node_dict.get("status", "UNKNOWN").upper()
    # Map to NodeStatus enum member; use getattr to avoid static-analysis issues
    status = getattr(NodeStatus, status_str, NodeStatus.UNKNOWN)

    # Convert field names from camelCase to snake_case for GraphQL
    return {
        "id": node_dict.get("id"),
        "title_line1": node_dict.get("titleLine1", ""),
        "title_line2": node_dict.get("titleLine2"),
        "status": status,
        "additional_lines": additional_lines,
        "ref_data_type": node_dict.get("refDataType", ""),
        "id_type": node_dict.get("idType", ""),
        "id_value": id_value,
        "as_of": parse_datetime_string(node_dict.get("asOf")),
        "payload": node_dict.get("payload"),
        "source": node_dict.get("source"),
        "expandable": node_dict.get("expandable", False) in [True, "True", "true"],
        "display_type": node_dict.get("displayType"),
    }


def convert_edge_dict_to_graphql(edge_dict: Dict[str, Any]) -> GraphEdge:
    """
    Convert edge dictionary from service layer to GraphQL GraphEdge object.
    Returns a properly typed GraphEdge instance.
    """
    metadata = edge_dict.get("metadata")
    if metadata and isinstance(metadata, dict):
        metadata = convert_dict_to_kv_list(metadata)

    return GraphEdge(
        source=edge_dict.get("source"),
        target=edge_dict.get("target"),
        relationship=edge_dict.get("relationship"),
        metadata=metadata,
    )


def convert_tree_row_to_graphql(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert tree list row dictionary to GraphQL format"""
    # Convert columns dict to list of KeyValuePair
    columns = row_dict.get("columns", {})
    if isinstance(columns, dict):
        columns = convert_dict_to_kv_list(columns)
    elif not isinstance(columns, list):
        columns = []

    # Convert idValue
    id_value = row_dict.get("idValue", {})
    if isinstance(id_value, dict):
        id_value = convert_dict_to_kv_list(id_value)
    elif not isinstance(id_value, list):
        id_value = []

    return {
        "id": row_dict.get("id"),
        "columns": columns,
        "expandable": row_dict.get("expandable", False),
        "ref_data_type": row_dict.get("refDataType", ""),
        "id_type": row_dict.get("idType", ""),
        "id_value": id_value,
        "payload": row_dict.get("payload"),
    }
