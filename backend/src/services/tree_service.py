"""
Tree service for handling tree-list operations.
"""

from typing import Dict, Any, List, Optional
from data_providers.base_provider import BaseDataProvider
from config.config_manager import ConfigurationManager


class TreeService:
    """Service for tree-list operations"""
    
    def __init__(self, data_provider_registry: Dict[str, BaseDataProvider], 
                 config_manager: ConfigurationManager):
        self.data_providers = data_provider_registry
        self.config_manager = config_manager
    
    def build_tree_list(self, ref_data_type: str, id_type: str, 
                       id_value: Dict[str, Any], 
                       page: int = 1, page_size: int = 50,
                       filters: Optional[Dict] = None, 
                       sort_by: Optional[str] = None) -> Dict[str, Any]:
        """Build paginated tree-list for expensive relationships"""
        
        provider = self._get_data_provider(ref_data_type)
        
        # This would use specialized tree-building logic
        # Different from graph building as it focuses on tabular data
        return self._build_paginated_tree(
            provider, ref_data_type, id_type, id_value, 
            page, page_size, filters, sort_by
        )
    
    def expand_tree_item(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Expand a tree item to show its immediate relationships"""
        # Similar to node expansion but formatted for tree display
        ref_data_type = node_data.get('refDataType')
        id_type = node_data.get('idType')
        id_value = node_data.get('idValue', {})
        
        if not all([ref_data_type, id_type, id_value]):
            raise ValueError("Invalid node data for tree expansion")
        
        provider = self._get_data_provider(ref_data_type)
        entity = provider.get_entity_by_id(ref_data_type, id_type, id_value)
        
        if not entity:
            return {'items': [], 'pagination': {}}
        
        # Get relationships and convert to tree format
        relationships = self.config_manager.get_entity_relationships(entity.entity_type)
        items = []
        
        for relationship in relationships:
            if not relationship.get('display_in_graph', True):
                continue
                
            try:
                related_ids = provider.get_related_entity_ids(entity, relationship['name'])
                
                for id_type_rel, id_value_rel in related_ids:
                    target_provider = self._get_data_provider(relationship['target_type'])
                    target_entity = target_provider.get_entity_by_id(
                        relationship['target_type'], id_type_rel, {id_type_rel: id_value_rel}
                    )
                    
                    if target_entity:
                        items.append({
                            'id': target_entity.id,
                            'columns': self._entity_to_columns(target_entity),
                            'expandable': len(self.config_manager.get_entity_relationships(target_entity.entity_type)) > 0,
                            'refDataType': target_entity.entity_type,
                            'idType': id_type_rel,
                            'idValue': {id_type_rel: id_value_rel}
                        })
            except Exception as e:
                print(f"Error expanding tree item for relationship {relationship['name']}: {e}")
                continue
        
        return {
            'items': items,
            'pagination': {
                'page': 1,
                'pageSize': len(items),
                'totalItems': len(items),
                'totalPages': 1,
                'hasNext': False,
                'hasPrevious': False
            }
        }
    
    def _build_paginated_tree(self, provider: BaseDataProvider, 
                            ref_data_type: str, id_type: str, id_value: Dict[str, Any],
                            page: int, page_size: int, 
                            filters: Optional[Dict], sort_by: Optional[str]) -> Dict[str, Any]:
        """Build paginated tree structure"""
        # For now, return empty structure
        # In a real implementation, this would handle complex tree building with pagination
        return {
            'items': [],
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'totalItems': 0,
                'totalPages': 0,
                'hasNext': False,
                'hasPrevious': False
            }
        }
    
    def _entity_to_columns(self, entity) -> Dict[str, Any]:
        """Convert entity to column format for tree display"""
        # Create a simplified column view of the entity
        columns = {
            'id': entity.id,
            'type': entity.entity_type,
            'status': entity.get_field_value('status') or 'UNKNOWN'
        }
        
        # Add entity-specific columns
        if entity.entity_type == 'Stock':
            columns.update({
                'name': entity.get_field_value('name'),
                'isin': entity.get_field_value('isin'),
                'sector': entity.get_field_value('sector')
            })
        elif entity.entity_type == 'Option':
            columns.update({
                'name': entity.get_field_value('name'),
                'optionType': entity.get_field_value('optionType'),
                'strike': entity.get_field_value('strike'),
                'expirationDate': entity.get_field_value('expirationDate')
            })
        elif entity.entity_type == 'Listing':
            columns.update({
                'ric': entity.get_field_value('ric'),
                'bloombergTicker': entity.get_field_value('bloombergTicker'),
                'exchangeId': entity.get_field_value('exchangeId')
            })
        
        return columns
    
    def _get_data_provider(self, entity_type: str) -> BaseDataProvider:
        """Get appropriate data provider for entity type"""
        provider_map = {
            'Stock': 'InstrumentDataProvider',
            'Option': 'InstrumentDataProvider',
            'Future': 'InstrumentDataProvider',
            'Bond': 'InstrumentDataProvider',
            'Listing': 'ListingDataProvider',
            'Exchange': 'ExchangeDataProvider',
            'InstrumentParty': 'PartyDataProvider',
            'Client': 'PartyDataProvider'
        }
        
        provider_name = provider_map.get(entity_type)
        if not provider_name:
            raise ValueError(f"No data provider found for entity type: {entity_type}")
        
        if provider_name not in self.data_providers:
            raise ValueError(f"Data provider not registered: {provider_name}")
        
        return self.data_providers[provider_name]
