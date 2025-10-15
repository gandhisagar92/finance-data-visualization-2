"""
Entity type classes for financial data relationship explorer.
Each entity type represents a specific financial data object with its own properties and methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import re


class Entity(ABC):
    """Base class for all entity types"""

    def __init__(
        self,
        data: Dict[str, Any],
        entity_type: str,
        display_type: str = "graph-node",
        **kwargs,
    ):
        self.data = data
        self.entity_type = entity_type  # e.g., "Stock", "Listing", "Exchange", etc.
        self.display_type = display_type  # e.g., "graph-node" or "list-row"
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())

    def _apply_template(
        self, template: Dict[str, Any], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply template to data, replacing ${field} placeholders with actual values.
        Supports nested dictionaries and lists.
        """
        if isinstance(template, dict):
            result = {}
            for key, value in template.items():
                # Handle special keys like "idValue.key" and "idValue.value"
                if "${" in str(key):
                    # Evaluate key template
                    evaluated_key = self._replace_placeholders(key, data)
                    result[evaluated_key] = self._apply_template(value, data)
                else:
                    result[key] = self._apply_template(value, data)
            return result
        elif isinstance(template, list):
            return [self._apply_template(item, data) for item in template]
        elif isinstance(template, str):
            return self._replace_placeholders(template, data)
        else:
            return template

    def _replace_placeholders(self, template_str: str, data: Dict[str, Any]) -> Any:
        """Replace ${field} placeholders with actual values from data"""
        if not isinstance(template_str, str) or "${" not in template_str:
            return template_str

        # Pattern to match ${field} or ${field:default_value}
        pattern = r"\$\{([^}]+)\}"
        matches = re.findall(pattern, template_str)

        result = template_str
        for match in matches:
            # Check for default value
            if ":" in match:
                field_path, default = match.split(":", 1)
            else:
                field_path = match
                default = None

            # Get value from nested path (e.g., "idValue.key")
            value = self._get_nested_value(data, field_path)

            if value is None:
                value = default if default is not None else ""

            # Replace the placeholder
            result = result.replace(
                f"${{{match}}}", str(value) if value is not None else ""
            )

        # If result is still a template variable alone, return None
        if result.strip() == "":
            return None

        return result

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return None
            else:
                return None

        return value

    def to_graph_node_dict(self, entity_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert entity to node representation for graph visualization.
        Uses entity_definition template to transform data.
        """
        # Get the graph-node template
        template = entity_definition.get("body", {}).get("graph-node", {})
        header_template = entity_definition.get("header", {})
        footer_template = entity_definition.get("footer", {})

        # Apply templates
        result = {}
        result.update(self._apply_template(header_template, self.data))
        result.update(self._apply_template(template, self.data))
        result.update(self._apply_template(footer_template, self.data))

        # Remove None values
        result = {k: v for k, v in result.items() if v is not None}

        return result

    def to_tree_list_row_dict(
        self, entity_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert entity to list row representation for tree view.
        Uses entity_definition template to transform data.
        """
        # Get the list-row template
        template = entity_definition.get("body", {}).get("list-row", {})
        header_template = entity_definition.get("header", {})
        footer_template = entity_definition.get("footer", {})

        # Apply templates
        result = {}
        result.update(self._apply_template(header_template, self.data))

        # Process columns
        columns_template = template.get("columns", [])
        columns = []
        for col_template in columns_template:
            col = self._apply_template(col_template, self.data)
            if col.get("value") is not None:  # Only include if value exists
                columns.append(col)

        if columns:
            result["columns"] = columns

        result.update(self._apply_template(footer_template, self.data))

        # Remove None values
        result = {k: v for k, v in result.items() if v is not None}

        return result

    def get_field_value(self, field_name: str) -> Any:
        """Get value of a specific field from entity data"""
        return self.data.get(field_name)
