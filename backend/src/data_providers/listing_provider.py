"""
Listing data provider implementation.
Handles data retrieval for Listing entities.
"""

from .base_provider import BaseDataProvider
from .cached_provider_mixin import CachedProviderMixin
from entities.entity_types import BaseEntity
from typing import List, Dict, Any, Optional, Tuple
import json
import os


class ListingDataProvider(CachedProviderMixin, BaseDataProvider):
    """Data provider for listing-related entities"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config=config)
        self.mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON files"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        mock_data_path = os.path.join(project_root, 'mock_data', 'listings.json')
        
        try:
            with open(mock_data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'listings': []}
    
    def get_entity_by_id(self, entity_type: str, id_type: str, 
                        id_value: Dict[str, Any], 
                        parent_node: Optional[BaseEntity] = None, 
                        **kwargs) -> Optional[BaseEntity]:
        """Get listing entity by ID"""
        
        if entity_type == "Listing":
            data = self._get_listing_data(id_value.get('tradingLineId'))
            return self.create_entity_instance('Listing', data) if data else None
            
        return None
    
    def _get_listing_data(self, trading_line_id: str) -> Optional[Dict[str, Any]]:
        """Get raw listing data by trading line ID"""
        listings = self.mock_data.get('listings', [])
        for listing in listings:
            if listing.get('tradingLineId') == trading_line_id:
                return listing
        return None
    
    def get_related_entity_ids(self, source_entity: BaseEntity, 
                              relationship_name: str, **kwargs) -> List[Tuple[str, str]]:
        """Get related entity IDs based on relationship"""
        
        if relationship_name == "HAS_EXCHANGE" and source_entity.entity_type == "Listing":
            exchange_id = source_entity.get_field_value('exchangeId')
            if exchange_id:
                return [("exchangeId", exchange_id)]
        
        return []
    
    def resolve_entity_type(self, generic_type: str, id_type: str, 
                          id_value: Dict[str, Any]) -> Optional[str]:
        """Resolve entity type"""
        # Listings are not generic types
        return None
