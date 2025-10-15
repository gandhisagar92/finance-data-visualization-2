"""
Configuration manager for the application.
Manages entity types, relationships, and metadata.
"""

from typing import Dict, Any, List, Optional
from .entity_definition import specific_entity_definition
from .relationship_definition import relationship_definition
import yaml
import os


class ConfigurationManager:
    """Manages configuration settings for the application"""

    def __init__(self):
        self.entity_definitions = specific_entity_definition
        self.relationship_definitions = relationship_definition
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from meta.yaml"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(current_dir, "meta.yaml")

        try:
            with open(meta_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: meta.yaml not found at {meta_path}")
            return {"entities": {}}
        except yaml.YAMLError as e:
            print(f"Error parsing meta.yaml: {e}")
            return {"entities": {}}

    def get_entity_definition(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get entity definition for a specific type"""
        return self.entity_definitions.get(entity_type)

    def get_entity_relationships(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get relationships for a specific entity type"""
        return self.relationship_definitions.get(entity_type, [])

    def get_metadata_for_api(self) -> Dict[str, Any]:
        """
        Convert metadata to API response format.
        Returns structure compatible with GET /api/meta endpoint.
        """
        entities_metadata = self.metadata.get("entities", {})
        reference_data_types = []

        for entity_name, entity_config in entities_metadata.items():
            id_types_list = []
            id_types = entity_config.get("id_types", {})

            for id_type_name, id_type_config in id_types.items():
                id_type_entry = {
                    "type": id_type_name,
                    "inputs": id_type_config.get("inputs", []),
                }
                id_types_list.append(id_type_entry)

            ref_data_type_entry = {"refDataType": entity_name, "idTypes": id_types_list}
            reference_data_types.append(ref_data_type_entry)

        return {"referenceDataTypes": reference_data_types}

    def get_all_entity_types(self) -> List[str]:
        """Get list of all entity types"""
        return list(self.entity_definitions.keys())

    def get_relationship_by_name(
        self, entity_type: str, relationship_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific relationship by name"""
        relationships = self.get_entity_relationships(entity_type)
        for rel in relationships:
            if rel.get("name") == relationship_name:
                return rel
        return None

    def get_relationship_by_type(
        self, entity_type: str, target_entity_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific relationship by type"""
        relationships = self.get_entity_relationships(entity_type)
        for rel in relationships:
            if rel.get("targetType") == target_entity_type:
                return rel
        return None

    def get_all_relationships(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all relationships for an entity type"""
        return self.relationship_definitions.get(entity_type, [])
