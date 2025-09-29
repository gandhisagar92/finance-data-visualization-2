"""
Configuration manager for handling entity and relationship definitions.
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
import os


class ConfigurationManager:
    """Manages entity and relationship configurations"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Default to config directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_dir = current_dir
        
        self.config_dir = Path(config_dir)
        self._entity_config = None
        self._relationship_config = None
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files"""
        entity_file = self.config_dir / "entity_types.yaml"
        relationship_file = self.config_dir / "relationships.yaml"
        
        try:
            with open(entity_file, 'r') as f:
                self._entity_config = yaml.safe_load(f)
        except FileNotFoundError:
            self._entity_config = {'entities': {}, 'specific_entities': {}}
            
        try:
            with open(relationship_file, 'r') as f:
                self._relationship_config = yaml.safe_load(f)
        except FileNotFoundError:
            self._relationship_config = {'relationships': {}}
    
    def get_generic_entities(self) -> Dict[str, Any]:
        """Get all generic entity types"""
        return self._entity_config.get('entities', {})
    
    def get_specific_entity_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific entity type"""
        return self._entity_config.get('specific_entities', {}).get(entity_type)
    
    def get_entity_relationships(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get all relationships for an entity type"""
        return self._relationship_config.get('relationships', {}).get(entity_type, [])
    
    def get_relationship_config(self, source_type: str, 
                              relationship_name: str) -> Optional[Dict[str, Any]]:
        """Get specific relationship configuration"""
        relationships = self.get_entity_relationships(source_type)
        for rel in relationships:
            if rel.get('name') == relationship_name:
                return rel
        return None
    
    def get_data_provider_config(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """Get data provider configuration for entity type"""
        entity_config = self.get_specific_entity_config(entity_type)
        if entity_config:
            return entity_config.get('data_source')
        return None
    
    def reload_configurations(self):
        """Reload configurations from files"""
        self._load_configurations()
    
    def get_metadata_for_api(self) -> Dict[str, Any]:
        """Get metadata formatted for API response"""
        generic_entities = self.get_generic_entities()
        
        reference_data_types = []
        for entity_name, entity_config in generic_entities.items():
            id_types = []
            for id_type_name, id_type_config in entity_config.get('id_types', {}).items():
                id_types.append({
                    'type': id_type_name,
                    'inputs': id_type_config.get('inputs', [])
                })
            
            reference_data_types.append({
                'refDataType': entity_name,
                'idTypes': id_types
            })
        
        return {
            'referenceDataTypes': reference_data_types
        }
