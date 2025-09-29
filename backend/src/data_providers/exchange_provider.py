"""
Exchange data provider implementation.
Handles data retrieval for Exchange entities.
"""

from .base_provider import BaseDataProvider
from .cached_provider_mixin import CachedProviderMixin
from entities.entity_types import BaseEntity
from typing import List, Dict, Any, Optional, Tuple
import json
import os


class ExchangeDataProvider(CachedProviderMixin, BaseDataProvider):
    """Data provider for exchange-related entities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config=config)
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON files"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        mock_data_path = os.path.join(project_root, 'mock_data', 'exchanges.json')
        
        try:
            with open(mock_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'exchanges': []}
    
    def get_entity_by_id(self, entity_type: str, id_type: str, 
                        id_value: Dict[str, Any], 
                        parent_node: Optional[BaseEntity] = None, 
                        **kwargs) -> Optional[BaseEntity]:
        """Get exchange entity by ID"""
        
        if entity_type == "Exchange":
            data = self._get_exchange_data(id_value.get('exchangeId'))
            return self.create_entity_instance('Exchange', data) if data else None
            
        return None
    
    def _get_exchange_data(self, exchange_id: str) -> Optional[Dict[str, Any]]:
        """Get raw exchange data by exchange ID"""
        exchanges = self.mock_data.get('exchanges', [])
        for exchange in exchanges:
            if exchange.get('exchangeId') == exchange_id:
                return exchange
        return None
    
    def get_related_entity_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs based on relationship"""
        # Exchanges typically don't have outbound relationships in this model
        return []
    
    def resolve_entity_type(self, generic_type: str, id_type: str, 
                          id_value: Dict[str, Any]) -> Optional[str]:
        """Resolve entity type"""
        # Exchanges are not generic types
        return None
